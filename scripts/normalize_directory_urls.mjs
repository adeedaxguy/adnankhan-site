import fs from "node:fs";
import path from "node:path";

const ROOT = process.cwd();
const SITE = "https://lofts.studio";
const SKIP_DIRS = new Set([".git", ".vercel", "admin", "api", "assets"]);
const TARGET_EXTENSIONS = new Set([".html", ".xml", ".txt"]);

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory() && SKIP_DIRS.has(entry.name)) continue;
    const filePath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(filePath, files);
    } else {
      files.push(filePath);
    }
  }
  return files;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

const allFiles = walk(ROOT);
const directoryRoutes = new Set();
const publicRoutes = new Set();

for (const file of allFiles) {
  if (path.extname(file) !== ".html") continue;
  const relFile = path.relative(ROOT, file).split(path.sep).join("/");
  if (path.basename(file) === "index.html") {
    const relDir = path.relative(ROOT, path.dirname(file)).split(path.sep).join("/");
    if (!relDir) continue;
    const route = `/${relDir}`;
    directoryRoutes.add(route);
    publicRoutes.add(route);
  } else {
    publicRoutes.add(`/${relFile}`);
  }
}

const delimiterLookahead = String.raw`(?=["'<>\s),#?])`;
let changedFiles = 0;
const joinedRouteRepairs = [];

for (const route of publicRoutes) {
  for (const directoryRoute of directoryRoutes) {
    if (!route.startsWith(`${directoryRoute}/s`)) continue;
    joinedRouteRepairs.push([directoryRoute + route.slice(directoryRoute.length + 1), route]);
  }
}

joinedRouteRepairs.sort((a, b) => b[0].length - a[0].length);

for (const file of allFiles) {
  if (!TARGET_EXTENSIONS.has(path.extname(file))) continue;
  let text = fs.readFileSync(file, "utf8");
  let next = text;

  for (const [brokenRoute, fixedRoute] of joinedRouteRepairs) {
    next = next.split(SITE + brokenRoute).join(SITE + fixedRoute);
    next = next.split(brokenRoute).join(fixedRoute);
  }

  next = next
    .split('hreflang="en-uk"')
    .join('hreflang="en-gb"')
    .split('hreflang="en-uae"')
    .join('hreflang="en-ae"');

  for (const route of directoryRoutes) {
    next = next.replace(
      new RegExp(`${escapeRegExp(SITE + route)}/${delimiterLookahead}`, "g"),
      SITE + route,
    );
    next = next.replace(
      new RegExp(`${escapeRegExp(route)}/${delimiterLookahead}`, "g"),
      route,
    );
  }

  if (next !== text) {
    fs.writeFileSync(file, next);
    changedFiles += 1;
  }
}

console.log(`normalized ${changedFiles} files across ${directoryRoutes.size} directory routes`);
