module.exports = function handler(req, res) {
  res.status(200).json({ ok: true, name: "知微", mode: "vercel-preview", time: new Date().toISOString() });
};
