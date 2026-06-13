// Vercel Cron Job — Daily Blog Post Generator
// Schedule: 0 3 * * * (3am UTC daily)
// Requires env vars: OPENROUTER_API_KEY, KV_REST_API_URL, KV_REST_API_TOKEN, CRON_SECRET

export const config = { runtime: 'edge' };

// Rotating keyword list — researched for Lofts Studio target market (US/UK SMBs)
const KEYWORDS = [
  { kw: 'shopify development agency', title: 'How to Choose the Right Shopify Development Agency (2026 Guide)' },
  { kw: 'wordpress speed optimization', title: 'WordPress Speed Optimization: The Complete Technical Guide for 2026' },
  { kw: 'shopify plus migration', title: 'Shopify Plus Migration: Everything You Need to Know Before You Switch' },
  { kw: 'custom shopify theme development', title: 'Custom Shopify Theme vs Pre-built: Which Actually Converts Better?' },
  { kw: 'woocommerce vs shopify', title: 'WooCommerce vs Shopify in 2026: An Honest Comparison for Growing Brands' },
  { kw: 'ecommerce conversion rate optimization', title: 'Ecommerce CRO: 15 Proven Changes That Lift Conversion Rates' },
  { kw: 'shopify store redesign', title: 'When and How to Redesign Your Shopify Store Without Losing Sales' },
  { kw: 'headless shopify development', title: 'Headless Shopify: Is It Right for Your Business in 2026?' },
  { kw: 'wordpress web design agency', title: 'What to Expect When Hiring a WordPress Web Design Agency' },
  { kw: 'shopify page speed optimization', title: 'Shopify Page Speed: Why It Matters and How to Get 90+ Lighthouse Scores' },
  { kw: 'ecommerce website redesign', title: 'The E-commerce Website Redesign Playbook: Avoid the Mistakes That Kill Conversions' },
  { kw: 'shopify plus agency UK', title: 'Finding the Best Shopify Plus Agency in the UK: A Buyer\'s Guide' },
  { kw: 'wordpress maintenance service', title: 'WordPress Maintenance: What\'s Actually Included and Why It Matters' },
  { kw: 'shopify development cost', title: 'How Much Does Shopify Development Actually Cost? (Real Pricing Breakdown)' },
  { kw: 'b2b website design', title: 'B2B Website Design in 2026: What Buyers Expect Before They Contact You' },
  { kw: 'ecommerce technical seo', title: 'Technical SEO for Ecommerce: The Complete Shopify & WooCommerce Checklist' },
  { kw: 'shopify checkout optimization', title: 'Shopify Checkout Optimization: 12 Tweaks That Reduce Cart Abandonment' },
  { kw: 'webflow vs wordpress', title: 'Webflow vs WordPress in 2026: Which Platform Should Your Business Choose?' },
  { kw: 'insurance website design', title: 'Insurance Website Design: Trust Signals That Turn Browsers Into Leads' },
  { kw: 'landing page design agency', title: 'Landing Page Design: Why Most Agency Pages Fail (and How to Fix Yours)' },
  { kw: 'shopify subscription app', title: 'The Best Shopify Subscription Setups for DTC Brands in 2026' },
  { kw: 'wordpress plugin development', title: 'Custom WordPress Plugin vs Off-the-shelf: When to Build Your Own' },
  { kw: 'ecommerce website audit', title: 'How to Audit Your E-commerce Website: A Step-by-Step Framework' },
  { kw: 'shopify migration service', title: 'Migrating to Shopify: The Complete Step-by-Step Guide (No Data Loss)' },
  { kw: 'next.js website development', title: 'Next.js for Marketing Sites: Faster, Better SEO, Lower Bounce Rate' },
  { kw: 'website redesign checklist', title: 'The 40-Point Website Redesign Checklist You Need Before Going Live' },
  { kw: 'shopify theme customization', title: 'Shopify Theme Customization: What\'s Possible Without a Developer?' },
  { kw: 'web design for small business UK', title: 'Web Design for Small Business in the UK: What Actually Works in 2026' },
  { kw: 'ecommerce website development cost', title: 'E-commerce Website Development Cost: Real Numbers for 2026' },
  { kw: 'wordpress vs shopify for ecommerce', title: 'WordPress vs Shopify for E-commerce: The Definitive 2026 Comparison' },
];

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
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 80);
}

export default async function handler(req) {
  // Security: Vercel passes Authorization header for cron jobs
  const auth = req.headers.get('authorization') || '';
  const secret = process.env.CRON_SECRET || '';
  if (secret && auth !== `Bearer ${secret}`) {
    return new Response(JSON.stringify({ error: 'Unauthorised' }), { status: 401, headers: { 'content-type': 'application/json' } });
  }

  const KV_URL   = process.env.KV_REST_API_URL;
  const KV_TOKEN = process.env.KV_REST_API_TOKEN;
  const OR_KEY   = process.env.OPENROUTER_API_KEY;

  if (!KV_URL || !KV_TOKEN || !OR_KEY) {
    return new Response(JSON.stringify({ error: 'Missing env vars' }), { status: 500, headers: { 'content-type': 'application/json' } });
  }

  // Pick keyword by day-of-year so we never repeat until 365 days pass
  const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000);
  const entry = KEYWORDS[dayOfYear % KEYWORDS.length];

  // Check if we already published this keyword this week (avoid duplicates)
  const existingKeys = await kvCmd(KV_URL, KV_TOKEN, 'LRANGE', 'lofts:blog:slugs', 0, 99);
  const slug = slugify(entry.title);
  if (existingKeys && existingKeys.includes(slug)) {
    return new Response(JSON.stringify({ skipped: true, reason: 'Already published', slug }), { headers: { 'content-type': 'application/json' } });
  }

  const now = new Date().toISOString();

  // Generate post via OpenRouter
  const systemPrompt = `You are an expert web development content writer for Lofts Studio, a UK/US web studio run by two brothers — Adnan Khan (Multan) and Irfan Khan (Dubai). The studio specialises in Shopify, WordPress, and custom web builds. Write for business owners in the US and UK who are researching web development, not technical developers. Tone: authoritative but conversational, like a knowledgeable friend. Never be salesy. Use UK/US English.`;

  const userPrompt = `Write a 2,000+ word blog post targeting the keyword: "${entry.kw}"
Title: "${entry.title}"

Requirements:
- H2 and H3 subheadings (use markdown ## and ###)
- Target keyword in first 100 words and in at least 2 H2s
- At least 5 actionable sections with real examples
- Include a "Quick Summary" box at the top (3 bullet points, what readers will learn)
- Natural keyword variations throughout (LSI keywords)
- End with a concise FAQ section (4-5 questions)
- Do NOT mention or link to Lofts Studio in the body (subtle brand authority only)
- Word count: 2,000–2,500 words

Return ONLY valid JSON in this exact format (no markdown wrapper, no extra text):
{
  "slug": "${slug}",
  "title": "${entry.title}",
  "keyword": "${entry.kw}",
  "metaTitle": "60-char SEO title here",
  "metaDescription": "150-char meta description here",
  "excerpt": "2-sentence summary for blog listing",
  "content": "full markdown content here",
  "readingMinutes": 8
}`;

  let post;
  try {
    const aiRes = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${OR_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://lofts.studio',
        'X-Title': 'Lofts Studio Blog Automation',
      },
      body: JSON.stringify({
        model: 'anthropic/claude-3.5-haiku',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user',   content: userPrompt },
        ],
        max_tokens: 4000,
        temperature: 0.7,
      }),
    });

    const aiJson = await aiRes.json();
    const raw = aiJson.choices?.[0]?.message?.content || '';

    // Strip any accidental markdown wrapper
    const jsonStr = raw.replace(/^```json\s*/i, '').replace(/^```\s*/i, '').replace(/```\s*$/i, '').trim();
    post = JSON.parse(jsonStr);
  } catch (err) {
    return new Response(JSON.stringify({ error: 'AI generation failed', detail: String(err) }), { status: 500, headers: { 'content-type': 'application/json' } });
  }

  post.createdAt = now;
  post.slug = slug; // ensure consistent slug

  // Save to KV
  const postKey = `lofts:blog:post:${slug}`;
  const meta = { slug, title: post.title, excerpt: post.excerpt, keyword: post.keyword, createdAt: now, readingMinutes: post.readingMinutes || 8 };

  await Promise.all([
    kvCmd(KV_URL, KV_TOKEN, 'SET', postKey, JSON.stringify(post)),
    kvCmd(KV_URL, KV_TOKEN, 'LPUSH', 'lofts:blog:posts', JSON.stringify(meta)),
    kvCmd(KV_URL, KV_TOKEN, 'LPUSH', 'lofts:blog:slugs', slug),
  ]);

  return new Response(JSON.stringify({ ok: true, slug, title: post.title, keyword: post.keyword }), {
    headers: { 'content-type': 'application/json' },
  });
}
