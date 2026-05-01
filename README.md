# 知微

> 见微知著，见构知文。

**知微是一个开源的论文结构化理解基础设施。**

它把 AI / LLM / 机器学习论文从静态 PDF 编译成可交互、可回溯、可验证的知识结构。

论文不应该只是 PDF。
公式不应该只是符号。
实验不应该只是表格。
人类最重要的技术思想，不应该只被少数熟悉暗号的人继承。

知微要做的，是为复杂论文建立一层开放的理解结构：

```text
PDF → Document Blocks → Source Anchors → Paper IR → Visual Modules
```

它不是 ChatPDF。
不是论文总结器。
不是文献分发服务。

它关注的不是“如何拿到论文”，而是：

> **拿到论文之后，如何真正理解它。**

第一堵墙是访问。
第二堵墙是理解。
知微要拆第二堵墙。

## Core Idea

知微的核心不是聊天框，也不是一段摘要，而是 **Paper IR**。

Paper IR 是一种开放的中间表示：它把论文中的问题、方法、公式、实验、论点、证据链和原文锚点转化为机器可读、用户可交互的结构。

```text
PDF
  → Document Blocks
  → Source Anchors
  → Paper IR
  → 知微·构 / 析 / 证 / 辨 / 验 / 径
```

所有解释节点都应该能回到来源。没有 source anchor 的强结论，不应该被当成确定事实展示。

## Why 知微 Exists

现代科学正在以前所未有的速度增长。

每一天，新的模型、新的理论、新的实验和新的系统被写进论文。
它们是人类文明最顶级的知识结晶，却常常被三重墙挡住：

- 语言的墙；
- 形式化表达的墙；
- 信息结构复杂度的墙。

很多人不是不够聪明。
他们只是没有导师、没有路径、没有足够熟悉那些论文里的暗号。

知微不想把论文压扁成摘要。
我们想把论文拆成可以追踪、可以验证、可以交互的结构：

- 一个概念如何被定义；
- 一个公式为什么出现；
- 一个实验到底在证明什么；
- 一个 claim 由哪张表、哪幅图、哪个消融支撑；
- 一个方法相对 baseline 到底改了哪里；
- 一个读者如何从局部细节走到整篇论文的核心。

> 真正的理解不是消灭复杂性，而是为复杂性建立路径。

## What We Are Building

知微将复杂论文编译成一种新的知识界面。

- **知微·构**：重建论文的结构骨架；
- **知微·析**：拆解公式、变量、概念和图表；
- **知微·证**：追踪 claim 与证据链；
- **知微·辨**：呈现方法差异、baseline、局限与争议；
- **知微·验**：重建实验逻辑，说明实验到底在证明什么；
- **知微·径**：生成理解路径、复现路线与风险提示。

知微不是替人“读完论文”。
知微是帮助人进入论文。

> We do not replace reading.
> We make deep reading possible.

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

Paper IR 是知微的开放协议边界。Parser、extractor、renderer、benchmark 和外部工具都应该通过 Paper IR 交换论文理解结果，而不是依赖 UI 私有结构。

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

第一批稳定示例：

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

## Relation Graphs

知微不只解析单篇论文。
下一阶段，它会把论文、公式、实验、代码和相关工作连接成可验证的关系图谱。

计划中的图谱包括：

- **Paper Relation Graph**：论文与论文之间的继承、改进、对比和扩展关系；
- **Formula Relation Graph**：公式、变量、机制和直觉解释之间的依赖关系；
- **Code Relation Graph**：论文方法、公式与代码实现之间的对应关系。

目标是让重要论文不再孤立地存在于 PDF 里，而是成为可以被连接、比较、复用和验证的知识对象。

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

Good first contributions include:

- improving Paper IR schema coverage;
- adding source-grounded example IR;
- strengthening formula / claim / experiment validation;
- building renderer components that consume Paper IR without hardcoded paper content;
- improving docs for parser, extractor, and benchmark workflows.

## Manifesto

如果你想知道知微为什么不是另一个 PDF reader，可以读长版宣言：

- `docs/manifesto.md`

一句话说：

> 科学不是神庙里的密文。
> 科学是人类共同写下的火种。

## License

Apache-2.0. See `LICENSE`.
