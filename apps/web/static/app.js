// ------------------------------
// State and Copy
// ------------------------------

const moduleIds = ["structure", "formula", "evidence", "delta", "experiments", "reproduction"];

const moduleText = {
  zh: {
    structure: ["知微·构", "结构解析", "从问题、方法、实验到结论，重建论文的结构骨架。"],
    formula: ["知微·析", "公式拆解", "把关键公式拆成变量、依赖关系和直觉解释。"],
    evidence: ["知微·证", "证据链溯源", "查看核心 claim 如何被表格、实验、段落和图支撑。"],
    delta: ["知微·辨", "方法差异对比", "解释本文相对 baseline 或既有范式改了哪里。"],
    experiments: ["知微·验", "实验逻辑重建", "把实验按证明目的重新组织，而不是只复述表格。"],
    reproduction: ["知微·径", "复现路线生成", "整理数据、模型、算力、步骤、缺失细节和风险点。"]
  },
  en: {
    structure: ["Structure", "Paper Structure", "Rebuild the paper from problem, method, experiments, and claims."],
    formula: ["Formula", "Formula Deconstruction", "Break key formulas into variables, dependencies, and grounded intuition."],
    evidence: ["Evidence", "Claim-Evidence Chain", "Inspect how claims are supported by tables, experiments, paragraphs, and figures."],
    delta: ["Delta", "Method Delta", "Explain how the paper changes prior baselines or existing paradigms."],
    experiments: ["Experiments", "Experiment Logic", "Organize experiments by what they try to prove, not by table order."],
    reproduction: ["Reproduce", "Reproduction Roadmap", "Track datasets, models, compute, steps, missing details, and risk points."]
  }
};

const uiText = {
  zh: {
    "brand.name": "知微",
    "brand.slogan": "见微知著，见构知文。",
    "header.currentPaper": "当前论文",
    "actions.upload": "上传 PDF",
    "actions.reparse": "重新解析",
    "actions.export": "导出",
    "actions.exportMarkdown": "Markdown 学习笔记",
    "actions.exportPng": "PNG 图谱",
    "source.paperSource": "论文源文",
    "source.overviewMode": "总览模式",
    "source.viewSource": "查看原文",
    "source.enterDetail": "进入详情工作台",
    "source.prevPage": "上一页",
    "source.nextPage": "下一页",
    "source.page": "页码",
    "source.zoom": "缩放",
    "source.pdfTitle": "PDF 原文",
    "source.currentSource": "当前来源",
    "source.locate": "定位原文",
    "source.noAnchor": "尚未选择 anchor",
    "source.noAnchorText": "点击任意节点或证据来源后，这里显示原文摘录。",
    "source.demoMode": "当前为示例模式",
    "source.noPdf": "暂未加载原始 PDF",
    "source.demoText": "你仍可以查看完整结构化解析结果。上传自己的论文后，知微会同步显示原文定位与证据锚点。",
    "library.title": "论文库",
    "library.current": "当前论文",
    "library.regexSearch": "正则搜索",
    "library.searchPlaceholder": "例如: resnet|lora|rag",
    "library.choosePaper": "选择论文",
    "library.selectPaper": "选择论文",
    "library.invalidRegex": "正则无效",
    "library.matched": "匹配 {count} 篇",
    "library.defaultHint": "默认显示最重要的 {count} 篇，可输入正则搜索全部论文",
    "detail.backOverview": "← 返回总览",
    "detail.chooseNodeTitle": "选择一个结构节点",
    "detail.chooseNodeText": "知微会在这里显示解释、证据来源与可修正内容。",
    "detail.interpretation": "节点解读",
    "detail.role": "它在论文中的作用",
    "detail.evidence": "证据与来源",
    "detail.variables": "变量解释",
    "detail.risks": "风险提示",
    "detail.noSource": "没有绑定来源，verification 会提示风险。",
    "correction.summary": "修正这个节点",
    "correction.title": "标题",
    "correction.description": "解释",
    "correction.save": "保存修正",
    "correction.markIncorrect": "标记不准确",
    "overview.eyebrow": "论文总览",
    "overview.chainEyebrow": "认知链",
    "overview.chainTitle": "先建立整体感，再进入细节",
    "overview.expand": "展开查看",
    "overview.modulesEyebrow": "六大模块",
    "overview.modulesTitle": "选择一个方向深挖",
    "overview.pathEyebrow": "推荐路径",
    "overview.pathTitle": "从哪里开始看",
    "overview.pathFastLabel": "3 分钟理解",
    "overview.pathFastTitle": "先看这篇论文想解决什么",
    "overview.pathFastDesc": "问题 → 核心思想 → 方法差异 → 结论",
    "overview.pathDeltaLabel": "方法读者",
    "overview.pathDeltaTitle": "先看本文相对 baseline 改了哪里",
    "overview.pathDeltaDesc": "进入知微·辨，快速定位方法变化。",
    "overview.pathFormulaLabel": "公式读者",
    "overview.pathFormulaTitle": "先看关键公式和变量怎么工作",
    "overview.pathFormulaDesc": "进入知微·析，拆解公式角色、变量和依赖。",
    "overview.problem": "问题",
    "overview.coreIdea": "核心思想",
    "overview.method": "方法",
    "overview.conclusion": "结论",
    "overview.methodStructure": "方法结构",
    "overview.trainingInference": "训练/推理",
    "overview.experiments": "实验",
    "overview.claims": "结论",
    "guide.eyebrow": "当前论文速览",
    "guide.title": "建议先建立结构感",
    "guide.copy": "先用总览页建立问题、方法和证据链的整体关系，再进入某个模块深挖。",
    "guide.difficulty": "阅读难度",
    "guide.type": "论文类型",
    "guide.formulas": "关键公式",
    "guide.claims": "主要 claim",
    "guide.entries": "推荐入口",
    "guide.fromCore": "从核心思想开始",
    "guide.fromDelta": "从方法差异开始",
    "guide.fromFormula": "从公式开始",
    "guide.fromExperiments": "从实验开始",
    "guide.tips": "学习提示",
    "guide.tip1": "第一次读这篇论文：建议先看“知微·辨”，理解它相对既有方法改了哪里。",
    "guide.tip2": "已经熟悉背景：可直接进入“知微·析”或“知微·验”，复核公式与实验逻辑。",
    "status.ready": "示例论文",
    "status.parsing": "解析中",
    "status.corrected": "已修正",
    "status.marked": "已标记"
  },
  en: {
    "brand.name": "知微",
    "brand.slogan": "See the structure. Understand the paper.",
    "header.currentPaper": "Current Paper",
    "actions.upload": "Upload PDF",
    "actions.reparse": "Reparse",
    "actions.export": "Export",
    "actions.exportMarkdown": "Markdown Notes",
    "actions.exportPng": "PNG Graph",
    "source.paperSource": "Paper Source",
    "source.overviewMode": "Overview Mode",
    "source.viewSource": "View Source",
    "source.enterDetail": "Open Workspace",
    "source.prevPage": "Prev",
    "source.nextPage": "Next",
    "source.page": "Page",
    "source.zoom": "Zoom",
    "source.pdfTitle": "PDF Source",
    "source.currentSource": "Current Source",
    "source.locate": "Locate",
    "source.noAnchor": "No anchor selected",
    "source.noAnchorText": "Select any node or evidence source to see the original excerpt here.",
    "source.demoMode": "Demo mode",
    "source.noPdf": "Original PDF not loaded",
    "source.demoText": "You can still inspect the complete structured result. Upload your own paper to enable source positioning and evidence anchors.",
    "library.title": "Paper Library",
    "library.current": "Current Paper",
    "library.regexSearch": "Regex Search",
    "library.searchPlaceholder": "e.g. resnet|lora|rag",
    "library.choosePaper": "Choose paper",
    "library.selectPaper": "Choose paper",
    "library.invalidRegex": "Invalid regex",
    "library.matched": "{count} matched",
    "library.defaultHint": "Showing the top {count} papers. Use regex to search the full library.",
    "detail.backOverview": "← Back to Overview",
    "detail.chooseNodeTitle": "Select a Structure Node",
    "detail.chooseNodeText": "This panel will show interpretation, evidence sources, and correction controls here.",
    "detail.interpretation": "Interpretation",
    "detail.role": "Role in the Paper",
    "detail.evidence": "Evidence and Sources",
    "detail.variables": "Variable Explanation",
    "detail.risks": "Risk Flags",
    "detail.noSource": "No source anchors are attached; verification should flag this risk.",
    "correction.summary": "Correct This Node",
    "correction.title": "Title",
    "correction.description": "Explanation",
    "correction.save": "Save Correction",
    "correction.markIncorrect": "Mark Inaccurate",
    "overview.eyebrow": "Paper Overview",
    "overview.chainEyebrow": "Cognitive Chain",
    "overview.chainTitle": "Build the whole picture before drilling down",
    "overview.expand": "Open detail",
    "overview.modulesEyebrow": "Six Modules",
    "overview.modulesTitle": "Choose a direction to inspect",
    "overview.pathEyebrow": "Suggested Paths",
    "overview.pathTitle": "Where to start",
    "overview.pathFastLabel": "3-minute read",
    "overview.pathFastTitle": "Start with the problem this paper solves",
    "overview.pathFastDesc": "Problem → Core idea → Method delta → Conclusion",
    "overview.pathDeltaLabel": "Method reader",
    "overview.pathDeltaTitle": "See what changed from the baseline",
    "overview.pathDeltaDesc": "Open Method Delta to locate the key changes quickly.",
    "overview.pathFormulaLabel": "Formula reader",
    "overview.pathFormulaTitle": "See how the core formulas work",
    "overview.pathFormulaDesc": "Open Formula to inspect roles, variables, and dependencies.",
    "overview.problem": "Problem",
    "overview.coreIdea": "Core Idea",
    "overview.method": "Method",
    "overview.conclusion": "Conclusion",
    "overview.methodStructure": "Method Structure",
    "overview.trainingInference": "Training / Inference",
    "overview.experiments": "Experiments",
    "overview.claims": "Claims",
    "guide.eyebrow": "Paper Snapshot",
    "guide.title": "Start with the structure",
    "guide.copy": "Use the overview to connect the problem, method, and evidence chain before opening a specific module.",
    "guide.difficulty": "Difficulty",
    "guide.type": "Paper Type",
    "guide.formulas": "Formulas",
    "guide.claims": "Claims",
    "guide.entries": "Suggested Entry Points",
    "guide.fromCore": "Start from the core idea",
    "guide.fromDelta": "Start from method delta",
    "guide.fromFormula": "Start from formulas",
    "guide.fromExperiments": "Start from experiments",
    "guide.tips": "Reading Tips",
    "guide.tip1": "First time reading this paper: start with Delta to see how it changes prior methods.",
    "guide.tip2": "Already know the background: jump to Formula or Experiments to audit the mechanism and evidence.",
    "status.ready": "Demo Paper",
    "status.parsing": "Parsing",
    "status.corrected": "Corrected",
    "status.marked": "Marked"
  }
};

const state = {
  papers: [],
  paper: null,
  ir: null,
  blocks: [],
  anchorMap: new Map(),
  view: "overview",
  module: "structure",
  selected: null,
  selectedAnchor: null,
  currentPage: 1,
  zoom: 100,
  paperPickerOpen: false,
  paperFilter: "",
  lang: localStorage.getItem("zhiwei_lang") === "en" ? "en" : "zh"
};

const $ = (id) => document.getElementById(id);

document.addEventListener("DOMContentLoaded", () => {
  bindEvents();
  applyLanguage();
  renderTabs();
  loadPapers();
});

// ------------------------------
// I18N
// ------------------------------

function t(key, fallback = "") {
  return uiText[state.lang]?.[key] || uiText.zh[key] || fallback || key;
}

function formatText(key, values = {}, fallback = "") {
  return t(key, fallback).replace(/\{(\w+)\}/g, (_, name) => String(values[name] ?? ""));
}

function getModules() {
  const copy = moduleText[state.lang] || moduleText.zh;
  return moduleIds.map((id) => [id, ...(copy[id] || moduleText.zh[id])]);
}

function applyLanguage() {
  document.documentElement.lang = state.lang === "en" ? "en" : "zh-CN";
  document.documentElement.dataset.lang = state.lang;
  document.title = state.lang === "en" ? "知微 · Paper IR Infrastructure" : "知微 · 论文结构化理解基础设施";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n, el.textContent);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.setAttribute("placeholder", t(el.dataset.i18nPlaceholder, el.getAttribute("placeholder") || ""));
  });
  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    el.setAttribute("title", t(el.dataset.i18nTitle, el.getAttribute("title") || ""));
  });
  document.querySelectorAll("[data-i18n-aria-label]").forEach((el) => {
    el.setAttribute("aria-label", t(el.dataset.i18nAriaLabel, el.getAttribute("aria-label") || ""));
  });
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.lang === state.lang);
  });
}

function bindEvents() {
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.lang = btn.dataset.lang === "en" ? "en" : "zh";
      localStorage.setItem("zhiwei_lang", state.lang);
      applyLanguage();
      updatePaperChrome();
      renderTabs();
      renderPaperList();
      renderWorkspace();
      renderDetail();
      renderSourceInspector();
      renderPdf();
    });
  });
  $("pdf-input").addEventListener("change", handleUpload);
  $("reparse-btn").addEventListener("click", reparseCurrent);
  $("paper-picker-btn").addEventListener("click", () => togglePaperPicker());
  $("paper-search-input").addEventListener("input", (event) => {
    state.paperFilter = event.target.value || "";
    renderPaperList();
  });
  $("export-menu-btn").addEventListener("click", () => $("export-menu").classList.toggle("open"));
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".export-wrap")) $("export-menu").classList.remove("open");
    if (!event.target.closest("#paper-picker")) closePaperPicker();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closePaperPicker();
  });
  document.querySelectorAll("[data-export]").forEach((item) => {
    item.addEventListener("click", () => {
      const kind = item.dataset.export;
      $("export-menu").classList.remove("open");
      if (kind === "png") exportGraphPng();
      else exportFile(kind);
    });
  });
  $("prev-page-btn").addEventListener("click", () => jumpPage(Math.max(1, state.currentPage - 1)));
  $("next-page-btn").addEventListener("click", () => jumpPage(state.currentPage + 1));
  $("page-input").addEventListener("change", (event) => jumpPage(Number(event.target.value || 1)));
  $("back-overview-btn").addEventListener("click", showOverview);
  $("side-enter-detail-btn").addEventListener("click", () => enterDetail("structure"));
  $("side-view-source-btn").addEventListener("click", () => enterDetail(state.module || "structure"));
  $("zoom-select").addEventListener("change", (event) => {
    state.zoom = Number(event.target.value || 100);
    renderPdf();
  });
  $("locate-source-btn").addEventListener("click", () => {
    if (state.selectedAnchor) goToAnchor(state.selectedAnchor.anchor_id);
  });
  $("correction-form").addEventListener("submit", saveCorrection);
  $("mark-incorrect-btn").addEventListener("click", markIncorrect);
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

// ------------------------------
// Data Loading
// ------------------------------

async function loadPapers() {
  const data = await api("/api/papers");
  state.papers = data.papers || [];
  renderPaperList();
  if (!state.paper && state.papers.length) {
    const preferred = state.papers.find((paper) => paper.id === "paper_attention_2017") || state.papers[0];
    await selectPaper(preferred.id);
  }
}

async function selectPaper(paperId) {
  const [paper, ir, blocksData] = await Promise.all([
    api(`/api/papers/${paperId}`),
    api(`/api/papers/${paperId}/ir`),
    api(`/api/papers/${paperId}/blocks`)
  ]);
  state.paper = paper;
  state.ir = ir;
  state.blocks = blocksData.blocks || [];
  state.anchorMap = new Map((ir.anchors || []).map((anchor) => [anchor.anchor_id, anchor]));
  state.view = "overview";
  state.module = "structure";
  state.selected = null;
  state.selectedAnchor = null;
  state.currentPage = 1;
  closePaperPicker();
  updatePaperChrome();
  renderPaperList();
  renderWarnings();
  renderTabs();
  renderWorkspace();
  renderDetail();
  renderPdf();
  renderSourceInspector();
}

function updatePaperChrome() {
  const meta = state.ir?.metadata || state.paper || {};
  $("paper-title").textContent = meta.title || "未命名论文";
  $("status-pill").textContent = statusLabel(state.paper?.status || "ready");
  $("paper-meta").textContent = [meta.year, meta.venue, meta.paper_type].filter(Boolean).join(" · ") || "AI / LLM 方法论文";
  $("side-paper-title").textContent = meta.title || "未命名论文";
  $("side-paper-authors").textContent = compactAuthors(meta.authors || state.paper?.authors || []);
  $("side-paper-tags").innerHTML = paperTags(meta)
    .filter(Boolean)
    .map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`)
    .join("");
  $("side-paper-summary").textContent = overviewSummary().oneLiner;
  $("page-input").value = String(state.currentPage);
  document.body.classList.toggle("overview-mode", state.view === "overview");
  document.body.classList.toggle("detail-mode", state.view === "detail");
}

function statusLabel(status) {
  const raw = String(status || "").toLowerCase();
  if (raw.includes("解析") || raw.includes("parsing")) return t("status.parsing");
  if (raw.includes("修正") || raw.includes("corrected")) return t("status.corrected");
  if (raw.includes("标记") || raw.includes("marked")) return t("status.marked");
  if (raw.includes("示例") || raw.includes("demo") || raw === "ready") return t("status.ready");
  return status || t("status.ready");
}

function paperTags(meta) {
  const typeTags = String(meta.paper_type || "")
    .split("/")
    .map((tag) => tag.trim())
    .filter(Boolean)
    .slice(0, 3);
  return [meta.year, meta.venue, ...typeTags];
}

function compactAuthors(authors) {
  if (!authors || !authors.length) return state.lang === "en" ? "Unknown authors" : "作者未知";
  if (authors.length <= 2) return authors.join(", ");
  return `${authors[0]} et al.`;
}

function compactText(value, max = 90) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  if (text.length <= max) return text;
  return `${text.slice(0, max - 1)}…`;
}

function togglePaperPicker() {
  state.paperPickerOpen = !state.paperPickerOpen;
  renderPaperPickerState();
  if (state.paperPickerOpen) {
    setTimeout(() => $("paper-search-input").focus(), 0);
  }
}

function closePaperPicker() {
  if (!state.paperPickerOpen) return;
  state.paperPickerOpen = false;
  renderPaperPickerState();
}

function renderPaperPickerState() {
  const picker = $("paper-picker");
  const button = $("paper-picker-btn");
  if (!picker || !button) return;
  picker.classList.toggle("open", state.paperPickerOpen);
  button.setAttribute("aria-expanded", state.paperPickerOpen ? "true" : "false");
}

function renderPaperList() {
  const currentTitle = state.paper?.title || state.ir?.metadata?.title || t("library.selectPaper");
  $("paper-picker-current").textContent = currentTitle;
  $("paper-search-input").value = state.paperFilter;
  renderPaperPickerState();
  const result = filterPapers(state.papers, state.paperFilter);
  const visible = result.papers;
  const hint = $("paper-search-hint");
  hint.classList.toggle("warn", Boolean(result.error));
  hint.textContent = result.error
    ? `${t("library.invalidRegex")}：${result.error}`
    : state.paperFilter.trim()
      ? formatText("library.matched", { count: visible.length })
      : formatText("library.defaultHint", { count: visible.length });
  $("paper-list").innerHTML = visible
    .map((paper) => {
      const active = state.paper && state.paper.id === paper.id ? "active" : "";
      const meta = paperMetaLine(paper);
      return `<button class="paper-switch ${active}" data-paper-id="${escapeHtml(paper.id)}" type="button" role="option" aria-selected="${active ? "true" : "false"}">
        <span>${escapeHtml(paper.title || (state.lang === "en" ? "Untitled Paper" : "未命名论文"))}</span>
        <small>${escapeHtml(meta || paper.id)}</small>
      </button>`;
    })
    .join("");
  document.querySelectorAll(".paper-switch").forEach((item) => {
    item.addEventListener("click", () => {
      closePaperPicker();
      selectPaper(item.dataset.paperId);
    });
  });
}

function paperImportance(paper) {
  const rank = Number(paper.importance_rank || paper.rank || 0);
  const citations = Number(paper.citation_count || paper.citationCount || 0);
  if (rank > 0) return 100000000 - rank;
  if (citations > 0) return citations;
  const year = Number(paper.year || 0);
  if (paper.id === "paper_attention_2017") return 90000000;
  return year;
}

function sortedPapers(papers) {
  return [...papers].sort((a, b) => paperImportance(b) - paperImportance(a) || String(a.title).localeCompare(String(b.title)));
}

function filterPapers(papers, pattern) {
  const sorted = sortedPapers(papers);
  const query = pattern.trim();
  const defaultLimit = 6;
  if (!query) {
    const active = state.paper && !sorted.slice(0, defaultLimit).some((paper) => paper.id === state.paper.id) ? [state.paper] : [];
    return { papers: [...active, ...sorted.filter((paper) => !active.some((item) => item.id === paper.id)).slice(0, defaultLimit)], error: "" };
  }
  try {
    const regex = new RegExp(query, "i");
    return {
      papers: sorted.filter((paper) => regex.test(searchablePaperText(paper))).slice(0, 24),
      error: ""
    };
  } catch (error) {
    return { papers: sorted.slice(0, defaultLimit), error: error.message || "invalid regex" };
  }
}

function searchablePaperText(paper) {
  return [paper.title, paper.authors?.join(" "), paper.year, paper.venue, paper.paper_type, paper.status, paper.id]
    .filter(Boolean)
    .join(" ");
}

function paperMetaLine(paper) {
  const bits = [];
  if (paper.importance_rank) bits.push(`#${paper.importance_rank}`);
  if (paper.citation_count) bits.push(`${paper.citation_count} citations`);
  bits.push(...[paper.year, paper.venue, paper.status].filter(Boolean));
  return bits.join(" · ");
}

function renderTabs() {
  const modules = getModules();
  $("module-tabs").innerHTML = modules
    .map(([id, label]) => `<button class="module-tab ${state.module === id ? "active" : ""}" data-module="${id}" type="button">${label}</button>`)
    .join("");
  document.querySelectorAll(".module-tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.module = btn.dataset.module;
      state.selected = null;
      renderTabs();
      renderWorkspace();
      renderDetail();
    });
  });
  const current = modules.find(([id]) => id === state.module) || modules[0];
  $("module-eyebrow").textContent = current[1];
  $("module-title").textContent = current[2];
  $("module-desc").textContent = current[3];
  document.body.classList.toggle("overview-mode", state.view === "overview");
  document.body.classList.toggle("detail-mode", state.view === "detail");
}

// ------------------------------
// Renderers
// ------------------------------

function renderWarnings() {
  const warnings = (state.ir?.verification?.warnings || []).filter((warning) => warning.severity !== "info");
  const box = $("warnings");
  if (!warnings.length) {
    box.classList.remove("show");
    box.innerHTML = "";
    return;
  }
  box.classList.add("show");
  const label = state.lang === "en" ? `${warnings.length} item(s) need review` : `${warnings.length} 项需要复核`;
  box.innerHTML = `<strong>Grounding warning</strong><span>${label}：${escapeHtml(warnings[0].message)}</span>`;
}

function renderWorkspace() {
  if (!state.ir) {
    $("workspace").innerHTML = `<div class="empty-state"><strong>${state.lang === "en" ? "No paper loaded" : "未加载论文"}</strong><span>${state.lang === "en" ? "Upload a PDF or choose a demo paper." : "上传 PDF 或选择示例论文。"}</span></div>`;
    return;
  }
  if (state.view === "overview") {
    renderOverview();
    return;
  }
  const renderers = {
    structure: renderStructure,
    formula: renderFormula,
    evidence: renderEvidence,
    delta: renderDelta,
    experiments: renderExperiments,
    reproduction: renderReproduction
  };
  renderers[state.module]();
}

function showOverview() {
  state.view = "overview";
  state.selected = null;
  updatePaperChrome();
  renderTabs();
  renderWorkspace();
  renderDetail();
  renderPdf();
}

function enterDetail(moduleId = "structure", selection = null) {
  state.view = "detail";
  state.module = moduleId;
  state.selected = selection;
  updatePaperChrome();
  renderTabs();
  renderWorkspace();
  renderDetail();
  renderPdf();
  if (selection?.anchors?.[0]) goToAnchor(selection.anchors[0], false);
}

function renderOverview() {
  const summary = overviewSummary();
  const chain = overviewChain();
  const cards = moduleCards();
  $("workspace").innerHTML = `<div class="overview-page">
    <section class="overview-hero">
      <div class="hero-copy">
        <div class="context-eyebrow">${escapeHtml(t("overview.eyebrow"))}</div>
        <h2>${escapeHtml(summary.title)}</h2>
        <p>${escapeHtml(summary.subtitle)}</p>
      </div>
      <div class="summary-quads">
        ${summary.cards
          .map((card) => `<article class="summary-tile">
            <span>${escapeHtml(card.label)}</span>
            <p>${escapeHtml(card.text)}</p>
          </article>`)
          .join("")}
      </div>
    </section>

    <section class="overview-section">
      <div class="section-head">
        <div>
          <div class="context-eyebrow">${escapeHtml(t("overview.chainEyebrow"))}</div>
          <h3>${escapeHtml(t("overview.chainTitle"))}</h3>
        </div>
      </div>
      <div class="cognitive-chain">
        ${chain
          .map((item, index) => `<button class="chain-node" data-chain="${escapeHtml(item.id)}" type="button">
            <span>${String(index + 1).padStart(2, "0")}</span>
            <strong>${escapeHtml(item.title)}</strong>
            <em>${escapeHtml(item.summary)}</em>
            <b>${escapeHtml(t("overview.expand"))}</b>
          </button>`)
          .join("")}
      </div>
    </section>

    <section class="overview-section">
      <div class="section-head">
        <div>
          <div class="context-eyebrow">${escapeHtml(t("overview.modulesEyebrow"))}</div>
          <h3>${escapeHtml(t("overview.modulesTitle"))}</h3>
        </div>
      </div>
      <div class="module-entry-grid">
        ${cards
          .map((card) => `<button class="module-entry" data-module="${escapeHtml(card.module)}" type="button">
            <div>
              <span>${escapeHtml(card.name)}</span>
              <h4>${escapeHtml(card.title)}</h4>
              <p>${escapeHtml(card.desc)}</p>
            </div>
            <strong>${card.count}</strong>
          </button>`)
          .join("")}
      </div>
    </section>

    <section class="overview-section">
      <div class="section-head">
        <div>
          <div class="context-eyebrow">${escapeHtml(t("overview.pathEyebrow"))}</div>
          <h3>${escapeHtml(t("overview.pathTitle"))}</h3>
        </div>
      </div>
      <div class="path-grid">
        <button class="path-card" data-path="problem" type="button">
          <span>${escapeHtml(t("overview.pathFastLabel"))}</span>
          <strong>${escapeHtml(t("overview.pathFastTitle"))}</strong>
          <p>${escapeHtml(t("overview.pathFastDesc"))}</p>
        </button>
        <button class="path-card" data-path="delta" type="button">
          <span>${escapeHtml(t("overview.pathDeltaLabel"))}</span>
          <strong>${escapeHtml(t("overview.pathDeltaTitle"))}</strong>
          <p>${escapeHtml(t("overview.pathDeltaDesc"))}</p>
        </button>
        <button class="path-card" data-path="formula" type="button">
          <span>${escapeHtml(t("overview.pathFormulaLabel"))}</span>
          <strong>${escapeHtml(t("overview.pathFormulaTitle"))}</strong>
          <p>${escapeHtml(t("overview.pathFormulaDesc"))}</p>
        </button>
      </div>
    </section>
  </div>`;
  bindOverviewActions(chain);
}

function overviewSummary() {
  const meta = state.ir?.metadata || {};
  const skeleton = state.ir?.paper_skeleton || {};
  const claims = state.ir?.claim_evidence_map?.claims || [];
  const conclusion = claims[0]?.claim || skeleton.experiments?.summary || (state.lang === "en" ? "Every conclusion keeps source anchors for detail-level tracing." : "所有结论都保留 source anchor，可进入详情页逐项回溯。");
  return {
    title: meta.title || (state.lang === "en" ? "Untitled Paper" : "未命名论文"),
    subtitle: compactText(skeleton.core_idea?.summary || skeleton.method?.summary || meta.paper_type || (state.lang === "en" ? "AI / LLM method paper" : "AI / LLM 方法论文"), 92),
    oneLiner: compactText(skeleton.core_idea?.summary || skeleton.problem?.summary || (state.lang === "en" ? "This paper has been compiled into clickable, source-grounded Paper IR." : "这篇论文已被编译为可点击、可回溯来源的 Paper IR。"), 120),
    cards: [
      { label: t("overview.problem"), text: compactText(skeleton.problem?.summary || (state.lang === "en" ? "Open Structure to inspect the problem statement." : "查看知微·构中的问题定义。"), 88) },
      { label: t("overview.coreIdea"), text: compactText(skeleton.core_idea?.summary || (state.lang === "en" ? "Open Structure to inspect the core idea." : "查看知微·构中的核心思想。"), 88) },
      { label: t("overview.method"), text: compactText(skeleton.method?.summary || (state.lang === "en" ? "Open Delta to inspect method changes." : "查看知微·辨中的方法变化。"), 88) },
      { label: t("overview.conclusion"), text: compactText(conclusion, 88) }
    ]
  };
}

function overviewChain() {
  const graphNodes = new Map((state.ir?.method_graph?.nodes || []).map((node) => [node.node_id, normalizeGraphNode(node)]));
  const skeleton = state.ir?.paper_skeleton || {};
  const claims = state.ir?.claim_evidence_map?.claims || [];
  const makeSelection = (id, title, summary, anchors) => ({
    id,
    title,
    summary,
    type: "overview",
    typeLabel: state.lang === "en" ? "Overview Node" : "总览节点",
    anchors: anchors || [],
    raw: { node_id: id, title, summary, anchors: anchors || [] }
  });
  return [
    { id: "overview_problem", title: t("overview.problem"), summary: compactText(skeleton.problem?.summary || (state.lang === "en" ? "The core problem this paper addresses" : "论文要解决的核心问题"), 54), module: "structure", anchors: skeleton.problem?.anchors || [] },
    { id: "overview_core", title: t("overview.coreIdea"), summary: compactText(skeleton.core_idea?.summary || (state.lang === "en" ? "The key idea proposed by the paper" : "本文提出的关键想法"), 54), module: "structure", anchors: skeleton.core_idea?.anchors || [] },
    { id: "overview_method", title: t("overview.methodStructure"), summary: compactText(skeleton.method?.summary || (state.lang === "en" ? "Model, training, or inference flow" : "模型、训练或推理流程"), 54), module: "delta", anchors: skeleton.method?.anchors || [] },
    { id: "overview_training", title: t("overview.trainingInference"), summary: state.lang === "en" ? "Separate training-time, inference-time, and objectives" : "区分训练阶段、推理阶段与目标函数", module: "formula", anchors: skeleton.method?.anchors || [] },
    { id: "overview_experiments", title: t("overview.experiments"), summary: compactText(skeleton.experiments?.summary || (state.lang === "en" ? "Experimental design and evidence strength" : "实验设计与证据强度"), 54), module: "experiments", anchors: skeleton.experiments?.anchors || [] },
    { id: "overview_claims", title: t("overview.claims"), summary: compactText(claims[0]?.claim || (state.lang === "en" ? "Core claims and evidence chains" : "核心 claim 与证据链"), 54), module: "evidence", anchors: claims[0]?.anchors || [] }
  ].map((item) => ({ ...item, node: graphNodes.get(item.id) || makeSelection(item.id, item.title, item.summary, item.anchors) }));
}

function moduleCards() {
  const moduleMap = new Map(getModules().map(([id, name, title, desc]) => [id, { name, title, desc }]));
  const graphCount = state.ir?.method_graph?.nodes?.length || 0;
  const formulaCount = state.ir?.formula_ir?.formulas?.length || 0;
  const claimCount = state.ir?.claim_evidence_map?.claims?.length || 0;
  const deltaCount = state.ir?.method_delta?.deltas?.length || 0;
  const expCount = state.ir?.experiment_matrix?.experiments?.length || 0;
  const reproCount = state.ir?.reproduction_roadmap?.reproduction?.steps?.length || 0;
  return [
    ["structure", graphCount],
    ["formula", formulaCount],
    ["evidence", claimCount],
    ["delta", deltaCount],
    ["experiments", expCount],
    ["reproduction", reproCount]
  ].map(([module, count]) => ({ module, count, ...moduleMap.get(module) }));
}

function bindOverviewActions(chain) {
  document.querySelectorAll(".chain-node").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = chain.find((entry) => entry.id === btn.dataset.chain);
      const node = item?.node;
      const selection = node ? normalizeSelection("node", node.id, node.raw || node, node.title, node.summary, node.anchors) : null;
      enterDetail(item?.module || "structure", selection);
    });
  });
  document.querySelectorAll(".module-entry").forEach((btn) => {
    btn.addEventListener("click", () => enterDetail(btn.dataset.module));
  });
  document.querySelectorAll(".path-card").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (btn.dataset.path === "delta") enterDetail("delta");
      else if (btn.dataset.path === "formula") enterDetail("formula");
      else {
        const item = chain[0];
        const node = item.node;
        const selection = node ? normalizeSelection("node", node.id, node.raw || node, node.title, node.summary, node.anchors) : null;
        enterDetail("structure", selection);
      }
    });
  });
}

function renderStructure() {
  const graph = state.ir.method_graph || { nodes: [], edges: [] };
  const nodes = (graph.nodes || []).map(normalizeGraphNode);
  const edges = graph.edges || [];
  $("workspace").innerHTML = renderKnowledgeGraph(nodes, edges, "structure");
  bindGraphNodes(nodes);
}

function renderKnowledgeGraph(nodes, edges, mode) {
  if (!nodes.length) return `<div class="empty-state"><strong>${state.lang === "en" ? "No graph available" : "没有结构图"}</strong><span>${state.lang === "en" ? "method_graph.nodes is missing in this Paper IR." : "Paper IR 中缺少 method_graph.nodes。"}</span></div>`;
  const layout = layoutGraph(nodes, mode);
  const width = Math.max(1040, Math.max(...layout.map((n) => n.x)) + 300);
  const height = Math.max(760, Math.max(...layout.map((n) => n.y)) + 150);
  const edgeLines = edges
    .map((edge) => {
      const from = layout.find((node) => node.id === edge.from);
      const to = layout.find((node) => node.id === edge.to);
      if (!from || !to) return "";
      const start = anchorPoint(from, to);
      const end = anchorPoint(to, from);
      const midY = (start.y + end.y) / 2;
      const path = `M ${start.x} ${start.y} C ${start.x} ${midY}, ${end.x} ${midY}, ${end.x} ${end.y}`;
      return `<path class="graph-edge" d="${path}" data-from="${escapeHtml(edge.from)}" data-to="${escapeHtml(edge.to)}"></path>`;
    })
    .join("");
  const nodeCards = layout
    .map((node) => {
      const active = state.selected?.id === node.id ? "selected" : "";
      const tone = node.type || "module";
      return `<article class="graph-node ${active}" data-id="${escapeHtml(node.id)}" data-type="${escapeHtml(tone)}" style="left:${node.x}px;top:${node.y}px">
        <div class="node-kicker">${escapeHtml(node.typeLabel)}</div>
        <h3>${escapeHtml(node.title)}</h3>
        <p>${escapeHtml(node.summary)}</p>
        <div class="node-foot">
          <span>${(node.anchors || []).length} anchors</span>
          <span>${escapeHtml(node.type || "node")}</span>
        </div>
      </article>`;
    })
    .join("");
  return `<div id="graph-export-root" class="graph-stage" style="min-width:${width}px;min-height:${height}px">
    <svg id="graph-svg" class="edge-layer" viewBox="0 0 ${width} ${height}" aria-hidden="true">
      <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z"></path></marker></defs>
      ${edgeLines}
    </svg>
    ${nodeCards}
  </div>`;
}

function layoutGraph(nodes, mode) {
  const known = {
    kg_problem: [395, 40],
    kg_core: [395, 160],
    kg_encoder: [95, 305],
    kg_self_attention: [395, 305],
    kg_positional: [695, 305],
    kg_multi_head: [395, 450],
    kg_decoder: [695, 450],
    kg_training: [395, 585],
    kg_experiments: [95, 585],
    kg_claims: [695, 585]
  };
  if (mode === "structure" && nodes.some((node) => known[node.id])) {
    return nodes.map((node, index) => {
      const [x, y] = known[node.id] || [120 + (index % 3) * 300, 80 + Math.floor(index / 3) * 145];
      return { ...node, x, y, w: 250, h: 112 };
    });
  }
  return nodes.map((node, index) => ({
    ...node,
    x: 80 + (index % 3) * 310,
    y: 70 + Math.floor(index / 3) * 150,
    w: 260,
    h: 112
  }));
}

function anchorPoint(from, to) {
  const fx = from.x + from.w / 2;
  const fy = from.y + from.h / 2;
  const tx = to.x + to.w / 2;
  const ty = to.y + to.h / 2;
  if (Math.abs(tx - fx) > Math.abs(ty - fy)) {
    return {
      x: tx > fx ? from.x + from.w : from.x,
      y: fy
    };
  }
  return {
    x: fx,
    y: ty > fy ? from.y + from.h : from.y
  };
}

function bindGraphNodes(nodes) {
  document.querySelectorAll(".graph-node").forEach((el) => {
    el.addEventListener("mouseenter", () => highlightEdges(el.dataset.id, true));
    el.addEventListener("mouseleave", () => highlightEdges(el.dataset.id, false));
    el.addEventListener("click", () => {
      const node = nodes.find((item) => item.id === el.dataset.id);
      state.selected = normalizeSelection("node", node.id, node.raw || node, node.title, node.summary, node.anchors);
      renderWorkspace();
      renderDetail();
      if (node.anchors?.[0]) goToAnchor(node.anchors[0], false);
    });
  });
}

function highlightEdges(nodeId, on) {
  document.querySelectorAll(".graph-edge").forEach((edge) => {
    if (edge.dataset.from === nodeId || edge.dataset.to === nodeId) edge.classList.toggle("hot", on);
  });
}

function normalizeGraphNode(raw) {
  return {
    id: raw.node_id || raw.id,
    title: raw.title || raw.label || raw.node_id || "节点",
    summary: raw.summary || raw.description || "",
    type: raw.type || "module",
    typeLabel: typeLabel(raw.type || "module"),
    anchors: raw.anchors || [],
    raw
  };
}

function typeLabel(type) {
  const labels = state.lang === "en"
    ? {
        input: "Input / Problem",
        module: "Module",
        process: "Mechanism",
        objective: "Objective",
        output: "Output / Claim",
        dataset: "Dataset",
        evaluation: "Evaluation"
      }
    : {
        input: "问题输入",
        module: "结构模块",
        process: "关键机制",
        objective: "训练推理",
        output: "论文结论",
        dataset: "数据集",
        evaluation: "实验评估"
      };
  return labels[type] || type;
}

function formulaLatex(formula) {
  const raw = formula?.latex || formula?.formula || formula?.equation || formula?.expression || "";
  return String(raw)
    .trim()
    .replace(/^```(?:latex|tex)?/i, "")
    .replace(/```$/i, "")
    .replace(/^\$\$/g, "")
    .replace(/\$\$$/g, "")
    .replace(/^\\\[/, "")
    .replace(/\\\]$/, "")
    .replace(/^\\\(/, "")
    .replace(/\\\)$/, "")
    .trim();
}

function variableSymbol(variable) {
  return variable?.symbol || variable?.name || variable?.variable || "unknown";
}

function variableMeaning(variable) {
  return variable?.meaning || variable?.description || variable?.name || "";
}

function renderMathBlock(formula, extraClass = "") {
  const latex = formulaLatex(formula);
  if (!latex) return `<div class="math-line empty-math">${state.lang === "en" ? "Formula unavailable" : "公式未提供"}</div>`;
  return `<div class="math-shell ${extraClass}">
    <div class="math-paper">
      <span class="math-delimiter" aria-hidden="true">ƒ</span>
      <div class="math-line">\\[${escapeHtml(latex)}\\]</div>
    </div>
  </div>`;
}

function typesetMath(root = document.body, attempt = 0) {
  window.requestAnimationFrame(() => {
    if (window.MathJax?.typesetPromise) {
      try {
        window.MathJax.typesetClear?.([root]);
        window.MathJax.typesetPromise([root]).catch(() => {});
      } catch {
        // Formula rendering is progressive enhancement; escaped TeX remains readable if MathJax fails.
      }
      return;
    }
    if (attempt < 25) window.setTimeout(() => typesetMath(root, attempt + 1), 160);
  });
}

function renderFormula() {
  const formulas = state.ir.formula_ir?.formulas || [];
  if (!formulas.length) {
    $("workspace").innerHTML = `<div class="empty-state"><strong>${state.lang === "en" ? "No formulas extracted" : "未抽取到公式"}</strong><span>${state.lang === "en" ? "This Paper IR has no formula_ir section." : "当前 Paper IR 中没有 formula_ir。"}</span></div>`;
    return;
  }
  $("workspace").innerHTML = `<div class="formula-board">${formulas
    .map((formula) => {
      const low = (formula.variables || []).filter((v) => v.confidence === "low").length;
      const variables = (formula.variables || []).map((v) => ({ ...v, symbol: variableSymbol(v), confidence: v.confidence || "unknown" }));
      const formulaTitle = formula.name || formula.title || formula.formula_id.replace("formula_", "");
      return `<article class="formula-card ${state.selected?.id === formula.formula_id ? "selected" : ""}" data-kind="formula" data-id="${escapeHtml(formula.formula_id)}">
        <div class="card-topline">
          <span>${escapeHtml(formula.role || "formula")}</span>
          ${low ? `<b>${state.lang === "en" ? `${low} low-confidence vars` : `${low} 个低置信变量`}</b>` : `<b>grounded</b>`}
        </div>
        <h3>${escapeHtml(formulaTitle)}</h3>
        ${renderMathBlock(formula)}
        <p>${escapeHtml(formula.intuition || formula.plain_language_summary || "")}</p>
        <div class="variable-row">${variables
          .map((v) => `<span class="var-pill ${v.confidence === "low" ? "warn" : ""}">${escapeHtml(v.symbol)} · ${escapeHtml(v.confidence)}</span>`)
          .join("")}</div>
      </article>`;
    })
    .join("")}</div>`;
  bindCards("formula", (id) => formulas.find((item) => item.formula_id === id));
  typesetMath($("workspace"));
}

function renderEvidence() {
  const claims = state.ir.claim_evidence_map?.claims || [];
  $("workspace").innerHTML = `<div class="claim-board">${claims
    .map((claim) => `<article class="claim-card ${state.selected?.id === claim.claim_id ? "selected" : ""}" data-kind="claim" data-id="${escapeHtml(claim.claim_id)}">
      <div class="claim-strength ${escapeHtml(claimSupport(claim))}">${escapeHtml(claimSupport(claim))}</div>
      <h3>${escapeHtml(claimText(claim))}</h3>
      <div class="meta-row">
        <span class="tag">${escapeHtml(claim.claim_type || claim.evidence_source_type || "claim")}</span>
        ${(claim.risk_flags || []).map((flag) => `<span class="tag warn">${escapeHtml(flag)}</span>`).join("")}
      </div>
      <div class="evidence-stack">${(claim.evidence || [])
        .map((ev) => `<div class="evidence-line"><span>${escapeHtml(ev.source_type || ev.evidence_source_type || "evidence")}</span><p>${escapeHtml(evidenceText(ev))}</p></div>`)
        .join("")}</div>
    </article>`)
    .join("")}</div>`;
  bindCards("claim", (id) => claims.find((item) => item.claim_id === id));
}

function renderDelta() {
  const delta = state.ir.method_delta || {};
  const deltas = delta.deltas || [];
  const items = [
    normalizeTimelineItem("baseline", "Baseline", delta.baseline_method?.name || "Baseline", delta.baseline_method?.description || "", delta.baseline_method?.anchors || [], delta.baseline_method),
    ...deltas.map((d) => normalizeTimelineItem(d.delta_id, d.change_type || "delta", d.component || "Delta", d.after || d.why_it_matters || "", d.anchors || [], d)),
    normalizeTimelineItem("new_method", "New Method", delta.new_method?.name || (state.lang === "en" ? "This Method" : "本文方法"), delta.new_method?.description || "", delta.new_method?.anchors || [], delta.new_method)
  ];
  $("workspace").innerHTML = `<div class="delta-flow">${items
    .map((item, index) => `<article class="delta-card ${state.selected?.id === item.id ? "selected" : ""}" data-kind="delta" data-id="${escapeHtml(item.id)}">
      <div class="delta-index">${index + 1}</div>
      <div>
        <div class="card-topline"><span>${escapeHtml(item.kicker)}</span><b>${item.anchors.length} anchors</b></div>
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(item.summary)}</p>
        ${item.raw?.before ? `<div class="before-after"><span>Before</span><p>${escapeHtml(item.raw.before)}</p><span>After</span><p>${escapeHtml(item.raw.after)}</p></div>` : ""}
      </div>
    </article>`)
    .join("")}</div>`;
  bindCards("delta", (id) => items.find((item) => item.id === id));
}

function normalizeTimelineItem(id, kicker, title, summary, anchors, raw) {
  return { id, kicker, title, summary, anchors, raw: raw || {}, label: title, description: summary };
}

function renderExperiments() {
  const experiments = state.ir.experiment_matrix?.experiments || [];
  if (!experiments.length) {
    $("workspace").innerHTML = `<div class="empty-state"><strong>${state.lang === "en" ? "No experiment matrix" : "未抽取到实验矩阵"}</strong><span>${state.lang === "en" ? "This Paper IR has no experiment_matrix section." : "当前 Paper IR 中没有 experiment_matrix。"}</span></div>`;
    return;
  }
  $("workspace").innerHTML = `<div class="experiment-grid">${experiments
    .map((exp) => `<article class="experiment-card ${state.selected?.id === exp.experiment_id ? "selected" : ""}" data-kind="experiment" data-id="${escapeHtml(exp.experiment_id)}">
      <div class="card-topline"><span>${escapeHtml(exp.type || "experiment")}</span><b>${escapeHtml(exp.evidence_strength || "unclear")}</b></div>
      <h3>${escapeHtml(exp.name || exp.experiment_id)}</h3>
      <p>${escapeHtml(exp.what_it_tries_to_prove || "")}</p>
      <dl>
        <dt>${state.lang === "en" ? "Datasets" : "数据集"}</dt><dd>${escapeHtml(list(exp.dataset))}</dd>
        <dt>${state.lang === "en" ? "Metrics" : "指标"}</dt><dd>${escapeHtml(list(exp.metrics))}</dd>
        <dt>Baseline</dt><dd>${escapeHtml(list(exp.baseline))}</dd>
      </dl>
    </article>`)
    .join("")}</div>`;
  bindCards("experiment", (id) => experiments.find((item) => item.experiment_id === id));
}

function renderReproduction() {
  const repro = state.ir.reproduction_roadmap?.reproduction || {};
  const steps = repro.steps || [];
  $("workspace").innerHTML = `<div class="repro-layout">
    <article class="repro-summary ${state.selected?.id === "summary" ? "selected" : ""}" data-kind="reproduction" data-id="summary">
      <div class="card-topline"><span>${state.lang === "en" ? "Reproduction Overview" : "复现概览"}</span><b>${escapeHtml(repro.difficulty || "unknown")}</b></div>
      <h3>${state.lang === "en" ? "From paper to replicated result table" : "从论文到复现实验表"}</h3>
      <dl>
        <dt>${state.lang === "en" ? "Datasets" : "数据集"}</dt><dd>${escapeHtml(list(repro.required_datasets))}</dd>
        <dt>${state.lang === "en" ? "Models" : "模型"}</dt><dd>${escapeHtml(list(repro.required_models))}</dd>
        <dt>${state.lang === "en" ? "Compute" : "算力"}</dt><dd>${escapeHtml(repro.required_compute || "unknown")}</dd>
        <dt>${state.lang === "en" ? "Code" : "代码"}</dt><dd>${escapeHtml(repro.code_available || "unknown")}</dd>
      </dl>
    </article>
    <div class="step-list">${steps
      .map((step, index) => `<article class="step-card ${state.selected?.id === String(index) ? "selected" : ""}" data-kind="repro-step" data-id="${index}">
        <span>${String(index + 1).padStart(2, "0")}</span>
        <div><h3>${escapeHtml(step.step || "")}</h3><p>${escapeHtml(step.description || "")}</p></div>
      </article>`)
      .join("")}</div>
    <div class="risk-list">${(repro.missing_details || [])
      .map((item, index) => `<article class="risk-card" data-kind="missing" data-id="${index}">
        <div class="card-topline"><span>missing detail</span><b>${state.lang === "en" ? "review" : "需要复核"}</b></div>
        <h3>${escapeHtml(item.detail || "")}</h3>
        <p>${escapeHtml(item.why_it_matters || "")}</p>
      </article>`)
      .join("")}</div>
  </div>`;
  document.querySelectorAll("[data-kind]").forEach((card) => {
    card.addEventListener("click", () => {
      const kind = card.dataset.kind;
      let raw = repro;
      let id = card.dataset.id;
      if (kind === "repro-step") raw = steps[Number(id)];
      if (kind === "missing") raw = (repro.missing_details || [])[Number(id)];
      state.selected = normalizeSelection(kind, id, raw);
      renderWorkspace();
      renderDetail();
      if (raw?.anchors?.[0]) goToAnchor(raw.anchors[0], false);
    });
  });
}

function bindCards(kind, finder) {
  document.querySelectorAll(`[data-kind="${kind}"]`).forEach((card) => {
    card.addEventListener("click", () => {
      const raw = finder(card.dataset.id);
      state.selected = normalizeSelection(kind, card.dataset.id, raw);
      renderWorkspace();
      renderDetail();
      if (state.selected.anchors?.[0]) goToAnchor(state.selected.anchors[0], false);
    });
  });
}

function normalizeSelection(kind, id, raw, forcedTitle, forcedDesc, forcedAnchors) {
  raw = raw || {};
  const label = forcedTitle || raw.title || raw.label || raw.name || raw.component || raw.formula_id || raw.claim || raw.experiment_id || raw.step || id;
  const description =
    forcedDesc ||
    raw.summary ||
    raw.description ||
    raw.intuition ||
    raw.result_summary ||
    raw.what_it_tries_to_prove ||
    raw.why_it_matters ||
    raw.plain_language_summary ||
    "";
  return {
    kind,
    id,
    label,
    description,
    anchors: forcedAnchors || raw.anchors || [],
    raw
  };
}

function renderDetail() {
  const panel = $("detail-panel");
  if (state.view === "overview") {
    renderOverviewGuide();
    $("correction-details").open = false;
    return;
  }
  if (!state.selected) {
    panel.innerHTML = `<div class="detail-empty">
      <div class="empty-mark">构</div>
      <h2>${escapeHtml(t("detail.chooseNodeTitle"))}</h2>
      <p>${escapeHtml(t("detail.chooseNodeText"))}</p>
    </div>`;
    $("correction-details").open = false;
    $("correction-title").value = "";
    $("correction-description").value = "";
    return;
  }
  const item = state.selected;
  $("correction-title").value = item.label || "";
  $("correction-description").value = item.description || "";
  const raw = item.raw || {};
  panel.innerHTML = `<div class="detail-content">
    <div class="detail-kicker">${escapeHtml(item.kind)} · ${escapeHtml(item.id)}</div>
    <h2>${escapeHtml(item.label || item.id)}</h2>
    ${renderFormulaDetail(raw)}
    <section class="detail-section">
      <h3>${escapeHtml(t("detail.interpretation"))}</h3>
      <p>${escapeHtml(item.description || "unknown")}</p>
    </section>
    ${renderRoleSection(raw)}
    ${renderVariableSection(raw)}
    ${renderEvidenceSection(raw)}
    ${renderRiskSection(raw)}
    <section class="detail-section">
      <h3>${escapeHtml(t("detail.evidence"))}</h3>
      <div class="anchor-list">${renderAnchorButtons(item.anchors)}</div>
    </section>
  </div>`;
  bindAnchorButtons();
  typesetMath(panel);
}

// ------------------------------
// Detail Panel
// ------------------------------

function renderOverviewGuide() {
  const formulaCount = state.ir?.formula_ir?.formulas?.length || 0;
  const claimCount = state.ir?.claim_evidence_map?.claims?.length || 0;
  const repro = state.ir?.reproduction_roadmap?.reproduction || {};
  $("detail-panel").innerHTML = `<div class="overview-guide">
    <div class="guide-card primary">
      <div class="context-eyebrow">${escapeHtml(t("guide.eyebrow"))}</div>
      <h2>${escapeHtml(t("guide.title"))}</h2>
      <p>${escapeHtml(t("guide.copy"))}</p>
    </div>
    <div class="guide-metrics">
      <div><span>${escapeHtml(t("guide.difficulty"))}</span><b>${escapeHtml(repro.difficulty || "medium")}</b></div>
      <div><span>${escapeHtml(t("guide.type"))}</span><b>${escapeHtml(state.ir?.metadata?.paper_type || (state.lang === "en" ? "Architecture paper" : "架构论文"))}</b></div>
      <div><span>${escapeHtml(t("guide.formulas"))}</span><b>${formulaCount}</b></div>
      <div><span>${escapeHtml(t("guide.claims"))}</span><b>${claimCount}</b></div>
    </div>
    <section class="guide-section">
      <h3>${escapeHtml(t("guide.entries"))}</h3>
      <button data-guide-module="structure" type="button">${escapeHtml(t("guide.fromCore"))}</button>
      <button data-guide-module="delta" type="button">${escapeHtml(t("guide.fromDelta"))}</button>
      <button data-guide-module="formula" type="button">${escapeHtml(t("guide.fromFormula"))}</button>
      <button data-guide-module="experiments" type="button">${escapeHtml(t("guide.fromExperiments"))}</button>
    </section>
    <section class="guide-section muted">
      <h3>${escapeHtml(t("guide.tips"))}</h3>
      <p>${escapeHtml(t("guide.tip1"))}</p>
      <p>${escapeHtml(t("guide.tip2"))}</p>
    </section>
  </div>`;
  document.querySelectorAll("[data-guide-module]").forEach((btn) => {
    btn.addEventListener("click", () => enterDetail(btn.dataset.guideModule));
  });
}

function renderFormulaDetail(raw) {
  if (!formulaLatex(raw)) return "";
  return `<section class="detail-section formula-detail-section">
    <h3>${state.lang === "en" ? "Rendered Formula" : "公式"}</h3>
    ${renderMathBlock(raw, "detail-math")}
  </section>`;
}

function renderRoleSection(raw) {
  const values = [];
  if (raw.type) values.push([state.lang === "en" ? "Type" : "类型", raw.type]);
  if (raw.role) values.push([state.lang === "en" ? "Formula Role" : "公式角色", raw.role]);
  if (raw.evidence_strength) values.push([state.lang === "en" ? "Evidence Strength" : "证据强度", raw.evidence_strength]);
  if (raw.overall_support) values.push([state.lang === "en" ? "Overall Support" : "整体支持", raw.overall_support]);
  if (!values.length) return "";
  return `<section class="detail-section"><h3>${escapeHtml(t("detail.role"))}</h3><div class="detail-facts">${values
    .map(([k, v]) => `<div><span>${escapeHtml(k)}</span><b>${escapeHtml(v)}</b></div>`)
    .join("")}</div></section>`;
}

function renderVariableSection(raw) {
  if (!raw.variables?.length) return "";
  return `<section class="detail-section"><h3>${escapeHtml(t("detail.variables"))}</h3><div class="variable-list">${raw.variables
    .map((v) => `<button class="variable-item" data-anchor="${escapeHtml((v.anchors || [])[0] || "")}" type="button">
      <strong>${escapeHtml(variableSymbol(v))}</strong>
      <span>${escapeHtml(variableMeaning(v))}</span>
      <em>${escapeHtml(v.confidence || "unknown")}</em>
    </button>`)
    .join("")}</div></section>`;
}

function renderEvidenceSection(raw) {
  if (!raw.evidence?.length) return "";
  return `<section class="detail-section"><h3>Claim Evidence</h3><div class="anchor-list">${raw.evidence
    .map((ev) => `<button class="anchor-card" data-anchor="${escapeHtml((ev.anchors || [])[0] || "")}" type="button">
      <span>${escapeHtml(ev.source_type || "evidence")} · ${escapeHtml(ev.supports_claim || "")}</span>
      <p>${escapeHtml(ev.summary || "")}</p>
    </button>`)
    .join("")}</div></section>`;
}

function renderRiskSection(raw) {
  const flags = [];
  if (raw.risk_flags?.length) flags.push(...raw.risk_flags);
  if (raw.missing_details?.length) flags.push(...raw.missing_details.map((item) => item.detail));
  if (!flags.length) return "";
  return `<section class="detail-section"><h3>${escapeHtml(t("detail.risks"))}</h3><div class="risk-tags">${flags.map((flag) => `<span>${escapeHtml(flag)}</span>`).join("")}</div></section>`;
}

function renderAnchorButtons(anchors) {
  if (!anchors || !anchors.length) return `<div class="panel-empty">${escapeHtml(t("detail.noSource"))}</div>`;
  return anchors
    .map((id) => {
      const anchor = state.anchorMap.get(id);
      if (!anchor) return `<button class="anchor-card missing" type="button">${escapeHtml(id)} · missing</button>`;
      return `<button class="anchor-card" data-anchor="${escapeHtml(id)}" type="button">
        <span>${escapeHtml(anchor.source_type)} · ${state.lang === "en" ? `Page ${anchor.page}` : `第 ${anchor.page} 页`} · ${escapeHtml(anchor.section || "Unknown")}</span>
        <p>${escapeHtml(anchor.text_span || "")}</p>
      </button>`;
    })
    .join("");
}

function bindAnchorButtons() {
  document.querySelectorAll("[data-anchor]").forEach((btn) => {
    btn.addEventListener("click", (event) => {
      const id = event.currentTarget.dataset.anchor;
      if (id) goToAnchor(id);
    });
  });
}

// ------------------------------
// Source Anchors
// ------------------------------

function goToAnchor(anchorId, focus = true) {
  const anchor = state.anchorMap.get(anchorId);
  if (!anchor) return;
  state.selectedAnchor = anchor;
  state.currentPage = anchor.page || 1;
  $("page-input").value = String(state.currentPage);
  renderSourceInspector();
  renderPdf();
  if (focus) document.querySelector(".source-pane")?.scrollIntoView({ block: "nearest" });
}

function renderSourceInspector() {
  const anchor = state.selectedAnchor;
  if (!anchor) {
    $("source-meta").textContent = t("source.noAnchor");
    $("source-text").textContent = t("source.noAnchorText");
    return;
  }
  $("source-meta").textContent = `${anchor.anchor_id} · ${state.lang === "en" ? `Page ${anchor.page}` : `第 ${anchor.page} 页`} · ${anchor.section || "Unknown"} · ${anchor.source_type}`;
  $("source-text").textContent = anchor.text_span || "";
}

function jumpPage(page) {
  state.currentPage = Math.max(1, page || 1);
  $("page-input").value = String(state.currentPage);
  renderPdf();
}

function renderPdf() {
  const frame = $("pdf-frame");
  const empty = $("demo-source-state");
  const hasPdf = state.paper && state.paper.file_path && !String(state.paper.status || "").includes("示例");
  if (hasPdf) {
    empty.classList.remove("show");
    frame.classList.add("show");
    frame.src = `/api/papers/${state.paper.id}/pdf#page=${state.currentPage}&zoom=${state.zoom}`;
    return;
  }
  frame.classList.remove("show");
  const anchor = state.selectedAnchor;
  empty.classList.add("show");
  empty.innerHTML = `<div class="demo-page">
    <div class="demo-page-meta">${anchor ? `${state.lang === "en" ? `Page ${anchor.page}` : `第 ${anchor.page} 页`} · ${escapeHtml(anchor.section || "Unknown")}` : escapeHtml(t("source.demoMode"))}</div>
    <h3>${anchor ? "Source Anchor" : escapeHtml(t("source.noPdf"))}</h3>
    <p>${anchor ? escapeHtml(anchor.text_span || "") : escapeHtml(t("source.demoText"))}</p>
  </div>`;
}

async function handleUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const data = new FormData();
  data.append("pdf", file);
  $("upload-progress").classList.add("show");
  $("upload-progress").value = 12;
  const response = await fetch("/api/papers", { method: "POST", body: data });
  $("upload-progress").value = 80;
  if (!response.ok) {
    alert(await response.text());
    $("upload-progress").value = 0;
    $("upload-progress").classList.remove("show");
    return;
  }
  const payload = await response.json();
  $("upload-progress").value = 100;
  await loadPapers();
  await selectPaper(payload.paper_id);
  setTimeout(() => {
    $("upload-progress").value = 0;
    $("upload-progress").classList.remove("show");
  }, 800);
}

async function reparseCurrent() {
  if (!state.paper || String(state.paper.status || "").includes("示例")) return;
  $("status-pill").textContent = t("status.parsing");
  await api(`/api/papers/${state.paper.id}/reparse`, { method: "POST" });
  await selectPaper(state.paper.id);
}

// ------------------------------
// Export
// ------------------------------

function exportFile(kind) {
  if (!state.paper) return;
  window.location.href = `/api/papers/${state.paper.id}/export/${kind}`;
}

// ------------------------------
// Corrections
// ------------------------------

async function saveCorrection(event) {
  event.preventDefault();
  if (!state.paper || !state.selected) return;
  const oldValue = { label: state.selected.label, description: state.selected.description };
  const newValue = {
    label: $("correction-title").value,
    description: $("correction-description").value
  };
  await api(`/api/papers/${state.paper.id}/corrections`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target_type: state.selected.kind,
      target_id: state.selected.id,
      old_value: JSON.stringify(oldValue),
      new_value: newValue
    })
  });
  state.selected.label = newValue.label;
  state.selected.description = newValue.description;
  renderDetail();
  $("status-pill").textContent = t("status.corrected");
}

async function markIncorrect() {
  if (!state.paper || !state.selected) return;
  await api(`/api/papers/${state.paper.id}/corrections`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target_type: state.selected.kind,
      target_id: state.selected.id,
      old_value: JSON.stringify(state.selected.raw || {}),
      new_value: { inaccurate: true, note: "用户标记这个解释不准确" }
    })
  });
  $("status-pill").textContent = t("status.marked");
}

function exportGraphPng() {
  const root = $("graph-export-root");
  if (!root) {
    alert(state.lang === "en" ? "The current module has no graph to export." : "当前模块没有可导出的图谱。");
    return;
  }
  const width = Math.max(root.scrollWidth, 1040);
  const height = Math.max(root.scrollHeight, 760);
  const edges = Array.from(root.querySelectorAll(".graph-edge"))
    .map((edge) => `<path d="${edge.getAttribute("d")}" fill="none" stroke="#8aa39d" stroke-width="2" marker-end="url(#arrow)"></path>`)
    .join("");
  const nodes = Array.from(root.querySelectorAll(".graph-node"))
    .map((node) => {
      const x = parseFloat(node.style.left || "0");
      const y = parseFloat(node.style.top || "0");
      const title = node.querySelector("h3")?.textContent || "";
      const desc = node.querySelector("p")?.textContent || "";
      const kicker = node.querySelector(".node-kicker")?.textContent || "";
      return `<g transform="translate(${x},${y})">
        <rect width="250" height="112" rx="12" fill="#ffffff" stroke="#b9ccc6" stroke-width="1.4"></rect>
        <text x="14" y="24" fill="#1f6b61" font-size="12" font-family="Microsoft YaHei, sans-serif">${escapeXml(truncate(kicker, 28))}</text>
        <text x="14" y="52" fill="#1f2937" font-size="17" font-weight="600" font-family="Microsoft YaHei, sans-serif">${escapeXml(truncate(title, 22))}</text>
        <text x="14" y="78" fill="#4a5854" font-size="12.5" font-family="Microsoft YaHei, sans-serif">${escapeXml(truncate(desc, 32))}</text>
        <text x="14" y="96" fill="#4a5854" font-size="12.5" font-family="Microsoft YaHei, sans-serif">${escapeXml(truncate(desc.slice(32), 32))}</text>
      </g>`;
    })
    .join("");
  const svgText = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
    <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#8aa39d"></path></marker></defs>
    <rect width="100%" height="100%" fill="#f7f8f5"></rect>
    ${edges}
    ${nodes}
  </svg>`;
  const blob = new Blob([svgText], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const image = new Image();
  image.onload = () => {
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#f7f8f5";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(image, 0, 0);
    URL.revokeObjectURL(url);
    const a = document.createElement("a");
    a.href = canvas.toDataURL("image/png");
    a.download = `${state.paper?.id || "zhiwei"}_${state.module}.png`;
    a.click();
  };
  image.src = url;
}

function claimText(claim) {
  return claim?.claim || claim?.claim_text || claim?.statement || claim?.summary || claim?.description || claim?.claim_id || "unknown claim";
}

function claimSupport(claim) {
  return claim?.overall_support || claim?.support_strength || claim?.supports_claim || claim?.support || "unknown";
}

function evidenceText(evidence) {
  return evidence?.summary || evidence?.description || evidence?.text || evidence?.result || evidence?.evidence || "";
}

function expTitle(exp) {
  return exp?.name || exp?.task || exp?.variation || exp?.title || exp?.experiment_id || "experiment";
}

function expText(exp) {
  return exp?.what_it_tries_to_prove || exp?.result_summary || exp?.result || exp?.findings || exp?.finding || exp?.comparison || exp?.description || "";
}

function firstFilled(...values) {
  return values.find((value) => {
    if (Array.isArray(value)) return value.length > 0;
    if (value && typeof value === "object") return Object.keys(value).length > 0;
    return value !== undefined && value !== null && String(value).trim() !== "";
  });
}

function renderExperiments() {
  const experiments = state.ir.experiment_matrix?.experiments || [];
  if (!experiments.length) {
    $("workspace").innerHTML = `<div class="empty-state"><strong>${state.lang === "en" ? "No experiment matrix" : "未抽取到实验矩阵"}</strong><span>${state.lang === "en" ? "This Paper IR has no experiment_matrix section." : "当前 Paper IR 中没有 experiment_matrix。"}</span></div>`;
    return;
  }
  $("workspace").innerHTML = `<div class="experiment-grid">${experiments
    .map((exp) => `<article class="experiment-card ${state.selected?.id === exp.experiment_id ? "selected" : ""}" data-kind="experiment" data-id="${escapeHtml(exp.experiment_id)}">
      <div class="card-topline"><span>${escapeHtml(exp.type || "experiment")}</span><b>${escapeHtml(exp.evidence_strength || exp.support_strength || exp.support || "unclear")}</b></div>
      <h3>${escapeHtml(expTitle(exp))}</h3>
      <p>${escapeHtml(expText(exp))}</p>
      <dl>
        <dt>${state.lang === "en" ? "Datasets" : "数据集"}</dt><dd>${escapeHtml(list(firstFilled(exp.dataset, exp.datasets, exp.task)))}</dd>
        <dt>${state.lang === "en" ? "Metrics" : "指标"}</dt><dd>${escapeHtml(list(firstFilled(exp.metrics, exp.metric)))}</dd>
        <dt>Baseline</dt><dd>${escapeHtml(list(firstFilled(exp.baseline, exp.baselines, exp.comparison)))}</dd>
      </dl>
    </article>`)
    .join("")}</div>`;
  bindCards("experiment", (id) => experiments.find((item) => item.experiment_id === id));
}

function renderReproduction() {
  const reproRoot = state.ir.reproduction_roadmap || {};
  const repro = reproRoot.reproduction || reproRoot;
  const steps = repro.steps || [];
  $("workspace").innerHTML = `<div class="repro-layout">
    <article class="repro-summary ${state.selected?.id === "summary" ? "selected" : ""}" data-kind="reproduction" data-id="summary">
      <div class="card-topline"><span>${state.lang === "en" ? "Reproduction Overview" : "复现概览"}</span><b>${escapeHtml(repro.difficulty || "unknown")}</b></div>
      <h3>${state.lang === "en" ? "From paper to replicated result table" : "从论文到复现实验表"}</h3>
      <dl>
        <dt>${state.lang === "en" ? "Datasets" : "数据集"}</dt><dd>${escapeHtml(list(repro.required_datasets))}</dd>
        <dt>${state.lang === "en" ? "Models" : "模型"}</dt><dd>${escapeHtml(list(repro.required_models))}</dd>
        <dt>${state.lang === "en" ? "Compute" : "算力"}</dt><dd>${escapeHtml(list(repro.required_compute))}</dd>
        <dt>${state.lang === "en" ? "Code" : "代码"}</dt><dd>${escapeHtml(list(repro.code_available))}</dd>
      </dl>
    </article>
    <div class="step-list">${steps
      .map((step, index) => {
        const title = step.step || step.step_id || `${state.lang === "en" ? "Step" : "步骤"} ${index + 1}`;
        const description = step.description || step.step_description || step.detail || step.summary || "";
        return `<article class="step-card ${state.selected?.id === String(index) ? "selected" : ""}" data-kind="repro-step" data-id="${index}">
          <span>${String(index + 1).padStart(2, "0")}</span>
          <div><h3>${escapeHtml(title)}</h3><p>${escapeHtml(description)}</p></div>
        </article>`;
      })
      .join("")}</div>
    <div class="risk-list">${(repro.missing_details || [])
      .map((item, index) => `<article class="risk-card" data-kind="missing" data-id="${index}">
        <div class="card-topline"><span>missing detail</span><b>${state.lang === "en" ? "review" : "需要复核"}</b></div>
        <h3>${escapeHtml(item.detail || item.name || "unknown")}</h3>
        <p>${escapeHtml(item.why_it_matters || item.description || "")}</p>
      </article>`)
      .join("")}</div>
  </div>`;
  document.querySelectorAll("[data-kind]").forEach((card) => {
    card.addEventListener("click", () => {
      const kind = card.dataset.kind;
      let raw = repro;
      const id = card.dataset.id;
      if (kind === "repro-step") raw = steps[Number(id)];
      if (kind === "missing") raw = (repro.missing_details || [])[Number(id)];
      state.selected = normalizeSelection(kind, id, raw);
      renderWorkspace();
      renderDetail();
      if (raw?.anchors?.[0]) goToAnchor(raw.anchors[0], false);
    });
  });
}

function displayValue(value) {
  if (value === undefined || value === null || value === "") return "";
  if (Array.isArray(value)) return value.map(displayValue).filter(Boolean).join(", ");
  if (typeof value === "object") {
    const primary = value.name || value.title || value.resource || value.status || value.step || value.step_id || value.metric || value.dataset;
    const secondary = value.specification || value.description || value.url;
    if (primary && secondary) return `${primary}: ${secondary}`;
    return primary || secondary || JSON.stringify(value);
  }
  return String(value);
}

function list(value) {
  const rendered = displayValue(value);
  return rendered || "unknown";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeXml(value) {
  return escapeHtml(value);
}

function truncate(value, limit) {
  const text = String(value ?? "").replace(/\s+/g, " ").trim();
  if (text.length <= limit) return text;
  return `${text.slice(0, limit - 1)}…`;
}
