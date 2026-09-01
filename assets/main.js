/* ─────────────────────────────────────────────────────────────
   Adnan K. — shared interactivity
   ───────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  const adAttributionKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'gbraid', 'wbraid'];
  const adAttributionStore = 'lofts_ad_attribution';
  const marketingConsentStore = 'adnank-cookie-consent-v1';

  const hasMarketingConsent = () => {
    try {
      return window.localStorage.getItem(marketingConsentStore) === 'accepted';
    } catch {
      return false;
    }
  };

  const readStoredAttribution = () => {
    try {
      return JSON.parse(window.sessionStorage.getItem(adAttributionStore) || '{}') || {};
    } catch {
      return {};
    }
  };

  const persistAdAttribution = () => {
    try {
      const params = new URLSearchParams(window.location.search);
      const next = {};
      adAttributionKeys.forEach(key => {
        const value = params.get(key);
        if (value) next[key] = value;
      });
      if (!Object.keys(next).length) return;
      next.landing_page = window.location.href;
      next.referrer = document.referrer || '';
      next.captured_at = new Date().toISOString();
      window.sessionStorage.setItem(adAttributionStore, JSON.stringify(next));
    } catch {
      // Attribution is useful, but never worth breaking the page over.
    }
  };

  const getAdAttribution = () => {
    const stored = readStoredAttribution();
    return {
      ...stored,
      landing_page: stored.landing_page || window.location.href,
      referrer: stored.referrer || document.referrer || ''
    };
  };

  const appendAdAttribution = (formData) => {
    const attribution = getAdAttribution();
    Object.entries(attribution).forEach(([key, value]) => {
      if (value && !formData.has(key)) formData.append(key, value);
    });
    return attribution;
  };

  const trackMarketingEvent = (eventName, params = {}) => {
    if (!hasMarketingConsent()) return false;
    const payload = {
      ...params,
      page_path: window.location.pathname,
      page_title: document.title
    };
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: eventName, ...payload });
    if (typeof window.gtag === 'function') {
      window.gtag('event', eventName, payload);
    }
    return true;
  };

  persistAdAttribution();
  window.loftsGetAdAttribution = getAdAttribution;
  window.loftsTrackEvent = trackMarketingEvent;

  // Normalize legacy page headers to the same masthead used on the homepage.
  // Hundreds of static routes share this bootstrap, so the repair belongs here.
  function normalizeGlobalHeader() {
    const nav = document.querySelector('.nav-bar');
    if (!nav) return;

    let inner = nav.querySelector('.nav-inner');
    if (!inner) {
      inner = document.createElement('div');
      inner.className = 'nav-inner';
      while (nav.firstChild) inner.appendChild(nav.firstChild);
      nav.appendChild(inner);
    }

    let logo = inner.querySelector('.nav-logo');
    if (!logo) {
      logo = document.createElement('a');
      logo.className = 'nav-logo';
      inner.prepend(logo);
    }
    logo.href = '/';
    logo.setAttribute('aria-label', 'Lofts Studio home');
    logo.innerHTML = 'Lofts<span class="dot">studio</span>';

    let links = inner.querySelector('.nav-links');
    if (!links) {
      links = document.createElement('nav');
      links.className = 'nav-links';
      logo.insertAdjacentElement('afterend', links);
    }
    links.setAttribute('aria-label', 'Primary');
    links.innerHTML = `
      <div class="mega-wrap">
        <button class="nav-link" type="button" data-mega-trigger aria-expanded="false" aria-haspopup="true">
          Work
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="mega">
          <div class="mega-col">
            <h4>By vertical</h4>
            <a href="/work/ecommerce" class="mega-link"><div class="mega-link-title">Ecommerce</div><div class="mega-link-desc">Shopify, WooCommerce, headless.</div></a>
            <a href="/work/insurance-finance" class="mega-link"><div class="mega-link-title">Insurance &amp; Finance</div><div class="mega-link-desc">Brokers, carriers, reinsurance.</div></a>
            <a href="/work/membership-community" class="mega-link"><div class="mega-link-title">Membership &amp; Community</div><div class="mega-link-desc">Stripe, Discord, Whop.</div></a>
            <a href="/work/custom-apps" class="mega-link"><div class="mega-link-title">Custom Apps</div><div class="mega-link-desc">React, Next.js, Node.</div></a>
          </div>
          <div class="mega-col">
            <h4>Storefront</h4>
            <a href="/services/shopify-development.html" class="mega-link"><div class="mega-link-title">Shopify Development</div><div class="mega-link-desc">Custom themes. Shopify Plus.</div></a>
            <a href="/services/woocommerce-development.html" class="mega-link"><div class="mega-link-title">WooCommerce Development</div><div class="mega-link-desc">WordPress commerce, done right.</div></a>
            <a href="/services/shopify-plus-migration.html" class="mega-link"><div class="mega-link-title">Shopify Plus Migration</div><div class="mega-link-desc">Replatform without downtime.</div></a>
            <a href="/services/webflow-development.html" class="mega-link"><div class="mega-link-title">Webflow Development</div><div class="mega-link-desc">SaaS, B2B, brand-led sites.</div></a>
          </div>
          <div class="mega-col">
            <h4>Performance</h4>
            <a href="/services/speed-optimization.html" class="mega-link"><div class="mega-link-title">Speed Optimization</div><div class="mega-link-desc">Improve real-world loading.</div></a>
            <a href="/services/conversion-rate-optimization.html" class="mega-link"><div class="mega-link-title">Conversion Rate Optimization</div><div class="mega-link-desc">Remove conversion friction.</div></a>
            <a href="/services/technical-seo-audit.html" class="mega-link"><div class="mega-link-title">Technical SEO Audit</div><div class="mega-link-desc">Crawl, structure, and search signals.</div></a>
            <a href="/services/landing-page-sprint.html" class="mega-link"><div class="mega-link-title">Landing Page Sprint</div><div class="mega-link-desc">Focused launch sprint.</div></a>
          </div>
          <div class="mega-feature">
            <div>
              <span class="tag">Two founders. Two cities.</span>
              <h3>Senior strategy, design, and engineering from brief to launch.</h3>
            </div>
            <a href="/about.html" class="btn-link">Meet the founders <span aria-hidden="true">→</span></a>
          </div>
        </div>
      </div>
      <a href="/websites" class="nav-link">Web Design</a>
      <a href="/portfolio" class="nav-link">Portfolio</a>
      <a href="/process" class="nav-link">Process</a>
      <a href="/blog" class="nav-link">Blog</a>
      <a href="/tools" class="nav-link">Tools</a>
      <a href="/about.html" class="nav-link">About</a>`;

    inner.querySelectorAll(':scope > .btn, :scope > .nav-actions').forEach(element => element.remove());
    const actions = document.createElement('div');
    actions.className = 'nav-actions';
    actions.innerHTML = `
      <a href="/free-audit" class="btn btn-audit">
        <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        Free Audit
      </a>
      <a href="/#contact" class="btn btn-primary">
        Start a project
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
      </a>`;

    let menuButton = inner.querySelector('#menuBtn');
    if (!menuButton) {
      menuButton = document.createElement('button');
      menuButton.id = 'menuBtn';
      menuButton.className = 'menu-btn';
      menuButton.type = 'button';
      menuButton.setAttribute('aria-label', 'Open menu');
      menuButton.setAttribute('aria-expanded', 'false');
      menuButton.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="3" x2="21" y1="6" y2="6"/><line x1="3" x2="21" y1="12" y2="12"/><line x1="3" x2="21" y1="18" y2="18"/></svg>';
    }
    inner.append(actions, menuButton);

    const path = window.location.pathname.replace(/\/index\.html$/, '/').replace(/\/$/, '') || '/';
    links.querySelectorAll('a.nav-link').forEach(link => {
      const href = link.getAttribute('href');
      const current = href === '/about.html'
        ? path === '/about.html'
        : path === href || path.startsWith(href + '/');
      if (current) link.setAttribute('aria-current', 'page');
    });
    if (path === '/free-audit') actions.querySelector('.btn-audit').setAttribute('aria-current', 'page');

    // Static pages carried several generations of the mobile overlay.
    // Rebuild it below from the canonical template instead of preserving drift.
    document.getElementById('mobilePanel')?.remove();
  }

  normalizeGlobalHeader();

  // Keep headings intact. Whole-block reveals avoid the layout flicker and
  // uneven line breaks caused by wrapping every word after first paint.
  document.querySelectorAll('[data-split="words"]').forEach(el => {
    el.classList.add('split-static');
  });

  const hydrateLazyImage = (img) => {
    if (!img || !img.dataset.src) return;
    img.src = img.dataset.src;
    img.removeAttribute('data-src');
  };

  const lazyImages = document.querySelectorAll('img[data-src]');
  if (lazyImages.length) {
    if ('IntersectionObserver' in window) {
      const lazyImageObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          hydrateLazyImage(entry.target);
          lazyImageObserver.unobserve(entry.target);
        });
      }, { rootMargin: '180px 0px' });
      lazyImages.forEach(img => lazyImageObserver.observe(img));
    } else {
      lazyImages.forEach(hydrateLazyImage);
    }
  }

  // ── Floating nav: toggle "scrolled" state for opacity/shadow shift ──
  const navBar = document.querySelector('.nav-bar');
  if (navBar) {
    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        navBar.classList.toggle('scrolled', window.scrollY > 18);
        ticking = false;
      });
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  const contactSection = document.getElementById('contact')
    || document.querySelector('.landing-page-paid #book');
  if (contactSection) {
    const setContactVisibility = () => {
      const rect = contactSection.getBoundingClientRect();
      const viewport = window.innerHeight || document.documentElement.clientHeight;
      const visible = rect.top < viewport * 0.82 && rect.bottom > viewport * 0.18;
      document.body.classList.toggle('is-contact-visible', visible);
    };

    if ('IntersectionObserver' in window) {
      const contactObserver = new IntersectionObserver(() => setContactVisibility(), {
        threshold: [0, 0.18, 0.5],
        rootMargin: '-80px 0px -18% 0px',
      });
      contactObserver.observe(contactSection);
    }

    window.addEventListener('scroll', setContactVisibility, { passive: true });
    window.addEventListener('resize', setContactVisibility);
    setContactVisibility();
  }

  // ── Mobile nav overlay ──
  function ensureMobilePanel() {
    if (!document.getElementById('menuBtn') || document.getElementById('mobilePanel')) return;
    const panel = document.createElement('div');
    panel.id = 'mobilePanel';
    panel.className = 'mnav';
    panel.setAttribute('aria-hidden', 'true');
    panel.setAttribute('inert', '');
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-modal', 'true');
    panel.setAttribute('aria-label', 'Navigation');
    panel.innerHTML = `
      <div class="mnav-inner">
        <div class="mnav-top">
          <a href="/" class="mnav-logo">Lofts<span>studio</span></a>
          <button class="mnav-close" id="menuClose" type="button" aria-label="Close menu">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </div>
        <nav class="mnav-primary" aria-label="Main">
          <a href="/websites" class="mnav-link" data-num="01">Web Design</a>
          <a href="/portfolio" class="mnav-link" data-num="02">Portfolio</a>
          <a href="/about.html" class="mnav-link" data-num="03">About</a>
          <a href="/process" class="mnav-link" data-num="04">Process</a>
          <a href="/services" class="mnav-link" data-num="05">Services</a>
          <a href="/blog" class="mnav-link" data-num="06">Blog</a>
          <a href="/tools" class="mnav-link" data-num="07">Tools</a>
        </nav>
        <div class="mnav-services">
          <p class="mnav-label">Services</p>
          <div class="mnav-grid">
            <a href="/services/shopify-development.html">Shopify</a>
            <a href="/services/woocommerce-development.html">WooCommerce</a>
            <a href="/services/webflow-development.html">Webflow</a>
            <a href="/services/wordpress-development.html">WordPress</a>
            <a href="/services/saas-website-design.html">SaaS</a>
            <a href="/services/speed-optimization.html">Speed Opt.</a>
            <a href="/services/custom-app-development.html">Custom Apps</a>
            <a href="/services/ai-calling-agents.html">AI Calling</a>
          </div>
        </div>
        <a href="/free-audit" class="mnav-audit-link">Free 15-min Audit</a>
        <div class="mnav-foot">
          <a href="/#contact" class="mnav-cta">Start a project <span aria-hidden="true">→</span></a>
          <p class="mnav-meta">Multan &nbsp;·&nbsp; Dubai &nbsp;·&nbsp; US &amp; UK hours</p>
        </div>
      </div>`;
    document.body.appendChild(panel);
  }

  ensureMobilePanel();
  const menuBtn   = document.getElementById('menuBtn');
  const menuClose = document.getElementById('menuClose');
  const mnav      = document.getElementById('mobilePanel');

  if (menuBtn && mnav) {
    let open = false;

    const openMenu = () => {
      open = true;
      mnav.classList.add('open');
      mnav.removeAttribute('aria-hidden');
      mnav.removeAttribute('inert');
      menuBtn.setAttribute('aria-expanded', 'true');
      menuBtn.setAttribute('aria-label', 'Close menu');
      document.documentElement.classList.add('menu-lock');
      document.body.classList.add('menu-lock');
      mnav.scrollTop = 0;
      setTimeout(() => menuClose?.focus({ preventScroll: true }), 80);
    };

    const closeMenu = () => {
      const shouldRestoreFocus = mnav.contains(document.activeElement);
      open = false;
      mnav.classList.remove('open');
      mnav.setAttribute('aria-hidden', 'true');
      mnav.setAttribute('inert', '');
      menuBtn.setAttribute('aria-expanded', 'false');
      menuBtn.setAttribute('aria-label', 'Open menu');
      document.documentElement.classList.remove('menu-lock');
      document.body.classList.remove('menu-lock');
      if (shouldRestoreFocus) menuBtn.focus({ preventScroll: true });
    };

    // Open: hamburger button
    menuBtn.addEventListener('click', () => open ? closeMenu() : openMenu());

    // Close: X button inside the overlay
    if (menuClose) menuClose.addEventListener('click', closeMenu);

    // Close on nav link tap
    mnav.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => setTimeout(closeMenu, 60));
    });

    // Keyboard
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && open) {
        e.preventDefault();
        closeMenu();
        return;
      }
      if (e.key !== 'Tab' || !open) return;
      const focusable = [...mnav.querySelectorAll('a[href], button:not([disabled])')];
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });

    // Resize: close if going back to desktop
    window.addEventListener('resize', () => { if (window.innerWidth > 880 && open) closeMenu(); });
  }

  // ── Mega menu (click + hover, keyboard accessible) ──
  document.querySelectorAll('.mega-wrap').forEach(wrap => {
    const trigger = wrap.querySelector('[data-mega-trigger]');
    const mega = wrap.querySelector('.mega');
    if (!trigger || !mega) return;

    const open = () => { mega.classList.add('open'); trigger.setAttribute('aria-expanded', 'true'); };
    const close = () => { mega.classList.remove('open'); trigger.setAttribute('aria-expanded', 'false'); };

    trigger.addEventListener('click', e => {
      e.preventDefault();
      mega.classList.contains('open') ? close() : open();
    });
    trigger.addEventListener('keydown', e => {
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowDown') { e.preventDefault(); open(); mega.querySelector('a')?.focus(); }
    });
    document.addEventListener('click', e => {
      if (!wrap.contains(e.target)) close();
    });
  });

  // ── Smooth anchor scroll with nav offset ──
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href');
      if (id.length > 1) {
        const el = document.querySelector(id);
        if (el) {
          e.preventDefault();
          const y = el.getBoundingClientRect().top + window.scrollY - 84;
          window.scrollTo({ top: y, behavior: 'smooth' });
        }
      }
    });
  });

  // ── Lead forms — AJAX contact endpoint ──
  document.querySelectorAll('form[data-lead]').forEach(form => {
    const formStartedAt = Date.now();
    const submissionId = window.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    const honeypot = document.createElement('input');
    honeypot.type = 'text';
    honeypot.name = '_gotcha';
    honeypot.tabIndex = -1;
    honeypot.autocomplete = 'off';
    honeypot.setAttribute('aria-hidden', 'true');
    honeypot.style.cssText = 'position:absolute!important;left:-10000px!important;width:1px!important;height:1px!important;opacity:0!important;pointer-events:none!important;';
    form.appendChild(honeypot);
    let leadFormStarted = false;
    form.addEventListener('focusin', () => {
      if (leadFormStarted) return;
      leadFormStarted = true;
      trackMarketingEvent('form_start', {
        event_category: 'lead',
        event_label: form.getAttribute('data-lead-source') || form.querySelector('[name="source"]')?.value || 'contact-form',
        form_location: window.location.pathname
      });
    });

    form.addEventListener('submit', async e => {
      e.preventDefault();
      const wrap = form.closest('[data-lead-wrap]') || form.parentElement;
      const success = wrap?.querySelector('[data-lead-success]');
      const btn = form.querySelector('button[type="submit"]');
      const originalHTML = btn ? btn.innerHTML : '';
      if (btn) { btn.disabled = true; btn.innerHTML = 'Sending…'; }

      try {
        const formData = new FormData(form);
        formData.set('_startedAt', String(formStartedAt));
        formData.set('_submissionId', submissionId);
        if (!formData.has('page_url')) formData.append('page_url', window.location.href);
        if (!formData.has('page_title')) formData.append('page_title', document.title);
        if (!formData.has('source_path')) formData.append('source_path', window.location.pathname);
        const attribution = appendAdAttribution(formData);
        const leadSource = formData.get('source') || form.getAttribute('data-lead-source') || 'contact-form';

        trackMarketingEvent('form_submit_attempt', {
          event_category: 'lead',
          event_label: leadSource,
          form_location: window.location.pathname,
          ...attribution
        });

        const res = await fetch(form.action, {
          method: 'POST',
          headers: { 'Accept': 'application/json' },
          body: formData,
        });
        const data = await res.json().catch(() => ({}));
        const ok = res.ok && (data.success === 'true' || data.success === true);
        if (!ok) throw new Error(data.message || 'Submission failed');

        form.style.display = 'none';
        if (success) success.style.display = 'block';
        trackMarketingEvent('form_submit', {
          event_category: 'lead',
          event_label: leadSource,
          form_location: window.location.pathname,
          ...attribution
        });
        if (leadSource !== 'footer-newsletter') {
          trackMarketingEvent('generate_lead', {
            event_category: 'lead',
            event_label: leadSource,
            form_location: window.location.pathname,
            ...attribution
          });
        }
        // Reset button state in case the form is reopened later
        if (btn) { btn.disabled = false; btn.innerHTML = originalHTML; }
      } catch (err) {
        if (btn) { btn.disabled = false; btn.innerHTML = originalHTML; }
        trackMarketingEvent('form_submit_error', {
          event_category: 'lead',
          event_label: form.getAttribute('data-lead-source') || form.querySelector('[name="source"]')?.value || 'contact-form',
          form_location: window.location.pathname,
          error_message: err && err.message ? String(err.message).slice(0, 120) : 'Submission failed'
        });
        // Inline error message — no native alert popup
        let inlineErr = form.querySelector('[data-lead-error]');
        if (!inlineErr) {
          inlineErr = document.createElement('p');
          inlineErr.setAttribute('data-lead-error', '');
          inlineErr.setAttribute('role', 'alert');
          inlineErr.setAttribute('aria-live', 'polite');
          inlineErr.style.cssText = 'margin-top:0.75rem;font-size:0.85rem;color:#B91C1C;text-align:center;';
          form.appendChild(inlineErr);
        }
        inlineErr.textContent = "Couldn't send right now — please email hi@lofts.studio or try again in a minute.";
      }
    });
  });

  // ── Lead-intent clicks — helps separate traffic quality from form friction ──
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link) return;
    const href = link.getAttribute('href') || '';
    let eventName = '';
    if (href.startsWith('mailto:')) eventName = 'email_click';
    if (href.startsWith('tel:')) eventName = 'phone_click';
    if (href.includes('wa.me/') || href.toLowerCase().includes('whatsapp')) eventName = 'whatsapp_click';
    if (href === '/#contact' || href === '#contact') eventName = 'contact_cta_click';
    if (href.includes('/free-audit')) eventName = 'audit_cta_click';
    if (href.includes('/book')) eventName = 'booking_cta_click';
    if (!eventName) return;
    trackMarketingEvent(eventName, {
      event_category: 'lead',
      event_label: href.replace(/^mailto:/, '').split('?')[0],
      link_location: window.location.pathname
    });
  });

  // ── Native reveal system ──
  // Keep first paint and scrolling independent from animation libraries.
  // The observer is small, deterministic, and respects the existing CSS motion.
  setTimeout(() => {
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(entries => {
        entries.forEach(en => {
          if (en.isIntersecting) {
            en.target.classList.add('in');
            io.unobserve(en.target);
          }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
      document.querySelectorAll('[data-reveal]').forEach(el => io.observe(el));
    } else {
      document.querySelectorAll('[data-reveal]').forEach(el => el.classList.add('in'));
    }
  }, 40);

  // ── Year stamp in footer ──
  document.querySelectorAll('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });

})();

/* ═══════════════════════════════════════════════════════════════
   3D HERO CARD STACK
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  const scene = document.getElementById('stackScene');
  if (!scene) return;

  const cards = Array.from(scene.querySelectorAll('[data-stack-card]'));
  if (!cards.length) return;

  // ── State ──────────────────────────────────────────────────────
  let frontIdx   = 0;
  let tiltX      = 2;   // restrained editorial tilt
  let tiltY      = -4;
  let isHovering = false;
  let cycleTimer = null;
  let cycleStarted = false;

  // ── Positions for each depth slot ─────────────────────────────
  const SLOTS = [
    { tz:    0, tx:  0,  ty:  0,  op: 1.0  },
    { tz:  -18, tx:  8,  ty:  7,  op: 0.82 },
    { tz:  -36, tx: 15,  ty: 13,  op: 0.55 },
    { tz:  -54, tx: 21,  ty: 18,  op: 0.30 },
    { tz:  -72, tx: 27,  ty: 23,  op: 0.12 },
    { tz:  -88, tx: 32,  ty: 27,  op: 0.04 },
    { tz: -100, tx: 36,  ty: 31,  op: 0    },
    { tz: -100, tx: 36,  ty: 31,  op: 0    },
    { tz: -100, tx: 36,  ty: 31,  op: 0    },
    { tz: -100, tx: 36,  ty: 31,  op: 0    },
  ];

  const isMobile = () => window.innerWidth <= 768;

  function loadCardImage(card) {
    const img = card.querySelector('.stack-card-img[data-bg]');
    if (!img) return;
    img.style.backgroundImage = img.dataset.bg;
    img.removeAttribute('data-bg');
  }

  function updateSceneLabel() {
    const currentName = cards[frontIdx].querySelector('.scf-name');
    scene.setAttribute('aria-label', `Browse selected client work. Current project: ${currentName ? currentName.textContent.trim() : 'selected work'}`);
  }

  // ── Mobile: pure crossfade, no transforms ─────────────────────
  function applyFade() {
    cards.forEach((card, i) => {
      const isFront = i === frontIdx;
      if (isFront) loadCardImage(card);
      card.classList.toggle('is-front', isFront);
      card.style.transform = 'none';
      card.style.opacity   = isFront ? '1' : '0';
      card.style.zIndex    = isFront ? '2' : '1';
      card.setAttribute('aria-hidden', isFront ? 'false' : 'true');
    });
    updateSceneLabel();
  }

  // ── Desktop: full 3D stack ─────────────────────────────────────
  function applySlots(rx, ry) {
    if (isMobile()) { applyFade(); return; }
    cards.forEach((card, i) => {
      const slotIdx = (i - frontIdx + cards.length) % cards.length;
      const s = SLOTS[slotIdx] || SLOTS[SLOTS.length - 1];
      if (slotIdx === 0) loadCardImage(card);
      card.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg) translateZ(${s.tz}px) translateX(${s.tx}px) translateY(${s.ty}px)`;
      card.style.opacity   = s.op;
      card.style.zIndex    = cards.length - slotIdx;
      card.classList.toggle('is-front', slotIdx === 0);
      card.setAttribute('aria-hidden', slotIdx === 0 ? 'false' : 'true');
    });
    updateSceneLabel();
  }

  // ── Mouse tilt (desktop only) ──────────────────────────────────
  scene.addEventListener('mousemove', (e) => {
    if (isMobile()) return;
    startCycle();
    isHovering = true;
    const r  = scene.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width  - 0.5;
    const py = (e.clientY - r.top)  / r.height - 0.5;
    tiltX =  py * -8 + 1;
    tiltY =  px *  10 - 2;
    applySlots(tiltX, tiltY);
  });

  scene.addEventListener('mouseleave', () => {
    if (isMobile()) return;
    isHovering = false;
    const lerp = (a, b, t) => a + (b - a) * t;
    let frame;
    const ease = () => {
      tiltX = lerp(tiltX, 2,  0.08);
      tiltY = lerp(tiltY, -4, 0.08);
      applySlots(tiltX, tiltY);
      if (Math.abs(tiltX - 2) > 0.05 || Math.abs(tiltY + 4) > 0.05) {
        frame = requestAnimationFrame(ease);
      }
    };
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(ease);
  });

  // ── Tap → next card ───────────────────────────────────────────
  function advanceCard(direction) {
    startCycle();
    frontIdx = (frontIdx + direction + cards.length) % cards.length;
    applySlots(tiltX, tiltY);
    resetCycle();
  }

  scene.addEventListener('click', () => {
    advanceCard(1);
  });

  scene.addEventListener('keydown', (event) => {
    if (!['Enter', ' ', 'ArrowRight', 'ArrowLeft'].includes(event.key)) return;
    event.preventDefault();
    advanceCard(event.key === 'ArrowLeft' ? -1 : 1);
  });

  // ── Auto-cycle ────────────────────────────────────────────────
  function startCycle() {
    if (cycleStarted || isMobile() || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    cycleStarted = true;
    cards.forEach((card, i) => {
      const slotIdx = (i - frontIdx + cards.length) % cards.length;
      if (slotIdx <= 2) loadCardImage(card);
    });
    resetCycle();
  }

  function resetCycle() {
    if (!cycleStarted) return;
    clearInterval(cycleTimer);
    cycleTimer = setInterval(() => {
      if (!isHovering) {
        frontIdx = (frontIdx + 1) % cards.length;
        applySlots(tiltX, tiltY);
      }
    }, 3000);
  }

  // ── Init ──────────────────────────────────────────────────────
  applySlots(tiltX, tiltY);

  // Re-evaluate on resize (e.g. rotation)
  window.addEventListener('resize', () => applySlots(tiltX, tiltY));
  scene.addEventListener('pointerenter', startCycle, { once: true, passive: true });
  scene.addEventListener('focusin', startCycle, { once: true });

})();

/* ── Homepage hero anti-gravity motion ─────────────────────────── */
(function () {
  'use strict';

  const scene = document.querySelector('[data-hero-gravity]');
  const reel = scene && scene.querySelector('.hero-sidecar');
  const canRespond = window.matchMedia('(hover: hover) and (pointer: fine)').matches &&
    !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!scene || !reel || !canRespond) return;

  const current = { x: 0, y: 0, r: 0 };
  const target = { x: 0, y: 0, r: 0 };
  let frame = 0;

  function render() {
    current.x += (target.x - current.x) * .095;
    current.y += (target.y - current.y) * .095;
    current.r += (target.r - current.r) * .095;

    scene.style.setProperty('--hero-float-x', current.x.toFixed(2) + 'px');
    scene.style.setProperty('--hero-float-y', current.y.toFixed(2) + 'px');
    scene.style.setProperty('--hero-float-r', current.r.toFixed(3) + 'deg');

    const moving = Math.abs(target.x - current.x) > .03 ||
      Math.abs(target.y - current.y) > .03 ||
      Math.abs(target.r - current.r) > .003;
    frame = moving ? window.requestAnimationFrame(render) : 0;
  }

  function requestRender() {
    if (!frame) frame = window.requestAnimationFrame(render);
  }

  scene.addEventListener('pointermove', function (event) {
    const rect = scene.getBoundingClientRect();
    const x = Math.max(-1, Math.min(1, ((event.clientX - rect.left) / rect.width - .5) * 2));
    const y = Math.max(-1, Math.min(1, ((event.clientY - rect.top) / rect.height - .5) * 2));
    target.x = x * 11;
    target.y = y * 7;
    target.r = x * .42;
    requestRender();
  }, { passive: true });

  scene.addEventListener('pointerleave', function () {
    target.x = 0;
    target.y = 0;
    target.r = 0;
    requestRender();
  }, { passive: true });
})();


/* ── Homepage portfolio preview focus ───────────────────────────── */
(function () {
  'use strict';

  const stage = document.querySelector('.home-portfolio-stage');
  if (!stage) return;

  const canPreview = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!canPreview || reduceMotion) return;

  stage.querySelectorAll('.pf-card-img').forEach(frame => {
    let raf = 0;
    let lastEvent = null;

    const applyPreview = () => {
      raf = 0;
      if (!lastEvent) return;
      const rect = frame.getBoundingClientRect();
      const px = (lastEvent.clientX - rect.left) / rect.width - 0.5;
      const py = (lastEvent.clientY - rect.top) / rect.height - 0.5;
      frame.style.setProperty('--glow-x', `${((px + 0.5) * 100).toFixed(1)}%`);
      frame.style.setProperty('--glow-y', `${((py + 0.5) * 100).toFixed(1)}%`);
      frame.classList.add('is-previewing');
    };

    frame.addEventListener('pointermove', event => {
      lastEvent = event;
      if (!raf) raf = requestAnimationFrame(applyPreview);
    });

    frame.addEventListener('pointerleave', () => {
      lastEvent = null;
      if (raf) cancelAnimationFrame(raf);
      raf = 0;
      frame.style.setProperty('--glow-x', '50%');
      frame.style.setProperty('--glow-y', '42%');
      frame.classList.remove('is-previewing');
    });
  });
})();


/* ── Homepage spatial portfolio rail ───────────────────────────── */
(function () {
  'use strict';

  const rail = document.querySelector('[data-portfolio-rail]');
  if (!rail) return;

  const stage = rail.closest('.home-portfolio-stage');
  const cards = Array.from(rail.querySelectorAll('.pf-card, .pf-card--featured')).slice(0, 23);
  const previous = stage.querySelector('[data-portfolio-previous]');
  const next = stage.querySelector('[data-portfolio-next]');
  const currentLabel = stage.querySelector('[data-portfolio-current]');
  const titleLabel = stage.querySelector('[data-portfolio-title]');
  const totalLabel = stage.querySelector('[data-portfolio-total]');
  const playToggle = stage.querySelector('[data-portfolio-play]');
  const playIcon = stage.querySelector('[data-portfolio-play-icon]');
  const pauseIcon = stage.querySelector('[data-portfolio-pause-icon]');
  const announcer = stage.querySelector('[data-portfolio-announcer]');
  const desktop = window.matchMedia('(min-width: 821px)');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const autoplayDelay = 1450;
  const resumeDelay = 1000;
  const wheelThreshold = 10;
  const wheelCooldown = 140;
  let active = 0;
  let dragStart = null;
  let dragMoved = false;
  let suppressClick = false;
  let scrollFrame = 0;
  let autoplayTimer = 0;
  let resumeTimer = 0;
  let wheelAccumulator = 0;
  let wheelResetTimer = 0;
  let wheelLocked = false;
  let dragFrame = 0;
  let dragOffset = 0;
  let userPaused = false;
  let pointerInside = false;
  let focusInside = false;
  let stageVisible = false;

  if (!cards.length) return;
  if (totalLabel) totalLabel.textContent = String(cards.length).padStart(2, '0');

  function projectName(card) {
    const heading = card.querySelector('.pf-card-name');
    return heading ? heading.textContent.trim() : 'Selected project';
  }

  function wrappedOffset(index) {
    let offset = index - active;
    const half = Math.floor(cards.length / 2);
    if (offset > half) offset -= cards.length;
    if (offset < -half) offset += cards.length;
    return offset;
  }

  function render(announce) {
    cards.forEach(function (card, index) {
      const offset = wrappedOffset(index);
      const distance = Math.abs(offset);
      card.style.setProperty('--rail-x', (offset * 76) + '%');
      card.style.setProperty('--rail-y', (distance * 12 - (distance === 0 ? 8 : 0)) + 'px');
      card.style.setProperty('--rail-z', (-distance * 118) + 'px');
      card.style.setProperty('--rail-rotate', (-offset * 7) + 'deg');
      card.style.setProperty('--rail-tilt', (offset * 1.15) + 'deg');
      card.style.setProperty('--rail-scale', distance === 0 ? '1.055' : String(1 - distance * .04));
      card.style.setProperty('--rail-opacity', String(1 - distance * .14));
      card.style.setProperty('--rail-order', String(cards.length - distance));
      card.classList.toggle('is-rail-active', index === active);
    });

    const selected = cards[active];
    if (currentLabel) currentLabel.textContent = String(active + 1).padStart(2, '0');
    if (titleLabel) titleLabel.textContent = projectName(selected);
    if (announce) {
      const message = 'Current project: ' + projectName(selected) + ', ' + (active + 1) + ' of ' + cards.length;
      rail.setAttribute('aria-label', 'Selected client work. ' + message);
      if (announcer) announcer.textContent = message;
    }
  }

  function select(index, announce) {
    active = (index + cards.length) % cards.length;
    render(announce);
    if (!desktop.matches) {
      const card = cards[active];
      const target = card.offsetLeft - (rail.clientWidth - card.offsetWidth) / 2;
      rail.scrollTo({ left: target, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
    }
  }

  function canAutoplay() {
    return !userPaused && !reducedMotion.matches && stageVisible && !pointerInside && !focusInside && !document.hidden;
  }

  function stopAutoplay() {
    window.clearTimeout(autoplayTimer);
    autoplayTimer = 0;
  }

  function queueAutoplay(delay) {
    stopAutoplay();
    if (!canAutoplay()) return;
    autoplayTimer = window.setTimeout(function () {
      select(active + 1, false);
      queueAutoplay(autoplayDelay);
    }, typeof delay === 'number' ? delay : autoplayDelay);
  }

  function updatePlayToggle() {
    if (!playToggle) return;
    const paused = userPaused || reducedMotion.matches;
    playToggle.setAttribute('aria-pressed', String(paused));
    playToggle.setAttribute('aria-label', paused ? 'Resume automatic rotation' : 'Pause automatic rotation');
    playToggle.title = paused ? 'Resume automatic rotation' : 'Pause automatic rotation';
    playToggle.disabled = reducedMotion.matches;
    if (playIcon) playIcon.hidden = !paused;
    if (pauseIcon) pauseIcon.hidden = paused;
  }

  function resumeAfterInteraction() {
    stopAutoplay();
    window.clearTimeout(resumeTimer);
    if (userPaused || reducedMotion.matches) return;
    resumeTimer = window.setTimeout(function () { queueAutoplay(350); }, resumeDelay);
  }

  function selectManually(index) {
    select(index, true);
    resumeAfterInteraction();
  }

  function paintDragOffset() {
    dragFrame = 0;
    rail.style.setProperty('--portfolio-drag-x', dragOffset + 'px');
  }

  cards.forEach(function (card, index) {
    card.addEventListener('focusin', function () { selectManually(index); });
  });

  if (previous) previous.addEventListener('click', function () { selectManually(active - 1); });
  if (next) next.addEventListener('click', function () { selectManually(active + 1); });
  if (playToggle) playToggle.addEventListener('click', function () {
    userPaused = !userPaused;
    window.clearTimeout(resumeTimer);
    updatePlayToggle();
    if (userPaused) stopAutoplay();
    else queueAutoplay(600);
  });

  rail.addEventListener('keydown', function (event) {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    selectManually(active + (event.key === 'ArrowRight' ? 1 : -1));
  });

  rail.addEventListener('pointerdown', function (event) {
    if (!desktop.matches || event.button !== 0) return;
    dragStart = { x: event.clientX, y: event.clientY, id: event.pointerId, active: active };
    dragMoved = false;
    rail.classList.add('is-dragging');
    rail.setPointerCapture(event.pointerId);
    stopAutoplay();
  });

  rail.addEventListener('pointermove', function (event) {
    if (!dragStart || dragStart.id !== event.pointerId) return;
    const dx = event.clientX - dragStart.x;
    const dy = event.clientY - dragStart.y;
    if (Math.abs(dx) > 8 && Math.abs(dx) > Math.abs(dy)) dragMoved = true;
    dragOffset = Math.max(-120, Math.min(120, dx * .52));
    if (!dragFrame) dragFrame = requestAnimationFrame(paintDragOffset);
  }, { passive: true });

  rail.addEventListener('pointerup', function (event) {
    if (!dragStart || dragStart.id !== event.pointerId) return;
    const dx = event.clientX - dragStart.x;
    const dy = event.clientY - dragStart.y;
    const startActive = dragStart.active;
    dragStart = null;
    if (dragFrame) cancelAnimationFrame(dragFrame);
    dragFrame = 0;
    dragOffset = 0;
    rail.classList.remove('is-dragging');
    rail.style.removeProperty('--portfolio-drag-x');
    if (rail.hasPointerCapture(event.pointerId)) rail.releasePointerCapture(event.pointerId);
    if (dragMoved) {
      suppressClick = true;
      window.setTimeout(function () { suppressClick = false; }, 0);
    }
    if (Math.abs(dx) > 36 && Math.abs(dx) > Math.abs(dy)) selectManually(startActive + (dx < 0 ? 1 : -1));
    else resumeAfterInteraction();
  });

  rail.addEventListener('pointercancel', function () {
    dragStart = null;
    if (dragFrame) cancelAnimationFrame(dragFrame);
    dragFrame = 0;
    dragOffset = 0;
    rail.classList.remove('is-dragging');
    rail.style.removeProperty('--portfolio-drag-x');
    resumeAfterInteraction();
  }, { passive: true });

  rail.addEventListener('click', function (event) {
    if (!suppressClick) return;
    event.preventDefault();
    event.stopPropagation();
  }, true);

  rail.addEventListener('dragstart', function (event) { event.preventDefault(); });

  rail.addEventListener('wheel', function (event) {
    if (!desktop.matches) return;
    const horizontal = event.shiftKey && Math.abs(event.deltaX) < 1 ? event.deltaY : event.deltaX;
    const isHorizontalIntent = event.shiftKey || (Math.abs(horizontal) >= 6 && Math.abs(horizontal) > Math.abs(event.deltaY));
    if (!isHorizontalIntent || wheelLocked) return;
    event.preventDefault();
    wheelAccumulator += horizontal;
    window.clearTimeout(wheelResetTimer);
    wheelResetTimer = window.setTimeout(function () { wheelAccumulator = 0; }, wheelCooldown);
    if (Math.abs(wheelAccumulator) < wheelThreshold) return;
    selectManually(active + (wheelAccumulator > 0 ? 1 : -1));
    wheelAccumulator = 0;
    wheelLocked = true;
    window.setTimeout(function () { wheelLocked = false; }, wheelCooldown);
  }, { passive: false });

  rail.addEventListener('pointerenter', function () {
    pointerInside = true;
    stopAutoplay();
  });

  rail.addEventListener('pointerleave', function () {
    pointerInside = false;
    if (!dragStart) resumeAfterInteraction();
  });

  rail.addEventListener('focusin', function () {
    focusInside = true;
    stopAutoplay();
  });

  rail.addEventListener('focusout', function () {
    window.setTimeout(function () {
      focusInside = rail.contains(document.activeElement);
      if (!focusInside) resumeAfterInteraction();
    }, 0);
  });

  rail.addEventListener('scroll', function () {
    if (desktop.matches || scrollFrame) return;
    scrollFrame = requestAnimationFrame(function () {
      scrollFrame = 0;
      const centre = rail.scrollLeft + rail.clientWidth / 2;
      let nearest = active;
      let nearestDistance = Infinity;
      cards.forEach(function (card, index) {
        const distance = Math.abs(card.offsetLeft + card.offsetWidth / 2 - centre);
        if (distance < nearestDistance) {
          nearest = index;
          nearestDistance = distance;
        }
      });
      if (nearest !== active) {
        active = nearest;
        render(false);
      }
    });
  }, { passive: true });

  const visibilityObserver = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
    stageVisible = entries[0].isIntersecting && entries[0].intersectionRatio >= .28;
    if (stageVisible) queueAutoplay(autoplayDelay);
    else stopAutoplay();
  }, { threshold: [0, .28, .6] }) : null;

  if (visibilityObserver) visibilityObserver.observe(stage);
  else stageVisible = true;

  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stopAutoplay();
    else queueAutoplay(autoplayDelay);
  });

  reducedMotion.addEventListener('change', function () {
    updatePlayToggle();
    if (reducedMotion.matches) stopAutoplay();
    else queueAutoplay(autoplayDelay);
  });

  desktop.addEventListener('change', function () {
    rail.style.removeProperty('--portfolio-drag-x');
    render(false);
  });
  updatePlayToggle();
  render(false);
})();


/* ── Theme toggle (light / dark) ────────────────────────────────── */
(function () {
  var KEY = 'lofts-theme';
  function apply(m){ document.documentElement.setAttribute('data-theme', m === 'dark' ? 'dark' : 'light'); }
  function get(){ try { var v = localStorage.getItem(KEY); return (v === 'dark') ? 'dark' : 'light'; } catch(e){ return 'light'; } }
  apply(get());
  var ICON = {
    light:'<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    dark:'<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>'
  };
  function build(){
    var nav = document.querySelector('.nav-inner');
    if (!nav || nav.querySelector('.theme-toggle')) return;
    var cur = get();
    var wrap = document.createElement('div');
    wrap.className = 'theme-toggle'; wrap.setAttribute('role','group'); wrap.setAttribute('aria-label','Theme');
    ['light','dark'].forEach(function(m){
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'theme-opt' + (m === cur ? ' is-active' : '');
      b.dataset.mode = m; var label = m.charAt(0).toUpperCase()+m.slice(1);
      b.title = label; b.setAttribute('aria-label', label + ' theme');
      b.setAttribute('aria-pressed', m === cur ? 'true' : 'false');
      b.innerHTML = ICON[m];
      b.addEventListener('click', function(){
        try { localStorage.setItem(KEY, m); } catch(e){}
        apply(m);
        wrap.querySelectorAll('.theme-opt').forEach(function(o){
          var active = o.dataset.mode === m;
          o.classList.toggle('is-active', active);
          o.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
      });
      wrap.appendChild(b);
    });
    var mb = nav.querySelector('.menu-btn');
    if (mb) nav.insertBefore(wrap, mb); else nav.appendChild(wrap);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build); else build();
})();

/* ── Scroll progress bar ──
   Injects a thin glowing bar along the bottom of the menu bar that
   fills as the page scrolls from top to bottom. Works on every page. */
(function () {
  function init() {
    var bar = document.querySelector('.nav-bar');
    if (!bar || bar.querySelector('.scroll-progress')) return;
    var track = document.createElement('div');
    track.className = 'scroll-progress';
    var fill = document.createElement('div');
    fill.className = 'scroll-progress__fill';
    track.appendChild(fill);
    bar.appendChild(track);

    var ticking = false;
    function update() {
      var doc = document.documentElement;
      var max = (doc.scrollHeight - window.innerHeight);
      var pct = max > 0 ? (window.scrollY || doc.scrollTop || 0) / max : 0;
      if (pct < 0) pct = 0; else if (pct > 1) pct = 1;
      fill.style.width = (pct * 100) + '%';
      ticking = false;
    }
    function onScroll() {
      if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    update();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

/* ── Lofts 2026 experience layer ──────────────────────────────── */
(function () {
  'use strict';

  document.documentElement.classList.add('lofts-experience');

  var route = window.location.pathname.split('/').filter(Boolean)[0] || 'home';
  document.body.classList.add('route-' + route.replace(/[^a-z0-9-]/gi, '-').toLowerCase());

  function installVisualHeroes() {
    var pathname = window.location.pathname.replace(/\/index\.html$/, '/').replace(/\/+$/, '') || '/';
    var segments = pathname.split('/').filter(Boolean);
    var primaryRoute = segments[0] || '';

    // The portfolio archive owns a purpose-built editorial hero. Running the
    // generic visual-hero transformer here nests two independent grid systems
    // and collapses the archive copy into a single column.
    if (primaryRoute === 'portfolio' && segments.length === 1) return;

    var isLandingPage = primaryRoute === 'services' || primaryRoute === 'locations' ||
      primaryRoute === 'websites' || primaryRoute === 'work';

    if (!isLandingPage || document.querySelector('[data-lofts-hero-stage]')) return;

    var hero = null;
    var grid = null;
    var copy = null;
    var breadcrumb = null;
    var legacyProof = null;

    if (document.querySelector('main > .loc-hero, main > .region-hero')) {
      hero = document.querySelector('main > .loc-hero, main > .region-hero');
      grid = hero && hero.querySelector(':scope > .container');
      copy = grid && grid.querySelector('.loc-hero-copy');
    } else if (document.querySelector('main > .page-hero')) {
      hero = document.querySelector('main > .page-hero');
      grid = hero && hero.querySelector('.page-hero-grid');
      copy = grid && grid.querySelector('.page-hero-copy');
      legacyProof = grid && grid.querySelector('.page-hero-proof');
    } else {
      hero = document.querySelector('main > section.paper:first-of-type');
      grid = hero && hero.querySelector(':scope > .container');
      if (grid) {
        copy = Array.from(grid.children).find(function (child) {
          return child.matches('[data-reveal], .portfolio-hero-shell') && child.querySelector('h1');
        });
      }
    }

    if (!hero || !grid || !copy) return;

    breadcrumb = hero.querySelector('.page-breadcrumb, .loc-breadcrumb, nav[aria-label="Breadcrumb"]');

    var projects = {
      studio: [
        { name: 'Discova', meta: 'WordPress / Travel / B2B', image: '/assets/work/discova.webp', href: '/portfolio/discova.html' },
        { name: 'Salud Capital', meta: 'WordPress / Finance / Editorial', image: '/assets/work/saludcap.webp', href: '/portfolio/saludcap.html' },
        { name: 'American Gulf', meta: 'Insurance / B2B / WordPress', image: '/assets/work/americangulf.webp', href: '/portfolio/americangulf.html' },
        { name: 'Woven Media', meta: 'Publishing / Editorial / CMS', image: '/assets/work/wovenmedia.webp', href: '/portfolio/wovenmedia.html' }
      ],
      commerce: [
        { name: 'Joshifresco', meta: 'Commerce / Art / Editorial', image: '/assets/work/joshifresco.webp', href: '/portfolio/joshifresco.html' },
        { name: 'Jamaican Coffee Club', meta: 'DTC / Subscription / WooCommerce', image: '/assets/work/jamaicancoffeeclub.webp', href: '/portfolio/jamaicancoffeeclub.html' },
        { name: 'Mercanto', meta: 'B2B / Marketplace / Food', image: '/assets/work/mercanto.webp', href: '/portfolio/mercanto.html' },
        { name: 'Counter Culture', meta: 'Shopify / Fashion / DTC', image: '/assets/work/counter-culture.webp', href: '/portfolio/counter-culture.html' }
      ],
      product: [
        { name: 'Woven Media', meta: 'Product / Publishing / CMS', image: '/assets/work/wovenmedia.webp', href: '/portfolio/wovenmedia.html' },
        { name: 'iCloseLeads', meta: 'SaaS / AI / Lead operations', image: '/assets/work/icloseleads.jpg', href: '/portfolio/icloseleads.html' },
        { name: 'Acturion', meta: 'B2B / Insurance / Platform', image: '/assets/work/acturion.webp', href: '/portfolio/acturion.html' },
        { name: 'Cartelligent', meta: 'Automotive / Service / Platform', image: '/assets/work/cartelligent.webp', href: '/portfolio/cartelligent.html' }
      ],
      local: [
        { name: 'American Reinsurance', meta: 'Professional services / B2B', image: '/assets/work/americanreinsurance.webp', href: '/portfolio/americanreinsurance.html' },
        { name: 'Cartelligent', meta: 'Automotive / Service / Lead flow', image: '/assets/work/cartelligent.webp', href: '/portfolio/cartelligent.html' },
        { name: 'Discova', meta: 'Multi-market / WordPress / B2B', image: '/assets/work/discova.webp', href: '/portfolio/discova.html' },
        { name: 'Acturion', meta: 'Finance / B2B / WordPress', image: '/assets/work/acturion.webp', href: '/portfolio/acturion.html' }
      ],
      editorial: [
        { name: 'Website structure audit', meta: 'Audit / Structure / Conversion', image: '/assets/blog/website-structure-audit-report.png', href: '/blog/website-structure-audit-report.html' },
        { name: 'Answer engine checklist', meta: 'SEO / AEO / Entity signals', image: '/assets/blog/answer-engine-optimization-checklist.png', href: '/blog/answer-engine-optimization-checklist.html' },
        { name: 'Modify or rebuild?', meta: 'Shopify / Architecture / Risk', image: '/assets/blog/shopify-theme-customization-modify-or-rebuild.png', href: '/blog/shopify-theme-customization-modify-or-rebuild.html' },
        { name: 'AI-search landing audit', meta: 'AI search / Landing pages / Leads', image: '/assets/blog/ai-search-landing-page-audit.png', href: '/blog/ai-search-landing-page-audit.html' }
      ]
    };

    var routeKey = pathname.toLowerCase();
    var group = 'studio';
    if (primaryRoute === 'blog' || primaryRoute === 'notes' || primaryRoute === 'tools') {
      group = 'editorial';
    } else if (/shopify|woocommerce|ecommerce|store|retail|restaurant|cafe|bakery|florist|fashion|jewel|coffee/.test(routeKey)) {
      group = 'commerce';
    } else if (/saas|custom|software|webflow|ai-|automation|app-development|product/.test(routeKey)) {
      group = 'product';
    } else if (primaryRoute === 'locations' || primaryRoute === 'websites') {
      group = 'local';
    }

    var source = projects[group];
    var hash = Array.from(pathname).reduce(function (total, character) {
      return ((total * 31) + character.charCodeAt(0)) >>> 0;
    }, 7);
    var chosen = [0, 1, 2].map(function (step) {
      return source[(hash + step) % source.length];
    });

    var stageLabel = group === 'editorial' ? 'Selected field notes' : 'Selected shipped work';
    var archiveLabel = group === 'editorial' ? 'Read the journal' : 'Explore the archive';
    var archiveHref = group === 'editorial' ? '/blog' : '/portfolio';
    var proofValue = primaryRoute === 'portfolio' ? '15 years' : '3,400+';
    var proofLabel = primaryRoute === 'portfolio' ? 'of senior-led delivery' : 'projects handled across almost 15 years';

    var stage = document.createElement('aside');
    stage.className = 'lofts-hero-stage';
    stage.setAttribute('data-lofts-hero-stage', '');
    stage.setAttribute('aria-label', stageLabel);
    stage.innerHTML =
      '<div class="lofts-hero-stage__head">' +
        '<span><i aria-hidden="true"></i>' + stageLabel + '</span>' +
        '<a href="' + archiveHref + '">' + archiveLabel + '<b aria-hidden="true">&nearr;</b></a>' +
      '</div>' +
      '<div class="lofts-hero-stage__canvas">' +
        chosen.map(function (item, index) {
          return '<a class="lofts-hero-tile lofts-hero-tile--' + (index + 1) + '" href="' + item.href + '" aria-label="View ' + item.name + '">' +
            '<span class="lofts-hero-tile__chrome" aria-hidden="true"><i></i><i></i><i></i></span>' +
            '<img src="' + item.image + '" alt="' + item.name + ' project by Lofts Studio" width="1200" height="900" ' + (index === 0 ? 'loading="eager" fetchpriority="high"' : 'loading="lazy"') + ' decoding="async" />' +
            '<span class="lofts-hero-tile__caption"><strong>' + item.name + '</strong><small>' + item.meta + '</small></span>' +
          '</a>';
        }).join('') +
        '<div class="lofts-hero-stage__proof"><strong>' + proofValue + '</strong><span>' + proofLabel + '</span></div>' +
      '</div>';

    hero.classList.add('lofts-visual-hero');
    grid.classList.add('lofts-visual-hero__grid');
    copy.classList.add('lofts-visual-hero__copy');
    if (breadcrumb) {
      breadcrumb.classList.add('lofts-visual-hero__breadcrumb');
      grid.classList.add('lofts-has-breadcrumb');
    }
    if (legacyProof) legacyProof.classList.add('lofts-legacy-hero-proof');

    if (grid.classList.contains('page-hero-grid')) {
      grid.appendChild(stage);
    } else {
      Array.from(grid.children).forEach(function (child) {
        if (child !== copy && child !== breadcrumb) child.classList.add('lofts-visual-hero__after');
      });
      grid.appendChild(stage);
    }

    window.requestAnimationFrame(function () { stage.classList.add('lofts-hero-stage--ready'); });

    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches &&
        window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      stage.addEventListener('pointermove', function (event) {
        var rect = stage.getBoundingClientRect();
        var x = ((event.clientX - rect.left) / rect.width) - .5;
        var y = ((event.clientY - rect.top) / rect.height) - .5;
        stage.style.setProperty('--stage-x', (x * 8).toFixed(2) + 'px');
        stage.style.setProperty('--stage-y', (y * 6).toFixed(2) + 'px');
      }, { passive: true });
      stage.addEventListener('pointerleave', function () {
        stage.style.setProperty('--stage-x', '0px');
        stage.style.setProperty('--stage-y', '0px');
      }, { passive: true });
    }
  }

  installVisualHeroes();

  var socialProfiles = [
    { name: 'Instagram', mark: 'IG', url: 'https://www.instagram.com/lofts.studio/' },
    { name: 'Facebook', mark: 'f', url: 'https://www.facebook.com/profile.php?id=61591722984967' },
    { name: 'Pinterest', mark: 'P', url: 'https://www.pinterest.com/loftsstudio/' },
    { name: 'LinkedIn', mark: 'in', url: 'https://www.linkedin.com/company/lofts-studio/' }
  ];

  function ensurePublicFooter() {
    if (/^\/admin(?:\/|$)/.test(window.location.pathname) ||
        document.body.classList.contains('landing-page-paid')) return null;

    var footer = document.querySelector('.site-footer');
    if (footer) return footer;

    var main = document.querySelector('main');
    if (!main) return null;

    footer = document.createElement('footer');
    footer.className = 'site-footer lofts-compact-footer';
    footer.innerHTML =
      '<div class="container">' +
        '<div class="lofts-compact-footer__nav">' +
          '<a class="lofts-compact-footer__brand" href="/"><em>Lofts</em><span>STUDIO</span></a>' +
          '<nav aria-label="Footer navigation">' +
            '<a href="/portfolio">Work</a>' +
            '<a href="/services">Services</a>' +
            '<a href="/tools">Tools</a>' +
            '<a href="/#contact">Get in touch</a>' +
          '</nav>' +
        '</div>' +
        '<div class="footer-bottom">' +
          '<p class="meta">&copy; ' + new Date().getFullYear() + ' Lofts Studio</p>' +
          '<p class="meta">Senior web design &amp; engineering</p>' +
        '</div>' +
      '</div>';
    main.insertAdjacentElement('afterend', footer);
    return footer;
  }

  function installFooterSocials(footer) {
    if (!footer || footer.querySelector('.lofts-footer-socials')) return;
    var footerContainer = footer.querySelector(':scope > .container') || footer;
    var footerBottom = footerContainer.querySelector(':scope > .footer-bottom');
    var socialSection = document.createElement('section');
    socialSection.className = 'lofts-footer-socials';
    socialSection.setAttribute('aria-labelledby', 'lofts-social-heading');
    socialSection.innerHTML =
      '<div class="lofts-footer-socials__intro">' +
        '<span>Elsewhere</span>' +
        '<p id="lofts-social-heading">Follow the work, field notes, and studio updates.</p>' +
      '</div>' +
      '<nav class="lofts-footer-socials__links" aria-label="Lofts Studio social profiles">' +
        socialProfiles.map(function (profile) {
          return '<a class="lofts-social-link" href="' + profile.url + '" target="_blank" rel="me noopener noreferrer">' +
            '<span class="lofts-social-link__mark" aria-hidden="true">' + profile.mark + '</span>' +
            '<span>' + profile.name + '</span>' +
            '<b aria-hidden="true">&nearr;</b>' +
          '</a>';
        }).join('') +
      '</nav>';

    if (footerBottom) footerContainer.insertBefore(socialSection, footerBottom);
    else footerContainer.appendChild(socialSection);
  }

  var publicFooter = ensurePublicFooter();
  installFooterSocials(publicFooter);

  var footerContainer = publicFooter && (publicFooter.querySelector(':scope > .container') || publicFooter);
  if (footerContainer && !publicFooter.classList.contains('lofts-compact-footer') && !footerContainer.querySelector('.lofts-footer-call')) {
    var footerCall = document.createElement('div');
    footerCall.className = 'lofts-footer-call';
    footerCall.innerHTML = '<div><span class="lofts-footer-call__eyebrow">A useful next step</span><a class="lofts-footer-call__link" href="/#contact">Bring us the page, funnel, or system that needs to move.</a><p class="lofts-footer-call__note">We will respond with the clearest first move, not a generic proposal.</p></div><div class="lofts-footer-call__actions"><a class="btn btn-primary" href="/#contact">Start a project <span aria-hidden="true">&rarr;</span></a><a class="btn btn-ghost" href="/free-audit">Run a free audit</a></div>';
    footerContainer.insertBefore(footerCall, footerContainer.firstChild);
  }

  function installMobileAccessibility() {
    var mobileNavFoot = document.querySelector('.mnav-foot');
    var diagnosticNavLinks = document.querySelector('.diagnostic-nav-links');
    var accessibilityLauncher = document.querySelector('.a11y-launcher');
    if (!accessibilityLauncher || (!mobileNavFoot && !diagnosticNavLinks)) return false;
    if (mobileNavFoot?.querySelector('.mnav-accessibility') || diagnosticNavLinks?.querySelector('.diagnostic-a11y')) return true;

    var mobileAccessibility = document.createElement('button');
    mobileAccessibility.type = 'button';
    var useDiagnosticNav = !mobileNavFoot && diagnosticNavLinks;
    mobileAccessibility.className = useDiagnosticNav ? 'diagnostic-a11y' : 'mnav-accessibility';
    mobileAccessibility.setAttribute('aria-label', 'Accessibility preferences');
    var accessibilityIcon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="4" r="2"/><path d="M4 9h16M12 6v14m-4 1 4-9 4 9"/></svg>';
    mobileAccessibility.innerHTML = useDiagnosticNav
      ? accessibilityIcon
      : accessibilityIcon + ' Accessibility preferences';
    mobileAccessibility.addEventListener('click', function () {
      var menuClose = document.getElementById('menuClose');
      if (menuClose) menuClose.click();
      window.setTimeout(function () { accessibilityLauncher.click(); }, 90);
    });
    if (useDiagnosticNav) diagnosticNavLinks.appendChild(mobileAccessibility);
    else mobileNavFoot.insertBefore(mobileAccessibility, mobileNavFoot.firstChild);
    document.documentElement.classList.add('has-mnav-accessibility');
    return true;
  }

  if (!installMobileAccessibility() && 'MutationObserver' in window) {
    var accessibilityObserver = new MutationObserver(function () {
      if (installMobileAccessibility()) accessibilityObserver.disconnect();
    });
    accessibilityObserver.observe(document.body, { childList: true, subtree: true });
    window.setTimeout(function () { accessibilityObserver.disconnect(); }, 15000);
  }

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var canTilt = window.matchMedia('(hover: hover) and (pointer: fine)').matches &&
    !reduceMotion;

  if (canTilt) {
    document.querySelectorAll('.home-portfolio-stage .pf-card-img, .portfolio-page .work-card-img-link').forEach(function (media) {
      media.setAttribute('data-lofts-tilt', '');
      media.addEventListener('pointermove', function (event) {
        var rect = media.getBoundingClientRect();
        var x = (event.clientX - rect.left) / rect.width - .5;
        var y = (event.clientY - rect.top) / rect.height - .5;
        media.style.setProperty('--tilt-x', (y * -2.4).toFixed(2) + 'deg');
        media.style.setProperty('--tilt-y', (x * 2.4).toFixed(2) + 'deg');
      }, { passive: true });
      media.addEventListener('pointerleave', function () {
        media.style.setProperty('--tilt-x', '0deg');
        media.style.setProperty('--tilt-y', '0deg');
      }, { passive: true });
    });
  }

  function installScrollExperience() {
    if (reduceMotion) return;

    var root = document.documentElement;
    var revealNodes = Array.from(document.querySelectorAll(
      '[data-reveal], .service-card, .tool-card, .post-card, .review-card, .metric-card, .portfolio-page .work-card'
    )).filter(function (element) {
      return !element.classList.contains('hero-grid') && !element.closest('.hero-scroll-scene');
    });

    revealNodes.forEach(function (element) {
      element.setAttribute('data-lofts-reveal', '');
      var siblings = Array.from(element.parentElement ? element.parentElement.children : []);
      var order = Math.max(0, siblings.indexOf(element)) % 5;
      element.style.setProperty('--lofts-reveal-delay', (order * 65) + 'ms');
    });

    var initialRevealRects = revealNodes.map(function (element) {
      return { element: element, rect: element.getBoundingClientRect() };
    });
    initialRevealRects.forEach(function (item) {
      var element = item.element;
      var rect = item.rect;
      if (rect.top < window.innerHeight * .94 && rect.bottom > 0) {
        element.classList.add('lofts-in-view');
      }
    });

    root.classList.add('lofts-motion-ready');

    if ('IntersectionObserver' in window) {
      var revealObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('lofts-in-view');
          revealObserver.unobserve(entry.target);
        });
      }, { threshold: .08, rootMargin: '0px 0px -8% 0px' });
      revealNodes.forEach(function (element) {
        if (!element.classList.contains('lofts-in-view')) revealObserver.observe(element);
      });
    } else {
      revealNodes.forEach(function (element) { element.classList.add('lofts-in-view'); });
    }

    var parallaxFrames = Array.from(document.querySelectorAll(
      '.home-portfolio-stage .pf-card-img, .portfolio-page .work-card-img-link, .case-study .case-image'
    ));
    var activeParallax = new Set();
    parallaxFrames.forEach(function (frame) { frame.setAttribute('data-lofts-parallax', ''); });

    if ('IntersectionObserver' in window) {
      var parallaxObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) activeParallax.add(entry.target);
          else activeParallax.delete(entry.target);
        });
      }, { rootMargin: '240px 0px' });
      parallaxFrames.forEach(function (frame) { parallaxObserver.observe(frame); });
    } else {
      parallaxFrames.forEach(function (frame) { activeParallax.add(frame); });
    }

    var heroTrack = document.querySelector('.hero-scroll-track');
    var heroScene = document.querySelector('.hero-scroll-scene');
    var essay = document.querySelector('.home-page .essay-section');
    var lastInputY = window.scrollY;
    var lastInputTime = performance.now();
    var scrollVelocity = 0;
    var framePending = false;

    function clamp(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }

    function easeProgress(value) {
      return value * value * (3 - (2 * value));
    }

    function updateHero() {
      if (!heroTrack || !heroScene) return;
      var rect = heroScene.getBoundingClientRect();
      var progress = clamp(-rect.top / Math.max(1, rect.height), 0, 1);
      var eased = easeProgress(progress);

      heroScene.style.setProperty('--hero-copy-y', (-8 * eased).toFixed(1) + 'px');
      heroScene.style.setProperty('--hero-reel-y', (-18 * eased).toFixed(1) + 'px');
      heroScene.style.setProperty('--hero-echo-shadow', Math.min(8, Math.abs(scrollVelocity) * 2.5).toFixed(1) + 'px');
      heroScene.classList.remove('hero-copy-away');
    }

    function updateParallax() {
      if (window.innerWidth <= 640) {
        activeParallax.forEach(function (frame) {
          var image = frame.querySelector('img');
          if (image) image.style.removeProperty('--lofts-media-y');
        });
        return;
      }

      activeParallax.forEach(function (frame) {
        var image = frame.querySelector('img');
        if (!image) return;
        var rect = frame.getBoundingClientRect();
        var centerOffset = ((rect.top + (rect.height / 2)) - (window.innerHeight / 2)) / window.innerHeight;
        var range = window.innerWidth > 980 ? 22 : 12;
        image.style.setProperty('--lofts-media-y', clamp(centerOffset * -range, -range, range).toFixed(1) + 'px');
      });
    }

    function updateEssay() {
      if (!essay) return;
      var rect = essay.getBoundingClientRect();
      var progress = clamp((window.innerHeight - rect.top) / (window.innerHeight + rect.height * .55), 0, 1);
      essay.style.setProperty('--essay-rule-progress', (progress * 100).toFixed(2) + '%');
      essay.style.setProperty('--essay-content-y', ((1 - progress) * 24).toFixed(1) + 'px');
    }

    function renderMotion() {
      framePending = false;
      document.body.classList.toggle('lofts-scrolled', window.scrollY > 24);
      updateHero();
      updateParallax();
      updateEssay();
      scrollVelocity *= .72;
      if (Math.abs(scrollVelocity) > .015) requestFrame();
    }

    function requestFrame() {
      if (framePending) return;
      framePending = true;
      window.requestAnimationFrame(renderMotion);
    }

    function onScroll() {
      var now = performance.now();
      var y = window.scrollY;
      var elapsed = Math.max(16, now - lastInputTime);
      var instantVelocity = (y - lastInputY) / elapsed;
      scrollVelocity = (scrollVelocity * .48) + (instantVelocity * .52);
      lastInputY = y;
      lastInputTime = now;
      requestFrame();
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', requestFrame, { passive: true });
    requestFrame();
  }

  installScrollExperience();
})();

/* ── Optional third-party loaders for PageSpeed-sensitive pages ── */
(function () {
  var script = document.currentScript || document.querySelector('script[data-full-css], script[data-widgets-src], script[data-analytics-id]');
  var fullCss = script && script.dataset ? script.dataset.fullCss : '';
  var analyticsId = script && script.dataset ? script.dataset.analyticsId : '';
  var widgetsSrc = script && script.dataset ? script.dataset.widgetsSrc : '';
  var gtmId = 'GTM-PM4CX9JG';
  var consentKey = 'adnank-cookie-consent-v1';
  var loadedFullCss = false;
  var loadedAnalytics = false;
  var loadedWidgets = false;

  function loadScript(src, id) {
    if (!src || (id && document.getElementById(id))) return;
    var s = document.createElement('script');
    if (id) s.id = id;
    s.async = true;
    s.src = src;
    document.head.appendChild(s);
  }

  function loadFullCss() {
    if (!fullCss || loadedFullCss || document.querySelector('link[href="' + fullCss + '"]')) return;
    loadedFullCss = true;
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = fullCss;
    var experienceLink = document.querySelector('link[data-lofts-experience]');
    if (experienceLink && experienceLink.parentNode) {
      experienceLink.parentNode.insertBefore(link, experienceLink);
    } else {
      document.head.appendChild(link);
    }
  }

  function loadAnalytics() {
    var consent = null;
    try { consent = window.localStorage.getItem(consentKey); } catch (_) {}
    if ((!analyticsId && !gtmId) || consent !== 'accepted' || loadedAnalytics || document.getElementById('lofts-gtm')) return;
    loadedAnalytics = true;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ 'gtm.start': Date.now(), event: 'gtm.js' });
    loadScript('https://www.googletagmanager.com/gtm.js?id=' + encodeURIComponent(gtmId), 'lofts-gtm');
  }

  function loadWidgets() {
    if (!widgetsSrc || loadedWidgets) return;
    loadedWidgets = true;
    loadScript(widgetsSrc, 'lofts-widgets');
  }

  function afterFirstPaint(fn, delay) {
    var run = function () { window.setTimeout(fn, delay || 0); };
    if (document.readyState === 'complete') run();
    else window.addEventListener('load', run, { once: true });
  }

  if (!fullCss && !analyticsId && !widgetsSrc && !gtmId) return;
  if (fullCss && window.location.hash) loadFullCss();
  if (fullCss) afterFirstPaint(loadFullCss, 180);
  if (widgetsSrc) afterFirstPaint(loadWidgets, 900);
  document.addEventListener('cookie:consent', function (event) {
    if (event.detail === 'accepted') loadAnalytics();
  });
  afterFirstPaint(loadAnalytics, 1200);
  ['pointerdown', 'keydown', 'touchstart', 'scroll'].forEach(function (eventName) {
    window.addEventListener(eventName, function () {
      loadFullCss();
      loadAnalytics();
      loadWidgets();
    }, { once: true, passive: true });
  });
})();
