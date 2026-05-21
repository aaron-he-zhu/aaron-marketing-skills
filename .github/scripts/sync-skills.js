/**
 * Sync skills manifest
 *
 * Scans category directories for SKILL.md files and updates
 * marketplace.json, plugin.json, CodeBuddy, and Codex manifest skill root.
 * Use --check to fail if generated files are stale without writing them.
 */

const fs = require("fs");
const path = require("path");

const CATEGORIES = [
  "research",
  "build",
  "optimize",
  "monitor",
  "cross-cutting",
];

const ROOT = path.resolve(__dirname, "../..");
const MARKETPLACE_PATH = path.join(ROOT, "marketplace.json");
const MARKETPLACE_PLUGIN_PATH = path.join(ROOT, ".claude-plugin", "marketplace.json");
const PLUGIN_PATH = path.join(ROOT, ".claude-plugin", "plugin.json");
const CODEBUDDY_PATH = path.join(ROOT, ".codebuddy-plugin", "marketplace.json");
const CODEX_PLUGIN_PATH = path.join(ROOT, ".codex-plugin", "plugin.json");
const CHECK_ONLY = process.argv.includes("--check");

function discoverSkills() {
  const skills = [];

  for (const category of CATEGORIES) {
    const categoryDir = path.join(ROOT, category);
    if (!fs.existsSync(categoryDir)) continue;

    const entries = fs.readdirSync(categoryDir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;

      const skillFile = path.join(categoryDir, entry.name, "SKILL.md");
      if (fs.existsSync(skillFile)) {
        skills.push(`./${category}/${entry.name}`);
      }
    }
  }

  return skills.sort((a, b) => {
    const categoryOrder = (p) =>
      CATEGORIES.indexOf(p.split("/")[1]);
    const ca = categoryOrder(a);
    const cb = categoryOrder(b);
    if (ca !== cb) return ca - cb;
    return a.localeCompare(b);
  });
}

function writeOrCheck(filePath, serialized, label) {
  const current = fs.readFileSync(filePath, "utf8");
  if (current === serialized) {
    console.log(`OK ${label}`);
    return false;
  }

  if (CHECK_ONLY) {
    console.error(`STALE ${label}`);
    return true;
  }

  fs.writeFileSync(filePath, serialized, "utf8");
  console.log(`Updated ${label}`);
  return true;
}

function marketplaceContent(skills) {
  const data = JSON.parse(fs.readFileSync(MARKETPLACE_PATH, "utf8"));
  data.plugins[0].skills = skills;
  return JSON.stringify(data, null, 2) + "\n";
}

function pluginContent(skills) {
  const data = JSON.parse(fs.readFileSync(PLUGIN_PATH, "utf8"));
  data.skills = skills;
  return JSON.stringify(data, null, 2) + "\n";
}

function codeBuddyContent(skills) {
  const data = JSON.parse(fs.readFileSync(CODEBUDDY_PATH, "utf8"));
  data.plugins[0].skills = skills;
  return JSON.stringify(data, null, 2) + "\n";
}

function codexPluginContent() {
  const data = JSON.parse(fs.readFileSync(CODEX_PLUGIN_PATH, "utf8"));
  data.skills = "./";
  return JSON.stringify(data, null, 2) + "\n";
}

const skills = discoverSkills();
console.log(`Discovered ${skills.length} skills:`);
skills.forEach((s) => console.log(`  ${s}`));

let stale = false;
const marketplace = marketplaceContent(skills);
stale = writeOrCheck(MARKETPLACE_PATH, marketplace, "marketplace.json") || stale;
stale = writeOrCheck(MARKETPLACE_PLUGIN_PATH, marketplace, ".claude-plugin/marketplace.json") || stale;
stale = writeOrCheck(PLUGIN_PATH, pluginContent(skills), ".claude-plugin/plugin.json") || stale;
stale = writeOrCheck(CODEBUDDY_PATH, codeBuddyContent(skills), ".codebuddy-plugin/marketplace.json") || stale;
stale = writeOrCheck(CODEX_PLUGIN_PATH, codexPluginContent(), ".codex-plugin/plugin.json") || stale;

if (CHECK_ONLY && stale) {
  console.error("Run `node .github/scripts/sync-skills.js` and commit the generated manifest changes.");
  process.exit(1);
}
