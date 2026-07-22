const AGENCY_API = '/api/admin/agency';
const AGENCY_TOKEN_KEY = 'ads-command-token';
const SHARED_TOKEN_KEY = 'lofts-admin-token';
const STAGE_LABELS = {
  new: 'New',
  contacted: 'Contacted',
  qualified: 'Qualified',
  proposal: 'Proposal',
  won: 'Won',
  lost: 'Lost',
};

const agencyState = {
  token: '',
  data: null,
  range: '30',
  currentView: 'overview',
  selectedLeadId: '',
  draggedLeadId: '',
  zohoNoticeShown: false,
  emailLeadContext: null,
};

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}

function safeUrl(value) {
  try {
    const url = new URL(String(value || ''));
    return ['http:', 'https:', 'mailto:', 'tel:'].includes(url.protocol) ? url.href : '';
  } catch { return ''; }
}

function formatNumber(value, digits = 0) {
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: digits }).format(Number(value) || 0);
}

function currencySymbol(currency) {
  return ({ USD: '$', GBP: '£', EUR: '€', AUD: 'A$' })[currency] || `${currency || 'USD'} `;
}

function money(value, digits = 0) {
  const currency = agencyState.data?.project?.currency || 'USD';
  return `${currencySymbol(currency)}${formatNumber(value, digits)}`;
}

function percentage(value, digits = 1) {
  return `${formatNumber(value, digits)}%`;
}

function titleCase(value) {
  return String(value || '').replace(/[_-]+/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
}

function initials(value) {
  return String(value || '?').trim().split(/\s+/).slice(0, 2).map(part => part.charAt(0)).join('').toUpperCase() || '?';
}

function relativeTime(timestamp) {
  const value = Number(timestamp);
  if (!value) return 'Unknown';
  const minutes = Math.floor((Date.now() - value) / 60000);
  if (minutes < 1) return 'Now';
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d`;
  return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function fullDate(timestamp) {
  if (!timestamp) return 'Not recorded';
  return new Date(Number(timestamp)).toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' });
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
}

function refreshIcons() {
  if (window.lucide) window.lucide.createIcons({ attrs: { 'aria-hidden': 'true' } });
}

function showToast(message) {
  const toast = document.getElementById('agency-toast');
  toast.textContent = message;
  toast.classList.add('show');
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove('show'), 2800);
}

function getToken() {
  return sessionStorage.getItem(AGENCY_TOKEN_KEY) || sessionStorage.getItem(SHARED_TOKEN_KEY) || '';
}

function persistToken(token) {
  sessionStorage.setItem(AGENCY_TOKEN_KEY, token);
  sessionStorage.setItem(SHARED_TOKEN_KEY, token);
}

async function requestAgency(action, options = {}) {
  const project = options.project || agencyState.data?.project?.id || '';
  const query = new URLSearchParams({ action });
  if (project) query.set('project', project);
  const response = await fetch(`${AGENCY_API}?${query}`, {
    method: options.method || 'GET',
    headers: {
      'x-admin-token': agencyState.token,
      ...(options.body ? { 'content-type': 'application/json' } : {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.error || 'Agency data request failed.');
    error.status = response.status;
    throw error;
  }
  return payload;
}

async function loadAgency(projectId, options = {}) {
  const refresh = document.getElementById('agency-refresh');
  refresh?.classList.add('loading');
  try {
    const data = await requestAgency('load', { project: projectId || '' });
    agencyState.data = data;
    if (!agencyState.selectedLeadId || !data.leads.some(lead => lead.id === agencyState.selectedLeadId)) {
      agencyState.selectedLeadId = data.leads.find(lead => !lead.isTest && lead.source !== 'footer-newsletter')?.id || '';
    }
    showAgencyApp();
    renderAgency();
    if (!options.silent) showToast('Command center refreshed');
  } finally {
    refresh?.classList.remove('loading');
  }
}

function showAgencyApp() {
  document.getElementById('agency-auth').hidden = true;
  document.getElementById('agency-app').hidden = false;
}

function showAuth(message = '') {
  document.getElementById('agency-auth').hidden = false;
  document.getElementById('agency-app').hidden = true;
  setText('agency-auth-error', message);
  refreshIcons();
}

function aggregateCampaignMetrics() {
  const campaigns = agencyState.data?.project?.campaigns || [];
  return campaigns.reduce((totals, campaign) => {
    const metrics = campaign.metrics || {};
    for (const key of ['impressions', 'clicks', 'cost', 'conversions', 'qualified', 'revenue']) {
      totals[key] += Number(metrics[key]) || 0;
    }
    return totals;
  }, { impressions: 0, clicks: 0, cost: 0, conversions: 0, qualified: 0, revenue: 0 });
}

function realLeads() {
  return (agencyState.data?.leads || []).filter(lead => lead.source !== 'footer-newsletter' && !lead.isTest);
}

function rangeCutoff() {
  if (agencyState.range === 'all') return 0;
  return Date.now() - Number(agencyState.range) * 86400000;
}

function renderAgency() {
  const { project, projects } = agencyState.data;
  const select = document.getElementById('agency-project-select');
  select.innerHTML = projects.map(item => `<option value="${escapeHtml(item.id)}" ${item.id === project.id ? 'selected' : ''}>${escapeHtml(item.name)}</option>`).join('');
  setText('agency-project-status', titleCase(project.status));
  setText('nav-campaign-count', project.campaigns.length);
  setText('nav-keyword-count', project.research?.keywords?.filter(item => item.status === 'enabled').length || 0);
  setText('nav-lead-count', agencyState.data.leadSummary.leads);
  renderAlert();
  renderOverview();
  renderCampaigns();
  renderKeywords();
  renderLeads();
  renderPipeline();
  renderResearch();
  renderReports();
  renderSettings();
  refreshIcons();
}

function renderAlert() {
  const strip = document.getElementById('agency-alert-strip');
  const project = agencyState.data.project;
  const messages = [];
  if (project.tracking?.googleAdsApi === 'stale') messages.push('Google Ads reporting is stale; check the scheduled script before using performance data.');
  if (project.tracking?.googleAdsApi === 'not_connected') messages.push('Google Ads reporting is not connected; performance uses recorded snapshots.');
  if (!project.campaigns.length) messages.push('No campaign has been added to this project.');
  strip.hidden = !messages.length;
  strip.innerHTML = messages.length ? `<strong>Attention:</strong> ${escapeHtml(messages.join(' '))}` : '';
}

function metricCard(label, value, detail, icon) {
  return `<article class="agency-metric"><div class="agency-metric-label"><span>${escapeHtml(label)}</span><i data-lucide="${icon}"></i></div><strong>${escapeHtml(value)}</strong><small>${escapeHtml(detail)}</small></article>`;
}

function renderOverview() {
  const metrics = aggregateCampaignMetrics();
  const summary = agencyState.data.leadSummary;
  const cpl = summary.leads ? metrics.cost / summary.leads : 0;
  document.getElementById('agency-kpis').innerHTML = [
    metricCard('Spend', money(metrics.cost, 2), `${money(agencyState.data.project.monthlyBudget)} monthly budget`, 'circle-dollar-sign'),
    metricCard('Clicks', formatNumber(metrics.clicks), `${percentage(metrics.impressions ? metrics.clicks / metrics.impressions * 100 : 0)} CTR`, 'mouse-pointer-click'),
    metricCard('Real leads', formatNumber(summary.leads), `${summary.testLeads} tests excluded`, 'user-round-plus'),
    metricCard('Cost per lead', money(cpl, 2), summary.leads ? 'Based on CRM leads' : 'Awaiting first lead', 'badge-dollar-sign'),
    metricCard('Qualified', formatNumber(summary.qualified), `${summary.won} won`, 'badge-check'),
    metricCard('Revenue', money(summary.revenue, 2), `${money(summary.pipelineValue, 2)} open pipeline`, 'banknote'),
  ].join('');
  renderChart();
  renderHealth();
  renderCampaignTable('overview-campaign-table', agencyState.data.project.campaigns.slice(0, 4));
  renderFunnel();
  renderRecentLeads();
}

function renderChart() {
  const svg = document.getElementById('agency-performance-chart');
  const empty = document.getElementById('agency-chart-empty');
  const cutoff = rangeCutoff();
  const points = (agencyState.data.campaignSnapshots || []).filter(item => !cutoff || item._ts >= cutoff);
  if (points.length < 2) {
    svg.innerHTML = '';
    empty.hidden = false;
    return;
  }
  empty.hidden = true;
  const width = 760;
  const height = 260;
  const pad = { left: 42, right: 18, top: 18, bottom: 32 };
  const maxCost = Math.max(1, ...points.map(item => Number(item.cost) || 0));
  const maxLeads = Math.max(1, ...points.map(item => Number(item.conversions) || 0));
  const x = index => pad.left + index * ((width - pad.left - pad.right) / (points.length - 1));
  const yCost = value => pad.top + (height - pad.top - pad.bottom) * (1 - value / maxCost);
  const yLead = value => pad.top + (height - pad.top - pad.bottom) * (1 - value / maxLeads);
  const spendPath = points.map((item, index) => `${index ? 'L' : 'M'} ${x(index)} ${yCost(Number(item.cost) || 0)}`).join(' ');
  const leadPath = points.map((item, index) => `${index ? 'L' : 'M'} ${x(index)} ${yLead(Number(item.conversions) || 0)}`).join(' ');
  const grid = [0, .25, .5, .75, 1].map(ratio => {
    const y = pad.top + ratio * (height - pad.top - pad.bottom);
    return `<line x1="${pad.left}" y1="${y}" x2="${width - pad.right}" y2="${y}" stroke="#dce2df" stroke-width="1"/><text x="${pad.left - 8}" y="${y + 3}" text-anchor="end" fill="#77817d" font-size="10">${money(maxCost * (1 - ratio), 0)}</text>`;
  }).join('');
  const labels = points.map((item, index) => {
    if (index !== 0 && index !== points.length - 1 && points.length > 5) return '';
    return `<text x="${x(index)}" y="${height - 8}" text-anchor="middle" fill="#77817d" font-size="10">${new Date(item._ts).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</text>`;
  }).join('');
  svg.innerHTML = `${grid}<path d="${spendPath}" fill="none" stroke="#285da8" stroke-width="3"/><path d="${leadPath}" fill="none" stroke="#16735e" stroke-width="3"/>${points.map((item, index) => `<circle cx="${x(index)}" cy="${yCost(Number(item.cost) || 0)}" r="3" fill="#285da8"/><circle cx="${x(index)}" cy="${yLead(Number(item.conversions) || 0)}" r="3" fill="#16735e"/>`).join('')}${labels}`;
}

function renderHealth() {
  const project = agencyState.data.project;
  const checks = [
    { label: 'Campaign enabled', ok: project.campaigns.some(item => item.status === 'enabled'), detail: `${project.campaigns.length} total` },
    { label: 'Form conversion', ok: project.tracking?.formConversion === 'verified', detail: project.tracking?.formConversion || 'missing' },
    { label: 'GTM and event QA', ok: project.tracking?.gtm === 'verified', detail: project.tracking?.gtm || 'missing' },
    { label: 'Lead delivery', ok: project.tracking?.emailDelivery === 'verified', detail: project.tracking?.emailDelivery || 'missing' },
    { label: 'Google Ads reporting', ok: project.tracking?.googleAdsApi === 'verified', detail: project.tracking?.googleAdsApi === 'verified' ? `Synced ${relativeTime(project.googleAdsConnection?.lastSyncedAt)}` : project.tracking?.googleAdsApi === 'stale' ? 'Stale feed' : 'Snapshot mode' },
  ];
  const score = Math.round(checks.filter(item => item.ok).length / checks.length * 100);
  document.getElementById('agency-health-panel').innerHTML = `<div class="agency-health-score"><div><p class="agency-eyebrow">System health</p><strong>${score}</strong></div><span>${checks.filter(item => item.ok).length}/${checks.length} ready</span></div><div class="agency-health-list">${checks.map(item => `<div class="agency-health-row ${item.ok ? 'good' : 'warn'}"><i data-lucide="${item.ok ? 'circle-check' : 'triangle-alert'}"></i><span>${escapeHtml(item.label)}</span><small>${escapeHtml(titleCase(item.detail))}</small></div>`).join('')}</div>`;
}

function renderCampaignTable(id, campaigns) {
  const table = document.getElementById(id);
  table.innerHTML = `<thead><tr><th>Campaign</th><th>Status</th><th>Budget</th><th>Spend</th><th>Clicks</th><th>CTR</th><th>Leads</th><th>CPL</th></tr></thead><tbody>${campaigns.length ? campaigns.map(campaign => {
    const m = campaign.metrics || {};
    const ctr = m.impressions ? m.clicks / m.impressions * 100 : 0;
    const cpl = m.conversions ? m.cost / m.conversions : 0;
    return `<tr><td><strong>${escapeHtml(campaign.name)}</strong><small>${escapeHtml(campaign.channel)} · ${escapeHtml(campaign.type)}</small></td><td><span class="agency-chip ${campaign.status === 'enabled' ? 'green' : 'gray'}">${escapeHtml(campaign.status)}</span></td><td class="agency-table-number">${money(campaign.dailyBudget, 2)}/day</td><td class="agency-table-number">${money(m.cost, 2)}</td><td class="agency-table-number">${formatNumber(m.clicks)}</td><td class="agency-table-number">${percentage(ctr)}</td><td class="agency-table-number">${formatNumber(m.conversions, 1)}</td><td class="agency-table-number">${money(cpl, 2)}</td></tr>`;
  }).join('') : '<tr><td colspan="8"><div class="agency-empty">No campaigns configured</div></td></tr>'}</tbody>`;
}

function renderFunnel() {
  const leads = realLeads();
  const counts = {
    Captured: agencyState.data.leadSummary.leads,
    Contacted: leads.filter(item => ['contacted', 'qualified', 'proposal', 'won'].includes(item.stage)).length,
    Qualified: leads.filter(item => ['qualified', 'proposal', 'won'].includes(item.stage)).length,
    Proposal: leads.filter(item => ['proposal', 'won'].includes(item.stage)).length,
    Won: leads.filter(item => item.stage === 'won').length,
  };
  const max = Math.max(1, counts.Captured);
  document.getElementById('agency-funnel').innerHTML = Object.entries(counts).map(([label, count]) => `<div class="agency-funnel-row"><span>${label}</span><div class="agency-funnel-track"><div class="agency-funnel-fill" style="width:${Math.max(count ? 4 : 0, count / max * 100)}%"></div></div><strong>${count}</strong></div>`).join('');
}

function renderRecentLeads() {
  const leads = (agencyState.data.leads || []).filter(lead => lead.source !== 'footer-newsletter' && !lead.isTest).slice(0, 5);
  document.getElementById('agency-recent-leads').innerHTML = leads.length ? leads.map(lead => `<button class="agency-activity-item" data-open-lead="${escapeHtml(lead.id)}"><span class="agency-avatar">${escapeHtml(initials(lead.name || lead.email))}</span><span><strong>${escapeHtml(lead.name || lead.email || 'Anonymous')}</strong><small>${escapeHtml(lead.utm_campaign || lead.source || 'Direct')}</small></span><time>${escapeHtml(relativeTime(lead._ts))}</time></button>`).join('') : '<div class="agency-empty">No real leads yet</div>';
  bindLeadOpeners();
}

function renderCampaigns() {
  const project = agencyState.data.project;
  const metrics = aggregateCampaignMetrics();
  document.getElementById('agency-campaign-summary').innerHTML = [
    ['Active campaigns', project.campaigns.filter(item => item.status === 'enabled').length],
    ['Daily budget', money(project.campaigns.reduce((sum, item) => sum + (Number(item.dailyBudget) || 0), 0), 2)],
    ['CPC cap', project.campaigns.length ? money(project.campaigns[0].cpcCap, 2) : '—'],
    ['Recorded spend', money(metrics.cost, 2)],
  ].map(([label, value]) => `<div class="agency-summary-cell"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join('');
  renderCampaignTable('campaign-table', project.campaigns);
  const campaign = project.campaigns[0];
  document.getElementById('campaign-detail-grid').innerHTML = campaign ? [
    ['Campaign setup', [['Bid strategy', campaign.bidStrategy], ['CPC cap', money(campaign.cpcCap, 2)], ['Ad group', campaign.adGroup], ['Goal', campaign.conversionGoal]]],
    ['Targeting', [['Locations', (campaign.locations || []).join(', ')], ['Channel', campaign.channel], ['Type', campaign.type], ['Launch', campaign.launchedAt]]],
    ['Destination', [['Landing page', campaign.landingPage], ['Primary conversion', project.primaryConversion], ['Keywords', project.research?.keywords?.filter(item => item.status === 'enabled').length || 0], ['Negatives', project.research?.negatives || 0]]],
  ].map(([title, rows]) => `<section class="agency-detail-block"><h3>${escapeHtml(title)}</h3>${rows.map(([key, value]) => `<div class="agency-key-value"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value || '—')}</strong></div>`).join('')}</section>`).join('') : '<div class="agency-empty">No campaign setup recorded</div>';
  const campaignSelect = document.getElementById('snapshot-campaign');
  campaignSelect.innerHTML = project.campaigns.map(item => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name)}</option>`).join('');
  document.getElementById('agency-add-snapshot').disabled = !project.campaigns.length;
}

function renderKeywords() {
  const keywords = agencyState.data.project.research?.keywords || [];
  const enabled = keywords.filter(item => item.status === 'enabled');
  const avgCpc = enabled.length ? enabled.reduce((sum, item) => sum + (Number(item.cpc) || 0), 0) / enabled.length : 0;
  const commercial = enabled.filter(item => item.intent === 'Commercial').length;
  document.getElementById('keyword-kpis').innerHTML = [
    metricCard('Enabled', formatNumber(enabled.length), `${keywords.length - enabled.length} paused`, 'circle-play'),
    metricCard('Commercial intent', formatNumber(commercial), `${percentage(enabled.length ? commercial / enabled.length * 100 : 0)} of launch set`, 'badge-check'),
    metricCard('Average CPC signal', money(avgCpc, 2), 'Across research sources', 'circle-dollar-sign'),
    metricCard('Negative keywords', formatNumber(agencyState.data.project.research?.negatives || 0), 'Launch protection', 'shield-minus'),
  ].join('');
  filterKeywords();
}

function filterKeywords() {
  if (!agencyState.data) return;
  const query = document.getElementById('keyword-search').value.trim().toLowerCase();
  const status = document.getElementById('keyword-status-filter').value;
  const keywords = (agencyState.data.project.research?.keywords || []).filter(item => (!query || item.keyword.toLowerCase().includes(query)) && (status === 'all' || item.status === status));
  const metricKey = item => `${String(item.keyword || '').trim().toLowerCase()}|${String(item.matchType || '').trim().toLowerCase()}`;
  const liveMetrics = new Map((agencyState.data.googleAdsKeywordMetrics || []).map(item => [metricKey(item), item]));
  document.getElementById('keyword-table').innerHTML = `<thead><tr><th>Keyword</th><th>Match</th><th>Status</th><th>Intent</th><th>Volume</th><th>KD</th><th>Research CPC</th><th>Live impr.</th><th>Live clicks</th><th>Live spend</th><th>Live conv.</th><th>Source</th><th>Decision</th></tr></thead><tbody>${keywords.length ? keywords.map(item => {
    const live = liveMetrics.get(metricKey(item));
    return `<tr><td><strong>${escapeHtml(item.keyword)}</strong></td><td><span class="agency-chip blue">${escapeHtml(item.matchType)}</span></td><td><span class="agency-chip ${item.status === 'enabled' ? 'green' : 'red'}">${escapeHtml(item.status)}</span></td><td>${escapeHtml(item.intent)}</td><td class="agency-table-number">${formatNumber(item.volume)}</td><td class="agency-table-number">${formatNumber(item.kd)}</td><td class="agency-table-number">${money(item.cpc, 2)}</td><td class="agency-table-number">${live ? formatNumber(live.impressions) : '—'}</td><td class="agency-table-number">${live ? formatNumber(live.clicks) : '—'}</td><td class="agency-table-number">${live ? money(live.cost, 2) : '—'}</td><td class="agency-table-number">${live ? formatNumber(live.conversions, 1) : '—'}</td><td>${escapeHtml(item.source)}</td><td>${escapeHtml(item.decision)}</td></tr>`;
  }).join('') : '<tr><td colspan="13"><div class="agency-empty">No matching keywords</div></td></tr>'}</tbody>`;
}

function leadStageClass(stage) {
  if (stage === 'won' || stage === 'qualified') return 'green';
  if (stage === 'lost') return 'red';
  if (stage === 'proposal') return 'amber';
  if (stage === 'contacted') return 'blue';
  return 'gray';
}

function filteredLeads() {
  const query = document.getElementById('lead-search').value.trim().toLowerCase();
  const stage = document.getElementById('lead-stage-filter').value;
  const hideTests = document.getElementById('hide-test-leads').checked;
  return (agencyState.data.leads || []).filter(lead => {
    if (lead.source === 'footer-newsletter') return false;
    if (hideTests && lead.isTest) return false;
    if (stage !== 'all' && lead.stage !== stage) return false;
    if (query && !JSON.stringify(lead).toLowerCase().includes(query)) return false;
    return true;
  });
}

function renderLeads() {
  const stageFilter = document.getElementById('lead-stage-filter');
  if (stageFilter.options.length === 1) {
    stageFilter.insertAdjacentHTML('beforeend', (agencyState.data.stages || []).map(stage => `<option value="${stage}">${STAGE_LABELS[stage]}</option>`).join(''));
  }
  const leads = filteredLeads();
  if (agencyState.selectedLeadId && !leads.some(lead => lead.id === agencyState.selectedLeadId)) agencyState.selectedLeadId = leads[0]?.id || '';
  document.getElementById('agency-lead-list').innerHTML = leads.length ? leads.map(lead => `<button class="agency-lead-row ${lead.id === agencyState.selectedLeadId ? 'active' : ''}" data-open-lead="${escapeHtml(lead.id)}"><span class="agency-avatar">${escapeHtml(initials(lead.name || lead.email))}</span><span><strong>${escapeHtml(lead.name || lead.email || 'Anonymous')}</strong><small>${escapeHtml(lead.email || lead.phone || lead.message || 'No contact details')}</small></span><span class="agency-lead-meta"><span class="agency-chip ${leadStageClass(lead.stage)}">${escapeHtml(STAGE_LABELS[lead.stage])}</span><time>${escapeHtml(relativeTime(lead._ts))}</time></span></button>`).join('') : '<div class="agency-empty">No leads match this view</div>';
  renderLeadDetail(agencyState.selectedLeadId);
  bindLeadOpeners();
}

function detailRows(rows) {
  const visible = rows.filter(([, value]) => value !== undefined && value !== null && value !== '');
  return visible.length ? `<dl>${visible.map(([key, value]) => `<div><dt>${escapeHtml(key)}</dt><dd>${escapeHtml(value)}</dd></div>`).join('')}</dl>` : '<div class="agency-empty">No data captured</div>';
}

function renderLeadActivity(lead) {
  const activity = Array.isArray(lead.activity) ? lead.activity : [];
  if (!activity.length) return '<div class="agency-empty">No activity yet</div>';
  return `<div class="agency-timeline">${activity.map(item => {
    if (item.type === 'email') {
      return `<article class="agency-timeline-item email"><span><i data-lucide="send"></i></span><div><strong>${escapeHtml(item.subject || 'Email sent')}</strong><small>To ${escapeHtml(item.to || lead.email || 'lead')} · ${escapeHtml(fullDate(item.at))}</small>${item.body ? `<p>${escapeHtml(item.body)}</p>` : ''}</div></article>`;
    }
    if (item.type === 'stage') {
      return `<article class="agency-timeline-item"><span><i data-lucide="arrow-right-left"></i></span><div><strong>Stage changed to ${escapeHtml(STAGE_LABELS[item.to] || titleCase(item.to))}</strong><small>From ${escapeHtml(STAGE_LABELS[item.from] || titleCase(item.from))} · ${escapeHtml(fullDate(item.at))}</small></div></article>`;
    }
    return `<article class="agency-timeline-item"><span><i data-lucide="notebook-pen"></i></span><div><strong>${item.type === 'note' ? 'Note added' : escapeHtml(titleCase(item.type))}</strong><small>${escapeHtml(fullDate(item.at))}</small></div></article>`;
  }).join('')}</div>`;
}

function renderLeadDetail(leadId) {
  const container = document.getElementById('agency-lead-detail');
  const lead = (agencyState.data.leads || []).find(item => item.id === leadId);
  if (!lead) {
    container.innerHTML = '<div class="agency-empty">Select a lead to view details</div>';
    return;
  }
  const attribution = [
    ['Source', lead.utm_source || lead.source],
    ['Medium', lead.utm_medium],
    ['Campaign', lead.utm_campaign],
    ['Keyword', lead.utm_term],
    ['Creative', lead.utm_content],
    ['GCLID', lead.gclid],
    ['Google campaign', lead.gad_campaignid],
    ['Landing page', lead.landing_page || lead.landingPage || lead.page_url],
  ];
  const known = new Set(['id', 'projectId', 'name', 'email', 'phone', 'website', 'url', 'message', 'scope', 'source', 'stage', 'assignedTo', 'value', 'nextAction', 'lostReason', 'isTest', 'notes', 'activity', 'updatedAt', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'gad_campaignid', 'landing_page', 'landingPage', 'page_url', 'page_title']);
  const extra = Object.entries(lead).filter(([key, value]) => !known.has(key) && !key.startsWith('_') && value !== '' && value !== null && value !== undefined).slice(0, 14);
  const mailReady = Boolean(agencyState.data.project.zohoMail?.connected);
  container.innerHTML = `<div class="agency-lead-detail-head"><div><h2>${escapeHtml(lead.name || 'Anonymous')}</h2><p>${escapeHtml(lead.email || lead.phone || 'No contact details')} · ${escapeHtml(fullDate(lead._ts))}</p></div><div class="agency-lead-head-actions"><button class="agency-secondary-btn" id="lead-email" type="button" ${lead.email && mailReady ? '' : 'disabled'} title="${lead.email ? (mailReady ? 'Email this lead' : 'Connect Zoho Mail in Setup') : 'No email address'}"><i data-lucide="mail"></i>Email</button><span class="agency-chip ${lead.isTest ? 'amber' : leadStageClass(lead.stage)}">${lead.isTest ? 'Test lead' : escapeHtml(STAGE_LABELS[lead.stage])}</span></div></div>
    <div class="agency-lead-controls">
      <label>Stage<select id="lead-stage-input">${agencyState.data.stages.map(stage => `<option value="${stage}" ${lead.stage === stage ? 'selected' : ''}>${STAGE_LABELS[stage]}</option>`).join('')}</select></label>
      <label>Deal value<input id="lead-value-input" type="number" min="0" step="0.01" value="${escapeHtml(lead.value)}" /></label>
      <label>Owner<input id="lead-owner-input" value="${escapeHtml(lead.assignedTo)}" placeholder="Unassigned" /></label>
      <label class="agency-lead-control-wide">Next action<input id="lead-next-input" value="${escapeHtml(lead.nextAction)}" placeholder="Follow-up date or action" /></label>
      <label class="agency-toggle agency-lead-test-toggle"><input id="lead-test-input" type="checkbox" ${lead.isTest ? 'checked' : ''} /><span></span>Test lead</label>
      <button class="agency-primary-btn" id="lead-save" type="button">Save lead</button>
    </div>
    <div class="agency-lead-sections">
      <section class="agency-lead-section"><h3>Contact</h3>${detailRows([['Email', lead.email], ['Phone', lead.phone], ['Website', lead.website || lead.url], ['Scope', lead.scope]])}</section>
      <section class="agency-lead-section"><h3>Attribution</h3>${detailRows(attribution)}</section>
      ${lead.message ? `<section class="agency-lead-section wide"><h3>Message</h3><p class="agency-research-copy">${escapeHtml(lead.message)}</p></section>` : ''}
      ${extra.length ? `<section class="agency-lead-section wide"><h3>Submission data</h3>${detailRows(extra.map(([key, value]) => [titleCase(key), value]))}</section>` : ''}
      <section class="agency-lead-section wide"><h3>Sales notes</h3><form class="agency-note-form" id="lead-note-form"><textarea id="lead-note-input" placeholder="Add a call note, qualification detail, or next step"></textarea><button class="agency-secondary-btn" type="submit"><i data-lucide="plus"></i>Add note</button></form><div class="agency-note-list">${lead.notes.length ? lead.notes.map(note => `<article class="agency-note">${escapeHtml(note.body)}<time>${escapeHtml(fullDate(note.at))}</time></article>`).join('') : '<div class="agency-empty">No notes yet</div>'}</div></section>
      <section class="agency-lead-section wide"><h3>Activity</h3>${renderLeadActivity(lead)}</section>
    </div>`;
  document.getElementById('lead-save').addEventListener('click', () => saveLead(lead.id));
  document.getElementById('lead-email')?.addEventListener('click', () => openLeadEmail(lead));
  document.getElementById('lead-note-form').addEventListener('submit', event => {
    event.preventDefault();
    const note = document.getElementById('lead-note-input').value.trim();
    if (note) saveLead(lead.id, note);
  });
  refreshIcons();
}

function bindLeadOpeners() {
  document.querySelectorAll('[data-open-lead]').forEach(button => {
    button.addEventListener('click', () => {
      agencyState.selectedLeadId = button.dataset.openLead;
      switchView('leads');
      renderLeads();
    });
  });
}

async function saveLead(leadId, note = '') {
  const patch = note ? {} : {
    stage: document.getElementById('lead-stage-input').value,
    value: document.getElementById('lead-value-input').value,
    assignedTo: document.getElementById('lead-owner-input').value,
    nextAction: document.getElementById('lead-next-input').value,
    isTest: document.getElementById('lead-test-input').checked,
  };
  await requestAgency('lead', { method: 'POST', body: { projectId: agencyState.data.project.id, leadId, patch, note } });
  await loadAgency(agencyState.data.project.id, { silent: true });
  agencyState.selectedLeadId = leadId;
  renderLeads();
  renderOverview();
  renderPipeline();
  showToast(note ? 'Note added' : 'Lead updated');
}

function renderPipeline() {
  const leads = realLeads();
  setText('pipeline-open-value', money(leads.filter(lead => !['won', 'lost'].includes(lead.stage)).reduce((sum, lead) => sum + lead.value, 0), 2));
  document.getElementById('agency-pipeline-board').innerHTML = (agencyState.data.stages || []).map(stage => {
    const stageLeads = leads.filter(lead => lead.stage === stage);
    return `<section class="agency-pipeline-column" data-stage="${stage}"><div class="agency-pipeline-head"><strong>${STAGE_LABELS[stage]}</strong><span>${stageLeads.length}</span></div><div class="agency-pipeline-cards">${stageLeads.map(lead => `<article class="agency-deal-card" draggable="true" data-lead-id="${escapeHtml(lead.id)}"><strong>${escapeHtml(lead.name || lead.email || 'Anonymous')}</strong><small>${escapeHtml(lead.utm_campaign || lead.source || 'Direct')}</small><div class="agency-deal-foot"><span>${escapeHtml(relativeTime(lead._ts))}</span><b>${money(lead.value, 0)}</b></div></article>`).join('')}</div></section>`;
  }).join('');
  document.querySelectorAll('.agency-deal-card').forEach(card => {
    card.addEventListener('dragstart', () => { agencyState.draggedLeadId = card.dataset.leadId; });
    card.addEventListener('dblclick', () => { agencyState.selectedLeadId = card.dataset.leadId; switchView('leads'); renderLeads(); });
  });
  document.querySelectorAll('.agency-pipeline-column').forEach(column => {
    column.addEventListener('dragover', event => { event.preventDefault(); column.classList.add('drag-over'); });
    column.addEventListener('dragleave', () => column.classList.remove('drag-over'));
    column.addEventListener('drop', async event => {
      event.preventDefault();
      column.classList.remove('drag-over');
      if (!agencyState.draggedLeadId) return;
      const stage = column.dataset.stage;
      await requestAgency('lead', { method: 'POST', body: { projectId: agencyState.data.project.id, leadId: agencyState.draggedLeadId, patch: { stage } } });
      agencyState.draggedLeadId = '';
      await loadAgency(agencyState.data.project.id, { silent: true });
      switchView('pipeline');
      showToast(`Lead moved to ${STAGE_LABELS[stage]}`);
    });
  });
}

function renderResearch() {
  const project = agencyState.data.project;
  const research = project.research || {};
  setText('research-updated', research.completedAt ? `Completed ${research.completedAt}` : 'Not completed');
  document.getElementById('research-summary').innerHTML = `<p class="agency-eyebrow">Keyword strategy</p><h2>${escapeHtml(research.summary || 'Research pending')}</h2><p class="agency-research-copy">${escapeHtml(research.keywords?.filter(item => item.status === 'enabled').length || 0)} active keywords · ${escapeHtml(research.negatives || 0)} negatives · exact and phrase match control.</p><div class="agency-research-tools">${(research.tools || []).map(tool => `<span>${escapeHtml(tool)}</span>`).join('')}</div>`;
  document.getElementById('landing-page-review').innerHTML = `<p class="agency-eyebrow">Conversion destination</p><h2>Landing-page readiness</h2><div class="agency-check-list">${[
    ['Dedicated paid-traffic page', Boolean(project.landingPage)],
    ['Primary lead form', project.tracking?.formConversion === 'verified'],
    ['Form delivery QA', project.tracking?.emailDelivery === 'verified'],
    ['Conversion event QA', project.tracking?.gtm === 'verified'],
    ['Portfolio and trust proof', Boolean(project.landingPage)],
  ].map(([label, ok]) => `<div class="agency-check-item"><i data-lucide="${ok ? 'circle-check' : 'circle-dashed'}"></i><span>${escapeHtml(label)}</span><span class="agency-chip ${ok ? 'green' : 'amber'}">${ok ? 'Ready' : 'Review'}</span></div>`).join('')}</div>`;
  document.getElementById('research-rejections').innerHTML = (research.rejected || []).length ? research.rejected.map(item => `<article class="agency-rejection-item"><strong>${escapeHtml(item.keyword)}</strong><span>${escapeHtml(item.reason)}</span></article>`).join('') : '<div class="agency-empty">No rejected opportunities recorded</div>';
}

function renderReports() {
  const project = agencyState.data.project;
  const metrics = aggregateCampaignMetrics();
  const summary = agencyState.data.leadSummary;
  document.getElementById('agency-report-header').innerHTML = `<div class="agency-report-cell lead"><span>Project</span><strong>${escapeHtml(project.name)}</strong><small>${escapeHtml(project.goal)}</small></div><div class="agency-report-cell"><span>Spend</span><strong>${money(metrics.cost, 2)}</strong></div><div class="agency-report-cell"><span>Real leads</span><strong>${summary.leads}</strong></div><div class="agency-report-cell"><span>Revenue</span><strong>${money(summary.revenue, 2)}</strong></div>`;
  const snapshots = [...(agencyState.data.campaignSnapshots || [])].sort((a, b) => (b._ts || 0) - (a._ts || 0));
  document.getElementById('snapshot-table').innerHTML = `<thead><tr><th>Recorded</th><th>Campaign</th><th>Impressions</th><th>Clicks</th><th>Spend</th><th>Conversions</th><th>Qualified</th><th>Revenue</th><th>Source</th></tr></thead><tbody>${snapshots.length ? snapshots.map(item => `<tr><td>${escapeHtml(fullDate(item._ts))}</td><td>${escapeHtml(project.campaigns.find(campaign => campaign.id === item.campaignId)?.name || item.campaignId)}</td><td class="agency-table-number">${formatNumber(item.impressions)}</td><td class="agency-table-number">${formatNumber(item.clicks)}</td><td class="agency-table-number">${money(item.cost, 2)}</td><td class="agency-table-number">${formatNumber(item.conversions, 1)}</td><td class="agency-table-number">${formatNumber(item.qualified)}</td><td class="agency-table-number">${money(item.revenue, 2)}</td><td><span class="agency-chip gray">${escapeHtml(item.source || 'manual')}</span></td></tr>`).join('') : '<tr><td colspan="9"><div class="agency-empty">No performance snapshots recorded</div></td></tr>'}</tbody>`;
}

function renderSettings() {
  const project = agencyState.data.project;
  const adsConnection = project.googleAdsConnection;
  const adsReady = project.tracking?.googleAdsApi === 'verified';
  const adsStale = project.tracking?.googleAdsApi === 'stale';
  const zoho = project.zohoMail || {};
  const connections = [
    ['Google Ads', adsReady, adsStale ? 'Reporting feed stale' : adsReady ? `Synced ${relativeTime(adsConnection?.lastSyncedAt)}` : 'Campaign reporting', 'megaphone', adsStale ? 'Stale' : adsReady ? 'Connected' : 'Pending'],
    ['Google Tag Manager', project.tracking?.gtm === 'verified', 'Conversion events', 'tags'],
    ['Lead forms', project.tracking?.formConversion === 'verified', 'Primary conversion', 'notebook-tabs'],
    ['Lead notifications', project.tracking?.emailDelivery === 'verified', 'Inbound delivery', 'mail-check'],
    ['Zoho Mail', zoho.connected, zoho.connected ? zoho.fromEmail : 'CRM outbound email', 'send', zoho.connected ? 'Connected' : zoho.clientConfigured ? 'Authorise' : 'Pending'],
    ['Agency CRM', true, 'KV lead pipeline', 'contact-round'],
    ['Meta Ads', project.tracking?.metaAdsApi === 'verified', 'Future channel', 'megaphone'],
  ];
  document.getElementById('agency-connections').innerHTML = connections.map(([name, ready, detail, icon, label]) => `<article class="agency-connection"><span class="agency-connection-icon"><i data-lucide="${icon}"></i></span><span><strong>${escapeHtml(name)}</strong><small>${escapeHtml(detail)}</small></span><span class="agency-chip ${ready ? 'green' : 'amber'}">${escapeHtml(label || (ready ? 'Connected' : 'Pending'))}</span></article>`).join('');
  document.getElementById('agency-google-ads-setup').innerHTML = `<div class="agency-section-head"><div><p class="agency-eyebrow">Google Ads reporting</p><h2>Scheduled data feed</h2></div><span class="agency-chip ${adsReady ? 'green' : adsStale ? 'amber' : 'gray'}">${adsReady ? 'Connected' : adsStale ? 'Stale' : 'Not connected'}</span></div><div class="agency-sync-meta">${[
    ['Mode', 'Google Ads Script'],
    ['Account', adsConnection?.accountId || 'Not verified'],
    ['Last sync', adsConnection?.lastSyncedAt ? fullDate(adsConnection.lastSyncedAt) : 'Never'],
    ['Campaigns received', adsConnection?.campaignCount ?? '—'],
    ['Keywords received', adsConnection?.keywordCount ?? '—'],
  ].map(([label, value]) => `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join('')}</div><div class="agency-sync-actions"><button class="agency-primary-btn" id="open-google-ads-script" type="button" ${project.campaigns.length ? '' : 'disabled'}><i data-lucide="code-xml"></i>Open sync script</button></div>`;
  document.getElementById('agency-zoho-setup').innerHTML = `<div class="agency-section-head"><div><p class="agency-eyebrow">CRM outbound email</p><h2>Zoho Mail</h2></div><span class="agency-chip ${zoho.connected ? 'green' : zoho.clientConfigured ? 'amber' : 'gray'}">${zoho.connected ? 'Connected' : zoho.clientConfigured ? 'Ready to authorise' : 'Not connected'}</span></div><div class="agency-sync-meta">${[
    ['Mailbox', zoho.fromEmail || 'Not configured'],
    ['Permission', zoho.permission || 'Send only'],
    ['Connected', zoho.connectedAt ? fullDate(zoho.connectedAt) : 'Never'],
    ['Last sent', zoho.lastSentAt ? fullDate(zoho.lastSentAt) : 'No emails sent'],
    ['Data center', String(zoho.dataCenter || 'us').toUpperCase()],
  ].map(([label, value]) => `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join('')}</div><div class="agency-sync-actions agency-sync-actions-split"><button class="agency-secondary-btn" id="configure-zoho" type="button"><i data-lucide="key-round"></i>OAuth settings</button><span>${zoho.connected ? `<button class="agency-secondary-btn" id="test-zoho" type="button"><i data-lucide="send"></i>Send test to mailbox</button>` : ''}${zoho.clientConfigured ? `<button class="agency-primary-btn" id="authorise-zoho" type="button"><i data-lucide="shield-check"></i>${zoho.connected ? 'Reauthorise' : 'Authorise mailbox'}</button>` : ''}${zoho.connected ? `<button class="agency-secondary-btn danger" id="disconnect-zoho" type="button"><i data-lucide="unlink"></i>Disconnect</button>` : ''}</span></div>`;
  document.getElementById('agency-project-profile').innerHTML = `<div class="agency-section-head"><div><p class="agency-eyebrow">Project profile</p><h2>${escapeHtml(project.name)}</h2></div></div><div class="agency-project-profile-grid">${[
    ['Website', project.website], ['Owner', project.owner], ['Monthly budget', money(project.monthlyBudget, 0)], ['Currency', project.currency], ['Timezone', project.timezone], ['Goal', project.goal], ['Primary conversion', project.primaryConversion], ['Landing page', project.landingPage],
  ].map(([label, value]) => `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(value || 'Not set')}</strong></div>`).join('')}</div>`;
  document.getElementById('open-google-ads-script')?.addEventListener('click', openGoogleAdsScript);
  document.getElementById('configure-zoho')?.addEventListener('click', openZohoConfig);
  document.getElementById('test-zoho')?.addEventListener('click', testZohoMail);
  document.getElementById('authorise-zoho')?.addEventListener('click', startZohoAuthorization);
  document.getElementById('disconnect-zoho')?.addEventListener('click', disconnectZohoMail);
}

async function openGoogleAdsScript() {
  const button = document.getElementById('open-google-ads-script');
  button.disabled = true;
  try {
    const result = await requestAgency('google-ads-script');
    document.getElementById('google-ads-script-output').value = result.script;
    openDialog('google-ads-script-modal');
  } catch (error) {
    showToast(error.message);
  } finally {
    button.disabled = false;
  }
}

function openZohoConfig() {
  const zoho = agencyState.data.project.zohoMail || {};
  const form = document.getElementById('zoho-config-form');
  form.elements.fromEmail.value = zoho.fromEmail || '';
  form.elements.clientId.value = '';
  form.elements.clientSecret.value = '';
  form.elements.dataCenter.value = zoho.dataCenter || 'us';
  setText('zoho-config-error', '');
  openDialog('zoho-config-modal');
}

async function configureZohoClient(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  setText('zoho-config-error', '');
  try {
    const payload = Object.fromEntries(new FormData(form).entries());
    await requestAgency('zoho-client', {
      method: 'POST',
      body: { ...payload, projectId: agencyState.data.project.id },
    });
    closeDialog('zoho-config-modal');
    await startZohoAuthorization();
  } catch (error) {
    setText('zoho-config-error', error.message);
  } finally {
    button.disabled = false;
  }
}

async function startZohoAuthorization() {
  const button = document.getElementById('authorise-zoho');
  if (button) button.disabled = true;
  try {
    const result = await requestAgency('zoho-authorize');
    window.location.assign(result.authorizeUrl);
  } catch (error) {
    showToast(error.message);
    if (button) button.disabled = false;
  }
}

async function disconnectZohoMail() {
  if (!window.confirm('Disconnect Zoho Mail from this project?')) return;
  const button = document.getElementById('disconnect-zoho');
  if (button) button.disabled = true;
  try {
    await requestAgency('zoho-disconnect', {
      method: 'POST',
      body: { projectId: agencyState.data.project.id },
    });
    await loadAgency(agencyState.data.project.id, { silent: true });
    switchView('settings');
    showToast('Zoho Mail disconnected');
  } catch (error) {
    showToast(error.message);
    if (button) button.disabled = false;
  }
}

async function testZohoMail() {
  const zoho = agencyState.data.project.zohoMail || {};
  if (!zoho.connected || !zoho.fromEmail) return;
  if (!window.confirm(`Send one connection test to ${zoho.fromEmail}?`)) return;
  const button = document.getElementById('test-zoho');
  if (button) button.disabled = true;
  try {
    await requestAgency('send-test-email', {
      method: 'POST',
      body: { projectId: agencyState.data.project.id },
    });
    await loadAgency(agencyState.data.project.id, { silent: true });
    switchView('settings');
    showToast(`Test email sent to ${zoho.fromEmail}`);
  } catch (error) {
    showToast(error.message);
    if (button) button.disabled = false;
  }
}

function openLeadEmail(lead) {
  const zoho = agencyState.data.project.zohoMail || {};
  if (!zoho.connected || !lead.email) return;
  const project = agencyState.data.project;
  const projectName = String(project.name || 'our team').trim();
  const owner = String(project.owner || projectName).trim();
  const firstName = String(lead.name || '').trim().split(/\s+/)[0] || 'there';
  agencyState.emailLeadContext = Object.freeze({ id: String(lead.id), email: String(lead.email).trim().toLowerCase() });
  document.getElementById('email-from').value = zoho.fromEmail || '';
  document.getElementById('email-to').value = lead.email;
  document.getElementById('email-subject').value = `Re: Your enquiry to ${projectName}`;
  document.getElementById('email-content').value = `Hi ${firstName},\n\nThank you for reaching out to ${projectName}. I have reviewed your enquiry and would be glad to discuss the project with you.\n\nWould you be available for a short call this week? You can reply with a time that works for you.\n\nBest,\n${owner}\n${projectName}`;
  setText('email-form-error', '');
  openDialog('email-lead-modal');
}

async function sendLeadEmail(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const context = agencyState.emailLeadContext;
  const lead = (agencyState.data.leads || []).find(item => item.id === context?.id);
  if (!lead || String(lead.email || '').trim().toLowerCase() !== context.email) {
    setText('email-form-error', 'The selected lead changed. Close this email and open it again.');
    return;
  }
  const button = document.getElementById('email-send-button');
  button.disabled = true;
  setText('email-form-error', '');
  try {
    const fields = Object.fromEntries(new FormData(form).entries());
    const result = await requestAgency('send-email', {
      method: 'POST',
      body: { ...fields, projectId: agencyState.data.project.id, leadId: context.id, toAddress: context.email },
    });
    closeDialog('email-lead-modal');
    await loadAgency(agencyState.data.project.id, { silent: true });
    agencyState.selectedLeadId = context.id;
    agencyState.emailLeadContext = null;
    switchView('leads');
    renderLeads();
    showToast(result.warning || 'Email sent through Zoho Mail');
  } catch (error) {
    setText('email-form-error', error.message);
  } finally {
    button.disabled = false;
  }
}

function switchView(view) {
  agencyState.currentView = view;
  document.querySelectorAll('.agency-nav-item').forEach(item => item.classList.toggle('active', item.dataset.view === view));
  document.querySelectorAll('.agency-view').forEach(section => section.classList.toggle('active', section.id === `view-${view}`));
  const section = document.getElementById(`view-${view}`);
  setText('agency-view-title', section?.dataset.title || titleCase(view));
  setText('agency-view-kicker', section?.dataset.kicker || 'Agency operations');
  if (view === 'leads') renderLeads();
  if (view === 'pipeline') renderPipeline();
  refreshIcons();
}

function openDialog(id) {
  const dialog = document.getElementById(id);
  if (dialog && !dialog.open) dialog.showModal();
}

function closeDialog(id) {
  const dialog = document.getElementById(id);
  if (dialog?.open) dialog.close();
  if (id === 'email-lead-modal') agencyState.emailLeadContext = null;
}

function handleZohoReturn() {
  if (agencyState.zohoNoticeShown) return;
  const params = new URLSearchParams(window.location.search);
  const status = params.get('zoho');
  if (!status) return;
  agencyState.zohoNoticeShown = true;
  const reason = params.get('reason');
  const messages = {
    access_denied: 'Zoho access was not granted.',
    mailbox_not_found: 'That Zoho account does not contain the configured sender mailbox.',
    token_exchange: 'Zoho could not complete the secure token exchange.',
    refresh_token_missing: 'Zoho did not provide offline access. Reauthorise the mailbox.',
    invalid_state: 'The Zoho connection request expired. Start it again.',
    client_missing: 'The Zoho OAuth client is not configured.',
  };
  switchView('settings');
  showToast(status === 'connected' ? 'Zoho Mail connected' : (messages[reason] || 'Zoho Mail connection failed.'));
  window.history.replaceState({}, '', '/admin/agency.html');
}

async function createProject(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    const result = await requestAgency('project', { method: 'POST', body: payload });
    closeDialog('project-modal');
    form.reset();
    await loadAgency(result.project.id, { silent: true });
    showToast('Project created');
  } catch (error) {
    setText('project-form-error', error.message);
  }
}

async function saveSnapshot(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    await requestAgency('snapshot', {
      method: 'POST',
      body: {
        projectId: agencyState.data.project.id,
        campaignId: payload.campaignId,
        metrics: payload,
      },
    });
    closeDialog('snapshot-modal');
    form.reset();
    await loadAgency(agencyState.data.project.id, { silent: true });
    switchView('campaigns');
    showToast('Performance snapshot saved');
  } catch (error) {
    setText('snapshot-form-error', error.message);
  }
}

function bindAgencyEvents() {
  document.getElementById('agency-auth-form').addEventListener('submit', async event => {
    event.preventDefault();
    const input = document.getElementById('agency-password');
    agencyState.token = input.value.trim();
    try {
      const data = await requestAgency('load');
      persistToken(agencyState.token);
      agencyState.data = data;
      showAgencyApp();
      renderAgency();
      handleZohoReturn();
    } catch (error) {
      setText('agency-auth-error', error.status === 401 ? 'That passphrase did not work.' : error.message);
    }
  });
  document.querySelectorAll('.agency-nav-item').forEach(button => button.addEventListener('click', () => switchView(button.dataset.view)));
  document.querySelectorAll('[data-go-view]').forEach(button => button.addEventListener('click', () => switchView(button.dataset.goView)));
  document.querySelectorAll('[data-range]').forEach(button => button.addEventListener('click', () => {
    agencyState.range = button.dataset.range;
    document.querySelectorAll('[data-range]').forEach(item => item.classList.toggle('active', item === button));
    renderOverview();
    refreshIcons();
  }));
  document.getElementById('agency-project-select').addEventListener('change', event => loadAgency(event.target.value));
  document.getElementById('agency-refresh').addEventListener('click', () => loadAgency(agencyState.data.project.id));
  document.getElementById('agency-new-project').addEventListener('click', () => openDialog('project-modal'));
  document.getElementById('agency-add-snapshot').addEventListener('click', () => openDialog('snapshot-modal'));
  document.getElementById('keyword-search').addEventListener('input', filterKeywords);
  document.getElementById('keyword-status-filter').addEventListener('change', filterKeywords);
  document.getElementById('lead-search').addEventListener('input', renderLeads);
  document.getElementById('lead-stage-filter').addEventListener('change', renderLeads);
  document.getElementById('hide-test-leads').addEventListener('change', renderLeads);
  document.getElementById('project-form').addEventListener('submit', createProject);
  document.getElementById('snapshot-form').addEventListener('submit', saveSnapshot);
  document.getElementById('zoho-config-form').addEventListener('submit', configureZohoClient);
  document.getElementById('email-lead-form').addEventListener('submit', sendLeadEmail);
  document.getElementById('print-report').addEventListener('click', () => window.print());
  document.querySelectorAll('[data-close-modal]').forEach(button => button.addEventListener('click', () => closeDialog(button.dataset.closeModal)));
  document.getElementById('agency-sign-out').addEventListener('click', () => {
    sessionStorage.removeItem(AGENCY_TOKEN_KEY);
    sessionStorage.removeItem(SHARED_TOKEN_KEY);
    agencyState.token = '';
    agencyState.data = null;
    showAuth();
  });
}

async function startAgency() {
  bindAgencyEvents();
  agencyState.token = getToken();
  if (!agencyState.token) {
    showAuth();
    return;
  }
  try {
    await loadAgency('', { silent: true });
    handleZohoReturn();
  } catch (error) {
    if (error.status === 401) {
      sessionStorage.removeItem(AGENCY_TOKEN_KEY);
      showAuth('Your session expired. Sign in again.');
    } else {
      showAuth(error.message);
    }
  }
}

startAgency();
