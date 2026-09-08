/* Mission Studio: classic script, no network or browser storage required. */
(function (root) {
  'use strict';

  const MISSION_IDS = Object.freeze(['launch', 'validate', 'release', 'proposal', 'content']);
  const MAX_BRIEF_BYTES = 8000;
  const CATEGORIES = Object.freeze({ launch: 'Go to market', validate: 'Discovery', release: 'Engineering', proposal: 'Sales', content: 'Editorial' });
  const DEPARTMENTS = Object.freeze({ developers: 'Developers', designers: 'Designers', marketing: 'Marketing', 'social-media': 'Social media', finance: 'Finance', 'small-business': 'Small business', legal: 'Legal', sales: 'Sales' });
  const NUMBER = new Intl.NumberFormat('en-US');

  function byteLength(value) {
    return new TextEncoder().encode(value).length;
  }

  function hasUnpairedSurrogate(value) {
    for (let index = 0; index < value.length; index += 1) {
      const code = value.charCodeAt(index);
      if (code >= 0xd800 && code <= 0xdbff) {
        const next = value.charCodeAt(index + 1);
        if (!(next >= 0xdc00 && next <= 0xdfff)) return true;
        index += 1;
      } else if (code >= 0xdc00 && code <= 0xdfff) return true;
    }
    return false;
  }

  function validateBrief(value) {
    if (typeof value !== 'string') return { valid: false, bytes: 0, message: 'Enter a mission brief to create your prompt.' };
    const bytes = byteLength(value);
    if (hasUnpairedSurrogate(value)) return { valid: false, bytes, message: 'Your brief contains an incomplete Unicode character. Remove or replace it to export.' };
    if (/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f]/.test(value)) return { valid: false, bytes, message: 'Remove control characters from your brief. Tabs and line breaks are allowed.' };
    if (!/[^\t\n\r \u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]/.test(value)) return { valid: false, bytes, message: 'Add a little context first: what are you working on, and what should the crew deliver?' };
    if (bytes > MAX_BRIEF_BYTES) return { valid: false, bytes, message: 'Your brief is ' + NUMBER.format(bytes - MAX_BRIEF_BYTES) + ' bytes over the 8,000-byte limit. Shorten it before exporting.' };
    return { valid: true, bytes, message: '' };
  }

  function parseMissionHash(hash) {
    if (typeof hash !== 'string') return null;
    const match = /^#mission=(launch|validate|release|proposal|content)$/.exec(hash);
    return match ? match[1] : null;
  }

  function presetShare(href, mission) {
    if (!mission || !MISSION_IDS.includes(mission.id)) throw new Error('Choose a valid mission preset.');
    let url;
    try { url = new URL(href); } catch (_) { url = null; }
    const localHost = url && (/^localhost\.?$/i.test(url.hostname) || /\.localhost\.?$/i.test(url.hostname) || /^127(?:\.\d{1,3}){3}$/.test(url.hostname) || url.hostname === '[::1]');
    if (url && !localHost && (url.protocol === 'https:' || url.protocol === 'http:')) {
      return { local: false, text: url.origin + url.pathname + '#mission=' + mission.id };
    }
    return { local: true, text: 'Claude, Inc. Mission Studio — ' + mission.title + ' (preset: ' + mission.id + ')' };
  }

  function validateDataset(data) {
    const fail = message => ({ valid: false, message: 'The mission catalog could not be loaded. ' + message + ' Reopen studio/missions.html from a complete checkout, or regenerate studio/missions.js with scripts/build_studio.py.' });
    const text = value => typeof value === 'string' && value.trim().length > 0;
    const texts = value => Array.isArray(value) && value.length > 0 && value.every(text);
    const unique = value => new Set(value).size === value.length;
    if (!data || data.schemaVersion !== 1 || data.source !== 'alebgl77/claude-inc' || data.skillCount !== 50 || !Array.isArray(data.missions) || data.missions.length !== 5) return fail('The data is missing or uses an unsupported format.');
    const seen = new Set();
    for (const mission of data.missions) {
      if (!mission || !MISSION_IDS.includes(mission.id) || seen.has(mission.id)) return fail('A preset is missing, duplicated, or unknown.');
      seen.add(mission.id);
      if (!['title', 'summary', 'outcome', 'sampleBrief', 'promptPrefix', 'promptSuffix', 'planMarkdown'].every(key => text(mission[key])) || !validateBrief(mission.sampleBrief).valid) return fail('A preset is incomplete.');
      if (!texts(mission.departments) || !unique(mission.departments) || !mission.departments.every(department => Object.prototype.hasOwnProperty.call(DEPARTMENTS, department))) return fail('A department is invalid.');
      if (!Array.isArray(mission.skills) || !mission.skills.length || !mission.skills.every(skill => skill && text(skill.id) && mission.departments.includes(skill.department)) || !unique(mission.skills.map(skill => skill.id))) return fail('The employee manifest is invalid.');
      const metrics = mission.metrics;
      if (!metrics || !['selectedSkillBytes', 'allSkillBytes', 'selectedSkills', 'totalSkills'].every(key => Number.isSafeInteger(metrics[key]) && metrics[key] > 0) || metrics.selectedSkillBytes > metrics.allSkillBytes || metrics.selectedSkills !== mission.skills.length || metrics.totalSkills !== data.skillCount || metrics.selectedSkills > metrics.totalSkills) return fail('The skill-size measurements are invalid.');
      if (!Array.isArray(mission.stages) || !mission.stages.length) return fail('A workflow is missing.');
      const prior = new Set();
      const usedSkills = new Set();
      for (const stage of mission.stages) {
        if (!stage || !text(stage.id) || prior.has(stage.id) || !text(stage.title) || !mission.departments.includes(stage.department) || typeof stage.review !== 'boolean' || !texts(stage.skills) || !unique(stage.skills) || !texts(stage.deliverables) || !texts(stage.checks) || !Array.isArray(stage.needs) || !unique(stage.needs) || !stage.needs.every(id => prior.has(id))) return fail('A workflow has an invalid stage or dependency.');
        if (!stage.skills.every(id => mission.skills.some(skill => skill.id === id && skill.department === stage.department))) return fail('A stage names an employee outside its department.');
        stage.skills.forEach(id => usedSkills.add(id));
        prior.add(stage.id);
      }
      if (usedSkills.size !== mission.skills.length || !mission.stages.some(stage => stage.review)) return fail('The crew or review stage is incomplete.');
    }
    return { valid: true, message: '' };
  }

  function composePrompt(mission, brief) {
    const validation = validateBrief(brief);
    if (!validation.valid) throw new Error(validation.message);
    return mission.promptPrefix + brief + mission.promptSuffix;
  }

  function composePlan(mission, brief) {
    const validation = validateBrief(brief);
    if (!validation.valid) throw new Error(validation.message);
    const fences = brief.match(/`+/g) || [];
    const fence = '`'.repeat(Math.max(3, ...fences.map(value => value.length + 1)));
    return mission.planMarkdown + '\n\n## Your mission brief (literal task data)\n\n' + fence + 'text\n' + brief + '\n' + fence + '\n';
  }

  function readingReduction(metrics) {
    if (!metrics || !Number.isSafeInteger(metrics.selectedSkillBytes) || !Number.isSafeInteger(metrics.allSkillBytes) || metrics.allSkillBytes <= 0 || metrics.selectedSkillBytes < 0 || metrics.selectedSkillBytes > metrics.allSkillBytes) throw new Error('Invalid skill-size measurements.');
    return Math.round((1 - metrics.selectedSkillBytes / metrics.allSkillBytes) * 100);
  }

  function escapeXml(value) {
    return String(value).replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[character])).replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\ufffe\uffff]/g, '');
  }

  function humanize(value) {
    return String(value).split('-').map(word => /^(ai|api|b2b|cro|cto|cfo|qa|seo|ui|ux)$/i.test(word) ? word.toUpperCase() : word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  }

  function wrapText(value, maxCharacters) {
    const lines = [];
    let line = '';
    for (const word of String(value).trim().split(/\s+/)) {
      if (line && line.length + word.length + 1 > maxCharacters) { lines.push(line); line = ''; }
      if (word.length > maxCharacters) {
        if (line) { lines.push(line); line = ''; }
        for (let start = 0; start < word.length; start += maxCharacters) {
          const piece = word.slice(start, start + maxCharacters);
          if (piece.length === maxCharacters) lines.push(piece); else line = piece;
        }
      } else line = line ? line + ' ' + word : word;
    }
    if (line) lines.push(line);
    return lines;
  }

  function createMissionCard(mission) {
    const e = escapeXml;
    const lines = [];
    const svgText = (x, y, value, style) => '<text x="' + x + '" y="' + y + '" class="' + style + '">' + e(value) + '</text>';
    const titleLines = wrapText(mission.title, 34);
    const summaryLines = wrapText(mission.summary, 102);
    const contentTop = 195 + titleLines.length * 66 + summaryLines.length * 25;
    const stageHeights = mission.stages.map(stage => 68 + wrapText(stage.title, 44).length * 24);
    const crewHeight = mission.departments.reduce((sum, department) => sum + 53 + mission.skills.filter(skill => skill.department === department).reduce((height, skill) => height + wrapText(humanize(skill.id), 30).length * 23, 0), 80);
    const bodyHeight = Math.max(stageHeights.reduce((sum, height) => sum + height, 0) + 45, crewHeight);
    const height = contentTop + bodyHeight + 95;
    lines.push('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="' + height + '" viewBox="0 0 1200 ' + height + '" role="img" aria-labelledby="card-title card-description">');
    lines.push('<title id="card-title">' + e('Mission blueprint: ' + mission.title) + '</title><desc id="card-description">A Claude, Inc. mission template with an ordered workflow and selected crew. This is a plan, not completed work. No custom brief is included.</desc>');
    lines.push('<style>text{fill:#25271f;font-family:Trebuchet MS,Segoe UI,sans-serif}.mono{font-family:Consolas,Liberation Mono,monospace;font-size:12px;letter-spacing:1px}.brand{font-family:Georgia,serif;font-size:32px;font-weight:bold}.title{font-family:Georgia,serif;font-size:61px;letter-spacing:-2px}.summary{font-size:18px;fill:#66695b}.stage{font-size:20px}.note{font-family:Consolas,monospace;font-size:12px;fill:#66695b}.accent{fill:#b9462c}.light{fill:#f6f3eb}.crew{font-size:17px;fill:#f6f3eb}.crew-label{font-family:Consolas,monospace;font-size:11px;letter-spacing:1px;fill:#c6c4b4}.number{font-family:Consolas,monospace;font-size:13px;fill:#f6f3eb}.footer{font-family:Georgia,serif;font-size:19px;font-style:italic;fill:#66695b}</style>');
    lines.push('<rect width="1200" height="' + height + '" fill="#f6f3eb"/><rect x="0" y="0" width="1200" height="9" fill="#b9462c"/>');
    lines.push(svgText(55, 70, 'claude, inc.', 'brand'), svgText(760, 66, 'MISSION STUDIO / THE BLUEPRINT', 'mono'));
    lines.push('<path d="M55 101H1145" stroke="#25271f"/>', svgText(55, 139, 'MISSION ' + String(MISSION_IDS.indexOf(mission.id) + 1).padStart(2, '0') + ' / ' + mission.id.toUpperCase(), 'mono accent'));
    titleLines.forEach((line, index) => lines.push(svgText(52, 205 + index * 66, line, 'title')));
    summaryLines.forEach((line, index) => lines.push(svgText(55, 185 + titleLines.length * 66 + index * 25, line, 'summary')));
    lines.push('<path d="M55 ' + (contentTop - 12) + 'H1145" stroke="#25271f"/>');
    lines.push(svgText(55, contentTop + 20, 'THE RUN OF SHOW / ' + mission.stages.length + ' STAGES', 'mono'));
    let stageTop = contentTop + 45;
    mission.stages.forEach((stage, index) => {
      if (index < mission.stages.length - 1) lines.push('<path d="M74 ' + (stageTop + 34) + 'V' + (stageTop + stageHeights[index]) + '" stroke="#d7d3c6"/>');
      lines.push('<rect x="55" y="' + stageTop + '" width="38" height="38" fill="' + (stage.review ? '#b9462c' : '#25271f') + '"/>');
      lines.push(svgText(65, stageTop + 24, String(index + 1).padStart(2, '0'), 'number'));
      const title = wrapText(stage.title, 44);
      title.forEach((line, lineIndex) => lines.push(svgText(112, stageTop + 17 + lineIndex * 24, line, 'stage')));
      const ownerY = stageTop + 20 + title.length * 24;
      lines.push(svgText(112, ownerY, (stage.review ? 'REVIEW OWNER / ' : 'OWNER / ') + DEPARTMENTS[stage.department].toUpperCase(), 'note'));
      const deps = stage.needs.map(id => String(mission.stages.findIndex(item => item.id === id) + 1).padStart(2, '0')).join(', ');
      lines.push(svgText(112, ownerY + 21, deps ? 'AFTER ' + deps + ' / ' + stage.deliverables.length + ' DELIVERABLES' : 'START HERE / ' + stage.deliverables.length + ' DELIVERABLES', 'note'));
      stageTop += stageHeights[index];
    });
    lines.push('<rect x="786" y="' + (contentTop + 4) + '" width="359" height="' + (bodyHeight - 4) + '" fill="#25271f"/>');
    lines.push(svgText(814, contentTop + 38, 'THE CREW / ' + mission.skills.length + ' EMPLOYEES', 'mono light'));
    let crewTop = contentTop + 79;
    mission.departments.forEach(department => {
      lines.push(svgText(814, crewTop, DEPARTMENTS[department].toUpperCase(), 'crew-label'));
      crewTop += 29;
      mission.skills.filter(skill => skill.department === department).forEach(skill => {
        wrapText(humanize(skill.id), 30).forEach(line => { lines.push(svgText(814, crewTop, line, 'crew')); crewTop += 23; });
      });
      crewTop += 24;
    });
    lines.push('<path d="M55 ' + (height - 66) + 'H1145" stroke="#d7d3c6"/>', svgText(55, height - 30, 'A focused crew. A visible hand-off. A definition of done.', 'footer'), svgText(819, height - 30, 'PLAN ONLY / NO CUSTOM BRIEF', 'note'));
    lines.push('</svg>');
    return lines.join('\n');
  }

  const api = Object.freeze({ MISSION_IDS, MAX_BRIEF_BYTES, byteLength, validateBrief, validateDataset, parseMissionHash, presetShare, composePrompt, composePlan, readingReduction, escapeXml, createMissionCard, wrapText });
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (!root || !root.document) return;

  function boot() {
    const document = root.document;
    const byId = id => document.getElementById(id);
    const element = (tag, className, value) => {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (value !== undefined) node.textContent = value;
      return node;
    };
    const catalog = root.CLAUDE_INC_MISSIONS;
    const datasetCheck = validateDataset(catalog);
    if (!datasetCheck.valid) { byId('load-error').textContent = datasetCheck.message; byId('load-error').hidden = false; return; }
    const missions = MISSION_IDS.map(id => catalog.missions.find(mission => mission.id === id));
    const drafts = new Map(missions.map(mission => [mission.id, mission.sampleBrief]));
    let current;
    let editRevision = 0;
    const status = message => { byId('action-status').textContent = message; };
    const hideFallback = () => { byId('copy-fallback').hidden = true; byId('manual-copy').value = ''; };

    function updateBrief() {
      const value = byId('mission-brief').value;
      drafts.set(current.id, value);
      editRevision += 1;
      const check = validateBrief(value);
      byId('brief-size').textContent = NUMBER.format(check.bytes) + ' / 8,000 B';
      byId('mission-brief').setAttribute('aria-invalid', String(!check.valid));
      byId('brief-error').textContent = check.message;
      byId('brief-error').hidden = check.valid;
      byId('brief-kind').textContent = value === current.sampleBrief ? 'EXAMPLE · EDIT ME' : 'YOUR DRAFT';
      document.querySelectorAll('[data-export]').forEach(button => { button.disabled = !check.valid; });
      byId('prompt-text').value = check.valid ? composePrompt(current, value) : '';
      hideFallback();
      status('');
      return check.valid;
    }

    function renderMission(id, announce) {
      current = missions.find(mission => mission.id === id) || missions[0];
      const missionIndex = MISSION_IDS.indexOf(current.id);
      byId('mission-reference').textContent = 'MISSION ' + String(missionIndex + 1).padStart(2, '0');
      byId('mission-title').textContent = current.title;
      byId('mission-summary').textContent = current.summary;
      byId('mission-outcome').textContent = current.outcome;
      byId('crew-count').textContent = String(current.skills.length);
      byId('stage-count').textContent = String(current.stages.length).padStart(2, '0');
      byId('reading-reduction').textContent = readingReduction(current.metrics) + '%';
      document.title = current.title + ' — Mission Studio';
      byId('mission-nav').querySelectorAll('button').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.mission === current.id)));
      byId('stage-list').replaceChildren();
      current.stages.forEach((stage, index) => {
        const item = element('li');
        const details = element('details', 'stage' + (stage.review ? ' review-stage' : ''));
        details.open = index === 0;
        const summary = element('summary');
        const title = element('span');
        title.append(element('span', 'stage-title', stage.title));
        const meta = element('span', 'stage-meta');
        meta.append(element('span', stage.review ? 'review-label' : '', (stage.review ? 'Review owner' : 'Owner') + ' · ' + DEPARTMENTS[stage.department]));
        const dependencies = stage.needs.map(id => String(current.stages.findIndex(candidate => candidate.id === id) + 1).padStart(2, '0')).join(', ');
        meta.append(element('span', '', dependencies ? ' / After ' + dependencies : ' / Starts here'));
        title.append(meta);
        const toggle = element('span', 'stage-toggle', '+');
        toggle.setAttribute('aria-hidden', 'true');
        summary.append(element('span', 'stage-number', String(index + 1).padStart(2, '0')), title, toggle);
        const body = element('div', 'stage-body');
        body.append(element('p', 'stage-kicker', 'Hand off these files'));
        const deliverables = element('ul');
        stage.deliverables.forEach(value => deliverables.append(element('li', '', value)));
        body.append(deliverables, element('p', 'stage-kicker', 'Definition of done · checks not yet run'));
        const checks = element('ul');
        stage.checks.forEach(value => checks.append(element('li', '', value)));
        body.append(checks);
        if (stage.review) body.append(element('p', 'stage-handoff', 'Use a reviewer distinct from the producing assignments. Disclose any single-assistant review limitation.'));
        const nextOwners = [...new Set(current.stages.filter(candidate => candidate.needs.includes(stage.id)).map(candidate => DEPARTMENTS[candidate.department]))];
        body.append(element('p', 'stage-handoff', nextOwners.length ? 'Next hand-off → ' + nextOwners.join(' + ') : 'Final hand-off → Founder review'));
        body.append(element('p', 'stage-crew', 'Assigned: ' + stage.skills.map(humanize).join(' · ')));
        details.append(summary, body);
        item.append(details);
        byId('stage-list').append(item);
      });
      byId('crew-list').replaceChildren();
      current.skills.forEach(skill => { const item = element('li'); item.append(element('span', 'crew-name', humanize(skill.id)), element('span', 'crew-department', DEPARTMENTS[skill.department])); byId('crew-list').append(item); });
      byId('reading-explanation').textContent = NUMBER.format(current.metrics.selectedSkillBytes) + ' bytes of selected employee manuals / ' + NUMBER.format(current.metrics.allSkillBytes) + ' bytes across the company. CEO and department manuals, plus your brief, are additional context in the complete prompt.';
      byId('mission-brief').value = drafts.get(current.id);
      updateBrief();
      if (announce) status(current.title + ' selected. Your draft for this mission is ready to edit.');
    }

    missions.forEach((mission, index) => {
      const button = element('button', 'mission-option');
      button.type = 'button';
      button.dataset.mission = mission.id;
      button.setAttribute('aria-pressed', 'false');
      button.setAttribute('aria-controls', 'studio-content');
      const label = element('span');
      label.append(element('span', 'mission-option-name', mission.title), element('span', 'mission-option-kind', CATEGORIES[mission.id]));
      const arrow = element('span', 'mission-arrow', '↗');
      arrow.setAttribute('aria-hidden', 'true');
      button.append(element('span', 'mission-number', String(index + 1).padStart(2, '0')), label, arrow);
      button.addEventListener('click', () => {
        renderMission(mission.id, true);
        root.location.hash = 'mission=' + mission.id;
      });
      byId('mission-nav').append(button);
    });

    async function copyText(text, success, revision, fallbackMessage) {
      hideFallback();
      try {
        if (!root.navigator.clipboard || typeof root.navigator.clipboard.writeText !== 'function') throw new Error('Clipboard unavailable');
        await root.navigator.clipboard.writeText(text);
        if (revision === editRevision) status(success);
      } catch (_) {
        if (revision !== editRevision) return;
        byId('manual-copy').value = text;
        byId('copy-fallback').hidden = false;
        status(fallbackMessage || 'Automatic copying is unavailable. Your text is ready to copy manually below.');
        byId('manual-copy').focus();
        byId('manual-copy').select();
      }
    }

    function download(text, name, mime) {
      let url;
      let link;
      try {
        url = root.URL.createObjectURL(new Blob([text], { type: mime }));
        link = element('a');
        link.href = url;
        link.download = name;
        link.hidden = true;
        document.body.append(link);
        link.click();
        status('Download requested: ' + name + '. Check your browser’s downloads.');
      } catch (_) { status('This browser could not start the download. Try copying the prompt, or open this folder in another browser.'); }
      finally {
        if (link) link.remove();
        if (url) root.setTimeout(() => root.URL.revokeObjectURL(url), 1000);
      }
    }

    function withBrief(action) {
      const value = byId('mission-brief').value;
      if (!validateBrief(value).valid) { updateBrief(); byId('mission-brief').focus(); return; }
      hideFallback();
      editRevision += 1;
      action(value);
    }

    byId('mission-brief').addEventListener('input', updateBrief);
    byId('copy-prompt').addEventListener('click', () => withBrief(brief => copyText(composePrompt(current, brief), 'Complete prompt copied. Paste it into your assistant to start the mission.', editRevision)));
    byId('download-prompt').addEventListener('click', () => withBrief(brief => download(composePrompt(current, brief), 'claude-inc-' + current.id + '-prompt.md', 'text/markdown;charset=utf-8')));
    byId('download-plan').addEventListener('click', () => withBrief(brief => download(composePlan(current, brief), 'claude-inc-' + current.id + '-plan.md', 'text/markdown;charset=utf-8')));
    byId('download-card').addEventListener('click', () => withBrief(() => download(createMissionCard(current), 'claude-inc-' + current.id + '-blueprint.svg', 'image/svg+xml;charset=utf-8')));
    byId('share-preset').addEventListener('click', () => withBrief(() => {
      const share = presetShare(root.location.href, current);
      const message = share.local ? 'This is a local preview, so its address cannot be shared publicly. Preset name copied; share it with someone who has Mission Studio.' : 'Preset link copied. It contains only the mission selection, never your custom brief.';
      const fallback = share.local ? 'This is a local preview, so its address cannot be shared publicly. Copy the preset name below; your custom brief is excluded.' : 'Automatic copying is unavailable. Copy the preset link below; your custom brief is excluded.';
      copyText(share.text, message, editRevision, fallback);
    }));
    byId('select-copy').addEventListener('click', () => { byId('manual-copy').focus(); byId('manual-copy').select(); status('Text selected. Use your device’s copy command.'); });
    root.addEventListener('hashchange', () => {
      const id = parseMissionHash(root.location.hash);
      if (id && id !== current.id) renderMission(id, true);
      else if (!id && root.location.hash) status('That preset address is not recognized. Choose a mission from the index.');
    });
    renderMission(parseMissionHash(root.location.hash) || 'launch', false);
    if (root.location.hash && !parseMissionHash(root.location.hash)) status('That preset address is not recognized. The first mission is selected; choose any mission from the index.');
    byId('studio-content').hidden = false;
  }

  if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})(typeof window !== 'undefined' ? window : null);
