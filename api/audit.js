// Vercel Function — Website Audit Tool (v3)
// Client-ready report with technical, SEO, performance, design, trust, and broken-link checks.

const TIMEOUT_MS = 9000;
const LINK_AUDIT_LIMIT = 24;
const LINK_TIMEOUT_MS = 3200;

export default async function handler(req, res) {
  const webReq = await toWebRequest(req);
  const response = await handleAuditRequest(webReq);
  if (res && typeof res.setHeader === 'function') return sendNodeResponse(res, response);
  return response;
}

async function handleAuditRequest(req) {
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors() });
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);

  let body;
  try { body = await req.json(); } catch { body = {}; }
  const isAeoMode = body.mode === 'aeo';

  let rawUrl = (body.url || '').trim();
  if (!rawUrl) return json({ error: 'No URL provided' }, 400);
  const enteredWithoutProtocol = !/^https?:\/\//i.test(rawUrl);
  if (enteredWithoutProtocol) rawUrl = 'https://' + rawUrl.replace(/^\/+/, '');
  let url;
  try { url = new URL(rawUrl); } catch { return json({ error: 'Invalid URL' }, 400); }

  const results = {};
  const errors  = {};

  // ── Fetch the page ─────────────────────────────────────────────
  let html = '', finalUrl = url.href, statusCode = 0, headers = {}, ttfbMs = 0;

  const fetchPage = async (targetUrl) => {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
    const t0 = Date.now();
    const res = await fetch(targetUrl.href, {
      signal: ctrl.signal,
      redirect: 'follow',
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; LoftsStudio-Audit/1.0)', 'Accept': 'text/html,application/xhtml+xml' },
    });
    clearTimeout(timer);
    return {
      ttfbMs: Date.now() - t0,
      statusCode: res.status,
      finalUrl: res.url || targetUrl.href,
      headers: Object.fromEntries(res.headers.entries()),
      html: await res.text(),
    };
  };

  try {
    ({ html, finalUrl, statusCode, headers, ttfbMs } = await fetchPage(url));
  } catch (e) {
    if (enteredWithoutProtocol && url.protocol === 'https:') {
      try {
        url = new URL(url.href.replace(/^https:/i, 'http:'));
        ({ html, finalUrl, statusCode, headers, ttfbMs } = await fetchPage(url));
      } catch (fallbackError) {
        errors.fetch = String(fallbackError).slice(0, 120);
      }
    } else {
      errors.fetch = String(e).slice(0, 120);
    }
  }

  const textContent = html ? htmlToText(html) : '';
  let linkAudit = emptyLinkAudit();
  let technicalData = {};

  // ════════════════════════════════════════════
  //  CATEGORY: TECHNICAL
  // ════════════════════════════════════════════

  results.https = {
    pass: url.protocol === 'https:',
    label: 'HTTPS / SSL certificate',
    value: url.protocol === 'https:' ? 'Secure connection active' : 'Site is running on HTTP — no SSL',
    impact: 'critical', category: 'technical',
    fix: 'Install a free SSL certificate via your hosting provider (Let\'s Encrypt). Most hosts do this in one click.',
  };

  results.httpsRedirect = {
    pass: finalUrl.startsWith('https://'),
    label: 'HTTP → HTTPS redirect',
    value: finalUrl.startsWith('https://') ? 'All traffic forces HTTPS' : 'HTTP traffic is NOT redirected to HTTPS',
    impact: 'high', category: 'technical',
    fix: 'Add a 301 redirect from http:// to https:// in your .htaccess or server config.',
  };

  results.status = {
    pass: statusCode >= 200 && statusCode < 300,
    label: 'Page loads successfully (HTTP 200)',
    value: statusCode ? `HTTP ${statusCode}` : 'Could not reach site',
    impact: 'critical', category: 'technical',
    fix: 'Check your hosting — the page may be returning an error or be unreachable.',
  };

  results.secHeaders = {
    pass: !!(headers['strict-transport-security'] || headers['x-frame-options'] || headers['x-content-type-options']),
    label: 'Security headers (HSTS, X-Frame)',
    value: headers['strict-transport-security'] ? 'HSTS + security headers active' : 'Missing security headers',
    impact: 'medium', category: 'technical',
    fix: 'Add HSTS, X-Frame-Options, and X-Content-Type-Options headers in your server or CDN config.',
  };

  if (html) {
    const isNoindex = /meta[^>]+name=["']robots["'][^>]*noindex/i.test(html) || /meta[^>]+content=["'][^"']*noindex/i.test(html);
    results.noindex = {
      pass: !isNoindex,
      label: 'Google can index this page',
      value: isNoindex ? 'NOINDEX tag found — Google will NOT rank this page' : 'Page is indexable by Google',
      impact: 'critical', category: 'technical',
      fix: 'Remove the noindex meta tag or update your robots.txt. This is blocking all Google traffic.',
    };

    const hasCanonical = /rel=["']canonical["']/i.test(html);
    results.canonical = {
      pass: hasCanonical,
      label: 'Canonical URL tag',
      value: hasCanonical ? 'Canonical tag present' : 'No canonical tag — duplicate content risk',
      impact: 'medium', category: 'technical',
      fix: 'Add <link rel="canonical" href="https://yourdomain.com/page/"> to the <head> of every page.',
    };

    const linkInventory = extractLinks(html, finalUrl);
    linkAudit = await auditLinks(linkInventory, finalUrl, html, isAeoMode ? 8 : LINK_AUDIT_LIMIT);
    const brokenCount = linkAudit.broken.length;
    results.brokenLinks = {
      pass: brokenCount === 0,
      label: 'Broken links on the page',
      value: linkAudit.checked
        ? brokenCount
          ? `${brokenCount} broken link${brokenCount === 1 ? '' : 's'} found in ${linkAudit.checked} checked`
          : `${linkAudit.checked} links checked, no broken links found`
        : 'No checkable links found',
      impact: brokenCount > 2 ? 'high' : brokenCount ? 'medium' : 'low',
      category: 'technical',
      note: brokenCount ? `First issue: ${linkAudit.broken[0].url}` : linkAudit.unchecked.length ? `${linkAudit.unchecked.length} links could not be verified quickly` : 'Navigation paths look healthy from this page',
      fix: brokenCount ? 'Repair or redirect broken links so visitors and Google do not hit dead ends.' : '',
      details: linkAudit.broken.slice(0, 8).map(link => ({
        url: link.url,
        status: link.status || link.error || 'unreachable',
        text: link.text || 'Link',
      })),
    };

    // ════════════════════════════════════════════
    //  CATEGORY: SEO
    // ════════════════════════════════════════════

    const titleMatch = html.match(/<title[^>]*>([^<]{1,200})<\/title>/i);
    const titleText  = titleMatch ? titleMatch[1].trim() : '';
    const titleLen   = titleText.length;
    results.title = {
      pass: titleLen >= 30 && titleLen <= 65,
      label: 'Page title tag (SEO)',
      value: titleText ? `"${titleText.slice(0, 60)}${titleText.length > 60 ? '…' : ''}" (${titleLen} chars)` : 'No title tag found',
      impact: 'high', category: 'seo',
      note: !titleText ? 'Missing — critical SEO issue' : titleLen < 30 ? 'Too short — add more keywords' : titleLen > 65 ? 'Too long — Google truncates at ~65 chars' : 'Good length',
      fix: !titleText ? 'Add a <title> tag in the <head>. Use format: "Primary Keyword | Brand Name".' : titleLen > 65 ? `Shorten to under 65 characters. Remove filler words.` : titleLen < 30 ? 'Expand the title to include more keywords (30-65 chars is ideal).' : '',
    };

    const descMatch = html.match(/meta[^>]+name=["']description["'][^>]*content=["']([^"']{1,400})["']/i)
                   || html.match(/meta[^>]+content=["']([^"']{1,400})["'][^>]*name=["']description["']/i);
    const descText = descMatch ? descMatch[1].trim() : '';
    const descLen  = descText.length;
    results.metaDesc = {
      pass: descLen >= 100 && descLen <= 165,
      label: 'Meta description',
      value: descText ? `${descLen} characters` : 'No meta description found',
      impact: 'high', category: 'seo',
      note: !descText ? 'Missing — Google will auto-generate, often badly' : descLen < 100 ? 'Too short — add more detail' : descLen > 165 ? 'Too long — will be cut off in search results' : 'Good length',
      fix: !descText ? 'Add a meta description tag: <meta name="description" content="Your 120-155 char summary here">' : descLen > 165 ? 'Shorten to 155 characters. Lead with the main benefit.' : descLen < 100 ? 'Expand to 120-155 chars. Summarise what the page is about and why to click.' : '',
    };

    const h1Matches = (html.match(/<h1[^>]*>/gi) || []).length;
    results.h1 = {
      pass: h1Matches === 1,
      label: 'H1 heading (one per page)',
      value: h1Matches === 0 ? 'No H1 tag found' : h1Matches === 1 ? '1 H1 tag ✓' : `${h1Matches} H1 tags found (should be exactly 1)`,
      impact: 'high', category: 'seo',
      fix: h1Matches === 0 ? 'Add exactly one <h1> tag containing your main keyword for this page.' : h1Matches > 1 ? `Change additional H1s to H2 or H3. Each page must have only one H1.` : '',
    };

    const hasOGTitle = /property=["']og:title["']/i.test(html);
    const hasOGImg   = /property=["']og:image["']/i.test(html);
    results.openGraph = {
      pass: hasOGTitle && hasOGImg,
      label: 'Open Graph (social sharing preview)',
      value: hasOGTitle && hasOGImg ? 'OG title and image present' : !hasOGTitle ? 'Missing og:title' : 'Missing og:image',
      impact: 'medium', category: 'seo',
      note: 'Controls how links look when shared on LinkedIn, WhatsApp, Twitter',
      fix: 'Add og:title, og:description, and og:image meta tags. Use a 1200×630px image for best results.',
    };

    const hasSchema = /application\/ld\+json/i.test(html) || /itemscope/i.test(html);
    results.schema = {
      pass: hasSchema,
      label: 'Structured data (Schema.org)',
      value: hasSchema ? 'Schema markup detected' : 'No structured data found',
      impact: 'medium', category: 'seo',
      note: 'Helps Google show rich results like star ratings, FAQs, and business info',
      fix: 'Add JSON-LD schema for your business type. Use schema.org/LocalBusiness for service businesses.',
    };

    // ════════════════════════════════════════════
    //  CATEGORY: PERFORMANCE
    // ════════════════════════════════════════════

    results.speed = {
      pass: ttfbMs > 0 && ttfbMs < 1800,
      label: 'Server response speed (TTFB)',
      value: ttfbMs ? `${ttfbMs}ms to first byte` : 'Could not measure',
      impact: 'high', category: 'performance',
      note: ttfbMs > 1800 ? 'Slow — hurts Core Web Vitals and Google ranking' : ttfbMs > 800 ? 'Moderate — could be faster' : 'Fast',
      fix: 'Enable server-side caching, use a CDN (Cloudflare is free), or upgrade your hosting plan.',
    };

    const hasViewport = /meta[^>]+name=["']viewport["'][^>]*content/i.test(html) || /meta[^>]+content[^>]+name=["']viewport["']/i.test(html);
    results.viewport = {
      pass: hasViewport,
      label: 'Mobile viewport meta tag',
      value: hasViewport ? 'Mobile viewport configured' : 'Missing viewport tag — site likely broken on phones',
      impact: 'critical', category: 'performance',
      fix: 'Add <meta name="viewport" content="width=device-width, initial-scale=1"> inside the <head>.',
    };

    const allImgs   = (html.match(/<img[^>]+>/gi) || []).length;
    const imgsNoAlt = (html.match(/<img(?![^>]*\balt=["'][^"']+["'])[^>]*>/gi) || []).length;
    const altScore  = allImgs > 0 ? Math.round(((allImgs - imgsNoAlt) / allImgs) * 100) : 100;
    results.altText = {
      pass: altScore >= 80,
      label: 'Image alt text (accessibility + SEO)',
      value: allImgs === 0 ? 'No images found' : `${altScore}% of ${allImgs} images have alt text`,
      impact: 'medium', category: 'performance',
      note: imgsNoAlt > 0 ? `${imgsNoAlt} image(s) missing alt text` : 'All images have alt text',
      fix: `Add descriptive alt attributes to the ${imgsNoAlt} image(s) missing them. Describe what's in the image using relevant keywords.`,
    };

    const srcsetCount = (html.match(/<img[^>]+srcset[^>]+>/gi) || []).length;
    const hasResponsiveImgs = allImgs === 0 || (srcsetCount / allImgs) >= 0.3;
    results.responsiveImages = {
      pass: hasResponsiveImgs,
      label: 'Responsive images (srcset)',
      value: allImgs === 0 ? 'No images found' : `${srcsetCount} of ${allImgs} images use srcset`,
      impact: 'medium', category: 'performance',
      fix: 'Add srcset and sizes attributes to images. Use WebP format and serve different sizes for desktop vs. mobile.',
    };

    // ════════════════════════════════════════════
    //  CATEGORY: DESIGN
    // ════════════════════════════════════════════

    const h2Matches = (html.match(/<h2[^>]*>/gi) || []).length;
    const bodyHtml = (html.match(/<body[\s\S]*?<\/body>/i) || [html])[0];
    const firstScreenText = htmlToText(stripScripts(bodyHtml).slice(0, 12000));
    const ctaRegex = /\b(contact us|get started|send an enquiry|book a call|request a demo|buy now|order now|sign up|schedule|free trial|talk to us|start free|get in touch|hire us|send enquiry|book now|free consultation|call us|speak to|try free|start a conversation|free audit)\b/i;
    const hasCTA = ctaRegex.test(textContent);
    const hasEarlyCTA = ctaRegex.test(firstScreenText);
    const paragraphStats = getParagraphStats(html);
    const hasContactPath = /href=["'](?:tel:|mailto:)|<form\b|\/contact|#contact|contact us|get in touch|book a call|start a conversation/i.test(html);

    results.heroClarity = {
      pass: h1Matches === 1 && titleText && hasEarlyCTA,
      label: 'First-screen message and action',
      value: h1Matches === 1 && hasEarlyCTA ? 'Clear headline with an early action' : !hasEarlyCTA ? 'No obvious action found near the top' : 'Headline structure needs attention',
      impact: 'high', category: 'design',
      note: 'A visitor should know what you do, why it matters, and what to click within a few seconds.',
      fix: 'Tighten the first screen around one clear promise, one primary action, and a short proof point.',
    };

    results.contentScannability = {
      pass: h2Matches >= 2 && paragraphStats.longParagraphs <= 2,
      label: 'Scannable page structure',
      value: `${h2Matches} section heading${h2Matches === 1 ? '' : 's'}, ${paragraphStats.longParagraphs} dense paragraph${paragraphStats.longParagraphs === 1 ? '' : 's'}`,
      impact: 'medium', category: 'design',
      note: paragraphStats.longParagraphs ? 'Dense copy makes good offers feel harder to understand.' : 'Copy is broken into manageable sections.',
      fix: 'Add clear section headings, shorten long paragraphs, and move key selling points into short blocks.',
    };

    results.conversionPath = {
      pass: hasCTA && hasContactPath,
      label: 'Low-friction enquiry path',
      value: hasContactPath ? 'Contact path detected' : 'No obvious way to enquire from this page',
      impact: 'critical', category: 'design',
      note: 'Good design does not just look better; it makes the next step feel obvious.',
      fix: 'Add a visible enquiry button, phone/email path, or short form near the top and again near the bottom.',
    };

    results.mobileConfidence = {
      pass: hasViewport && (allImgs === 0 || hasResponsiveImgs),
      label: 'Mobile confidence signals',
      value: hasViewport ? (hasResponsiveImgs ? 'Viewport and responsive media detected' : 'Viewport present, image handling needs work') : 'Mobile viewport missing',
      impact: 'high', category: 'design',
      note: 'Most prospects will judge the business from a phone first.',
      fix: 'Use a mobile-first layout, responsive images, clear tap targets, and repeat the main CTA after important sections.',
    };

    // ════════════════════════════════════════════
    //  CATEGORY: TRUST
    // ════════════════════════════════════════════

    const hasAnalytics = /googletagmanager\.com|gtag\(|google-analytics\.com|_gaq\b|data-analytics-id=["']G-[A-Z0-9]+["']/i.test(html);
    results.analytics = {
      pass: hasAnalytics,
      label: 'Analytics tracking installed',
      value: hasAnalytics ? 'Google Analytics / GTM detected' : 'No analytics found — you\'re flying blind',
      impact: 'high', category: 'trust',
      fix: 'Install Google Analytics 4 (free). Without it you can\'t see where visitors come from or what they do.',
    };

    const hasFavicon = /rel=["'][^"']*icon[^"']*["']/i.test(html) || /rel=["']shortcut icon["']/i.test(html);
    results.favicon = {
      pass: hasFavicon,
      label: 'Favicon (browser tab icon)',
      value: hasFavicon ? 'Favicon detected' : 'No favicon — looks unfinished in browser tabs',
      impact: 'low', category: 'trust',
      fix: 'Create a 32×32 and 180×180 icon and add <link rel="icon" href="/favicon.ico"> to your <head>.',
    };

    results.cta = {
      pass: hasCTA,
      label: 'Clear call-to-action (CTA)',
      value: hasCTA ? 'CTA button or link found' : 'No clear CTA detected — visitors don\'t know what to do next',
      impact: 'critical', category: 'trust',
      fix: 'Add a prominent action button above the fold: "Get Started", "Book a Call", or "Contact Us".',
    };

    const hasPhoneLink = /href=["']tel:/i.test(html);
    const hasPhoneText = /(\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}/.test(html.replace(/<[^>]+>/g, ' '));
    results.phone = {
      pass: hasPhoneLink || hasPhoneText,
      label: 'Phone number visible',
      value: (hasPhoneLink || hasPhoneText) ? 'Phone number or tel: link detected' : 'No phone number found on the page',
      impact: 'medium', category: 'trust',
      fix: 'Add your phone number to the header and footer. Use <a href="tel:+1234567890"> so mobile users can tap to call.',
    };

    const hasSocialProof = /testimonial|review|rating|\bstar[s\b]|case study|clients?|trusted by|award|certified|accredited|featured in|as seen|trustpilot|clutch\.co|g2\.com|capterra|\b4\.[5-9]\b|\b5\.0\b|\breviews\b/i.test(html);
    results.socialProof = {
      pass: hasSocialProof,
      label: 'Social proof / trust signals',
      value: hasSocialProof ? 'Testimonials or trust indicators found' : 'No testimonials, reviews, or trust badges detected',
      impact: 'high', category: 'trust',
      fix: 'Add 3-5 customer testimonials, a star rating widget, client logos, or a "Featured in" press section.',
    };

    const footerMatch = html.match(/<footer[\s\S]*?<\/footer>/i);
    const footerContent = footerMatch ? footerMatch[0] : '';
    const footerLinkCount = (footerContent.match(/<a\s/gi) || []).length;
    results.footer = {
      pass: !!footerMatch && footerLinkCount >= 3,
      label: 'Footer with navigation + contact',
      value: !footerMatch ? 'No <footer> element found' : footerLinkCount < 3 ? `Footer found but only ${footerLinkCount} link(s) — too sparse` : `Footer with ${footerLinkCount} links`,
      impact: 'low', category: 'trust',
      fix: 'Add a footer with key page links, contact info, copyright year, and privacy policy link.',
    };

    const hasPrivacy = /privacy.{0,10}policy|privacy.{0,10}notice|terms.{0,20}(of.{0,10})?(service|use|conditions)|cookie.{0,10}policy/i.test(html);
    results.privacy = {
      pass: hasPrivacy,
      label: 'Privacy policy / Terms of service',
      value: hasPrivacy ? 'Privacy or terms page linked' : 'No privacy policy detected — GDPR/CCPA risk',
      impact: 'medium', category: 'trust',
      fix: 'Add a Privacy Policy page (required by GDPR, CCPA, and Google Ads). Link it from the footer.',
    };

    technicalData = buildTechnicalData({ html, finalUrl, statusCode, headers, ttfbMs, linkAudit, textContent });
  }

  // ── Score ───────────────────────────────────────────────────────
  const checks   = Object.values(results);
  const total    = checks.length;
  const passed   = checks.filter(c => c.pass).length;
  const score    = Math.round((passed / total) * 100);
  const critical = checks.filter(c => !c.pass && c.impact === 'critical').length;
  const high     = checks.filter(c => !c.pass && c.impact === 'high').length;

  const grade = score >= 90 ? 'A' : score >= 75 ? 'B' : score >= 60 ? 'C' : score >= 45 ? 'D' : 'F';

  // Category scores
  const categories = ['technical', 'seo', 'performance', 'design', 'trust'];
  const catScores = {};
  for (const cat of categories) {
    const catChecks = checks.filter(c => c.category === cat);
    const catPassed = catChecks.filter(c => c.pass).length;
    catScores[cat] = catChecks.length > 0 ? Math.round((catPassed / catChecks.length) * 100) : 100;
  }

  const report = buildClientReport({ finalUrl, score, grade, checks, catScores, critical, high, linkAudit, technicalData });

  return json({ url: finalUrl, score, grade, passed, total, critical, high, ttfbMs, results, catScores, linkAudit, technicalData, report, errors });
}

async function toWebRequest(req) {
  if (req && typeof req.json === 'function' && req.headers && typeof req.headers.get === 'function') return req;

  const headers = new Headers();
  for (const [key, value] of Object.entries(req.headers || {})) {
    if (Array.isArray(value)) value.forEach(item => headers.append(key, String(item)));
    else if (value != null) headers.set(key, String(value));
  }

  const protocolHeader = headers.get('x-forwarded-proto') || 'https';
  const protocol = protocolHeader.split(',')[0].trim() || 'https';
  const host = headers.get('host') || 'lofts.studio';
  const url = /^https?:\/\//i.test(req.url || '') ? req.url : `${protocol}://${host}${req.url || '/'}`;
  const method = req.method || 'GET';
  let body;

  if (!/^(GET|HEAD)$/i.test(method)) {
    if (req.body != null) body = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
    else body = await readRawBody(req);
  }

  return new Request(url, { method, headers, body });
}

function readRawBody(req) {
  return new Promise(resolve => {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => resolve(body));
    req.on('error', () => resolve(''));
  });
}

async function sendNodeResponse(res, response) {
  res.statusCode = response.status;
  response.headers.forEach((value, key) => res.setHeader(key, value));
  res.end(await response.text());
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json', ...cors() } });
}

function cors() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Cache-Control': 'no-store',
  };
}

function emptyLinkAudit() {
  return { totalFound: 0, checked: 0, ok: [], broken: [], unchecked: [], skipped: 0, internalChecked: 0, externalChecked: 0 };
}

function stripScripts(html) {
  return String(html || '')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ');
}

function htmlToText(html) {
  return stripScripts(html)
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/\s+/g, ' ')
    .trim();
}

function getParagraphStats(html) {
  const paragraphs = [...String(html || '').matchAll(/<p\b[^>]*>([\s\S]*?)<\/p>/gi)].map(match => htmlToText(match[1]));
  const lengths = paragraphs.map(p => p.length).filter(Boolean);
  const longParagraphs = lengths.filter(len => len > 260).length;
  const averageLength = lengths.length ? Math.round(lengths.reduce((sum, len) => sum + len, 0) / lengths.length) : 0;
  return { count: paragraphs.length, averageLength, longParagraphs };
}

function extractLinks(html, baseUrl) {
  const base = new URL(baseUrl);
  const seen = new Set();
  const links = [];
  const matches = String(html || '').matchAll(/<a\b[^>]*href\s*=\s*(["']?)([^"'\s>]+)\1[^>]*>/gi);

  for (const match of matches) {
    const rawHref = (match[2] || '').trim();
    const text = htmlToText(match[0]).slice(0, 80);
    if (!rawHref || /^(mailto:|tel:|sms:|javascript:|data:)/i.test(rawHref)) continue;

    if (rawHref.startsWith('#')) {
      const key = `${base.origin}${base.pathname}${rawHref}`;
      if (!seen.has(key)) {
        seen.add(key);
        links.push({ url: key, href: rawHref, text, samePageAnchor: true, internal: true });
      }
      continue;
    }

    let target;
    try { target = new URL(rawHref, base.href); } catch { continue; }
    if (!/^https?:$/i.test(target.protocol)) continue;
    target.hash = target.hash || '';
    const key = target.href;
    if (seen.has(key)) continue;
    seen.add(key);
    links.push({ url: target.href, href: rawHref, text, internal: target.origin === base.origin });
  }

  const internal = links.filter(link => link.internal && !link.samePageAnchor);
  const external = links.filter(link => !link.internal);
  const anchors = links.filter(link => link.samePageAnchor);
  return [...anchors, ...internal, ...external];
}

async function auditLinks(links, finalUrl, html, limit = LINK_AUDIT_LIMIT) {
  const audit = emptyLinkAudit();
  audit.totalFound = links.length;

  const anchorIds = new Set([...String(html || '').matchAll(/\s(?:id|name)\s*=\s*["']([^"']+)["']/gi)].map(match => match[1]));
  const samePageAnchors = links.filter(link => link.samePageAnchor);
  for (const link of samePageAnchors) {
    const id = safeDecode((link.href || '').replace(/^#/, ''));
    audit.checked += 1;
    audit.internalChecked += 1;
    if (id && anchorIds.has(id)) audit.ok.push({ ...link, status: 200 });
    else audit.broken.push({ ...link, status: 'missing anchor' });
  }

  const toCheck = links
    .filter(link => !link.samePageAnchor)
    .slice(0, Math.max(0, limit - samePageAnchors.length));
  audit.skipped = Math.max(0, links.length - samePageAnchors.length - toCheck.length);

  const checked = await Promise.all(toCheck.map(checkLink));
  for (const item of checked) {
    audit.checked += 1;
    if (item.internal) audit.internalChecked += 1;
    else audit.externalChecked += 1;
    if (item.error) audit.unchecked.push(item);
    else if (isBrokenStatus(item.status)) audit.broken.push(item);
    else audit.ok.push(item);
  }

  return audit;
}

async function checkLink(link) {
  const head = await fetchStatus(link.url, 'HEAD');
  if (head.status && head.status !== 405 && head.status !== 501) return { ...link, ...head };
  const get = await fetchStatus(link.url, 'GET');
  return { ...link, ...get };
}

async function fetchStatus(url, method) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), LINK_TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      method,
      redirect: 'follow',
      signal: ctrl.signal,
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; LoftsStudio-Audit/1.0)', 'Accept': 'text/html,*/*;q=0.8' },
    });
    return { status: res.status, finalUrl: res.url || url };
  } catch (e) {
    return { error: String(e && e.name === 'AbortError' ? 'timeout' : e).slice(0, 80) };
  } finally {
    clearTimeout(timer);
  }
}

function isBrokenStatus(status) {
  if (!status || typeof status !== 'number') return false;
  if ([401, 403, 429].includes(status)) return false;
  return status >= 400;
}

function safeDecode(value) {
  try { return decodeURIComponent(value); } catch { return value; }
}

function buildTechnicalData({ html, finalUrl, statusCode, headers, ttfbMs, linkAudit, textContent }) {
  const count = pattern => (String(html || '').match(pattern) || []).length;
  const headingCounts = {};
  for (let i = 1; i <= 6; i++) headingCounts[`h${i}`] = count(new RegExp(`<h${i}\\b`, 'gi'));

  return {
    finalUrl,
    statusCode,
    ttfbMs,
    pageBytes: html.length,
    wordCount: textContent ? textContent.split(/\s+/).filter(Boolean).length : 0,
    headings: headingCounts,
    images: count(/<img\b/gi),
    scripts: count(/<script\b/gi),
    stylesheets: count(/<link\b[^>]*rel=["'][^"']*stylesheet/gi),
    forms: count(/<form\b/gi),
    buttons: count(/<button\b/gi),
    linksFound: linkAudit.totalFound,
    linksChecked: linkAudit.checked,
    brokenLinks: linkAudit.broken.length,
    contentType: headers['content-type'] || '',
    cacheControl: headers['cache-control'] || '',
    server: headers.server || headers['x-powered-by'] || '',
  };
}

function buildClientReport({ finalUrl, score, grade, checks, catScores, critical, high, linkAudit, technicalData }) {
  const failed = checks
    .filter(check => !check.pass)
    .sort((a, b) => impactWeight(b.impact) - impactWeight(a.impact));
  const passed = checks.filter(check => check.pass);
  const designFails = failed.filter(check => check.category === 'design' || check.category === 'trust');
  const technicalFails = failed.filter(check => check.category === 'technical' || check.category === 'performance' || check.category === 'seo');
  const topActions = failed.slice(0, 6).map(check => ({
    label: check.label,
    impact: check.impact,
    value: check.value,
    why: explainClientImpact(check),
    recommendation: check.fix || 'Review and improve this area before sending more traffic to the page.',
    expectedOutcome: expectedOutcome(check),
  }));
  const quickChecks = topActions.slice(0, 3).map(action => ({
    label: action.label,
    impact: action.impact,
    finding: action.value,
    why: action.why,
    move: action.recommendation,
  }));

  const status = score >= 80 ? 'strong foundation' : score >= 60 ? 'good site with clear improvement opportunities' : 'site with visible conversion and trust friction';
  const strongestCategories = Object.entries(catScores || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 2)
    .map(([key, value]) => `${labelForCategory(key)} (${value}/100)`);
  const weakestCategories = Object.entries(catScores || {})
    .sort((a, b) => a[1] - b[1])
    .slice(0, 2)
    .map(([key, value]) => `${labelForCategory(key)} (${value}/100)`);
  const opportunityCards = buildOpportunityCards({ failed, checks, catScores, linkAudit });
  const quickWins = failed
    .filter(check => ['critical', 'high', 'medium'].includes(check.impact))
    .slice(0, 5)
    .map(check => ({
      title: check.label,
      impact: check.impact,
      finding: check.value,
      why: explainClientImpact(check),
      action: check.fix || 'Review this item and improve it before sending more traffic to the page.',
    }));
  const strengths = passed
    .filter(check => ['critical', 'high', 'medium'].includes(check.impact))
    .slice(0, 4)
    .map(check => `${check.label}: ${check.value}`);

  return {
    generatedAt: new Date().toISOString(),
    headline: `Audit report for ${new URL(finalUrl).hostname}`,
    summary: `This page has a ${status}. The score is ${score}/100, with ${critical} critical and ${high} high-priority issue${high === 1 ? '' : 's'} to review first. The biggest opportunity is to turn the page from an online brochure into a clearer enquiry path.`,
    quickBrief: {
      title: '30-second client brief',
      why: failed.length
        ? 'The audit is not just a technical score. It shows where a prospect can lose trust, miss the next step, or leave before enquiring.'
        : 'The core checks look healthy. The opportunity is to sharpen the page so visitors understand the offer faster and feel more confident taking action.',
      before: designFails.length
        ? 'Before improvement, the page may look acceptable but still make visitors work too hard to understand the offer, trust the business, and choose the next step.'
        : 'Before improvement, the page has a usable foundation but can still make the proof, offer, and next step sharper.',
      after: 'After improvement, the page should feel clearer, faster to scan, more trustworthy, and more focused on turning qualified visitors into enquiries.',
      topChecks: quickChecks,
    },
    executiveSummary: [
      weakestCategories.length ? `Weakest areas: ${weakestCategories.join(' and ')}.` : 'No weak category stood out, so the opportunity is refinement and stronger messaging.',
      strongestCategories.length ? `Strongest signals: ${strongestCategories.join(' and ')}.` : 'The page needs a stronger foundation before strengths are obvious.',
      failed.length ? `${failed.length} items should be reviewed before more traffic is sent to this page.` : 'The core checks look healthy, so the next step is a conversion-focused polish.',
    ],
    beforeAfter: {
      before: [
        designFails.length ? 'Visitors may need extra effort to understand the offer, trust the business, or choose the next step.' : 'The page has a usable presentation, but the strongest proof and action can still be sharper.',
        linkAudit.broken.length ? `${linkAudit.broken.length} broken link${linkAudit.broken.length === 1 ? '' : 's'} can interrupt the buyer journey and waste crawl attention.` : 'Navigation paths checked from this page do not show dead ends.',
        technicalFails.length ? 'Search and performance signals are leaving avoidable ranking or conversion gains on the table.' : 'The technical foundation is mostly in place.',
      ],
      after: [
        'A sharper first screen explains the offer, backs it with proof, and gives visitors one obvious next action.',
        'Trust signals, contact paths, mobile behaviour, and navigation are cleaned so the business feels easier to choose.',
        'The page becomes easier to scan, easier to enquire from, and better prepared for SEO, referrals, and paid traffic.',
      ],
    },
    opportunityCards,
    designAnalysis: designFails.length
      ? designFails.slice(0, 6).map(check => `${check.label}: ${check.value}. ${explainClientImpact(check)}`)
      : [
          'The main design and trust checks passed, so the next improvement is refinement: sharper proof, cleaner page rhythm, stronger calls to action, and more persuasive above-the-fold positioning.',
          'Even when the basics pass, a redesign can still improve how quickly a visitor understands the offer and feels confident enough to enquire.',
        ],
    quickWins,
    priorityActions: topActions,
    strengths,
    brokenLinks: linkAudit.broken.slice(0, 10),
    technicalSnapshot: technicalData,
    catScores,
    grade,
  };
}

function impactWeight(impact) {
  return ({ critical: 4, high: 3, medium: 2, low: 1 })[impact] || 0;
}

function labelForCategory(category) {
  return ({ technical: 'Technical', seo: 'SEO', performance: 'Performance', design: 'Design', trust: 'Trust' })[category] || category;
}

function buildOpportunityCards({ failed, checks, catScores, linkAudit }) {
  const find = labels => labels
    .map(label => checks.find(check => check.label === label))
    .filter(Boolean);
  const designIssues = find(['First-screen message and action', 'Scannable page structure', 'Low-friction enquiry path', 'Clear call-to-action (CTA)']).filter(check => !check.pass);
  const trustIssues = find(['Social proof / trust signals', 'Phone number visible', 'Privacy policy / Terms of service', 'Analytics tracking installed']).filter(check => !check.pass);
  const seoIssues = failed.filter(check => ['technical', 'seo', 'performance'].includes(check.category));
  const linkIssues = linkAudit.broken || [];

  return [
    {
      theme: 'risk',
      title: 'Lost enquiry risk',
      score: Math.min(catScores.design ?? 100, catScores.trust ?? 100),
      finding: designIssues.length ? summarizeIssue(designIssues[0]) : 'The design basics pass, but the page can still work harder to make the next step feel obvious.',
      why: 'A visitor who has to think too hard usually leaves quietly. The page should answer “why this business?” and “what do I do next?” without effort.',
      action: designIssues.length ? designIssues[0].fix : 'Strengthen the first screen, repeat the main CTA, and place proof close to the decision points.',
    },
    {
      theme: 'trust',
      title: 'Trust and proof gap',
      score: catScores.trust ?? 100,
      finding: trustIssues.length ? summarizeIssue(trustIssues[0]) : 'Core trust checks passed, so this is a chance to make proof more visible and persuasive.',
      why: 'Prospects compare confidence, not just design. Reviews, proof, contact clarity, and policies reduce hesitation before enquiry.',
      action: trustIssues.length ? trustIssues[0].fix : 'Add stronger testimonials, client outcomes, project proof, and a clear contact path near the top and bottom.',
    },
    {
      theme: 'growth',
      title: 'Search and traffic readiness',
      score: Math.min(catScores.technical ?? 100, catScores.seo ?? 100, catScores.performance ?? 100),
      finding: seoIssues.length ? summarizeIssue(seoIssues[0]) : 'Search and performance checks are mostly healthy from this page.',
      why: 'Better technical signals help more qualified visitors reach the page, and faster clearer pages keep more of those visitors engaged.',
      action: seoIssues.length ? seoIssues[0].fix : 'Use the healthy foundation to add stronger service, location, and proof content around the offer.',
    },
    {
      theme: 'navigation',
      title: 'Journey continuity',
      score: linkIssues.length ? 45 : 92,
      finding: linkIssues.length ? `${linkIssues.length} broken link${linkIssues.length === 1 ? '' : 's'} found in the scan.` : 'No broken links were found in the checked links from this page.',
      why: 'Every dead end creates doubt. Clean navigation helps prospects keep moving from interest to enquiry.',
      action: linkIssues.length ? 'Repair the broken links or redirect them to the most relevant live pages.' : 'Keep the journey tight by linking service, proof, FAQ, and contact sections in a clear order.',
    },
  ];
}

function summarizeIssue(check) {
  return `${check.label}: ${check.value}`;
}

function explainClientImpact(check) {
  const label = check.label || '';
  if (/CTA|action|enquiry|contact/i.test(label)) return 'This can reduce enquiries because visitors do not get a confident next step at the moment they are interested.';
  if (/Social proof|review|trust/i.test(label)) return 'This can make the business feel harder to trust than competitors with visible proof and reassurance.';
  if (/title|description|H1|Schema|index|canonical/i.test(label)) return 'This can weaken search visibility and make the page less compelling when it appears in Google.';
  if (/speed|response|viewport|mobile|image/i.test(label)) return 'This can make mobile visitors leave early, especially when the page feels slow or awkward on phones.';
  if (/Broken links|loads|HTTP|redirect|HTTPS|security/i.test(label)) return 'This can create doubt and interrupt the visitor journey before they enquire.';
  if (/Analytics/i.test(label)) return 'This makes it harder to know which channels and pages are producing serious leads.';
  return 'This creates friction that can make a qualified visitor hesitate, leave, or choose another provider.';
}

function expectedOutcome(check) {
  const category = check.category || '';
  if (category === 'design') return 'Clearer first impression and a smoother path to enquiry.';
  if (category === 'trust') return 'More confidence before a prospect contacts the business.';
  if (category === 'seo') return 'Cleaner search presentation and stronger page relevance.';
  if (category === 'performance') return 'Faster, more comfortable browsing on mobile and desktop.';
  if (category === 'technical') return 'Fewer dead ends and a more reliable foundation for traffic.';
  return 'Less friction and a more persuasive page experience.';
}
