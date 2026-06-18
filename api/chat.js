// Vercel Edge Function — proxies chat requests to OpenRouter.
// OpenRouter is a single API that gives you access to multiple LLMs.
// Add OPENROUTER_API_KEY in Vercel project Settings → Environment Variables.
// Get a key (no credit card required) at https://openrouter.ai/keys
//
// Free OpenRouter models share an upstream rate limit, so this proxy tries a
// chain of models in order — first success wins. Override OPENROUTER_MODEL to
// force a single model and skip the fallback chain.
//
export const config = { runtime: 'edge' };

// Models ordered to prefer NON-reasoning instruct models first.
// Reasoning models (Nemotron, Qwen-next, Kimi) leak chain-of-thought
// into replies — Gemma and standard instruct models are clean.
const MODEL_CHAIN = [
  'google/gemma-4-31b-it:free',
  'google/gemma-4-26b-a4b-it:free',
  'qwen/qwen3-next-80b-a3b-instruct:free',
  'moonshotai/kimi-k2.6:free',
  'nvidia/nemotron-3-super-120b-a12b:free',
];

const SYSTEM = `You are the Lofts Studio assistant — friendly, concise, and warmly persuasive.
About Lofts Studio: A senior web engineering studio run by brothers Adnan Khan (Multan, Pakistan) and Irfan Khan (Dubai, UAE). Deep delivery history across ecommerce, local business, and custom platforms. Both Top Rated on Upwork. 100% Job Success Score. Works with US, UK, and GCC-funded founders.
Services: Shopify Development, WooCommerce Development, Shopify Plus Migration, Speed Optimization, Conversion Rate Optimization, Technical SEO Audit, Landing Page Sprint, Custom App Development, AI Calling Agents, AI Workflow Automation, Design & Branding.
Commercial details: Do not provide public numbers, ranges, or package tiers. If asked, explain that Lofts Studio scopes privately after reviewing the project and point them to the contact form.
Process: Clear scope, clear milestones, clear launch date. Async-first (Loom over meetings). Daily updates. 30 days post-launch support included.
Voice: Calm, senior, evidence-led. Never pushy. Never use exclamation marks. Speak in the third person about the founders. Suggest the contact form or email if they're qualified.
CRITICAL OUTPUT RULES — these override everything else:
- Reply ONLY with the final answer to the visitor. Never include reasoning, planning, internal thinking, scratchpad notes, or chain-of-thought.
- NEVER start a reply with phrases like "Okay," / "Let me think" / "The user is asking" / "Let me recall" / "I need to" / "Hmm,"
- NEVER write meta-commentary about the visitor's intent ("this person is probably evaluating...").
- NEVER use <think>, <thinking>, or any reasoning tags.
- Speak DIRECTLY to the visitor as if you are the assistant talking. First word of every reply is the actual answer.
If the visitor asks about commercial terms or ranges, do not provide numbers. Say Lofts Studio scopes privately after reviewing the project and suggest the contact form on the homepage.
If they want to book a call, recommend they fill out the contact form on the homepage — the team replies within 4 hours.
If they ask for an email address, share: hi@lofts.studio — and mention the contact form is even faster.
If they ask off-topic (weather, jokes, code help) gently redirect: "I'm here to help with questions about Lofts Studio — happy to chat about your project."
Keep responses under 90 words. End with one helpful next step (contact form or hi@lofts.studio).`;

const FALLBACK = "I'm not connected to the AI service right now. Reach the team at hi@lofts.studio or use the contact form on the homepage — replies within four hours.";

async function kvLogChat(messages, reply, model) {
  const KV_URL   = process.env.KV_REST_API_URL;
  const KV_TOKEN = process.env.KV_REST_API_TOKEN;
  if (!KV_URL || !KV_TOKEN) return;
  try {
    const lastUserMsg = [...messages].reverse().find(m => m.role === 'user')?.content || '';
    const entry = {
      _ts: Date.now(),
      model,
      messageCount: messages.length,
      lastUserMessage: lastUserMsg.slice(0, 300),
      lastReply: reply.slice(0, 300),
      thread: messages.slice(-6).map(m => ({ role: m.role, content: m.content.slice(0, 400) })),
    };
    await fetch(KV_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(['LPUSH', 'lofts:chats', JSON.stringify(entry)]),
    });
  } catch { /* non-blocking */ }
}

export default async function handler(req) {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'POST only' }), { status: 405 });
  }

  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ reply: FALLBACK }), {
      status: 200, headers: { 'content-type': 'application/json' }
    });
  }

  // If user pinned a specific model, use just that; otherwise try the chain.
  const forced = process.env.OPENROUTER_MODEL;
  const models = forced ? [forced] : MODEL_CHAIN;

  let body;
  try { body = await req.json(); } catch { body = {}; }
  const messages = Array.isArray(body.messages) ? body.messages.slice(-12) : [];

  const safeMessages = messages
    .filter(m => m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string')
    .map(m => ({ role: m.role, content: m.content.slice(0, 1500) }));

  const payloadBase = {
    temperature: 0.5,
    max_tokens: 240,
    messages: [{ role: 'system', content: SYSTEM }, ...safeMessages],
    // OpenRouter: tell reasoning-tuned models to exclude reasoning tokens from the visible reply
    reasoning: { exclude: true, effort: 'low' },
    // Belt-and-braces: NVIDIA Nemotron's vendor flag for non-reasoning mode
    extra_body: { chat_template_kwargs: { thinking: false } },
  };

  /** Strip any leaked chain-of-thought from the model's reply.
   *  Handles three patterns:
   *  1. <think>…</think> or <thinking>…</thinking> tagged blocks
   *  2. Replies starting with reasoning markers like "Okay, the user is asking..."
   *  3. Multi-paragraph replies whose first paragraph is meta-commentary
   */
  function sanitizeReply(text) {
    if (!text) return text;
    let out = text;

    // 1. Strip tagged reasoning blocks (whole-message OR prefix)
    out = out.replace(/<think(?:ing)?>[\s\S]*?<\/think(?:ing)?>/gi, '').trim();
    // Unclosed reasoning prefix (some models open <think> and never close it)
    out = out.replace(/^<think(?:ing)?>[\s\S]*?(?=\n\n|$)/i, '').trim();

    // 2. Strip leading reasoning sentences (greedy: kill ANY paragraph
    //    starting with a reasoning marker until we hit a non-reasoning paragraph)
    const REASONING_STARTS = /^(okay,?\s|hmm,?\s|let me\s|the user (is|wants|seems|asked|mentioned)|i need to\s|i should\s|first,?\s+let me|so,?\s+the user|alright,?\s|wait,?\s+the user)/i;
    const paragraphs = out.split(/\n\s*\n/);
    let firstClean = 0;
    while (firstClean < paragraphs.length && REASONING_STARTS.test(paragraphs[firstClean].trim())) {
      firstClean += 1;
    }
    if (firstClean > 0 && firstClean < paragraphs.length) {
      out = paragraphs.slice(firstClean).join('\n\n').trim();
    } else if (firstClean === paragraphs.length) {
      // Whole reply was reasoning — return a clean fallback
      return "Lofts Studio scopes each project privately after reviewing the work. The fastest way to get the right next step is the contact form on the homepage — Adnan replies in four hours with three specific suggestions for your case.";
    }

    return out.trim();
  }

  let lastError = null;
  let modelTried = null;

  // Per-model timeout so a single stuck model can't burn the function runtime.
  // Vercel hobby tier kills the function at 10s — we keep total below 9s.
  const PER_MODEL_TIMEOUT_MS = 3500;

  for (const model of models) {
    modelTried = model;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), PER_MODEL_TIMEOUT_MS);

    try {
      const r = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'https://adnank.vercel.app',
          'X-Title': 'Adnan K. Studio',
        },
        body: JSON.stringify({ model, ...payloadBase }),
        signal: controller.signal,
      });
      clearTimeout(timer);

      if (r.ok) {
        const data = await r.json();
        const rawReply = data?.choices?.[0]?.message?.content?.trim();
        const cleaned = sanitizeReply(rawReply);
        if (cleaned) {
          // Log to KV inbox (non-blocking)
          kvLogChat(safeMessages, cleaned, model);
          return new Response(JSON.stringify({ reply: cleaned, model }), {
            status: 200,
            headers: { 'content-type': 'application/json', 'cache-control': 'no-store' },
          });
        }
      }

      lastError = await r.text();
      // 429 / 404 / 5xx → fall through to next model
    } catch (e) {
      clearTimeout(timer);
      lastError = String(e).slice(0, 200);
    }
  }

  // All models failed
  return new Response(JSON.stringify({
    reply: "All the free models are busy at the moment. Quickest path is to use the contact form on the homepage directly &mdash; he replies within four hours.",
    error: (lastError || '').slice(0, 240),
    lastModel: modelTried,
  }), { status: 200, headers: { 'content-type': 'application/json' } });
}
