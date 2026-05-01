# 已知问题

1. v1 默认使用 `pypdf` 抽取文本，暂不提供 bbox 级高亮；IR 已保留 `bbox` 字段，前端先按 `page + text_span` 回跳。
2. 默认 extractor 是启发式 grounded 版本，能建立完整 Paper IR，但复杂论文的 baseline、claim 和公式变量仍需要用户修正。
3. LLM provider 已抽象为 OpenAI-compatible API，但默认关闭；接入后仍必须通过 grounding verification。
4. Demo 样例没有真实 PDF，只用于验证六个模块和 anchor 机制。
5. 前端不依赖 React Flow / PDF.js 构建链，第一版用原生 SVG 和浏览器 PDF viewer 降低安装门槛；后续可替换为 React Flow + PDF.js。
