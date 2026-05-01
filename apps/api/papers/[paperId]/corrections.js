const { getPaperBundle } = require("../../_demo");

module.exports = function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "method not allowed" });
    return;
  }
  const bundle = getPaperBundle(req.query.paperId);
  if (!bundle) {
    res.status(404).json({ error: "not found" });
    return;
  }
  res.status(200).json({
    ok: true,
    correction_id: `vercel_corr_${Date.now()}`,
    paper_id: bundle.paper.id,
    persistence: "preview_only"
  });
};
