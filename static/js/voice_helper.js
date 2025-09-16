/*
  Voice Assistant Helper for Panchakarma Portal
  - Web Speech API (SpeechRecognition + speechSynthesis)
  - Conversational utilities (ask, yes/no, collectAadhaar, collectPassword)
  - Page flows: landing, login, patient_dashboard, book_detox, post_booking
  
  This is an accessibility add-on. It never interferes unless the user opens the voice assistant panel.
*/
(function(){
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const synth = window.speechSynthesis;
  const VOICE_PREFERENCES = ['en-IN', 'en-GB', 'en-US', 'en'];
  let CACHED_VOICE = null;

  function pickPreferredVoice(voices){
    if (!voices || !voices.length) return null;
    for (const pref of VOICE_PREFERENCES){
      const v = voices.find(v => (v.lang||'').toLowerCase().startsWith(pref.toLowerCase()));
      if (v) return v;
    }
    // Also try by name hints
    const india = voices.find(v => (v.name||'').toLowerCase().includes('india'));
    if (india) return india;
    return voices[0];
  }

  function getBestVoice(){
    return new Promise((resolve) => {
      if (!synth) return resolve(null);
      const tryPick = () => {
        const voices = synth.getVoices();
        if (voices && voices.length){
          CACHED_VOICE = CACHED_VOICE || pickPreferredVoice(voices);
          resolve(CACHED_VOICE);
          return true;
        }
        return false;
      };
      if (tryPick()) return;
      const onVoices = () => {
        synth.removeEventListener('voiceschanged', onVoices);
        tryPick();
      };
      synth.addEventListener('voiceschanged', onVoices);
      // Fallback timeout
      setTimeout(() => {
        synth.removeEventListener('voiceschanged', onVoices);
        tryPick();
      }, 1200);
    });
  }

  function wait(ms) { return new Promise(r => setTimeout(r, ms)); }

  function speakText(text, opts={}){
    return new Promise(async (resolve) => {
      if (!synth) { console.warn('speechSynthesis not supported'); return resolve(); }
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = opts.lang || 'en-IN';
      utter.rate = opts.rate || 1.0;
      utter.pitch = opts.pitch || 1.0;
      utter.volume = opts.volume == null ? 1.0 : opts.volume;
      try {
        const v = await getBestVoice();
        if (v) utter.voice = v;
      } catch(e){ /* ignore */ }
      utter.onend = () => resolve();
      utter.onerror = (e) => { console.error('TTS error', e); resolve(); };
      synth.cancel(); // ensure nothing queued blocks the new utterance
      synth.speak(utter);
    });
  }

  function toDigitsFromWords(str){
    if (!str) return '';
    const map = {
      'zero':'0','oh':'0','o':'0',
      'one':'1','won':'1','van':'1',
      'two':'2','to':'2','too':'2','tu':'2',
      'three':'3','tree':'3','free':'3',
      'four':'4','for':'4','fore':'4',
      'five':'5',
      'six':'6',
      'seven':'7',
      'eight':'8','ate':'8',
      'nine':'9'
    };
    let lowered = (''+str).toLowerCase();
    // Replace common separators
    lowered = lowered.replace(/[^a-z0-9 ]/g, ' ');
    const tokens = lowered.split(/\s+/).filter(Boolean);
    const digits = tokens.map(t => {
      if (/^\d+$/.test(t)) return t;
      return map[t] || '';
    }).join('');
    // If no conversion happened, fallback to stripping non-digits from original
    return digits || (''+str).replace(/\D/g, '');
  }

  function normalizeYesNo(str){
    if (!str) return null;
    const s = String(str).toLowerCase();
    const hasYes = /(^|\b)yes(\b|$)/.test(s);
    const hasNo  = /(^|\b)no(\b|$)/.test(s);
    if (hasYes && !hasNo) return 'yes';
    if (hasNo && !hasYes) return 'no';
    return null;
  }

  function includesAny(str, arr){
    const s = (str||'').toLowerCase();
    return arr.some(k => s.includes(k));
  }

  function normalizeEmailFromSpeech(str){
    if (!str) return '';
    let s = String(str).toLowerCase().trim();
    // Common replacements for spoken email
    s = s.replace(/\s+at\s+/g, '@');
    s = s.replace(/\s+dot\s+/g, '.');
    s = s.replace(/\s+underscore\s+/g, '_');
    s = s.replace(/\s+(dash|hyphen|minus)\s+/g, '-');
    s = s.replace(/\s+plus\s+/g, '+');
    s = s.replace(/\s+/g, '');
    // Sometimes STT expands common domains; ensure no trailing words
    return s;
  }

  function replaceNumberWordsInline(str){
    if (!str) return '';
    const map = {
      'zero':'0','oh':'0','o':'0',
      'one':'1','won':'1','van':'1',
      'two':'2','to':'2','too':'2','tu':'2',
      'three':'3','tree':'3','free':'3',
      'four':'4','for':'4','fore':'4',
      'five':'5',
      'six':'6',
      'seven':'7',
      'eight':'8','ate':'8',
      'nine':'9'
    };
    let out = ' ' + String(str).toLowerCase() + ' ';
    Object.keys(map).forEach(k => {
      out = out.replace(new RegExp('(^|\\b)'+k+'(\\b|$)','g'), (m, a,b) => a+map[k]+b);
    });
    return out.trim();
  }

  function normalizeSymbolsFromSpeech(str){
    if (!str) return '';
    let s = ' ' + String(str) + ' ';
    s = s.replace(/\s+underscore\s+/gi, '_');
    s = s.replace(/\s+(dash|hyphen|minus)\s+/gi, '-');
    s = s.replace(/\s+dot\s+/gi, '.');
    s = s.replace(/\s+space\s+/gi, '');
    return s.trim();
  }

  function buildPasswordCandidates(spoken){
    const set = new Set();
    const add = v => { if (v && v.length) set.add(v); };
    const base = (spoken||'').trim();
    const noTrail = base.replace(/[.,;!?]+$/,'').trim();
    add(base);
    add(noTrail);
    add(noTrail.replace(/\s+/g,''));
    const sym = normalizeSymbolsFromSpeech(noTrail);
    add(sym);
    add(sym.replace(/\s+/g,''));
    const num = replaceNumberWordsInline(noTrail);
    add(num);
    add(num.replace(/\s+/g,''));
    const symNum = replaceNumberWordsInline(sym);
    add(symNum);
    add(symNum.replace(/\s+/g,''));
    return Array.from(set).slice(0,6);
  }

  class VoiceAssistant{
    constructor(opts={}){
      this.panel = null;
      this.logEl = null;
      this.statusEl = null;
      this.toggleBtn = null;
      this.active = false;
      this.recognition = null;
      this.listening = false;
      this.currentFlow = null;
      this.page = 'none';
      this.opts = opts;

      this._bindUI();
      this._setupRecognition();
    }

    _bindUI(){
      const panelSel = this.opts.panelSelector || '#voice-assistant-panel';
      const toggleSel = this.opts.toggleSelector || '#voice-assistant-toggle';
      this.panel = document.querySelector(panelSel);
      this.toggleBtn = document.querySelector(toggleSel);
      this.logEl = this.panel ? this.panel.querySelector('#vap-log') : null;
      this.statusEl = this.panel ? this.panel.querySelector('#vap-status-text') : null;

      if (this.toggleBtn){
        this.toggleBtn.addEventListener('click', () => this.toggle());
      }
      const closeBtn = this.panel ? this.panel.querySelector('#vap-close') : null;
      if (closeBtn){
        closeBtn.addEventListener('click', () => this.close());
      }
    }

    _setupRecognition(){
      if (!SpeechRecognition) {
        console.warn('SpeechRecognition not supported');
        return;
      }
      this.recognition = new SpeechRecognition();
      this.recognition.lang = 'en-IN';
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.maxAlternatives = 5;
    }

    _setGrammar(words){
      try{
        const SpeechGrammarList = window.SpeechGrammarList || window.webkitSpeechGrammarList;
        if (!SpeechGrammarList || !this.recognition) return;
        const list = new SpeechGrammarList();
        if (Array.isArray(words) && words.length){
          const safe = words.map(w => String(w).trim()).filter(Boolean).join(' | ');
          const grammar = `#JSGF V1.0; grammar custom; public <alt> = ${safe} ;`;
          try { list.addFromString(grammar, 1); } catch(e){}
        }
        this.recognition.grammars = list;
      }catch(e){ /* ignore */ }
    }

    async _ensureMicPermission(){
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          }
        });
        // Immediately stop tracks so we don't hold the mic
        stream.getTracks().forEach(t => t.stop());
      } catch(e){
        console.warn('Microphone permission denied or error:', e);
      }
    }

    _beep(){
      try{
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return;
        const ctx = new Ctx();
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.type = 'sine';
        o.frequency.value = 880; // A5
        o.connect(g);
        g.connect(ctx.destination);
        g.gain.value = 0.05;
        o.start();
        setTimeout(() => { o.stop(); ctx.close(); }, 120);
      }catch(e){ /* ignore */ }
    }

    async toggle(){
      if (!this.active) return this.open();
      return this.close();
    }

    async open(){
      if (!synth || !SpeechRecognition){
        alert('Voice features are not supported in this browser. Please use the latest Chrome.');
        return;
      }
      await this._ensureMicPermission();
      if (this.panel){ this.panel.style.display = 'block'; }
      this.active = true;
      this._setStatus('Ready');
      this._appendLog('Assistant', 'Voice mode enabled.');
      // Prime voices and give immediate audible feedback to satisfy autoplay policies
      try { await speakText('Voice assistant enabled.'); } catch(e){}
      this.detectPage();
      await wait(200);
      await this.startFlowForCurrentPage();
    }

    close(){
      this.active = false;
      this._setStatus('Idle');
      this._stopListening();
      if (this.panel){ this.panel.style.display = 'none'; }
      this._appendLog('Assistant', 'Voice mode closed.');
    }

    detectPage(){
      const path = location.pathname;
      if (path === '/' || path === '/landing'){ this.page = 'landing'; }
      else if (path.startsWith('/auth/login')){ this.page = 'login'; }
      else if (path.startsWith('/patient/dashboard')){ this.page = 'patient_dashboard'; }
      else if (path.startsWith('/patient/book-detox')){ this.page = 'book_detox'; }
      else if (path.startsWith('/patient/detox-dashboard')){ this.page = 'detox_dashboard'; }
      else if (path.startsWith('/patient/detox-schedule/')){ this.page = 'detox_schedule'; }
      else if (path.startsWith('/patient/detox-progress/')){ this.page = 'detox_progress'; }
      else { this.page = 'none'; }
    }

    async startFlowForCurrentPage(){
      if (!this.active) return;
      if (this.page === 'landing') return this._flowLanding();
      if (this.page === 'login') return this._flowLogin();
      if (this.page === 'patient_dashboard') return this._flowPatientDashboard();
      if (this.page === 'book_detox') return this._flowBookDetox();
      if (this.page === 'detox_dashboard') return this._flowDetoxDashboard();
      if (this.page === 'detox_schedule') return this._flowDetoxSchedule();
      if (this.page === 'detox_progress') return this._flowDetoxProgress();
      await speakText('Voice assistant is ready. Navigate to a supported page to continue.');
    }

    _setStatus(text){ if (this.statusEl) this.statusEl.textContent = text; }

    _appendLog(who, text){
      if (!this.logEl) return;
      const row = document.createElement('div');
      row.className = 'vap-row';
      const whoEl = document.createElement('strong');
      whoEl.textContent = who + ': ';
      const textEl = document.createElement('span');
      textEl.textContent = text;
      row.appendChild(whoEl);
      row.appendChild(textEl);
      this.logEl.appendChild(row);
      this.logEl.scrollTop = this.logEl.scrollHeight;
    }

    async say(text, opts={}){
      this._setStatus('Speaking');
      this._appendLog('Assistant', text);
      await speakText(text, opts);
      this._setStatus('Ready');
    }

    _startListening(options={}){
      const { safetyMs=10000, dictation=true } = options;
      return new Promise((resolve) => {
        if (!this.recognition) return resolve(null);
        if (this.listening) try { this.recognition.stop(); } catch(e){}
        // Stop any TTS before listening to avoid echo pickup
        try { if (window.speechSynthesis && window.speechSynthesis.speaking) window.speechSynthesis.cancel(); } catch(e){}
        this.listening = true;
        this._setStatus('Listening');

        // Temporarily enable dictation-friendly settings
        const prevInterim = this.recognition.interimResults;
        const prevCont = this.recognition.continuous;
        this.recognition.interimResults = !!dictation;
        this.recognition.continuous = !!dictation;

        let settled = false;
        let finalTranscript = '';
        let interimTranscript = '';
        let safetyTimer = null;
        let silenceTimer = null;

        const pickBestAlt = (res) => {
          try{
            let best = res[0];
            for (let j=1; j<res.length; j++){
              if ((res[j].confidence||0) > (best.confidence||0)) best = res[j];
            }
            return best && best.transcript ? best.transcript : '';
          }catch(e){ return (res[0] && res[0].transcript) ? res[0].transcript : ''; }
        };

        const scheduleSilenceStop = () => {
          if (silenceTimer) clearTimeout(silenceTimer);
          // Stop ~1.2s after last result to allow user to finish
          silenceTimer = setTimeout(() => {
            try { this.recognition.stop(); } catch(e){}
          }, 1200);
        };

        const onResult = (event) => {
          for (let i=event.resultIndex; i<event.results.length; i++){
            const res = event.results[i];
            const txt = pickBestAlt(res);
            if (res.isFinal){
              finalTranscript += (finalTranscript ? ' ' : '') + (txt||'');
            } else {
              interimTranscript = txt || interimTranscript;
            }
          }
          scheduleSilenceStop();
        };
        const onErr = (err) => {
          if (settled) return;
          settled = true;
          this.listening = false;
          console.warn('Speech error', err);
          this._setStatus('Ready');
          cleanup();
          resolve((finalTranscript || interimTranscript || '').trim() || null);
        };
        const onEnd = () => {
          if (settled) return;
          settled = true;
          this.listening = false;
          this._setStatus('Ready');
          cleanup();
          resolve((finalTranscript || interimTranscript || '').trim() || null);
        };
        const cleanup = () => {
          this.recognition.removeEventListener('result', onResult);
          this.recognition.removeEventListener('error', onErr);
          this.recognition.removeEventListener('end', onEnd);
          if (safetyTimer) { clearTimeout(safetyTimer); safetyTimer = null; }
          if (silenceTimer) { clearTimeout(silenceTimer); silenceTimer = null; }
          // restore settings
          this.recognition.interimResults = prevInterim;
          this.recognition.continuous = prevCont;
        };

        this.recognition.addEventListener('result', onResult);
        this.recognition.addEventListener('error', onErr);
        this.recognition.addEventListener('end', onEnd);
        try { this.recognition.start(); } catch(e){ console.warn('start failed', e); resolve(null); }
        // Safety: stop after configured time if nothing came back
        safetyTimer = setTimeout(() => {
          try { this.recognition.stop(); } catch(e){}
        }, safetyMs);
      });
    }

    _stopListening(){
      try {
        if (this.recognition && this.listening) {
          this.recognition.stop();
        }
      } catch (e) {
        // ignore
      }
      this.listening = false;
      try {
        if (typeof window !== 'undefined' && window.speechSynthesis && window.speechSynthesis.speaking) {
          window.speechSynthesis.cancel();
        }
      } catch (e) {
        // ignore
      }
    }

    _stopTTS(){
      try {
        if (window.speechSynthesis && window.speechSynthesis.speaking) {
          window.speechSynthesis.cancel();
        }
      } catch(e) { /* ignore */ }
    }

    _handleCloseCommand(){
      // Sign out and close assistant
      this.active = false;
      try { window.location.href = '/auth/logout'; } catch(e){}
      this.close();
      return true;
    }

    _checkCloseCommand(text){
      const s = (text||'').toLowerCase();
      if (/(^|\b)(close|sign out|logout|log out)(\b|$)/.test(s)){
        this._handleCloseCommand();
        return true;
      }
      return false;
    }

    async ask(prompt, {validate, parse, reprompt='I did not catch that, please repeat.', maxRetries=3, listenOptions}={}){
      for (let i=0; i<maxRetries; i++){
        await this.say(prompt);
        await wait(350);
        this._beep();
        this._setGrammar(null);
        await wait(220);
        const heard = await this._startListening(listenOptions || {});
        const text = (heard||'').trim();
        if (this._checkCloseCommand(text)) return null;
        if (!text){
          await this.say(reprompt);
          continue;
        }
        let val = parse ? parse(text) : text;
        if (!validate || validate(val)) return val;
        await this.say(reprompt);
      }
      return null;
    }

    async askYesNo(question){
      for (let i=0; i<3; i++){
        await this.say(question);
        await wait(350);
        this._beep();
        this._setGrammar(['yes','no']);
        await wait(220);
        const heard = await this._startListening({dictation:false, safetyMs:6000});
        this._setGrammar(null);
        if (this._checkCloseCommand(heard)) return null;
        const yn = normalizeYesNo(heard);
        if (yn) return yn;
        await this.say("I didn't catch that, please say Yes or No.");
      }
      return null;
    }

    _getDetoxAppointmentsFromDashboard(){
      const items = [];
      try {
        const cards = document.querySelectorAll('.card');
        const seen = new Set();
        cards.forEach(card => {
          const plan = (card.querySelector('.card-header h6') || {}).textContent || '';
          const schedA = card.querySelector('a[href^="/patient/detox-schedule/"]');
          const progA = card.querySelector('a[href^="/patient/detox-progress/"]');
          let id = null;
          if (schedA) id = schedA.getAttribute('href').split('/').pop();
          if (!id && progA) id = progA.getAttribute('href').split('/').pop();
          if (id && !seen.has(id)){
            seen.add(id);
            items.push({ id, plan: (plan||'').trim(), hasSchedule: !!schedA, hasProgress: !!progA });
          }
        });
      } catch(e){ /* ignore */ }
      return items;
    }

    async _promptCloseOrBack(){
      await this.say('Say Close to sign out and close the assistant, or say Back to return to the Detox Dashboard.');
      await wait(300);
      this._beep();
      const heard = await this._startListening({dictation:false, safetyMs:8000});
      const s = (heard||'').toLowerCase();
      if (this._checkCloseCommand(s)) return true;
      if (/(^|\b)back(\b|$)/.test(s)){
        await this.say('Going back to the Detox Dashboard.');
        window.location.href = '/patient/detox-dashboard';
        return true;
      }
      return false;
    }

    async _flowLanding(){
      await this.say("If you want to continue exploring Panchakarma services, say 'Yes and Continue'. If not, click the cross and continue.");
      const ans = await this.askYesNo('Would you like to continue?');
      if (ans === 'yes'){
        const confirm = await this.askYesNo('Open Patient Login now?');
        if (confirm === 'yes'){
          await this.say('Opening Patient Login.');
          window.location.href = '/auth/login';
        } else {
          await this.say('Okay, staying here.');
        }
      } else if (ans === 'no') {
        await this.say('Okay. Closing voice assistant.');
        this.close();
      }
    }

    async _flowLogin(){
      // Username (name or email)
      let username = null;
      for (let i=0; i<3 && !username; i++){
        const u = await this.ask('Please say your username. You can say your full name or your email.', {
          parse: s => {
            const raw = (s||'').trim();
            const norm = normalizeEmailFromSpeech(raw);
            return (norm.includes('@') || /\sdot\s|\sat\s/.test(raw.toLowerCase())) ? norm : raw;
          },
          validate: v => v && v.length >= 2,
          listenOptions: { safetyMs: 18000, dictation: true }
        });
        if (!u) continue;
        const yn = await this.askYesNo(`I heard '${u}'. Is that correct?`);
        if (yn === 'yes') username = u; else await this.say('Okay, let us try again.');
      }
      if (!username){ await this.say('Unable to capture your username. Closing voice assistant.'); return; }

      // Password (spoken)
      await this.say('Please say your password. For your security, ensure you are in a private space.');
      const rawPassword = await this.ask('Speak your password now.', { parse: s => (s||'').trim(), validate: v => !!v, listenOptions: { safetyMs: 15000, dictation: true } });
      if (!rawPassword){ await this.say('Unable to capture password. Closing voice assistant.'); return; }

      // Confirm and submit
      const yn = await this.askYesNo('Shall I proceed to sign you in?');
      if (yn !== 'yes'){ await this.say('Cancelled login.'); return; }

      const attemptLogin = async (pwd) => {
        try{
          const res = await fetch('/auth/login', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: 'patient', username: username, password: pwd })
          });
          return await res.json();
        }catch(e){ return { success: false, message: 'network' }; }
      };

      const candidates = buildPasswordCandidates(rawPassword);
      let ok = null;
      for (const c of candidates){
        const data = await attemptLogin(c);
        if (data && data.success){ ok = data; break; }
      }
      if (ok && ok.success){
        await this.say('Login successful. Opening your dashboard.');
        window.location.href = ok.redirect || '/patient/dashboard';
      } else {
        await this.say('Invalid credentials. Please try again.');
        return this._flowLogin();
      }
    }

    async _flowPatientDashboard(){
      const name = (window.SESSION && window.SESSION.name) ? window.SESSION.name : 'Patient';
      await this.say(`Welcome, ${name}. Would you like to book detox therapy or open the detox dashboard?`);
      for (let i=0; i<3; i++){
        await wait(350);
        this._beep();
        const heard = await this._startListening();
        if (this._checkCloseCommand(heard)) return;
        if (includesAny(heard, ['book detox', 'book therapy', 'book', 'detox therapy'])){
          const yn = await this.askYesNo('Open the detox booking page now?');
          if (yn === 'yes'){
            await this.say('Opening the booking page.');
            window.location.href = '/patient/book-detox';
            return;
          }
          return;
        }
        if (includesAny(heard, ['detox dashboard', 'dashboard'])){
          const yn = await this.askYesNo('Open the Detox Dashboard now?');
          if (yn === 'yes'){
            await this.say('Opening the Detox Dashboard.');
            window.location.href = '/patient/detox-dashboard';
            return;
          }
          return;
        }
        await this.say("I didn't catch that. Please say 'Book Detox Therapy' or 'Detox Dashboard'.");
      }
    }

    _getCentres(){
      if (window.CENTRES && Array.isArray(window.CENTRES)) return window.CENTRES;
      // Fallback: read from select options if present
      const sel = document.getElementById('centre_id');
      if (!sel) return [];
      const arr = [];
      sel.querySelectorAll('option').forEach(opt => {
        if (opt.value){ arr.push({ centre_id: opt.value, name: opt.textContent.trim() }); }
      });
      return arr;
    }

    _getPlans(){
      // id->label mapping aligned with template
      return [
        { id:'weight_loss_short', label:'Weight Loss Short, 7 days' },
        { id:'weight_loss_full', label:'Weight Loss Full, 14 days' },
        { id:'diabetes_short', label:'Diabetes Short, 7 days' },
        { id:'diabetes_full', label:'Diabetes Full, 14 days' }
      ];
    }

    async _chooseFromList(prompt, items, key='label'){
      if (!items || items.length === 0) return null;
      // Read up to first 8 to avoid overly long TTS
      const toRead = items.slice(0, 8);
      await this.say(prompt);
      await this.say('Here are your options. You can say the number or the name.');
      for (let i=0; i<toRead.length; i++){
        await this.say(`${i+1}. ${toRead[i][key] || toRead[i].name}`);
      }
      for (let tries=0; tries<3; tries++){
        const heard = await this._startListening();
        if (this._checkCloseCommand(heard)) return null;
        const h = (heard||'').toLowerCase();
        // by index
        const digits = toDigitsFromWords(h);
        if (digits && /^\d+$/.test(digits)){
          const idx = parseInt(digits, 10) - 1;
          if (idx >= 0 && idx < toRead.length) return toRead[idx];
        }
        // by name match (contains)
        const match = toRead.find(x => (x[key]||x.name).toLowerCase().includes(h.trim()));
        if (match) return match;
        await this.say("I didn't catch that. Please say the number or the name again.");
      }
      return null;
    }

    _parseDateToYMD(str){
      // Try to extract date in various ways
      let s = (str||'').trim();
      // If contains digits only, treat as yyyymmdd or ddmmyyyy? Too ambiguous. Prefer natural parse.
      // Try Date.parse
      let d = new Date(s);
      if (isNaN(d.getTime())){
        // Replace spoken month names to numbers is handled by Date
        // Try extracting digits
        const digits = s.replace(/[^0-9]/g,' ');
        const parts = digits.split(/\s+/).filter(Boolean);
        // If three parts, assume dd mm yyyy
        if (parts.length >= 3){
          let [a,b,c] = parts.slice(0,3).map(x=>parseInt(x,10));
          // heuristic
          if (c < 100) c = 2000 + c; // 25 -> 2025
          // If a>31, assume a is year
          if (a > 31){ const y=a; const m=b; const d0=c; d = new Date(y, m-1, d0); }
          else { d = new Date(c, b-1, a); }
        }
      }
      if (isNaN(d.getTime())) return null;
      const yyyy = d.getFullYear();
      const mm = String(d.getMonth()+1).padStart(2,'0');
      const dd = String(d.getDate()).padStart(2,'0');
      return `${yyyy}-${mm}-${dd}`;
    }

    async _flowBookDetox(){
      // Choose centre
      const centres = this._getCentres();
      const centresReadList = centres.map(c => ({...c, label: c.name}));
      const centre = await this._chooseFromList('Please choose your centre.', centresReadList, 'label');
      if (!centre){ await this.say('Unable to capture centre. Closing voice assistant.'); return; }

      // Choose plan
      const plans = this._getPlans();
      const plan = await this._chooseFromList('Please choose your detox plan.', plans, 'label');
      if (!plan){ await this.say('Unable to capture plan. Closing voice assistant.'); return; }

      // Choose date
      let dateYMD = null;
      for (let i=0; i<3 && !dateYMD; i++){
        await this.say('Please say the date you want, for example, 20 September 2025.');
        const heard = await this._startListening();
        if (this._checkCloseCommand(heard)) return;
        const parsed = this._parseDateToYMD(heard);
        if (parsed) dateYMD = parsed; else await this.say("I didn't get the date. Please repeat.");
      }
      if (!dateYMD){ await this.say('Unable to capture date. Closing voice assistant.'); return; }

      // Confirm
      await this.say(`You selected Centre: ${centre.name}, Plan: ${plan.label}, Date: ${dateYMD}. Shall I submit? Yes or No.`);
      const yn = await this.askYesNo('Please say Yes to submit, or No to cancel.');
      if (yn !== 'yes'){ await this.say('Cancelled booking.'); return; }

      // Submit
      try{
        const res = await fetch('/patient/book-detox', {
          method: 'POST',
          headers: { 'Content-Type':'application/json' },
          body: JSON.stringify({ centre_id: centre.centre_id, plan_type: plan.id, start_date: dateYMD })
        });
        const data = await res.json();
        if (data && data.success){
          await this.say('Your detox therapy request was submitted successfully.');
          // Post booking flow
          await this._flowPostBooking();
        } else {
          await this.say('Booking failed. The date may be out of range or there was a server error. Please try again.');
          return this._flowBookDetox();
        }
      }catch(e){
        console.error(e);
        await this.say('Network error while submitting booking. Please try again.');
        return this._flowBookDetox();
      }
    }

    async _flowPostBooking(){
      const ans1 = await this.askYesNo('For more details, do you want to go to the Detox Dashboard?');
      if (ans1 === 'yes'){
        await this.say('Opening Detox Dashboard.');
        window.location.href = '/patient/detox-dashboard';
        return;
      }
      const ans2 = await this.askYesNo('Do you want to sign out?');
      if (ans2 === 'yes'){
        await this.say('Signing you out.');
        window.location.href = '/auth/logout';
      } else {
        await this.say('Okay. Remaining on the dashboard.');
        window.location.href = '/patient/dashboard';
      }
    }

    async _flowDetoxDashboard(){
      const items = this._getDetoxAppointmentsFromDashboard();
      if (!items || items.length === 0){
        await this.say('You have no detox therapy appointments yet. You can book one from here.');
        return;
      }
      await this.say('On Detox Dashboard. Say View Schedule or View Progress.');
      let action = null; // 'schedule' | 'progress'
      for (let i=0; i<3 && !action; i++){
        await wait(300); this._beep();
        const heard = await this._startListening({dictation:false, safetyMs:8000});
        if (this._checkCloseCommand(heard)) return;
        const s = (heard||'').toLowerCase();
        if (s.includes('schedule')) action = 'schedule';
        else if (s.includes('progress')) action = 'progress';
        if (!action) await this.say("Please say 'View Schedule' or 'View Progress'.");
      }
      if (!action){ await this.say('Unable to capture your choice.'); return; }

      let chosen = null;
      if (items.length === 1){
        chosen = items[0];
      } else {
        // Read list and ask selection
        const listToRead = items.slice(0, 8).map((x, i) => `${i+1}. ${x.plan || 'Detox Plan'}`);
        await this.say('You have multiple detox appointments.');
        for (const l of listToRead){ await this.say(l); }
        const picked = await this._chooseFromList('Please choose an appointment by number or name.', items, 'plan');
        chosen = picked;
      }
      if (!chosen){ await this.say('Unable to choose an appointment.'); return; }

      if (action === 'schedule'){
        await this.say('Opening schedule.');
        window.location.href = `/patient/detox-schedule/${chosen.id}`;
      } else {
        await this.say('Opening progress.');
        window.location.href = `/patient/detox-progress/${chosen.id}`;
      }
    }

    async _flowDetoxSchedule(){
      // Read quick summary from DOM
      try{
        const plan = ((document.querySelector('.card .card-header.bg-primary h5')||{}).textContent||'').trim();
        // helper to read value after a <strong>Label:</strong>
        const readByLabel = (labelStartsWith) => {
          const els = Array.from(document.querySelectorAll('strong'));
          const el = els.find(e => (e.textContent||'').trim().toLowerCase().startsWith(labelStartsWith));
          if (!el) return '';
          const parent = el.parentElement;
          if (!parent) return '';
          return (parent.textContent||'').replace(el.textContent,'').trim();
        };
        const startDate = readByLabel('start date');
        const duration = readByLabel('duration');
        const therapyTime = readByLabel('therapy time');
        let status = '';
        try{
          const badge = document.querySelector('.card .badge');
          status = (badge && badge.textContent || '').trim();
        }catch(e){}
        const parts = [];
        if (plan) parts.push(`Plan ${plan}`);
        if (startDate) parts.push(`Start date ${startDate}`);
        if (duration) parts.push(`Duration ${duration}`);
        if (therapyTime) parts.push(`Therapy time ${therapyTime}`);
        if (status) parts.push(`Status ${status}`);
        if (parts.length){ await this.say(parts.join('. ') + '.'); }

        // Read first day first two slots if present
        const firstDay = document.querySelector('#scheduleAccordion .accordion-item');
        if (firstDay){
          const header = firstDay.querySelector('strong');
          const headerText = (header && header.textContent || '').trim();
          if (headerText) await this.say(headerText);
          const slotHeaders = firstDay.querySelectorAll('.card-header h6');
          for (let i=0; i<Math.min(2, slotHeaders.length); i++){
            const t = (slotHeaders[i].textContent||'').trim();
            if (t) await this.say(t);
          }
        }
      }catch(e){ /* ignore */ }

      // Offer close/back
      await this._promptCloseOrBack();
    }

    async _flowDetoxProgress(){
      try{
        const plan = ((document.querySelector('.card .card-header.bg-primary h5')||{}).textContent||'').trim();
        const readByLabel = (labelStartsWith) => {
          const els = Array.from(document.querySelectorAll('strong'));
          const el = els.find(e => (e.textContent||'').trim().toLowerCase().startsWith(labelStartsWith));
          if (!el) return '';
          const parent = el.parentElement;
          if (!parent) return '';
          return (parent.textContent||'').replace(el.textContent,'').trim();
        };
        const startDate = readByLabel('start date');
        const duration = readByLabel('duration');
        const status = (()=>{
          try{
            const badge = document.querySelector('.card .badge');
            return (badge && badge.textContent || '').trim();
          }catch(e){ return ''; }
        })();
        const parts = [];
        if (plan) parts.push(`Plan ${plan}`);
        if (startDate) parts.push(`Start date ${startDate}`);
        if (duration) parts.push(`Duration ${duration}`);
        if (status) parts.push(`Status ${status}`);
        if (parts.length){ await this.say(parts.join('. ') + '.'); }

        // Read first daily progress summary if available
        const firstSummary = document.querySelector('.card.border-left-primary .card-body');
        if (firstSummary){
          const dayTitle = (firstSummary.querySelector('.card-title')||{}).textContent||'';
          if (dayTitle) await this.say(dayTitle);
          const scoreEl = firstSummary.querySelector('.badge.bg-success');
          if (scoreEl){ await this.say(`Progress score ${scoreEl.textContent}`); }
          const vitalsList = firstSummary.querySelectorAll('ul.list-unstyled li');
          if (vitalsList && vitalsList.length){
            const v0 = (vitalsList[0].textContent||'').trim();
            await this.say(`Vitals example: ${v0}`);
          }
        }
      }catch(e){ /* ignore */ }

      await this._promptCloseOrBack();
    }
  }

  // Expose
  window.VoiceAssistant = VoiceAssistant;
})();
