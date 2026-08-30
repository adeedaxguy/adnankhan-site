document.documentElement.dataset.theme = 'light';
document.documentElement.style.colorScheme = 'light';

for (const image of document.images) {
  if (!image.hasAttribute('decoding')) image.decoding = 'async';
}

for (const year of document.querySelectorAll('[data-year]')) {
  year.textContent = new Date().getFullYear();
}

const fieldDots = document.querySelector('.rb-field-dots');
if (fieldDots) {
  const field = fieldDots.closest('svg');
  const flowLines = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  flowLines.setAttribute('class', 'rb-generated-flow');
  for (let row = 0; row < 10; row++) {
    const y = 118 + row * 49;
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M-24 ${y}C118 ${y - 76} 236 ${y + 88} 390 ${y}S646 ${y - 70} 794 ${y + 12}`);
    flowLines.append(path);
  }
  field?.insertBefore(flowLines, fieldDots);
  for (let index = 0; index < 84; index++) {
    const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    const x = 22 + (index % 14) * 56;
    const y = 108 + Math.floor(index / 14) * 84 + Math.sin(index * .72) * 22;
    dot.setAttribute('cx', x);
    dot.setAttribute('cy', y);
    dot.setAttribute('r', index % 5 === 0 ? 2.6 : 1.7);
    fieldDots.append(dot);
  }
}

if (!document.body.classList.contains('rebuild-home') && !document.querySelector('.rb-child-header')) {
  const childHeader = document.createElement('header');
  childHeader.className = 'rb-header rb-child-header';
  childHeader.innerHTML = `
    <a class="rb-logo" href="/" aria-label="Adnan Khan portfolio home">
      <span class="rb-logo-mark" aria-hidden="true"><i></i><i></i><i></i></span>
      <span>ADNAN KHAN</span>
    </a>
    <nav class="rb-nav" aria-label="Primary navigation">
      <a href="/portfolio">Work</a>
      <a href="/services">Expertise</a>
      <a href="/about.html">About</a>
      <a href="/process">Process</a>
      <a href="/reviews">Reviews</a>
    </nav>
    <a class="rb-button rb-button--primary rb-header-cta" href="https://www.upwork.com/freelancers/wordpressandshopifydeveloper" target="_blank" rel="noopener noreferrer">Upwork profile <span aria-hidden="true">↗</span></a>
    <button class="rb-menu" type="button" aria-expanded="false" aria-controls="rb-mobile-nav" aria-label="Open navigation">
      <span></span><span></span>
    </button>
    <nav class="rb-mobile-nav" id="rb-mobile-nav" aria-label="Mobile navigation" hidden>
      <a href="/portfolio">Work</a><a href="/services">Expertise</a><a href="/about.html">About</a><a href="/process">Process</a><a href="/reviews">Reviews</a><a href="https://www.upwork.com/freelancers/wordpressandshopifydeveloper" target="_blank" rel="noopener noreferrer">View Upwork profile</a>
    </nav>`;
  document.body.prepend(childHeader);
}

const menu = document.querySelector('.rb-menu');
const mobileNav = document.querySelector('.rb-mobile-nav');

const currentPath = location.pathname.replace(/\/(?:index\.html)?$/, '') || '/';

const commercialInnerRoute = /^(?:\/services(?:\/|$)|\/portfolio\/|\/websites\/|\/locations\/|\/work\/)/.test(currentPath);
const firstInnerSection = document.querySelector('body:not(.rebuild-home) main > section:first-child');
const firstInnerContainer = firstInnerSection?.querySelector(':scope > .container');

if (commercialInnerRoute && firstInnerSection && firstInnerContainer && !firstInnerContainer.querySelector('.rb-inner-visual')) {
  const portfolioCase = /^\/portfolio\//.test(currentPath);
  const pageTitle = firstInnerContainer.querySelector('h1')?.textContent.trim().replace(/\s+/g, ' ') || 'Selected work';
  const routeKey = currentPath.toLowerCase();
  const ogImage = document.querySelector('meta[property="og:image"]')?.content || '';
  let previewImage = '/assets/work/portfolio-hd/americanreinsurance.webp';

  if (portfolioCase && /\/assets\/work\/portfolio-hd\//.test(ogImage)) {
    previewImage = ogImage;
  } else if (/shopify|woocommerce|conversion|landing|ecommerce|market-my/.test(routeKey)) {
    previewImage = '/assets/work/portfolio-hd/jamaicancoffeeclub.webp';
  } else if (/custom-app|ai-|saas|automation/.test(routeKey)) {
    previewImage = '/assets/work/portfolio-hd/coap-online.webp';
  } else if (/\/services$/.test(routeKey)) {
    previewImage = '/assets/work/portfolio-hd/americangulf.webp';
  } else if (/\/websites\/|\/locations\//.test(routeKey)) {
    const routeImages = [
      '/assets/work/portfolio-hd/americanreinsurance.webp',
      '/assets/work/portfolio-hd/coap-online.webp',
      '/assets/work/portfolio-hd/mercanto.webp'
    ];
    previewImage = routeImages[routeKey.length % routeImages.length];
  }

  const innerCopy = firstInnerContainer.querySelector(':scope > [data-reveal]:has(h1), :scope > div:has(h1)');
  innerCopy?.classList.add('rb-inner-copy');
  for (const sibling of firstInnerContainer.querySelectorAll(':scope > [data-reveal]:not(.rb-inner-copy)')) {
    sibling.classList.add('rb-inner-proof');
  }

  const visual = document.createElement('figure');
  visual.className = 'rb-inner-visual';
  visual.innerHTML = `
    <span class="rb-inner-visual__frame">
      <span class="rb-inner-visual__chrome" aria-hidden="true"><i></i><i></i><i></i></span>
      <img src="${previewImage}" width="2200" height="1375" loading="eager" decoding="async" fetchpriority="high" alt="" />
    </span>
    <figcaption><span>${portfolioCase ? 'Project preview' : 'Selected portfolio evidence'}</span><strong></strong></figcaption>`;
  visual.querySelector('strong').textContent = portfolioCase ? pageTitle : 'Strategy, interface and build quality';
  visual.setAttribute('aria-label', portfolioCase ? `${pageTitle} project preview` : 'Selected project preview from Adnan Khan’s portfolio');
  firstInnerSection.classList.add('rb-split-inner-hero');
  if (/^\/(?:websites|locations)\//.test(currentPath)) firstInnerSection.classList.add('rb-directory-inner-hero');
  firstInnerContainer.classList.add('rb-inner-split');
  firstInnerContainer.append(visual);
}

for (const link of document.querySelectorAll('.rb-nav a, .rb-mobile-nav a')) {
  const linkPath = new URL(link.href, location.href).pathname.replace(/\/(?:index\.html)?$/, '') || '/';
  const matchesSection = ['/portfolio', '/services', '/reviews'].includes(linkPath) && currentPath.startsWith(`${linkPath}/`);
  if (linkPath === currentPath || matchesSection) link.setAttribute('aria-current', 'page');
}

function setMobileMenu(open, returnFocus = false) {
  if (!menu || !mobileNav) return;
  menu.setAttribute('aria-expanded', String(open));
  menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  mobileNav.hidden = !open;
  if (open) mobileNav.querySelector('a')?.focus();
  if (!open && returnFocus) menu.focus();
}

menu?.addEventListener('click', () => {
  setMobileMenu(menu.getAttribute('aria-expanded') !== 'true');
});

mobileNav?.addEventListener('click', (event) => {
  if (!event.target.closest('a')) return;
  setMobileMenu(false);
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') setMobileMenu(false, true);
});

document.addEventListener('pointerdown', (event) => {
  if (menu?.getAttribute('aria-expanded') !== 'true') return;
  if (menu.contains(event.target) || mobileNav?.contains(event.target)) return;
  setMobileMenu(false);
});

window.addEventListener('resize', () => {
  if (innerWidth > 900 && menu?.getAttribute('aria-expanded') === 'true') setMobileMenu(false);
}, { passive: true });

const revealTargets = document.querySelectorAll('.rebuild-home .rb-section-heading, .rebuild-home .rb-project, .rebuild-home .rb-founders-copy, .rebuild-home .rb-founder-map, .rebuild-home .rb-service-list a, .rebuild-home .rb-process li, .rebuild-home blockquote, .rebuild-home .rb-upwork-panel');
for (const target of revealTargets) target.dataset.rbReveal = '';

if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    }
  }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
  for (const target of revealTargets) observer.observe(target);
} else {
  for (const target of revealTargets) target.classList.add('is-visible');
}

function initProjectBrowser() {
  const browser = document.querySelector('[data-project-browser]');
  if (!browser) return;
  const grid = browser.querySelector('[data-project-grid]');
  const data = browser.querySelector('[data-project-data]');
  let projects = [];
  try {
    projects = JSON.parse(data?.textContent || '[]');
  } catch (error) {
    console.warn('Project data could not be read.', error);
  }
  if (!projects.length) return;
  const search = browser.querySelector('[data-project-search]');
  const platform = browser.querySelector('[data-project-platform]');
  const skill = browser.querySelector('[data-project-skill]');
  const status = browser.querySelector('[data-project-status]');
  const reset = browser.querySelector('[data-project-reset]');
  const empty = browser.querySelector('[data-project-empty]');
  const emptyReset = browser.querySelector('[data-project-empty-reset]');
  const pagination = browser.querySelector('[data-project-pagination]');
  const pageSize = 12;
  let page = 1;

  const params = new URLSearchParams(location.search);
  const hasOption = (select, value) => [...select.options].some(option => option.value === value);
  if (hasOption(platform, params.get('platform') || '')) platform.value = params.get('platform') || '';
  if (hasOption(skill, params.get('skill') || '')) skill.value = params.get('skill') || '';
  search.value = params.get('q') || '';
  page = Math.max(1, Number.parseInt(params.get('page') || '1', 10) || 1);

  function matches(project) {
    const query = search.value.trim().toLowerCase();
    return (!query || project.search.includes(query))
      && (!platform.value || project.platforms.includes(platform.value))
      && (!skill.value || project.skills.includes(skill.value));
  }

  function createProjectCard(project) {
    const card = document.createElement('a');
    card.className = 'seo-project-card';
    card.href = project.href;
    card.dataset.projectCard = '';
    card.dataset.platforms = project.platforms.join(' ');
    card.dataset.skills = project.skills.join(' ');
    card.dataset.search = project.search;

    if (project.image) {
      const image = document.createElement('img');
      if (project.previewImage) image.className = 'seo-project-card__image--preview';
      image.src = project.image;
      image.alt = project.imageAlt;
      image.width = 1200;
      image.height = 760;
      image.loading = 'eager';
      image.decoding = 'async';
      card.append(image);
    } else {
      const visual = document.createElement('span');
      visual.className = 'seo-project-card__visual';
      visual.setAttribute('aria-hidden', 'true');
      visual.append(document.createElement('i'), document.createElement('i'), document.createElement('i'));
      const initials = document.createElement('b');
      initials.textContent = project.initials;
      const platformLabel = document.createElement('em');
      platformLabel.textContent = project.primaryPlatform;
      visual.append(initials, platformLabel);
      card.append(visual);
    }

    const name = document.createElement('strong');
    name.textContent = project.name;
    const meta = document.createElement('span');
    meta.className = 'seo-project-card__meta';
    const platformName = document.createElement('span');
    platformName.textContent = project.primaryPlatform;
    const skillName = document.createElement('span');
    skillName.textContent = project.secondarySkill;
    meta.append(platformName, skillName);
    const role = document.createElement('small');
    role.textContent = project.role;
    card.append(name, meta, role);
    return card;
  }

  function updateUrl() {
    const url = new URL(location.href);
    const values = { q: search.value.trim(), platform: platform.value, skill: skill.value, page: page > 1 ? String(page) : '' };
    for (const [key, value] of Object.entries(values)) value ? url.searchParams.set(key, value) : url.searchParams.delete(key);
    url.hash = 'archive-all';
    history.replaceState(null, '', url);
  }

  function paginationMarkup(pageCount) {
    const pageNumbers = pageCount <= 7
      ? Array.from({ length: pageCount }, (_, index) => index + 1)
      : [...new Set([1, page - 1, page, page + 1, pageCount])].filter(value => value > 0 && value <= pageCount).sort((a, b) => a - b);
    let previous = 0;
    const numbered = pageNumbers.map((value) => {
      const gap = value - previous > 1 ? '<span aria-hidden="true">…</span>' : '';
      previous = value;
      return `${gap}<button type="button" data-page="${value}" aria-label="Project page ${value}"${page === value ? ' aria-current="page"' : ''}>${value}</button>`;
    }).join('');
    return `<button type="button" data-page="${page - 1}" aria-label="Previous project page"${page === 1 ? ' disabled' : ''}>Previous</button>${numbered}<button type="button" data-page="${page + 1}" aria-label="Next project page"${page === pageCount ? ' disabled' : ''}>Next</button>`;
  }

  function render({ updateLocation = true, scroll = false } = {}) {
    const filtered = projects.filter(matches);
    const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
    page = Math.min(page, pageCount);
    const start = (page - 1) * pageSize;
    const end = Math.min(start + pageSize, filtered.length);
    grid.replaceChildren(...filtered.slice(start, end).map(createProjectCard));
    status.textContent = filtered.length ? `Showing ${start + 1}–${end} of ${filtered.length} projects` : 'No matching projects';
    reset.hidden = !search.value && !platform.value && !skill.value;
    empty.hidden = filtered.length > 0;
    pagination.hidden = filtered.length === 0 || pageCount <= 1;
    pagination.innerHTML = filtered.length && pageCount > 1
      ? paginationMarkup(pageCount)
      : '';
    if (updateLocation) updateUrl();
    if (scroll) browser.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  function resetFilters() {
    search.value = '';
    platform.value = '';
    skill.value = '';
    page = 1;
    render();
    search.focus();
  }

  search.addEventListener('input', () => { page = 1; render(); });
  platform.addEventListener('change', () => { page = 1; render(); });
  skill.addEventListener('change', () => { page = 1; render(); });
  reset.addEventListener('click', resetFilters);
  emptyReset.addEventListener('click', resetFilters);
  pagination.addEventListener('click', (event) => {
    const button = event.target.closest('[data-page]');
    if (!button || button.disabled) return;
    page = Number(button.dataset.page);
    render({ scroll: true });
  });
  render({ updateLocation: false });
}

initProjectBrowser();

function initExpertiseCore() {
  const story = document.querySelector('[data-core-story]');
  const canvas = story?.querySelector('[data-core-canvas]');
  const visual = story?.querySelector('[data-core-visual]');
  const readout = story?.querySelector('[data-core-readout]');
  const lockup = story?.querySelector('[data-core-lockup]');
  const steps = [...(story?.querySelectorAll('[data-core-step]') || [])];
  const context = canvas?.getContext('2d', { alpha: true });
  if (!story || !canvas || !visual || !context) {
    story?.classList.add('is-static');
    return;
  }

  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const compactLayout = matchMedia('(max-width: 900px)');
  const labels = ['SIGNAL ACQUISITION', 'SYSTEM COORDINATION', 'DELIVERY RESOLVED'];
  const nodeLayout = [
    [-.5, -.28], [-.08, -.42], [.39, -.28], [.54, .08], [.2, .38], [-.28, .39], [-.54, .08]
  ];
  const pointCount = 196;
  const particles = [];
  let seed = 7831;
  const random = () => {
    seed |= 0;
    seed = seed + 0x6D2B79F5 | 0;
    let value = Math.imul(seed ^ seed >>> 15, 1 | seed);
    value = value + Math.imul(value ^ value >>> 7, 61 | value) ^ value;
    return ((value ^ value >>> 14) >>> 0) / 4294967296;
  };

  function markTarget(index) {
    const group = index % 7;
    if (group < 3) {
      const angle = Math.PI * (.52 + 1.02 * ((index / 7) % 1));
      const width = .19 + (group - 1) * .018;
      return [-.12 + Math.cos(angle) * width, Math.sin(angle) * .28, 0];
    }
    if (group < 5) {
      const column = (index * 7) % 11;
      const row = (index * 13) % 11;
      return [.17 + (column / 10 - .5) * .2, -.18 + (row / 10 - .5) * .2, 0];
    }
    const angle = index * 2.399963;
    const radius = .1 * Math.sqrt(((index * 17) % 29) / 28);
    return [.17 + Math.cos(angle) * radius, .17 + Math.sin(angle) * radius, 0];
  }

  for (let index = 0; index < pointCount; index++) {
    const theta = index * 2.399963;
    const latitude = Math.acos(1 - 2 * ((index + .5) / pointCount));
    const sourceRadius = .34 + random() * .42;
    const node = index % nodeLayout.length;
    const localAngle = theta * 1.7;
    const localRadius = .025 + random() * .075;
    particles.push({
      source: [
        Math.cos(theta) * Math.sin(latitude) * sourceRadius,
        Math.cos(latitude) * sourceRadius * .75,
        Math.sin(theta) * Math.sin(latitude) * sourceRadius
      ],
      system: [
        nodeLayout[node][0] + Math.cos(localAngle) * localRadius,
        nodeLayout[node][1] + Math.sin(localAngle) * localRadius,
        (random() - .5) * .17
      ],
      mark: markTarget(index),
      node,
      size: .62 + random() * 1.35,
      tone: random() > .64 ? 1 : 0
    });
  }

  let width = 1;
  let height = 1;
  let targetProgress = compactLayout.matches || reducedMotion.matches ? 1 : 0;
  let progress = targetProgress;
  let pointerX = 0;
  let pointerY = 0;
  let targetPointerX = 0;
  let targetPointerY = 0;
  let frame = 0;
  let visible = true;
  let lastTime = 0;

  const clamp = (value, minimum = 0, maximum = 1) => Math.min(maximum, Math.max(minimum, value));
  const smooth = (from, to, value) => {
    const unit = clamp((value - from) / (to - from));
    return unit * unit * (3 - 2 * unit);
  };
  const mix = (from, to, amount) => from + (to - from) * amount;

  function resize() {
    const bounds = canvas.getBoundingClientRect();
    const ratio = Math.min(devicePixelRatio || 1, 1.75);
    width = Math.max(1, bounds.width);
    height = Math.max(1, bounds.height);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    draw(performance.now());
  }

  function updateProgress() {
    if (compactLayout.matches || reducedMotion.matches) {
      targetProgress = 1;
      return;
    }
    const bounds = story.getBoundingClientRect();
    const distance = Math.max(1, bounds.height - innerHeight);
    targetProgress = clamp(-bounds.top / distance);
  }

  function project(point, rotation, tilt, scale) {
    const cosY = Math.cos(rotation);
    const sinY = Math.sin(rotation);
    const x1 = point[0] * cosY - point[2] * sinY;
    const z1 = point[0] * sinY + point[2] * cosY;
    const cosX = Math.cos(tilt);
    const sinX = Math.sin(tilt);
    const y1 = point[1] * cosX - z1 * sinX;
    const z2 = point[1] * sinX + z1 * cosX;
    const depth = 1 / (1.28 + z2 * .38);
    return [width / 2 + x1 * scale * depth, height / 2 + y1 * scale * depth, depth, z2];
  }

  function draw(time) {
    context.clearRect(0, 0, width, height);
    const systemAmount = smooth(.13, .47, progress);
    const resolveAmount = smooth(.59, .93, progress);
    const systemVisibility = smooth(.16, .32, progress) * (1 - smooth(.7, .91, progress));
    const resolveVisibility = smooth(.79, .96, progress);
    const scale = Math.min(width, height) * .73;
    const rotation = (1 - resolveAmount) * (time * .000055 + pointerX * .17);
    const tilt = (1 - resolveAmount) * (-.13 + pointerY * .11);

    context.save();
    context.translate(.5, .5);
    context.strokeStyle = `rgba(131,150,188,${.07 + systemVisibility * .06})`;
    context.lineWidth = 1;
    context.beginPath();
    context.moveTo(width * .12, height / 2);
    context.lineTo(width * .88, height / 2);
    context.moveTo(width / 2, height * .08);
    context.lineTo(width / 2, height * .92);
    context.stroke();

    const projectedNodes = nodeLayout.map(([x, y]) => project([x, y, 0], rotation, tilt, scale));
    if (systemVisibility > .01) {
      context.lineWidth = 1;
      for (let index = 0; index < projectedNodes.length; index++) {
        const current = projectedNodes[index];
        const next = projectedNodes[(index + 1) % projectedNodes.length];
        context.strokeStyle = `rgba(${index % 2 ? '98,78,222' : '23,212,195'},${systemVisibility * .34})`;
        context.beginPath();
        context.moveTo(current[0], current[1]);
        context.quadraticCurveTo(width / 2, height / 2, next[0], next[1]);
        context.stroke();
      }
    }

    const points = [];
    for (const particle of particles) {
      const systemPoint = [
        mix(particle.source[0], particle.system[0], systemAmount),
        mix(particle.source[1], particle.system[1], systemAmount),
        mix(particle.source[2], particle.system[2], systemAmount)
      ];
      const finalPoint = [
        mix(systemPoint[0], particle.mark[0], resolveAmount),
        mix(systemPoint[1], particle.mark[1], resolveAmount),
        mix(systemPoint[2], particle.mark[2], resolveAmount)
      ];
      const projected = project(finalPoint, rotation, tilt, scale);
      points.push([projected, particle]);
    }
    points.sort((a, b) => a[0][3] - b[0][3]);

    for (const [point, particle] of points) {
      const alpha = clamp(.28 + point[2] * .36 + resolveVisibility * .16);
      const radius = particle.size * point[2] * (1 + resolveVisibility * .22);
      context.fillStyle = particle.tone
        ? `rgba(119,96,235,${alpha})`
        : `rgba(37,224,207,${alpha})`;
      context.beginPath();
      context.arc(point[0], point[1], radius, 0, Math.PI * 2);
      context.fill();
    }

    if (systemVisibility > .04) {
      projectedNodes.forEach((point, index) => {
        const radius = 7 + systemVisibility * 6;
        context.strokeStyle = index % 2 ? `rgba(119,96,235,${systemVisibility})` : `rgba(37,224,207,${systemVisibility})`;
        context.fillStyle = 'rgba(17,24,44,.88)';
        context.lineWidth = 1.5;
        context.beginPath();
        context.arc(point[0], point[1], radius, 0, Math.PI * 2);
        context.fill();
        context.stroke();
        context.fillStyle = `rgba(232,237,248,${systemVisibility * .75})`;
        context.beginPath();
        context.arc(point[0], point[1], 1.6, 0, Math.PI * 2);
        context.fill();
      });
    }
    context.restore();

    const activeStep = progress < .34 ? 0 : progress < .72 ? 1 : 2;
    steps.forEach((step, index) => step.classList.toggle('is-active', compactLayout.matches || index === activeStep));
    if (readout) readout.textContent = labels[activeStep];
    lockup?.classList.toggle('is-resolved', progress > .88 || compactLayout.matches || reducedMotion.matches);
  }

  function animate(time) {
    frame = 0;
    if (!visible || document.hidden) return;
    const staticMode = compactLayout.matches || reducedMotion.matches;
    progress += (targetProgress - progress) * (staticMode ? 1 : .105);
    pointerX += (targetPointerX - pointerX) * .08;
    pointerY += (targetPointerY - pointerY) * .08;
    if (!lastTime || time - lastTime > 14) {
      draw(time);
      lastTime = time;
    }
    if (!staticMode || Math.abs(targetProgress - progress) > .001) frame = requestAnimationFrame(animate);
  }

  function requestDraw() {
    if (!frame && visible && !document.hidden) frame = requestAnimationFrame(animate);
  }

  function setStaticState() {
    story.classList.toggle('is-static', compactLayout.matches || reducedMotion.matches);
    updateProgress();
    progress = targetProgress;
    resize();
    requestDraw();
  }

  addEventListener('scroll', () => {
    updateProgress();
    requestDraw();
  }, { passive: true });
  visual.addEventListener('pointermove', (event) => {
    if (compactLayout.matches || reducedMotion.matches) return;
    const bounds = visual.getBoundingClientRect();
    targetPointerX = clamp((event.clientX - bounds.left) / bounds.width, 0, 1) * 2 - 1;
    targetPointerY = clamp((event.clientY - bounds.top) / bounds.height, 0, 1) * 2 - 1;
    requestDraw();
  }, { passive: true });
  visual.addEventListener('pointerleave', () => {
    targetPointerX = 0;
    targetPointerY = 0;
  }, { passive: true });
  document.addEventListener('visibilitychange', requestDraw);
  new ResizeObserver(resize).observe(canvas);
  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    if (visible) requestDraw();
    else if (frame) {
      cancelAnimationFrame(frame);
      frame = 0;
    }
  }, { rootMargin: '25% 0px' }).observe(story);
  reducedMotion.addEventListener?.('change', setStaticState);
  compactLayout.addEventListener?.('change', setStaticState);
  setStaticState();
}

initExpertiseCore();
