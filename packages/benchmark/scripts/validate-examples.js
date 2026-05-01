const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..", "..", "..");
const exampleRoot = path.join(root, "examples");
const generatedRoot = path.join(root, "samples", "benchmark", "generated");

const requiredModules = [
  "paper_skeleton",
  "method_graph",
  "method_delta",
  "formula_ir",
  "experiment_matrix",
  "claim_evidence_map",
  "reproduction_roadmap"
];

let errors = 0;
let warnings = 0;

function rel(filePath) {
  return path.relative(root, filePath).replaceAll(path.sep, "/");
}

function error(filePath, message) {
  errors += 1;
  console.error(`error ${rel(filePath)}: ${message}`);
}

function warn(filePath, message) {
  warnings += 1;
  console.warn(`warning ${rel(filePath)}: ${message}`);
}

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (err) {
    error(filePath, `invalid JSON: ${err.message}`);
    return null;
  }
}

function collectFiles() {
  const files = [];
  if (fs.existsSync(exampleRoot)) {
    for (const entry of fs.readdirSync(exampleRoot, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const filePath = path.join(exampleRoot, entry.name, "paper-ir.json");
      if (fs.existsSync(filePath)) files.push(filePath);
      else warn(path.join(exampleRoot, entry.name), "missing paper-ir.json");
    }
  }
  if (fs.existsSync(generatedRoot)) {
    for (const entry of fs.readdirSync(generatedRoot, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const filePath = path.join(generatedRoot, entry.name, "paper_ir.json");
      if (fs.existsSync(filePath)) files.push(filePath);
    }
  }
  return files;
}

function hasAnchors(value) {
  return Array.isArray(value?.anchors);
}

function validatePaper(filePath) {
  const ir = readJson(filePath);
  if (!ir) return;

  if (!ir.schema_version) error(filePath, "missing schema_version");
  if (!ir.metadata?.title) error(filePath, "missing metadata.title");
  if (!Array.isArray(ir.anchors)) error(filePath, "missing anchors array");

  for (const moduleName of requiredModules) {
    if (!ir[moduleName]) error(filePath, `missing ${moduleName}`);
  }

  for (const node of ir.method_graph?.nodes || []) {
    if (!hasAnchors(node)) {
      warn(filePath, `method_graph node ${node.node_id || node.label || "unknown"} missing anchors field`);
    } else if (node.anchors.length === 0) {
      warn(filePath, `method_graph node ${node.node_id || node.label || "unknown"} has empty anchors`);
    }
  }

  for (const claim of ir.claim_evidence_map?.claims || []) {
    if (!Array.isArray(claim.evidence) || claim.evidence.length === 0) {
      warn(filePath, `claim ${claim.claim_id || claim.claim || "unknown"} has no evidence`);
    }
  }

  for (const formula of ir.formula_ir?.formulas || []) {
    for (const variable of formula.variables || []) {
      if (!variable.confidence) {
        warn(filePath, `formula ${formula.formula_id || "unknown"} variable ${variable.symbol || "unknown"} missing confidence`);
      }
    }
  }
}

const files = collectFiles();
if (!files.length) {
  error(root, "no example Paper IR files found");
}

for (const file of files) {
  validatePaper(file);
}

if (errors) {
  console.error(`example validation failed: ${errors} error(s), ${warnings} warning(s)`);
  process.exit(1);
}

console.log(`example validation passed: ${files.length} file(s), ${warnings} warning(s)`);
