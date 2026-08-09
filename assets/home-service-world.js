import * as THREE from '/assets/vendor/three-r184.module.min.js';

const host = document.querySelector('[data-home-service-world-canvas]');
const shell = document.querySelector('[data-home-service-world]');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const saveData = Boolean(navigator.connection && navigator.connection.saveData);
const lowMemory = navigator.deviceMemory && navigator.deviceMemory <= 2;

if (host && shell && !reducedMotion && !saveData && !lowMemory && window.WebGLRenderingContext) {
  startServiceWorld(host, shell).catch(() => shell.classList.add('is-unavailable'));
}

async function startServiceWorld(canvasHost, worldShell) {
  const mobile = window.matchMedia('(max-width: 760px)').matches;
  const compact = window.matchMedia('(max-width: 1100px)').matches;
  const cameraY = mobile ? 3.8 : (compact ? 3.6 : 3.4);
  const cameraZ = mobile ? 10.25 : (compact ? 11.5 : 10.35);
  const root = document.documentElement;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(mobile ? 39 : (compact ? 37 : 34), 1, 0.1, 50);
  camera.position.set(0, cameraY, cameraZ);
  camera.lookAt(0, 0.15, 0);

  const renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: !mobile,
    powerPreference: mobile ? 'low-power' : 'high-performance'
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, mobile ? 1 : 1.4));
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.08;
  if (!mobile) {
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
  }
  canvasHost.appendChild(renderer.domElement);

  const geometries = [];
  const materials = [];
  const textures = [];
  const themeDrawers = [];
  const world = new THREE.Group();
  world.rotation.set(-0.08, -0.28, 0);
  world.scale.setScalar(mobile ? 0.86 : (compact ? 0.9 : 1));
  scene.add(world);

  function keepGeometry(geometry) {
    geometries.push(geometry);
    return geometry;
  }

  function keepMaterial(material) {
    materials.push(material);
    return material;
  }

  function physical(color, extra = {}) {
    return keepMaterial(new THREE.MeshPhysicalMaterial({
      color,
      metalness: 0.1,
      roughness: 0.2,
      clearcoat: 1,
      clearcoatRoughness: 0.12,
      ...extra
    }));
  }

  function addBox(parent, size, position, material, rotation = [0, 0, 0]) {
    const mesh = new THREE.Mesh(keepGeometry(new THREE.BoxGeometry(...size)), material);
    mesh.position.set(...position);
    mesh.rotation.set(...rotation);
    mesh.castShadow = !mobile;
    mesh.receiveShadow = !mobile;
    parent.add(mesh);
    return mesh;
  }

  function roundedPath(context, x, y, width, height, radius) {
    const r = Math.min(radius, width / 2, height / 2);
    context.beginPath();
    context.moveTo(x + r, y);
    context.arcTo(x + width, y, x + width, y + height, r);
    context.arcTo(x + width, y + height, x, y + height, r);
    context.arcTo(x, y + height, x, y, r);
    context.arcTo(x, y, x + width, y, r);
    context.closePath();
  }

  function makeCanvasTexture(width, height, draw) {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext('2d');
    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.minFilter = THREE.LinearFilter;
    texture.magFilter = THREE.LinearFilter;
    textures.push(texture);
    const redraw = dark => {
      context.clearRect(0, 0, width, height);
      draw(context, dark, width, height);
      texture.needsUpdate = true;
    };
    themeDrawers.push(redraw);
    redraw(root.dataset.theme === 'dark');
    return texture;
  }

  const paper = physical(0xf5f0e8);
  const paperInset = physical(0xe8ded1, { roughness: 0.28 });
  const ink = physical(0x211b17, { roughness: 0.3 });
  const accent = physical(0xaa482d, { roughness: 0.24, emissive: 0x2c0903, emissiveIntensity: 0.14 });
  const paleGlass = physical(0xf7f0e8, {
    transmission: mobile ? 0.12 : 0.32,
    thickness: 0.38,
    transparent: true,
    opacity: 0.92
  });

  const base = new THREE.Mesh(
    keepGeometry(new THREE.CylinderGeometry(4.35, 4.7, 0.24, mobile ? 28 : 44)),
    paperInset
  );
  base.position.y = -1.05;
  base.receiveShadow = !mobile;
  world.add(base);

  const underlay = new THREE.Mesh(
    keepGeometry(new THREE.CircleGeometry(4.15, mobile ? 28 : 44)),
    keepMaterial(new THREE.MeshBasicMaterial({ color: 0x5b3b2f, transparent: true, opacity: 0.075, depthWrite: false }))
  );
  underlay.rotation.x = -Math.PI / 2;
  underlay.position.y = -0.91;
  world.add(underlay);

  const orbit = new THREE.Mesh(
    keepGeometry(new THREE.TorusGeometry(3.55, 0.018, 4, mobile ? 48 : 80)),
    keepMaterial(new THREE.MeshBasicMaterial({ color: 0xa9432d, transparent: true, opacity: 0.24 }))
  );
  orbit.rotation.x = Math.PI / 2;
  orbit.position.y = -0.88;
  world.add(orbit);

  const core = new THREE.Group();
  core.position.set(0, 0.12, 0.05);
  world.add(core);
  addBox(core, [2.42, 2.05, 1.9], [0, 0, 0], paleGlass, [0, -0.04, 0]);
  addBox(core, [2.1, 0.17, 1.58], [0, 1.09, 0], paper, [0, -0.04, 0]);
  addBox(core, [2.02, 1.42, 0.09], [0, 0.08, 0.995], ink, [0, -0.04, 0]);

  const screenTexture = makeCanvasTexture(1024, 680, (context, dark, width, height) => {
    context.fillStyle = dark ? '#14110f' : '#f7f2eb';
    context.fillRect(0, 0, width, height);
    context.fillStyle = dark ? '#2b2622' : '#e5ddd1';
    context.fillRect(0, 0, width, 82);
    ['#a9432d', '#bf9a5d', '#6a8362'].forEach((color, index) => {
      context.fillStyle = color;
      context.beginPath();
      context.arc(48 + index * 34, 41, 10, 0, Math.PI * 2);
      context.fill();
    });
    context.fillStyle = dark ? '#f5eee5' : '#1b1714';
    context.font = '600 34px system-ui, sans-serif';
    context.fillText('LOFTS / CONNECTED WEB SYSTEM', 54, 154);
    context.fillStyle = '#a9432d';
    context.fillRect(54, 194, 150, 8);
    context.fillStyle = dark ? '#f5eee5' : '#1b1714';
    context.font = '500 64px Georgia, serif';
    context.fillText('Build. Launch.', 54, 306);
    context.fillText('Learn. Grow.', 54, 380);
    context.fillStyle = dark ? '#978d84' : '#746b63';
    context.font = '500 24px system-ui, sans-serif';
    context.fillText('One senior team from strategy through iteration.', 54, 446);
    const bars = [0.78, 0.56, 0.9];
    bars.forEach((value, index) => {
      context.fillStyle = dark ? '#302b27' : '#e1d9ce';
      roundedPath(context, 54, 506 + index * 44, 700, 14, 7);
      context.fill();
      context.fillStyle = index === 2 ? '#a9432d' : (dark ? '#a69b90' : '#776d63');
      roundedPath(context, 54, 506 + index * 44, 700 * value, 14, 7);
      context.fill();
    });
  });
  const screen = new THREE.Mesh(
    keepGeometry(new THREE.PlaneGeometry(1.89, 1.27)),
    keepMaterial(new THREE.MeshBasicMaterial({ map: screenTexture, toneMapped: false }))
  );
  screen.position.set(-0.04, 0.08, 1.047);
  screen.rotation.y = -0.04;
  core.add(screen);

  const spread = compact ? 0.78 : 1;
  const moduleDefinitions = [
    { name: 'COMMERCE', position: [-3.05 * spread, -0.26, 0.72 * spread], color: 0xb65b3c, height: 1.1 },
    { name: 'SAAS', position: [-2.35 * spread, -0.18, -2.2 * spread], color: 0x778d86, height: 1.36 },
    { name: 'WORDPRESS', position: [0.2 * spread, -0.24, -3.1 * spread], color: 0x8d7866, height: 0.98 },
    { name: 'SEO / AEO', position: [2.55 * spread, -0.2, -2.05 * spread], color: 0x617c66, height: 1.24 },
    { name: 'AI AGENTS', position: [2.82 * spread, -0.23, 0.78 * spread], color: 0x9b604b, height: 1.48 }
  ];
  const modules = [];
  const curves = [];
  const signals = [];

  moduleDefinitions.forEach((definition, index) => {
    const module = new THREE.Group();
    module.position.set(...definition.position);
    module.userData.baseY = definition.position[1];
    world.add(module);

    const bodyMaterial = physical(definition.color, {
      emissive: definition.color,
      emissiveIntensity: 0.015,
      roughness: 0.26
    });
    const topMaterial = index % 2 ? paper : paperInset;
    addBox(module, [1.02, definition.height, 0.92], [0, definition.height / 2, 0], bodyMaterial);
    addBox(module, [0.78, 0.1, 0.67], [0, definition.height + 0.055, 0], topMaterial);
    addBox(module, [0.22, 0.22 + index * 0.02, 0.22], [0, definition.height + 0.2, 0], index === 4 ? accent : ink);

    const labelTexture = makeCanvasTexture(600, 176, (context, dark, width, height) => {
      context.fillStyle = dark ? 'rgba(20,17,15,.93)' : 'rgba(250,247,242,.94)';
      roundedPath(context, 6, 6, width - 12, height - 12, 24);
      context.fill();
      context.strokeStyle = dark ? 'rgba(247,240,232,.28)' : 'rgba(26,22,18,.22)';
      context.lineWidth = 3;
      context.stroke();
      context.fillStyle = index === 4 ? '#b95638' : (dark ? '#f7f0e8' : '#1a1612');
      context.font = '600 45px system-ui, sans-serif';
      context.textAlign = 'center';
      context.textBaseline = 'middle';
      context.fillText(definition.name, width / 2, height / 2 + 2);
    });
    const label = new THREE.Mesh(
      keepGeometry(new THREE.PlaneGeometry(1.35, 0.4)),
      keepMaterial(new THREE.MeshBasicMaterial({ map: labelTexture, transparent: true, depthWrite: false, toneMapped: false }))
    );
    label.position.set(0, definition.height + 0.72, 0);
    module.add(label);
    module.userData.label = label;
    module.userData.bodyMaterial = bodyMaterial;
    modules.push(module);

    const start = new THREE.Vector3(...definition.position);
    start.y = -0.76;
    const end = new THREE.Vector3(0, -0.75, 0);
    const control = start.clone().multiplyScalar(0.55);
    control.y = -0.35 - (index % 2) * 0.12;
    const curve = new THREE.QuadraticBezierCurve3(start, control, end);
    curves.push(curve);
    const points = curve.getPoints(mobile ? 18 : 28);
    const line = new THREE.Line(
      keepGeometry(new THREE.BufferGeometry().setFromPoints(points)),
      keepMaterial(new THREE.LineBasicMaterial({ color: 0x6c5547, transparent: true, opacity: 0.27 }))
    );
    world.add(line);

    const signal = new THREE.Mesh(
      keepGeometry(new THREE.SphereGeometry(index === 4 ? 0.075 : 0.055, 8, 6)),
      index === 4 ? accent : paper
    );
    signal.castShadow = !mobile;
    world.add(signal);
    signals.push(signal);
  });

  scene.add(new THREE.HemisphereLight(0xfff9f0, 0x4b4038, 2.15));
  const key = new THREE.DirectionalLight(0xffffff, mobile ? 3.2 : 4.8);
  key.position.set(-3.5, 7, 6);
  key.castShadow = !mobile;
  if (!mobile) {
    key.shadow.mapSize.set(1024, 1024);
    key.shadow.camera.near = 0.1;
    key.shadow.camera.far = 20;
  }
  scene.add(key);
  const rim = new THREE.PointLight(0xb44c2e, 3.4, 18);
  rim.position.set(4.2, 2.6, 4.5);
  scene.add(rim);

  const labels = Array.from(worldShell.querySelectorAll('[data-service-world-label]'));
  const toggle = worldShell.querySelector('[data-service-world-toggle]');
  let paused = false;
  let inView = true;
  let running = true;
  let elapsed = 0;
  let lastTime = performance.now();
  const mouse = { x: 0, y: 0 };
  const targetMouse = { x: 0, y: 0 };

  function syncTheme() {
    const dark = root.dataset.theme === 'dark';
    renderer.toneMappingExposure = dark ? 0.94 : 1.08;
    paper.color.setHex(dark ? 0x6b625b : 0xf5f0e8);
    paperInset.color.setHex(dark ? 0x3a3430 : 0xe8ded1);
    ink.color.setHex(dark ? 0xeee7df : 0x211b17);
    paleGlass.color.setHex(dark ? 0x827a72 : 0xf7f0e8);
    underlay.material.color.setHex(dark ? 0x000000 : 0x5b3b2f);
    orbit.material.color.setHex(dark ? 0xca6d4d : 0xa9432d);
    themeDrawers.forEach(draw => draw(dark));
  }

  function sizeCanvas() {
    const rect = canvasHost.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    renderer.setSize(rect.width, rect.height, false);
    camera.aspect = rect.width / rect.height;
    camera.updateProjectionMatrix();
  }

  function onPointerMove(event) {
    const rect = canvasHost.getBoundingClientRect();
    targetMouse.x = THREE.MathUtils.clamp(((event.clientX - rect.left) / Math.max(1, rect.width)) * 2 - 1, -1, 1);
    targetMouse.y = THREE.MathUtils.clamp(-(((event.clientY - rect.top) / Math.max(1, rect.height)) * 2 - 1), -1, 1);
  }

  function setPaused(nextPaused) {
    paused = nextPaused;
    worldShell.classList.toggle('is-paused', paused);
    toggle.setAttribute('aria-pressed', String(paused));
    toggle.setAttribute('aria-label', paused ? 'Play 3D service animation' : 'Pause 3D service animation');
    toggle.title = paused ? 'Play animation' : 'Pause animation';
  }

  function render(now) {
    if (!running) return;
    window.requestAnimationFrame(render);
    const delta = Math.min(0.05, Math.max(0, (now - lastTime) / 1000));
    lastTime = now;
    if (!inView || document.hidden) return;
    if (paused) {
      renderer.render(scene, camera);
      return;
    }
    elapsed += delta;

    mouse.x += (targetMouse.x - mouse.x) * 0.055;
    mouse.y += (targetMouse.y - mouse.y) * 0.055;
    const scroll = window.loftsLenis ? window.loftsLenis.scroll : window.scrollY;
    const targetRotation = -0.28 + mouse.x * 0.14 + scroll * 0.0002;
    world.rotation.y += (targetRotation - world.rotation.y) * 0.038;
    world.rotation.x += ((-0.08 - mouse.y * 0.045) - world.rotation.x) * 0.038;
    camera.position.x += ((mouse.x * 0.24) - camera.position.x) * 0.025;
    camera.position.y += ((cameraY + mouse.y * 0.12) - camera.position.y) * 0.025;
    camera.lookAt(0, 0.12, 0);

    const activeIndex = Math.floor(elapsed / 2.25) % modules.length;
    modules.forEach((module, index) => {
      const isActive = index === activeIndex;
      const targetScale = isActive ? 1.065 : 1;
      const nextScale = module.scale.x + (targetScale - module.scale.x) * 0.055;
      module.scale.setScalar(nextScale);
      module.position.y = module.userData.baseY + Math.sin(elapsed * 0.72 + index * 1.1) * 0.045;
      module.userData.bodyMaterial.emissiveIntensity += ((isActive ? 0.12 : 0.015) - module.userData.bodyMaterial.emissiveIntensity) * 0.06;
      module.userData.label.lookAt(camera.position);
      if (labels[index]) labels[index].classList.toggle('is-active', isActive);

      const progress = (elapsed * 0.15 + index * 0.17) % 1;
      signals[index].position.copy(curves[index].getPointAt(progress));
      signals[index].scale.setScalar(isActive ? 1.3 : 1);
    });
    core.position.y = 0.12 + Math.sin(elapsed * 0.62) * 0.045;
    core.rotation.y = Math.sin(elapsed * 0.26) * 0.035;
    orbit.rotation.z = elapsed * 0.035;
    renderer.render(scene, camera);
  }

  const resize = debounce(sizeCanvas, 160);
  const observer = new IntersectionObserver(entries => {
    inView = Boolean(entries[0] && entries[0].isIntersecting);
  }, { rootMargin: '180px 0px' });
  const themeObserver = new MutationObserver(syncTheme);

  toggle.addEventListener('click', () => setPaused(!paused));
  window.addEventListener('resize', resize, { passive: true });
  window.addEventListener('pointermove', onPointerMove, { passive: true });
  observer.observe(worldShell);
  themeObserver.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
  syncTheme();
  worldShell.classList.add('is-ready');
  root.classList.add('home-service-world-ready');
  requestAnimationFrame(() => {
    sizeCanvas();
    render(performance.now());
  });

  window.addEventListener('pagehide', () => {
    running = false;
    observer.disconnect();
    themeObserver.disconnect();
    renderer.dispose();
    geometries.forEach(geometry => geometry.dispose());
    materials.forEach(material => material.dispose());
    textures.forEach(texture => texture.dispose());
  }, { once: true });
}

function debounce(callback, wait) {
  let timer = 0;
  return (...args) => {
    window.clearTimeout(timer);
    timer = window.setTimeout(() => callback(...args), wait);
  };
}
