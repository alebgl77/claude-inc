'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto'),path=require('node:path'),{spawnSync}=require('node:child_process');
const app=require('../studio/company.js'),harness=require('../studio/harness.js'),fixtures=require('./harness-fixtures.json');
const root=path.resolve(__dirname,'..'),context={window:{}};vm.runInNewContext(fs.readFileSync(path.join(root,'studio/company-data.js'),'utf8'),context);const data=context.window.CLAUDE_INC_COMPANY;
const copy=v=>JSON.parse(JSON.stringify(v)),state=name=>copy(fixtures.states.find(s=>s.name===name).state),validate=s=>app.parseProject(JSON.stringify(s),data);
const first=s=>s.tasks[0],policy=s=>s.harness.policies[first(s).id],assessment=s=>s.harness.assessments[0];
function revise(){const s=state('dependency-ready'),t=first(s);t.status='active';t.reviews[0].decision='revise';s.events.at(-1).type='task.revise';assessment(s).results[0]={...assessment(s).results[0],status:'fail',evidence:[],observation:''};return s;}
function activateLate(name){
  const s=state(name),old=s.harness.enabledRevision;
  s.events=s.events.filter(e=>e.type!=='harness.generate');s.events.forEach((e,i)=>e.revision=i+1);
  for(const t of s.tasks)for(const review of t.reviews){if(review.revision>old)review.revision--;review.reviewer='ceo';}
  s.events.push({revision:s.revision,type:'harness.generate',taskId:null,note:'Business harness enabled'});
  s.harness.enabledRevision=s.revision;s.harness.rounds=[];s.harness.assessments=[];
  for(const t of s.tasks)if(t.status==='done')delete s.harness.policies[t.id];else s.harness.policies[t.id].createdRevision=s.revision;
  return s;
}
test('SHA-256 matches standard empty, short, multiblock and million-byte vectors',()=>{
  for(const message of ['', 'abc', 'abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq','x'.repeat(55),'x'.repeat(56),'x'.repeat(63),'x'.repeat(64),'a'.repeat(1000000)])assert.equal(harness.sha256(message),crypto.createHash('sha256').update(message).digest('hex'));
  assert.throws(()=>harness.sha256('é'));
});
test('canonical Python goldens match including astral versus BMP artifact ordering',()=>{
  for(const golden of fixtures.hashes){
    const payload=golden.domain==='artifacts'?[...golden.payload].sort((a,b)=>harness.codepointCompare(a.path,b.path)):golden.payload;
    assert.equal(harness.canonical(payload),golden.canonical,golden.name);
    assert.equal(golden.domain==='artifacts'?harness.artifactFingerprint(golden.payload):harness.fingerprint(golden.domain,golden.payload),golden.sha256,golden.name);
  }
  assert.deepEqual(['🧭','\ue000','é'].sort(harness.codepointCompare),['é','\ue000','🧭']);
  assert.equal(harness.canonical({z:'é 🚀',a:'\n\t"\\'}),'{"a":"\\n\\t\\"\\\\","z":"\\u00e9 \\ud83d\\ude80"}');
  for(const value of [NaN,Infinity,1.5,2**53,undefined,'\ud800','\udfff','x\u0000',{'é':1}])assert.throws(()=>harness.canonical(value));
});
for(const fixture of fixtures.states)test('real CLI schema 2 fixture and next DTO: '+fixture.name,()=>{
  assert.deepEqual(validate(fixture.state),fixture.state);assert.deepEqual(harness.nextAction(fixture.state),fixture.next);
});
const invalids=[
 ['extra harness field',s=>s.harness.extra=true],['unknown harness version',s=>s.harness.version=2],['invalid activation',s=>s.harness.enabledRevision=1],
 ['fractional limit',s=>s.harness.defaults.maxIterations=1.5],['excessive limit',s=>s.harness.defaults.maxIterations=11],['unknown effort',s=>s.harness.defaults.effort='maximum'],['unknown stage',s=>s.harness.defaults.stage='prod'],
 ['extra default field',s=>s.harness.defaults.unused=0],['missing profile',s=>delete s.harness.profiles.legal],['unknown source',s=>s.harness.profiles.legal.source.path='file:///private'],['bad source digest',s=>s.harness.profiles.legal.source.sha256='x'],['source mismatch',s=>s.harness.profiles.legal.source.sha256='0'.repeat(64)],
 ['missing business check',s=>s.harness.profiles.legal.checks.pop()],['duplicate business criterion',s=>s.harness.profiles.legal.checks[1].criterion=s.harness.profiles.legal.checks[0].criterion],['extra check field',s=>s.harness.profiles.legal.checks[0].extra=true],['invalid Unicode profile',s=>s.harness.profiles.legal.checks[0].criterion='x\ud800'],
 ['missing policy',s=>delete s.harness.policies[first(s).id]],['foreign policy',s=>s.harness.policies.unknown=policy(s)],['wrong creation revision',s=>policy(s).createdRevision++],['policy effort changed',s=>policy(s).effort='deep'],['policy digest changed',s=>policy(s).fingerprint='a'.repeat(64)],['policy task contract changed',s=>first(s).acceptance+=' Changed'],
 ['foreign department skill',s=>policy(s).skills=['paid-ads']],['duplicate skill',s=>policy(s).skills.push(policy(s).skills[0])],['object skill',s=>policy(s).skills=[{}]],['missing gate',s=>policy(s).gates.pop()],['optional gate',s=>policy(s).gates[0].required=false],['gate text surrogate',s=>policy(s).gates[0].criterion='x\ud800'],
 ['activation history changed',s=>s.events[s.harness.enabledRevision-1].type='decision.add'],['duplicate activation',s=>{s.events.push({revision:++s.revision,type:'harness.generate',taskId:null,note:'Again'});}],
 ['missing round',s=>s.harness.rounds=[]],['duplicate round',s=>s.harness.rounds.push(copy(s.harness.rounds[0]))],['stale round revision',s=>s.harness.rounds[0].submitRevision--],['round wrong policy',s=>s.harness.rounds[0].policyFingerprint='b'.repeat(64)],['round changed metadata',s=>s.harness.rounds[0].artifacts[0].size++],['round path traversal',s=>s.harness.rounds[0].artifacts[0].path='../private'],['round missing artifacts',s=>s.harness.rounds[0].artifacts=[]],
 ['missing acceptance assessment',s=>s.harness.assessments=[]],['assessment replay',s=>s.harness.assessments.push(copy(assessment(s)))],['stale assessment submission',s=>assessment(s).submitRevision--],['assessment future review',s=>assessment(s).reviewRevision++],['assessment task mismatch',s=>assessment(s).taskId=s.tasks[1].id],['assessment policy mismatch',s=>assessment(s).policyFingerprint='c'.repeat(64)],['artifact fingerprint mismatch',s=>assessment(s).artifactFingerprint='d'.repeat(64)],
 ['missing gate result',s=>assessment(s).results.pop()],['duplicate gate result',s=>assessment(s).results[1]=copy(assessment(s).results[0])],['unknown result',s=>assessment(s).results[0].status='skipped'],['fail cannot accept',s=>assessment(s).results[0].status='fail'],['unknown cannot accept',s=>assessment(s).results[0].status='unknown'],['PASS needs evidence',s=>assessment(s).results[0].evidence=[]],['PASS needs observation',s=>assessment(s).results[0].observation=''],['foreign evidence',s=>assessment(s).results[0].evidence[0].path='other.md'],['empty locator',s=>assessment(s).results[0].evidence[0].locator=''],['surrogate observation',s=>assessment(s).results[0].observation='x\udfff'],['oversized locator',s=>assessment(s).results[0].evidence[0].locator='é'.repeat(501)],
 ['orphan extension',s=>s.harness.extensions.push({taskId:first(s).id,revision:s.revision,fromLimit:3,toLimit:4,reason:'Not an event'})],
];
for(const [name,mutate] of invalids)test('rejects '+name,()=>{const s=state('dependency-ready');mutate(s);assert.throws(()=>validate(s),name);});
test('FAIL and UNKNOWN are valid recorded revision results, never substituted with passes',()=>{
  for(const status of ['fail','unknown']){const s=revise();assessment(s).results[0].status=status;assert.deepEqual(validate(s),s);assert.equal(harness.nextAction(s).action,'work');}
});
test('historical acceptance and preactivation review have honest distinct semantics',()=>{
  const historical=activateLate('dependency-ready');assert.deepEqual(validate(historical),historical);assert.equal(Object.hasOwn(historical.harness.policies,first(historical).id),false);
  const review=activateLate('review');assert.deepEqual(validate(review),review);assert.equal(harness.nextAction(review).action,'revise');assert.equal(harness.usedLimit(review,first(review).id).used,1);
  const forged=copy(historical);forged.harness.policies[first(forged).id]=policy(state('dependency-ready'));assert.throws(()=>validate(forged));
});
test('CTO reviewer cannot be retroactively inserted before harness activation',()=>{
  const s=activateLate('dependency-ready');first(s).reviews[0].reviewer='cto';assert.throws(()=>validate(s),/CTO reviews require/);
});
test('final review wins over exhausted allowance, then a revision requires escalation',()=>{
  const review=state('review');review.harness.defaults.maxIterations=1;validate(review);assert.equal(harness.nextAction(review).action,'evaluate');
  const s=revise();s.harness.defaults.maxIterations=1;validate(s);assert.equal(harness.nextAction(s).action,'escalate');
  const invalid=copy(s);invalid.events.push({revision:++invalid.revision,type:'task.submit',taskId:first(s).id,note:'Over budget'});first(invalid).status='review';invalid.harness.rounds.push({...copy(invalid.harness.rounds[0]),submitRevision:invalid.revision});assert.throws(()=>validate(invalid));
  const revision=++s.revision,reason='One additional documented attempt';s.events.push({revision,type:'harness.extend',taskId:first(s).id,note:reason});s.harness.extensions.push({taskId:first(s).id,revision,fromLimit:1,toLimit:2,reason});validate(s);assert.equal(harness.nextAction(s).action,'work');
  for(const mutate of [s=>s.harness.extensions[0].reason='Different',s=>s.harness.extensions[0].fromLimit=0,s=>s.harness.extensions[0].toLimit=1,s=>s.harness.extensions[0].toLimit=11]){const bad=copy(s);mutate(bad);assert.throws(()=>validate(bad));}
});
test('completed tasks cannot receive loop extensions',()=>{
  const s=state('dependency-ready'),revision=++s.revision,reason='Late extension';s.events.push({revision,type:'harness.extend',taskId:first(s).id,note:reason});s.harness.extensions.push({taskId:first(s).id,revision,fromLimit:3,toLimit:4,reason});assert.throws(()=>validate(s));
});
test('new submissions invalidate earlier review data without rewriting recorded history',()=>{
  const s=revise(),t=first(s);t.status='review';t.artifacts=copy(t.artifacts);t.artifacts[0].sha256='f'.repeat(64);s.events.push({revision:++s.revision,type:'task.submit',taskId:t.id,note:'New round'});s.harness.rounds.push({taskId:t.id,submitRevision:s.revision,policyFingerprint:policy(s).fingerprint,artifacts:copy(t.artifacts)});validate(s);
  assert.equal(harness.nextAction(s).reviewTemplate.submitRevision,s.revision);assert.notEqual(harness.nextAction(s).reviewTemplate.artifactFingerprint,assessment(s).artifactFingerprint);
  t.status='done';const revision=++s.revision;s.events.push({revision,type:'task.accept',taskId:t.id,note:'Replayed old evidence'});t.reviews.push({revision,reviewer:'cto',decision:'accept',note:'Replayed old evidence'});s.harness.assessments.push({...copy(assessment(s)),reviewRevision:revision});assert.throws(()=>validate(s));
});
test('empty company plans, blocked tasks wait, dependencies and stable downstream priority agree with Python',()=>{
  const empty=state('ready');empty.tasks=[];empty.events=[empty.events[0],{revision:2,type:'harness.generate',taskId:null,note:'Business harness enabled'}];empty.revision=2;empty.harness.enabledRevision=2;empty.harness.policies={};validate(empty);assert.equal(harness.nextAction(empty).action,'plan');
  const blocked=state('review');first(blocked).status='blocked';first(blocked).blockedReason='Missing input';first(blocked).artifacts=[];first(blocked).summary=null;blocked.events.at(-1).type='task.block';blocked.harness.rounds=[];validate(blocked);assert.equal(harness.nextAction(blocked).action,'waiting');
  const snapshots=[...fixtures.states.map(f=>f.state),empty,blocked,activateLate('review'),activateLate('dependency-ready'),revise()];
  const script='import json,sys\nsys.path.insert(0,"skills/chief-of-staff/scripts")\nimport harness,project\nvalues=json.loads(sys.stdin.buffer.read().decode("utf-8"))\nfor value in values: project.validate_state(value,project.canonical_roster()[0])\nprint(json.dumps([harness.next_action(value) for value in values],ensure_ascii=True))';
  const r=spawnSync(process.env.PYTHON||'python',['-B','-c',script],{cwd:root,input:JSON.stringify(snapshots),encoding:'utf8'});assert.equal(r.status,0,r.stderr);assert.deepEqual(snapshots.map(harness.nextAction),JSON.parse(r.stdout));
});
test('schema 1 stays readable while CTO reviews and harness-only events require schema 2',()=>{
  const s=activateLate('dependency-ready');s.events.pop();s.revision--;s.schemaVersion=1;delete s.harness;first(s).reviews[0].reviewer='ceo';validate(s);assert.equal(harness.nextAction(s).action,'plan');first(s).reviews[0].reviewer='cto';assert.throws(()=>validate(s));
});
for(const mode of ['empty','historical-only'])test(mode+' harness rejects empty and unknown policy keys with Python parity',()=>{
  let valid;
  if(mode==='empty'){
    valid=state('ready');valid.tasks=[];valid.events=[valid.events[0],{revision:2,type:'harness.generate',taskId:null,note:'Business harness enabled'}];valid.revision=2;valid.harness.enabledRevision=2;valid.harness.policies={};
  }else{
    valid=activateLate('dependency-ready');const removed=valid.tasks.pop();valid.events=valid.events.filter(e=>e.taskId!==removed.id);
    valid.events.forEach((e,i)=>{e.revision=i+1;if(e.type==='task.accept')first(valid).reviews[0].revision=e.revision;});
    valid.revision=valid.events.length;valid.harness.enabledRevision=valid.revision;valid.harness.policies={};
  }
  assert.deepEqual(validate(valid),valid);
  const invalid=['','unknown'].map(key=>{const s=copy(valid);s.harness.policies[key]={unvalidated:'arbitrary payload'};return s;});
  invalid.forEach(s=>assert.throws(()=>validate(s)));
  const script='import json,sys\nsys.path.insert(0,"skills/chief-of-staff/scripts")\nimport project\nvalues=json.loads(sys.stdin.buffer.read().decode("utf-8"))\nresults=[]\nfor value in values:\n try:\n  project.validate_state(value,project.canonical_roster()[0]); results.append(True)\n except project.ProjectError:\n  results.append(False)\nprint(json.dumps(results))';
  const r=spawnSync(process.env.PYTHON||'python',['-B','-c',script],{cwd:root,input:JSON.stringify([valid,...invalid]),encoding:'utf8'});
  assert.equal(r.status,0,r.stderr);assert.deepEqual(JSON.parse(r.stdout),[true,false,false]);
});

test('harness source remains local, synchronous and free of HTML or execution sinks',()=>{
  const source=fs.readFileSync(path.join(root,'studio/harness.js'),'utf8');assert.doesNotMatch(source,/\.innerHTML\b|\.outerHTML\b|insertAdjacentHTML|\beval\s*\(|\bfetch\s*\(|XMLHttpRequest|localStorage|sessionStorage|sendBeacon|\basync\b|WebSocket/);
});
