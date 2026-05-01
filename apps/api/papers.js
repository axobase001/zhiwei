const { listPapers } = require("./_demo");

module.exports = function handler(req, res) {
  if (req.method === "GET") {
    res.status(200).json({ papers: listPapers() });
    return;
  }
  if (req.method === "POST") {
    res.status(501).json({
      error: "Vercel preview 暂不支持持久 PDF 上传解析。请使用本地版，或下一阶段接入对象存储和外部数据库。"
    });
    return;
  }
  res.status(405).json({ error: "method not allowed" });
};
