# 下一阶段扩展建议

1. 用 PyMuPDF 或 GROBID 增强 parser，补齐公式、表格、caption 和 bbox 定位。
2. 将 Paper IR schema 拆成可版本化 JSON Schema，并加入 migration。
3. 把 LLM extraction 拆成多 pass：metadata、skeleton、method graph、formula、experiments、claim-evidence、reproduction。
4. 建立 10 篇 AI / LLM method paper gold benchmark，加入自动评估脚本。
5. 前端迁移到 Next.js + React Flow + PDF.js，实现 bbox 高亮、图谱编辑和多用户协作。
6. 增加 correction replay，把用户修正自动应用到 IR 视图并生成修订版 Paper IR。
7. 为 LoRA、RAG、DPO、Attention 等常见公式加入可交互 playground。
