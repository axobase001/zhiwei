const { getPaperBundle } = require("../../../_demo");
const { toMarkdown } = require("../../../_markdown");

module.exports = function handler(req, res) {
  const bundle = getPaperBundle(req.query.paperId);
  if (!bundle) {
    res.status(404).json({ error: "not found" });
    return;
  }
  const { paper, ir } = bundle;
  const kind = req.query.kind;
  if (kind === "json") {
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.setHeader("Content-Disposition", `attachment; filename="${paper.id}_paper_ir.json"`);
    res.status(200).send(JSON.stringify(ir, null, 2));
    return;
  }
  if (kind === "markdown") {
    res.setHeader("Content-Type", "text/markdown; charset=utf-8");
    res.setHeader("Content-Disposition", `attachment; filename="${paper.id}_notes.md"`);
    res.status(200).send(toMarkdown(ir));
    return;
  }
  res.status(400).json({ error: "unsupported export" });
};
