import { readdir, readFile, writeFile } from "node:fs/promises";
import { extname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL("../", import.meta.url));
const TITLE_LIMIT = 65;
const DESCRIPTION_LIMIT = 165;

const entities = {
  amp: "&",
  apos: "'",
  gt: ">",
  hellip: "…",
  ldquo: "“",
  lsquo: "‘",
  lt: "<",
  mdash: "—",
  nbsp: " ",
  ndash: "–",
  quot: '"',
  rdquo: "”",
  rsquo: "’",
};

function decodeOnce(value) {
  return value.replace(/&(#x[\da-f]+|#\d+|[a-z]+);/gi, (entity, code) => {
    if (code[0] === "#") {
      const number = code[1].toLowerCase() === "x"
        ? Number.parseInt(code.slice(2), 16)
        : Number.parseInt(code.slice(1), 10);
      return Number.isFinite(number) ? String.fromCodePoint(number) : entity;
    }
    return entities[code.toLowerCase()] ?? entity;
  });
}

function decodeFully(value) {
  let decoded = value;
  for (let index = 0; index < 3; index += 1) {
    const next = decodeOnce(decoded);
    if (next === decoded) break;
    decoded = next;
  }
  return decoded;
}

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function trimAtWord(value, limit) {
  const normalized = value.replace(/\s+/g, " ").trim();
  if (normalized.length <= limit) return normalized;
  const candidate = normalized.slice(0, limit + 1);
  const lastSpace = candidate.lastIndexOf(" ");
  return candidate.slice(0, lastSpace > limit * 0.65 ? lastSpace : limit).trim();
}

function compactTitle(value) {
  if (value.length <= TITLE_LIMIT) return value;
  const suffix = /\s*\|\s*Lofts Studio$/i.test(value) ? " | Lofts Studio" : "";
  const base = value
    .replace(/\s*\|\s*Lofts Studio$/i, "")
    .replace(/ Website Design (?:&|and) Development$/i, " Website Design");
  return `${trimAtWord(base, 60 - suffix.length)}${suffix}`;
}

function compactDescription(value) {
  if (value.length <= DESCRIPTION_LIMIT) return value;
  return `${trimAtWord(value, 159).replace(/[,:;—–-]+$/, "")}.`;
}

async function htmlFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if ([".git", ".wrangler", "node_modules", "project-seo"].includes(entry.name)) continue;
    const path = join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await htmlFiles(path));
    else if (extname(entry.name) === ".html") files.push(path);
  }
  return files;
}

let changedFiles = 0;
for (const file of await htmlFiles(ROOT)) {
  const source = await readFile(file, "utf8");
  let output = source.replace(/<title([^>]*)>([\s\S]*?)<\/title>/i, (tag, attrs, raw) => {
    const visible = decodeFully(raw.trim());
    const title = compactTitle(visible);
    if (title === visible && !/&amp;(?:#\d+|#x[\da-f]+|[a-z]+);/i.test(raw)) return tag;
    return `<title${attrs}>${escapeHtml(title)}</title>`;
  });

  output = output.replace(/<meta\b[^>]*>/gi, (tag) => {
    const key = tag.match(/\b(?:name|property)=["']([^"']+)["']/i)?.[1]?.toLowerCase();
    const titleField = key === "og:title" || key === "twitter:title";
    const descriptionField = key === "description" || key === "og:description" || key === "twitter:description";
    if (!titleField && !descriptionField) return tag;
    return tag.replace(/\bcontent=(["'])(.*?)\1/i, (attribute, quote, raw) => {
      const visible = decodeFully(raw);
      const value = titleField ? compactTitle(visible) : compactDescription(visible);
      if (value === visible && !/&amp;(?:#\d+|#x[\da-f]+|[a-z]+);/i.test(raw)) return attribute;
      return `content=${quote}${escapeHtml(value)}${quote}`;
    });
  });

  if (output !== source) {
    await writeFile(file, output);
    changedFiles += 1;
  }
}

console.log(`Normalized search metadata in ${changedFiles} HTML files.`);
