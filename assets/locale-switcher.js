(function () {
  var supported = ['en', 'es', 'fr', 'it'];
  var labels = { en: 'English', es: 'Español', fr: 'Français', it: 'Italiano' };
  var path = window.location.pathname;
  var match = path.match(/^\/(es|fr|it)(\/|$)/);
  var current = match ? match[1] : 'en';
  var base = match ? path.replace(/^\/(es|fr|it)/, '') || '/' : path;
  var route = base;

  if (/^\/services\/website-development-company\.html\/?$/.test(base)) route = '/services/website-development-company.html';
  else if (/^\/free-audit\/?$/.test(base)) route = '/free-audit';
  else if (base !== '/') return;

  if (!document.querySelector('link[href*="locale-pilot.css"]')) {
    var css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = '/assets/locale-pilot.css?v=20260925a';
    document.head.appendChild(css);
  }

  function hrefFor(locale) {
    if (locale === 'en') return route;
    return route === '/' ? '/' + locale : '/' + locale + route;
  }
  function save(locale) {
    try { localStorage.setItem('lofts-locale', locale); } catch (error) {}
  }

  var root = document.createElement('div');
  root.className = 'lofts-language';
  root.setAttribute('data-open', 'false');
  root.innerHTML = '<button class="lofts-language__toggle" type="button" aria-expanded="false" aria-label="Change language">' + current.toUpperCase() + '</button>' +
    '<div class="lofts-language__menu" aria-label="Language options">' + supported.map(function (locale) {
      return '<a href="' + hrefFor(locale) + '" data-locale="' + locale + '"' + (locale === current ? ' aria-current="page"' : '') + '><span>' + labels[locale] + '</span><span>' + locale.toUpperCase() + '</span></a>';
    }).join('') + '</div>';
  document.body.appendChild(root);

  var toggle = root.querySelector('button');
  toggle.addEventListener('click', function () {
    var open = root.getAttribute('data-open') !== 'true';
    root.setAttribute('data-open', String(open));
    toggle.setAttribute('aria-expanded', String(open));
  });
  root.querySelectorAll('[data-locale]').forEach(function (link) {
    link.addEventListener('click', function () { save(link.getAttribute('data-locale')); });
  });
  document.addEventListener('click', function (event) {
    if (!root.contains(event.target)) {
      root.setAttribute('data-open', 'false');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });

  if (current !== 'en') return;
  var saved = null;
  try { saved = localStorage.getItem('lofts-locale'); } catch (error) {}
  var preferred = (navigator.languages && navigator.languages[0] || navigator.language || '').slice(0, 2).toLowerCase();
  if (!saved && supported.indexOf(preferred) > 0) {
    var hint = document.createElement('div');
    hint.className = 'lofts-language__hint';
    hint.innerHTML = '<button class="lofts-language__close" type="button" aria-label="Dismiss">×</button><span>View this page in </span><a href="' + hrefFor(preferred) + '" data-hint-locale="' + preferred + '">' + labels[preferred] + '</a>';
    root.appendChild(hint);
    hint.querySelector('a').addEventListener('click', function () { save(preferred); });
    hint.querySelector('button').addEventListener('click', function () { hint.remove(); });
  }
})();
