/* ─────────────────────────────────────────────────────────────
   Portfolio Admin — single-page tool, localStorage-backed.

   Architecture:
   - On load: fetch portfolio/portfolio.json (the source of truth)
   - Overlay any localStorage edits on top
   - Edits save to localStorage immediately
   - "Export" downloads the merged data as portfolio.json
   - User replaces the file in repo + redeploys to publish
   ───────────────────────────────────────────────────────────── */

// CONFIG — change this passphrase. It's client-side, so this is obscurity, not security.
// To deploy with real auth, see the workflow notes in index.html.
const ADMIN_PASSPHRASE = 'shipfaster';   // ⚠ change me
const STORAGE_KEY = 'adnank-portfolio-admin-v1';
const SESSION_KEY = 'adnank-portfolio-admin-unlocked';
const SHARED_TOKEN_KEY = 'lofts-admin-token';

let state = {
  items: [],
  meta: {},
  modalContext: { mode: 'edit', slug: null },
};

let adminOverview = {
  comments: [],
  submissions: [],
  chats: [],
  stats: {},
};

// ── Auth ────────────────────────────────────────────────────────
function adminLogin() {
  const input = document.getElementById('passwordInput');
  if (input.value === ADMIN_PASSPHRASE) {
    sessionStorage.setItem(SESSION_KEY, '1');
    sessionStorage.setItem(SHARED_TOKEN_KEY, ADMIN_PASSPHRASE);
    showApp();
  } else {
    document.getElementById('loginError').style.display = 'block';
    input.value = '';
    input.focus();
  }
}
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && document.getElementById('loginScreen').style.display !== 'none') {
    adminLogin();
  }
});
document.addEventListener('click', e => {
  const button = e.target.closest('[data-comment-action]');
  if (!button) return;
  moderateComment(button.dataset.commentAction, button.dataset.commentSlug, button.dataset.commentId);
});
function logout() {
  sessionStorage.removeItem(SESSION_KEY);
  sessionStorage.removeItem(SHARED_TOKEN_KEY);
  location.reload();
}
async function showApp() {
  document.getElementById('loginScreen').style.display = 'none';
  document.getElementById('adminApp').style.display = 'block';
  await loadData();
  render();
  loadAdminOverview();
}

// ── Data layer ──────────────────────────────────────────────────
async function loadData() {
  // 1. Fetch the source-of-truth JSON
  try {
    const res = await fetch('/portfolio/portfolio.json?nocache=' + Date.now());
    const json = await res.json();
    state.items = json.items || [];
    state.meta = { version: json.version, lastUpdated: json.lastUpdated, schema: json.schema, categories: json.categories };
  } catch (err) {
    toast('Failed to load portfolio.json: ' + err.message, 'error');
    return;
  }
  // 2. Overlay localStorage edits on top
  try {
    const overlay = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
    if (overlay && overlay.items) {
      state.items = overlay.items;
      toast('Loaded edits from local storage');
    }
  } catch (err) {
    console.warn('Local overlay parse failed:', err);
  }
}

function saveLocal() {
  const payload = {
    version: state.meta.version || 1,
    lastUpdated: new Date().toISOString().slice(0, 10),
    schema: state.meta.schema,
    categories: state.meta.categories,
    items: state.items,
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  state.meta.lastUpdated = payload.lastUpdated;
}

async function reloadFromFile() {
  if (!confirm('Reload from file? Any unsaved local edits will be discarded.')) return;
  localStorage.removeItem(STORAGE_KEY);
  await loadData();
  render();
  toast('Reloaded from portfolio.json');
}

function resetLocal() {
  if (!confirm('Clear all local edits and start over from portfolio.json?')) return;
  localStorage.removeItem(STORAGE_KEY);
  loadData().then(() => { render(); toast('Local edits cleared'); });
}

function exportJSON() {
  const payload = {
    version: state.meta.version || 1,
    lastUpdated: new Date().toISOString().slice(0, 10),
    schema: state.meta.schema || 'Source of truth for portfolio.',
    categories: state.meta.categories || [],
    items: state.items,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'portfolio.json';
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
  toast('Downloaded portfolio.json — replace in /portfolio/ and redeploy', 'success');
}

// ── Rendering ───────────────────────────────────────────────────
function render() {
  // Sort by displayOrder
  state.items.sort((a, b) => (a.displayOrder ?? 999) - (b.displayOrder ?? 999));

  // Stats
  document.getElementById('statTotal').textContent = state.items.length;
  document.getElementById('statFeatured').textContent = state.items.filter(i => i.featured).length;
  document.getElementById('statPublished').textContent = state.items.filter(i => i.published).length;
  document.getElementById('statDrafts').textContent = state.items.filter(i => !i.published).length;
  setText('dashPortfolio', state.items.length);
  setText('dashPortfolioLive', `Live ${state.items.filter(i => i.published).length}`);

  // List
  const list = document.getElementById('itemList');
  // Keep the header row, remove the rest
  const header = list.querySelector('.item-row.header');
  list.innerHTML = '';
  list.appendChild(header);

  state.items.forEach(item => {
    const row = document.createElement('div');
    row.className = 'item-row';
    row.draggable = true;
    row.dataset.slug = item.slug;
    row.innerHTML = `
      ${item.image
        ? `<img class="item-thumb" src="${item.image}" alt="" onerror="this.style.opacity=0.4">`
        : `<div class="item-thumb" style="display: grid; place-items: center; color: var(--muted-2); font-family: var(--font-mono); font-size: 0.7rem;">no img</div>`}
      <div>
        <p class="item-name">${escapeHtml(item.name || '(no name)')}</p>
        <p class="item-tagline">${escapeHtml(item.tagline || '')}</p>
      </div>
      <div class="col-tagline item-meta">${escapeHtml(item.category || '')}</div>
      <div class="col-platform item-meta">#${item.displayOrder ?? '—'}</div>
      <div class="col-badges">
        ${item.featured ? '<span class="badge featured">Featured</span> ' : ''}
        ${item.published ? '<span class="badge published">Live</span>' : '<span class="badge draft">Draft</span>'}
      </div>
      <div class="item-actions">
        <button onclick="visitLive('${item.url}')" ${!item.url ? 'disabled style="opacity:0.4"' : ''}>↗ Live</button>
        <button onclick="openModal('edit', '${item.slug}')">Edit</button>
        <button class="del" onclick="deleteItem('${item.slug}')">Delete</button>
      </div>
    `;
    list.appendChild(row);
  });

  attachDragHandlers();
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

async function loadAdminOverview() {
  setText('dashComments', '—');
  setText('dashPendingComments', 'Loading');
  setText('dashSubmissions', '—');
  setText('dashChats', 'Chats —');
  setText('commentTotal', '—');
  setText('commentPending', '—');
  setText('commentApproved', '—');

  const preview = document.getElementById('commentPreview');
  if (preview) {
    preview.innerHTML = '<p class="ops-note">Loading comments from the protected admin endpoint...</p>';
  }

  try {
    const res = await fetch('/api/admin/data?action=load&nocache=' + Date.now(), {
      headers: { 'x-admin-token': ADMIN_PASSPHRASE },
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'Admin data unavailable.');

    adminOverview = {
      comments: data.comments || [],
      submissions: data.submissions || [],
      chats: data.chats || [],
      stats: data.stats || {},
    };
    renderAdminOverview(adminOverview);
  } catch (err) {
    if (preview) {
      preview.innerHTML = `
        <p class="ops-note">
          Admin data could not load yet. Confirm <code>ADMIN_SECRET</code>, Vercel KV, and the site environment variables before using live moderation here.
        </p>
      `;
    }
    setText('dashPendingComments', 'Check API');
    setText('dashChats', 'Chats —');
    console.warn('Admin overview load failed:', err);
  }
}

function renderAdminOverview(data) {
  const comments = data.comments || [];
  const pending = comments.filter(c => !c.approved);
  const approved = comments.length - pending.length;
  const submissions = Number.isFinite(data.stats.totalSubmissions) ? data.stats.totalSubmissions : data.submissions.length;
  const chats = Number.isFinite(data.stats.totalChats) ? data.stats.totalChats : data.chats.length;

  setText('dashComments', comments.length);
  setText('dashPendingComments', `Pending ${pending.length}`);
  setText('dashSubmissions', submissions);
  setText('dashChats', `Chats ${chats}`);
  setText('commentTotal', comments.length);
  setText('commentPending', pending.length);
  setText('commentApproved', approved);
  renderCommentPreview(comments);
}

function renderCommentPreview(comments) {
  const el = document.getElementById('commentPreview');
  if (!el) return;

  if (!comments.length) {
    el.innerHTML = '<p class="ops-note">No blog comments yet. New comments will appear here when readers submit them.</p>';
    return;
  }

  el.innerHTML = comments.slice(0, 6).map(c => {
    const post = `/blog/${encodeURIComponent(c.slug || '')}.html#comments`;
    const status = c.approved ? 'Approved' : 'Pending';
    const approveButton = c.approved
      ? ''
      : `<button class="small-admin-btn good" data-comment-action="approve" data-comment-slug="${escapeHtml(c.slug)}" data-comment-id="${escapeHtml(c.id)}">Approve</button>`;
    return `
      <article class="comment-preview ${c.approved ? '' : 'pending'}">
        <div class="comment-preview-top">
          <span><strong>${escapeHtml(c.name || 'Anonymous')}</strong> · ${escapeHtml(status)}</span>
          <span>${escapeHtml(formatAdminTime(c.ts))}</span>
        </div>
        <p>${escapeHtml(c.body || '').slice(0, 220)}${(c.body || '').length > 220 ? '...' : ''}</p>
        <div class="comment-preview-actions">
          ${approveButton}
          <a class="small-admin-btn" href="${post}" target="_blank" rel="noopener">View post</a>
          <button class="small-admin-btn danger" data-comment-action="delete" data-comment-slug="${escapeHtml(c.slug)}" data-comment-id="${escapeHtml(c.id)}">Delete</button>
        </div>
      </article>
    `;
  }).join('');
}

function formatAdminTime(ts) {
  const value = Number(ts);
  if (!value) return 'Unknown time';
  const seconds = Math.floor((Date.now() - value) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  return new Date(value).toLocaleDateString();
}

async function moderateComment(type, slug, id) {
  if (!slug || !id) return;
  if (type === 'delete' && !confirm('Delete this comment permanently?')) return;

  try {
    const res = await fetch('/api/admin/data?action=comment', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-admin-token': ADMIN_PASSPHRASE,
      },
      body: JSON.stringify({ type, slug, id }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.ok) throw new Error(data.error || 'Comment action failed.');
    await loadAdminOverview();
    toast(type === 'delete' ? 'Comment deleted' : 'Comment approved', 'success');
  } catch (err) {
    toast(err.message || 'Comment action failed', 'error');
  }
}

function visitLive(url) {
  if (!url) return;
  window.open(url, '_blank', 'noopener');
}

// ── Drag to reorder ────────────────────────────────────────────
let draggedSlug = null;
function attachDragHandlers() {
  document.querySelectorAll('.item-row[draggable=true]').forEach(row => {
    row.addEventListener('dragstart', e => {
      draggedSlug = row.dataset.slug;
      row.classList.add('dragging');
    });
    row.addEventListener('dragend', () => {
      row.classList.remove('dragging');
      document.querySelectorAll('.drop-target').forEach(el => el.classList.remove('drop-target'));
    });
    row.addEventListener('dragover', e => {
      e.preventDefault();
      row.classList.add('drop-target');
    });
    row.addEventListener('dragleave', () => row.classList.remove('drop-target'));
    row.addEventListener('drop', e => {
      e.preventDefault();
      row.classList.remove('drop-target');
      const targetSlug = row.dataset.slug;
      if (!draggedSlug || draggedSlug === targetSlug) return;
      reorderItems(draggedSlug, targetSlug);
    });
  });
}
function reorderItems(fromSlug, toSlug) {
  const fromIdx = state.items.findIndex(i => i.slug === fromSlug);
  const toIdx = state.items.findIndex(i => i.slug === toSlug);
  if (fromIdx === -1 || toIdx === -1) return;
  const [moved] = state.items.splice(fromIdx, 1);
  state.items.splice(toIdx, 0, moved);
  // Renumber
  state.items.forEach((item, i) => { item.displayOrder = i + 1; });
  saveLocal();
  render();
  toast('Reordered — saved locally');
}

// ── Modal ──────────────────────────────────────────────────────
function openModal(mode, slug) {
  state.modalContext = { mode, slug };
  document.getElementById('modalTitle').textContent = mode === 'new' ? 'New project' : 'Edit project';
  const item = mode === 'edit' ? state.items.find(i => i.slug === slug) : null;

  const fld = id => document.getElementById('fld-' + id);
  fld('originalSlug').value = item?.slug || '';
  fld('slug').value = item?.slug || '';
  fld('displayOrder').value = item?.displayOrder ?? (state.items.length + 1);
  fld('name').value = item?.name || '';
  fld('tagline').value = item?.tagline || '';
  fld('summary').value = item?.summary || '';
  fld('url').value = item?.url || '';
  fld('image').value = item?.image || '';
  fld('platform').value = item?.platform || '';
  fld('category').value = item?.category || '';
  fld('stack').value = (item?.stack || []).join(', ');
  fld('metricValue').value = item?.metric?.value || '';
  fld('metricLabel').value = item?.metric?.label || '';
  fld('year').value = item?.year || '';
  fld('role').value = item?.role || '';
  fld('featured').checked = !!item?.featured;
  fld('published').checked = mode === 'new' ? true : !!item?.published;

  document.getElementById('modalOverlay').classList.add('open');
}
function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
}

function saveItem() {
  const fld = id => document.getElementById('fld-' + id).value.trim();
  const fldChecked = id => document.getElementById('fld-' + id).checked;

  const slug = fld('slug');
  if (!slug || !/^[a-z0-9-]+$/.test(slug)) {
    return toast('Slug required, kebab-case only (a-z 0-9 -)', 'error');
  }
  if (!fld('name')) return toast('Name required', 'error');

  const originalSlug = fld('originalSlug');
  // Check for slug conflicts (skip self)
  if (state.items.some(i => i.slug === slug && i.slug !== originalSlug)) {
    return toast(`Slug "${slug}" already exists`, 'error');
  }

  const itemData = {
    slug,
    name: fld('name'),
    tagline: fld('tagline'),
    summary: fld('summary'),
    url: fld('url'),
    image: fld('image'),
    platform: fld('platform'),
    category: fld('category'),
    stack: fld('stack').split(',').map(s => s.trim()).filter(Boolean),
    metric: { value: fld('metricValue'), label: fld('metricLabel') },
    year: fld('year'),
    role: fld('role'),
    featured: fldChecked('featured'),
    published: fldChecked('published'),
    displayOrder: parseInt(fld('displayOrder')) || (state.items.length + 1),
  };

  if (state.modalContext.mode === 'new') {
    state.items.push(itemData);
  } else {
    const idx = state.items.findIndex(i => i.slug === originalSlug);
    if (idx >= 0) state.items[idx] = itemData;
  }

  saveLocal();
  render();
  closeModal();
  toast(state.modalContext.mode === 'new' ? `Added "${itemData.name}"` : `Saved "${itemData.name}"`, 'success');
}

function deleteItem(slug) {
  const item = state.items.find(i => i.slug === slug);
  if (!item) return;
  if (!confirm(`Delete "${item.name}"? This only affects local state — export to publish.`)) return;
  state.items = state.items.filter(i => i.slug !== slug);
  saveLocal();
  render();
  toast(`Deleted "${item.name}"`);
}

// ── Toast ──────────────────────────────────────────────────────
let toastTimer = null;
function toast(message, kind) {
  const el = document.getElementById('toast');
  el.textContent = message;
  el.className = 'toast show ' + (kind || '');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 3500);
}

// ── Bootstrap ──────────────────────────────────────────────────
// Override the inline stub with the full version once this script loads
window.adminLogin = adminLogin;
window.logout = logout;
window.openModal = openModal;
window.closeModal = closeModal;
window.saveItem = saveItem;
window.deleteItem = deleteItem;
window.visitLive = visitLive;
window.exportJSON = exportJSON;
window.reloadFromFile = reloadFromFile;
window.resetLocal = resetLocal;
window.loadAdminOverview = loadAdminOverview;
window.moderateComment = moderateComment;

// Auto-unlock if session is active
if (sessionStorage.getItem(SESSION_KEY) === '1') {
  sessionStorage.setItem(SHARED_TOKEN_KEY, ADMIN_PASSPHRASE);
  document.getElementById('loginScreen').style.display = 'none';
  document.getElementById('adminApp').style.display = 'block';
  loadData().then(() => {
    render();
    loadAdminOverview();
  });
}
