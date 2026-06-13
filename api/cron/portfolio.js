// Vercel Cron Job — Portfolio Sync from Asana
// Schedule: 30 3 * * * (3:30am UTC daily)
// Two modes:
//   1. POST with body { items: [...] }  → used by Claude scheduled task (Asana MCP)
//   2. POST with body { action: "check-slugs" } → returns existing slugs
//   3. No body → falls back to Asana REST API (requires ASANA_TOKEN + ASANA_PROJECT_ID)
// All modes require: Authorization: Bearer {CRON_SECRET}

export const config = { runtime: 'edge' };

async function kvCmd(url, token, ...args) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  });
  const j = await res.json();
  return j.result ?? null;
}

function slugify(str) {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
}

export default async function handler(req) {
  const auth   = req.headers.get('authorization') || '';
  const secret = process.env.CRON_SECRET || '';
  if (secret && auth !== `Bearer ${secret}`) {
    return json({ error: 'Unauthorised' }, 401);
  }

  const KV_URL   = process.env.KV_REST_API_URL;
  const KV_TOKEN = process.env.KV_REST_API_TOKEN;
  if (!KV_URL || !KV_TOKEN) return json({ error: 'Missing KV env vars' }, 500);

  // Parse body (may be empty on Vercel-native cron GET triggers)
  let body = {};
  try {
    if (req.method === 'POST') {
      const text = await req.text();
      if (text) body = JSON.parse(text);
    }
  } catch (_) {}

  // ── Mode: check-slugs ────────────────────────────────────────────────────
  if (body.action === 'check-slugs') {
    const slugs = await kvCmd(KV_URL, KV_TOKEN, 'SMEMBERS', 'lofts:portfolio:slugs') || [];
    return json({ slugs });
  }

  // ── Mode: accept pre-fetched items from Claude scheduled task ────────────
  if (Array.isArray(body.items) && body.items.length > 0) {
    const existingSlugs = await kvCmd(KV_URL, KV_TOKEN, 'SMEMBERS', 'lofts:portfolio:slugs') || [];
    let added = 0;
    const results = [];

    for (const item of body.items.slice(0, 2)) {
      const slug = slugify(item.name || '');
      if (!slug) continue;
      if (existingSlugs.includes(slug)) { results.push({ slug, status: 'skipped_duplicate' }); continue; }

      const websiteUrl = (item.url || '').replace(/^https?:\/\//, '');
      const screenshotUrl = websiteUrl
        ? `https://image.thum.io/get/width/1600/crop/900/https://${websiteUrl}`
        : null;

      const portfolio = {
        slug,
        name: item.name,
        url: websiteUrl ? `https://${websiteUrl}` : '',
        industry: item.industry || 'Web Development',
        platform: item.platform || 'WordPress',
        description: item.description || `${item.name} — ${item.industry || 'web'} project.`,
        screenshotUrl,
        asanaGid: item.asanaGid || null,
        createdAt: new Date().toISOString(),
      };

      await Promise.all([
        kvCmd(KV_URL, KV_TOKEN, 'SET', `lofts:portfolio:item:${slug}`, JSON.stringify(portfolio)),
        kvCmd(KV_URL, KV_TOKEN, 'LPUSH', 'lofts:portfolio:items', JSON.stringify({
          slug, name: item.name,
          industry: portfolio.industry, platform: portfolio.platform,
          screenshotUrl, createdAt: portfolio.createdAt,
        })),
        kvCmd(KV_URL, KV_TOKEN, 'SADD', 'lofts:portfolio:slugs', slug),
      ]);

      added++;
      results.push({ slug, name: item.name, status: 'added' });
    }

    return json({ ok: true, mode: 'injected', added, results });
  }

  // ── Mode: Asana REST API fallback ────────────────────────────────────────
  const ASANA_TOKEN = process.env.ASANA_TOKEN;
  const PROJECT_ID  = process.env.ASANA_PROJECT_ID;
  if (!ASANA_TOKEN || !PROJECT_ID) {
    return json({
      error: 'No items in body and ASANA_TOKEN / ASANA_PROJECT_ID env vars are not set.',
      hint: 'Either POST with { items: [...] } from the Claude scheduled task, or add ASANA_TOKEN + ASANA_PROJECT_ID in Vercel dashboard.',
    }, 400);
  }

  let tasks = [];
  try {
    const asanaRes = await fetch(
      `https://app.asana.com/api/1.0/projects/${PROJECT_ID}/tasks?opt_fields=name,custom_fields,notes,completed,permalink_url&limit=100`,
      { headers: { Authorization: `Bearer ${ASANA_TOKEN}` } }
    );
    const asanaJson = await asanaRes.json();
    tasks = asanaJson.data || [];
  } catch (err) {
    return json({ error: 'Asana fetch failed', detail: String(err) }, 500);
  }

  const activeTasks      = tasks.filter(t => !t.completed);
  const existingSlugs    = await kvCmd(KV_URL, KV_TOKEN, 'SMEMBERS', 'lofts:portfolio:slugs') || [];
  let added = 0;
  const results = [];

  for (const task of activeTasks.slice(0, 2)) {
    const slug = slugify(task.name);
    if (existingSlugs.includes(slug)) { results.push({ slug, status: 'skipped_duplicate' }); continue; }

    const fields = {};
    (task.custom_fields || []).forEach(f => { if (f.name && f.text_value) fields[f.name] = f.text_value; });

    const websiteUrl    = (fields['Website URL'] || fields['URL'] || fields['website'] || '').replace(/^https?:\/\//, '');
    const industry      = fields['Industry'] || fields['Category'] || 'Web Development';
    const platform      = fields['Platform'] || fields['Tech Stack'] || 'WordPress';
    const screenshotUrl = websiteUrl
      ? `https://image.thum.io/get/width/1600/crop/900/https://${websiteUrl}`
      : null;

    const portfolio = {
      slug, name: task.name,
      url: websiteUrl ? `https://${websiteUrl}` : '',
      industry, platform,
      description: task.notes || `${task.name} — ${industry} website built on ${platform}.`,
      screenshotUrl,
      asanaGid: task.gid,
      createdAt: new Date().toISOString(),
    };

    await Promise.all([
      kvCmd(KV_URL, KV_TOKEN, 'SET', `lofts:portfolio:item:${slug}`, JSON.stringify(portfolio)),
      kvCmd(KV_URL, KV_TOKEN, 'LPUSH', 'lofts:portfolio:items', JSON.stringify({
        slug, name: task.name, industry, platform, screenshotUrl, createdAt: portfolio.createdAt,
      })),
      kvCmd(KV_URL, KV_TOKEN, 'SADD', 'lofts:portfolio:slugs', slug),
    ]);

    added++;
    results.push({ slug, name: task.name, status: 'added' });
  }

  return json({ ok: true, mode: 'asana-api', added, total: activeTasks.length, results });
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json' } });
}
