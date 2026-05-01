const { getPaperBundle } = require("../_demo");

module.exports = function handler(req, res) {
  const { paperId } = req.query;
  const bundle = getPaperBundle(paperId);
  if (!bundle) {
    res.status(404).json({ error: "not found" });
    return;
  }
  res.status(200).json(bundle.paper);
};
