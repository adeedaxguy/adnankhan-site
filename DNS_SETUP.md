# Cloudflare DNS — 2-minute setup (read first thing when you wake up)

## STATUS WHEN YOU READ THIS (auto-detected by monitor every 30 min)

As of last check:
- **NS propagated to Cloudflare ✅** (austin.ns.cloudflare.com / liz.ns.cloudflare.com active)
- **Cloudflare proxy is ON (orange cloud) ⚠️** — proxying to GoDaddy parking page (returns Cloudflare error 522)
- **A record still points to old parking IPs** (13.248.243.5 / 76.223.105.230)

You need to do the steps below to fix this.

## What's already done ✅

- `lofts.studio` and `www.lofts.studio` both added to Vercel project `adnan-site`
- vercel.json configured with host-based 301 redirect: `adnank.vercel.app/*` → `lofts.studio/*`
- vercel.json redirects `www.lofts.studio` → `lofts.studio` (canonical apex)
- HSTS header active, all canonicals already point to `lofts.studio`
- Cloudflare zone for `lofts.studio` is active and responding authoritatively

## What you need to do (2 minutes)

Cloudflare imported the **old GoDaddy parking page A records** by default (13.248.243.5 and 76.223.105.230). Replace them with Vercel's IP:

### Steps:

1. **Log into [dash.cloudflare.com](https://dash.cloudflare.com)**
2. Click on `lofts.studio` → left sidebar → **DNS** → **Records**
3. **Delete these existing records** (these are old GoDaddy parking page records — Cloudflare imported them automatically):
   - `A    lofts.studio    13.248.243.5`
   - `A    lofts.studio    76.223.105.230`
   - Any AWS-related CNAME or TXT records
   - Any AAAA records for `lofts.studio` (Vercel doesn't use IPv6 directly)
4. **Add Vercel A record (apex):**
   - **Type:** `A`
   - **Name:** `@`
   - **IPv4 address:** `76.76.21.21`
   - **Proxy status:** **DNS only** (gray cloud — important! Vercel handles its own CDN)
   - **TTL:** Auto
5. **Add Vercel A record (www):**
   - **Type:** `A`
   - **Name:** `www`
   - **IPv4 address:** `76.76.21.21`
   - **Proxy status:** **DNS only** (gray cloud)
   - **TTL:** Auto

That's it. Within 60 seconds Vercel detects + auto-provisions HTTPS.

## Verify it worked

```bash
dig +short A lofts.studio    # → 76.76.21.21
curl -sI https://lofts.studio | head -1   # → HTTP/2 200
```

Or open `https://lofts.studio` in a browser.

## What happens automatically once DNS is correct

- Vercel auto-provisions HTTPS cert (Let's Encrypt) in ~60s
- `adnank.vercel.app/*` 301-redirects to `lofts.studio/*` (already configured)
- `www.lofts.studio/*` redirects to `lofts.studio/*` (canonical apex)
- All 110+ pages live on lofts.studio
- Cloudflare provides DNS (no proxy needed for now)

## Next steps after DNS is live

1. Submit `https://lofts.studio/sitemap.xml` to Google Search Console
2. Update Adnan & Irfan Upwork bios to include lofts.studio
3. Update LinkedIn for both founders
4. Email signatures: `@lofts.studio` (after you set up email forwarding)
5. Launch Google Ads pilot (see PLAN.md)

## Troubleshooting

- **GoDaddy parking page still showing after DNS edit:** Wait 5-15 min for DNS cache. Flush local: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
- **Invalid cert warning:** Wait 60-90s for Vercel to provision
- **Not working after 30 min:** Ping me in chat
