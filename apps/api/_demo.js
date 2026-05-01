const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..", "..");
const BENCHMARK_DIR = path.join(ROOT, "samples", "benchmark", "generated");
const FALLBACK_IR = path.join(ROOT, "samples", "attention_demo_ir.json");

let cache = null;

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function paperFromIr(ir) {
  const meta = ir.metadata || {};
  return {
    id: meta.paper_id,
    title: meta.title,
    authors: meta.authors || [],
    year: meta.year || null,
    venue: meta.venue || null,
    arxiv_id: meta.arxiv_id || null,
    doi: meta.doi || null,
    language: meta.language || "en",
    paper_type: meta.paper_type || "AI / LLM 方法论文",
    citation_count: meta.citation_count || null,
    influential_citation_count: meta.influential_citation_count || null,
    importance_rank: meta.importance_rank || null,
    semantic_scholar_id: meta.semantic_scholar_id || null,
    file_path: "",
    status: "Mimo benchmark",
    created_at: meta.uploaded_at || ir.generated_at,
    updated_at: ir.generated_at
  };
}

function blocksFromAnchors(paperId, ir) {
  return (ir.anchors || []).map((anchor, index) => ({
    id: `${paperId}_blk_${String(index + 1).padStart(4, "0")}`,
    paper_id: paperId,
    block_type: anchor.source_type,
    content: anchor.text_span,
    page: anchor.page,
    section: anchor.section,
    bbox: anchor.bbox || null,
    anchor_id: anchor.anchor_id,
    created_at: ir.generated_at
  }));
}

function loadBenchmarkPapers() {
  if (!fs.existsSync(BENCHMARK_DIR)) return [];
  return fs
    .readdirSync(BENCHMARK_DIR, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => {
      const paperDir = path.join(BENCHMARK_DIR, entry.name);
      const irPath = path.join(paperDir, "paper_ir.json");
      if (!fs.existsSync(irPath)) return null;
      const ir = readJson(irPath);
      const paper = paperFromIr(ir);
      const blocksPath = path.join(paperDir, "document_blocks.json");
      const blocks = fs.existsSync(blocksPath) ? readJson(blocksPath) : blocksFromAnchors(paper.id, ir);
      return {
        paper,
        ir,
        anchors: ir.anchors || [],
        blocks
      };
    })
    .filter(Boolean)
    .sort((a, b) => {
      if (a.paper.id === "paper_attention_2017") return -1;
      if (b.paper.id === "paper_attention_2017") return 1;
      return (a.paper.year || 0) - (b.paper.year || 0) || a.paper.title.localeCompare(b.paper.title);
    });
}

function loadFallbackPaper() {
  const ir = readJson(FALLBACK_IR);
  const paper = paperFromIr(ir);
  paper.status = "示例论文";
  return {
    paper,
    ir,
    anchors: ir.anchors || [],
    blocks: blocksFromAnchors(paper.id, ir)
  };
}

function loadStore() {
  if (cache) return cache;
  const papers = loadBenchmarkPapers();
  cache = papers.length ? papers : [loadFallbackPaper()];
  return cache;
}

function listPapers() {
  return loadStore().map((item) => item.paper);
}

function getPaperBundle(paperId) {
  return loadStore().find((item) => item.paper.id === paperId) || null;
}

const first = loadStore()[0];

module.exports = {
  paper: first.paper,
  ir: first.ir,
  anchors: first.anchors,
  blocks: first.blocks,
  listPapers,
  getPaperBundle
};
