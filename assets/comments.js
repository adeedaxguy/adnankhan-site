/* Blog comments — loads + posts to /api/comments. High-end, no dependencies.
   Pairs with the markup injected by scripts/seo_engine.py and styles in
   assets/styles.css. Spam protection is enforced server-side; this layer adds
   a honeypot + time-trap + light client validation. */
(function () {
  var root = document.getElementById('comments');
  if (!root) return;
  var slug = root.getAttribute('data-slug');
  if (!slug) return;

  var list   = root.querySelector('[data-list]');
  var empty  = root.querySelector('[data-empty]');
  var countEl = root.querySelector('[data-count]');
  var form   = root.querySelector('[data-form]');
  var status = root.querySelector('[data-status]');
  var submit = form ? form.querySelector('.cf-submit') : null;
  var loadedAt = Date.now();

  function esc(s) {
    var d = document.createElement('div'); d.textContent = s == null ? '' : String(s);
    return d.innerHTML;
  }
  function initials(name) {
    var parts = String(name || '?').trim().split(/\s+/);
    var s = (parts[0] ? parts[0][0] : '') + (parts[1] ? parts[1][0] : '');
    return (s || '?').toUpperCase();
  }
  function hue(name) { // deterministic accent tint per name
    var h = 0; name = String(name || '');
    for (var i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
    return h;
  }
  function ago(ts) {
    var s = Math.max(1, Math.floor((Date.now() - ts) / 1000));
    if (s < 60) return 'just now';
    var m = Math.floor(s / 60); if (m < 60) return m + (m === 1 ? ' minute ago' : ' minutes ago');
    var h = Math.floor(m / 60); if (h < 24) return h + (h === 1 ? ' hour ago' : ' hours ago');
    var d = Math.floor(h / 24); if (d < 30) return d + (d === 1 ? ' day ago' : ' days ago');
    return new Date(ts).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  }
  function node(c) {
    var li = document.createElement('li');
    li.className = 'comment';
    li.innerHTML =
      '<div class="comment-avatar" style="--h:' + hue(c.name) + '">' + esc(initials(c.name)) + '</div>' +
      '<div class="comment-main">' +
        '<div class="comment-meta"><span class="comment-name">' + esc(c.name) + '</span>' +
        '<time class="comment-time">' + esc(ago(c.ts)) + '</time></div>' +
        '<div class="comment-text">' + esc(c.body).replace(/\n/g, '<br>') + '</div>' +
      '</div>';
    return li;
  }
  function setCount(n) {
    if (countEl) countEl.textContent = n === 0 ? '' : '· ' + n;
    if (empty) empty.hidden = n !== 0;
  }

  // Load existing comments
  fetch('/api/comments?slug=' + encodeURIComponent(slug), { headers: { 'accept': 'application/json' } })
    .then(function (r) { return r.json(); })
    .then(function (d) {
      var items = (d && d.comments) || [];
      list.innerHTML = '';
      items.forEach(function (c) { list.appendChild(node(c)); });
      setCount(items.length);
    })
    .catch(function () { setCount(0); });

  if (!form) return;

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var name = form.name.value.trim();
    var body = form.body.value.trim();
    if (name.length < 2) { say('Please add your name.', true); form.name.focus(); return; }
    if (body.length < 2) { say('Please write a comment.', true); form.body.focus(); return; }

    submit.disabled = true; submit.classList.add('is-loading');
    say('Posting…', false);

    fetch('/api/comments', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        slug: slug,
        name: name,
        email: form.email ? form.email.value.trim() : '',
        body: body,
        hp_url: form.hp_url ? form.hp_url.value : '',
        t: Date.now() - loadedAt,
      }),
    })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        var j = res.j || {};
        if (j.ok && j.comment) {
          if (empty) empty.hidden = true;
          var n = node(j.comment); n.classList.add('comment--new');
          list.insertBefore(n, list.firstChild);
          setCount(list.children.length);
          form.reset();
          say(j.message || 'Posted — thanks!', false);
        } else if (j.ok && j.pending) {
          form.reset();
          say(j.message || 'Thanks — your comment will appear once approved.', false);
        } else {
          say(j.message || 'Something went wrong. Please try again.', true);
        }
      })
      .catch(function () { say('Network hiccup — please try again.', true); })
      .then(function () { submit.disabled = false; submit.classList.remove('is-loading'); });
  });

  function say(msg, isErr) {
    if (!status) return;
    status.textContent = msg;
    status.classList.toggle('cf-note--err', !!isErr);
  }
})();
