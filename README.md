# 知微

见微知著，见构知文。

知微是一个开源的论文结构化理解基础设施，用于将 AI / LLM / 机器学习论文编译成可交互、可回溯、可验证的知识结构。

它不是 PDF 总结器，也不是论文获取工具。知微的核心是 **Paper IR**：把论文中的问题、方法、公式、实验、论点、证据链和原文锚点转化为机器可读、用户可交互的开放结构。

> 把论文从静态 PDF 编译成可交互、可回溯、可验证的知识结构。

## Core Idea

```text
PDF → Document Blocks → Source Anchors → Paper IR → Visual Modules
```

知微关注的是理解层，而不是论文访问或分发层。

## Quick Start

### Requirements

- Node.js >= 18
- Python >= 3.10

### Install

```bash
git clone https://github.com/axobase001/zhiwei.git
cd zhiwei
npm install
```

### Run

```bash
npm run dev
```

Open:

```text
http://127.0.0.1:8765
```

### Windows Helper

```powershell
.\start.ps1
```

`npm run dev` 启动轻量 Node 本地服务器；`start.ps1` 是 Windows 下启动 Python 本地 API 的辅助脚本。

## Paper IR

Paper IR 是知微的开放中间表示，用于承载论文结构、公式、实验、论点、证据和 source anchors。

Schema:

```text
packages/paper-ir/schemas/paper-ir.schema.json
```

Spec:

```text
docs/paper-ir-spec.md
```

相关协议：

- Source Anchor: `docs/anchor-spec.md`
- Formula IR: `docs/formula-ir-spec.md`
- Claim-Evidence: `docs/claim-evidence-spec.md`
- Experiment Matrix: `docs/experiment-matrix-spec.md`
- Reproduction Roadmap: `docs/reproduction-roadmap-spec.md`

## Built-in Examples

- Attention Is All You Need
- LoRA
- Retrieval-Augmented Generation
- Direct Preference Optimization

Example IR:

```text
examples/
samples/benchmark/generated/
```

其中 `examples/*/paper-ir.json` 是稳定示例；`samples/benchmark/generated/` 保存 pipeline benchmark 输出。

## Repository Structure

```text
zhiwei/
  apps/
    web/          # Web renderer and local static server
    api/          # Serverless API adapter
    api-python/   # Local Python API server
  packages/
    paper-ir/     # Paper IR schemas and schema validation
    parser/       # PDF -> document blocks / source anchors
    extractor/    # document blocks -> Paper IR
    renderer/     # IR-driven rendering helpers
    benchmark/    # example and benchmark validation
    playground/   # experiments
  examples/       # stable Paper IR examples
  samples/        # generated benchmark outputs
  docs/           # specs, roadmap, contributing, manifesto
```

Canonical source lives under `apps/` and `packages/`. Root-level `api/`, `static/`, and `backend/` folders are compatibility entrypoints only.

## Development

```bash
npm run check
npm run check:api
npm run validate:schemas
npm run validate:examples
npm run test
```

## Contributing

See `docs/contributing.md`.

The longer project manifesto lives in `docs/manifesto.md`.

## License

Apache-2.0. See `LICENSE`.
