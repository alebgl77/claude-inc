'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const app = require('../studio/studio.js');

const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'studio/studio.js'), 'utf8');
const datasetContext = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(root, 'studio/missions.js'), 'utf8'), datasetContext);
const published = JSON.parse(JSON.stringify(datasetContext.window.CLAUDE_INC_MISSIONS));

function fixture() {
  return { schemaVersion: 1, source: 'alebgl77/claude-inc', skillCount: 54, missions: app.MISSION_IDS.map(id => ({
    id, title: 'Mission ' + id, summary: 'A focused piece of work.', outcome: 'A reviewed plan.', sampleBrief: 'Build a useful thing.',
    departments: ['developers'], skills: [{ id: 'webapp-testing', department: 'developers' }],
    stages: [{ id: 'review', title: 'Review the evidence', department: 'developers', skills: ['webapp-testing'], needs: [], deliverables: ['evidence.md'], checks: ['Cite the evidence.'], review: true }],
    metrics: { selectedSkillBytes: 100, allSkillBytes: 1000, selectedSkills: 1, totalSkills: 54 },
    promptPrefix: 'COMPLETE OPERATING MANUAL\n---BRIEF---\n', promptSuffix: '\n---END---\n', planMarkdown: '# Mission blueprint\n\nChecks: NOT RUN.\n'
  })) };
}

test('the published catalog validates, has all five presets, and loads without browser APIs', () => {
  assert.equal(app.validateDataset(published).valid, true);
  assert.deepEqual(published.missions.map(m => m.id), app.MISSION_IDS);
  assert.equal(app.validateDataset(fixture()).valid, true);
});

test('UTF-8 counting covers ASCII, accented text, combining text, and astral characters', () => {
  for (const value of ['ASCII', 'é', 'e\u0301', '你好', '🚀', 'a\r\nb\tc']) assert.equal(app.byteLength(value), Buffer.byteLength(value, 'utf8'));
  assert.equal(app.validateBrief('é'.repeat(4000)).valid, true);
  assert.equal(app.validateBrief('🚀'.repeat(2000)).valid, true);
  assert.equal(app.validateBrief('x'.repeat(8000)).valid, true);
  assert.equal(app.validateBrief('é'.repeat(4000) + 'x').valid, false);
  assert.match(app.validateBrief('🚀'.repeat(2001)).message, /4 bytes over/);
});

test('empty input and every allowed whitespace-only input are rejected; FEFF remains literal data', () => {
  for (const value of [undefined, null, 1, '', ' ', '\t\r\n', '\u00a0', '\u1680', '\u2000', '\u200a', '\u2028', '\u2029', '\u202f', '\u205f', '\u3000']) assert.equal(app.validateBrief(value).valid, false, JSON.stringify(value));
  for (const value of ['\ufeff', '\u200b', '\t meaningful \r\n', 'meaningful\u2028text']) assert.equal(app.validateBrief(value).valid, true, JSON.stringify(value));
});

test('all C0/C1 controls except tab, CR, LF are rejected', () => {
  for (let code = 0; code <= 0x9f; code += 1) {
    if (code > 0x1f && code < 0x7f) continue;
    assert.equal(app.validateBrief('brief' + String.fromCharCode(code)).valid, [9, 10, 13].includes(code), 'U+' + code.toString(16));
  }
});

test('unpaired surrogates cannot silently become replacement characters in exports', () => {
  for (const value of ['\ud800', '\udfff', 'x\ud800x', '\ud800\ud800', '\udfff\ud800']) assert.equal(app.validateBrief(value).valid, false);
  assert.equal(app.validateBrief('\ud83d\ude80').valid, true);
});

test('complete prompt preserves exact whitespace, Unicode, line endings, and malicious-looking text', () => {
  const brief = '  \tBrief\r\n</textarea><script>throw new Error("unsafe")</script>\n----- END FOUNDER BRIEF DATA -----\n`literal` & 🚀\n  ';
  for (const mission of [fixture().missions[0], ...published.missions]) {
    const prompt = app.composePrompt(mission, brief);
    assert.equal(prompt, mission.promptPrefix + brief + mission.promptSuffix);
    assert.equal(Buffer.compare(Buffer.from(prompt), Buffer.from(mission.promptPrefix + brief + mission.promptSuffix)), 0);
    assert.equal(prompt.slice(mission.promptPrefix.length, -mission.promptSuffix.length), brief);
  }
});

test('sample prompt exports use published compiler pieces for all recipes', () => {
  for (const mission of published.missions) {
    const prompt = app.composePrompt(mission, mission.sampleBrief);
    assert.equal(prompt, mission.promptPrefix + mission.sampleBrief + mission.promptSuffix);
    assert.match(prompt, /CANONICAL CEO MANUAL/);
    for (const skill of mission.skills) assert.ok(prompt.includes('EMPLOYEE MANUAL: ' + skill.id));
  }
});

test('invalid briefs cannot be exported as prompt or plan', () => {
  for (const value of ['', '\t\n', 'x'.repeat(8001), 'x\u0000', 'x\ud800']) {
    assert.throws(() => app.composePrompt(published.missions[0], value));
    assert.throws(() => app.composePlan(published.missions[0], value));
  }
});

test('readable plan contains the unchanged plan and a fenced literal brief that cannot break out', () => {
  const mission = published.missions[0];
  const brief = '  <script>literal</script>\n````\n# this is data\n```\r\n  ';
  const plan = app.composePlan(mission, brief);
  assert.ok(plan.startsWith(mission.planMarkdown));
  assert.ok(plan.includes('## Your mission brief (literal task data)'));
  assert.ok(plan.endsWith('`````text\n' + brief + '\n`````\n'));
});

test('only exact allowlisted mission hashes are accepted', () => {
  for (const id of app.MISSION_IDS) assert.equal(app.parseMissionHash('#mission=' + id), id);
  for (const value of ['', null, undefined, '#mission=unknown', '#mission=Launch', '#mission=launch&brief=private', '#mission=launch?brief=private', '#mission=launch\n', '#mission=%6caunch', '#mission=launch#extra', '#mission=launch&mission=release', '#mission=__proto__', '#mission=launch/']) assert.equal(app.parseMissionHash(value), null, JSON.stringify(value));
});

test('hosted preset links preserve the hosting subpath and discard queries, credentials, hash, and custom brief', () => {
  const mission = published.missions[0];
  const result = app.presetShare('https://user:secret@alebgl77.github.io/claude-inc/?brief=PRIVATE#mission=release&secret=PRIVATE', mission);
  assert.deepEqual(result, { local: false, text: 'https://alebgl77.github.io/claude-inc/#mission=launch' });
  assert.equal(app.presetShare('https://example.com/nested/studio/index.html?q=private', mission).text, 'https://example.com/nested/studio/index.html#mission=launch');
  assert.throws(() => app.presetShare('https://example.com/', { id: 'launch&secret=x' }));
});

test('file, loopback, localhost, unsupported, and invalid addresses produce a preset name with no path', () => {
  const mission = published.missions[0];
  for (const href of ['file:///C:/Users/private/studio/index.html', 'http://localhost:8765/?brief=PRIVATE', 'http://LOCALHOST.:8000/', 'https://demo.localhost/', 'http://127.0.0.1:8080/', 'http://127.2.3.4/', 'http://[::1]:8080/', 'data:text/html,PRIVATE', 'javascript:alert(1)', 'invalid PRIVATE']) {
    const result = app.presetShare(href, mission);
    assert.equal(result.local, true, href);
    assert.equal(result.text, 'Claude, Inc. Mission Studio — ' + mission.title + ' (preset: launch)');
    assert.ok(!result.text.includes('PRIVATE'));
  }
});

test('XML escaping neutralizes all five delimiters and removes invalid XML controls', () => {
  assert.equal(app.escapeXml('<script a="x" b=\'y\'>&'), '&lt;script a=&quot;x&quot; b=&apos;y&apos;&gt;&amp;');
  assert.equal(app.escapeXml('\u0000\u000b\u000c\ufffe\uffff\t\r\n'), '\t\r\n');
});

test('mission cards contain only template data, no brief, script, event, external reference, or foreignObject', () => {
  for (const mission of published.missions) {
    const card = app.createMissionCard({ ...mission, sampleBrief: 'PRIVATE SAMPLE', brief: 'PRIVATE CUSTOM' });
    assert.match(card, /^<svg xmlns="http:\/\/www.w3.org\/2000\/svg"/);
    assert.ok(card.includes(app.escapeXml(mission.title)));
    assert.ok(card.includes('PLAN ONLY / NO CUSTOM BRIEF'));
    assert.doesNotMatch(card, /PRIVATE|<script|<foreignObject|\son\w+\s*=|\b(?:href|src)\s*=|url\(/i);
    assert.match(card, /OWNER \/ /);
    assert.match(card, /REVIEW OWNER \/ /);
  }
});

test('malicious catalog text stays XML text, including attempted attribute and style breakouts', () => {
  const mission = fixture().missions[0];
  mission.title = '"><script>attack()</script>&';
  mission.summary = '</text><image href="https://evil.example/">';
  mission.stages[0].title = '</style><foreignObject onload="attack()">';
  mission.skills[0].id = '</text><script>bad()</script>';
  const card = app.createMissionCard(mission);
  assert.doesNotMatch(card, /<script|<image|<foreignObject/);
  assert.ok(card.includes('&lt;script&gt;'));
  assert.ok(card.includes('&quot;'));
});

test('text wrapping handles long words without dropping characters', () => {
  assert.deepEqual(app.wrapText('one two three', 7), ['one two', 'three']);
  assert.deepEqual(app.wrapText('abcdefghij', 4), ['abcd', 'efgh', 'ij']);
});

test('skill metrics correspond to actual unique manual files, not prompt or runtime size', () => {
  const skillsRoot = path.join(root, 'skills');
  const manuals = fs.readdirSync(skillsRoot).filter(name => fs.existsSync(path.join(skillsRoot, name, 'SKILL.md')));
  const allBytes = manuals.reduce((sum, name) => sum + fs.readFileSync(path.join(skillsRoot, name, 'SKILL.md')).length, 0);
  assert.equal(manuals.length, 54);
  for (const mission of published.missions) {
    const selectedBytes = mission.skills.reduce((sum, skill) => sum + fs.readFileSync(path.join(skillsRoot, skill.id, 'SKILL.md')).length, 0);
    assert.equal(mission.metrics.selectedSkillBytes, selectedBytes);
    assert.equal(mission.metrics.allSkillBytes, allBytes);
    assert.equal(app.readingReduction(mission.metrics), Math.round((1 - selectedBytes / allBytes) * 100));
  }
  assert.equal(app.readingReduction({ selectedSkillBytes: 100, allSkillBytes: 100 }), 0);
  assert.throws(() => app.readingReduction({ selectedSkillBytes: 100, allSkillBytes: 0 }));
  assert.throws(() => app.readingReduction({ selectedSkillBytes: 200, allSkillBytes: 100 }));
});

test('malformed catalog variants fail helpfully instead of producing misleading plans', () => {
  const mutations = [
    data => { data.schemaVersion = 2; },
    data => { data.source = 'other'; },
    data => { data.skillCount = 49; },
    data => { data.missions.pop(); },
    data => { data.missions[1].id = 'launch'; },
    data => { data.missions[0].title = null; },
    data => { data.missions[0].sampleBrief = '\u0000'; },
    data => { data.missions[0].departments = ['unknown']; },
    data => { data.missions[0].departments.push('developers'); },
    data => { data.missions[0].skills.push(data.missions[0].skills[0]); },
    data => { data.missions[0].metrics.selectedSkillBytes = Infinity; },
    data => { data.missions[0].metrics.allSkillBytes = 0; },
    data => { data.missions[0].metrics.selectedSkillBytes = 1001; },
    data => { data.missions[0].metrics.selectedSkills = 2; },
    data => { data.missions[0].stages = []; },
    data => { data.missions[0].stages[0].needs = ['future']; },
    data => { data.missions[0].stages[0].needs = ['review']; },
    data => { data.missions[0].stages[0].skills = ['unknown']; },
    data => { data.missions[0].stages[0].review = false; },
    data => { data.missions[0].stages[0].deliverables = []; },
    data => { data.missions[0].stages[0].checks = [null]; }
  ];
  for (const value of [undefined, null, [], {}, { missions: [] }]) assert.equal(app.validateDataset(value).valid, false);
  for (const mutate of mutations) { const data = fixture(); mutate(data); const result = app.validateDataset(data); assert.equal(result.valid, false, mutate.toString()); assert.match(result.message, /catalog could not be loaded/); }
});

// A minimal document harness exercises state and events. Real browser layout and
// native clipboard/download behavior are verified separately in browser QA.
function browserHarness(data = fixture(), href = 'file:///studio/missions.html', clipboard) {
  class Element {
    constructor(tag = 'div') { this.tag = tag; this.children = []; this.attributes = {}; this.listeners = {}; this.dataset = {}; this.value = ''; this.hidden = false; this.textContent = ''; }
    append(...children) { this.children.push(...children); }
    replaceChildren(...children) { this.children = children; }
    setAttribute(name, value) { this.attributes[name] = value; }
    addEventListener(name, listener) { this.listeners[name] = listener; }
    querySelectorAll(selector) { return this.children.flatMap(child => [...(selector === 'button' && child.tag === 'button' ? [child] : []), ...child.querySelectorAll(selector)]); }
    focus() { this.focused = true; }
    select() { this.selected = true; }
    click() { return this.listeners.click ? this.listeners.click() : undefined; }
    remove() { this.removed = true; }
  }
  const ids = new Map();
  const exports = ['copy-prompt', 'download-prompt', 'download-plan', 'download-card', 'share-preset'];
  const document = { readyState: 'complete', body: new Element('body'), createElement: tag => new Element(tag), getElementById(id) { if (!ids.has(id)) ids.set(id, new Element(exports.includes(id) ? 'button' : 'div')); return ids.get(id); }, querySelectorAll: () => exports.map(id => document.getElementById(id)) };
  const url = new URL(href);
  const window = { document, CLAUDE_INC_MISSIONS: data, location: { href, hash: url.hash }, navigator: { clipboard }, addEventListener(name, listener) { this[name] = listener; }, setTimeout(callback) { callback(); }, URL: { createObjectURL() { return 'blob:test'; }, revokeObjectURL(value) { window.revoked = value; } } };
  vm.runInNewContext(source, { window, URL, TextEncoder, Blob });
  return { window, document, get: id => document.getElementById(id) };
}

test('the browser entry point displays a helpful missing-data error', () => {
  const harness = browserHarness(null);
  assert.equal(harness.get('load-error').hidden, false);
  assert.match(harness.get('load-error').textContent, /catalog could not be loaded/);
});

test('mission switching retains per-mission drafts in memory and an invalid draft disables every export', () => {
  const harness = browserHarness();
  const brief = harness.get('mission-brief');
  brief.value = '  Private launch draft 🚀  ';
  brief.listeners.input();
  const buttons = harness.get('mission-nav').children;
  buttons[1].click();
  assert.equal(brief.value, fixture().missions[1].sampleBrief);
  brief.value = 'Validation draft';
  brief.listeners.input();
  buttons[0].click();
  assert.equal(brief.value, '  Private launch draft 🚀  ');
  brief.value = '\t\n';
  brief.listeners.input();
  for (const id of ['copy-prompt', 'download-prompt', 'download-plan', 'download-card', 'share-preset']) assert.equal(harness.get(id).disabled, true);
  assert.equal(harness.get('prompt-text').value, '');
  assert.equal(brief.attributes['aria-invalid'], 'true');
  assert.equal(harness.get('brief-error').hidden, false);
});

test('catalog and user text render through inert text fields without HTML injection APIs', () => {
  assert.doesNotMatch(source, /\.innerHTML\b|\.outerHTML\b|insertAdjacentHTML|document\.write\b|\bfetch\s*\(|localStorage|sessionStorage/);
  const data = fixture();
  data.missions[0].title = '<script>attack()</script>';
  const harness = browserHarness(data);
  assert.equal(harness.get('mission-title').textContent, '<script>attack()</script>');
  const brief = harness.get('mission-brief');
  brief.value = '</textarea><script>attack()</script>';
  brief.listeners.input();
  assert.equal(harness.get('prompt-text').value, app.composePrompt(data.missions[0], brief.value));
});

test('missing or rejected clipboard access shows a visible manual-copy fallback without false success', async () => {
  for (const clipboard of [undefined, { writeText: () => Promise.reject(new Error('Denied')) }]) {
    const harness = browserHarness(fixture(), 'file:///private/index.html', clipboard);
    harness.get('copy-prompt').click();
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(harness.get('copy-fallback').hidden, false);
    assert.equal(harness.get('manual-copy').value, app.composePrompt(fixture().missions[0], fixture().missions[0].sampleBrief));
    assert.match(harness.get('action-status').textContent, /unavailable/);
    assert.doesNotMatch(harness.get('action-status').textContent, /prompt copied/);
    assert.equal(harness.get('manual-copy').selected, true);
  }
});

test('successful copying reports success only after the clipboard promise resolves', async () => {
  let complete;
  let copied;
  const harness = browserHarness(fixture(), 'https://example.com/studio/', { writeText(value) { copied = value; return new Promise(resolve => { complete = resolve; }); } });
  harness.get('copy-prompt').click();
  assert.equal(harness.get('action-status').textContent, '');
  complete();
  await new Promise(resolve => setImmediate(resolve));
  assert.match(harness.get('action-status').textContent, /Complete prompt copied/);
  assert.equal(copied, app.composePrompt(fixture().missions[0], fixture().missions[0].sampleBrief));
});

test('clipboard responses cannot overwrite status or resurrect an old brief after a mission change', async () => {
  let reject;
  const harness = browserHarness(fixture(), 'https://example.com/', { writeText() { return new Promise((_, fail) => { reject = fail; }); } });
  harness.get('copy-prompt').click();
  harness.get('mission-nav').children[1].click();
  reject(new Error('Denied'));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(harness.get('copy-fallback').hidden, true);
  assert.match(harness.get('action-status').textContent, /Mission validate selected/);
});

test('a newer export supersedes pending clipboard feedback without exposing stale private data', async () => {
  let reject;
  const harness = browserHarness(fixture(), 'https://example.com/', { writeText() { return new Promise((_, fail) => { reject = fail; }); } });
  harness.get('copy-prompt').click();
  harness.get('download-card').click();
  reject(new Error('Denied'));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(harness.get('copy-fallback').hidden, true);
  assert.match(harness.get('action-status').textContent, /Download requested/);
});

test('local sharing exposes only a preset name and hosted sharing excludes private text', async () => {
  for (const href of ['file:///private/studio/index.html', 'http://localhost:8765/?brief=PRIVATE', 'https://example.com/studio/?brief=PRIVATE']) {
    const harness = browserHarness(fixture(), href);
    harness.get('mission-brief').value = 'PRIVATE';
    harness.get('mission-brief').listeners.input();
    harness.get('share-preset').click();
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(harness.get('manual-copy').value, app.presetShare(href, fixture().missions[0]).text);
    assert.ok(!harness.get('manual-copy').value.includes('PRIVATE'));
  }
});

test('downloads request the correct file and revoke the temporary blob URL', () => {
  const harness = browserHarness();
  harness.get('download-card').click();
  const link = harness.document.body.children.at(-1);
  assert.equal(link.download, 'claude-inc-launch-blueprint.svg');
  assert.equal(link.removed, true);
  assert.equal(harness.window.revoked, 'blob:test');
  assert.match(harness.get('action-status').textContent, /Download requested/);
});

test('download failures report failure and release any allocated URL', () => {
  const harness = browserHarness();
  harness.document.body.append = () => { throw new Error('Browser denied download'); };
  harness.get('download-prompt').click();
  assert.equal(harness.window.revoked, 'blob:test');
  assert.match(harness.get('action-status').textContent, /could not start the download/);
  assert.doesNotMatch(harness.get('action-status').textContent, /Download requested/);
});

test('invalid initial hashes use the safe default and explain how to choose another mission', () => {
  const harness = browserHarness(fixture(), 'https://example.com/#mission=launch&brief=PRIVATE');
  assert.equal(harness.get('mission-title').textContent, 'Mission launch');
  assert.match(harness.get('action-status').textContent, /not recognized/);
  const selected = browserHarness(fixture(), 'https://example.com/#mission=proposal');
  assert.equal(selected.get('mission-title').textContent, 'Mission proposal');
});
