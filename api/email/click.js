import { recordEmailEngagement, signAutomationToken } from '../_lib/automation.js';

export const config = { runtime: 'edge' };

export default async function handler(req) {
  const url = new URL(req.url);
  try {
    const { payload, sequence } = await recordEmailEngagement(url.searchParams.get('t'), 'book-click', {
      userAgent: req.headers.get('user-agent') || '',
    });
    const token = await signAutomationToken({
      a: 'book', p: payload.p, l: payload.l, s: payload.s,
      exp: Math.max(Date.now() + 30 * 86400000, Number(payload.exp || 0)),
    });
    return Response.redirect(`${sequence.origin}/book/?t=${encodeURIComponent(token)}`, 302);
  } catch {
    return Response.redirect(`${url.origin}/book/`, 302);
  }
}
