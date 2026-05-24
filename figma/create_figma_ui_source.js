// Figma use_figma script for AI Multi-Agent Pipeline.
// Usage:
// 1. Create or open a Figma design file.
// 2. Run this file through the Figma `use_figma` MCP tool with that fileKey.
// 3. The script creates editable pages, design tokens, component samples, and key screen frames.
//
// This script intentionally creates editable Figma nodes instead of flattened screenshots.

const createdNodeIds = [];

const C = {
  bg: "#F4F7FB",
  surface: "#FFFFFF",
  surfaceSubtle: "#FBFDFF",
  text: "#1F2937",
  textStrong: "#0F172A",
  textMuted: "#64748B",
  border: "#E2E8F0",
  sidebar: "#172033",
  sidebarActive: "#22304A",
  brand: "#2DD4BF",
  primary: "#2563EB",
  primarySoft: "#DBEAFE",
  success: "#34A853",
  successSoft: "#E6F4EA",
  warning: "#FBBC04",
  warningSoft: "#FEF7E0",
  danger: "#EA4335",
  dangerSoft: "#FCE8E6",
  purple: "#A142F4",
  purpleSoft: "#F3E8FD"
};

const screens = [
  { name: "Dashboard / Platform Overview", route: "/", accent: C.primary },
  { name: "RunConsole / Execute Workflow", route: "/runs/new", accent: C.success },
  { name: "Workflow Editor / Drag CodeAgent", route: "/workflows/editor", accent: C.danger },
  { name: "RunHistory / Detail and Events", route: "/history", accent: C.purple },
  { name: "Replay / Workflow Playback", route: "/replay/:platformRunId", accent: C.purple },
  { name: "Reports / Markdown Center", route: "/reports", accent: C.warning },
  { name: "Agents / Registry", route: "/agents", accent: C.primary },
  { name: "Workflow Templates / Versioned Templates", route: "/workflows/templates", accent: C.success },
  { name: "Models / Provider Config", route: "/models", accent: C.primary },
  { name: "Plugins / Plugin Config", route: "/plugins", accent: C.success }
];

function rgb(hex) {
  const raw = hex.replace("#", "");
  return {
    r: parseInt(raw.slice(0, 2), 16) / 255,
    g: parseInt(raw.slice(2, 4), 16) / 255,
    b: parseInt(raw.slice(4, 6), 16) / 255
  };
}

function solid(hex) {
  return [{ type: "SOLID", color: rgb(hex) }];
}

async function loadFonts() {
  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
  await figma.loadFontAsync({ family: "Inter", style: "Bold" });
}

function track(node) {
  createdNodeIds.push(node.id);
  return node;
}

function rect(parent, name, x, y, w, h, fill, stroke = null, radius = 8) {
  const r = track(figma.createRectangle());
  r.name = name;
  r.x = x;
  r.y = y;
  r.resize(w, h);
  r.fills = solid(fill);
  r.cornerRadius = radius;
  if (stroke) {
    r.strokes = solid(stroke);
    r.strokeWeight = 1;
  } else {
    r.strokes = [];
  }
  parent.appendChild(r);
  return r;
}

function text(parent, name, x, y, w, h, value, size = 14, fill = C.text, bold = false) {
  const t = track(figma.createText());
  t.name = name;
  t.x = x;
  t.y = y;
  t.resize(w, h);
  t.fontName = { family: "Inter", style: bold ? "Bold" : "Regular" };
  t.characters = value;
  t.fontSize = size;
  t.fills = solid(fill);
  parent.appendChild(t);
  return t;
}

function frame(parent, name, x, y, w, h, fill = C.bg) {
  const f = track(figma.createFrame());
  f.name = name;
  f.x = x;
  f.y = y;
  f.resize(w, h);
  f.fills = solid(fill);
  f.clipsContent = false;
  parent.appendChild(f);
  return f;
}

function pill(parent, name, x, y, value, color, w = 120) {
  rect(parent, `${name}/bg`, x, y, w, 26, color, color, 13);
  text(parent, `${name}/label`, x + 10, y + 7, w - 20, 12, value, 9, "#FFFFFF", true);
}

function card(parent, name, x, y, w, h, title, body, accent = C.primary) {
  rect(parent, `${name}/card`, x, y, w, h, C.surface, C.border, 8);
  rect(parent, `${name}/accent`, x + 16, y + 16, 42, 6, accent, null, 3);
  text(parent, `${name}/title`, x + 16, y + 34, w - 32, 18, title, 14, C.textStrong, true);
  text(parent, `${name}/body`, x + 16, y + 60, w - 32, Math.max(12, h - 72), body, 11, C.textMuted);
}

function appShell(parent, screenName) {
  rect(parent, "AppShell/background", 0, 0, 1440, 900, C.bg, null, 0);
  rect(parent, "Sidebar", 0, 0, 248, 900, C.sidebar, null, 0);
  rect(parent, "BrandMark", 18, 20, 40, 40, C.brand, null, 8);
  text(parent, "BrandMark/Text", 30, 32, 18, 16, "AI", 13, C.textStrong, true);
  text(parent, "BrandTitle", 70, 24, 140, 18, "Agent Pipeline", 16, "#FFFFFF", true);
  text(parent, "BrandSubtitle", 70, 48, 140, 14, "Vue3 Console", 12, "#94A3B8");
  const nav = ["Dashboard", "RunConsole", "RunHistory", "Reports", "Models", "Plugins", "Agents", "Workflows", "Workflow Editor"];
  nav.forEach((item, i) => {
    const y = 90 + i * 56;
    const active = screenName.includes(item) || (screenName.includes("Workflow") && item === "Workflow Editor");
    rect(parent, `Nav/${item}/bg`, 0, y, 248, 46, active ? C.sidebarActive : C.sidebar, null, 0);
    text(parent, `Nav/${item}/label`, 48, y + 15, 150, 14, item, 13, active ? "#FFFFFF" : "#CBD5E1", active);
  });
  rect(parent, "Topbar", 248, 0, 1192, 72, C.surface, C.border, 0);
  text(parent, "Topbar/Title", 270, 18, 360, 20, "Python Agent Engine Control Plane", 18, C.textStrong, true);
  text(parent, "Topbar/SubTitle", 270, 46, 340, 14, "FastAPI + Vue3 + TypeScript preview", 12, C.textMuted);
}

function workflowNodes(parent, x, y) {
  card(parent, "Workflow/Product", x, y, 150, 72, "Product", "requirement", C.primary);
  card(parent, "Workflow/CodeAgent", x + 210, y, 160, 72, "CodeAgent", "write_file", C.danger);
  card(parent, "Workflow/Replay", x + 105, y + 120, 160, 72, "Replay", "events", C.success);
  rect(parent, "Workflow/Line/ProductToCodeAgent", x + 150, y + 36, 60, 3, C.primary, null, 1);
  rect(parent, "Workflow/Line/CodeAgentToReplayA", x + 290, y + 72, 3, 84, C.danger, null, 1);
  rect(parent, "Workflow/Line/CodeAgentToReplayB", x + 185, y + 153, 108, 3, C.danger, null, 1);
}

function buildDashboard(page, x, y) {
  const root = frame(page, "Dashboard / Platform Overview", x, y, 1440, 900, C.bg);
  appShell(root, "Dashboard");
  text(root, "PageTitle", 290, 118, 540, 36, "AI Multi-Agent Pipeline", 30, C.textStrong, true);
  text(root, "PageSubtitle", 292, 160, 620, 18, "基于多智能体协作的自主开发流水线", 14, C.textMuted);
  ["历史运行总数", "成功运行数量", "失败运行数量", "平均质量评分", "最近一次运行状态", "最近一次报告"].forEach((label, i) => {
    card(root, `Metric/${label}`, 290 + i * 185, 224, 170, 92, i === 3 ? "68.0" : i === 0 ? "10" : i === 1 ? "6" : i === 2 ? "4" : i === 4 ? "最近成功" : "latest_report.md", label, i === 2 ? C.danger : C.success);
  });
  card(root, "RecentRuns", 290, 348, 680, 332, "最近运行记录", "run_20260521_135615\nDemo task: create a minimal Python script...\n质量 100 · deepseek · 修复 0", C.primary);
  card(root, "RecentReports", 990, 348, 380, 332, "最近报告", "latest_report.md\nrun_20260521_135615.md\nrun_20260521_135547.md", C.success);
}

function buildRunConsole(page, x, y) {
  const root = frame(page, "RunConsole / Execute Workflow", x, y, 1440, 900, C.bg);
  appShell(root, "RunConsole");
  text(root, "PageTitle", 290, 112, 500, 32, "RunConsole", 28, C.textStrong, true);
  card(root, "RequirementForm", 290, 172, 430, 440, "运行任务表单", "需求输入框\n模型选择\n插件选择\n最大修复次数\n演示模式开关\n开始运行按钮", C.primary);
  card(root, "CodeAgentPanel", 744, 172, 308, 440, "CodeAgentPanel", "read_file / write_file / list_files\n审计日志预览\n违规路径快捷测试\nbefore / after diff", C.danger);
  card(root, "LiveEvents", 1072, 172, 300, 440, "实时事件日志", "AGENT_STARTED\nWRITE_FILE\nAGENT_FINISHED\nREPORT_INDEXED", C.success);
}

function buildWorkflowEditor(page, x, y) {
  const root = frame(page, "Workflow Editor / Drag CodeAgent", x, y, 1440, 900, C.bg);
  appShell(root, "Workflow Editor");
  text(root, "PageTitle", 290, 112, 600, 32, "Workflow Editor", 28, C.textStrong, true);
  card(root, "AgentPalette", 290, 170, 250, 560, "Agent Palette", "Product Agent\nCodeAgent\nTester Agent\nReport Agent", C.success);
  rect(root, "Canvas/Grid", 570, 170, 520, 560, "#F8FAFC", C.border, 8);
  workflowNodes(root, 650, 330);
  card(root, "PropertiesPanel", 1120, 170, 260, 560, "Properties", "CodeAgent\noperation: write_file\nfilePath: output/demo.txt\nblocked: .env", C.primary);
}

function buildReplay(page, x, y) {
  const root = frame(page, "Replay / Workflow Playback", x, y, 1440, 900, C.bg);
  appShell(root, "Replay");
  text(root, "PageTitle", 290, 112, 600, 32, "Workflow Replay", 28, C.textStrong, true);
  card(root, "ReplaySummary", 290, 170, 1080, 96, "任务摘要", "platformRunId / pythonRunId / requirement / qualityScore / status", C.purple);
  card(root, "ReplayTimeline", 290, 300, 640, 430, "事件时间线", "WORKFLOW_STARTED\nAGENT_STARTED Product\nAGENT_STARTED CodeAgent\nAGENT_FINISHED CodeAgent\nREPORT_GENERATED", C.purple);
  card(root, "ReplayControls", 960, 300, 410, 180, "播放控制", "上一步 · 下一步 · 自动播放 · 暂停 · 重置", C.primary);
  card(root, "CurrentEvent", 960, 508, 410, 222, "当前事件", "CodeAgent write_file\n输出文件: output/demo.txt\n审计日志已记录", C.danger);
}

function buildGeneric(page, screen, x, y) {
  const root = frame(page, screen.name, x, y, 1440, 900, C.bg);
  appShell(root, screen.name);
  text(root, "PageTitle", 290, 112, 760, 32, screen.name, 28, C.textStrong, true);
  text(root, "Route", 292, 154, 500, 16, screen.route, 12, C.textMuted);
  card(root, "MainList", 290, 210, 520, 520, "列表 / 配置区", "搜索、筛选、表格或卡片列表", screen.accent);
  card(root, "DetailPanel", 840, 210, 530, 520, "详情 / 预览区", "详情、Markdown、模板预览、状态说明", screen.accent);
}

await loadFonts();

const existingPages = figma.root.children;
const sourcePage = figma.createPage();
sourcePage.name = "AI Pipeline UI Source";
await figma.setCurrentPageAsync(sourcePage);

const cover = frame(sourcePage, "00 Cover / Figma Editable UI Source", 0, 0, 1440, 900, C.bg);
text(cover, "CoverTitle", 90, 120, 780, 90, "AI Multi-Agent Pipeline\nFigma UI Source", 44, C.textStrong, true);
text(cover, "CoverSubtitle", 94, 250, 760, 28, "Vue3 + TypeScript 前端的个人可编辑 Figma 设计源", 20, C.primary, true);
card(cover, "SourceRules", 94, 360, 540, 210, "Figma-first rules", "UI 修改先更新 Figma Frame\nVue 实现与 Figma Frame 保持命名映射\nCodeAgent / Replay / Workflow Editor 保持可演示闭环", C.primary);
card(cover, "DesignScope", 680, 360, 560, 210, "Included screens", "Dashboard · RunConsole · Workflow Editor · RunHistory · Replay · Reports · Agents · Templates · Models · Plugins", C.success);

const ds = frame(sourcePage, "01 Design System / Tokens and Components", 1540, 0, 1440, 900, C.bg);
text(ds, "DSTitle", 90, 80, 760, 36, "Design System Tokens", 30, C.textStrong, true);
Object.entries(C).slice(0, 16).forEach(([name, value], i) => {
  const col = i % 4;
  const row = Math.floor(i / 4);
  rect(ds, `Color/${name}`, 90 + col * 260, 150 + row * 110, 220, 70, value, C.border, 8);
  text(ds, `Color/${name}/label`, 102 + col * 260, 232 + row * 110, 210, 18, `${name} ${value}`, 11, C.text);
});
card(ds, "Component/SummaryCard", 90, 650, 260, 120, "Summary Card", "success / failed / warning", C.success);
card(ds, "Component/EventCard", 390, 650, 260, 120, "Replay Event Card", "agent / status / message", C.purple);
card(ds, "Component/CodeAgentPanel", 690, 650, 300, 120, "CodeAgent Panel", "audit / diff / blocked path", C.danger);

buildDashboard(sourcePage, 0, 980);
buildRunConsole(sourcePage, 1540, 980);
buildWorkflowEditor(sourcePage, 3080, 980);
buildReplay(sourcePage, 4620, 980);

const genericStartX = 0;
const genericStartY = 1980;
screens
  .filter((s) => !["/", "/runs/new", "/workflows/editor", "/replay/:platformRunId"].includes(s.route))
  .forEach((screen, i) => {
    buildGeneric(sourcePage, screen, genericStartX + (i % 3) * 1540, genericStartY + Math.floor(i / 3) * 980);
  });

sourcePage.setRelaunchData({ open: "AI Multi-Agent Pipeline editable UI source" });

return {
  createdNodeIds,
  pageName: sourcePage.name,
  screenCount: screens.length,
  previousPageCount: existingPages.length,
  message: "Created editable Figma UI source frames for AI Multi-Agent Pipeline."
};
