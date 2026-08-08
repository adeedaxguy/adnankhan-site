(function () {
  'use strict';

  var root = document.documentElement;
  var path = window.location.pathname;
  var excluded = path.indexOf('/admin/') === 0 ||
    document.body.classList.contains('diagnostic-page') ||
    document.body.classList.contains('agency-command-page');
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var saveData = !!(navigator.connection && navigator.connection.saveData);

  if (excluded || reducedMotion) {
    root.classList.add('lofts-motion-reduced');
    return;
  }

  var vendorRoot = '/assets/vendor/';

  function loadScript(src, test) {
    if (test()) return Promise.resolve();
    return new Promise(function (resolve, reject) {
      var existing = document.querySelector('script[src="' + src + '"]');
      if (existing) {
        existing.addEventListener('load', resolve, { once: true });
        existing.addEventListener('error', reject, { once: true });
        return;
      }
      var script = document.createElement('script');
      script.src = src;
      script.async = true;
      script.addEventListener('load', resolve, { once: true });
      script.addEventListener('error', reject, { once: true });
      document.head.appendChild(script);
    });
  }

  function debounce(fn, wait) {
    var timer = 0;
    return function () {
      var args = arguments;
      window.clearTimeout(timer);
      timer = window.setTimeout(function () { fn.apply(null, args); }, wait);
    };
  }

  function startScrollSystem() {
    if (!window.gsap || !window.ScrollTrigger || !window.Lenis) return;

    var gsap = window.gsap;
    var ScrollTrigger = window.ScrollTrigger;
    gsap.registerPlugin(ScrollTrigger);

    var lenis = new window.Lenis({
      duration: 1.05,
      easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
      smoothWheel: true,
      syncTouch: false,
      wheelMultiplier: 0.86,
      touchMultiplier: 1.05,
      anchors: { offset: -88, duration: 0.9 }
    });

    window.loftsLenis = lenis;
    root.classList.add('lofts-motion-ready', 'gsap-ready');
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
    gsap.ticker.lagSmoothing(0);

    document.addEventListener('visibilitychange', function () {
      if (document.hidden) lenis.stop();
      else lenis.start();
    });

    new MutationObserver(function () {
      if (document.body.classList.contains('menu-lock')) lenis.stop();
      else if (!document.hidden) lenis.start();
    }).observe(document.body, { attributes: true, attributeFilter: ['class'] });

    installHeroReveals(gsap);
    installTextParallax(gsap, ScrollTrigger);
    ScrollTrigger.refresh();
  }

  function installHeroReveals(gsap) {
    var homeLines = Array.prototype.slice.call(document.querySelectorAll('.hero-title-line > span'));
    if (homeLines.length) {
      gsap.fromTo(homeLines,
        { yPercent: 108 },
        { yPercent: 0, duration: 0.2, stagger: 0.045, ease: 'power2.out', clearProps: 'transform' }
      );
    }

    var letterHeading = document.querySelector('[data-letter-reveal]');
    if (!letterHeading || letterHeading.dataset.splitReady === 'true') return;

    var label = letterHeading.textContent.replace(/\s+/g, ' ').trim();
    var letters = [];

    function wrapTextNodes(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === Node.TEXT_NODE) {
          var fragment = document.createDocumentFragment();
          child.nodeValue.split(/(\s+)/).forEach(function (token) {
            if (!token) return;
            if (/^\s+$/.test(token)) {
              fragment.appendChild(document.createTextNode(token));
              return;
            }
            var word = document.createElement('span');
            word.className = 'lofts-word';
            Array.from(token).forEach(function (character) {
              var clip = document.createElement('span');
              clip.className = 'lofts-char-clip';
              clip.setAttribute('aria-hidden', 'true');
              var glyph = document.createElement('span');
              glyph.className = 'lofts-char';
              glyph.textContent = character;
              clip.appendChild(glyph);
              word.appendChild(clip);
              letters.push(glyph);
            });
            fragment.appendChild(word);
          });
          child.parentNode.replaceChild(fragment, child);
        } else if (child.nodeType === Node.ELEMENT_NODE) {
          wrapTextNodes(child);
        }
      });
    }

    letterHeading.dataset.splitReady = 'true';
    letterHeading.setAttribute('aria-label', label);
    wrapTextNodes(letterHeading);
    gsap.fromTo(letters,
      { yPercent: 112 },
      { yPercent: 0, duration: 0.2, stagger: 0.012, ease: 'power2.out', clearProps: 'transform' }
    );
  }

  function installTextParallax(gsap, ScrollTrigger) {
    if (window.matchMedia('(max-width: 760px), (pointer: coarse)').matches) return;

    var candidates = [
      '.hero-main',
      '.lofts-visual-hero__copy',
      '.page-hero-copy',
      '.services-hero__copy'
    ];

    candidates.forEach(function (selector) {
      document.querySelectorAll(selector).forEach(function (block) {
        var heading = block.querySelector('h1, .hero-title');
        var body = block.querySelector('.lead, p');
        if (!heading || !body || block.dataset.parallaxReady === 'true') return;
        block.dataset.parallaxReady = 'true';

        gsap.to(heading, {
          y: -48,
          ease: 'none',
          scrollTrigger: {
            trigger: block,
            start: 'top top',
            end: 'bottom 20%',
            scrub: 0.45
          }
        });
        gsap.to(body, {
          y: -8,
          ease: 'none',
          scrollTrigger: {
            trigger: block,
            start: 'top top',
            end: 'bottom 20%',
            scrub: 0.45
          }
        });
      });
    });
  }

  function startThreeHero() {
    var host = document.querySelector('[data-three-hero]');
    if (!host || saveData || !window.WebGLRenderingContext) return;
    if (navigator.deviceMemory && navigator.deviceMemory <= 2) return;

    import(vendorRoot + 'three-r184.module.min.js').then(function (THREE) {
      var mobile = window.matchMedia('(max-width: 760px)').matches;
      var scene = new THREE.Scene();
      var camera = new THREE.PerspectiveCamera(34, 1, 0.1, 40);
      camera.position.set(0, 0, 5.4);

      var renderer = new THREE.WebGLRenderer({ alpha: true, antialias: !mobile, powerPreference: 'low-power' });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, mobile ? 1 : 1.5));
      renderer.setClearColor(0x000000, 0);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      host.appendChild(renderer.domElement);

      var geometry = new THREE.IcosahedronGeometry(1.72, mobile ? 1 : 2);
      var material = new THREE.MeshPhysicalMaterial({
        color: 0xd2cdc2,
        metalness: 0.1,
        roughness: 0.2,
        clearcoat: 1.0,
        clearcoatRoughness: 0.12,
        transmission: 0.72,
        thickness: 0.34,
        transparent: true,
        opacity: 0.04,
        depthWrite: false,
        side: THREE.DoubleSide
      });
      var mesh = new THREE.Mesh(geometry, material);
      mesh.rotation.set(-0.16, 0.42, 0.08);
      mesh.scale.set(1.18, 0.9, 1);
      scene.add(mesh);

      var wire = new THREE.LineSegments(
        new THREE.EdgesGeometry(geometry, 14),
        new THREE.LineBasicMaterial({ color: 0x8b3a1f, transparent: true, opacity: 0.34, depthWrite: false })
      );
      wire.scale.setScalar(1.012);
      mesh.add(wire);

      scene.add(new THREE.HemisphereLight(0xf8f5ef, 0x3f443f, 1.25));
      var key = new THREE.DirectionalLight(0xffffff, 1.8);
      key.position.set(3, 4, 5);
      scene.add(key);
      var edge = new THREE.PointLight(0xa44c30, 2.8, 12);
      edge.position.set(-3, -1, 3);
      scene.add(edge);

      function syncThreeTheme() {
        var dark = root.getAttribute('data-theme') === 'dark';
        material.color.setHex(dark ? 0xa7a096 : 0xd2cdc2);
        material.opacity = dark ? 0.05 : 0.035;
        wire.material.color.setHex(dark ? 0xc96b4a : 0x8b3a1f);
        wire.material.opacity = dark ? 0.3 : 0.34;
      }
      syncThreeTheme();
      var themeObserver = new MutationObserver(syncThreeTheme);
      themeObserver.observe(root, { attributes: true, attributeFilter: ['data-theme'] });

      var positions = geometry.attributes.position;
      var base = new Float32Array(positions.array);
      var mouse = { x: 0, y: 0 };
      var targetMouse = { x: 0, y: 0 };
      var inView = true;
      var running = true;
      var startedAt = window.performance.now();

      function sizeCanvas() {
        var rect = host.getBoundingClientRect();
        if (!rect.width || !rect.height) return;
        renderer.setSize(rect.width, rect.height, false);
        camera.aspect = rect.width / rect.height;
        camera.updateProjectionMatrix();
      }

      function onPointerMove(event) {
        var rect = host.getBoundingClientRect();
        targetMouse.x = ((event.clientX - rect.left) / Math.max(1, rect.width)) * 2 - 1;
        targetMouse.y = -(((event.clientY - rect.top) / Math.max(1, rect.height)) * 2 - 1);
      }

      function render() {
        if (!running) return;
        window.requestAnimationFrame(render);
        if (!inView || document.hidden) return;

        var time = (window.performance.now() - startedAt) / 1000;
        mouse.x += (targetMouse.x - mouse.x) * 0.055;
        mouse.y += (targetMouse.y - mouse.y) * 0.055;

        for (var i = 0; i < positions.count; i += 1) {
          var offset = i * 3;
          var bx = base[offset];
          var by = base[offset + 1];
          var bz = base[offset + 2];
          var wave = Math.sin((bx * 1.55) + (by * 1.35) + (bz * 1.15) + (time * 0.72)) * 0.035;
          var cursor = ((bx * mouse.x) + (by * mouse.y)) * 0.012;
          var scale = 1 + wave + cursor;
          positions.array[offset] = bx * scale;
          positions.array[offset + 1] = by * scale;
          positions.array[offset + 2] = bz * scale;
        }
        positions.needsUpdate = true;
        geometry.computeVertexNormals();

        var scroll = window.loftsLenis ? window.loftsLenis.scroll : window.scrollY;
        mesh.rotation.y += ((0.48 + scroll * 0.00042 + mouse.x * 0.14) - mesh.rotation.y) * 0.045;
        mesh.rotation.x += ((-0.18 + mouse.y * 0.1) - mesh.rotation.x) * 0.045;
        renderer.render(scene, camera);
      }

      var observer = new IntersectionObserver(function (entries) {
        inView = !!(entries[0] && entries[0].isIntersecting);
      }, { rootMargin: '180px 0px' });
      observer.observe(host);

      var resize = debounce(sizeCanvas, 180);
      window.addEventListener('resize', resize, { passive: true });
      window.addEventListener('pointermove', onPointerMove, { passive: true });
      window.addEventListener('pagehide', function () {
        running = false;
        observer.disconnect();
        themeObserver.disconnect();
        renderer.dispose();
        geometry.dispose();
        material.dispose();
        wire.material.dispose();
      }, { once: true });

      sizeCanvas();
      host.classList.add('is-rendered');
      render();
    }).catch(function () {
      host.classList.add('is-unavailable');
    });
  }

  Promise.resolve()
    .then(function () { return loadScript(vendorRoot + 'gsap-3.15.0.min.js', function () { return !!window.gsap; }); })
    .then(function () { return loadScript(vendorRoot + 'scrolltrigger-3.15.0.min.js', function () { return !!window.ScrollTrigger; }); })
    .then(function () { return loadScript(vendorRoot + 'lenis-1.3.23.min.js', function () { return !!window.Lenis; }); })
    .then(startScrollSystem)
    .catch(function () { root.classList.add('lofts-motion-fallback'); });

  startThreeHero();
}());
