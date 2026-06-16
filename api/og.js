// Edge function — dynamic blog cover image (SVG).
// Renders the same two-tone editorial cover as the static Python generator,
// on the fly, so AI-scheduled posts get a featured image with zero storage.
//   /api/og?title=Post%20Title&cat=Shopify
export const config = { runtime: 'edge' };

const W = 1200, H = 675, PANEL_X = 750;
const CREAM = '#F4F0EA', INK = '#1A1612', ACCENT = '#8B3A1F',
      ACCENT_LT = '#D77A55', CREAM_LT = '#FAF7F1', LINE = '#D9D2C4',
      DIM = '#4A3E34';

function catKey(cat) {
  const c = (cat || '').toLowerCase();
  if (/\bai\b|automation/.test(c)) return 'ai';
  if (/seo/.test(c)) return 'seo';
  if (/speed|performance/.test(c)) return 'speed';
  if (/conversion|cro/.test(c)) return 'cro';
  if (/process/.test(c)) return 'process';
  if (/woo|wordpress/.test(c)) return 'woo';
  if (/custom|app/.test(c)) return 'apps';
  if (/migration/.test(c)) return 'migration';
  if (/shopify/.test(c)) return 'shopify';
  return 'default';
}

function esc(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// Greedy wrap by approx glyph width for a serif at the given px size.
function wrapTitle(title, maxChars, maxLines) {
  const words = String(title || '').split(/\s+/).filter(Boolean);
  const lines = [];
  let cur = '';
  for (const w of words) {
    const t = cur ? cur + ' ' + w : w;
    if (t.length <= maxChars) cur = t;
    else { if (cur) lines.push(cur); cur = w; }
  }
  if (cur) lines.push(cur);
  if (lines.length > maxLines) {
    lines.length = maxLines;
    lines[maxLines - 1] = lines[maxLines - 1].replace(/[\s\W]+$/, '') + '…';
  }
  return lines;
}

function motif(key) {
  const cx = (PANEL_X + W) / 2 + 6, cy = H / 2;
  const A = ACCENT_LT, C = CREAM_LT;
  let s = `<circle cx="${cx}" cy="${cy}" r="190" fill="none" stroke="${DIM}" stroke-width="2"/>`
        + `<circle cx="${cx}" cy="${cy}" r="150" fill="none" stroke="${DIM}" stroke-width="2"/>`;
  const ring = (x, y, r, fill) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill === 'none' ? 'none' : fill}"${fill === 'none' ? ` stroke="${A}" stroke-width="6"` : ''}/>`;
  if (key === 'ai') {
    const nodes = [[cx-70,cy-90],[cx+60,cy-110],[cx+105,cy+10],[cx-10,cy+30],[cx+70,cy+115],[cx-95,cy+70],[cx+120,cy-70]];
    for (let i=0;i<nodes.length;i++) for (let j=i+1;j<nodes.length;j++){
      const [x,y]=nodes[i],[x2,y2]=nodes[j];
      if (Math.abs(x-x2)+Math.abs(y-y2)<230) s+=`<line x1="${x}" y1="${y}" x2="${x2}" y2="${y2}" stroke="${DIM}" stroke-width="2"/>`;
    }
    for (const [x,y] of nodes) s+=`<circle cx="${x}" cy="${y}" r="15" fill="${A}"/><circle cx="${x}" cy="${y}" r="22" fill="none" stroke="${C}" stroke-width="2"/>`;
  } else if (key === 'seo') {
    [70,120,175,235].forEach((bh,i)=>{const x=cx-110+i*56;s+=`<rect x="${x}" y="${cy+80-bh}" width="38" height="${bh}" rx="7" fill="${DIM}"/>`;});
    const mx=cx+10,my=cy-10,r=96;
    s+=`<circle cx="${mx}" cy="${my}" r="${r}" fill="none" stroke="${A}" stroke-width="11"/>`
     + `<line x1="${mx+r*0.7}" y1="${my+r*0.7}" x2="${mx+r*1.5}" y2="${my+r*1.5}" stroke="${A}" stroke-width="13" stroke-linecap="round"/>`;
  } else if (key === 'speed') {
    s+=`<path d="${arc(cx,cy,130,140,400)}" fill="none" stroke="${DIM}" stroke-width="20"/>`
     + `<path d="${arc(cx,cy,130,140,255)}" fill="none" stroke="${A}" stroke-width="20"/>`;
    const ang=255*Math.PI/180;
    s+=`<line x1="${cx}" y1="${cy}" x2="${cx+105*Math.cos(ang)}" y2="${cy+105*Math.sin(ang)}" stroke="${C}" stroke-width="9" stroke-linecap="round"/><circle cx="${cx}" cy="${cy}" r="14" fill="${A}"/>`;
  } else if (key === 'woo' || key === 'shopify') {
    const x0=cx-105,y0=cy-80,x1=cx+105,y1=cy+120;
    s+=`<rect x="${x0}" y="${y0}" width="${x1-x0}" height="${y1-y0}" rx="20" fill="none" stroke="${A}" stroke-width="9"/>`
     + `<path d="${arc(cx,y0,(x1-x0)/2-58,180,360)}" fill="none" stroke="${A}" stroke-width="9"/>`
     + `<circle cx="${cx}" cy="${cy+15}" r="7" fill="${C}"/>`;
  } else if (key === 'apps') {
    s+=`<rect x="${cx-115}" y="${cy-115}" width="230" height="230" rx="18" fill="none" stroke="${A}" stroke-width="7"/>`
     + `<line x1="${cx-115}" y1="${cy-68}" x2="${cx+115}" y2="${cy-68}" stroke="${A}" stroke-width="5"/>`
     + [-90,-74,-58].map(xp=>`<circle cx="${cx+xp}" cy="${cy-92}" r="4" fill="${C}"/>`).join('')
     + `<text x="${cx}" y="${cy+24}" font-family="ui-monospace,Menlo,monospace" font-weight="700" font-size="90" fill="${C}" text-anchor="middle">&lt;/&gt;</text>`;
  } else if (key === 'migration') {
    s+=`<rect x="${cx-130}" y="${cy-90}" width="120" height="150" rx="16" fill="none" stroke="${A}" stroke-width="7"/>`
     + `<rect x="${cx+10}" y="${cy-40}" width="120" height="150" rx="16" fill="#3A271B" stroke="${A}" stroke-width="7"/>`
     + `<line x1="${cx-30}" y1="${cy+10}" x2="${cx+40}" y2="${cy+10}" stroke="${C}" stroke-width="9"/>`
     + `<polygon points="${cx+30},${cy-4} ${cx+58},${cy+10} ${cx+30},${cy+24}" fill="${C}"/>`;
  } else if (key === 'cro') {
    const pts=[[-130,-95],[130,-95],[64,25],[34,120],[-34,120],[-64,25]].map(([x,y])=>`${cx+x},${cy+y}`).join(' ');
    s+=`<polygon points="${pts}" fill="none" stroke="${A}" stroke-width="7"/>`
     + `<line x1="${cx-92}" y1="${cy-25}" x2="${cx+92}" y2="${cy-25}" stroke="${DIM}" stroke-width="4"/>`
     + `<circle cx="${cx}" cy="${cy+150}" r="9" fill="${A}"/>`;
  } else if (key === 'process') {
    const xs=[cx-110,cx,cx+110];
    s+=`<line x1="${xs[0]+28}" y1="${cy}" x2="${xs[1]-28}" y2="${cy}" stroke="${DIM}" stroke-width="4"/>`
     + `<line x1="${xs[1]+28}" y1="${cy}" x2="${xs[2]-28}" y2="${cy}" stroke="${DIM}" stroke-width="4"/>`
     + ring(xs[0],cy,28,'none')+`<circle cx="${xs[1]}" cy="${cy}" r="28" fill="${A}"/>`+ring(xs[2],cy,28,'none');
  } else {
    s+=`<circle cx="${cx}" cy="${cy}" r="95" fill="none" stroke="${A}" stroke-width="5"/>`
     + `<circle cx="${cx}" cy="${cy}" r="50" fill="none" stroke="${DIM}" stroke-width="5"/>`;
  }
  return s;
}

// SVG arc path helper (cx,cy,r, start/end degrees)
function arc(cx, cy, r, a0, a1) {
  const p = (a) => [cx + r * Math.cos(a * Math.PI / 180), cy + r * Math.sin(a * Math.PI / 180)];
  const [x0, y0] = p(a0), [x1, y1] = p(a1);
  const large = (a1 - a0) % 360 > 180 ? 1 : 0;
  return `M ${x0} ${y0} A ${r} ${r} 0 ${large} 1 ${x1} ${y1}`;
}

export default async function handler(req) {
  const url = new URL(req.url);
  const title = url.searchParams.get('title') || 'Field Notes';
  const cat = url.searchParams.get('cat') || '';
  const key = catKey(cat);

  const lines = wrapTitle(title, 22, 4);
  const fontSize = lines.length > 3 ? 44 : 52;
  const lh = Math.round(fontSize * 1.2);
  const startY = Math.round(H / 2 - ((lines.length - 1) * lh) / 2) - 10;
  const titleSvg = lines.map((ln, i) =>
    `<text x="72" y="${startY + i * lh}" font-family="Georgia,'Times New Roman',serif" font-weight="700" font-size="${fontSize}" fill="${INK}" letter-spacing="-0.5">${esc(ln)}</text>`
  ).join('');

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="${CREAM}"/>
  <rect x="${PANEL_X}" y="0" width="${W - PANEL_X}" height="${H}" fill="${INK}"/>
  <rect x="${PANEL_X - 4}" y="0" width="4" height="${H}" fill="${ACCENT}"/>
  ${motif(key)}
  <line x1="72" y1="107" x2="112" y2="107" stroke="${ACCENT}" stroke-width="4"/>
  <text x="126" y="113" font-family="ui-monospace,Menlo,monospace" font-size="22" letter-spacing="2" fill="${ACCENT}">${esc((cat || 'FIELD NOTES').toUpperCase())}</text>
  ${titleSvg}
  <line x1="72" y1="${H - 84}" x2="${PANEL_X - 44}" y2="${H - 84}" stroke="${LINE}" stroke-width="1"/>
  <text x="72" y="${H - 58}" font-family="Georgia,serif" font-weight="700" font-size="26" fill="${INK}">Lofts <tspan font-family="ui-monospace,Menlo,monospace" font-weight="400" font-size="19" fill="${ACCENT}">studio</tspan></text>
</svg>`;

  return new Response(svg, {
    headers: {
      'content-type': 'image/svg+xml; charset=utf-8',
      'cache-control': 'public, s-maxage=31536000, immutable',
    },
  });
}
