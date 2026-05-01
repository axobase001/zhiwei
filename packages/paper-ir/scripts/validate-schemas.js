import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, "..");
const schemaDir = path.join(root, "schemas");
const paperIrPath = path.join(schemaDir, "paper-ir.schema.json");

const requiredTopLevel = [
  "schema_version",
  "metadata",
  "anchors",
  "paper_skeleton",
  "method_graph",
  "method_delta",
  "formula_ir",
  "experiment_matrix",
  "claim_evidence_map",
  "glossary",
  "reproduction_roadmap",
  "verification"
];

function fail(message) {
  console.error(`schema validation failed: ${message}`);
  process.exitCode = 1;
}

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    fail(`${path.relative(process.cwd(), filePath)} is not valid JSON: ${error.message}`);
    return null;
  }
}

for (const file of fs.readdirSync(schemaDir).filter((name) => name.endsWith(".json"))) {
  const schema = readJson(path.join(schemaDir, file));
  if (!schema) continue;
  if (!schema.$schema && file === "paper-ir.schema.json") {
    fail(`${file} must declare $schema`);
  }
  if (!schema.type && !schema.$ref && !schema.properties) {
    fail(`${file} does not look like a JSON Schema`);
  }
}

const paperIr = readJson(paperIrPath);
if (paperIr) {
  if (paperIr.type !== "object") fail("paper-ir.schema.json must describe an object");
  if (!paperIr.properties || typeof paperIr.properties !== "object") {
    fail("paper-ir.schema.json must contain properties");
  }
  const declaredRequired = new Set(paperIr.required || []);
  for (const field of requiredTopLevel) {
    if (!paperIr.properties?.[field]) fail(`paper-ir.schema.json missing properties.${field}`);
    if (!declaredRequired.has(field)) fail(`paper-ir.schema.json missing required field ${field}`);
  }
}

if (process.exitCode) {
  process.exit(process.exitCode);
}

console.log("schema validation passed");
