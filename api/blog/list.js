// Edge function — return paginated blog post list from KV
export const config = { runtime: 'edge' };

export default async function handler(req) {
  const KV_URL   = process.env.KV_REST_API_URL;
  const KV_TOKEN = process.env.KV_REST_API_TOKEN;

  if (!KV_URL || !KV_TOKEN) return json([], 200);

  try {
    const url = new URL(req.url);
    const page  = parseInt(url.searchParams.get('page')  || '0');
    const limit = parseInt(url.searchParams.get('limit') || '12');
    const start = page * limit;
    const end   = start + limit - 1;

    const res = await fetch(KV_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(['LRANGE', 'lofts:blog:posts', start, end]),
    });
    const { result } = await res.json();
    const posts = (result || []).map(s => { try { return JSON.parse(s); } catch { return null; } }).filter(Boolean);

    // Total count
    const countRes = await fetch(KV_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(['LLEN', 'lofts:blog:posts']),
    });
    const { result: total } = await countRes.json();

    return json({ posts, total: total || 0, page, limit });
  } catch (err) {
    return json({ posts: [], total: 0, error: String(err) });
  }
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'public, s-maxage=300', 'access-control-allow-origin': '*' },
  });
}
