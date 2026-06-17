/* ─────────────────────────────────────────────────────────────
   Adnan K. — Floating widgets
   1) Cookie consent (must run before chatbot)
   2) AI chatbot (Groq-backed via /api/chat)
   3) Lead capture inside chatbot → /api/chat falls through to email
   ───────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  // ─────────── COOKIE CONSENT ───────────
  const COOKIE_KEY = 'adnank-cookie-consent-v1';
  const consent = (() => {
    try { return localStorage.getItem(COOKIE_KEY); } catch { return null; }
  })();

  function setConsent(val) {
    try { localStorage.setItem(COOKIE_KEY, val); } catch {}
    document.dispatchEvent(new CustomEvent('cookie:consent', { detail: val }));
    const banner = document.getElementById('cookieBanner');
    if (banner) {
      banner.style.opacity = '0';
      banner.style.transform = 'translateY(20px)';
      setTimeout(() => banner.remove(), 300);
    }
  }

  function mountCookieBanner() {
    if (consent) return;
    const html = `
      <div id="cookieBanner" class="cookie-banner" role="region" aria-label="Cookie consent">
        <div class="cookie-inner">
          <p class="cookie-text">
            This site uses a small amount of localStorage to remember your visit and run the chat widget. Nothing is sold, shared, or tracked across the web. <a href="/cookie-policy.html">Read the cookie policy</a>.
          </p>
          <div class="cookie-actions">
            <button type="button" class="cookie-btn cookie-decline" data-decline>Decline</button>
            <button type="button" class="cookie-btn cookie-accept" data-accept>Accept</button>
          </div>
        </div>
      </div>`;
    document.body.insertAdjacentHTML('beforeend', html);
    document.querySelector('[data-accept]')?.addEventListener('click', () => setConsent('accepted'));
    document.querySelector('[data-decline]')?.addEventListener('click', () => setConsent('declined'));
  }

  // ─────────── CHATBOT ───────────
  const CHAT_KEY = 'adnank-chat-history-v1';
  const calendlyURL = 'https://calendly.com/adnan-technodigg';
  const formAnchor = '/#contact';

  function getHistory() {
    try { return JSON.parse(localStorage.getItem(CHAT_KEY) || '[]'); } catch { return []; }
  }
  function saveHistory(h) {
    if (consent !== 'accepted') return; // respect declined
    try { localStorage.setItem(CHAT_KEY, JSON.stringify(h.slice(-20))); } catch {}
  }

  function mountChatbot() {
    const html = `
      <button id="chatLauncher" class="chat-launcher" aria-label="Open chat" aria-expanded="false">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
        </svg>
        <span class="chat-launcher-label">Ask&nbsp;the&nbsp;studio</span>
        <span class="chat-launcher-dot" aria-hidden="true"></span>
      </button>

      <div id="chatPanel" class="chat-panel" role="dialog" aria-label="Chat with Adnan's studio" aria-hidden="true">
        <header class="chat-head">
          <div class="chat-head-meta">
            <div class="chat-avatar" aria-hidden="true">AK</div>
            <div>
              <p class="chat-name">Adnan K. &mdash; Studio</p>
              <p class="chat-sub"><span class="chat-pulse"></span> Usually replies in 4 hours</p>
            </div>
          </div>
          <button type="button" class="chat-close" aria-label="Close chat" data-chat-close>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </header>

        <div id="chatLog" class="chat-log" role="log" aria-live="polite"></div>

        <div id="chatQuick" class="chat-quick">
          <button type="button" class="chat-chip" data-q="What does a typical Shopify build effort?">What does a build effort?</button>
          <button type="button" class="chat-chip" data-q="What's your process for a new project?">What&rsquo;s the process?</button>
          <button type="button" class="chat-chip" data-q="Can you migrate my store to Shopify Plus?">Plus migration?</button>
          <button type="button" class="chat-chip" data-q="I'd like to book a call with Adnan.">Book a call</button>
        </div>

        <form id="chatForm" class="chat-form" autocomplete="off">
          <label class="sr-only" for="chatInput">Type a message</label>
          <input id="chatInput" type="text" placeholder="Ask anything &mdash; scoping, process, scope&hellip;" required maxlength="600" />
          <button type="submit" class="chat-send" aria-label="Send message">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          </button>
        </form>

        <p class="chat-foot">AI-powered &middot; <a href="/cookie-policy.html">Cookie policy</a> &middot; <a href="/#contact">Contact form</a></p>
      </div>`;
    document.body.insertAdjacentHTML('beforeend', html);

    const launcher = document.getElementById('chatLauncher');
    const panel = document.getElementById('chatPanel');
    const log = document.getElementById('chatLog');
    const form = document.getElementById('chatForm');
    const input = document.getElementById('chatInput');
    const quick = document.getElementById('chatQuick');

    let history = getHistory();
    let isOpen = false;
    let isThinking = false;
    let turnCount = history.filter(m => m.role === 'user').length;
    let emailCaptureShown = false;

    function open() {
      panel.classList.add('open');
      panel.setAttribute('aria-hidden', 'false');
      launcher.setAttribute('aria-expanded', 'true');
      launcher.classList.add('chat-launcher-open');
      document.body.classList.add('chat-open');
      isOpen = true;
      if (!history.length) bootGreeting();
      // On mobile full-screen, lock body scroll
      if (window.innerWidth <= 640) document.body.style.overflow = 'hidden';
      setTimeout(() => input.focus(), 350);
    }
    function close() {
      panel.classList.remove('open');
      panel.setAttribute('aria-hidden', 'true');
      launcher.setAttribute('aria-expanded', 'false');
      launcher.classList.remove('chat-launcher-open');
      document.body.classList.remove('chat-open');
      document.body.style.overflow = '';
      isOpen = false;
    }
    function toggle() { isOpen ? close() : open(); }
    launcher.addEventListener('click', toggle);
    panel.querySelector('[data-chat-close]').addEventListener('click', close);

    function render() {
      log.innerHTML = '';
      history.forEach(m => {
        const div = document.createElement('div');
        div.className = 'chat-msg chat-msg-' + m.role;
        if (m.html) {
          div.innerHTML = m.content;
        } else {
          div.textContent = m.content;
        }
        log.appendChild(div);
      });
      log.scrollTop = log.scrollHeight;
    }

    function pushUser(text) {
      history.push({ role: 'user', content: text });
      saveHistory(history);
      render();
      turnCount += 1;
    }
    function pushAssistant(text, opts) {
      history.push({ role: 'assistant', content: text, html: !!(opts && opts.html) });
      saveHistory(history);
      render();
    }
    function pushTyping() {
      const div = document.createElement('div');
      div.className = 'chat-msg chat-msg-assistant chat-typing';
      div.id = 'chatTyping';
      div.innerHTML = '<span></span><span></span><span></span>';
      log.appendChild(div);
      log.scrollTop = log.scrollHeight;
    }
    function popTyping() { document.getElementById('chatTyping')?.remove(); }

    function bootGreeting() {
      pushAssistant("Hi &mdash; I'm Adnan's assistant. Ask me about scoping, process, or specific platform questions. If it's a fit I'll point you at the booking form. What's on your mind?", { html: true });
    }

    async function sendToAI(userText) {
      isThinking = true;
      pushTyping();
      try {
        const r = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            messages: history.filter(m => m.role === 'user' || m.role === 'assistant').slice(-10).map(m => ({
              role: m.role,
              content: (m.content || '').replace(/<[^>]+>/g, '')
            }))
          })
        });
        const data = await r.json();
        popTyping();
        pushAssistant(data.reply || "I didn't catch that — could you rephrase?");
      } catch (e) {
        popTyping();
        pushAssistant("Connection blip. Email <a href='mailto:hi@lofts.studio' class='chat-link'>hi@lofts.studio</a> or use <a href='/#contact' class='chat-link'>the contact form</a> &mdash; the team replies within 4 hours.", { html: true });
      } finally {
        isThinking = false;
        maybeShowEmailCapture();
      }
    }

    function maybeShowEmailCapture() {
      if (emailCaptureShown) return;
      if (turnCount < 3) return;
      emailCaptureShown = true;
      const html = `<div class="chat-cta">
        <p class="chat-cta-eyebrow">Ready to talk specifics?</p>
        <p class="chat-cta-text">Adnan reviews every brief personally and replies within four hours with three concrete suggestions &mdash; whether you hire him or not.</p>
        <div class="chat-cta-actions">
          <a href="${formAnchor}" class="chat-cta-btn chat-cta-primary">
            Start a conversation
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
          </a>
        </div>
      </div>`;
      pushAssistant(html, { html: true });
    }

    quick.addEventListener('click', e => {
      const btn = e.target.closest('.chat-chip');
      if (!btn || isThinking) return;
      const q = btn.dataset.q;
      if (q === "I'd like to book a call with Adnan.") {
        pushUser(q);
        pushAssistant(`Best way is the form on the homepage &mdash; <a href='${formAnchor}' class='chat-link'>open it here</a>. Adnan replies in 4 hours with three suggestions for your project, whether you hire him or not.`, { html: true });
        return;
      }
      pushUser(q);
      sendToAI(q);
    });

    form.addEventListener('submit', e => {
      e.preventDefault();
      if (isThinking) return;
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      pushUser(text);
      sendToAI(text);
    });

    render();

    // Initial subtle attention bump after 12s
    setTimeout(() => {
      if (!isOpen) launcher.classList.add('chat-launcher-bump');
      setTimeout(() => launcher.classList.remove('chat-launcher-bump'), 1400);
    }, 12000);
  }

  // ─────────── BOOT ───────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
  function mountMobileBar() {
    const bar = document.createElement('nav');
    bar.className = 'mob-bar';
    bar.setAttribute('aria-label', 'Quick navigation');
    bar.innerHTML = `
      <a href="/portfolio/" class="mob-bar-item" aria-label="View portfolio">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1.2"/><rect x="14" y="3" width="7" height="7" rx="1.2"/><rect x="14" y="14" width="7" height="7" rx="1.2"/><rect x="3" y="14" width="7" height="7" rx="1.2"/></svg>
        <span>Work</span>
      </a>
      <button type="button" class="mob-bar-item mob-bar-cta" id="mobConversationBtn" aria-label="Start a conversation">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
        Start a conversation
      </button>
      <button type="button" class="mob-bar-item" id="mobBarChatBtn" aria-label="Ask the studio">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
        <span>Ask</span>
      </button>`;
    document.body.appendChild(bar);

    // Glass popup for "Start a conversation"
    const popup = document.createElement('div');
    popup.id = 'convPopup';
    popup.className = 'conv-popup';
    popup.setAttribute('aria-modal', 'true');
    popup.setAttribute('role', 'dialog');
    popup.innerHTML = `
      <div class="conv-popup-backdrop" id="convPopupBackdrop"></div>
      <div class="conv-popup-sheet">
        <div class="conv-popup-handle"></div>

        <!-- View 1: action buttons -->
        <div id="convViewActions">
          <div class="conv-popup-avatar">LS</div>
          <h3 class="conv-popup-title">Let&rsquo;s talk about your project</h3>
          <p class="conv-popup-sub">Tell us what you&rsquo;re building. We&rsquo;ll come back with three specific ideas &mdash; no pitch, no fluff.</p>
          <div class="conv-popup-actions">
            <button type="button" class="conv-popup-btn-primary" id="convShowForm">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="2,4 12,13 22,4"/></svg>
              Send a message
            </button>
            <button type="button" class="conv-popup-btn-secondary" id="convPopupChat">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
              Chat with the studio AI
            </button>
            <a href="mailto:hi@lofts.studio" class="conv-popup-btn-ghost">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              hi@lofts.studio
            </a>
          </div>
          <p class="conv-popup-note">Mon&ndash;Sat &middot; US &amp; UK hours covered</p>
        </div>

        <!-- View 2: inline form -->
        <div id="convViewForm" style="display:none">
          <button type="button" class="conv-popup-back" id="convBackBtn">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            Back
          </button>
          <h3 class="conv-popup-title" style="margin-top:0.6rem">Send us a message</h3>
          <p class="conv-popup-sub">We reply within 4 hours, Mon&ndash;Sat.</p>
          <form id="convInlineForm" class="conv-inline-form" novalidate>
            <input type="text"  name="name"    id="convName"    class="conv-field" placeholder="Your name"            required autocomplete="name" />
            <input type="email" name="email"   id="convEmail"   class="conv-field" placeholder="your@email.com"       required autocomplete="email" />
            <textarea           name="message" id="convMessage" class="conv-field conv-field-ta" placeholder="Tell us about your project…" rows="3" required></textarea>
            <div id="convFormError" class="conv-form-error" style="display:none">Please fill in all fields.</div>
            <button type="submit" class="conv-popup-btn-primary" id="convSubmitBtn">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
              Send message
            </button>
          </form>
        </div>

        <!-- View 3: success -->
        <div id="convViewSuccess" style="display:none;text-align:center;padding:1rem 0 0.5rem">
          <div class="conv-success-check">
            <svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <h3 class="conv-popup-title" style="margin-top:1rem">Message sent!</h3>
          <p class="conv-popup-sub">We&rsquo;ll reply within 4 hours with three specific ideas for your project.</p>
          <button type="button" class="conv-popup-btn-secondary" id="convDoneBtn">Done</button>
        </div>

      </div>`;
    document.body.appendChild(popup);

    function showView(id) {
      ['convViewActions','convViewForm','convViewSuccess'].forEach(v => {
        const el = document.getElementById(v);
        if (el) el.style.display = (v === id) ? '' : 'none';
      });
    }

    function openPopup() {
      showView('convViewActions');
      popup.classList.add('open');
      document.body.classList.add('menu-lock');
    }
    function closePopup() {
      popup.classList.remove('open');
      document.body.classList.remove('menu-lock');
    }

    document.getElementById('mobConversationBtn')?.addEventListener('click', openPopup);
    document.getElementById('convPopupBackdrop')?.addEventListener('click', closePopup);
    document.getElementById('convDoneBtn')?.addEventListener('click', closePopup);
    document.getElementById('convBackBtn')?.addEventListener('click', () => showView('convViewActions'));

    document.getElementById('convShowForm')?.addEventListener('click', () => {
      showView('convViewForm');
      setTimeout(() => document.getElementById('convName')?.focus(), 200);
    });

    document.getElementById('convPopupChat')?.addEventListener('click', () => {
      closePopup();
      setTimeout(() => document.getElementById('chatLauncher')?.click(), 100);
    });

    document.getElementById('convInlineForm')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name    = document.getElementById('convName')?.value.trim();
      const email   = document.getElementById('convEmail')?.value.trim();
      const message = document.getElementById('convMessage')?.value.trim();
      const errEl   = document.getElementById('convFormError');
      const btn     = document.getElementById('convSubmitBtn');
      if (!name || !email || !message) { if (errEl) errEl.style.display = ''; return; }
      if (errEl) errEl.style.display = 'none';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      try {
        await fetch('/api/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, message, source: 'mobile-popup' }),
        });
      } catch {}
      showView('convViewSuccess');
    });

    // Wire AI chat button
    document.getElementById('mobBarChatBtn')?.addEventListener('click', () => {
      document.getElementById('chatLauncher')?.click();
    });
  }

  function boot() {
    mountCookieBanner();
    // Mount chatbot regardless of consent — but it won't persist history if declined.
    mountChatbot();
    mountMobileBar();
  }
})();

/* ─────────────────────────────────────────────────────────────
   Improvement pack: custom cursor + device mockup + sticky CTA
   Boots only when its target elements exist in the DOM.
   ───────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  // ── 1. Custom cursor — terracotta dot + outline ring ──
  function bootCursor() {
    const hoverable = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!hoverable || reduced) return;

    const dot = document.createElement('div');
    dot.className = 'cursor-dot';
    const ring = document.createElement('div');
    ring.className = 'cursor-ring';
    document.body.appendChild(dot);
    document.body.appendChild(ring);
    document.body.classList.add('cursor-ready');

    let mx = window.innerWidth / 2, my = window.innerHeight / 2;
    let rx = mx, ry = my;
    window.addEventListener('mousemove', e => {
      mx = e.clientX; my = e.clientY;
      dot.style.transform = `translate3d(${mx}px, ${my}px, 0)`;
    }, { passive: true });

    // Ring lags behind for elegance
    function raf() {
      rx += (mx - rx) * 0.18;
      ry += (my - ry) * 0.18;
      ring.style.transform = `translate3d(${rx}px, ${ry}px, 0)`;
      requestAnimationFrame(raf);
    }
    raf();

    // Hover state on interactive elements
    const HOVER_SEL = 'a, button, input, textarea, select, [role="button"], .work-card, .case-study a, details summary, [data-cursor-hover]';
    document.addEventListener('mouseover', e => {
      if (e.target.closest && e.target.closest(HOVER_SEL)) document.body.classList.add('cursor-hover');
    });
    document.addEventListener('mouseout', e => {
      if (e.target.closest && e.target.closest(HOVER_SEL)) document.body.classList.remove('cursor-hover');
    });

    // Hide when leaving window
    document.addEventListener('mouseleave', () => {
      dot.style.opacity = '0';
      ring.style.opacity = '0';
    });
    document.addEventListener('mouseenter', () => {
      dot.style.opacity = '1';
      ring.style.opacity = '';
    });
  }

  // ── 2. Device mockup rotator — fade through client screenshots ──
  function bootDeviceMockup() {
    const mockup = document.querySelector('[data-device-mockup]');
    if (!mockup) return;
    const slides = mockup.querySelectorAll('.device-slide');
    const urlEl = mockup.querySelector('.device-chrome-url');
    const captionName = mockup.querySelector('.device-caption-name');
    const captionTag = mockup.querySelector('.device-caption-tag');
    const progress = mockup.querySelector('.device-progress');
    if (!slides.length) return;

    const DURATION = 4200; // ms per slide
    let i = 0;
    let lastTs = performance.now();
    let elapsed = 0;
    let paused = false;

    function showSlide(idx) {
      slides.forEach((s, j) => s.classList.toggle('is-active', j === idx));
      const active = slides[idx];
      if (urlEl) urlEl.textContent = active.dataset.url || '';
      if (captionName) captionName.textContent = active.dataset.name || '';
      if (captionTag) captionTag.textContent = active.dataset.tag || '';
    }
    showSlide(0);

    function tick(ts) {
      if (!paused) {
        const dt = ts - lastTs;
        elapsed += dt;
        if (progress) progress.style.width = Math.min(100, (elapsed / DURATION) * 100) + '%';
        if (elapsed >= DURATION) {
          i = (i + 1) % slides.length;
          showSlide(i);
          elapsed = 0;
          if (progress) progress.style.width = '0%';
        }
      }
      lastTs = ts;
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);

    mockup.addEventListener('mouseenter', () => { paused = true; });
    mockup.addEventListener('mouseleave', () => { paused = false; });
  }

  // ── 3. Sticky "Book a free audit" pill — appears after hero ──
  function bootAuditCTA() {
    const cta = document.querySelector('.audit-cta');
    if (!cta) return;
    let shown = false;
    function check() {
      const scrolled = window.scrollY > window.innerHeight * 0.7;
      if (scrolled !== shown) {
        cta.classList.toggle('is-visible', scrolled);
        shown = scrolled;
      }
    }
    window.addEventListener('scroll', check, { passive: true });
    check();
  }

  function init() {
    bootCursor();
    bootDeviceMockup();
    bootAuditCTA();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
