// Edge function — return single blog post by slug
export const config = { runtime: 'edge' };

export default async function handler(req) {
  const KV_URL   = process.env.KV_REST_API_URL;
  const KV_TOKEN = process.env.KV_REST_API_TOKEN;
  const url      = new URL(req.url);
  const slug     = url.searchParams.get('slug') || '';

  if (!slug) return json({ error: 'No slug' }, 400);
  if (!KV_URL || !KV_TOKEN) return json({ error: 'KV not configured' }, 500);

  try {
    const res = await fetch(KV_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(['GET', `lofts:blog:post:${slug}`]),
    });
    const { result } = await res.json();
    if (!result) return json({ error: 'Post not found' }, 404);

    const post = JSON.parse(result);
    return json(post);
  } catch (err) {
    return json({ error: String(err) }, 500);
  }
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'public, s-maxage=3600', 'access-control-allow-origin': '*' },
  });
}
