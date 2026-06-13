/* ─────────────────────────────────────────────────────────────
   Adnan K. — shared interactivity
   ───────────────────────────────────────────────────────────── */

(function () {
  'use strict';

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
      menuBtn.setAttribute('aria-expanded', 'true');
      document.documentElement.classList.add('menu-lock');
      document.body.classList.add('menu-lock');
      mnav.scrollTop = 0;
    };

    const closeMenu = () => {
      open = false;
      mnav.classList.remove('open');
      mnav.setAttribute('aria-hidden', 'true');
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

  // ── Lead forms — Formsubmit.co AJAX ──
  // First submission triggers an activation email to .
  // After one click in that email, all future submissions deliver automatically.
  document.querySelectorAll('form[data-lead]').forEach(form => {
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const wrap = form.closest('[data-lead-wrap]') || form.parentElement;
      const success = wrap?.querySelector('[data-lead-success]');
      const btn = form.querySelector('button[type="submit"]');
      const originalHTML = btn ? btn.innerHTML : '';
      if (btn) { btn.disabled = true; btn.innerHTML = 'Sending…'; }

      try {
        const res = await fetch(form.action, {
          method: 'POST',
          headers: { 'Accept': 'application/json' },
          body: new FormData(form),
        });
        const data = await res.json().catch(() => ({}));
        const ok = res.ok && (data.success === 'true' || data.success === true || res.status === 200);
        if (!ok) throw new Error(data.message || 'Submission failed');

        form.style.display = 'none';
        if (success) success.style.display = 'block';
        // Reset button state in case the form is reopened later
        if (btn) { btn.disabled = false; btn.innerHTML = originalHTML; }
      } catch (err) {
        if (btn) { btn.disabled = false; btn.innerHTML = originalHTML; }
        // Inline error message — no native alert popup
        let inlineErr = form.querySelector('[data-lead-error]');
        if (!inlineErr) {
          inlineErr = document.createElement('p');
          inlineErr.setAttribute('data-lead-error', '');
          inlineErr.style.cssText = 'margin-top:0.75rem;font-size:0.85rem;color:#B91C1C;text-align:center;';
          form.appendChild(inlineErr);
        }
        inlineErr.textContent = "Couldn't send — please use the contact form directly.";
      }
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

    // 3) Generic section reveal — set hidden then animate to visible on scroll.
    //    Using gsap.set + gsap.to (instead of fromTo) avoids the flash where
    //    the element is visible briefly before fromTo's "from" state kicks in.
    gsap.utils.toArray('[data-reveal]').forEach(el => {
      gsap.set(el, { opacity: 0, y: 28 });
      ScrollTrigger.create({
        trigger: el,
        start: 'top 88%',
        once: true,
        onEnter: () => gsap.to(el, {
          opacity: 1, y: 0, duration: 0.95, ease: 'power3.out',
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

  const isMobile = () => window.innerWidth <= 880;

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
      card.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg) translateZ(${s.tz}px) translateX(${s.tx}px) translateY(${s.ty}px)`;
      card.style.opacity   = s.op;
      card.style.zIndex    = cards.length - slotIdx;
      card.classList.toggle('is-front', slotIdx === 0);
    });
  }

  // ── Mouse tilt (desktop only) ──────────────────────────────────
  scene.addEventListener('mousemove', (e) => {
    if (isMobile()) return;
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
    frontIdx = (frontIdx + 1) % cards.length;
    applySlots(tiltX, tiltY);
    resetCycle();
  });

  // ── Auto-cycle ────────────────────────────────────────────────
  function resetCycle() {
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
  resetCycle();

  // Re-evaluate on resize (e.g. rotation)
  window.addEventListener('resize', () => applySlots(tiltX, tiltY));

})();
