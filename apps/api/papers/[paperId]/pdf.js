module.exports = function handler(req, res) {
  res.status(404).json({ error: "Vercel preview demo has no original PDF." });
};
