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

let state = {
  items: [],
  meta: {},
  modalContext: { mode: 'edit', slug: null },
};

// ── Auth ────────────────────────────────────────────────────────
function adminLogin() {
  const input = document.getElementById('passwordInput');
  if (input.value === ADMIN_PASSPHRASE) {
    sessionStorage.setItem(SESSION_KEY, '1');
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
function logout() {
  sessionStorage.removeItem(SESSION_KEY);
  location.reload();
}
async function showApp() {
  document.getElementById('loginScreen').style.display = 'none';
  document.getElementById('adminApp').style.display = 'block';
  await loadData();
  render();
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

// Auto-unlock if session is active
if (sessionStorage.getItem(SESSION_KEY) === '1') {
  document.getElementById('loginScreen').style.display = 'none';
  document.getElementById('adminApp').style.display = 'block';
  loadData().then(render);
}
