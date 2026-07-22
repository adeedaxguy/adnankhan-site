export const config = { runtime: 'edge' };

const ADMIN_SECRET = process.env.ADMIN_SECRET;
const KV_URL = process.env.KV_REST_API_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN;

const STAGES = ['new', 'contacted', 'qualified', 'proposal', 'won', 'lost'];

const LOFTS_KEYWORDS = [
  { keyword: 'landing page design service', matchType: 'Exact', status: 'enabled', intent: 'Commercial', volume: 600, kd: 11, cpc: 3.50, source: 'Ahrefs', decision: 'Core' },
  { keyword: 'landing page design agency', matchType: 'Exact', status: 'enabled', intent: 'Commercial', volume: 400, kd: 1, cpc: 3.00, source: 'Ahrefs', decision: 'Core' },
  { keyword: 'landing page design agency', matchType: 'Phrase', status: 'enabled', intent: 'Commercial', volume: 400, kd: 1, cpc: 3.00, source: 'Ahrefs', decision: 'Scale' },
  { keyword: 'landing page agency', matchType: 'Exact', status: 'enabled', intent: 'Commercial', volume: 390, kd: 15, cpc: 7.65, source: 'SEMrush', decision: 'Controlled test' },
  { keyword: 'landing page agency', matchType: 'Phrase', status: 'enabled', intent: 'Commercial', volume: 390, kd: 15, cpc: 7.65, source: 'SEMrush', decision: 'Controlled test' },
  { keyword: 'ppc landing page design', matchType: 'Exact', status: 'enabled', intent: 'Commercial', volume: 200, kd: 1, cpc: 4.50, source: 'Ahrefs', decision: 'Core' },
  { keyword: 'saas landing page design', matchType: 'Exact', status: 'enabled', intent: 'Commercial', volume: 200, kd: 3, cpc: 1.70, source: 'Ahrefs', decision: 'Test' },
  { keyword: 'ecommerce landing page design', matchType: 'Exact', status: 'enabled', intent: 'Commercial', volume: 100, kd: 1, cpc: 3.50, source: 'Ahrefs', decision: 'Test' },
  { keyword: 'high converting landing page design', matchType: 'Exact', status: 'enabled', intent: 'Commercial', volume: 100, kd: 6, cpc: 3.50, source: 'Ahrefs', decision: 'Test' },
  { keyword: 'hire landing page designer', matchType: 'Exact', status: 'enabled', intent: 'Commercial', volume: 90, kd: 8, cpc: 0, source: 'SEMrush', decision: 'Core' },
  { keyword: 'lead generation landing page design', matchType: 'Exact', status: 'enabled', intent: 'Commercial', volume: 60, kd: 3, cpc: 0, source: 'Ahrefs', decision: 'Test' },
  { keyword: 'google ads landing page design', matchType: 'Exact', status: 'enabled', intent: 'Commercial', volume: 40, kd: 2, cpc: 0, source: 'Planner', decision: 'High fit' },
  { keyword: 'conversion focused landing page', matchType: 'Exact', status: 'enabled', intent: 'Commercial', volume: 30, kd: 4, cpc: 0, source: 'Planner', decision: 'High fit' },
  { keyword: 'landing page design service', matchType: 'Phrase', status: 'enabled', intent: 'Commercial', volume: 600, kd: 11, cpc: 3.50, source: 'Ahrefs', decision: 'Scale' },
  { keyword: 'landing page development services', matchType: 'Exact', status: 'paused', intent: 'Mixed', volume: 40, kd: 21, cpc: 15.10, source: 'SEMrush + SpyFu', decision: 'Rejected after review' },
];

const LOFTS_PROJECT = {
  id: 'lofts-studio',
  name: 'Lofts Studio',
  website: 'https://lofts.studio',
  status: 'active',
  health: 'learning',
  currency: 'USD',
  timezone: 'Asia/Karachi',
  owner: 'Adnan',
  goal: 'Qualified landing-page enquiries',
  monthlyBudget: 600,
  channels: ['Google Ads'],
  landingPage: 'https://lofts.studio/services/landing-page-sprint.html',
  primaryConversion: 'Submit lead form',
  tracking: {
    formConversion: 'verified',
    emailDelivery: 'verified',
    gtm: 'verified',
    googleAdsApi: 'not_connected',
    metaAdsApi: 'not_connected',
  },
  campaigns: [{
    id: '24052211013',
    name: '2026-07-22 | SEARCH | LP Form Leads | US+UK | Exact+Phrase | CPC Cap',
    channel: 'Google Ads',
    type: 'Search',
    status: 'enabled',
    launchedAt: '2026-07-23',
    dailyBudget: 20,
    bidStrategy: 'Maximize clicks',
    cpcCap: 4.50,
    locations: ['United States', 'United Kingdom'],
    adGroup: 'Landing Page Service',
    conversionGoal: 'Submit lead form',
    landingPage: 'https://lofts.studio/services/landing-page-sprint.html',
    metrics: { impressions: 0, clicks: 0, cost: 0, conversions: 0, qualified: 0, revenue: 0 },
  }],
  research: {
    completedAt: '2026-07-23',
    tools: ['Google Keyword Planner', 'Ahrefs', 'SEMrush', 'SpyFu'],
    keywords: LOFTS_KEYWORDS,
    negatives: 46,
    summary: 'Exact and phrase match launch focused on commercial landing-page service intent.',
    rejected: [
      { keyword: 'landing page optimization service', reason: 'Estimated CPC near $14; poor fit for the launch cap.' },
      { keyword: 'landing page designer', reason: 'Broad intent and estimated CPC above the launch cap.' },
      { keyword: 'custom landing page design', reason: 'Estimated CPC above $5 with less precise lead intent.' },
      { keyword: 'web design', reason: 'Too broad for the dedicated landing-page offer.' },
    ],
  },
};

async function kvCmd(...args) {
  if (!KV_URL || !KV_TOKEN) return null;
  const res = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  });
  if (!res.ok) return null;
  const json = await res.json();
  return json.result ?? null;
}

function parseJson(value, fallback = null) {
  try { return typeof value === 'string' ? JSON.parse(value) : value; } catch { return fallback; }
}

async function kvList(key, end = 499) {
  const result = await kvCmd('LRANGE', key, '0', String(end));
  return Array.isArray(result) ? result.map(item => parseJson(item, item)) : [];
}

function hashString(value) {
  let hash = 2166136261;
  for (let i = 0; i < value.length; i++) {
    hash ^= value.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(36);
}

function normalizeHash(result) {
  if (!result) return {};
  if (!Array.isArray(result)) return result;
  const output = {};
  for (let i = 0; i < result.length; i += 2) output[result[i]] = result[i + 1];
  return output;
}

function makeLeadId(projectId, lead) {
  if (lead._id) return String(lead._id).slice(0, 96);
  return `legacy-${hashString(`${projectId}|${lead._ts || ''}|${lead.email || ''}|${lead.source || ''}`)}`;
}

function isLikelyTestLead(lead) {
  const value = [lead.name, lead.email, lead.message, lead._subject].filter(Boolean).join(' ');
  return /(\btest(?:ing|er)?\b|\bqa\b|codex|do not contact|debug|example\.com|lalaland|techncodex|texhnxodx)/i.test(value);
}

function sanitizeProject(project) {
  return {
    id: String(project.id || '').slice(0, 64),
    name: String(project.name || '').slice(0, 100),
    website: String(project.website || '').slice(0, 240),
    status: project.status === 'paused' ? 'paused' : 'active',
    health: project.health || 'setup',
    currency: String(project.currency || 'USD').toUpperCase().slice(0, 3),
    timezone: String(project.timezone || 'UTC').slice(0, 64),
    owner: String(project.owner || 'Unassigned').slice(0, 80),
    goal: String(project.goal || 'Qualified leads').slice(0, 160),
    monthlyBudget: Math.max(0, Number(project.monthlyBudget) || 0),
    channels: Array.isArray(project.channels) ? project.channels.slice(0, 8) : [],
    landingPage: String(project.landingPage || '').slice(0, 240),
    primaryConversion: String(project.primaryConversion || 'Lead form').slice(0, 100),
    tracking: project.tracking || {},
    campaigns: Array.isArray(project.campaigns) ? project.campaigns : [],
    research: project.research || { tools: [], keywords: [], rejected: [] },
  };
}

async function getProjects() {
  const custom = normalizeHash(await kvCmd('HGETALL', 'agency:projects'));
  const projects = [LOFTS_PROJECT];
  for (const raw of Object.values(custom)) {
    const project = parseJson(raw);
    if (project && project.id !== LOFTS_PROJECT.id) projects.push(sanitizeProject(project));
  }
  return projects;
}

async function loadRawLeads(projectId) {
  if (projectId === LOFTS_PROJECT.id) return kvList('lofts:submissions');
  return kvList(`agency:leads:${projectId}`);
}

async function loadOverlays() {
  const raw = normalizeHash(await kvCmd('HGETALL', 'agency:lead-overlays'));
  const parsed = {};
  for (const [key, value] of Object.entries(raw)) parsed[key] = parseJson(value, {});
  return parsed;
}

function normalizeLead(projectId, lead, overlays) {
  const id = makeLeadId(projectId, lead);
  const overlay = overlays[`${projectId}:${id}`] || {};
  const source = lead.source || 'contact-form';
  return {
    ...lead,
    id,
    projectId,
    source,
    stage: STAGES.includes(overlay.stage) ? overlay.stage : 'new',
    assignedTo: overlay.assignedTo || '',
    value: Number(overlay.value) || 0,
    nextAction: overlay.nextAction || '',
    lostReason: overlay.lostReason || '',
    isTest: typeof overlay.isTest === 'boolean' ? overlay.isTest : isLikelyTestLead(lead),
    notes: Array.isArray(overlay.notes) ? overlay.notes : [],
    activity: Array.isArray(overlay.activity) ? overlay.activity : [],
    updatedAt: overlay.updatedAt || lead._ts || null,
  };
}

function leadSummary(leads) {
  const real = leads.filter(lead => lead.source !== 'footer-newsletter' && !lead.isTest);
  const won = real.filter(lead => lead.stage === 'won');
  const qualified = real.filter(lead => ['qualified', 'proposal', 'won'].includes(lead.stage));
  return {
    captured: leads.filter(lead => lead.source !== 'footer-newsletter').length,
    leads: real.length,
    testLeads: leads.filter(lead => lead.source !== 'footer-newsletter' && lead.isTest).length,
    newLeads: real.filter(lead => lead.stage === 'new').length,
    qualified: qualified.length,
    won: won.length,
    pipelineValue: real.filter(lead => !['won', 'lost'].includes(lead.stage)).reduce((sum, lead) => sum + lead.value, 0),
    revenue: won.reduce((sum, lead) => sum + lead.value, 0),
  };
}

async function campaignData(project) {
  const snapshots = (await kvList(`agency:campaign-snapshots:${project.id}`, 179))
    .filter(item => item && typeof item === 'object')
    .sort((a, b) => (a._ts || 0) - (b._ts || 0));
  const latestByCampaign = {};
  for (const snapshot of snapshots) latestByCampaign[snapshot.campaignId] = snapshot;
  const campaigns = (project.campaigns || []).map(campaign => ({
    ...campaign,
    metrics: latestByCampaign[campaign.id] || campaign.metrics,
  }));
  return { campaigns, snapshots };
}

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json', 'Cache-Control': 'no-store' },
  });
}

export default async function handler(req) {
  const url = new URL(req.url);
  const token = req.headers.get('x-admin-token');
  if (!ADMIN_SECRET || token !== ADMIN_SECRET) return jsonResponse({ error: 'Unauthorized' }, 401);

  const action = url.searchParams.get('action') || 'load';

  if (action === 'load') {
    const projects = await getProjects();
    const selectedId = url.searchParams.get('project') || projects[0]?.id;
    const selected = projects.find(project => project.id === selectedId) || projects[0];
    if (!selected) return jsonResponse({ error: 'No projects configured.' }, 404);

    const overlays = await loadOverlays();
    const projectLeadSets = await Promise.all(projects.map(async project => {
      const raw = await loadRawLeads(project.id);
      const leads = raw.map(lead => normalizeLead(project.id, lead, overlays));
      return { projectId: project.id, leads, summary: leadSummary(leads) };
    }));
    const selectedSet = projectLeadSets.find(item => item.projectId === selected.id);
    const { campaigns, snapshots } = await campaignData(selected);
    const projectSummaries = projects.map(project => {
      const leadSet = projectLeadSets.find(item => item.projectId === project.id);
      return { ...project, campaigns: undefined, research: undefined, leadSummary: leadSet?.summary || leadSummary([]) };
    });

    return jsonResponse({
      projects: projectSummaries,
      project: { ...selected, campaigns },
      leads: selectedSet?.leads || [],
      leadSummary: selectedSet?.summary || leadSummary([]),
      campaignSnapshots: snapshots,
      stages: STAGES,
      generatedAt: Date.now(),
    });
  }

  if (action === 'lead' && req.method === 'POST') {
    const body = await req.json().catch(() => ({}));
    const projectId = String(body.projectId || '').slice(0, 64);
    const leadId = String(body.leadId || '').slice(0, 96);
    if (!projectId || !leadId) return jsonResponse({ error: 'Missing project or lead.' }, 400);

    const key = `${projectId}:${leadId}`;
    const current = parseJson(await kvCmd('HGET', 'agency:lead-overlays', key), {}) || {};
    const next = { ...current };
    const patch = body.patch || {};
    if (patch.stage && STAGES.includes(patch.stage)) {
      if (patch.stage !== current.stage) {
        next.activity = [{ type: 'stage', from: current.stage || 'new', to: patch.stage, at: Date.now() }, ...(current.activity || [])].slice(0, 50);
      }
      next.stage = patch.stage;
    }
    if (typeof patch.assignedTo === 'string') next.assignedTo = patch.assignedTo.slice(0, 80);
    if (typeof patch.nextAction === 'string') next.nextAction = patch.nextAction.slice(0, 240);
    if (typeof patch.lostReason === 'string') next.lostReason = patch.lostReason.slice(0, 240);
    if (typeof patch.isTest === 'boolean') next.isTest = patch.isTest;
    if (patch.value !== undefined) next.value = Math.max(0, Number(patch.value) || 0);
    if (typeof body.note === 'string' && body.note.trim()) {
      next.notes = [{ id: crypto.randomUUID(), body: body.note.trim().slice(0, 2000), at: Date.now() }, ...(current.notes || [])].slice(0, 50);
      next.activity = [{ type: 'note', at: Date.now() }, ...(next.activity || current.activity || [])].slice(0, 50);
    }
    next.updatedAt = Date.now();
    const saved = await kvCmd('HSET', 'agency:lead-overlays', key, JSON.stringify(next));
    if (saved === null) return jsonResponse({ error: 'Agency storage is unavailable. Nothing was saved.' }, 503);
    return jsonResponse({ ok: true, overlay: next });
  }

  if (action === 'snapshot' && req.method === 'POST') {
    const body = await req.json().catch(() => ({}));
    const projectId = String(body.projectId || '').slice(0, 64);
    const campaignId = String(body.campaignId || '').slice(0, 64);
    if (!projectId || !campaignId) return jsonResponse({ error: 'Missing project or campaign.' }, 400);
    const metrics = body.metrics || {};
    const snapshot = {
      campaignId,
      impressions: Math.max(0, Number(metrics.impressions) || 0),
      clicks: Math.max(0, Number(metrics.clicks) || 0),
      cost: Math.max(0, Number(metrics.cost) || 0),
      conversions: Math.max(0, Number(metrics.conversions) || 0),
      qualified: Math.max(0, Number(metrics.qualified) || 0),
      revenue: Math.max(0, Number(metrics.revenue) || 0),
      source: 'manual',
      _ts: Date.now(),
    };
    const key = `agency:campaign-snapshots:${projectId}`;
    const saved = await kvCmd('LPUSH', key, JSON.stringify(snapshot));
    if (saved === null) return jsonResponse({ error: 'Agency storage is unavailable. Nothing was saved.' }, 503);
    await kvCmd('LTRIM', key, '0', '179');
    return jsonResponse({ ok: true, snapshot });
  }

  if (action === 'project' && req.method === 'POST') {
    const body = await req.json().catch(() => ({}));
    const name = String(body.name || '').trim().slice(0, 100);
    const id = String(body.id || name).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 64);
    if (!name || !id || id === LOFTS_PROJECT.id) return jsonResponse({ error: 'Choose a different project name.' }, 400);
    const project = sanitizeProject({
      id,
      name,
      website: body.website,
      status: 'active',
      health: 'setup',
      currency: body.currency,
      timezone: body.timezone,
      owner: body.owner,
      goal: body.goal,
      monthlyBudget: body.monthlyBudget,
      channels: body.channel ? [String(body.channel).slice(0, 40)] : [],
      tracking: { formConversion: 'not_connected', emailDelivery: 'not_connected', gtm: 'not_connected', googleAdsApi: 'not_connected', metaAdsApi: 'not_connected' },
      campaigns: [],
      research: { tools: [], keywords: [], rejected: [], summary: '' },
    });
    const saved = await kvCmd('HSET', 'agency:projects', id, JSON.stringify(project));
    if (saved === null) return jsonResponse({ error: 'Agency storage is unavailable. Nothing was saved.' }, 503);
    return jsonResponse({ ok: true, project });
  }

  return jsonResponse({ error: 'Unknown action.' }, 400);
}
