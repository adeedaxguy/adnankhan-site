const HANDLERS = new Map([
  ["/api/audit", () => import("./api/audit.js")],
  ["/api/booking", () => import("./api/booking.js")],
  ["/api/chat", () => import("./api/chat.js")],
  ["/api/comments", () => import("./api/comments.js")],
  ["/api/contact", () => import("./api/contact.js")],
  ["/api/google-ads-sync", () => import("./api/google-ads-sync.js")],
  ["/api/og", () => import("./api/og.js")],
  ["/api/unsubscribe", () => import("./api/unsubscribe.js")],
  ["/api/admin/agency", () => import("./api/admin/agency.js")],
  ["/api/admin/data", () => import("./api/admin/data.js")],
  ["/api/blog/list", () => import("./api/blog/list.js")],
  ["/api/blog/post", () => import("./api/blog/post.js")],
  ["/api/cron/blog", () => import("./api/cron/blog.js")],
  ["/api/cron/lead-automation", () => import("./api/cron/lead-automation.js")],
  ["/api/cron/portfolio", () => import("./api/cron/portfolio.js")],
  ["/api/email/click", () => import("./api/email/click.js")],
  ["/api/email/open", () => import("./api/email/open.js")],
  ["/api/google-calendar/callback", () => import("./api/google-calendar/callback.js")],
  ["/api/integrations/growth-os-mail", () => import("./api/integrations/growth-os-mail.js")],
  ["/api/zoho/callback", () => import("./api/zoho/callback.js")],
]);

const REDIRECTS = new Map([
  ["/notes", "/blog/"],
  ["/notes/", "/blog/"],
  ["/work.html", "/portfolio/"],
  ["/services/shopify-developer-ae.html", "/services/shopify-developer-uae.html"],
  ["/blog/shopify-developer-freelance-rates.html", "/blog/hire-shopify-developer-guide-2026.html"],
  ["/blog/landing-page-design-cost.html", "/blog/landing-page-conversion-rate-optimization.html"],
  ["/blog/pricing-page-design.html", "/blog/conversion-focused-web-design.html"],
  ["/blog/free-seo-audit-report-pdf.html", "/free-audit"],
  ["/blog/free-site-audit-report.html", "/free-audit"],
  ["/blog/site-audit-report-pdf.html", "/free-audit"],
  ["/blog/site-audit-report-sample.html", "/free-audit"],
  ["/blog/website-audit-report-generator-free.html", "/free-audit"],
  ["/blog/website-audit-report-sample-pdf.html", "/free-audit"],
  ["/blog/website-structure-audit-report-pdf.html", "/free-audit"],
  ["/blog/seo-compatibility-checker-free.html", "/tools/seo-aeo-checker.html"],
  ["/blog/seo-compatibility-checker-online-free.html", "/tools/seo-aeo-checker.html"],
  ["/blog/seo-compatibility-checker-online.html", "/tools/seo-aeo-checker.html"],
  ["/blog/website-technical-seo-checker.html", "/tools/seo-aeo-checker.html"],
  ["/blog/small-business-website-cost-2026.html", "/blog/custom-website-vs-template.html"],
]);

const SECURITY_HEADERS = {
  "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "SAMEORIGIN",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
};

function redirect(url, destination, status = 308) {
  return Response.redirect(new URL(destination, url), status);
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

async function recoveryContact(request, env) {
  if (request.method !== "POST") return json({ error: "POST only" }, 405);

  let payload;
  try {
    const type = request.headers.get("content-type") || "";
    payload = type.includes("application/json")
      ? await request.json()
      : Object.fromEntries(await request.formData());
  } catch {
    return json({ success: false, message: "Invalid form submission." }, 400);
  }

  const clean = (value, limit = 4000) => String(value || "").trim().slice(0, limit);
  if (clean(payload._gotcha, 200)) return json({ success: true, message: "Received" });

  const source = clean(payload.source || "contact-form", 100);
  const newsletter = source === "footer-newsletter";
  const email = clean(payload.email, 254).toLowerCase();
  const name = clean(payload.name, 120);
  const phone = clean(payload.phone, 32);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ success: false, message: "Enter a valid email address." }, 400);
  }
  if (!newsletter && name.length < 2) return json({ success: false, message: "Enter your name." }, 400);
  const phoneDigits = phone.replace(/\D/g, "");
  if (!newsletter && (phoneDigits.length < 7 || phoneDigits.length > 15)) {
    return json({ success: false, message: "Enter a valid phone or WhatsApp number, including your country code." }, 400);
  }

  const endpoint = String(env.GROWTH_OS_INQUIRY_URL || "");
  if (!endpoint) {
    return json({ success: false, message: "Please email hi@lofts.studio while the enquiry service is recovering." }, 503);
  }

  const details = clean(
    [payload.focus || payload.bottleneck, payload.message || payload.project || payload.details]
      .filter(Boolean)
      .join("\n") || (newsletter ? "Newsletter subscription" : "Website project enquiry"),
    3000,
  );
  const submissionId = clean(payload._submissionId, 96).replace(/[^a-zA-Z0-9-]/g, "") || crypto.randomUUID();

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        Origin: "https://lofts.studio",
        "Content-Type": "application/json",
        "Idempotency-Key": `lofts-recovery-${submissionId}`,
      },
      body: JSON.stringify({
        name: newsletter ? email.split("@")[0] : name,
        email,
        phone: newsletter ? "" : phone,
        company: clean(payload.company || payload.business || payload.website || (newsletter ? "Newsletter" : "Inbound project inquiry"), 180),
        website: /^https?:\/\//i.test(String(payload.website || "")) ? payload.website : "",
        message: details,
        consent: true,
        source,
        attribution: {
          landing_page: clean(payload.landingPage || payload.page, 500) || null,
          referrer: clean(payload.referrer, 500) || null,
          utm_source: clean(payload.utm_source, 120) || null,
          utm_medium: clean(payload.utm_medium, 120) || null,
          utm_campaign: clean(payload.utm_campaign, 120) || null,
        },
      }),
    });
    if (!response.ok) throw new Error(`Growth OS returned ${response.status}`);
    return json({ success: true, message: "Received", submissionId, followUp: "forwarded" });
  } catch {
    return json({ success: false, message: "Please email hi@lofts.studio while the enquiry service is recovering." }, 503);
  }
}

function withHeaders(response, pathname) {
  const headers = new Headers(response.headers);
  for (const [key, value] of Object.entries(SECURITY_HEADERS)) headers.set(key, value);
  if (pathname.startsWith("/assets/") && response.ok) {
    headers.set("Cache-Control", "public, max-age=31536000, immutable");
  }
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

const ENV_KEYS = [
  "ADMIN_SECRET",
  "COMMENTS_ADMIN_TOKEN",
  "CONTACT_EMAIL",
  "CONTACT_EMAIL_BCC",
  "CONTACT_EMAIL_CC",
  "CRON_SECRET",
  "GROWTH_OS_INQUIRY_URL",
  "GROWTH_OS_SERVICE_TOKEN",
  "KV_REST_API_READ_ONLY_TOKEN",
  "KV_REST_API_TOKEN",
  "KV_REST_API_URL",
  "KV_URL",
  "OPENROUTER_API_KEY",
  "REDIS_URL",
  "RESEND_API_KEY",
  "TURNSTILE_SECRET_KEY",
  "SITE_URL",
];

function hydrateProcessEnv(env) {
  for (const key of ENV_KEYS) {
    if (typeof env[key] === "string") process.env[key] = env[key];
  }
}

async function invoke(handler, request, context) {
  const response = await handler(request, context);
  return response instanceof Response
    ? response
    : new Response(JSON.stringify(response ?? null), { headers: { "content-type": "application/json" } });
}

async function fetchStaticAsset(request, env) {
  const original = new URL(request.url);
  const candidates = [original.pathname];

  if (original.pathname === "/") {
    candidates.push("/index.html");
  } else if (original.pathname.endsWith("/")) {
    candidates.push(`${original.pathname}index.html`);
  } else if (!/\.[^/]+$/.test(original.pathname)) {
    candidates.push(`${original.pathname}.html`, `${original.pathname}/index.html`);
  }

  for (const pathname of candidates) {
    const assetUrl = new URL(original);
    assetUrl.pathname = pathname;
    const response = await env.ASSETS.fetch(new Request(assetUrl, request));
    if (response.status !== 404) return response;
  }

  const notFoundUrl = new URL(original);
  notFoundUrl.pathname = "/404.html";
  const notFound = await env.ASSETS.fetch(new Request(notFoundUrl, request));
  return new Response(notFound.body, {
    status: 404,
    headers: notFound.headers,
  });
}

export default {
  async fetch(request, env, context) {
    globalThis.__LOFTS_ENV = env;
    hydrateProcessEnv(env);
    const url = new URL(request.url);

    if (url.hostname === "www.lofts.studio") {
      url.hostname = "lofts.studio";
      return Response.redirect(url, 308);
    }

    if (url.pathname === "/notes" || url.pathname.startsWith("/notes/")) {
      return redirect(url, "/blog/");
    }

    const mapped = REDIRECTS.get(url.pathname);
    if (mapped) return redirect(url, mapped);

    const go = url.pathname.match(/^\/go\/([^/]+)$/);
    if (go) return Response.redirect(`https://go.lofts.studio/go/${encodeURIComponent(go[1])}`, 307);

    if (url.pathname === "/api/contact" && (!env.KV_REST_API_URL || !env.KV_REST_API_TOKEN)) {
      return withHeaders(await recoveryContact(request, env), url.pathname);
    }

    const loadHandler = HANDLERS.get(url.pathname);
    if (loadHandler) {
      const { default: handler } = await loadHandler();
      return withHeaders(await invoke(handler, request, context), url.pathname);
    }

    return withHeaders(await fetchStaticAsset(request, env), url.pathname);
  },

  async scheduled(controller, env, context) {
    const headers = { Authorization: `Bearer ${env.CRON_SECRET || ""}` };
    let path = "/api/cron/lead-automation";
    if (controller.cron === "0 3 * * *") path = "/api/cron/blog";
    if (controller.cron === "30 3 * * *") path = "/api/cron/portfolio";
    context.waitUntil(this.fetch(new Request(`https://lofts.studio${path}`, { headers }), env, context));
  },
};

