/* ─────────────────────────────────────────────────────────────
   Adnan K. — shared interactivity
   ───────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  const adAttributionKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'gbraid', 'wbraid'];
  const adAttributionStore = 'lofts_ad_attribution';

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
    const payload = {
      ...params,
      page_path: window.location.pathname,
      page_title: document.title
    };
    window.dataLayer = window.dataLayer || [];
    if (typeof window.gtag === 'function') {
      window.gtag('event', eventName, payload);
    } else {
      window.dataLayer.push({ event: eventName, ...payload });
    }
  };

  persistAdAttribution();
  window.loftsGetAdAttribution = getAdAttribution;
  window.loftsTrackEvent = trackMarketingEvent;

  // ── Hero word-split (runs synchronously, before paint of split-done state) ──
  // CSS animation drives the actual reveal; we just wrap words + add the class.
  // Works without GSAP — independent of CDN availability.
  const splitWordsForReveal = (el) => {
    let idx = 0;
    const walk = (node) => {
      if (node.nodeType === 3) {
        const frag = document.createDocumentFragment();
        node.textContent.split(/(\s+)/).forEach(piece => {
          if (!piece) return;
          if (/^\s+$/.test(piece)) {
            frag.appendChild(document.createTextNode(piece));
          } else {
            const mask = document.createElement('span');
            mask.className = 'word-mask';
            const inner = document.createElement('span');
            inner.className = 'word';
            inner.style.setProperty('--i', idx++);
            inner.textContent = piece;
            mask.appendChild(inner);
            frag.appendChild(mask);
          }
        });
        node.parentNode.replaceChild(frag, node);
      } else if (node.nodeType === 1 && node.tagName !== 'SCRIPT' && node.tagName !== 'STYLE') {
        Array.from(node.childNodes).forEach(walk);
      }
    };
    walk(el);
  };

  // Process every data-split element immediately on script eval.
  // Browsers respect defer → this runs after DOMContent but before window.load.
  document.querySelectorAll('[data-split="words"]').forEach(el => {
    splitWordsForReveal(el);
    el.classList.add('split-done');
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

  // Failsafe: if for any reason the words aren't visible after 3s, force them visible.
  setTimeout(() => {
    document.querySelectorAll('[data-split="words"]').forEach(el => {
      el.style.visibility = 'visible';
      el.querySelectorAll('.word').forEach(w => { w.style.transform = 'translateY(0)'; });
    });
  }, 3000);

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

  const contactSection = document.getElementById('contact');
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
      document.documentElement.classList.add('menu-lock');
      document.body.classList.add('menu-lock');
      mnav.scrollTop = 0;
    };

    const closeMenu = () => {
      open = false;
      mnav.classList.remove('open');
      mnav.setAttribute('aria-hidden', 'true');
      mnav.setAttribute('inert', '');
      menuBtn.setAttribute('aria-expanded', 'false');
      document.documentElement.classList.remove('menu-lock');
      document.body.classList.remove('menu-lock');
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
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && open) closeMenu(); });

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
    if (href.includes('/free-audit/')) eventName = 'audit_cta_click';
    if (!eventName) return;
    trackMarketingEvent(eventName, {
      event_category: 'lead',
      event_label: href.replace(/^mailto:/, '').split('?')[0],
      link_location: window.location.pathname
    });
  });

  // ── Reveal fallback (used ONLY if GSAP fails to load) ──
  // If GSAP loads (the usual path), it takes over via the .gsap-ready class and
  // animates these elements smoothly. If GSAP fails — broken CDN, ad blocker,
  // ancient browser — this IntersectionObserver is the safety net so content
  // still appears instead of staying invisible.
  const gsapTakeoverTimeout = setTimeout(() => {
    if (document.documentElement.classList.contains('gsap-ready')) return;
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
  }, 1500); // wait 1.5s for GSAP CDN; if it didn't arrive, fall back

  // ── Year stamp in footer ──
  document.querySelectorAll('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });

  // ── GSAP premium animations ──
  // Loads after window load to avoid blocking first paint. No-op if CDN failed.
  window.addEventListener('load', () => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;

    gsap.registerPlugin(ScrollTrigger);
    document.documentElement.classList.add('gsap-ready');

    // 1) Hero word-reveal already handled by IIFE + CSS animation (above).
    //    GSAP doesn't need to touch [data-split="words"] elements.

    // 1b) Scroll-triggered mask-reveal for .h-1 / .h-2 headlines.
    //     Reuses the same .word-mask wrapper but driven by ScrollTrigger.
    const splitWordsScroll = (el) => {
      const walk = (node) => {
        if (node.nodeType === 3) {
          const frag = document.createDocumentFragment();
          node.textContent.split(/(\s+)/).forEach(piece => {
            if (!piece) return;
            if (/^\s+$/.test(piece)) {
              frag.appendChild(document.createTextNode(piece));
            } else {
              const mask = document.createElement('span');
              mask.className = 'word-mask';
              const inner = document.createElement('span');
              inner.className = 'word';
              inner.textContent = piece;
              mask.appendChild(inner);
              frag.appendChild(mask);
            }
          });
          node.parentNode.replaceChild(frag, node);
        } else if (node.nodeType === 1 && node.tagName !== 'SCRIPT' && node.tagName !== 'STYLE') {
          Array.from(node.childNodes).forEach(walk);
        }
      };
      walk(el);
    };

    document.querySelectorAll('.h-1, .h-2').forEach(el => {
      if (el.closest('[data-split="words"]')) return;
      if (el.querySelector('.word-mask')) return;
      splitWordsScroll(el);
      gsap.set(el.querySelectorAll('.word'), { yPercent: 110 });
      ScrollTrigger.create({
        trigger: el,
        start: 'top 88%',
        once: true,
        onEnter: () => gsap.to(el.querySelectorAll('.word'), {
          yPercent: 0,
          duration: 1.1,
          ease: 'power3.out',
          stagger: 0.04,
        }),
      });
    });

    // 2) Counters — animate from 0 → target when the element scrolls into view.
    document.querySelectorAll('[data-count]').forEach(el => {
      const target = parseFloat(el.dataset.count);
      if (isNaN(target)) return;
      const decimals = parseInt(el.dataset.decimals) || 0;
      const prefix = el.dataset.prefix || '';
      const suffix = el.dataset.suffix || '';
      const format = (v) => prefix + v.toFixed(decimals) + suffix;
      const obj = { val: 0 };
      el.textContent = format(0);

      ScrollTrigger.create({
        trigger: el,
        start: 'top 88%',
        once: true,
        onEnter: () => {
          gsap.to(obj, {
            val: target,
            duration: 1.8,
            ease: 'power2.out',
            onUpdate: () => { el.textContent = format(obj.val); },
          });
        },
      });
    });

    // 3) Generic section reveal — keep content readable even if animation timing stalls.
    gsap.utils.toArray('[data-reveal]').forEach(el => {
      ScrollTrigger.create({
        trigger: el,
        start: 'top 88%',
        once: true,
        onEnter: () => gsap.fromTo(el, {
          y: 18,
        }, {
          y: 0, duration: 0.72, ease: 'power3.out',
        }),
      });
    });

    // 4) Magnetic CTAs — primary buttons subtly track the cursor.
    document.querySelectorAll('[data-magnetic]').forEach(btn => {
      const strength = 0.22;
      const onMove = (e) => {
        const r = btn.getBoundingClientRect();
        const x = (e.clientX - r.left - r.width / 2) * strength;
        const y = (e.clientY - r.top - r.height / 2) * strength;
        gsap.to(btn, { x, y, duration: 0.45, ease: 'power3.out' });
      };
      const onLeave = () => {
        gsap.to(btn, { x: 0, y: 0, duration: 0.7, ease: 'elastic.out(1, 0.3)' });
      };
      btn.addEventListener('mousemove', onMove);
      btn.addEventListener('mouseleave', onLeave);
    });

    // 5) Refresh on font load (Fraunces is variable + loads after first paint;
    //    triggers ScrollTrigger to recompute positions accurately).
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => ScrollTrigger.refresh());
    }
  });
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
  let tiltX      = 4;   // base tilt
  let tiltY      = -8;
  let isHovering = false;
  let cycleTimer = null;
  let cycleStarted = false;

  // ── Positions for each depth slot ─────────────────────────────
  const SLOTS = [
    { tz:    0, tx:  0,  ty:  0,  op: 1.0  },
    { tz:  -22, tx: 13,  ty: 11,  op: 0.85 },
    { tz:  -44, tx: 24,  ty: 20,  op: 0.65 },
    { tz:  -66, tx: 34,  ty: 28,  op: 0.45 },
    { tz:  -88, tx: 42,  ty: 34,  op: 0.20 },
    { tz: -108, tx: 50,  ty: 40,  op: 0.08 },
    { tz: -120, tx: 55,  ty: 44,  op: 0    },
    { tz: -120, tx: 55,  ty: 44,  op: 0    },
    { tz: -120, tx: 55,  ty: 44,  op: 0    },
    { tz: -120, tx: 55,  ty: 44,  op: 0    },
  ];

  const isMobile = () => window.innerWidth <= 768;

  function loadCardImage(card) {
    const img = card.querySelector('.stack-card-img[data-bg]');
    if (!img) return;
    img.style.backgroundImage = img.dataset.bg;
    img.removeAttribute('data-bg');
  }

  // ── Mobile: pure crossfade, no transforms ─────────────────────
  function applyFade() {
    cards.forEach((card, i) => {
      const isFront = i === frontIdx;
      card.classList.toggle('is-front', isFront);
      card.style.transform = '';
      card.style.opacity   = '';
      card.style.zIndex    = '';
    });
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
    });
  }

  // ── Mouse tilt (desktop only) ──────────────────────────────────
  scene.addEventListener('mousemove', (e) => {
    if (isMobile()) return;
    startCycle();
    isHovering = true;
    const r  = scene.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width  - 0.5;
    const py = (e.clientY - r.top)  / r.height - 0.5;
    tiltX =  py * -14 + 2;
    tiltY =  px *  18 - 4;
    applySlots(tiltX, tiltY);
  });

  scene.addEventListener('mouseleave', () => {
    if (isMobile()) return;
    isHovering = false;
    const lerp = (a, b, t) => a + (b - a) * t;
    let frame;
    const ease = () => {
      tiltX = lerp(tiltX, 4,  0.08);
      tiltY = lerp(tiltY, -8, 0.08);
      applySlots(tiltX, tiltY);
      if (Math.abs(tiltX - 4) > 0.05 || Math.abs(tiltY + 8) > 0.05) {
        frame = requestAnimationFrame(ease);
      }
    };
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(ease);
  });

  // ── Tap → next card ───────────────────────────────────────────
  scene.addEventListener('click', () => {
    startCycle();
    frontIdx = (frontIdx + 1) % cards.length;
    applySlots(tiltX, tiltY);
    resetCycle();
  });

  // ── Auto-cycle ────────────────────────────────────────────────
  function startCycle() {
    if (cycleStarted) return;
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


/* ── Theme toggle (light / dark) ────────────────────────────────── */
(function () {
  var KEY = 'lofts-theme';
  function apply(m){ document.documentElement.setAttribute('data-theme', m === 'dark' ? 'dark' : 'light'); }
  function get(){ try { var v = localStorage.getItem(KEY); return (v === 'dark') ? 'dark' : 'light'; } catch(e){ return 'light'; } }
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
      b.title = label; b.setAttribute('aria-label', label + ' theme'); b.innerHTML = ICON[m];
      b.addEventListener('click', function(){
        try { localStorage.setItem(KEY, m); } catch(e){}
        apply(m);
        wrap.querySelectorAll('.theme-opt').forEach(function(o){ o.classList.toggle('is-active', o.dataset.mode === m); });
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

/* ── Optional third-party loaders for PageSpeed-sensitive pages ── */
(function () {
  var script = document.currentScript || document.querySelector('script[data-full-css], script[data-widgets-src], script[data-analytics-id]');
  var fullCss = script && script.dataset ? script.dataset.fullCss : '';
  var analyticsId = script && script.dataset ? script.dataset.analyticsId : '';
  var widgetsSrc = script && script.dataset ? script.dataset.widgetsSrc : '';
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
    document.head.appendChild(link);
  }

  function loadAnalytics() {
    if (!analyticsId || loadedAnalytics || typeof window.gtag === 'function') return;
    loadedAnalytics = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function(){ window.dataLayer.push(arguments); };
    loadScript('https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(analyticsId), 'lofts-gtag');
    window.gtag('js', new Date());
    window.gtag('config', analyticsId);
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

  if (!fullCss && !analyticsId && !widgetsSrc) return;
  if (fullCss && window.location.hash) loadFullCss();
  if (fullCss) afterFirstPaint(loadFullCss, 180);
  if (widgetsSrc) afterFirstPaint(loadWidgets, 900);
  ['pointerdown', 'keydown', 'touchstart', 'scroll'].forEach(function (eventName) {
    window.addEventListener(eventName, function () {
      loadFullCss();
      loadAnalytics();
      loadWidgets();
    }, { once: true, passive: true });
  });
})();
