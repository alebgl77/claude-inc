'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),os=require('node:os'),{spawnSync}=require('node:child_process');
const app=require('../studio/company.js'),root=path.resolve(__dirname,'..'),source=fs.readFileSync(path.join(root,'studio/company.js'),'utf8');
const context={window:{}};vm.runInNewContext(fs.readFileSync(path.join(root,'studio/company-data.js'),'utf8'),context);
const data=JSON.parse(JSON.stringify(context.window.CLAUDE_INC_COMPANY)),ids=data.departments.map(d=>d.id);
const fields={brief:'A useful project',goal:'A reviewed result',constraints:'Keep it local'};
const copy=value=>JSON.parse(JSON.stringify(value));
function project(){
  const s={schemaVersion:1,name:'Example project',brief:'PRIVATE project context 🚀',goals:['A real outcome'],constraints:['Local only'],activeDepartments:[ids[0]],departments:[...ids],tasks:[],decisions:[],events:[],revision:0};
  const event=(type,taskId,note='Recorded evidence')=>{s.events.push({revision:++s.revision,type,taskId,note});return s.revision;};event('init',null,'Project initialized');
  for(const [i,status] of app.STATUSES.entries()){
    const t={id:'task-'+i,department:ids[i],title:'Task '+i,acceptance:'Demonstrate the result.',dependsOn:[],status,artifacts:[],summary:null,blockedReason:null,reviews:[]};
    s.tasks.push(t);event('task.add',t.id);
    if(status==='planned')continue;
    event('task.start',t.id);
    if(status==='blocked'){t.blockedReason='Input missing';event('task.block',t.id);}
    if(['review','done'].includes(status)){t.artifacts=[{path:'output/result-'+i+'.md',size:12,sha256:'a'.repeat(64)}];t.summary='File produced';event('task.submit',t.id);}
    if(status==='done'){const revision=event('task.accept',t.id,'Checked against source');t.reviews.push({decision:'accept',reviewer:'ceo',note:'Checked against source',revision});}
  }
  const revision=event('decision.add',null,'Use supplied sources only');s.decisions.push({id:1,text:'Use supplied sources only',revision});
  return s;
}
class Element{
  constructor(tag='div'){this.tag=tag;this.children=[];this.attributes={};this.listeners={};this.value='';this.hidden=false;this.textContent='';this.files=[];}
  append(...children){this.children.push(...children);}replaceChildren(...children){this.children=children;}
  setAttribute(name,value){this.attributes[name]=value;}addEventListener(name,fn){this.listeners[name]=fn;}
  focus(){this.focused=true;}select(){this.selected=true;}scrollIntoView(){this.scrolled=true;}
  click(){return this.listeners.click?.();}remove(){this.removed=true;}
}
function harness({catalog=data,clipboard,search='',hash=''}={}){
  const html=fs.readFileSync(path.join(root,'studio/index.html'),'utf8'),elements=new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));
  const document={readyState:'complete',body:new Element('body'),createElement:tag=>new Element(tag),getElementById(id){assert.ok(elements.has(id),'Missing real HTML id: '+id);return elements.get(id);}};
  const window={document,CLAUDE_INC_COMPANY:catalog,location:{search,hash,replace(value){window.redirect=value;}},navigator:{clipboard},setTimeout(fn){fn();},URL:{createObjectURL(blob){window.blob=blob;return 'blob:test';},revokeObjectURL(url){window.revoked=url;}}};
  vm.runInNewContext(source,{window,TextEncoder,TextDecoder,Blob});
  const get=id=>document.getElementById(id);
  function edit(values=fields){for(const [key,id] of [['brief','project-brief'],['goal','project-goal'],['constraints','project-constraints']]){get(id).value=values[key];get(id).listeners.input();}}
  async function load(value){const raw=typeof value==='string'?value:JSON.stringify(value),buffer=new TextEncoder().encode(raw);get('project-file').files=[{size:buffer.byteLength,arrayBuffer:async()=>buffer.buffer}];await get('project-file').listeners.change();}
  return{window,document,get,edit,load};
}
function allText(node){return node.textContent+'\n'+node.children.map(allText).join('\n');}

test('canonical dataset has eight distinct departments and all fifty manual-backed employees',()=>{
  assert.equal(app.validateDataset(data).valid,true);assert.equal(data.departments.length,8);
  const skills=[...data.departments.flatMap(d=>d.skills),...data.staff];assert.equal(skills.length,50);assert.equal(new Set(skills.map(s=>s.id)).size,50);
  for(const skill of skills){const manual=fs.readFileSync(path.join(root,'skills',skill.id,'SKILL.md'),'utf8').replace(/\r\n/g,'\n');assert.ok(manual.includes(skill.output),skill.id);assert.ok(manual.includes('# '+skill.name),skill.id);}
  assert.deepEqual(data.staff.map(s=>s.id),['chief-of-staff','token-accountant']);
  for(const department of data.departments)assert.match(department.scope,/^You /);
});
test('dataset validation rejects missing, duplicate, malformed and unsafe identifiers',()=>{
  for(const input of [null,{},[],{...data,schemaVersion:2}])assert.equal(app.validateDataset(input).valid,false);
  for(const mutate of [d=>d.departments.pop(),d=>d.staff.pop(),d=>d.departments[0].skills.pop(),d=>d.departments[0].id='../private',d=>d.staff[0].id=d.departments[0].skills[0].id,d=>d.departments[0].skills[0].output=null]){
    const value=copy(data);mutate(value);assert.equal(app.validateDataset(value).valid,false);
  }
  assert.equal(harness({catalog:null}).get('company-error').hidden,false);
});
test('all departments are keyboard buttons and all fifty skills can be explored',()=>{
  const h=harness(),buttons=h.get('department-nav').children;assert.equal(buttons.length,8);assert.equal(h.get('hero-departments').children.length,8);assert.equal(h.get('staff-list').children.length,2);
  buttons.forEach((b,i)=>{assert.equal(b.tag,'button');b.click();assert.equal(h.get('department-name').textContent,data.departments[i].name);assert.equal(h.get('employee-list').children.length,6);assert.equal(b.attributes['aria-pressed'],'true');assert.ok(allText(h.get('employee-list')).includes(data.departments[i].skills[0].id));});
  h.get('hero-departments').children[1].click();assert.equal(h.get('department-name').focused,true);assert.equal(h.get('departments').scrolled,true);
});
test('legacy exact query and hash recipes reach Mission Studio without propagating private text',()=>{
  for(const id of data.missionIds){assert.equal(app.legacyMission('?mission='+id,'',data),'missions.html#mission='+id);assert.equal(harness({hash:'#mission='+id}).window.redirect,'missions.html#mission='+id);}
  for(const s of ['?mission=unknown','?mission=launch&brief=PRIVATE','?mission=%6caunch','#mission=launch\n','?mission=__proto__'])assert.equal(app.legacyMission(s,'',data),null);
});
test('literal founder sections preserve Unicode, whitespace, line endings, and fenced malicious-looking text',()=>{
  const raw='  \tCafé 🚀 你好 e\u0301\r\n</textarea><script>literal()</script>\n'+String.fromCharCode(96).repeat(9)+'\n  ';
  const f={brief:raw,goal:'\tGoal\r\n ',constraints:'<img src=x onerror=attack()> & $(touch X)'};
  const output=app.composeBrief(data,f,[ids[3],ids[0]]);
  for(const value of Object.values(f))assert.ok(output.includes(value));
  assert.ok(output.includes(String.fromCharCode(96).repeat(10)+'text\n'+raw+'\n'+String.fromCharCode(96).repeat(10)));
  assert.match(output,/All eight departments remain available/);for(const id of ids)assert.ok(output.includes(id));
  assert.match(output,/preferences, not exclusions/);assert.match(output,/dependencies.*acceptance checks/);assert.match(output,/PASS, FAIL, or NOT RUN/);
  assert.equal(app.bytes(output),Buffer.byteLength(output,'utf8'));
});
test('complete export enforces the exact 8000 UTF-8 byte boundary including metadata',()=>{
  const f={brief:'x',goal:'',constraints:''},overhead=app.bytes(app.buildBrief(data,f,[]))-1;
  f.brief='x'.repeat(8000-overhead);assert.equal(app.bytes(app.composeBrief(data,f,[])),8000);
  f.brief+='x';assert.equal(app.validateDraft(data,f,[]).valid,false);assert.throws(()=>app.composeBrief(data,f,[]));
  f.brief='🚀'.repeat(Math.floor((8000-overhead)/4));assert.equal(app.validateDraft(data,f,[]).valid,true);f.brief+='🚀';assert.equal(app.validateDraft(data,f,[]).valid,false);
});
test('invalid text, controls, unpaired surrogates and unknown preferences cannot export',()=>{
  for(const raw of ['',null,undefined,' \t\r\n','x\u0000','x\u007f','x\ud800','x\udfff','x'.repeat(8001)]){
    assert.throws(()=>app.composeBrief(data,{...fields,brief:raw},[]));assert.equal(app.validText(raw),false);
  }
  for(let code=0;code<=159;code++){if(code>31&&code<127)continue;assert.equal(app.validText('ok'+String.fromCharCode(code)),[9,10,13].includes(code));}
  for(const prefs of [['unknown'],[ids[0],ids[0]],null])assert.throws(()=>app.composeBrief(data,fields,prefs));
  for(const key of ['goal','constraints'])assert.throws(()=>app.composeBrief(data,{...fields,[key]:'x\ud800'},[]));
  assert.equal(app.validText('\ufeff'),true);assert.equal(app.validText('\u200b'),true);
  for(const value of ['\u00a0','\u1680','\u2000','\u2028','\u202f','\u205f','\u3000'])assert.equal(app.validText(value),false);
});
test('draft stays freeform; selecting preferences does not exclude any department',()=>{
  const h=harness();assert.equal(h.get('download-brief').disabled,true);h.edit();
  const checkbox=h.get('department-preferences').children[1].children[0];checkbox.checked=true;checkbox.listeners.change();
  assert.equal(h.get('download-brief').disabled,false);assert.equal(h.get('department-nav').children.length,8);assert.equal(h.get('project-brief').value,fields.brief);
  h.edit({...fields,brief:' '});assert.equal(h.get('copy-ceo').disabled,true);assert.equal(h.get('brief-error').hidden,false);assert.equal(h.get('project-brief').attributes['aria-invalid'],'true');
});
test('downloaded UTF-8 Blob matches complete brief exactly and releases its URL',async()=>{
  const h=harness();h.edit({...fields,brief:' \tExact café 🚀\r\n'});
  h.get('download-brief').click();assert.equal(await h.window.blob.text(),app.composeBrief(data,{...fields,brief:' \tExact café 🚀\r\n'},[]));
  const link=h.document.body.children.at(-1);assert.equal(link.download,'company-brief.md');assert.equal(link.removed,true);assert.equal(h.window.revoked,'blob:test');assert.match(h.get('action-status').textContent,/Download requested/);
});
test('download errors are visible and release any allocated URL',()=>{
  const h=harness();h.edit();h.document.body.append=()=>{throw new Error('Denied');};h.get('download-brief').click();
  assert.match(h.get('action-status').textContent,/could not start/);assert.equal(h.window.revoked,'blob:test');
});
test('clipboard absence or rejection has a visible exact manual-copy fallback',async()=>{
  for(const clipboard of [undefined,{writeText:()=>Promise.reject(new Error('Denied'))}]){
    const h=harness({clipboard});h.edit();await h.get('copy-ceo').click();assert.equal(h.get('copy-fallback').hidden,false);assert.equal(h.get('manual-copy').value,'/company\n\n'+app.composeBrief(data,fields,[]));assert.equal(h.get('manual-copy').selected,true);assert.match(h.get('action-status').textContent,/unavailable/);
  }
});
test('clipboard completion is honest and stale completions cannot restore private data',async()=>{
  let resolve;const h=harness({clipboard:{writeText:()=>new Promise(done=>{resolve=done;})}});h.edit();const pending=h.get('copy-ceo').click();assert.equal(h.get('action-status').textContent,'');resolve();await pending;assert.match(h.get('action-status').textContent,/copied/);
  for(const action of ['edit','download']){let reject;const g=harness({clipboard:{writeText:()=>new Promise((_,fail)=>{reject=fail;})}});g.edit();const old=g.get('copy-ceo').click();if(action==='edit')g.edit({...fields,brief:'New draft'});else g.get('download-brief').click();reject(new Error('Denied'));await old;assert.equal(g.get('copy-fallback').hidden,true);assert.equal(g.get('manual-copy').value,'');}
});
test('realistic multi-department state validates every lifecycle status and displays actual tasks',async()=>{
  const s=project();assert.deepEqual(app.parseProject(JSON.stringify(s),data),s);const h=harness();await h.load(s);
  assert.equal(h.get('project-board').hidden,false);assert.equal(h.get('snapshot-name').textContent,s.name);assert.equal(h.get('snapshot-departments').children.length,8);assert.equal(h.get('snapshot-tasks').children.length,5);
  assert.match(allText(h.get('snapshot-tasks')),/task-4/);assert.match(allText(h.get('snapshot-tasks')),/Recorded review: accept · ceo/);assert.match(allText(h.get('snapshot-tasks')),/output\/result-4.md/);
  assert.match(allText(h.get('snapshot-context')),/PRIVATE project context 🚀/);assert.match(allText(h.get('snapshot-decisions')),/Use supplied sources only/);
});
test('malformed, ambiguous, oversized or unknown-schema project JSON is rejected',()=>{
  for(const value of ['',null,'{}','[]','{bad','{"schemaVersion":1,"schemaVersion":1}','{"x":{"a":1,"\\u0061":2}}','['.repeat(33)+']'.repeat(33),' '.repeat(app.MAX_STATE_BYTES+1)])assert.throws(()=>app.parseProject(value,data));
  const cases=[s=>s.schemaVersion=2,s=>s.privateExtra='x',s=>s.name='x'.repeat(257),s=>s.brief='x\u0000',s=>s.activeDepartments=[],s=>s.departments.reverse(),s=>s.revision=2049,s=>s.tasks=Array(129).fill(s.tasks[0]),s=>s.goals=Array(33).fill('x'),s=>s.events.pop(),s=>s.decisions[0].revision=999];
  for(const mutate of cases){const s=project();mutate(s);assert.throws(()=>app.validateProject(s,data),mutate.toString());}
});
test('contradictory task states, dependencies, reviews and histories fail validation',()=>{
  const cases=[s=>s.tasks[0].status='running',s=>s.tasks[1].id=s.tasks[0].id,s=>s.tasks[0].dependsOn=['task-1'],s=>s.tasks[1].dependsOn=['task-0'],s=>s.tasks[2].blockedReason=null,s=>s.tasks[3].artifacts=[],s=>s.tasks[3].summary=null,s=>s.tasks[4].reviews[0].reviewer=s.tasks[4].department,s=>s.tasks[4].reviews[0].note='Conflicting note',s=>s.tasks[4].reviews=[],s=>s.events[1].type='__proto__',s=>s.events[1].type=['task.add'],s=>s.events[1].taskId='missing',s=>s.events[2].type='task.submit',s=>s.decisions[0].text='Conflicting decision'];
  for(const mutate of cases){const s=project();mutate(s);assert.throws(()=>app.validateProject(s,data),mutate.toString());}
});
test('artifact names must stay portable and relative; hashes and sizes are only recorded metadata',()=>{
  for(const value of ['/private/file','../secret','a/../b','C:/private','x:y','a\\b','a//b','a/.','a/CON.txt','.claude/company/project.json','a.','a ']){
    const s=project();s.tasks[3].artifacts[0].path=value;assert.throws(()=>app.validateProject(s,data),value);
  }
  for(const [key,value] of [['size',-1],['size',2**30],['sha256','bad']]){const s=project();s.tasks[3].artifacts[0][key]=value;assert.throws(()=>app.validateProject(s,data));}
});
test('imported text is inert, never leaks to exports, and reset clears displayed private state',async()=>{
  const h=harness();h.edit();const s=project();s.name='</h3><script>attack()</script>';s.brief='<img src=x onerror=attack()> PRIVATE IMPORT';
  await h.load(s);assert.equal(h.get('snapshot-name').textContent,s.name);assert.ok(allText(h.get('snapshot-context')).includes(s.brief));
  h.get('download-brief').click();assert.ok(!(await h.window.blob.text()).includes('PRIVATE IMPORT'));assert.equal(h.get('project-brief').value,fields.brief);
  h.get('reset-project').click();assert.equal(h.get('project-board').hidden,true);assert.equal(h.get('snapshot-name').textContent,'');assert.equal(h.get('snapshot-context').children.length,0);assert.equal(h.get('project-brief').value,fields.brief);
});
test('invalid imports preserve the old snapshot and failed reads show an error',async()=>{
  const h=harness();await h.load(project());await h.load('{broken');assert.equal(h.get('snapshot-name').textContent,'Example project');assert.equal(h.get('import-error').hidden,false);
  for(const file of [{size:app.MAX_STATE_BYTES+1,arrayBuffer:()=>{throw new Error('Must not read');}},{size:2,arrayBuffer:async()=>new Uint8Array([0xff,0xfe]).buffer},{size:1,arrayBuffer:async()=>{throw new Error('Denied');}}]){
    h.get('project-file').files=[file];await h.get('project-file').listeners.change();assert.equal(h.get('import-error').hidden,false);assert.equal(h.get('snapshot-name').textContent,'Example project');
  }
});
test('a newer import or explicit close supersedes pending file reads',async()=>{
  for(const action of ['load','reset']){
    const h=harness();let resolve;h.get('project-file').files=[{size:100,arrayBuffer:()=>new Promise(done=>{resolve=done;})}];const pending=h.get('project-file').listeners.change();
    if(action==='load'){const newer=project();newer.name='New snapshot';await h.load(newer);}else h.get('reset-project').click();
    resolve(new TextEncoder().encode(JSON.stringify(project())).buffer);await pending;
    assert.equal(h.get('snapshot-name').textContent,action==='load'?'New snapshot':'');assert.equal(h.get('project-board').hidden,action==='reset');
  }
});
test('privacy and safe-command contract is enforced by static source and real HTML fixtures',()=>{
  assert.doesNotMatch(source,/\.innerHTML\b|\.outerHTML\b|insertAdjacentHTML|document\.write\b|\bfetch\s*\(|XMLHttpRequest|localStorage|sessionStorage|sendBeacon|location\.(?:href|search|hash)\s*=/);
  const html=fs.readFileSync(path.join(root,'studio/index.html'),'utf8');assert.match(html,/company project init --name 'My project' --brief-file company-brief\.md/);assert.match(html,/company project start/);assert.match(html,/company project status/);assert.match(html,/\.claude\/company\/project\.json/);assert.doesNotMatch(html,/<script[^>]+src="https?:|<link[^>]+href="https?:[^"]+"[^>]+rel="stylesheet"/);
  assert.match(fs.readFileSync(path.join(root,'studio/missions.html'),'utf8'),/src="studio\.js"/);assert.match(html,/href="missions\.html"/);
});
test('company generator is deterministic, current, profile-free, and check mode writes nothing',()=>{
  const python=process.env.PYTHON||'python';
  const run=(args,cwd=root)=>spawnSync(python,args,{cwd,encoding:'utf8',timeout:20000});
  const result=run(['-B','scripts/build_company.py','--check']);assert.equal(result.status,0,result.stderr);
  const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'company-data-test-'));
  try{
    for(const dir of ['scripts','skills','agents','commands','bin'])fs.cpSync(path.join(root,dir),path.join(temporary,dir),{recursive:true});
    fs.mkdirSync(path.join(temporary,'studio'));const target=path.join(temporary,'studio/company-data.js');
    assert.equal(run(['-B','scripts/build_company.py','--check'],temporary).status,1);assert.equal(fs.existsSync(target),false);
    assert.equal(run(['-B','scripts/build_company.py'],temporary).status,0);const before=fs.readFileSync(target);assert.deepEqual(before,fs.readFileSync(path.join(root,'studio/company-data.js')));
    assert.equal(run(['-B','scripts/build_company.py','--check'],temporary).status,0);const stat=fs.statSync(target).mtimeMs;
    const manual=path.join(temporary,'skills',data.departments[0].skills[0].id,'SKILL.md');fs.writeFileSync(manual,fs.readFileSync(manual,'utf8').replace('## Output format','## Output format\n\nCANONICAL OUTPUT CHANGE'));
    assert.equal(run(['-B','scripts/build_company.py','--check'],temporary).status,1);assert.deepEqual(fs.readFileSync(target),before);assert.equal(fs.statSync(target).mtimeMs,stat);
    const generated=before.toString('ascii');assert.doesNotMatch(generated,/<|C:\\\\Users|company-team\.md|PRIVATE/);
  }finally{assert.equal(path.dirname(path.resolve(temporary)),path.resolve(os.tmpdir()));assert.ok(path.basename(temporary).startsWith('company-data-test-'));fs.rmSync(temporary,{recursive:true,force:true});}
});

test('pasted CLI JSON uses the same board validation, clears raw data, and stays out of founder exports',async()=>{
  const h=harness();h.edit();h.get('project-json').value=JSON.stringify(project());h.get('open-pasted-project').click();
  assert.equal(h.get('snapshot-name').textContent,'Example project');assert.equal(h.get('project-json').value,'');assert.equal(h.get('paste-snapshot').open,false);
  h.get('download-brief').click();assert.ok(!(await h.window.blob.text()).includes('PRIVATE project context'));
  h.get('project-json').value='{invalid';h.get('open-pasted-project').click();assert.equal(h.get('import-error').hidden,false);assert.equal(h.get('snapshot-name').textContent,'Example project');assert.equal(h.get('project-json').value,'{invalid');
  h.get('project-json').value='x'.repeat(app.MAX_STATE_BYTES+1);h.get('open-pasted-project').click();assert.equal(h.get('snapshot-name').textContent,'Example project');
  h.get('reset-project').click();assert.equal(h.get('project-json').value,'');assert.equal(h.get('snapshot-name').textContent,'');
});
test('pasting a snapshot supersedes any pending file read and cannot restore older private state',async()=>{
  const h=harness();let resolve;h.get('project-file').files=[{size:100,arrayBuffer:()=>new Promise(done=>{resolve=done;})}];const pending=h.get('project-file').listeners.change();
  const newer=project();newer.name='Pasted company';h.get('project-json').value=JSON.stringify(newer);h.get('open-pasted-project').click();
  resolve(new TextEncoder().encode(JSON.stringify(project())).buffer);await pending;assert.equal(h.get('snapshot-name').textContent,'Pasted company');assert.equal(h.get('project-json').value,'');
});

test('a downloaded company brief initializes the real CLI and its multi-department board imports unchanged',async()=>{
  const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'company-cli-browser-'));
  const helper=path.join(root,'skills/chief-of-staff/scripts/project.py');
  const run=(...args)=>{const r=spawnSync(process.env.PYTHON||'python',['-B',helper,...args],{cwd:temporary,encoding:'utf8',timeout:20000});assert.equal(r.status,0,r.stderr);return r.stdout;};
  try{
    const founder={brief:' \tCLI integration fixture café 🚀\r\n',goal:'Verify browser / CLI parity',constraints:'Synthetic local test'};
    const brief=app.composeBrief(data,founder,['marketing']);
    fs.writeFileSync(path.join(temporary,'company-brief.md'),brief,'utf8');
    run('init','--name','Browser CLI fixture','--brief-file','company-brief.md');
    run('task','add','--id','offer','--department','marketing','--title','Create fixture offer','--acceptance','Contains synthetic fixture label');
    run('task','add','--id','site','--department','developers','--title','Use reviewed offer','--acceptance','Uses the accepted fixture','--depends-on','offer');
    run('task','start','offer');
    fs.writeFileSync(path.join(temporary,'offer.md'),'Synthetic fixture only. No business claim.','utf8');
    run('task','submit','offer','--artifact','offer.md','--summary','Wrote synthetic fixture');
    run('task','review','offer','--decision','accept','--reviewer','ceo','--note','Verified fixture label');
    run('task','start','site');
    run('decision','add','--text','Keep the integration fixture local.');
    const output=run('status','--format','json'),state=app.parseProject(output,data);
    assert.equal(state.brief,brief);assert.equal(state.tasks[0].status,'done');assert.equal(state.tasks[1].status,'active');assert.deepEqual(state.tasks[1].dependsOn,['offer']);
    const h=harness();await h.load(output);assert.equal(h.get('snapshot-name').textContent,'Browser CLI fixture');
    assert.match(allText(h.get('snapshot-tasks')),/Recorded review: accept · ceo/);assert.match(allText(h.get('snapshot-tasks')),/Depends on: offer/);
  }finally{assert.equal(path.dirname(path.resolve(temporary)),path.resolve(os.tmpdir()));assert.ok(path.basename(temporary).startsWith('company-cli-browser-'));fs.rmSync(temporary,{recursive:true,force:true});}
});
