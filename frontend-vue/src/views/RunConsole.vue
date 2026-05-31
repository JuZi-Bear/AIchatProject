<script setup lang="ts">
import { ElMessage } from "element-plus";
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";

import ArtifactPanel from "@/components/Workbench/ArtifactPanel.vue";
import CodeAgentToolDrawer from "@/components/Workbench/CodeAgentToolDrawer.vue";
import ComposerBar from "@/components/Workbench/ComposerBar.vue";
import TaskTimeline from "@/components/Workbench/TaskTimeline.vue";
import WorkspaceActionPanel from "@/components/Workbench/WorkspaceActionPanel.vue";
import WorkspaceProjectSidebar from "@/components/Workbench/WorkspaceProjectSidebar.vue";
import WorkbenchSidePanel from "@/components/Workbench/WorkbenchSidePanel.vue";
import WorkbenchSideRail from "@/components/Workbench/WorkbenchSideRail.vue";
import RequirementBuilder from "@/components/RunConsole/RequirementBuilder.vue";
import RunResultHighlight from "@/components/RunConsole/RunResultHighlight.vue";
import { currentApiMode, getApiModeLabel } from "@/api/client";
import { aiGenerateProject, executeCodeAgent } from "@/api/codeAgent";
import { getRunEvents } from "@/api/events";
import { subscribeRunEvents, type RunEventSubscription } from "@/api/eventStream";
import { getModels } from "@/api/models";
import { getPlugins } from "@/api/plugins";
import { postRun } from "@/api/runs";
import { createWorkspace, getWorkspaces, updateWorkspace } from "@/api/workspaces";
import {
  executePlatformDynamicLangGraphTemplate,
  executePlatformWorkflowTemplate,
  getPlatformWorkflowTemplates,
  getWorkflowTemplates,
} from "@/api/workflows";
import { useSettingsStore } from "@/stores/settings";
import type { CodeAgentFolderChange, CodeAgentFolderTemplate, CodeAgentOperation, CodeAgentResponse } from "@/types/codeAgent";
import type { DemoCase, DemoCaseKey } from "@/types/demo";
import type { FolderWorkflowContext, FolderWorkflowRunMode, WorkbenchSidePanelName, WorkspaceAction, WorkspaceExtendedSettings } from "@/types/interaction";
import type { ModelConfig } from "@/types/model";
import type { PluginConfig } from "@/types/plugin";
import type { RunRequest, RunResponse } from "@/types/run";
import type { RunEvent } from "@/types/runEvent";
import { createDefaultWorkspace, type WorkspaceConfig, type WorkspaceSafetyStatus } from "@/types/workspace";
import type { WorkflowTemplate } from "@/types/workflow";
import type { WorkflowTemplateData } from "@/types/workflowEditor";

const demoCases: DemoCase[] = [
  {
    key: "simple_success",
    label: "简单成功案例",
    description: "适合快速展示从需求到测试通过的标准闭环。",
    requirement: "写一个函数 add_numbers(a, b)，返回两个数字之和，并对非数字输入抛出 ValueError。",
  },
  {
    key: "auto_repair",
    label: "翻车自动修复案例",
    description: "适合突出测试失败、错误分析和自动修复高光时刻。",
    requirement: "写一个函数 get_second_largest(nums)，返回列表中第二大的不同数字；需要处理重复数字、空列表和不足两个不同数字的情况。",
  },
  {
    key: "comprehensive",
    label: "综合案例",
    description: "适合展示多 Agent 协作、插件结果、质量评分和报告产出。",
    requirement: "实现 analyze_scores(scores)，返回最高分、最低分、平均分、及格率，并处理空列表、非数字输入和分数越界情况。",
  },
  {
    key: "custom",
    label: "自定义输入",
    description: "保留当前输入内容，用于现场临时命题。",
    requirement: "",
  },
];

const demoFolderPath = "output/code_agent_workspace";

const builtinFolderTemplates: CodeAgentFolderTemplate[] = [
  {
    key: "folder_scan",
    name: "文件夹扫描模板",
    description: "扫描受控工作区，输出文件树、跳过项和安全摘要。",
    source: "builtin",
    baseDir: demoFolderPath,
    includePatterns: "**/*.md, **/*.txt, **/*.py, **/*.ts, **/*.vue",
    excludePatterns: ".env, .git/**, node_modules/**, dist/**, target/**",
    outputFile: "code_agent_folder_inventory.md",
    content: "# CodeAgent folder inventory\n\n- Scan controlled workspace.\n- Highlight blocked paths and skipped files.\n",
    recursive: true,
    dryRun: true,
    backupBeforeWrite: true,
    recommendedOperation: "scan_folder",
  },
  {
    key: "folder_markdown_summary",
    name: "生成 Markdown 汇总",
    description: "把文件夹读取结果整合为一个 Markdown 结果文件。",
    source: "builtin",
    baseDir: demoFolderPath,
    includePatterns: "**/*.md, **/*.txt, **/*.py",
    excludePatterns: ".env, .git/**, node_modules/**, dist/**, target/**",
    outputFile: "code_agent_folder_summary.md",
    content: "# Folder Summary\n\n## What changed\n- Summarize the controlled workspace.\n\n## Next steps\n- Review diff before applying.\n",
    recursive: true,
    dryRun: true,
    backupBeforeWrite: true,
    recommendedOperation: "plan_folder_changes",
  },
  {
    key: "folder_dry_run_diff",
    name: "dry-run diff 预览",
    description: "只生成变更计划和 diff，不写入磁盘。",
    source: "builtin",
    baseDir: demoFolderPath,
    includePatterns: "**/*.md, **/*.txt",
    excludePatterns: ".env, .git/**, node_modules/**, dist/**, target/**",
    outputFile: "code_agent_dry_run_result.md",
    content: "# Dry-run result\n\nThis plan should be reviewed before any folder write.\n",
    recursive: true,
    dryRun: true,
    backupBeforeWrite: true,
    recommendedOperation: "plan_folder_changes",
  },
  {
    key: "folder_apply_with_backup",
    name: "应用到文件夹模板",
    description: "基于已生成计划应用变更，默认写入前备份。",
    source: "builtin",
    baseDir: demoFolderPath,
    includePatterns: "**/*.md, **/*.txt",
    excludePatterns: ".env, .git/**, node_modules/**, dist/**, target/**",
    outputFile: "code_agent_apply_result.md",
    content: "# Applied folder result\n\n- This file is applied after reviewing the generated plan.\n",
    recursive: true,
    dryRun: false,
    backupBeforeWrite: true,
    recommendedOperation: "apply_folder_changes",
  },
  {
    key: "folder_blocked_path_check",
    name: "阻断路径安全测试",
    description: "演示 .env / .git / node_modules 等敏感路径阻断。",
    source: "builtin",
    baseDir: ".",
    includePatterns: ".env, .git/**, node_modules/**",
    excludePatterns: "",
    outputFile: "blocked_path_result.md",
    content: "# Blocked path check\n\nThis template intentionally targets blocked paths for safety demonstration.\n",
    recursive: true,
    dryRun: true,
    backupBeforeWrite: true,
    recommendedOperation: "scan_folder",
  },
];

const settingsStore = useSettingsStore();
const apiModeLabel = getApiModeLabel();
const isJavaMode = currentApiMode === "java";
const runModeOptions: Array<{ label: string; value: FolderWorkflowRunMode }> = [
  { label: "CodeAgent AI 一键生成", value: "code_agent_ai_generate" },
  { label: "文件夹工作流", value: "folder_workflow" },
  { label: "普通 Agent", value: "agent_run" },
  { label: "Runtime Lite", value: "runtime_lite" },
  { label: "Dynamic LangGraph", value: "dynamic_langgraph" },
];
const models = ref<ModelConfig[]>([]);
const plugins = ref<PluginConfig[]>([]);
const workspaces = ref<WorkspaceConfig[]>([]);
const platformWorkflowTemplates = ref<WorkflowTemplateData[]>([]);
const workflowFolderTemplates = ref<CodeAgentFolderTemplate[]>([]);
const loadingOptions = ref(false);
const workspaceLoading = ref(false);
const templateLoading = ref(false);
const running = ref(false);
const result = ref<RunResponse | null>(null);
const codeAgentResult = ref<CodeAgentResponse | null>(null);
const errorDetail = ref("");
const lastRequirement = ref("");
const selectedDemoCaseKey = ref<DemoCaseKey>("auto_repair");
const runMode = ref<FolderWorkflowRunMode>("code_agent_ai_generate");
const selectedWorkspaceId = ref<number | null>(null);
const selectedFolderTemplateKey = ref("folder_scan");
const selectedPlatformTemplateKey = ref("");
const activeSidePanel = ref<WorkbenchSidePanelName | null>(null);
const liveEvents = ref<RunEvent[]>([]);
const liveEventError = ref("");
const liveEventStreaming = ref(false);
const liveEventConnected = ref(false);
let liveEventSubscription: RunEventSubscription | null = null;
const defaultWorkspacePolicy = createDefaultWorkspace();
const workspaceActionTemplateMap: Record<WorkspaceAction, string> = {
  scan: "folder_scan",
  markdown_summary: "folder_markdown_summary",
  dry_run_diff: "folder_dry_run_diff",
  apply: "folder_apply_with_backup",
  blocked_check: "folder_blocked_path_check",
};

const form = reactive<RunRequest>({
  requirement: "",
  model_provider: settingsStore.selectedModelProvider,
  enabled_plugins: [...settingsStore.enabledPlugins],
  max_retry_count: settingsStore.maxRetryCount,
  require_human_approval: settingsStore.requireHumanApproval,
  demo_mode: settingsStore.demoMode,
  offline_mode: settingsStore.offlineMode,
});

const folderForm = reactive({
  baseDir: demoFolderPath,
  includePatterns: "**/*.md, **/*.txt, **/*.py, **/*.ts, **/*.vue",
  excludePatterns: ".env, .git/**, node_modules/**, dist/**, target/**",
  outputFile: "code_agent_folder_result.md",
  content: `# CodeAgent folder result

- This file is generated from the controlled folder workspace mode.
- Review the diff before applying changes.
`,
  recursive: true,
  dryRun: true,
  backupBeforeWrite: true,
});

const selectedSummary = computed(() => result.value?.run_summary || null);
const resultPlatformRunId = computed(() => result.value?.platform_run_id || result.value?.platformRunId || "");
const selectedDemoCase = computed(
  () => demoCases.find((demoCase) => demoCase.key === selectedDemoCaseKey.value) || demoCases[0],
);
const activePluginCount = computed(() => form.enabled_plugins.length);
const folderTemplateOptions = computed(() => [...builtinFolderTemplates, ...workflowFolderTemplates.value]);
const enabledWorkspaces = computed(() => workspaces.value.filter((workspace) => workspace.enabled));
const selectedWorkspace = computed(
  () =>
    enabledWorkspaces.value.find((workspace) => workspace.id === selectedWorkspaceId.value) ||
    enabledWorkspaces.value.find((workspace) => workspace.isDefault) ||
    enabledWorkspaces.value[0],
);
const selectedFolderTemplate = computed(() =>
  folderTemplateOptions.value.find((template) => template.key === selectedFolderTemplateKey.value),
);
const selectedPlatformTemplate = computed(() =>
  platformWorkflowTemplates.value.find((template) => template.workflowTemplateKey === selectedPlatformTemplateKey.value),
);
const currentTemplateName = computed(() => {
  if (runMode.value === "runtime_lite" || runMode.value === "dynamic_langgraph") {
    return selectedPlatformTemplate.value?.name || selectedPlatformTemplateKey.value || "";
  }

  return selectedFolderTemplate.value?.name || selectedFolderTemplateKey.value || "";
});
const workspaceSafety = computed<WorkspaceSafetyStatus>(() => {
  if (currentApiMode !== "java") {
    return {
      mode: "python-direct",
      message: "Python Direct：由 Python CodeAgent 白名单做最终校验",
      type: "info",
    };
  }

  if (!enabledWorkspaces.value.length) {
    return {
      mode: "unavailable",
      message: "尚未配置 Workspace",
      type: "warning",
    };
  }

  const targetPath = normalizePath(folderForm.baseDir);
  const matched = enabledWorkspaces.value.find((workspace) => pathInsideRoot(targetPath, workspace.rootPath));

  if (!matched) {
    return {
      mode: "outside",
      message: "路径不在已配置 Workspace 内",
      type: "warning",
    };
  }

  return {
    mode: "configured",
    workspace: matched,
    message: `Workspace：${matched.name}`,
    type: "success",
  };
});
const folderContext = computed<FolderWorkflowContext>(() => ({
  runMode: runMode.value,
  workspaceId: selectedWorkspaceId.value,
  folderPath: folderForm.baseDir,
  folderTemplateKey: selectedFolderTemplateKey.value,
  platformTemplateKey: selectedPlatformTemplateKey.value,
  modelProvider: form.model_provider,
  outputFile: folderForm.outputFile,
  includePatterns: folderForm.includePatterns,
  excludePatterns: folderForm.excludePatterns,
  recursive: folderForm.recursive,
  dryRun: folderForm.dryRun,
  backupBeforeWrite: folderForm.backupBeforeWrite,
  safety: workspaceSafety.value,
}));
const artifactCount = computed(() => {
  const reportCount = selectedSummary.value?.report_path ? 1 : 0;
  const replayCount = resultPlatformRunId.value ? 1 : 0;
  const codeAgentCount =
    codeAgentResult.value?.results.reduce((total, item) => {
      return total + Number(Boolean(item.filePath)) + (item.changes?.length || 0) + Number(Boolean(item.auditPath));
    }, 0) || 0;

  return reportCount + replayCount + codeAgentCount;
});
const outputCount = computed(() => artifactCount.value + Number(Boolean(result.value || errorDetail.value)));
const sidePanelMeta = computed(() => {
  const meta: Record<WorkbenchSidePanelName, { title: string; subtitle: string }> = {
    settings: {
      title: "运行设置",
      subtitle: "模型、插件、演示模式和审批开关。",
    },
    workspace: {
      title: "Workspace 功能区",
      subtitle: "文件夹权限、扫描范围、Markdown 输出和快捷动作。",
    },
    builder: {
      title: "需求构造器",
      subtitle: "用结构化字段拼出自然语言任务。",
    },
    tools: {
      title: "CodeAgent 工具",
      subtitle: "高级模式：单文件、文件夹、AI 项目生成和审计预览。",
    },
    output: {
      title: "Output",
      subtitle: "文件、diff、审计日志、报告、Replay 和运行结果。",
    },
    events: {
      title: "运行事件",
      subtitle: "Java RunEvent / SSE 事件流。",
    },
  };

  return activeSidePanel.value ? meta[activeSidePanel.value] : { title: "", subtitle: "" };
});
const runStatusText = computed(() => {
  if (running.value) {
    return "running";
  }
  if (errorDetail.value) {
    return "failed";
  }
  if (codeAgentResult.value) {
    return codeAgentResult.value.success ? "success" : "failed";
  }
  if (result.value) {
    return selectedSummary.value?.success ? "success" : "completed";
  }
  return "ready";
});

function pluginValue(plugin: PluginConfig) {
  return plugin.display_name || plugin.name;
}

function toggleSidePanel(panel: WorkbenchSidePanelName) {
  activeSidePanel.value = activeSidePanel.value === panel ? null : panel;
}

function closeSidePanel() {
  activeSidePanel.value = null;
}

function eventTagType(event: RunEvent) {
  if (event.status === "FAILED" || event.eventType.includes("FAILED") || event.eventType === "ERROR_OCCURRED") {
    return "danger";
  }

  if (event.status === "SUCCESS" || event.eventType.includes("SUCCESS") || event.eventType === "REPORT_INDEXED") {
    return "success";
  }

  if (event.status === "RUNNING" || event.eventType.includes("STARTED")) {
    return "primary";
  }

  if (event.status === "WAITING_FOR_HUMAN" || event.eventType.includes("APPROVAL")) {
    return "warning";
  }

  return "info";
}

function nextPlatformRunId() {
  return `folder_workflow_${Date.now()}_${Math.random().toString(16).slice(2, 8)}`;
}

function splitPatternInput(value: string) {
  return value
    .replace(/;/g, ",")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function normalizePath(value: string) {
  return value.trim().replace(/\\/g, "/").replace(/\/+$/, "").toLowerCase();
}

function pathInsideRoot(targetPath: string, rootPath: string) {
  const normalizedRoot = normalizePath(rootPath);

  return targetPath === normalizedRoot || targetPath.startsWith(`${normalizedRoot}/`);
}

function workflowTemplateToFolderTemplate(
  template: (WorkflowTemplate | WorkflowTemplateData) & {
    agentSequence?: string[];
    agent_sequence?: string[];
    markdown?: string;
  },
): CodeAgentFolderTemplate | null {
  const agentSequence = "agent_sequence" in template ? template.agent_sequence || [] : template.agentSequence || [];
  const nodes = "nodes" in template ? template.nodes || [] : [];
  const hasCodeAgent = agentSequence.includes("code_agent") || nodes.some((node) => node.agentKey === "code_agent");

  if (!hasCodeAgent) {
    return null;
  }

  const firstConfig = (nodes.find((node) => node.agentKey === "code_agent")?.codeAgentConfig || {}) as Record<
    string,
    unknown
  >;
  const key = "workflowTemplateKey" in template ? template.workflowTemplateKey : template.key;
  const content = String(
    firstConfig.content ||
      ("markdown" in template ? template.markdown : "") ||
      `# ${template.name || key}\n\n${template.description || "Generated from Workflow Template."}\n`,
  );

  return {
    key: `workflow_${key}`,
    name: `Workflow · ${template.name || key}`,
    description: template.description || "从 Workflow Template 提取 CodeAgent 文件夹参数。",
    source: "workflowTemplateKey" in template ? "platform" : "api",
    baseDir: String(firstConfig.baseDir || firstConfig.target_path || demoFolderPath),
    includePatterns: String(firstConfig.includePatterns || "**/*.md, **/*.txt, **/*.py"),
    excludePatterns: String(firstConfig.excludePatterns || ".env, .git/**, node_modules/**, dist/**, target/**"),
    outputFile: String(firstConfig.outputFile || "code_agent_workflow_result.md"),
    content,
    recursive: firstConfig.recursive === false ? false : true,
    dryRun: firstConfig.dryRun === false ? false : true,
    backupBeforeWrite: firstConfig.backupBeforeWrite === false ? false : true,
    recommendedOperation: "plan_folder_changes",
  };
}

function handleWorkbenchKeydown(event: KeyboardEvent) {
  if (event.key === "Escape") {
    closeSidePanel();
  }
}

function normalizeError(error: unknown) {
  const possibleError = error as {
    message?: string;
    response?: {
      status?: number;
      data?: unknown;
    };
  };

  if (possibleError.response?.data) {
    const data = possibleError.response.data;

    if (typeof data === "string") {
      return data;
    }

    if (typeof data === "object" && data && "detail" in data) {
      return `HTTP ${possibleError.response.status || ""} ${String((data as { detail?: unknown }).detail)}`;
    }

    return JSON.stringify(data, null, 2);
  }

  return possibleError.message || "运行失败";
}

function isTerminalEvent(event: RunEvent) {
  return event.eventType === "RUN_SUCCESS" || event.eventType === "RUN_FAILED" || event.eventType === "RUN_CANCELLED";
}

function appendLiveEvent(event: RunEvent) {
  const existingIndex = liveEvents.value.findIndex((item) => item.id === event.id && item.id > 0);

  if (existingIndex >= 0) {
    liveEvents.value.splice(existingIndex, 1, event);
  } else {
    liveEvents.value.push(event);
  }

  liveEvents.value.sort((left, right) => (left.createdAt || "").localeCompare(right.createdAt || ""));
}

function closeLiveEventStream() {
  liveEventSubscription?.close();
  liveEventSubscription = null;
  liveEventStreaming.value = false;
  liveEventConnected.value = false;
}

async function loadLiveEventHistory(platformRunId: string) {
  if (!isJavaMode || !platformRunId) {
    return;
  }

  try {
    liveEvents.value = await getRunEvents(platformRunId);
  } catch (error) {
    liveEventError.value = error instanceof Error ? error.message : "加载历史事件失败";
  }
}

function startLiveEventStream(platformRunId: string) {
  if (!isJavaMode || !platformRunId) {
    return;
  }

  closeLiveEventStream();
  liveEventError.value = "";
  liveEventStreaming.value = true;

  liveEventSubscription = subscribeRunEvents(
    platformRunId,
    (event) => {
      appendLiveEvent(event);
      if (isTerminalEvent(event)) {
        closeLiveEventStream();
      }
    },
    (error) => {
      liveEventError.value = error.message;
      closeLiveEventStream();
      loadLiveEventHistory(platformRunId);
    },
    () => {
      liveEventConnected.value = true;
    },
  );

  if (!liveEventSubscription.supported) {
    liveEventStreaming.value = false;
    loadLiveEventHistory(platformRunId);
  }
}

function syncFormFromSettings() {
  form.model_provider = settingsStore.selectedModelProvider;
  form.enabled_plugins = [...settingsStore.enabledPlugins];
  form.max_retry_count = settingsStore.maxRetryCount;
  form.require_human_approval = settingsStore.requireHumanApproval;
  form.demo_mode = settingsStore.demoMode;
  form.offline_mode = settingsStore.offlineMode;
}

function applyDemoCase(caseKey = selectedDemoCaseKey.value) {
  const demoCase = demoCases.find((item) => item.key === caseKey);

  if (!demoCase || demoCase.key === "custom") {
    return;
  }

  form.demo_mode = true;
  form.requirement = demoCase.requirement;
  form.max_retry_count = demoCase.key === "simple_success" ? 1 : Math.max(form.max_retry_count, 3);
}

function handleDemoCaseChange(caseKey: DemoCaseKey) {
  selectedDemoCaseKey.value = caseKey;
  applyDemoCase(caseKey);
}

function handleRequirementTemplateApplied(payload: {
  key: string;
  useCodeAgent: boolean;
  codeAgentOperation: string;
}) {
  if (payload.useCodeAgent || payload.key.startsWith("code_agent")) {
    activeSidePanel.value = "tools";
  }
}

function handleCodeAgentExecuted(response: CodeAgentResponse) {
  codeAgentResult.value = response;
  response.events.forEach(appendLiveEvent);
  activeSidePanel.value = "output";
}

function startNewConversation() {
  form.requirement = "";
  result.value = null;
  codeAgentResult.value = null;
  liveEvents.value = [];
  errorDetail.value = "";
  lastRequirement.value = "";
  closeLiveEventStream();
}

function workspaceNameFromPath(rootPath: string) {
  const normalized = rootPath.replace(/\\/g, "/").replace(/\/+$/, "");
  const name = normalized.split("/").filter(Boolean).pop() || "Workspace";
  return name.replace(/[_-]+/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function applyWorkspace(workspace = selectedWorkspace.value, options: { silent?: boolean } = {}) {
  if (!workspace) {
    return;
  }

  selectedWorkspaceId.value = workspace.id || null;
  folderForm.baseDir = workspace.rootPath;
  folderForm.dryRun = workspace.dryRunDefault;
  folderForm.backupBeforeWrite = workspace.backupBeforeWrite;

  if (!options.silent) {
    ElMessage.success(`已选择文件夹：${workspace.name}`);
  }
}

function selectWorkspace(workspace: WorkspaceConfig) {
  applyWorkspace(workspace);
  activeSidePanel.value = "workspace";
}

async function createWorkspaceFromPath(rootPath: string) {
  const nextRootPath = rootPath.trim();
  if (!nextRootPath) {
    ElMessage.warning("请先输入文件夹路径");
    return;
  }

  folderForm.baseDir = nextRootPath;

  if (!isJavaMode) {
    activeSidePanel.value = "workspace";
    ElMessage.info("Python Direct 模式使用本地白名单，不创建 Java Workspace。");
    return;
  }

  const existing = workspaces.value.find((workspace) => normalizePath(workspace.rootPath) === normalizePath(nextRootPath));
  if (existing) {
    applyWorkspace(existing);
    activeSidePanel.value = "workspace";
    return;
  }

  workspaceLoading.value = true;
  try {
    const created = await createWorkspace({
      ...createDefaultWorkspace(),
      name: workspaceNameFromPath(nextRootPath),
      rootPath: nextRootPath,
      isDefault: !workspaces.value.some((workspace) => workspace.enabled),
    });
    workspaces.value = [...workspaces.value, created];
    applyWorkspace(created);
    activeSidePanel.value = "workspace";
    ElMessage.success(`已创建 Workspace：${created.name}`);
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "创建 Workspace 失败");
  } finally {
    workspaceLoading.value = false;
  }
}

function applyFolderTemplate(
  templateKey = selectedFolderTemplateKey.value,
  options: { silent?: boolean; preserveFolder?: boolean } = {},
) {
  const template = folderTemplateOptions.value.find((item) => item.key === templateKey);

  if (!template) {
    if (!options.silent) {
      ElMessage.warning("请选择文件夹工作流模板");
    }
    return;
  }

  selectedFolderTemplateKey.value = template.key;
  const currentBaseDir = folderForm.baseDir;
  folderForm.baseDir = options.preserveFolder
    ? currentBaseDir
    : template.baseDir === demoFolderPath && selectedWorkspace.value
      ? selectedWorkspace.value.rootPath
      : template.baseDir;
  folderForm.includePatterns = template.includePatterns;
  folderForm.excludePatterns = template.excludePatterns;
  folderForm.outputFile = template.outputFile;
  folderForm.content = template.content;
  folderForm.recursive = template.recursive;
  folderForm.dryRun = template.dryRun;
  folderForm.backupBeforeWrite = template.backupBeforeWrite;

  if (!options.silent) {
    ElMessage.success(`已应用模板：${template.name}`);
  }
}

async function saveWorkspaceSettings(settings: WorkspaceExtendedSettings & { rootPath: string }) {
  folderForm.baseDir = settings.rootPath;
  folderForm.includePatterns = settings.includePatterns;
  folderForm.excludePatterns = settings.excludePatterns;
  folderForm.outputFile = settings.outputFile;
  folderForm.dryRun = settings.dryRunDefault;
  folderForm.backupBeforeWrite = settings.backupBeforeWrite;

  if (!isJavaMode) {
    ElMessage.info("Python Direct 模式仅更新当前页面设置。");
    return;
  }

  workspaceLoading.value = true;
  try {
    const base = selectedWorkspace.value || {
      ...createDefaultWorkspace(),
      name: workspaceNameFromPath(settings.rootPath),
      rootPath: settings.rootPath,
      isDefault: !workspaces.value.some((workspace) => workspace.enabled),
    };
    const payload: WorkspaceConfig = {
      ...base,
      rootPath: settings.rootPath,
      maxFiles: settings.maxFiles,
      maxReadChars: settings.maxReadChars,
      dryRunDefault: settings.dryRunDefault,
      backupBeforeWrite: settings.backupBeforeWrite,
    };
    const saved = payload.id ? await updateWorkspace(payload.id, payload) : await createWorkspace(payload);
    const existingIndex = workspaces.value.findIndex((workspace) => workspace.id === saved.id);
    if (existingIndex >= 0) {
      workspaces.value.splice(existingIndex, 1, saved);
    } else {
      workspaces.value.push(saved);
    }
    applyWorkspace(saved, { silent: true });
    ElMessage.success("Workspace 设置已保存");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存 Workspace 失败");
  } finally {
    workspaceLoading.value = false;
  }
}

async function runWorkspaceAction(action: WorkspaceAction) {
  const templateKey = workspaceActionTemplateMap[action];
  selectedFolderTemplateKey.value = templateKey;
  applyFolderTemplate(templateKey, { silent: true, preserveFolder: action !== "blocked_check" });
  if (action === "markdown_summary") {
    folderForm.outputFile = folderForm.outputFile || "code_agent_folder_summary.md";
  }
  runMode.value = "folder_workflow";
  await submitFolderWorkflow();
}

async function loadWorkspaces() {
  if (!isJavaMode) {
    workspaces.value = [];
    return;
  }

  workspaceLoading.value = true;
  try {
    workspaces.value = await getWorkspaces();
    const defaultWorkspace = workspaces.value.find((workspace) => workspace.enabled && workspace.isDefault);
    if (defaultWorkspace) {
      applyWorkspace(defaultWorkspace, { silent: true });
    }
  } catch (error) {
    workspaces.value = [];
    ElMessage.warning(error instanceof Error ? error.message : "加载 Workspace 失败");
  } finally {
    workspaceLoading.value = false;
  }
}

async function loadWorkflowTemplates() {
  templateLoading.value = true;
  try {
    const [apiTemplates, platformTemplates] = await Promise.allSettled([
      getWorkflowTemplates(),
      getPlatformWorkflowTemplates(),
    ]);
    const nextFolderTemplates: CodeAgentFolderTemplate[] = [];

    if (apiTemplates.status === "fulfilled") {
      apiTemplates.value
        .map((template) => workflowTemplateToFolderTemplate(template))
        .filter((template): template is CodeAgentFolderTemplate => Boolean(template))
        .forEach((template) => nextFolderTemplates.push(template));
    }

    if (platformTemplates.status === "fulfilled") {
      platformWorkflowTemplates.value = platformTemplates.value;
      platformTemplates.value
        .map((template) => workflowTemplateToFolderTemplate(template))
        .filter((template): template is CodeAgentFolderTemplate => Boolean(template))
        .forEach((template) => nextFolderTemplates.push(template));

      if (!selectedPlatformTemplateKey.value && platformTemplates.value.length) {
        selectedPlatformTemplateKey.value = platformTemplates.value[0].workflowTemplateKey;
      }
    } else {
      platformWorkflowTemplates.value = [];
    }

    workflowFolderTemplates.value = nextFolderTemplates;
    if (!selectedFolderTemplateKey.value || !folderTemplateOptions.value.some((item) => item.key === selectedFolderTemplateKey.value)) {
      selectedFolderTemplateKey.value = folderTemplateOptions.value[0]?.key || "";
    }
    applyFolderTemplate(selectedFolderTemplateKey.value, { silent: true });
  } finally {
    templateLoading.value = false;
  }
}

async function loadOptions() {
  loadingOptions.value = true;

  try {
    await settingsStore.loadSettings();
    syncFormFromSettings();

    const [modelRows, pluginRows] = await Promise.all([getModels(), getPlugins()]);
    models.value = modelRows;
    plugins.value = pluginRows;

    settingsStore.hydratePluginDefaults(
      pluginRows.filter((plugin) => plugin.enabled).map((plugin) => pluginValue(plugin)),
    );

    const selectedModel = modelRows.find((model) => model.provider === settingsStore.selectedModelProvider);
    const firstEnabledModel = modelRows.find((model) => model.enabled) || modelRows[0];
    if (selectedModel || firstEnabledModel) {
      form.model_provider = (selectedModel || firstEnabledModel).provider;
    }

    form.enabled_plugins = settingsStore.enabledPlugins.length
      ? [...settingsStore.enabledPlugins]
      : pluginRows.filter((plugin) => plugin.enabled).map((plugin) => pluginValue(plugin));

    await Promise.all([loadWorkspaces(), loadWorkflowTemplates()]);
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "加载模型和插件失败");
  } finally {
    loadingOptions.value = false;
  }
}

function latestPlannedChanges(): CodeAgentFolderChange[] {
  const changes =
    codeAgentResult.value?.results.flatMap((item) =>
      (item.changes || []).map((change) => ({
        filePath: change.relativePath || change.filePath,
        content: change.after || change.content || "",
        action: change.action,
        reason: change.reason,
      })),
    ) || [];

  return changes;
}

async function submitAgentRun() {
  if (running.value) {
    return;
  }

  if (!form.requirement.trim()) {
    ElMessage.warning("请先输入需求");
    return;
  }

  running.value = true;
  result.value = null;
  errorDetail.value = "";
  liveEvents.value = [];
  liveEventError.value = "";
  closeLiveEventStream();
  lastRequirement.value = form.requirement.trim();

  try {
    settingsStore.setRunDefaults({
      demoMode: form.demo_mode,
      maxRetryCount: form.max_retry_count,
      requireHumanApproval: form.require_human_approval,
      offlineMode: form.offline_mode,
    });

    result.value = await postRun({
      ...form,
      requirement: form.requirement.trim(),
    });
    if (resultPlatformRunId.value) {
      startLiveEventStream(resultPlatformRunId.value);
    }
    activeSidePanel.value = "output";
    ElMessage.success("运行完成");
  } catch (error) {
    errorDetail.value = normalizeError(error);
    ElMessage.error(errorDetail.value);
  } finally {
    running.value = false;
  }
}

async function submitFolderWorkflow() {
  if (running.value) {
    return;
  }

  if (!folderForm.baseDir.trim()) {
    ElMessage.warning("请先选择或输入文件夹路径");
    return;
  }

  const template = selectedFolderTemplate.value;
  let operation: CodeAgentOperation = template?.recommendedOperation || "plan_folder_changes";
  let plannedChanges = operation === "apply_folder_changes" ? latestPlannedChanges() : undefined;

  if (operation === "apply_folder_changes" && !plannedChanges?.length) {
    operation = "plan_folder_changes";
    plannedChanges = undefined;
    ElMessage.info("尚未生成变更计划，已先切换为 dry-run 计划。");
  }

  running.value = true;
  result.value = null;
  codeAgentResult.value = null;
  errorDetail.value = "";
  liveEvents.value = [];
  liveEventError.value = "";
  lastRequirement.value = form.requirement.trim() || `${template?.name || "文件夹工作流"}：${folderForm.baseDir}`;
  const platformRunId = nextPlatformRunId();
  closeLiveEventStream();
  startLiveEventStream(platformRunId);

  try {
    const response = await executeCodeAgent({
      operation,
      filePath: folderForm.baseDir.trim(),
      includePatterns: splitPatternInput(folderForm.includePatterns),
      excludePatterns: splitPatternInput(folderForm.excludePatterns),
      outputFile: folderForm.outputFile.trim(),
      content:
        form.requirement.trim() || folderForm.content
          ? `${folderForm.content}\n\n## User task\n${form.requirement.trim()}`
          : folderForm.content,
      recursive: folderForm.recursive,
      dryRun: operation === "apply_folder_changes" ? false : folderForm.dryRun,
      backupBeforeWrite: folderForm.backupBeforeWrite,
      changes: plannedChanges,
      platformRunId,
    });

    codeAgentResult.value = response;
    response.events.forEach(appendLiveEvent);
    if (response.platformRunId || platformRunId) {
      await loadLiveEventHistory(response.platformRunId || platformRunId);
    }
    activeSidePanel.value = "output";
    if (response.success) {
      ElMessage.success(response.message || "文件夹工作流完成");
    } else {
      ElMessage.error(response.message || "文件夹工作流失败");
    }
  } catch (error) {
    errorDetail.value = normalizeError(error);
    ElMessage.error(errorDetail.value);
  } finally {
    running.value = false;
    closeLiveEventStream();
  }
}

async function submitAiProjectGeneration() {
  if (running.value) {
    return;
  }

  if (!form.requirement.trim()) {
    ElMessage.warning("请先输入你想生成或修改的项目目标");
    return;
  }

  if (!folderForm.baseDir.trim()) {
    ElMessage.warning("请先选择或输入 Workspace 文件夹");
    return;
  }

  running.value = true;
  result.value = null;
  codeAgentResult.value = null;
  errorDetail.value = "";
  liveEvents.value = [];
  liveEventError.value = "";
  lastRequirement.value = form.requirement.trim();
  closeLiveEventStream();

  try {
    const response = await aiGenerateProject({
      requirement: form.requirement.trim(),
      baseDir: folderForm.baseDir.trim(),
      modelProvider: form.model_provider || undefined,
    });

    codeAgentResult.value = response;
    response.events.forEach(appendLiveEvent);
    if (response.platformRunId) {
      await loadLiveEventHistory(response.platformRunId);
    }
    activeSidePanel.value = "output";
    if (response.success) {
      ElMessage.success(response.message || "AI 一键生成完成");
    } else {
      ElMessage.error(response.message || "AI 一键生成失败");
    }
  } catch (error) {
    errorDetail.value = normalizeError(error);
    ElMessage.error(errorDetail.value);
  } finally {
    running.value = false;
  }
}

async function submitPlatformWorkflow() {
  if (!isJavaMode) {
    ElMessage.warning("模板执行仅 Java Gateway 模式支持");
    return;
  }

  if (!selectedPlatformTemplateKey.value) {
    ElMessage.warning("请先选择平台工作流模板");
    return;
  }

  running.value = true;
  result.value = null;
  codeAgentResult.value = null;
  errorDetail.value = "";
  liveEvents.value = [];
  liveEventError.value = "";
  lastRequirement.value = form.requirement.trim() || selectedPlatformTemplate.value?.name || "平台工作流模板";
  closeLiveEventStream();

  const inputData = {
    requirement: form.requirement.trim(),
    folderPath: folderForm.baseDir,
    workspaceId: selectedWorkspaceId.value,
    folderTemplateKey: selectedFolderTemplateKey.value,
    modelProvider: form.model_provider,
    includePatterns: splitPatternInput(folderForm.includePatterns),
    excludePatterns: splitPatternInput(folderForm.excludePatterns),
    outputFile: folderForm.outputFile,
    dryRun: folderForm.dryRun,
    backupBeforeWrite: folderForm.backupBeforeWrite,
  };

  try {
    const response =
      runMode.value === "dynamic_langgraph"
        ? await executePlatformDynamicLangGraphTemplate(selectedPlatformTemplateKey.value, inputData)
        : await executePlatformWorkflowTemplate(selectedPlatformTemplateKey.value, inputData);

    result.value = response as unknown as RunResponse;
    if (resultPlatformRunId.value) {
      startLiveEventStream(resultPlatformRunId.value);
      await loadLiveEventHistory(resultPlatformRunId.value);
    }
    activeSidePanel.value = "output";
    ElMessage.success("平台工作流已执行");
  } catch (error) {
    errorDetail.value = normalizeError(error);
    ElMessage.error(errorDetail.value);
  } finally {
    running.value = false;
  }
}

async function submitRun() {
  if (runMode.value === "code_agent_ai_generate") {
    await submitAiProjectGeneration();
    return;
  }

  if (runMode.value === "agent_run") {
    await submitAgentRun();
    return;
  }

  if (runMode.value === "runtime_lite" || runMode.value === "dynamic_langgraph") {
    await submitPlatformWorkflow();
    return;
  }

  await submitFolderWorkflow();
}

async function startDemoRun() {
  form.demo_mode = true;
  runMode.value = "agent_run";
  applyDemoCase();

  if (selectedDemoCaseKey.value === "custom" && !form.requirement.trim()) {
    ElMessage.warning("自定义演示需要先输入需求");
    return;
  }

  await submitRun();
}

onMounted(async () => {
  window.addEventListener("keydown", handleWorkbenchKeydown);
  await loadOptions();

  if (form.demo_mode && !form.requirement.trim()) {
    applyDemoCase();
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleWorkbenchKeydown);
  closeLiveEventStream();
});

watch(
  () => [form.demo_mode, form.max_retry_count, form.require_human_approval, form.offline_mode],
  () => {
    settingsStore.setRunDefaults({
      demoMode: form.demo_mode,
      maxRetryCount: form.max_retry_count,
      requireHumanApproval: form.require_human_approval,
      offlineMode: form.offline_mode,
    });
  },
);
</script>

<template>
  <section class="codex-run-page">
    <main class="run-workbench">
      <WorkspaceProjectSidebar
        :workspaces="enabledWorkspaces"
        :selected-workspace-id="selectedWorkspaceId"
        :folder-path="folderForm.baseDir"
        :is-java-mode="isJavaMode"
        :loading="workspaceLoading"
        @new-chat="startNewConversation"
        @select-workspace="selectWorkspace"
        @create-workspace="createWorkspaceFromPath"
        @update-folder-path="folderForm.baseDir = $event"
        @open-workspace-panel="activeSidePanel = 'workspace'"
        @open-tools="activeSidePanel = 'tools'"
        @open-settings="activeSidePanel = 'settings'"
      />

      <WorkbenchSideRail
        :active-panel="activeSidePanel"
        :event-count="liveEvents.length"
        :output-count="outputCount"
        @toggle="toggleSidePanel"
      />

      <section class="session-column">
        <TaskTimeline
          :requirement="lastRequirement || form.requirement"
          :folder-context="folderContext"
          :template-name="currentTemplateName"
          :running="running"
          :error-detail="errorDetail"
          :response="result"
          :live-events="liveEvents"
          :code-agent-response="codeAgentResult"
        />

        <div class="composer-shell">
          <ComposerBar
            v-model="form.requirement"
            v-model:model-provider="form.model_provider"
            v-model:run-mode="runMode"
            v-model:workspace-id="selectedWorkspaceId"
            v-model:folder-path="folderForm.baseDir"
            v-model:folder-template-key="selectedFolderTemplateKey"
            v-model:platform-template-key="selectedPlatformTemplateKey"
            v-model:output-file="folderForm.outputFile"
            v-model:dry-run="folderForm.dryRun"
            v-model:backup-before-write="folderForm.backupBeforeWrite"
            :running="running"
            :demo-mode="form.demo_mode"
            :api-mode-label="apiModeLabel"
            :status-text="runStatusText"
            :models="models"
            :loading-options="loadingOptions"
            :active-plugin-count="activePluginCount"
            :workspaces="enabledWorkspaces"
            :workspace-loading="workspaceLoading"
            :workspace-safety="workspaceSafety"
            :folder-templates="folderTemplateOptions"
            :platform-templates="platformWorkflowTemplates"
            :template-loading="templateLoading"
            @submit="submitRun"
            @start-demo="startDemoRun"
            @open-builder="activeSidePanel = 'builder'"
            @open-tools="activeSidePanel = 'tools'"
            @open-output="activeSidePanel = 'output'"
            @open-workspace="activeSidePanel = 'workspace'"
            @workspace-change="applyWorkspace()"
            @template-change="applyFolderTemplate()"
          />
        </div>
      </section>

      <WorkbenchSidePanel
        :visible="Boolean(activeSidePanel)"
        :title="sidePanelMeta.title"
        :subtitle="sidePanelMeta.subtitle"
        @close="closeSidePanel"
      >
        <div v-if="activeSidePanel === 'workspace'" class="side-section">
          <WorkspaceActionPanel
            :workspace="selectedWorkspace"
            :folder-path="folderForm.baseDir"
            :include-patterns="folderForm.includePatterns"
            :exclude-patterns="folderForm.excludePatterns"
            :output-file="folderForm.outputFile"
            :max-files="selectedWorkspace?.maxFiles || defaultWorkspacePolicy.maxFiles"
            :max-read-chars="selectedWorkspace?.maxReadChars || defaultWorkspacePolicy.maxReadChars"
            :dry-run-default="folderForm.dryRun"
            :backup-before-write="folderForm.backupBeforeWrite"
            :safety="workspaceSafety"
            :loading="workspaceLoading || running"
            @update:folder-path="folderForm.baseDir = $event"
            @update:include-patterns="folderForm.includePatterns = $event"
            @update:exclude-patterns="folderForm.excludePatterns = $event"
            @update:output-file="folderForm.outputFile = $event"
            @save-workspace="saveWorkspaceSettings"
            @run-action="runWorkspaceAction"
          />
        </div>

        <div v-else-if="activeSidePanel === 'settings'" class="side-section settings-panel">
          <el-form label-position="top" :disabled="running">
            <el-form-item label="运行模式">
              <el-select v-model="runMode" class="full-width" placeholder="选择运行模式">
                <el-option v-for="option in runModeOptions" :key="option.value" :label="option.label" :value="option.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="工作流模板">
              <el-select
                v-if="runMode === 'runtime_lite' || runMode === 'dynamic_langgraph'"
                v-model="selectedPlatformTemplateKey"
                class="full-width"
                :loading="templateLoading"
                placeholder="选择平台模板"
              >
                <el-option
                  v-for="template in platformWorkflowTemplates"
                  :key="template.workflowTemplateKey"
                  :label="template.name"
                  :value="template.workflowTemplateKey"
                />
              </el-select>
              <el-select
                v-else
                v-model="selectedFolderTemplateKey"
                class="full-width"
                :loading="templateLoading"
                placeholder="选择文件夹模板"
                @change="applyFolderTemplate()"
              >
                <el-option
                  v-for="template in folderTemplateOptions"
                  :key="template.key"
                  :label="template.name"
                  :value="template.key"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="演示模式">
              <div class="setting-line">
                <el-switch v-model="form.demo_mode" active-text="启用 Demo" />
              </div>
            </el-form-item>
            <el-form-item v-if="form.demo_mode" label="演示案例">
              <el-select
                v-model="selectedDemoCaseKey"
                class="full-width"
                placeholder="选择演示案例"
                @change="handleDemoCaseChange"
              >
                <el-option
                  v-for="demoCase in demoCases"
                  :key="demoCase.key"
                  :label="demoCase.label"
                  :value="demoCase.key"
                />
              </el-select>
              <p class="side-help">{{ selectedDemoCase.description }}</p>
            </el-form-item>
            <el-form-item label="模型">
              <el-select v-model="form.model_provider" class="full-width" :loading="loadingOptions" placeholder="模型">
                <el-option
                  v-for="model in models"
                  :key="model.provider"
                  :label="`${model.name} / ${model.model}`"
                  :value="model.provider"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="插件">
              <el-select
                v-model="form.enabled_plugins"
                multiple
                collapse-tags
                collapse-tags-tooltip
                class="full-width"
                :loading="loadingOptions"
                placeholder="插件"
              >
                <el-option
                  v-for="plugin in plugins"
                  :key="plugin.name"
                  :label="plugin.display_name"
                  :value="pluginValue(plugin)"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="最大修复次数">
              <el-input-number v-model="form.max_retry_count" :min="0" :max="10" controls-position="right" />
            </el-form-item>
            <div class="settings-switches">
              <el-switch v-model="form.require_human_approval" active-text="人工审批" />
              <el-switch v-model="form.offline_mode" active-text="离线模式" />
            </div>
          </el-form>
        </div>

        <div v-else-if="activeSidePanel === 'builder'" class="side-section">
          <RequirementBuilder
            v-model="form.requirement"
            :disabled="running"
            @template-applied="handleRequirementTemplateApplied"
          />
        </div>

        <div v-else-if="activeSidePanel === 'tools'" class="side-section">
          <CodeAgentToolDrawer @executed="handleCodeAgentExecuted" />
        </div>

        <div v-else-if="activeSidePanel === 'events'" class="side-section events-panel">
          <div class="event-status-row">
            <el-tag :type="liveEventConnected ? 'success' : 'info'" effect="plain">
              {{ liveEventConnected ? "SSE 已连接" : "SSE 未连接" }}
            </el-tag>
            <el-tag v-if="liveEventStreaming" type="primary" effect="plain">streaming</el-tag>
            <el-tag effect="plain">{{ liveEvents.length }} events</el-tag>
          </div>
          <el-alert
            v-if="liveEventError"
            :title="liveEventError"
            type="warning"
            show-icon
            :closable="false"
          />
          <el-empty v-if="!liveEvents.length" description="暂无事件，运行后会显示 SSE / RunEvent" />
          <div v-else class="event-list">
            <article v-for="event in liveEvents" :key="event.id || `${event.eventType}-${event.createdAt}`" class="event-card">
              <div class="event-card-head">
                <el-tag :type="eventTagType(event)" effect="plain" size="small">
                  {{ event.eventText || event.eventType }}
                </el-tag>
                <span>{{ event.status || "UNKNOWN" }}</span>
              </div>
              <p>{{ event.message || event.detailJson || "无事件描述" }}</p>
              <small>{{ event.createdAt }}</small>
            </article>
          </div>
        </div>

        <div v-else-if="activeSidePanel === 'output'" class="side-section output-panel">
          <RunResultHighlight
            :response="result"
            :requirement="lastRequirement || form.requirement"
            :live-events="liveEvents"
            :is-java-mode="isJavaMode"
            :running="running"
            :error-detail="errorDetail"
          />
          <ArtifactPanel
            :run-response="result"
            :code-agent-response="codeAgentResult"
            :live-events="liveEvents"
            :is-java-mode="isJavaMode"
          />
        </div>
      </WorkbenchSidePanel>
    </main>
  </section>
</template>

<style scoped>
.codex-run-page {
  display: grid;
  height: 100%;
  min-height: 0;
  margin: 0;
  overflow: hidden;
  background: #0f1115;
  color: #f4f4f5;
}

.run-workbench {
  border: 0;
  border-radius: 0;
}

.run-workbench {
  position: relative;
  display: grid;
  grid-template-columns: 264px minmax(0, 1fr);
  height: 100%;
  min-height: 0;
  padding: 0 92px 0 0;
  overflow: hidden;
  background:
    radial-gradient(circle at 55% 0%, rgba(77, 163, 255, 0.08), transparent 34%),
    #0f1115;
}

.session-column {
  display: grid;
  grid-template-rows: minmax(0, 1fr) auto;
  gap: 0;
  width: min(960px, 100%);
  height: 100%;
  min-height: 0;
  margin: 0 auto;
  min-width: 0;
  padding: 18px 0 0;
}

.composer-shell {
  z-index: 18;
  align-self: end;
  padding: 10px 0 10px;
  background: linear-gradient(180deg, rgba(15, 17, 21, 0), #0f1115 22%, #0f1115 100%);
}

.session-column :deep(.task-timeline) {
  min-height: 0;
  overflow: auto;
  padding: 0 0 24px;
  scrollbar-color: #343741 transparent;
}

.session-column :deep(.task-timeline::-webkit-scrollbar) {
  width: 10px;
}

.session-column :deep(.task-timeline::-webkit-scrollbar-thumb) {
  border: 3px solid transparent;
  border-radius: 999px;
  background: #343741;
  background-clip: padding-box;
}

.side-section {
  min-width: 0;
}

.settings-panel :deep(.el-form-item) {
  margin-bottom: 14px;
}

.settings-panel :deep(.el-form-item__label) {
  color: #d4d4d8;
}

.settings-panel :deep(.el-input__wrapper),
.settings-panel :deep(.el-select__wrapper),
.settings-panel :deep(.el-input-number__decrease),
.settings-panel :deep(.el-input-number__increase) {
  border-color: #343741;
  background: #17191f;
  box-shadow: 0 0 0 1px #343741 inset;
}

.settings-panel :deep(.el-input__inner),
.settings-panel :deep(.el-select__placeholder),
.settings-panel :deep(.el-select__selected-item) {
  color: #f4f4f5;
}

.setting-line,
.settings-switches,
.event-status-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.settings-switches {
  display: grid;
  gap: 12px;
}

.side-help {
  margin: 8px 0 0;
  color: #a1a1aa;
  font-size: 12px;
  line-height: 1.45;
}

.events-panel {
  display: grid;
  gap: 12px;
}

.output-panel {
  display: grid;
  gap: 12px;
}

.event-list {
  display: grid;
  gap: 10px;
}

.event-card {
  display: grid;
  gap: 7px;
  padding: 12px;
  border: 1px solid #343741;
  border-radius: 14px;
  background: #17191f;
}

.event-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.event-card-head span,
.event-card small {
  color: #a1a1aa;
  font-size: 12px;
}

.event-card p {
  margin: 0;
  color: #d4d4d8;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

@media (max-width: 980px) {
  .codex-run-page {
    height: auto;
    min-height: 100vh;
    overflow: visible;
  }

  .run-workbench {
    grid-template-columns: 1fr;
    min-height: 100vh;
    padding: 14px 14px 0;
    overflow: visible;
  }

  .session-column {
    min-height: calc(100vh - 100px);
  }
}
</style>
