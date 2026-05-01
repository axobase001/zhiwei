const { getPaperBundle } = require("../../_demo");

module.exports = function handler(req, res) {
  const bundle = getPaperBundle(req.query.paperId);
  if (!bundle) {
    res.status(404).json({ error: "not found" });
    return;
  }
  res.status(200).json({ anchors: bundle.anchors });
};
