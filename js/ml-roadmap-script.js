  <script>
  (() => {
    const STORAGE_KEY = 'goroyeh56-ml-roadmap-v3';

    // ════════════════════════════════════════════════════════════════════
    // PYTHON SYNTAX HIGHLIGHTER
    // ════════════════════════════════════════════════════════════════════
    const PY_KEYWORDS = new Set([
      'False','None','True','and','as','assert','async','await',
      'break','class','continue','def','del','elif','else','except',
      'finally','for','from','global','if','import','in','is','lambda',
      'nonlocal','not','or','pass','raise','return','try','while','with','yield'
    ]);
    const PY_BUILTINS = new Set([
      'print','len','range','type','int','float','str','list','dict',
      'set','tuple','bool','abs','max','min','sum','sorted','enumerate',
      'zip','map','filter','isinstance','hasattr','getattr','setattr',
      'open','input','super','object','property','staticmethod','classmethod',
      'round','repr','format','id','hash','iter','next','reversed','any','all'
    ]);

    function highlightPython(code) {
      // Process line by line to handle comments correctly
      return code.split('\n').map(line => highlightLine(line)).join('\n');
    }

    function highlightLine(line) {
      // Find comment position (outside strings)
      let inStr = false, strChar = '', commentIdx = -1;
      for (let i = 0; i < line.length; i++) {
        const ch = line[i];
        if (!inStr && (ch === '"' || ch === "'")) {
          // Check triple-quote
          if (line.slice(i, i+3) === ch.repeat(3)) { inStr = true; strChar = ch.repeat(3); i += 2; }
          else { inStr = true; strChar = ch; }
        } else if (inStr) {
          if (strChar.length === 3 && line.slice(i, i+3) === strChar) { inStr = false; i += 2; }
          else if (strChar.length === 1 && ch === strChar && line[i-1] !== '\\') { inStr = false; }
        } else if (!inStr && ch === '#') { commentIdx = i; break; }
      }

      let codePart = commentIdx >= 0 ? line.slice(0, commentIdx) : line;
      let commentPart = commentIdx >= 0 ? line.slice(commentIdx) : '';

      // Highlight the code part (tokens)
      codePart = highlightTokens(codePart);

      // Escape comment
      if (commentPart) {
        commentPart = `<span class="py-cm">${esc(commentPart)}</span>`;
      }
      return codePart + commentPart;
    }

    function highlightTokens(code) {
      // Tokenize: strings, numbers, identifiers, operators
      const tokens = [];
      let i = 0;
      while (i < code.length) {
        // Triple-quoted strings
        if ((code[i] === '"' || code[i] === "'") && code.slice(i, i+3) === code[i].repeat(3)) {
          const q = code[i].repeat(3);
          let end = code.indexOf(q, i + 3);
          if (end < 0) end = code.length - 3;
          const raw = code.slice(i, end + 3);
          tokens.push(`<span class="py-str">${esc(raw)}</span>`);
          i = end + 3; continue;
        }
        // Single/double quoted strings
        if (code[i] === '"' || code[i] === "'" || 
            (code[i] === 'f' && (code[i+1] === '"' || code[i+1] === "'")) ||
            (code[i] === 'r' && (code[i+1] === '"' || code[i+1] === "'")) ||
            (code[i] === 'b' && (code[i+1] === '"' || code[i+1] === "'"))) {
          const prefix = (code[i] !== '"' && code[i] !== "'") ? code[i] : '';
          const qi = i + prefix.length;
          const q = code[qi];
          let j = qi + 1;
          while (j < code.length && !(code[j] === q && code[j-1] !== '\\')) j++;
          const raw = code.slice(i, j + 1);
          tokens.push(`<span class="py-str">${esc(raw)}</span>`);
          i = j + 1; continue;
        }
        // Decorator
        if (code[i] === '@') {
          let j = i + 1;
          while (j < code.length && /[\w.]/.test(code[j])) j++;
          tokens.push(`<span class="py-dec">${esc(code.slice(i, j))}</span>`);
          i = j; continue;
        }
        // Numbers (int, float, scientific, hex)
        if (/[0-9]/.test(code[i]) || (code[i] === '.' && /[0-9]/.test(code[i+1]))) {
          let j = i;
          if (code[i] === '0' && (code[i+1] === 'x' || code[i+1] === 'X')) {
            j += 2; while (j < code.length && /[0-9a-fA-F_]/.test(code[j])) j++;
          } else {
            while (j < code.length && /[0-9._eEjJ]/.test(code[j])) j++;
          }
          tokens.push(`<span class="py-num">${esc(code.slice(i, j))}</span>`);
          i = j; continue;
        }
        // Identifiers / keywords
        if (/[a-zA-Z_]/.test(code[i])) {
          let j = i;
          while (j < code.length && /[\w]/.test(code[j])) j++;
          const word = code.slice(i, j);
          // Check if followed by '(' → function call
          const isCall = code.slice(j).trimStart()[0] === '(';
          if (PY_KEYWORDS.has(word)) {
            tokens.push(`<span class="py-kw">${esc(word)}</span>`);
          } else if (PY_BUILTINS.has(word) || isCall) {
            tokens.push(`<span class="py-fn">${esc(word)}</span>`);
          } else if (word[0] === word[0].toUpperCase() && word[0] !== '_') {
            tokens.push(`<span class="py-cls">${esc(word)}</span>`);
          } else {
            tokens.push(esc(word));
          }
          i = j; continue;
        }
        tokens.push(esc(code[i]));
        i++;
      }
      return tokens.join('');
    }

    function esc(s) {
      return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }

    // ════════════════════════════════════════════════════════════════════
    // MULTILINE OUTPUT RENDERER
    // ════════════════════════════════════════════════════════════════════
    function renderOutput(outputEl, stdout, stderr, imgData, status) {
      const lines = [];
      const allText = (stdout || '') + (stderr ? '\n' + stderr : '');

      if (!allText.trim() && !imgData) {
        outputEl.innerHTML = `<span class="out-line info">${esc(status || '✓ Ran (no output)')}</span>`;
        return;
      }

      let html = '';
      // Split stdout into individual lines with line numbers
      if (stdout && stdout.trim()) {
        const stdoutLines = stdout.split('\n');
        // Remove trailing empty lines
        while (stdoutLines.length > 0 && stdoutLines[stdoutLines.length-1].trim() === '') stdoutLines.pop();
        stdoutLines.forEach((line, idx) => {
          html += `<span class="out-line"><span class="out-line-num">${idx+1}</span>${esc(line)}</span>\n`;
        });
      }
      if (stderr && stderr.trim()) {
        stderr.split('\n').forEach(line => {
          if (line.trim()) html += `<span class="out-line err">${esc(line)}</span>\n`;
        });
      }
      if (imgData) {
        html += `<img class="out-img" src="${imgData}" alt="matplotlib output"/>`;
      }
      outputEl.innerHTML = html;
    }

    // ════════════════════════════════════════════════════════════════════
    // CODE FILE LOADER (fetch from code/ folder)
    // ════════════════════════════════════════════════════════════════════
    const codeCache = {};

    async function loadCodeFile(path) {
      if (codeCache[path]) return codeCache[path];
      try {
        const res = await fetch(path + '?_=' + Math.floor(Date.now()/60000)); // 1-min cache bust
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const text = await res.text();
        codeCache[path] = text;
        return text;
      } catch(e) {
        return null;
      }
    }

    // ════════════════════════════════════════════════════════════════════
    // JUDGE0 PYTHON RUNNER
    // ════════════════════════════════════════════════════════════════════
    const JUDGE0_ENDPOINT = 'https://judge0.sabe.io/submissions?base64_encoded=false&wait=true';
    const PYTHON_ID = 71;

    // Matplotlib capture shim injected before user code
    const PLOT_SHIM = `import sys,io,base64
_pimg=None
try:
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 _os=plt.savefig
 def _sf(f=None,*a,**k):
  global _pimg
  b=io.BytesIO();_os(b,*a,**k);b.seek(0)
  _pimg='data:image/png;base64,'+base64.b64encode(b.read()).decode()
  plt.close('all')
 plt.savefig=_sf
 _osh=plt.show
 def _sh():
  global _pimg
  b=io.BytesIO();plt.savefig(b,format='png',dpi=90,bbox_inches='tight')
  b.seek(0);_pimg='data:image/png;base64,'+base64.b64encode(b.read()).decode()
  plt.close('all')
 plt.show=_sh
except:pass
`;

    const PLOT_FOOTER = `
if '_pimg' in dir() and _pimg:print('__IMG__:'+_pimg)
elif 'plt' in dir():
 try:
  if plt.get_fignums():
   b=__import__('io').BytesIO()
   plt.savefig(b,format='png',dpi=90,bbox_inches='tight')
   b.seek(0)
   print('__IMG__:data:image/png;base64,'+__import__('base64').b64encode(b.read()).decode())
   plt.close('all')
 except:pass
`;

    async function runPython(code, outputEl) {
      outputEl.innerHTML = '<span class="out-line info">⏳ Submitting to Python runner…</span>';
      const fullCode = PLOT_SHIM + '\n' + code + '\n' + PLOT_FOOTER;
      try {
        const res = await fetch(JUDGE0_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ language_id: PYTHON_ID, source_code: fullCode }),
        });
        if (!res.ok) throw new Error(`Runner returned ${res.status}`);
        const result = await res.json();

        let stdout = result.stdout || '';
        const stderr = result.stderr || result.compile_output || '';
        const status = result.status?.description || '';

        // Extract embedded plot
        let imgData = null;
        const lines = stdout.split('\n');
        const cleanLines = [];
        for (const line of lines) {
          if (line.startsWith('__IMG__:')) { imgData = line.slice(8); }
          else { cleanLines.push(line); }
        }
        stdout = cleanLines.join('\n');
        renderOutput(outputEl, stdout, stderr, imgData, status);

      } catch(e) {
        outputEl.innerHTML = `<span class="out-line err">❌ ${esc(String(e))}</span>
<span class="out-line info">Try pasting into <a href="https://replit.com" target="_blank" style="color:#79c0ff">replit.com</a> or <a href="https://colab.research.google.com" target="_blank" style="color:#79c0ff">Google Colab</a></span>`;
      }
    }

    // ════════════════════════════════════════════════════════════════════
    // EDITOR PANEL: create with syntax highlighting textarea
    // ════════════════════════════════════════════════════════════════════
    function createEditorPanel(topicId, initialCode) {
      const highlighted = highlightPython(initialCode);
      return `<div class="editor-panel" id="editor-${topicId}">
        <div class="editor-toolbar">
          <span class="editor-toolbar-label">Python — edit &amp; run</span>
          <button class="clear-btn" onclick="clearOutput('${topicId}')">Clear</button>
          <button class="run-btn" id="runbtn-${topicId}" onclick="runCode('${topicId}')">
            <svg viewBox="0 0 12 12" fill="currentColor"><polygon points="2,1 11,6 2,11"/></svg> Run
          </button>
        </div>
        <div class="editor-wrap" style="position:relative;background:#0d1117;">
          <div class="editor-highlighted" id="hl-${topicId}" aria-hidden="true">${highlighted}</div>
          <textarea class="editor-textarea" id="edtxt-${topicId}" spellcheck="false"
            oninput="syncHighlight('${topicId}')"
            onscroll="syncScroll('${topicId}')"
            style="background:transparent;color:#e6edf3;position:relative;z-index:1;width:100%;min-height:130px;border:none;outline:none;resize:vertical;font-family:'SF Mono','Fira Code','Consolas',monospace;font-size:0.81rem;line-height:1.7;padding:0.9rem 1.2rem;tab-size:4;box-sizing:border-box;caret-color:#e6edf3;">${esc(initialCode)}</textarea>
        </div>
        <div class="editor-output" id="edout-${topicId}">
          <span class="out-line info">Click ▷ Run to execute Python</span>
        </div>
      </div>`;
    }

    // Sync highlight layer with textarea
    window.syncHighlight = (topicId) => {
      const ta = document.getElementById(`edtxt-${topicId}`);
      const hl = document.getElementById(`hl-${topicId}`);
      if (!ta || !hl) return;
      hl.innerHTML = highlightPython(ta.value);
      // Keep highlight scroll in sync
      hl.scrollTop  = ta.scrollTop;
      hl.scrollLeft = ta.scrollLeft;
    };

    window.syncScroll = (topicId) => {
      const ta = document.getElementById(`edtxt-${topicId}`);
      const hl = document.getElementById(`hl-${topicId}`);
      if (ta && hl) { hl.scrollTop = ta.scrollTop; hl.scrollLeft = ta.scrollLeft; }
    };

    // Tab key support
    document.addEventListener('keydown', e => {
      if (e.key === 'Tab' && e.target.classList.contains('editor-textarea')) {
        e.preventDefault();
        const ta = e.target, s = ta.selectionStart;
        ta.value = ta.value.substring(0, s) + '    ' + ta.value.substring(ta.selectionEnd);
        ta.selectionStart = ta.selectionEnd = s + 4;
        syncHighlight(ta.id.replace('edtxt-', ''));
      }
    });

    window.runCode = async (topicId) => {
      const ta  = document.getElementById(`edtxt-${topicId}`);
      const out = document.getElementById(`edout-${topicId}`);
      const btn = document.getElementById(`runbtn-${topicId}`);
      if (!ta || !out || !btn) return;
      btn.disabled = true;
      btn.innerHTML = '⏳ Running…';
      await runPython(ta.value, out);
      btn.disabled = false;
      btn.innerHTML = '<svg viewBox="0 0 12 12" fill="currentColor"><polygon points="2,1 11,6 2,11"/></svg> Run';
    };

    window.clearOutput = (topicId) => {
      const out = document.getElementById(`edout-${topicId}`);
      if (out) out.innerHTML = '<span class="out-line info">Click ▷ Run to execute Python</span>';
    };

    window.copyTopicCode = (topicId, btn) => {
      const ta = document.getElementById(`edtxt-${topicId}`);
      if (!ta) return;
      navigator.clipboard.writeText(ta.value).then(() => {
        btn.textContent = 'Copied!'; btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
      });
    };

    window.toggleEditor = async (topicId) => {
      const panel = document.getElementById(`editor-${topicId}`);
      if (!panel) return;
      const opening = !panel.classList.contains('open');
      panel.classList.toggle('open', opening);
      if (opening) {
        // Lazy-load code from file if textarea is empty/placeholder
        const ta = document.getElementById(`edtxt-${topicId}`);
        if (ta && ta.dataset.codeFile && ta.value.trim() === '') {
          ta.value = '# Loading…';
          const code = await loadCodeFile(ta.dataset.codeFile);
          if (code) {
            ta.value = code;
            syncHighlight(topicId);
          } else {
            ta.value = `# Could not load ${ta.dataset.codeFile}\n# Paste your code here`;
            syncHighlight(topicId);
          }
        }
        setTimeout(() => panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 100);
      }
    };

    // ════════════════════════════════════════════════════════════════════
    // TAB SWITCHER
    // ════════════════════════════════════════════════════════════════════
    window.switchTab = (tab) => {
      document.querySelectorAll('.rm-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.rm-tab-panel').forEach(p => p.classList.remove('active'));
      document.getElementById(`tab-${tab}`).classList.add('active');
      document.getElementById(`panel-${tab}`).classList.add('active');
      // Update sidebar
      renderSidebar(loadState(), tab);
    };

    // ════════════════════════════════════════════════════════════════════
    // STATE MANAGEMENT
    // ════════════════════════════════════════════════════════════════════
    function loadState() {
      try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
      catch { return {}; }
    }
    function saveState(state) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      const el = document.getElementById('lastUpdated');
      if (el) el.textContent = new Date().toLocaleDateString('en-US', {month:'short',day:'numeric',year:'numeric'});
    }
    function getChapterStatus(ch, state) {
      const done = ch.topics.filter(t => state[t.id]).length;
      if (done === ch.topics.length) return 'done';
      if (done > 0) return 'in-progress';
      return 'not-started';
    }
    function updateStats(state) {
      const allTopics = chapters.flatMap(c => c.topics);
      const csTopics  = caseStudyWeeks.map(w => ({id: `cs-${w.id}`}));
      const total     = allTopics.length + csTopics.length;
      const done      = Object.values(state).filter(Boolean).length;
      const doneCh    = chapters.filter(c => getChapterStatus(c,state)==='done').length;
      const pct       = Math.round(done/total*100);
      const pEl = document.getElementById('hero-pct');         if(pEl) pEl.textContent = pct+'%';
      const cEl = document.getElementById('hero-done-ch');     if(cEl) cEl.textContent = doneCh;
      const tEl = document.getElementById('hero-done-t');      if(tEl) tEl.textContent = done;
      const bEl = document.getElementById('heroPbar');         if(bEl) bEl.style.width = pct+'%';
      const lEl = document.getElementById('heroPbarLabel');    if(lEl) lEl.textContent = `${done} / ${total} topics completed`;
    }

    // ════════════════════════════════════════════════════════════════════
    // SIDEBAR
    // ════════════════════════════════════════════════════════════════════
    function renderSidebar(state, activeTab = 'fundamentals') {
      const nav = document.getElementById('rmSidebarNav');
      nav.innerHTML = '';
      if (activeTab === 'fundamentals') {
        chapters.forEach((ch, i) => {
          const status = getChapterStatus(ch, state);
          const li = document.createElement('li');
          li.innerHTML = `<button class="rm-nav-link status-${status}" onclick="scrollToChapter('${ch.id}')">
            <span class="rm-nav-num">${i+1}</span>${ch.title}</button>`;
          nav.appendChild(li);
        });
      } else {
        caseStudyWeeks.forEach((w, i) => {
          const done = !!state[`cs-${w.id}`];
          const li = document.createElement('li');
          li.innerHTML = `<button class="rm-nav-link ${done?'status-done':'status-not-started'}" onclick="scrollToCS('${w.id}')">
            <span class="rm-nav-num">W${i+1}</span>${w.topic}</button>`;
          nav.appendChild(li);
        });
      }
    }

    // ════════════════════════════════════════════════════════════════════
    // TAB 1: FUNDAMENTALS — RENDER
    // ════════════════════════════════════════════════════════════════════
    function renderTopicDetail(t) {
      const parts = [];
      if (t.formula) {
        parts.push(`<div class="td-formula">
          <div class="td-formula-title">${t.formula.title}</div>
          <div class="td-formula-lines">
            ${t.formula.lines.map(l => `<div class="td-formula-row">
              <span class="td-formula-label">${l.label}</span>
              <span class="td-formula-expr">${esc(l.expr)}</span>
            </div>`).join('')}
          </div>
          ${t.formula.note ? `<div class="td-formula-note">${t.formula.note}</div>` : ''}
        </div>`);
      }
      if (t.snippet) {
        const highlighted = highlightPython(t.snippet.raw);
        parts.push(`<div class="td-code">
          <div class="td-code-header">
            <span class="td-code-lang">${t.snippet.lang}</span>
            <div class="td-code-actions">
              <button class="copy-btn" onclick="copyTopicCode('${t.id}',this)">Copy</button>
              <button class="practice-btn" onclick="toggleEditor('${t.id}')">▷ Practice</button>
            </div>
          </div>
          <pre class="code-block" id="tcode-${t.id}" style="background:#0d1117;color:#e6edf3;padding:1rem 1.2rem;font-family:'SF Mono','Fira Code','Consolas',monospace;font-size:0.81rem;line-height:1.7;overflow-x:auto;margin:0;border-radius:0;">${highlighted}</pre>
          ${createEditorPanel(t.id, t.snippet.raw)}
        </div>`);
      }
      if (!parts.length) return '';
      return `<div class="topic-detail" id="td-${t.id}">${parts.join('')}</div>`;
    }

    function renderChapters(state) {
      const wrap = document.getElementById('rmChapters');
      wrap.innerHTML = '';
      const statusLabels = {done:'Completed','in-progress':'In progress','not-started':'Not started'};
      chapters.forEach((ch, ci) => {
        const status = getChapterStatus(ch, state);
        const doneCt = ch.topics.filter(t => state[t.id]).length;
        const pct    = Math.round(doneCt/ch.topics.length*100);
        const topicsHtml = ch.topics.map(t => {
          const hasDetail = !!(t.formula || t.snippet);
          return `<div class="topic-row ${state[t.id]?'done':''}" id="tr-${t.id}">
            <div class="topic-main ${hasDetail?'expandable':''}" ${hasDetail?`onclick="toggleTopicDetail('${t.id}')"`:''}">
              <button class="topic-check-btn ${state[t.id]?'checked':''}"
                onclick="event.stopPropagation();toggleTopic('${ch.id}','${t.id}')" aria-label="Mark complete">
                <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                  <polyline points="1.5,5 4,7.5 8.5,2.5" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <span class="topic-text ${state[t.id]?'done-text':''}">${t.text}</span>
              <span class="topic-tag-pill">${t.tag}</span>
              ${hasDetail?'<span class="topic-expand-icon">▼</span>':''}
            </div>
            ${hasDetail ? renderTopicDetail(t) : ''}
          </div>`;
        }).join('');
        const div = document.createElement('div');
        div.className = `rm-chapter status-${status}`;
        div.id = `chapter-${ch.id}`;
        div.innerHTML = `
          <div class="rm-chapter-header" onclick="toggleChapter('${ch.id}')">
            <div class="ch-num-badge">${ci+1}</div>
            <div class="ch-info">
              <div class="ch-title-row">
                <span class="ch-name">${ch.title}</span>
                <span class="ch-status-badge">${statusLabels[status]}</span>
              </div>
              <div class="ch-meta-row">${ch.meta}</div>
              <div class="ch-progress-mini">
                <div class="ch-prog-track"><div class="ch-prog-fill" style="width:${pct}%"></div></div>
                <span class="ch-prog-label">${doneCt}/${ch.topics.length}</span>
              </div>
            </div>
            <span class="ch-arrow">▼</span>
          </div>
          <div class="rm-chapter-body" id="chbody-${ch.id}">
            <div class="topics-list">${topicsHtml}</div>
            ${ch.resources?.length?`<div class="resources-section"><p class="resources-title">Resources</p><div class="resource-links">${ch.resources.map(r=>`<a class="resource-link" href="${r.url}" target="_blank">${r.label}</a>`).join('')}</div></div>`:''}
          </div>`;
        wrap.appendChild(div);
      });
    }

    // ════════════════════════════════════════════════════════════════════
    // TAB 2: CASE STUDY — RENDER
    // ════════════════════════════════════════════════════════════════════
    function renderCaseStudy(state) {
      const grid = document.getElementById('csGrid');
      grid.innerHTML = '';
      caseStudyWeeks.forEach((w, i) => {
        const isDone = !!state[`cs-${w.id}`];
        const card = document.createElement('div');
        card.className = 'cs-card';
        card.id = `cs-card-${w.id}`;

        const badgeClass = isDone ? 'done' : '';
        const statusLabel = isDone ? 'Done' : 'Pending';
        const statusBadgeClass = isDone ? 'cs-done-badge' : 'cs-pending-badge';

        // Build editor with code from file
        const editorHtml = createEditorPanel(`cs-${w.id}`, w.starterCode || `# ${w.topic}\n# Load the full example: code/casestudy/${w.codeFile}\n\nimport numpy as np\nprint("Week ${i+1}: ${w.topic}")`);

        card.innerHTML = `
          <div class="cs-header" onclick="toggleCS('${w.id}')">
            <div class="cs-week-badge ${badgeClass}">W${i+1}</div>
            <div class="cs-info">
              <div class="cs-title">${w.topic}</div>
              <div class="cs-goal">🎯 ${w.goal}</div>
            </div>
            <span class="cs-status-badge ${statusBadgeClass}">${statusLabel}</span>
            <button class="topic-check-btn ${isDone?'checked':''}" style="margin-left:4px"
              onclick="event.stopPropagation();toggleCSWeek('${w.id}')" aria-label="Mark done">
              <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                <polyline points="1.5,5 4,7.5 8.5,2.5" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <span class="cs-arrow">▼</span>
          </div>
          <div class="cs-body" id="csbody-${w.id}">
            <div class="cs-outcomes">
              <div class="cs-outcomes-label">Content</div>
              <div class="cs-outcomes-text">${w.content}</div>
              <div class="cs-outcomes-label" style="margin-top:0.75rem">Desired outcome</div>
              <div class="cs-outcomes-text">${w.desired}</div>
            </div>
            <div style="border-top:1px solid var(--border);padding:0.75rem 1.25rem 0;">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">
                <span style="font-size:0.75rem;font-weight:500;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.08em;">Code Example</span>
                <div style="display:flex;gap:6px;">
                  <a href="code/casestudy/${w.codeFile}" target="_blank" style="font-size:0.73rem;color:var(--gold);text-decoration:none;border:1px solid var(--gold);padding:2px 9px;border-radius:4px;">View .py ↗</a>
                  <button class="practice-btn" onclick="toggleEditor('cs-${w.id}')">▷ Practice</button>
                </div>
              </div>
              <pre class="code-block" id="tcode-cs-${w.id}" style="background:#0d1117;color:#e6edf3;padding:0.9rem 1.2rem;font-family:'SF Mono','Fira Code','Consolas',monospace;font-size:0.8rem;line-height:1.7;overflow-x:auto;margin:0;border-radius:var(--radius-sm);max-height:200px;">${highlightPython(w.starterCode || '# Full example in code/casestudy/' + w.codeFile)}</pre>
              ${editorHtml}
            </div>
            <div class="resources-section">
              <p class="resources-title">Resources</p>
              <div class="resource-links">${w.resources.map(r=>`<a class="resource-link" href="${r.url}" target="_blank">${r.label}</a>`).join('')}</div>
            </div>
          </div>`;
        grid.appendChild(card);
      });
    }

    // ════════════════════════════════════════════════════════════════════
    // DOM TOGGLE FUNCTIONS (no re-render)
    // ════════════════════════════════════════════════════════════════════
    window.toggleChapter = (id) => {
      const body = document.getElementById(`chbody-${id}`);
      const chEl = document.getElementById(`chapter-${id}`);
      if (!body) return;
      const opening = !body.classList.contains('open');
      document.querySelectorAll('.rm-chapter-body.open').forEach(b => {
        b.classList.remove('open'); b.closest('.rm-chapter')?.classList.remove('is-open');
      });
      if (opening) { body.classList.add('open'); chEl?.classList.add('is-open');
        setTimeout(() => chEl?.scrollIntoView({behavior:'smooth',block:'start'}), 50); }
    };

    window.scrollToChapter = (id) => {
      const body = document.getElementById(`chbody-${id}`);
      const chEl = document.getElementById(`chapter-${id}`);
      if (!body) return;
      document.querySelectorAll('.rm-chapter-body.open').forEach(b => {
        b.classList.remove('open'); b.closest('.rm-chapter')?.classList.remove('is-open');
      });
      body.classList.add('open'); chEl?.classList.add('is-open');
      setTimeout(() => chEl?.scrollIntoView({behavior:'smooth',block:'start'}), 50);
    };

    window.toggleTopicDetail = (topicId) => {
      const row = document.getElementById(`tr-${topicId}`);
      if (!row) return;
      const opening = !row.classList.contains('topic-open');
      row.classList.toggle('topic-open', opening);
      if (opening) setTimeout(() => row.scrollIntoView({behavior:'smooth',block:'nearest'}), 80);
    };

    window.toggleTopic = (chId, topicId) => {
      const state = loadState();
      state[topicId] = !state[topicId];
      saveState(state);
      const isDone = !!state[topicId];
      const row  = document.getElementById(`tr-${topicId}`);
      const btn  = row?.querySelector('.topic-check-btn');
      const text = row?.querySelector('.topic-text');
      if (row)  row.classList.toggle('done', isDone);
      if (btn)  btn.classList.toggle('checked', isDone);
      if (text) text.classList.toggle('done-text', isDone);
      const ch = chapters.find(c => c.id === chId);
      const chEl = document.getElementById(`chapter-${chId}`);
      if (ch && chEl) {
        const doneCt = ch.topics.filter(t => state[t.id]).length;
        const pct = Math.round(doneCt/ch.topics.length*100);
        const newSt = doneCt===ch.topics.length?'done':doneCt>0?'in-progress':'not-started';
        const lbs = {done:'Completed','in-progress':'In progress','not-started':'Not started'};
        const fill = chEl.querySelector('.ch-prog-fill'); if(fill) fill.style.width=pct+'%';
        const lb = chEl.querySelector('.ch-prog-label'); if(lb) lb.textContent=`${doneCt}/${ch.topics.length}`;
        const bd = chEl.querySelector('.ch-status-badge'); if(bd) bd.textContent=lbs[newSt];
        chEl.className = chEl.className.replace(/status-\S+/,'')+` status-${newSt}`;
        const sb = document.querySelector(`#rmSidebarNav button[onclick*="${chId}"]`);
        if(sb) sb.className = sb.className.replace(/status-\S+/,'')+` status-${newSt}`;
      }
      updateStats(state);
    };

    window.toggleCS = (id) => {
      const body = document.getElementById(`csbody-${id}`);
      const card = document.getElementById(`cs-card-${id}`);
      if (!body) return;
      const opening = !card.classList.contains('is-open');
      document.querySelectorAll('.cs-card.is-open').forEach(c => c.classList.remove('is-open'));
      document.querySelectorAll('.cs-body').forEach(b => b.style.display = 'none');
      if (opening) {
        card.classList.add('is-open'); body.style.display = 'block';
        setTimeout(() => card.scrollIntoView({behavior:'smooth',block:'start'}), 50);
      }
    };

    window.scrollToCS = (id) => {
      toggleCS(id);
    };

    window.toggleCSWeek = (weekId) => {
      const state = loadState();
      const key = `cs-${weekId}`;
      state[key] = !state[key];
      saveState(state);
      const card = document.getElementById(`cs-card-${weekId}`);
      const btn  = card?.querySelector('.topic-check-btn');
      const badge = card?.querySelector('.cs-week-badge');
      const statusBadge = card?.querySelector('.cs-status-badge');
      if (btn) btn.classList.toggle('checked', !!state[key]);
      if (badge) { badge.classList.toggle('done', !!state[key]); }
      if (statusBadge) {
        statusBadge.textContent = state[key] ? 'Done' : 'Pending';
        statusBadge.className = `cs-status-badge ${state[key] ? 'cs-done-badge' : 'cs-pending-badge'}`;
      }
      const sideBtn = document.querySelector(`#rmSidebarNav button[onclick*="${weekId}"]`);
      if (sideBtn) sideBtn.className = sideBtn.className.replace(/status-\S+/, '') + ` status-${state[key]?'done':'not-started'}`;
      updateStats(state);
    };

    // ════════════════════════════════════════════════════════════════════
    // DATA: FUNDAMENTALS CHAPTERS
    // ════════════════════════════════════════════════════════════════════
    const chapters = [
      { id:'python-math', title:'Python & Math 基礎', meta:'NumPy · Linear Algebra · Calculus · Probability',
        topics:[
          { id:'numpy-broadcast', text:'NumPy arrays & broadcasting', tag:'NumPy',
            snippet:{ lang:'Python', raw:`import numpy as np\nA = np.array([[1,2,3],[4,5,6],[7,8,9]])\nb = np.array([10,20,30])\nresult = A + b   # broadcasting: shape (3,3)\nprint("result:\\n", result)\nW = np.random.randn(3,2)\nout = A @ W\nprint("out shape:", out.shape)` }},
          { id:'matrix-mult', text:'Matrix multiplication', tag:'Math',
            formula:{ title:'Matrix Multiplication',
              lines:[{label:'Definition',expr:'C = A × B,  C[i,j] = Σₖ A[i,k] · B[k,j]'},{label:'Shapes',expr:'A:(m×k), B:(k×n) → C:(m×n)'},{label:'Dot product',expr:'a·b = Σᵢ aᵢbᵢ = |a||b|cosθ'},{label:'Note',expr:'AB ≠ BA  (not commutative)'}],
              note:'Inner dimensions must match.' },
            snippet:{ lang:'Python', raw:`import numpy as np\nA = np.random.randn(3,4)\nB = np.random.randn(4,2)\nC = A @ B\nprint("A:", A.shape, "B:", B.shape, "→ C:", C.shape)\nd = A[0] @ B[:,0]\nprint("dot product:", round(d, 4))` }},
          { id:'gradient-deriv', text:'Gradient & partial derivatives', tag:'Calculus',
            formula:{ title:'Gradient & Chain Rule',
              lines:[{label:'Partial deriv.',expr:'∂f/∂xᵢ = lim [f(x+εeᵢ) − f(x)] / ε  as ε→0'},{label:'Gradient',expr:'∇f(x) = [∂f/∂x₁, ..., ∂f/∂xₙ]ᵀ'},{label:'Chain rule',expr:"d/dx f(g(x)) = f'(g(x)) · g'(x)"},{label:'MSE gradient',expr:'∂L/∂w = −2(y − ŷ) · ∂ŷ/∂w'}],
              note:'∇f points in steepest ascent direction. GD moves in −∇f direction.' },
            snippet:{ lang:'Python', raw:`import numpy as np\n\n# Numerical gradient check\ndef f(x): return x[0]**2 + 2*x[1]**2\n\nx = np.array([2.0, 3.0])\neps = 1e-5\nanalytic_grad = np.array([2*x[0], 4*x[1]])\nnumeric_grad = np.array([\n    (f(x + eps*np.eye(2)[i]) - f(x)) / eps\n    for i in range(2)\n])\nprint("Analytic:", analytic_grad)\nprint("Numeric: ", numeric_grad.round(4))` }},
          { id:'prob-stats', text:'Probability & statistics review', tag:'Math',
            formula:{ title:'Key Probability Formulas',
              lines:[{label:"Bayes' theorem",expr:'P(A|B) = P(B|A) · P(A) / P(B)'},{label:'Gaussian PDF',expr:'p(x) = (1/√2πσ²) · exp(−(x−μ)²/2σ²)'},{label:'Expectation',expr:'E[X] = Σ x·P(X=x)'},{label:'Variance',expr:'Var(X) = E[X²] − (E[X])²'}],
              note:'In ML: P(class|data) ∝ P(data|class)·P(class)  →  posterior ∝ likelihood × prior.' }},
        ],
        resources:[{label:'NumPy docs',url:'https://numpy.org/doc/stable/'},{label:'3Blue1Brown — Linear Algebra',url:'https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2ZAgoEGczxSlvb'}]},
      { id:'classical-ml', title:'Classical ML — Sklearn', meta:'Regression · Classification · Evaluation · Pipelines',
        topics:[
          { id:'lin-log-reg', text:'Linear & logistic regression', tag:'Sklearn',
            formula:{ title:'Linear vs Logistic Regression',
              lines:[{label:'Linear',expr:'ŷ = wᵀx + b,   Loss = (1/n)Σ(y−ŷ)²'},{label:'Gradient',expr:'w ← w − α·(1/n)Xᵀ(Xw−y)'},{label:'Sigmoid',expr:'σ(z) = 1/(1+e⁻ᶻ)'},{label:'Cross-entropy',expr:'L = −Σ[y log(ŷ) + (1−y) log(1−ŷ)]'}],
              note:'Logistic outputs probability via sigmoid, threshold at 0.5 for binary classification.' },
            snippet:{ lang:'Python', raw:`from sklearn.linear_model import LogisticRegression\nfrom sklearn.datasets import make_classification\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.metrics import accuracy_score, classification_report\n\nX, y = make_classification(n_samples=200, n_features=4, random_state=42)\nX_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2)\n\nclf = LogisticRegression(max_iter=200)\nclf.fit(X_tr, y_tr)\nprint("Accuracy:", accuracy_score(y_te, clf.predict(X_te)))\nprint(classification_report(y_te, clf.predict(X_te)))` }},
          { id:'cross-val', text:'Cross-validation & metrics', tag:'Eval',
            formula:{ title:'Evaluation Metrics',
              lines:[{label:'Precision',expr:'P = TP / (TP + FP)'},{label:'Recall',expr:'R = TP / (TP + FN)'},{label:'F1 score',expr:'F1 = 2·P·R / (P+R)'},{label:'k-fold CV',expr:'score = (1/k) Σᵢ score(fold_i)'}],
              note:'Use F1 when classes are imbalanced. Precision: FP costly. Recall: FN costly.' },
            snippet:{ lang:'Python', raw:`from sklearn.model_selection import cross_val_score\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.datasets import make_classification\n\nX, y = make_classification(n_samples=400, random_state=0)\nrf = RandomForestClassifier(n_estimators=50, random_state=42)\nscores = cross_val_score(rf, X, y, cv=5, scoring='f1')\nprint(f"F1 scores: {scores.round(3)}")\nprint(f"Mean F1:   {scores.mean():.3f} +/- {scores.std():.3f}")` }},
          { id:'feat-eng', text:'Feature engineering & pipelines', tag:'Sklearn',
            snippet:{ lang:'Python', raw:`from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.decomposition import PCA\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.datasets import load_breast_cancer\nfrom sklearn.model_selection import train_test_split\n\nX, y = load_breast_cancer(return_X_y=True)\nX_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=0)\n\npipe = Pipeline([\n    ('scaler', StandardScaler()),\n    ('pca', PCA(n_components=10)),\n    ('clf', RandomForestClassifier(n_estimators=50))\n])\npipe.fit(X_tr, y_tr)\nprint("Pipeline accuracy:", round(pipe.score(X_te, y_te), 4))` }},
        ],
        resources:[{label:'Sklearn user guide',url:'https://scikit-learn.org/stable/user_guide.html'}]},
      { id:'deep-learning', title:'Deep Learning — PyTorch', meta:'Autograd · MLP · Training loop · Optimizers',
        topics:[
          { id:'mlp-scratch', text:'Build MLP from scratch', tag:'PyTorch',
            snippet:{ lang:'Python', raw:`import numpy as np\n\ndef relu(x): return np.maximum(0, x)\ndef sigmoid(x): return 1 / (1 + np.exp(-x))\n\n# 2-layer MLP forward pass\nnp.random.seed(42)\nW1 = np.random.randn(4, 8) * 0.1\nb1 = np.zeros(8)\nW2 = np.random.randn(8, 1) * 0.1\nb2 = np.zeros(1)\n\nX = np.random.randn(5, 4)  # 5 samples\nh = relu(X @ W1 + b1)\ny = sigmoid(h @ W2 + b2)\nprint("Input shape:", X.shape)\nprint("Output shape:", y.shape)\nprint("Predictions:", y.flatten().round(3))` }},
          { id:'train-loop', text:'Custom training loop', tag:'PyTorch',
            formula:{ title:'Gradient Descent Update Rule',
              lines:[{label:'Forward',expr:'ŷ = f(x; θ)'},{label:'Loss',expr:'L = loss(ŷ, y)'},{label:'Backward',expr:'g = ∇θ L  (backprop)'},{label:'Update',expr:'θ ← θ − α · g'}],
              note:'Adam adapts α per parameter using first (m) and second (v) moment estimates.' },
            snippet:{ lang:'Python', raw:`import numpy as np\n\n# Mini gradient descent: fit y = 3x + 2\nnp.random.seed(0)\nX = np.random.randn(100)\ny = 3*X + 2 + 0.1*np.random.randn(100)\n\nw, b, lr = 0.0, 0.0, 0.1\nfor epoch in range(25):\n    pred = w*X + b\n    loss = ((pred - y)**2).mean()\n    dw = (2*(pred-y)*X).mean()\n    db = (2*(pred-y)).mean()\n    w -= lr*dw; b -= lr*db\n    if epoch % 5 == 0:\n        print(f"Epoch {epoch:2d}: loss={loss:.4f}, w={w:.3f}, b={b:.3f}")\nprint(f"\\nTrue: w=3, b=2 | Learned: w={w:.3f}, b={b:.3f}")` }},
        ],
        resources:[{label:'PyTorch tutorials',url:'https://pytorch.org/tutorials/'},{label:'Karpathy — Zero to Hero',url:'https://karpathy.ai/zero-to-hero.html'}]},
      { id:'computer-vision', title:'Computer Vision — CNNs', meta:'Conv layers · ResNet · Transfer learning',
        topics:[
          { id:'conv-pooling', text:'Conv2D & pooling intuition', tag:'CNN',
            formula:{ title:'Convolution Operation',
              lines:[{label:'Output size',expr:'H_out = (H_in + 2P − K) / S + 1'},{label:'Conv2D',expr:'y[i,j] = Σₘ Σₙ x[i·S+m, j·S+n] · w[m,n]'},{label:'Params',expr:'# params = K×K×C_in×C_out + C_out'},{label:'MaxPool',expr:'y[i,j] = max over K×K window at (i·S, j·S)'}],
              note:'padding=1 with K=3 keeps H,W unchanged (same padding).' },
            snippet:{ lang:'Python', raw:`import numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nfrom scipy.signal import convolve2d\n\n# Edge detection via convolution\nimg = np.zeros((32,32))\nimg[8:24, 8:24] = 1.0  # white square\n\nsobel_x = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])\nsobel_y = sobel_x.T\nedges_x = convolve2d(img, sobel_x, mode='same')\nedges_y = convolve2d(img, sobel_y, mode='same')\nedges   = np.sqrt(edges_x**2 + edges_y**2)\n\nfig, axes = plt.subplots(1,3,figsize=(9,3))\nfor ax,im,t in zip(axes,[img,edges_x,edges],['Input','Sobel X','Magnitude']):\n    ax.imshow(im, cmap='gray'); ax.set_title(t); ax.axis('off')\nplt.tight_layout()\nplt.savefig('/tmp/conv.png', dpi=80, bbox_inches='tight')\nprint("Convolution demo done!")` }},
          { id:'resnet-skip', text:'ResNet & skip connections', tag:'CNN',
            formula:{ title:'Residual Block',
              lines:[{label:'Residual',expr:'H(x) = F(x) + x'},{label:'F(x)',expr:'F(x) = W₂·ReLU(W₁x+b₁)+b₂'},{label:'Gradient flow',expr:'∂L/∂x = ∂L/∂H·(∂F/∂x + I)'},{label:'Key insight',expr:'Identity shortcut → gradient ≥ 1 → no vanishing'}],
              note:'Skip connections solve vanishing gradient in deep networks (100+ layers).' }},
        ],
        resources:[{label:'CS231n Stanford',url:'http://cs231n.stanford.edu/'}]},
      { id:'transformers', title:'Transformers & Attention', meta:'Self-attention · ViT · DETR',
        topics:[
          { id:'self-attn', text:'Self-attention mechanism', tag:'Attention',
            formula:{ title:'Scaled Dot-Product Attention',
              lines:[{label:'Projections',expr:'Q = XWQ,  K = XWK,  V = XWV'},{label:'Scores',expr:'scores = QKᵀ / √dₖ'},{label:'Weights',expr:'α = softmax(scores)'},{label:'Output',expr:'Attention(Q,K,V) = α · V'}],
              note:'Dividing by √dₖ stabilises softmax gradients in high-dimensional spaces.' },
            snippet:{ lang:'Python', raw:`import numpy as np\n\ndef softmax(x):\n    e = np.exp(x - x.max(axis=-1, keepdims=True))\n    return e / e.sum(axis=-1, keepdims=True)\n\ndef attention(Q, K, V):\n    d_k = Q.shape[-1]\n    scores = Q @ K.T / np.sqrt(d_k)\n    weights = softmax(scores)\n    return weights @ V, weights\n\nnp.random.seed(0)\nseq, d_k = 4, 8\nQ = np.random.randn(seq, d_k)\nK = np.random.randn(seq, d_k)\nV = np.random.randn(seq, d_k)\n\nout, w = attention(Q, K, V)\nprint("Attention weights (4x4):\\n", w.round(3))\nprint("Output shape:", out.shape)` }},
        ],
        resources:[{label:'Attention Is All You Need',url:'https://arxiv.org/abs/1706.03762'},{label:'Illustrated Transformer',url:'https://jalammar.github.io/illustrated-transformer/'}]},
      { id:'lidar-3d', title:'3D Perception — LiDAR', meta:'Point clouds · PointNet · BEV',
        topics:[
          { id:'bev', text:"Bird's Eye View (BEV) projection", tag:'AV',
            snippet:{ lang:'Python', raw:`import numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\ndef lidar_to_bev(pts, x_range=(-20,20), y_range=(-20,20), res=0.2):\n    W = int((x_range[1]-x_range[0])/res)\n    H = int((y_range[1]-y_range[0])/res)\n    bev = np.zeros((H, W))\n    xi = ((pts[:,0]-x_range[0])/res).astype(int)\n    yi = ((pts[:,1]-y_range[0])/res).astype(int)\n    m  = (xi>=0)&(xi<W)&(yi>=0)&(yi<H)\n    np.maximum.at(bev, (yi[m], xi[m]), pts[m,2])\n    return bev\n\nnp.random.seed(1)\npts = np.random.randn(2000, 3) * [5, 5, 0.5]\nbev = lidar_to_bev(pts)\n\nplt.figure(figsize=(5,5))\nplt.imshow(bev, cmap='plasma', origin='lower')\nplt.title('BEV Height Map')\nplt.colorbar(label='Height (m)')\nplt.tight_layout()\nplt.savefig('/tmp/bev.png', dpi=80, bbox_inches='tight')\nprint("BEV shape:", bev.shape)` }},
          { id:'kalman', text:'Kalman filter for tracking', tag:'Tracking',
            formula:{ title:'Kalman Filter Equations',
              lines:[{label:'Predict',expr:'x̂⁻ = F·x,   P⁻ = F·P·Fᵀ+Q'},{label:'Innovation',expr:'y = z − H·x̂⁻'},{label:'Kalman gain',expr:'K = P⁻·Hᵀ·(H·P⁻·Hᵀ+R)⁻¹'},{label:'Update',expr:'x̂ = x̂⁻+K·y,   P = (I−K·H)·P⁻'}],
              note:'F=motion model, H=observation model, Q=process noise, R=measurement noise.' },
            snippet:{ lang:'Python', raw:`import numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\nnp.random.seed(42)\nT = 40\ntrue_pos = np.linspace(0,10,T) + np.sin(np.linspace(0,6,T))\nmeasured = true_pos + np.random.randn(T)*0.8\n\nx, P = 0.0, 1.0\nF, H, Q, R = 1.0, 1.0, 0.01, 0.64\nestimates = []\nfor z in measured:\n    x=F*x; P=F*P*F+Q\n    K=P*H/(H*P*H+R); x=x+K*(z-H*x); P=(1-K*H)*P\n    estimates.append(x)\n\nplt.figure(figsize=(8,3))\nplt.plot(true_pos,'g-',lw=2,label='True')\nplt.plot(measured,'r.',ms=4,alpha=0.5,label='Noisy')\nplt.plot(estimates,'b-',lw=2,label='Kalman')\nplt.legend(); plt.title('1D Kalman Filter')\nplt.tight_layout()\nplt.savefig('/tmp/kalman.png',dpi=80,bbox_inches='tight')\nprint("Done!")` }},
        ],
        resources:[{label:'Kalman Filter tutorial',url:'https://www.kalmanfilter.net/'},{label:'nuScenes dataset',url:'https://www.nuscenes.org/'}]},
    ];

    // ════════════════════════════════════════════════════════════════════
    // DATA: CASE STUDY WEEKS (from spreadsheet)
    // ════════════════════════════════════════════════════════════════════
    const caseStudyWeeks = [
      { id:'week01', topic:'Linear Algebra & Calculus', codeFile:'week01_linear_algebra.py',
        content:'矩陣運算 (@)、座標變換、微分與梯度下降。',
        desired:'手寫 3D 旋轉矩陣並視覺化點雲位移。',
        goal:'手寫 3D 旋轉矩陣並視覺化點雲位移',
        starterCode:`import numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\n# 3D Rotation Matrix (Rz)\ndef Rz(theta):\n    c, s = np.cos(theta), np.sin(theta)\n    return np.array([[c,-s,0],[s,c,0],[0,0,1]])\n\n# Apply 45° rotation to a point cloud\nnp.random.seed(0)\npts = np.random.randn(30, 3)\nR = Rz(np.radians(45))\npts_rot = (R @ pts.T).T\n\nprint("Rotation matrix (45°):\\n", R.round(3))\nprint("Original pt[0]:", pts[0].round(3))\nprint("Rotated  pt[0]:", pts_rot[0].round(3))`,
        resources:[{label:'3B1B Essence of Linear Algebra',url:'https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2ZAgoEGczxSlvb'},{label:'Khan Academy: Matrices',url:'https://www.khanacademy.org/math/linear-algebra'}]},
      { id:'week02', topic:'Python for ML (Vectorization)', codeFile:'week02_vectorization.py',
        content:'NumPy Boolean Masking, Broadcasting, Pythonic data filtering.',
        desired:'實作高效點雲過濾 (ROI)，無 for 迴圈處理 10w+ 數據。',
        goal:'無 for 迴圈高效過濾 10w+ 點雲 ROI',
        starterCode:`import numpy as np\nimport time\n\nnp.random.seed(0)\nN = 100_000\npts = np.column_stack([\n    np.random.uniform(-40, 70, N),  # x\n    np.random.uniform(-40, 40, N),  # y\n    np.random.uniform(-3,   5, N),  # z\n])\n\n# Vectorized ROI filter (no for loop!)\nt0 = time.perf_counter()\nmask = (\n    (pts[:,0] >= 0) & (pts[:,0] <= 50) &\n    (pts[:,1] >= -20) & (pts[:,1] <= 20) &\n    (pts[:,2] >= -2) & (pts[:,2] <= 3)\n)\nroi = pts[mask]\nt1 = time.perf_counter()\n\nprint(f"Total: {N:,} pts")\nprint(f"ROI:   {len(roi):,} pts ({len(roi)/N*100:.1f}%)")\nprint(f"Time:  {(t1-t0)*1000:.2f} ms")`,
        resources:[{label:'NumPy Broadcasting',url:'https://numpy.org/doc/stable/user/basics.broadcasting.html'},{label:'NumPy Indexing',url:'https://numpy.org/doc/stable/user/basics.indexing.html'}]},
      { id:'week03', topic:'Waymo Dataset Parsing', codeFile:'week03_waymo_parsing.py',
        content:'Protobuf 格式解析、TFRecord 讀取、感測器內外參。',
        desired:'成功提取 Waymo 第一幀影像與點雲數據。',
        goal:'提取 Waymo 第一幀影像與點雲，理解資料結構',
        starterCode:`import numpy as np\n\n# Waymo camera intrinsic matrix (FRONT camera approximate)\nfx, fy = 1900, 1900  # focal length\ncx, cy = 960, 640    # principal point\nK = np.array([[fx, 0, cx],\n              [0, fy, cy],\n              [0,  0,  1]], dtype=float)\n\n# LiDAR → Camera extrinsic\nR_ext = np.array([[0,-1,0],[0,0,-1],[1,0,0]], dtype=float)\nt_ext = np.array([0.1, 0.8, 1.5])\n\n# Project a 3D point to image\ndef project(pt_lidar, K, R, t):\n    pt_cam = R @ pt_lidar + t\n    if pt_cam[2] <= 0: return None, None\n    u = K[0,0]*pt_cam[0]/pt_cam[2] + K[0,2]\n    v = K[1,1]*pt_cam[1]/pt_cam[2] + K[1,2]\n    return u, v\n\n# Test with a car at (20, 3, 1) in LiDAR frame\nu, v = project(np.array([20., 3., 1.]), K, R_ext, t_ext)\nprint(f"Car at (20,3,1)m → pixel ({u:.0f}, {v:.0f})")`,
        resources:[{label:'Waymo Open Dataset',url:'https://waymo.com/open/'},{label:'Waymo GitHub',url:'https://github.com/waymo-research/waymo-open-dataset'}]},
      { id:'week04', topic:'Geometric 3D Projection', codeFile:'week04_3d_projection.py',
        content:'3D Bounding Box 頂點計算、3D 到 2D 投影公式。',
        desired:'產出第一張 3D Box 投影在相機影像上的 Demo。',
        goal:'產出 3D Box 投影在相機影像上的 Demo',
        starterCode:`import numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\ndef box3d_corners(cx,cy,cz,l,w,h,heading):\n    """8 corners of 3D bounding box."""\n    x = np.array([ l/2, l/2,-l/2,-l/2, l/2, l/2,-l/2,-l/2])\n    y = np.array([ w/2,-w/2,-w/2, w/2, w/2,-w/2,-w/2, w/2])\n    z = np.array([-h/2,-h/2,-h/2,-h/2, h/2, h/2, h/2, h/2])\n    c,s = np.cos(heading), np.sin(heading)\n    xr = c*x - s*y; yr = s*x + c*y\n    return np.column_stack([xr+cx, yr+cy, z+cz])\n\n# Car at (20, 3, 1), 4.5×2×1.6m, 5° heading\ncorners = box3d_corners(20, 3, 1, 4.5, 2.0, 1.6, np.radians(5))\nprint("8 corners (x,y,z):")\nprint(corners.round(2))\n\n# BEV footprint (bottom 4 corners)\nfig, ax = plt.subplots(figsize=(5,5))\nfoot = corners[:4,:2]\nfout = np.vstack([foot,foot[0]])\nax.plot(fout[:,0],fout[:,1],'r-',lw=2,label='Box')\nax.scatter([20],[3],c='g',s=100,label='Center')\nax.legend(); ax.set_title('3D Box BEV Footprint')\nplt.savefig('/tmp/box.png',dpi=80,bbox_inches='tight')\nprint("Plot saved!")`,
        resources:[{label:'KITTI 3D Object Detection',url:'https://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d'},{label:'Camera Calibration OpenCV',url:'https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html'}]},
      { id:'week05', topic:'Deep Learning Fundamental', codeFile:'week05_deep_learning.py',
        content:'手寫 Linear Layer, Activation Functions (ReLU, Sigmoid)。',
        desired:'僅使用 NumPy 實作前向傳播 (Forward Pass)。',
        goal:'NumPy-only MLP forward pass on Iris dataset',
        starterCode:`import numpy as np\nfrom sklearn.datasets import load_iris\nfrom sklearn.preprocessing import StandardScaler\n\ndef relu(x): return np.maximum(0, x)\ndef softmax(x):\n    e = np.exp(x - x.max(axis=-1, keepdims=True))\n    return e / e.sum(axis=-1, keepdims=True)\n\n# Load Iris (150 samples, 4 features, 3 classes)\niris = load_iris()\nX = StandardScaler().fit_transform(iris.data)\ny = iris.target\n\n# Random MLP: 4 → 16 → 8 → 3\nnp.random.seed(42)\nW1 = np.random.randn(4,16)*0.1; b1 = np.zeros(16)\nW2 = np.random.randn(16,8)*0.1; b2 = np.zeros(8)\nW3 = np.random.randn(8,3)*0.1; b3 = np.zeros(3)\n\nh1 = relu(X @ W1 + b1)\nh2 = relu(h1 @ W2 + b2)\nout = softmax(h2 @ W3 + b3)\n\npreds = out.argmax(axis=1)\nprint(f"Random init accuracy: {(preds==y).mean():.2%}")\nprint(f"Output shape: {out.shape}")`,
        resources:[{label:'Karpathy micrograd',url:'https://github.com/karpathy/micrograd'},{label:'fast.ai',url:'https://www.fast.ai/'}]},
      { id:'week06', topic:'CV Foundations (CNN & ViT)', codeFile:'week06_cnn_vit.py',
        content:'卷積運算原理、Transformer Self-Attention 機制。',
        desired:'實作簡單的 Image Backbone 提取影像特徵。',
        goal:'從 scratch 實作 CNN 特徵提取 + ViT patch attention',
        starterCode:`import numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nfrom scipy.signal import convolve2d\n\n# Simulate a 32x32 scene\nnp.random.seed(6)\nimg = np.zeros((32,32))\nimg[8:24,8:24] = 0.9   # vehicle\nimg[4:6,:] = 0.5       # horizon\nimg += np.random.randn(32,32)*0.05\nimg = np.clip(img, 0, 1)\n\n# Apply 4 learned kernels\nkernels = [\n    np.array([[-1,0,1],[-2,0,2],[-1,0,1]]),  # Sobel X\n    np.array([[-1,-2,-1],[0,0,0],[1,2,1]]),  # Sobel Y\n    np.array([[0,-1,0],[-1,4,-1],[0,-1,0]]), # Laplacian\n    np.array([[1,1,1],[1,-8,1],[1,1,1]]),    # Edges\n]\nfeatures = [np.maximum(0, convolve2d(img,k,mode='same')/4) for k in kernels]\n\nfig,axes = plt.subplots(1,5,figsize=(12,2.5))\naxes[0].imshow(img,cmap='gray'); axes[0].set_title('Input')\nfor i,(f,t) in enumerate(zip(features,['Sobel X','Sobel Y','Laplacian','Edges'])):\n    axes[i+1].imshow(f,cmap='hot'); axes[i+1].set_title(t)\nfor ax in axes: ax.axis('off')\nplt.tight_layout()\nplt.savefig('/tmp/cnn.png',dpi=80,bbox_inches='tight')\nprint("Feature maps saved!")`,
        resources:[{label:'CS231n: Conv Nets',url:'http://cs231n.stanford.edu/slides/2023/lecture_5.pdf'},{label:'ViT paper',url:'https://arxiv.org/abs/2010.11929'}]},
      { id:'week07', topic:'3D Perception Models', codeFile:'week07_3d_perception.py',
        content:'PointNet, Voxelization (體素化), BEV (Bird\'s Eye View)。',
        desired:'將點雲轉換為 BEV 表徵，準備輸入模型。',
        goal:'點雲轉 BEV tensor，理解 PointNet 架構',
        starterCode:`import numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\n# PointNet: shared MLP + global max pooling\nnp.random.seed(7)\n\ndef shared_mlp(pts, sizes=[3,64,128]):\n    x = pts  # (N, 3)\n    for i in range(len(sizes)-1):\n        W = np.random.randn(sizes[i+1], sizes[i]) * np.sqrt(2/sizes[i])\n        b = np.zeros(sizes[i+1])\n        x = np.maximum(0, x @ W.T + b)\n    return x  # (N, 128)\n\ndef pointnet(pts):\n    feats = shared_mlp(pts, [3,64,128])\n    return feats.max(axis=0)  # global max pool → (128,)\n\npts = np.random.randn(200, 3)\ng = pointnet(pts)\nprint("Input:", pts.shape, "→ Global feature:", g.shape)\nprint("PointNet is permutation-invariant! ✓")`,
        resources:[{label:'PointNet paper',url:'https://arxiv.org/abs/1612.00593'},{label:'Open3D docs',url:'http://www.open3d.org/docs/release/'}]},
      { id:'week08', topic:'Model Training Pipeline', codeFile:'week08_training_pipeline.py',
        content:'PyTorch DataLoader, Loss Functions (IoU Loss), Optimizer。',
        desired:'搭建完整的訓練流程，並在小型數據集上過濾過擬合。',
        goal:'搭建帶有 IoU Loss 的完整訓練流程',
        starterCode:`import numpy as np\n\ndef iou(pred, gt):\n    """pred, gt: [cx, cy, w, h]"""\n    x1p,y1p = pred[0]-pred[2]/2, pred[1]-pred[3]/2\n    x2p,y2p = pred[0]+pred[2]/2, pred[1]+pred[3]/2\n    x1g,y1g = gt[0]-gt[2]/2, gt[1]-gt[3]/2\n    x2g,y2g = gt[0]+gt[2]/2, gt[1]+gt[3]/2\n    xi1,yi1 = max(x1p,x1g), max(y1p,y1g)\n    xi2,yi2 = min(x2p,x2g), min(y2p,y2g)\n    inter = max(0,xi2-xi1)*max(0,yi2-yi1)\n    union = pred[2]*pred[3] + gt[2]*gt[3] - inter\n    return inter/(union+1e-6)\n\n# Test IoU\npred = [10, 5, 4, 2]  # cx,cy,w,h\ngt   = [11, 5, 4, 2]\nprint(f"IoU: {iou(pred, gt):.3f}  (should be ~0.6)")\nprint(f"IoU loss: {1-iou(pred,gt):.3f}")`,
        resources:[{label:'IoU Loss paper',url:'https://arxiv.org/abs/1902.09630'},{label:'PyTorch DataLoader',url:'https://pytorch.org/docs/stable/data.html'}]},
      { id:'week09', topic:'Sensor Fusion Strategy', codeFile:'week09_sensor_fusion.py',
        content:'Camera-LiDAR Fusion, Early vs Late Fusion 理論。',
        desired:'實作簡易的幾何對齊融合 (Geometric Alignment)。',
        goal:'實作 Camera-LiDAR 幾何對齊融合',
        starterCode:`import numpy as np\n\n# Camera-LiDAR Geometric Alignment\nK = np.array([[1900,0,960],[0,1900,640],[0,0,1]],dtype=float)\nR = np.array([[0,-1,0],[0,0,-1],[1,0,0]],dtype=float)  # LiDAR→Camera\nt = np.array([0.1, 0.8, 1.5])\n\ndef lidar_to_pixel(p3d, K, R, t):\n    pc = R @ p3d + t  # camera frame\n    if pc[2] <= 0: return None\n    u = K[0,0]*pc[0]/pc[2]+K[0,2]\n    v = K[1,1]*pc[1]/pc[2]+K[1,2]\n    return np.array([u, v, pc[2]])  # u, v, depth\n\n# Project a cluster of LiDAR points (a vehicle)\nvehicle_pts = np.random.randn(20,3)*[0.8,0.5,0.3]+[25,3,1]\n\nprojected = [lidar_to_pixel(p, K, R, t) for p in vehicle_pts]\nprojected = [p for p in projected if p is not None]\nif projected:\n    uv = np.array(projected)\n    print(f"Projected {len(uv)} of {len(vehicle_pts)} points")\n    print(f"  Pixel range: u=[{uv[:,0].min():.0f},{uv[:,0].max():.0f}]  v=[{uv[:,1].min():.0f},{uv[:,1].max():.0f}]")\n    print(f"  Mean depth: {uv[:,2].mean():.1f} m")`,
        resources:[{label:'BEVFusion paper',url:'https://arxiv.org/abs/2205.13542'},{label:'Waymo Fusion',url:'https://waymo.com/research/'}]},
      { id:'week10', topic:'Temporal Modeling', codeFile:'week10_temporal.py',
        content:'時序特徵融合、RNN/Transformer 處理序列數據。',
        desired:'利用前一幀資訊處理物體遮擋 (Occlusion) 問題。',
        goal:'用 Kalman Filter 處理遮擋，追蹤物體跨幀位置',
        starterCode:`import numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\n# 1D Kalman Filter: track object through occlusion\nnp.random.seed(10)\nT = 30\ntrue_x = np.linspace(0, 15, T)\nnoisy  = true_x + np.random.randn(T)*0.8\nOCCLUDED = set(range(10, 18))  # frames 10-17 occluded\n\nx, P = 0.0, 2.0\nF, H, Q, R = 1.0, 1.0, 0.05, 0.64\nestimates = []\n\nfor f in range(T):\n    x = F*x; P = F*P*F+Q  # predict\n    if f not in OCCLUDED:  # update only if visible\n        K = P*H/(H*P*H+R); x = x+K*(noisy[f]-H*x); P = (1-K*H)*P\n    estimates.append(x)\n\nplt.figure(figsize=(8,3))\nplt.plot(true_x,'g-',lw=2,label='True position')\nplt.plot(noisy,'r.',ms=5,alpha=0.5,label='Measurement')\nplt.plot(estimates,'b-',lw=2,label='Kalman estimate')\nplt.axvspan(10,17,alpha=0.15,color='orange',label='Occlusion')\nplt.legend(fontsize=8); plt.title('Tracking Through Occlusion')\nplt.tight_layout()\nplt.savefig('/tmp/track.png',dpi=80,bbox_inches='tight')\nprint("Tracking done! KF uses velocity to predict during occlusion.")`,
        resources:[{label:'Kalman Filter explained',url:'https://www.kalmanfilter.net/'},{label:'SORT tracker paper',url:'https://arxiv.org/abs/1602.00763'}]},
      { id:'week11', topic:'Capstone: End-to-End Perception', codeFile:'week11_capstone.py',
        content:'整合上述模組，訓練一個完整的 3D 偵測器。',
        desired:'在 Waymo 驗證集上達到初步可接受的 mAP 表現。',
        goal:'整合所有模組，端到端 3D 偵測器 with mAP evaluation',
        starterCode:`import numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\ndef iou_approx(pred_cx, pred_cy, gt_cx, gt_cy, thresh_m=3.0):\n    dist = np.sqrt((pred_cx-gt_cx)**2 + (pred_cy-gt_cy)**2)\n    return max(0, 1.0 - dist/thresh_m)\n\nnp.random.seed(11)\nall_ious = []\nfor _ in range(100):  # 100 detections\n    gt_cx, gt_cy = np.random.uniform(5,45), np.random.uniform(-15,15)\n    pred_cx = gt_cx + np.random.randn()*2.0\n    pred_cy = gt_cy + np.random.randn()*1.5\n    all_ious.append(iou_approx(pred_cx, pred_cy, gt_cx, gt_cy))\n\nall_ious = np.array(all_ious)\nfor t in [0.3, 0.5, 0.7]:\n    ap = (all_ious>=t).mean()\n    print(f"  AP@{t:.1f}: {ap:.3f}")\n\nplt.hist(all_ious, bins=20, color='steelblue', edgecolor='white')\nplt.axvline(0.5, ls='--', color='red', label='0.5 threshold')\nplt.title('Detection IoU Distribution')\nplt.xlabel('IoU'); plt.legend()\nplt.savefig('/tmp/cap.png',dpi=80,bbox_inches='tight')\nprint("Evaluation done!")`,
        resources:[{label:'KITTI benchmark',url:'https://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d'},{label:'nuScenes eval',url:'https://www.nuscenes.org/object-detection'}]},
      { id:'week12', topic:'Optimization & Deployment', codeFile:'week12_deployment.py',
        content:'模型量化 (PTQ)、Inference 速度分析、筆記彙整。',
        desired:'完成公開網頁更新，展示所有 Chapter 的 Code 與 Demo。',
        goal:'PTQ INT8 量化分析 + inference latency comparison',
        starterCode:`import numpy as np\nimport matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n\n# Post-Training Quantization: FP32 → INT8\ndef quantize(tensor, bits=8):\n    alpha = np.abs(tensor).max()\n    levels = 2**(bits-1) - 1\n    scale  = alpha / levels\n    q = np.clip(np.round(tensor/scale), -levels, levels).astype(np.int8)\n    return q, scale\n\ndef dequantize(q, scale): return q.astype(np.float32)*scale\n\nnp.random.seed(12)\nW = np.random.randn(64,64).astype(np.float32)\n\nprint("Quantization MSE vs bit width:")\nfor bits in [4,6,8,16]:\n    q,s = quantize(W,bits)\n    W_r = dequantize(q,s)\n    mse = ((W-W_r)**2).mean()\n    mb  = W.nbytes*bits/32/1024**2\n    print(f"  INT{bits:2d}: MSE={mse:.6f}  size={mb:.1f}MB")\n\nprint("\\nFP32 baseline: MSE=0  size=1.0MB")`,
        resources:[{label:'ONNX Runtime',url:'https://onnxruntime.ai/'},{label:'TensorRT docs',url:'https://developer.nvidia.com/tensorrt'},{label:'Chip Huyen DMLS',url:'https://huyenchip.com/machine-learning-systems-design/toc.html'}]},
    ];

    // ════════════════════════════════════════════════════════════════════
    // INIT
    // ════════════════════════════════════════════════════════════════════
    function init() {
      const state = loadState();
      renderChapters(state);
      renderCaseStudy(state);
      renderSidebar(state, 'fundamentals');
      updateStats(state);
      if (localStorage.getItem(STORAGE_KEY)) {
        const el = document.getElementById('lastUpdated');
        if (el) el.textContent = 'Previously saved';
      }
    }

    init();
  })();
  </script>
</body>
</html>
