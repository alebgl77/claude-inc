/* Pure snapshot metadata validation and derived guidance; never executes work. */
(function(root){
'use strict';
const PROFILE_PATH='skills/chief-of-staff/references/harness-profiles.json';
const STAGES=['discover','build','launch','operate'],EFFORTS=['light','balanced','deep'];
const digest=value=>typeof value==='string'&&/^[0-9a-f]{64}$/.test(value);
const own=(object,key)=>Object.prototype.hasOwnProperty.call(object,key);
const plain=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
const integer=(value,low,high)=>Number.isSafeInteger(value)&&value>=low&&value<=high;
function validString(value){
  if(typeof value!=='string'||new TextEncoder().encode(value).length>8000||/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f]/.test(value))return false;
  for(let i=0;i<value.length;i++){const c=value.charCodeAt(i);if(c>=0xd800&&c<=0xdbff){const next=value.charCodeAt(++i);if(!(next>=0xdc00&&next<=0xdfff))return false;}else if(c>=0xdc00&&c<=0xdfff)return false;}
  return true;
}
function canonical(value){
  function encode(item){
    if(item===null||typeof item==='boolean')return JSON.stringify(item);
    if(typeof item==='number'){if(!Number.isSafeInteger(item))throw new Error('Canonical numbers must be safe integers.');return JSON.stringify(item);}
    if(typeof item==='string'){if(!validString(item))throw new Error('Invalid canonical Unicode text.');return JSON.stringify(item);}
    if(Array.isArray(item))return '['+item.map(encode).join(',')+']';
    if(plain(item))return '{'+Object.keys(item).sort().map(key=>{if(!/^[\x00-\x7f]*$/.test(key))throw new Error('Canonical keys must be ASCII.');return JSON.stringify(key)+':'+encode(item[key]);}).join(',')+'}';
    throw new Error('Unsupported canonical value.');
  }
  return encode(value).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));
}
// SHA-256 on ASCII canonical JSON. Fixed constants and unsigned 32-bit operations
// preserve the synchronous import API and its existing generation race guards.
function sha256(ascii){
  if(typeof ascii!=='string'||/[^\x00-\x7f]/.test(ascii))throw new Error('SHA-256 input must be ASCII.');
  const k=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  const h=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  const length=ascii.length,buffer=new Uint8Array(Math.ceil((length+9)/64)*64),view=new DataView(buffer.buffer);
  for(let i=0;i<length;i++)buffer[i]=ascii.charCodeAt(i);buffer[length]=0x80;
  view.setUint32(buffer.length-8,Math.floor(length/0x20000000));view.setUint32(buffer.length-4,(length*8)>>>0);
  const w=new Uint32Array(64),rotate=(x,n)=>(x>>>n)|(x<<(32-n));
  for(let offset=0;offset<buffer.length;offset+=64){
    for(let i=0;i<16;i++)w[i]=view.getUint32(offset+i*4);
    for(let i=16;i<64;i++){const x=w[i-15],y=w[i-2];w[i]=(w[i-16]+(rotate(x,7)^rotate(x,18)^(x>>>3))+w[i-7]+(rotate(y,17)^rotate(y,19)^(y>>>10)))>>>0;}
    let [a,b,c,d,e,f,g,j]=h;
    for(let i=0;i<64;i++){const t1=(j+(rotate(e,6)^rotate(e,11)^rotate(e,25))+((e&f)^(~e&g))+k[i]+w[i])>>>0,t2=((rotate(a,2)^rotate(a,13)^rotate(a,22))+((a&b)^(a&c)^(b&c)))>>>0;j=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;}
    [a,b,c,d,e,f,g,j].forEach((v,i)=>{h[i]=(h[i]+v)>>>0;});
  }
  return h.map(v=>v.toString(16).padStart(8,'0')).join('');
}
const fingerprint=(domain,payload)=>sha256('claude-inc/harness-'+domain+'/v1\n'+canonical(payload));
function codepointCompare(a,b){const x=Array.from(a),y=Array.from(b);for(let i=0;i<Math.min(x.length,y.length);i++){const delta=x[i].codePointAt(0)-y[i].codePointAt(0);if(delta)return delta;}return x.length-y.length;}
const artifactFingerprint=artifacts=>fingerprint('artifacts',[...artifacts].sort((a,b)=>codepointCompare(a.path,b.path)));
const policyPayload=(task,p)=>({task:{id:task.id,department:task.department,title:task.title,acceptance:task.acceptance,dependsOn:task.dependsOn},stage:p.stage,effort:p.effort,skills:p.skills,gates:p.gates});
function usedLimit(state,id,before=state.revision+1){
  const used=state.events.filter(e=>e.type==='task.submit'&&e.taskId===id&&e.revision<before).length;
  let limit=null;
  if(state.schemaVersion===2&&own(state.harness.policies,id)){limit=state.harness.defaults.maxIterations;for(const extension of state.harness.extensions)if(extension.taskId===id&&extension.revision<before)limit=extension.toLimit;}
  return {used,limit};
}
const currentSubmission=(state,id,before=state.revision+1)=>state.events.reduce((revision,e)=>e.taskId===id&&e.type==='task.submit'&&e.revision<before?e.revision:revision,0);
function latestRound(state,id,before=state.revision+1){const revision=currentSubmission(state,id,before);return state.harness.rounds.find(r=>r.taskId===id&&r.submitRevision===revision)||null;}
function validate(state,data,helpers){
  const {exact,list,unique,validText,fail}=helpers,h=state.harness;
  const check=(condition,message)=>{if(!condition)fail('Harness: '+message);};
  const same=(a,b)=>canonical(a)===canonical(b);
  const ids=data.departments.map(d=>d.id),tasks=new Map(state.tasks.map(t=>[t.id,t]));
  check(exact(h,'version enabledRevision defaults profiles policies rounds assessments extensions'),'unexpected fields.');
  check(h.version===1&&integer(h.enabledRevision,2,state.revision),'invalid activation revision.');
  const enabled=h.enabledRevision;
  check(!state.tasks.some(task=>task.reviews.some(review=>review.reviewer==='cto'&&review.revision<=enabled)),'CTO reviews require an active schema-2 harness.');
  check(exact(h.defaults,'stage effort maxIterations')&&STAGES.includes(h.defaults.stage)&&EFFORTS.includes(h.defaults.effort)&&integer(h.defaults.maxIterations,1,10),'invalid stage, effort or iteration limit.');
  check(exact(h.profiles,ids.join(' ')),'invalid profile departments.');
  const criteria=[],hashes=[];
  for(const profile of Object.values(h.profiles)){
    check(exact(profile,'source checks')&&exact(profile.source,'path sha256')&&profile.source.path===PROFILE_PATH&&digest(profile.source.sha256),'invalid profile source.');
    hashes.push(profile.source.sha256);check(list(profile.checks,2)&&profile.checks.length===2,'each department needs two business checks.');
    const checks=[];
    for(const item of profile.checks){check(exact(item,'id criterion')&&typeof item.id==='string'&&/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(item.id)&&item.id.length<=80&&validText(item.criterion,2000),'invalid business check.');checks.push(item.id);criteria.push(item.criterion);}
    check(unique(checks),'duplicate business check.');
  }
  check(unique(criteria)&&new Set(hashes).size===1,'profile criteria or source snapshots disagree.');
  const generated=state.events.filter(e=>e.type==='harness.generate');
  check(generated.length===1&&generated[0].revision===enabled&&generated[0].taskId===null,'activation differs from history.');
  const oldDone=new Set(state.events.filter(e=>e.type==='task.accept'&&e.revision<enabled).map(e=>e.taskId));
  for(const task of state.tasks)check(oldDone.has(task.id)||state.events.filter(e=>e.type==='task.submit'&&e.taskId===task.id&&e.revision<enabled).length<10,'activation cannot enroll an unfinished task with ten prior submissions.');
  const eligible=state.tasks.filter(t=>!oldDone.has(t.id)).map(t=>t.id);
  check(exact(h.policies,eligible.join(' ')),'policies must cover unfinished and new tasks only.');
  const adds=new Map(state.events.filter(e=>e.type==='task.add').map(e=>[e.taskId,e.revision]));
  for(const id of eligible){
    const p=h.policies[id],task=tasks.get(id);
    check(exact(p,'createdRevision stage effort skills gates fingerprint')&&p.createdRevision===Math.max(enabled,adds.get(id)),'invalid policy creation.');
    check(list(p.skills,32)&&unique(p.skills),'invalid skill selection.');
    const allowed=[...data.departments.find(d=>d.id===task.department).skills,...data.staff].map(s=>s.id);
    check(p.skills.every(s=>typeof s==='string'&&allowed.includes(s)),'skills must belong to the task department or staff.');
    check(list(p.gates,8)&&p.gates.length>=3,'missing required gates.');
    for(const gate of p.gates)check(exact(gate,'id criterion source required')&&gate.required===true&&validText(gate.criterion),'invalid gate.');
    const custom=p.gates.slice(3).map(g=>g.criterion);check(custom.every(c=>validText(c,2000))&&unique(custom),'invalid project criteria.');
    const gates=[{id:'contract',criterion:task.acceptance,source:'contract',required:true},...h.profiles[task.department].checks.map(c=>({id:'business-'+c.id,criterion:c.criterion,source:'profile',required:true})),...custom.map((criterion,i)=>({id:'project-'+(i+1),criterion,source:'project',required:true}))];
    check(p.stage===h.defaults.stage&&p.effort===h.defaults.effort&&same(p.gates,gates)&&digest(p.fingerprint)&&p.fingerprint===fingerprint('policy',policyPayload(task,p)),'policy baseline or fingerprint differs.');
  }
  const extensionEvents=state.events.filter(e=>e.type==='harness.extend');
  check(list(h.extensions,2048)&&h.extensions.length===extensionEvents.length,'extensions differ from history.');
  const limits=new Map(eligible.map(id=>[id,h.defaults.maxIterations]));
  h.extensions.forEach((extension,i)=>{
    const e=extensionEvents[i];
    check(exact(extension,'taskId revision fromLimit toLimit reason')&&typeof extension.taskId==='string'&&limits.has(extension.taskId),'invalid extension task.');
    const previous=limits.get(extension.taskId);
    check(!state.events.some(item=>item.type==='task.accept'&&item.taskId===extension.taskId&&item.revision<extension.revision),'extension cannot follow task acceptance.');
    check(e.taskId===extension.taskId&&e.revision===extension.revision&&integer(extension.revision,enabled+1,state.revision)&&extension.revision>h.policies[extension.taskId].createdRevision&&extension.fromLimit===previous&&integer(extension.toLimit,previous+1,10)&&validText(extension.reason)&&extension.reason===e.note,'invalid extension revision, reason or limit.');
    limits.set(extension.taskId,extension.toLimit);
  });
  function artifacts(records){
    check(list(records,16)&&records.length>0,'submission requires artifact metadata.');
    const paths=[];
    for(const a of records){check(exact(a,'path size sha256')&&validText(a.path,1024)&&!/[\\:\r\n\t]/.test(a.path)&&!a.path.split('/').some(p=>!p||p==='.'||p==='..')&&!/^\.claude\/company(?:\/|$)/i.test(a.path)&&integer(a.size,0,32*1024*1024)&&digest(a.sha256),'invalid round artifact metadata.');paths.push(a.path);}
    check(unique(paths),'duplicate round artifact paths.');
  }
  const submissions=state.events.filter(e=>e.type==='task.submit'&&e.revision>enabled),rounds=new Map();
  check(list(h.rounds,2048)&&h.rounds.length===submissions.length,'rounds must match post-activation submissions.');
  h.rounds.forEach((round,i)=>{
    const e=submissions[i];
    check(exact(round,'taskId submitRevision policyFingerprint artifacts')&&typeof round.taskId==='string'&&own(h.policies,round.taskId)&&e.taskId===round.taskId&&e.revision===round.submitRevision&&round.policyFingerprint===h.policies[round.taskId].fingerprint,'round differs from its submit event or policy.');
    artifacts(round.artifacts);rounds.set(e.revision,round);
  });
  for(const id of eligible){const round=latestRound(state,id);check(!round||same(round.artifacts,tasks.get(id).artifacts),'current artifacts differ from the last round.');}
  check(list(h.assessments,2048),'invalid assessment collection.');
  const assessments=new Map();let previous=0;
  for(const a of h.assessments){
    check(exact(a,'taskId reviewRevision submitRevision policyFingerprint artifactFingerprint results')&&integer(a.reviewRevision,previous+1,state.revision)&&typeof a.taskId==='string'&&own(h.policies,a.taskId),'invalid assessment identity or order.');previous=a.reviewRevision;
    const e=state.events[a.reviewRevision-1],round=rounds.get(a.submitRevision),p=h.policies[a.taskId];
    check(integer(a.submitRevision,enabled+1,a.reviewRevision-1)&&e.taskId===a.taskId&&['task.accept','task.revise'].includes(e.type)&&currentSubmission(state,a.taskId,a.reviewRevision)===a.submitRevision&&round&&round.taskId===a.taskId,'assessment does not target the reviewed submission.');
    check(a.policyFingerprint===p.fingerprint&&a.artifactFingerprint===artifactFingerprint(round.artifacts),'assessment fingerprints differ.');
    check(list(a.results,8),'invalid gate results.');const seen=[],gateIds=p.gates.map(g=>g.id),paths=round.artifacts.map(r=>r.path);
    for(const r of a.results){
      check(exact(r,'gateId status evidence observation')&&gateIds.includes(r.gateId)&&['pass','fail','unknown'].includes(r.status),'unknown gate or result.');seen.push(r.gateId);
      check(list(r.evidence,16)&&validText(r.observation,8000,r.status!=='pass'),'invalid gate observation or evidence.');
      for(const evidence of r.evidence)check(exact(evidence,'path locator')&&paths.includes(evidence.path)&&validText(evidence.locator,1000),'evidence must reference this round with a plain text locator.');
      check(r.status!=='pass'||r.evidence.length>0,'PASS requires an observation and artifact evidence.');
    }
    check(unique(seen)&&seen.length===gateIds.length,'gate results must cover every required gate once.');
    check(e.type!=='task.accept'||a.results.every(r=>r.status==='pass'),'accepted task has unresolved gates.');assessments.set(a.reviewRevision,a);
  }
  for(const e of state.events){
    if(e.revision<=enabled||!own(h.policies,e.taskId))continue;
    if(['task.start','task.submit'].includes(e.type)){const {used,limit}=usedLimit(state,e.taskId,e.revision);check(used<limit,'event history exceeds the iteration allowance.');}
    check(e.type!=='task.accept'||assessments.has(e.revision),'controlled acceptance requires a complete assessment.');
  }
  return state;
}
function nextAction(state){
  const tasks=state.tasks,byId=new Map(tasks.map(t=>[t.id,t])),policies=state.schemaVersion===2?state.harness.policies:{};
  const blockers=new Map(tasks.map(t=>[t.id,t.dependsOn.filter(id=>byId.get(id).status!=='done')]));
  const downstream=id=>{const found=new Set();for(const t of tasks)if(t.status!=='done'&&(t.dependsOn.includes(id)||t.dependsOn.some(dep=>found.has(dep))))found.add(t.id);return found.size;};
  const ranked=tasks.map((t,i)=>({t,i,score:downstream(t.id)})).sort((a,b)=>b.score-a.score||a.i-b.i).map(v=>v.t);
  const ready=ranked.filter(t=>{const {used,limit}=usedLimit(state,t.id);return t.status==='planned'&&!blockers.get(t.id).length&&(limit===null||used<limit);}).map(t=>t.id);
  const result={sourceRevision:state.revision,action:'waiting',taskId:null,phase:'waiting',reason:'No eligible work: resolve recorded blockers or unaccepted dependencies.',used:0,limit:null,dependencyBlockers:[],policyFingerprint:null,readyIndependentIds:ready,reviewTemplate:null};
  if(state.schemaVersion===1)return {...result,action:'plan',phase:'planning',readyIndependentIds:[],reason:'Harness is not enabled. Inspect the founder scope and enable it explicitly at the current revision before using harness loops.'};
  if(!tasks.length)return {...result,action:'plan',phase:'planning',reason:'Create real task contracts from the founder project; no tasks have been invented.'};
  if(tasks.every(t=>t.status==='done'))return {...result,action:'complete',phase:'complete',reason:'All recorded tasks are accepted; this is historical review state, not proof of delivery or publication.'};
  let task=ranked.find(t=>t.status==='review');
  if(task){
    const current=own(policies,task.id)?latestRound(state,task.id):null;
    if(own(policies,task.id)&&!current)Object.assign(result,{action:'revise',phase:'review',reason:'This submission predates harness activation. Revise, then submit a fresh artifact round before acceptance.'});
    else{
      Object.assign(result,{action:'evaluate',phase:'review',reason:'Inspect the submitted artifacts and every required criterion, then record an evidence-backed review.'});
      if(current)result.reviewTemplate={version:1,taskId:task.id,submitRevision:current.submitRevision,policyFingerprint:policies[task.id].fingerprint,artifactFingerprint:artifactFingerprint(current.artifacts),results:policies[task.id].gates.map(g=>({gateId:g.id,status:'unknown',evidence:[],observation:''}))};
    }
  }else{
    task=ranked.find(t=>t.status==='active');
    if(task)Object.assign(result,{action:'work',phase:'execution',reason:'Continue the active task against its fixed contract; submit actual artifact files when ready.'});
    else if(ready.length){task=byId.get(ready[0]);Object.assign(result,{action:'start',phase:'execution',reason:'Dependencies are accepted; inspect their current artifacts before starting this task.'});}
    else task=ranked.find(t=>{const {used,limit}=usedLimit(state,t.id);return t.status!=='done'&&own(policies,t.id)&&used>=limit;});
    if(task){const {used,limit}=usedLimit(state,task.id);if(limit!==null&&used>=limit)Object.assign(result,{action:'escalate',phase:'escalation',reason:'The lifetime submission allowance is exhausted. Seek an explicit reasoned extension or stop this work.'});}
  }
  if(task)Object.assign(result,{taskId:task.id,...usedLimit(state,task.id),dependencyBlockers:blockers.get(task.id),policyFingerprint:own(policies,task.id)?policies[task.id].fingerprint:null});
  return result;
}
const api={canonical,sha256,fingerprint,policyPayload,artifactFingerprint,codepointCompare,validate,usedLimit,currentSubmission,latestRound,nextAction};
if(typeof module!=='undefined'&&module.exports)module.exports=api;
if(root)root.CLAUDE_INC_HARNESS=api;
})(typeof window!=='undefined'?window:null);
