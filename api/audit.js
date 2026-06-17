// Vercel Edge Function — Website Audit Tool (v2)
// 22 checks across 4 categories: Technical, SEO, Performance, Design & Trust

export const config = { runtime: 'edge' };

const TIMEOUT_MS = 9000;

export default async function handler(req) {
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors() });
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);

  let body;
  try { body = await req.json(); } catch { body = {}; }

  let rawUrl = (body.url || '').trim();
  if (!rawUrl) return json({ error: 'No URL provided' }, 400);
  if (!/^https?:\/\//i.test(rawUrl)) rawUrl = 'https://' + rawUrl;
  let url;
  try { url = new URL(rawUrl); } catch { return json({ error: 'Invalid URL' }, 400); }

  const results = {};
  const errors  = {};

  // ── Fetch the page ─────────────────────────────────────────────
  let html = '', finalUrl = url.href, statusCode = 0, headers = {}, ttfbMs = 0;

  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
    const t0 = Date.now();
    const res = await fetch(url.href, {
      signal: ctrl.signal,
      redirect: 'follow',
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; LoftsStudio-Audit/1.0)', 'Accept': 'text/html,application/xhtml+xml' },
    });
    clearTimeout(timer);
    ttfbMs    = Date.now() - t0;
    statusCode = res.status;
    finalUrl   = res.url || url.href;
    headers    = Object.fromEntries(res.headers.entries());
    html       = await res.text();
  } catch (e) { errors.fetch = String(e).slice(0, 120); }

  const h = html.toLowerCase();

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
    //  CATEGORY: DESIGN & TRUST
    // ════════════════════════════════════════════

    const hasAnalytics = /googletagmanager\.com|gtag\(|google-analytics\.com|_gaq\b/i.test(html);
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

    const ctaRegex = /\b(contact us|get started|send an enquiry|book a call|request a demo|buy now|order now|sign up|schedule|free trial|talk to us|start free|get in touch|hire us|send an enquiry|send enquiry|book now|free consultation|call us|speak to|try free)\b/i;
    const hasCTA = ctaRegex.test(html.replace(/<[^>]+>/g, ' '));
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
  const categories = ['technical', 'seo', 'performance', 'trust'];
  const catScores = {};
  for (const cat of categories) {
    const catChecks = checks.filter(c => c.category === cat);
    const catPassed = catChecks.filter(c => c.pass).length;
    catScores[cat] = catChecks.length > 0 ? Math.round((catPassed / catChecks.length) * 100) : 100;
  }

  return json({ url: finalUrl, score, grade, passed, total, critical, high, ttfbMs, results, catScores, errors });
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
