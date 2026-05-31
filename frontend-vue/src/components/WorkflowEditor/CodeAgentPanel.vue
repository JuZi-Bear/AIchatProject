<script setup lang="ts">
import { Refresh, VideoPlay } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";

import { executeCodeAgent, openCodeAgentFolder, getCodeAgentPreviewUrl, aiGenerateProject } from "@/api/codeAgent";
import { currentApiMode } from "@/api/client";
import { getModels } from "@/api/models";
import type { ModelConfig } from "@/types/model";
import { subscribeRunEvents, type RunEventSubscription } from "@/api/eventStream";
import { getRunEvents } from "@/api/events";
import { getWorkspaces } from "@/api/workspaces";
import { getPlatformWorkflowTemplates, getWorkflowTemplates } from "@/api/workflows";
import { useWorkflowEditorStore } from "@/components/WorkflowEditor/WorkflowEditorStore";
import type {
  CodeAgentFolderTemplate,
  CodeAgentFolderChange,
  CodeAgentOperation,
  CodeAgentResponse,
} from "@/types/codeAgent";
import type { RunEvent } from "@/types/runEvent";
import type { WorkspaceConfig, WorkspaceSafetyStatus } from "@/types/workspace";

const props = withDefaults(
  defineProps<{
    alwaysVisible?: boolean;
    embedded?: boolean;
  }>(),
  {
    alwaysVisible: false,
    embedded: false,
  },
);
const emit = defineEmits<{
  executed: [response: CodeAgentResponse];
  event: [event: RunEvent];
}>();

const store = useWorkflowEditorStore();
const selectedNode = computed(() => store.selectedNode);
const visible = computed(() => props.alwaysVisible || selectedNode.value?.agentKey === "code_agent");
const isEmbedded = computed(() => props.embedded);
const loading = ref(false);
const templateLoading = ref(false);
const workspaceLoading = ref(false);
const previewLoading = ref(false);
const auditLoading = ref(false);
const sseStatus = ref("");
const previewKey = ref(0);
const result = ref<CodeAgentResponse | null>(null);
const filePreview = ref<{ filePath: string; content: string; truncated?: boolean } | null>(null);
const auditPreview = ref<{ path: string; content: string; lines: string[]; truncated?: boolean } | null>(null);
const diffPreview = ref<{
  filePath: string;
  before: string;
  after: string;
  beforeMissing: boolean;
  beforeTruncated?: boolean;
  afterTruncated?: boolean;
  rows: Array<{ type: "added" | "removed" | "unchanged"; text: string; lineNo: number }>;
} | null>(null);
const events = ref<RunEvent[]>([]);
let subscription: RunEventSubscription | null = null;

const auditLogPath = "output/code_agent_audit.jsonl";
const blockedPathExample = ".env";
const demoWritePath = "output/code_agent_demo.txt";
const demoFolderPath = "output/code_agent_workspace";
const demoWriteContent = `# CodeAgent demo file

def my_func():
    return "created by CodeAgent"
`;

const mode = ref<"file" | "folder" | "ai_generate">("file");
const selectedFolderTemplateKey = ref("folder_scan");

const aiForm = reactive({
  requirement: "写一个炫酷的网页版计算器，包含 HTML, CSS 和 JS，带有矩阵雨背景粒子特效",
  baseDir: "output/code_agent_workspace",
  modelProvider: "",
});

const form = reactive({
  operation: "read_file" as CodeAgentOperation,
  filePath: "output/code_agent_demo.txt",
  content: "",
  recursive: false,
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

const workflowFolderTemplates = ref<CodeAgentFolderTemplate[]>([]);
const workspaces = ref<WorkspaceConfig[]>([]);
const selectedWorkspaceId = ref<number | null>(null);
const models = ref<ModelConfig[]>([]);

const operationOptions = [
  { label: "read_file", value: "read_file" },
  { label: "write_file", value: "write_file" },
  { label: "list_files", value: "list_files" },
] as const;

const resultFiles = computed(
  () =>
    result.value?.results.filter(
      (item) => item.filePath && item.operation !== "list_files" && !String(item.operation).includes("folder"),
    ) || [],
);
const folderResults = computed(
  () =>
    result.value?.results.filter(
      (item) =>
        String(item.operation).includes("folder") ||
        Boolean(item.fileTree?.length) ||
        Boolean(item.folderFiles?.length) ||
        Boolean(item.changes?.length) ||
        Boolean(item.blockedFiles?.length),
    ) || [],
);
const folderChanges = computed(() => folderResults.value.flatMap((item) => item.changes || []));
const folderBlockedFiles = computed(() => folderResults.value.flatMap((item) => item.blockedFiles || []));
const folderFileTree = computed(() => folderResults.value.flatMap((item) => item.fileTree || []));
const folderReadFiles = computed(() => folderResults.value.flatMap((item) => item.folderFiles || []));
const folderBackups = computed(() => folderResults.value.flatMap((item) => item.backups || []));
const folderTemplateOptions = computed(() => [...builtinFolderTemplates, ...workflowFolderTemplates.value]);
const enabledWorkspaces = computed(() => workspaces.value.filter((workspace) => workspace.enabled));
const selectedWorkspace = computed(
  () =>
    enabledWorkspaces.value.find((workspace) => workspace.id === selectedWorkspaceId.value) ||
    enabledWorkspaces.value.find((workspace) => workspace.isDefault) ||
    enabledWorkspaces.value[0],
);
const workspaceSafety = computed<WorkspaceSafetyStatus>(() => {
  if (currentApiMode !== "java") {
    return {
      mode: "python-direct",
      message: "Python Direct 模式使用 config/settings.yaml 中的 CodeAgent 白名单。",
      type: "info",
    };
  }

  if (!enabledWorkspaces.value.length) {
    return {
      mode: "unavailable",
      message: "尚未配置启用的 Workspace，请到 Workspace 页面新增受控工作区。",
      type: "warning",
    };
  }

  const targetPath = normalizePath(folderForm.baseDir);
  const matched = enabledWorkspaces.value.find((workspace) => pathInsideRoot(targetPath, workspace.rootPath));

  if (!matched) {
    return {
      mode: "outside",
      message: "当前路径不属于 Java 平台已配置 Workspace。Python CodeAgent 仍会进行最终白名单校验。",
      type: "warning",
    };
  }

  return {
    mode: "configured",
    workspace: matched,
    message: `当前路径位于受控工作区：${matched.name}`,
    type: "success",
  };
});
const hasViolation = computed(() => {
  const failureText = [
    result.value?.message,
    ...events.value.map((event) => `${event.eventText} ${event.message} ${event.status}`),
  ]
    .filter(Boolean)
    .join(" ");

  return Boolean(
    result.value &&
      (!result.value.success || /禁止|阻断|白名单|blocked|denied|FAILED/i.test(failureText)),
  );
});
const latestAuditPath = computed(
  () => result.value?.results.find((item) => item.auditPath)?.auditPath || auditLogPath,
);

function nextPlatformRunId() {
  return `code_agent_${Date.now()}_${Math.random().toString(16).slice(2, 8)}`;
}

function eventKey(event: RunEvent) {
  return `${event.eventType}-${event.createdAt}-${event.message}`;
}

function appendEvent(event: RunEvent) {
  const currentKeys = new Set(events.value.map(eventKey));

  if (!currentKeys.has(eventKey(event))) {
    events.value.push(event);
    emit("event", event);
  }
}

async function copyText(text: string, successMessage: string) {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }

    ElMessage.success(successMessage);
  } catch {
    ElMessage.error("复制失败，请手动选择内容复制");
  }
}

function fillDemoWrite() {
  mode.value = "file";
  form.operation = "write_file";
  form.filePath = demoWritePath;
  form.content = demoWriteContent;
  form.recursive = false;
}

function fillDemoFolder() {
  mode.value = "folder";
  folderForm.baseDir = demoFolderPath;
  folderForm.outputFile = "code_agent_folder_result.md";
  folderForm.content = `# CodeAgent folder result

Generated at ${new Date().toLocaleString()}.

## Summary
- Folder mode scans a controlled workspace.
- It previews file changes before writing.
- Applying writes an audit JSONL record.
`;
  folderForm.dryRun = true;
  folderForm.backupBeforeWrite = true;
}

function workflowTemplateToFolderTemplate(template: {
  workflowTemplateKey?: string;
  key?: string;
  name?: string;
  description?: string;
  markdown?: string;
  source?: string;
  nodes?: Array<{ agentKey?: string; codeAgentConfig?: Record<string, unknown> }>;
  agent_sequence?: string[];
  agentSequence?: string[];
}): CodeAgentFolderTemplate | null {
  const agentSequence = template.agent_sequence || template.agentSequence || [];
  const hasCodeAgent =
    agentSequence.includes("code_agent") ||
    (template.nodes || []).some((node) => node.agentKey === "code_agent");

  if (!hasCodeAgent) {
    return null;
  }

  const firstConfig = (template.nodes || []).find((node) => node.agentKey === "code_agent")?.codeAgentConfig || {};
  const key = template.workflowTemplateKey || template.key || `workflow_${Date.now()}`;
  const content = String(
    firstConfig.content ||
      template.markdown ||
      `# ${template.name || key}\n\n${template.description || "Generated from Workflow Template."}\n`,
  );

  return {
    key: `workflow_${key}`,
    name: `Workflow · ${template.name || key}`,
    description: template.description || "从 Workflow Template 提取 CodeAgent 文件夹参数。",
    source: template.source === "java-mysql" || template.workflowTemplateKey ? "platform" : "api",
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

async function loadFolderTemplates() {
  templateLoading.value = true;

  try {
    const [apiTemplates, platformTemplates] = await Promise.allSettled([
      getWorkflowTemplates(),
      getPlatformWorkflowTemplates(),
    ]);
    const nextTemplates: CodeAgentFolderTemplate[] = [];

    if (apiTemplates.status === "fulfilled") {
      apiTemplates.value
        .map((template) => workflowTemplateToFolderTemplate(template))
        .filter((template): template is CodeAgentFolderTemplate => Boolean(template))
        .forEach((template) => nextTemplates.push(template));
    }

    if (platformTemplates.status === "fulfilled") {
      platformTemplates.value
        .map((template) => workflowTemplateToFolderTemplate(template))
        .filter((template): template is CodeAgentFolderTemplate => Boolean(template))
        .forEach((template) => nextTemplates.push(template));
    }

    workflowFolderTemplates.value = nextTemplates;
  } catch {
    workflowFolderTemplates.value = [];
  } finally {
    templateLoading.value = false;
  }
}

function applyFolderTemplate(templateKey = selectedFolderTemplateKey.value) {
  const template = folderTemplateOptions.value.find((item) => item.key === templateKey);

  if (!template) {
    ElMessage.warning("请选择文件夹工作流模板");
    return;
  }

  mode.value = "folder";
  selectedFolderTemplateKey.value = template.key;
  folderForm.baseDir = template.baseDir;
  folderForm.includePatterns = template.includePatterns;
  folderForm.excludePatterns = template.excludePatterns;
  folderForm.outputFile = template.outputFile;
  folderForm.content = template.content;
  folderForm.recursive = template.recursive;
  folderForm.dryRun = template.dryRun;
  folderForm.backupBeforeWrite = template.backupBeforeWrite;
  ElMessage.success(`已应用模板：${template.name}`);
}

function runRecommendedFolderOperation() {
  const template = folderTemplateOptions.value.find((item) => item.key === selectedFolderTemplateKey.value);
  const operation = template?.recommendedOperation || "plan_folder_changes";

  if (operation === "scan_folder") {
    scanFolder();
  } else if (operation === "read_folder") {
    readFolder();
  } else if (operation === "apply_folder_changes") {
    applyFolderChanges();
  } else {
    planFolderChanges();
  }
}

async function runBlockedPathCheck() {
  mode.value = "file";
  form.operation = "read_file";
  form.filePath = blockedPathExample;
  form.content = "";
  form.recursive = false;
  await runCodeAgent();
}

function closeSubscription() {
  subscription?.close();
  subscription = null;
}

async function loadHistoryEvents(platformRunId?: string) {
  if (currentApiMode !== "java" || !platformRunId) {
    return;
  }

  try {
    const history = await getRunEvents(platformRunId);
    history.forEach(appendEvent);
  } catch {
    // History fallback is best-effort only.
  }
}

async function runCodeAgent() {
  loading.value = true;
  result.value = null;
  filePreview.value = null;
  auditPreview.value = null;
  diffPreview.value = null;
  events.value = [];
  sseStatus.value = "";
  closeSubscription();
  const platformRunId = nextPlatformRunId();
  const targetPath = form.filePath.trim();
  let beforeRead: Awaited<ReturnType<typeof readFileContentForDiff>> | null = null;

  if (currentApiMode === "java") {
    subscription = subscribeRunEvents(
      platformRunId,
      appendEvent,
      (error) => {
        sseStatus.value = error.message;
      },
      () => {
        sseStatus.value = "SSE 已连接";
      },
    );
  }

  try {
    if (form.operation === "write_file" && targetPath) {
      beforeRead = await readFileContentForDiff(targetPath);
    }

    const response = await executeCodeAgent({
      operation: form.operation,
      filePath: targetPath,
      content: form.content,
      recursive: form.recursive,
      platformRunId,
    });

    result.value = response;
    emit("executed", response);
    response.events.forEach(appendEvent);
    await loadHistoryEvents(response.platformRunId || platformRunId);

    if (form.operation === "write_file" && targetPath) {
      await buildDiffPreview(targetPath, beforeRead);
    }

    if (response.success) {
      ElMessage.success(response.message || "CodeAgent 操作完成");
    } else {
      ElMessage.error(response.message || "CodeAgent 操作失败");
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "CodeAgent 请求失败");
  } finally {
    loading.value = false;
    closeSubscription();
  }
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

  if (!targetPath || !normalizedRoot) {
    return false;
  }

  return targetPath === normalizedRoot || targetPath.startsWith(`${normalizedRoot}/`);
}

async function loadWorkspaces() {
  if (currentApiMode !== "java") {
    workspaces.value = [];
    return;
  }

  workspaceLoading.value = true;

  try {
    workspaces.value = await getWorkspaces();
    const defaultWorkspace =
      enabledWorkspaces.value.find((workspace) => workspace.isDefault) || enabledWorkspaces.value[0];

    if (defaultWorkspace) {
      selectedWorkspaceId.value = defaultWorkspace.id || null;

      if (!folderForm.baseDir || folderForm.baseDir === demoFolderPath) {
        applyWorkspace(defaultWorkspace, { silent: true });
      }
    }
  } catch {
    workspaces.value = [];
  } finally {
    workspaceLoading.value = false;
  }
}

function applyWorkspace(workspace = selectedWorkspace.value, options: { silent?: boolean } = {}) {
  if (!workspace) {
    return;
  }

  selectedWorkspaceId.value = workspace.id || null;
  folderForm.baseDir = workspace.rootPath;
  aiForm.baseDir = workspace.rootPath;
  folderForm.dryRun = workspace.dryRunDefault;
  folderForm.backupBeforeWrite = workspace.backupBeforeWrite;

  if (!options.silent) {
    ElMessage.success(`已切换到 Workspace：${workspace.name}`);
  }
}

function resetExecutionState() {
  result.value = null;
  filePreview.value = null;
  auditPreview.value = null;
  diffPreview.value = null;
  events.value = [];
  sseStatus.value = "";
  closeSubscription();
}

function latestPlannedChanges(): CodeAgentFolderChange[] {
  return folderChanges.value.map((change) => ({
    filePath: change.relativePath || change.filePath,
    content: change.after ?? change.content ?? "",
    action: change.action,
    reason: change.reason,
  }));
}

async function runFolderOperation(operation: CodeAgentOperation, options: { apply?: boolean } = {}) {
  loading.value = true;
  const plannedChanges = operation === "apply_folder_changes" && folderChanges.value.length ? latestPlannedChanges() : undefined;
  resetExecutionState();
  const platformRunId = nextPlatformRunId();

  if (currentApiMode === "java") {
    subscription = subscribeRunEvents(
      platformRunId,
      appendEvent,
      (error) => {
        sseStatus.value = error.message;
      },
      () => {
        sseStatus.value = "SSE 已连接";
      },
    );
  }

  try {
    const response = await executeCodeAgent({
      operation,
      filePath: folderForm.baseDir.trim(),
      includePatterns: splitPatternInput(folderForm.includePatterns),
      excludePatterns: splitPatternInput(folderForm.excludePatterns),
      outputFile: folderForm.outputFile.trim(),
      content: folderForm.content,
      recursive: folderForm.recursive,
      dryRun: operation === "apply_folder_changes" ? !options.apply : folderForm.dryRun,
      backupBeforeWrite: folderForm.backupBeforeWrite,
      changes: plannedChanges,
      platformRunId,
    });

    result.value = response;
    emit("executed", response);
    response.events.forEach(appendEvent);
    await loadHistoryEvents(response.platformRunId || platformRunId);

    if (response.success) {
      ElMessage.success(response.message || "CodeAgent 文件夹操作完成");
    } else {
      ElMessage.error(response.message || "CodeAgent 文件夹操作失败");
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "CodeAgent 文件夹请求失败");
  } finally {
    loading.value = false;
    closeSubscription();
  }
}

function scanFolder() {
  runFolderOperation("scan_folder");
}

function readFolder() {
  runFolderOperation("read_folder");
}

function planFolderChanges() {
  runFolderOperation("plan_folder_changes");
}

function applyFolderChanges() {
  if (!folderChanges.value.length) {
    ElMessage.warning("请先生成文件夹变更计划");
    return;
  }

  runFolderOperation("apply_folder_changes", { apply: true });
}

async function readFileContentForDiff(filePath: string) {
  try {
    const response = await executeCodeAgent({
      operation: "read_file",
      filePath,
      platformRunId: nextPlatformRunId(),
    });
    const readResult = response.results.find((item) => typeof item.content === "string");

    return {
      success: response.success && Boolean(readResult),
      content: readResult?.content || "",
      truncated: readResult?.truncated,
      missing: !response.success,
      message: response.message,
    };
  } catch (error) {
    return {
      success: false,
      content: "",
      truncated: false,
      missing: true,
      message: error instanceof Error ? error.message : "读取写入前内容失败",
    };
  }
}

async function buildDiffPreview(
  filePath: string,
  beforeRead: Awaited<ReturnType<typeof readFileContentForDiff>> | null,
) {
  const afterRead = await readFileContentForDiff(filePath);
  const before = beforeRead?.content || "";
  const after = afterRead.content || form.content || "";

  diffPreview.value = {
    filePath,
    before,
    after,
    beforeMissing: Boolean(beforeRead?.missing),
    beforeTruncated: beforeRead?.truncated,
    afterTruncated: afterRead.truncated,
    rows: buildLineDiff(before, after),
  };
}

function buildLineDiff(before: string, after: string) {
  const beforeLines = before.split(/\r?\n/);
  const afterLines = after.split(/\r?\n/);
  let prefix = 0;

  while (
    prefix < beforeLines.length &&
    prefix < afterLines.length &&
    beforeLines[prefix] === afterLines[prefix]
  ) {
    prefix += 1;
  }

  let beforeSuffix = beforeLines.length - 1;
  let afterSuffix = afterLines.length - 1;

  while (
    beforeSuffix >= prefix &&
    afterSuffix >= prefix &&
    beforeLines[beforeSuffix] === afterLines[afterSuffix]
  ) {
    beforeSuffix -= 1;
    afterSuffix -= 1;
  }

  const rows: Array<{ type: "added" | "removed" | "unchanged"; text: string; lineNo: number }> = [];

  beforeLines.slice(0, prefix).forEach((line, index) => {
    rows.push({ type: "unchanged", text: line, lineNo: index + 1 });
  });

  beforeLines.slice(prefix, beforeSuffix + 1).forEach((line, index) => {
    rows.push({ type: "removed", text: line, lineNo: prefix + index + 1 });
  });

  afterLines.slice(prefix, afterSuffix + 1).forEach((line, index) => {
    rows.push({ type: "added", text: line, lineNo: prefix + index + 1 });
  });

  beforeLines.slice(beforeSuffix + 1).forEach((line, index) => {
    rows.push({ type: "unchanged", text: line, lineNo: beforeSuffix + index + 2 });
  });

  return rows.length ? rows : [{ type: "unchanged" as const, text: "", lineNo: 1 }];
}

function formatDiffText() {
  if (!diffPreview.value) {
    return "";
  }

  const header = [
    `--- before/${diffPreview.value.filePath}`,
    `+++ after/${diffPreview.value.filePath}`,
  ];
  const body = diffPreview.value.rows.map((row) => {
    const marker = row.type === "added" ? "+" : row.type === "removed" ? "-" : " ";
    return `${marker}${row.text}`;
  });

  return [...header, ...body].join("\n");
}

function copyDiff() {
  copyText(formatDiffText(), "已复制 diff");
}

async function previewAuditLog() {
  auditLoading.value = true;

  try {
    const response = await executeCodeAgent({
      operation: "read_file",
      filePath: latestAuditPath.value,
      platformRunId: nextPlatformRunId(),
    });
    const readResult = response.results.find((item) => typeof item.content === "string");
    const content = readResult?.content || response.message || "";
    auditPreview.value = {
      path: latestAuditPath.value,
      content,
      lines: content.split(/\r?\n/).filter(Boolean).slice(-12),
      truncated: readResult?.truncated,
    };

    response.events.forEach(appendEvent);

    if (!response.success) {
      ElMessage.warning(response.message || "审计日志暂不可读");
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "读取审计日志失败");
  } finally {
    auditLoading.value = false;
  }
}

function copyAuditLog() {
  if (!auditPreview.value) {
    ElMessage.warning("请先预览审计日志");
    return;
  }

  copyText(auditPreview.value.content, "已复制审计日志");
}

async function previewFile(filePath: string) {
  previewLoading.value = true;
  const platformRunId = nextPlatformRunId();

  try {
    const response = await executeCodeAgent({
      operation: "read_file",
      filePath,
      platformRunId,
    });
    response.events.forEach(appendEvent);
    await loadHistoryEvents(response.platformRunId || platformRunId);

    const readResult = response.results.find((item) => typeof item.content === "string");
    filePreview.value = {
      filePath,
      content: readResult?.content || response.message || "",
      truncated: readResult?.truncated,
    };

    if (!response.success) {
      ElMessage.error(response.message || "文件预览失败");
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "文件预览失败");
  } finally {
    previewLoading.value = false;
  }
}

const htmlPreviewVisible = ref(false);
const htmlPreviewUrl = ref("");
const htmlPreviewTitle = ref("");

function previewHtmlFile(filePath: string) {
  htmlPreviewUrl.value = getCodeAgentPreviewUrl(filePath);
  htmlPreviewTitle.value = filePath;
  htmlPreviewVisible.value = true;
}

function openPreviewInNewWindow() {
  if (htmlPreviewUrl.value) {
    window.open(htmlPreviewUrl.value, "_blank");
  }
}

const openFolderLoading = ref(false);
async function openFolderByPath(path: string) {
  if (!path) {
    ElMessage.warning("文件夹路径为空");
    return;
  }
  openFolderLoading.value = true;
  try {
    const res = await openCodeAgentFolder(path);
    if (res.success) {
      ElMessage.success(res.message || "已打开文件夹");
    } else {
      ElMessage.error(res.message || "打开文件夹失败");
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "打开文件夹失败");
  } finally {
    openFolderLoading.value = false;
  }
}

function openWorkspaceFolder() {
  const path = folderForm.baseDir || "output/code_agent_workspace";
  openFolderByPath(path);
}

function openFileFolder() {
  let path = form.filePath || "output";
  openFolderByPath(path);
}

async function runAiGeneration() {
  if (!aiForm.requirement.trim()) {
    ElMessage.warning("请输入项目需求");
    return;
  }
  loading.value = true;
  resetExecutionState();
  const platformRunId = nextPlatformRunId();

  try {
    const response = await aiGenerateProject({
      requirement: aiForm.requirement.trim(),
      baseDir: aiForm.baseDir.trim(),
      modelProvider: aiForm.modelProvider || undefined,
    });

    result.value = response;
    emit("executed", response);
    if (response.events && response.events.length) {
      response.events.forEach(appendEvent);
    }

    if (response.success) {
      ElMessage.success(response.message || "AI 项目一键生成成功！");
    } else {
      ElMessage.error(response.message || "AI 项目生成失败");
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "AI 生成请求失败");
  } finally {
    loading.value = false;
  }
}

async function loadModels() {
  try {
    models.value = await getModels();
  } catch {
    models.value = [];
  }
}

onMounted(() => {
  loadFolderTemplates();
  loadWorkspaces();
  loadModels();
});

onBeforeUnmount(closeSubscription);
</script>

<template>
  <el-card
    v-if="visible"
    shadow="never"
    class="code-agent-card"
    :class="{ 'code-agent-card-embedded': isEmbedded }"
  >
    <template v-if="!isEmbedded" #header>
      <div class="panel-head">
        <span>CodeAgent 文件操作</span>
        <el-tag type="warning" effect="plain">简化执行模块</el-tag>
      </div>
    </template>

    <el-alert
      :title="
        isEmbedded
          ? '白名单文件操作：read / write / list / folder mode；Java 模式下进入 RunEvent + SSE。'
          : '仅支持白名单目录内 read_file / write_file / list_files / folder mode，不是完整 Codex。Java 模式下事件会进入 RunEvent + SSE。'
      "
      type="info"
      show-icon
      :closable="false"
      class="panel-alert"
    />

    <el-alert
      v-if="hasViolation"
      title="CodeAgent 操作被阻断或失败"
      description="请检查路径是否在白名单内，或是否命中了 .env、.git、node_modules、构建产物等阻断路径。"
      type="error"
      show-icon
      :closable="false"
      class="panel-alert"
    />

    <div class="quick-actions">
      <el-button size="small" plain @click="fillDemoWrite">填入 Demo 写文件</el-button>
      <el-button size="small" type="primary" plain @click="fillDemoFolder">填入文件夹模式 Demo</el-button>
      <el-button size="small" type="danger" plain :loading="loading" @click="runBlockedPathCheck">
        测试阻断路径 .env
      </el-button>
      <el-button size="small" plain :loading="auditLoading" @click="previewAuditLog">
        预览审计日志
      </el-button>
    </div>

    <el-radio-group v-model="mode" class="mode-switch">
      <el-radio-button label="file">单文件模式</el-radio-button>
      <el-radio-button label="folder">文件夹模式</el-radio-button>
      <el-radio-button label="ai_generate">AI 一键生成项目</el-radio-button>
    </el-radio-group>

    <el-form v-if="mode === 'file'" label-position="top" class="code-agent-form">
      <el-form-item label="操作">
        <el-select v-model="form.operation" class="full-width">
          <el-option
            v-for="option in operationOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item :label="form.operation === 'list_files' ? '目录路径' : '文件路径'">
        <el-input v-model="form.filePath" placeholder="src/moduleA.py" />
      </el-form-item>

      <el-form-item v-if="form.operation === 'write_file'" label="写入内容">
        <el-input v-model="form.content" type="textarea" :rows="7" placeholder="# 添加新函数 my_func" />
      </el-form-item>

      <el-form-item v-if="form.operation === 'list_files'" label="递归列出">
        <el-switch v-model="form.recursive" active-text="递归" inactive-text="仅当前目录" />
      </el-form-item>

      <el-button type="primary" :icon="VideoPlay" :loading="loading" class="full-width" @click="runCodeAgent">
        触发 CodeAgent 节点
      </el-button>
    </el-form>

    <el-form v-else-if="mode === 'folder'" label-position="top" class="code-agent-form">
      <div class="folder-mode-note">
        <strong>安全文件夹工作区</strong>
        <span>默认 dry-run 预览 diff，确认后再应用到目录。</span>
      </div>

      <div class="workspace-picker">
        <div class="workspace-copy">
          <strong>Project Workspace</strong>
          <span>平台层保存受控工作区，Python CodeAgent 仍执行最终路径安全校验。</span>
        </div>
        <div class="workspace-controls">
          <el-select
            v-model="selectedWorkspaceId"
            class="full-width"
            :loading="workspaceLoading"
            :disabled="currentApiMode !== 'java' || !enabledWorkspaces.length"
            placeholder="选择受控 Workspace"
            @change="() => applyWorkspace()"
          >
            <el-option
              v-for="workspace in enabledWorkspaces"
              :key="workspace.id || workspace.rootPath"
              :label="`${workspace.isDefault ? '默认 · ' : ''}${workspace.name}`"
              :value="workspace.id"
            >
              <div class="template-option">
                <strong>{{ workspace.name }}</strong>
                <span>{{ workspace.rootPath }}</span>
              </div>
            </el-option>
          </el-select>
          <el-button size="small" plain :disabled="!selectedWorkspace" @click="applyWorkspace()">
            使用工作区
          </el-button>
          <el-button size="small" type="primary" plain :loading="openFolderLoading" @click="openWorkspaceFolder">
            打开文件夹
          </el-button>
        </div>
        <el-alert
          :title="workspaceSafety.message"
          :type="workspaceSafety.type"
          show-icon
          :closable="false"
          class="workspace-alert"
        />
        <div v-if="workspaceSafety.workspace" class="workspace-policy-line">
          <el-tag effect="plain">max files {{ workspaceSafety.workspace.maxFiles }}</el-tag>
          <el-tag effect="plain">max chars {{ workspaceSafety.workspace.maxReadChars }}</el-tag>
          <el-tag :type="workspaceSafety.workspace.dryRunDefault ? 'primary' : 'warning'" effect="plain">
            {{ workspaceSafety.workspace.dryRunDefault ? "默认 dry-run" : "允许直接写入" }}
          </el-tag>
          <el-tag :type="workspaceSafety.workspace.backupBeforeWrite ? 'success' : 'warning'" effect="plain">
            {{ workspaceSafety.workspace.backupBeforeWrite ? "写入前备份" : "不自动备份" }}
          </el-tag>
        </div>
      </div>

      <div class="folder-template-picker">
        <div class="folder-template-copy">
          <strong>文件夹工作流模板</strong>
          <span>模板会填充工作区、过滤规则、输出文件和计划内容。</span>
        </div>
        <el-select
          v-model="selectedFolderTemplateKey"
          filterable
          class="full-width"
          :loading="templateLoading"
          @change="applyFolderTemplate"
        >
          <el-option
            v-for="template in folderTemplateOptions"
            :key="template.key"
            :label="`${template.source === 'builtin' ? '内置' : template.source === 'platform' ? 'MySQL' : 'API'} · ${template.name}`"
            :value="template.key"
          >
            <div class="template-option">
              <strong>{{ template.name }}</strong>
              <span>{{ template.description }}</span>
            </div>
          </el-option>
        </el-select>
        <div class="folder-template-actions">
          <el-button size="small" plain @click="applyFolderTemplate()">应用模板</el-button>
          <el-button size="small" type="primary" plain :loading="loading" @click="runRecommendedFolderOperation">
            执行推荐动作
          </el-button>
        </div>
      </div>

      <el-form-item label="文件夹路径">
        <el-input v-model="folderForm.baseDir" placeholder="output/code_agent_workspace" />
      </el-form-item>

      <el-form-item label="include patterns">
        <el-input v-model="folderForm.includePatterns" placeholder="**/*.py, **/*.md" />
      </el-form-item>

      <el-form-item label="exclude patterns">
        <el-input v-model="folderForm.excludePatterns" placeholder=".env, .git/**, node_modules/**" />
      </el-form-item>

      <el-form-item label="输出文件">
        <el-input v-model="folderForm.outputFile" placeholder="code_agent_folder_result.md" />
      </el-form-item>

      <el-form-item label="输出内容 / 计划内容">
        <el-input
          v-model="folderForm.content"
          type="textarea"
          :rows="6"
          placeholder="将 AI 整合结果写入目标文件夹中的输出文件"
        />
      </el-form-item>

      <div class="folder-switches">
        <el-switch v-model="folderForm.recursive" active-text="递归扫描" inactive-text="仅当前目录" />
        <el-switch v-model="folderForm.dryRun" active-text="默认 dry-run" inactive-text="直接写入" />
        <el-switch v-model="folderForm.backupBeforeWrite" active-text="写入前备份" inactive-text="不备份" />
      </div>

      <div class="folder-actions">
        <el-button plain :loading="loading" @click="scanFolder">扫描文件夹</el-button>
        <el-button plain :loading="loading" @click="readFolder">读取文件夹</el-button>
        <el-button type="primary" plain :loading="loading" @click="planFolderChanges">生成修改计划</el-button>
        <el-button
          type="success"
          :icon="VideoPlay"
          :loading="loading"
          :disabled="!folderChanges.length"
          @click="applyFolderChanges"
        >
          应用到文件夹
        </el-button>
      </div>
    </el-form>

    <el-form v-else-if="mode === 'ai_generate'" label-position="top" class="code-agent-form">
      <div class="folder-mode-note" style="border-color: #d7f5dd; background: #e6f9ec; color: #1e7e34;">
        <strong>AI 一键项目生成</strong>
        <span>通过自然语言描述，AI 将会在 Workspace 下自动创建多个关联的代码文件（HTML, CSS, JS），并支持一键网页预览。</span>
      </div>

      <div class="workspace-picker">
        <div class="workspace-copy">
          <strong>Project Workspace</strong>
          <span>生成的项目文件将安全地写入受控工作区中，并支持白名单校验。</span>
        </div>
        <div class="workspace-controls">
          <el-select
            v-model="selectedWorkspaceId"
            class="full-width"
            :loading="workspaceLoading"
            :disabled="currentApiMode !== 'java' || !enabledWorkspaces.length"
            placeholder="选择受控 Workspace"
            @change="() => applyWorkspace()"
          >
            <el-option
              v-for="workspace in enabledWorkspaces"
              :key="workspace.id || workspace.rootPath"
              :label="`${workspace.isDefault ? '默认 · ' : ''}${workspace.name}`"
              :value="workspace.id"
            >
              <div class="template-option">
                <strong>{{ workspace.name }}</strong>
                <span>{{ workspace.rootPath }}</span>
              </div>
            </el-option>
          </el-select>
          <el-button size="small" plain :disabled="!selectedWorkspace" @click="applyWorkspace()">
            使用工作区
          </el-button>
          <el-button size="small" type="primary" plain :loading="openFolderLoading" @click="openWorkspaceFolder">
            打开文件夹
          </el-button>
        </div>
        <el-alert
          :title="workspaceSafety.message"
          :type="workspaceSafety.type"
          show-icon
          :closable="false"
          class="workspace-alert"
        />
      </div>

      <el-form-item label="生成目标路径">
        <el-input v-model="aiForm.baseDir" placeholder="output/code_agent_workspace" />
      </el-form-item>

      <el-form-item label="项目需求">
        <el-input
          v-model="aiForm.requirement"
          type="textarea"
          :rows="6"
          placeholder="请输入您对项目的描述，例如：写一个带有矩阵雨背景粒子特效的炫酷网页版计算器，包含 HTML, CSS 和 JS。"
        />
      </el-form-item>

      <el-form-item label="模型选择">
        <el-select v-model="aiForm.modelProvider" placeholder="默认模型" class="full-width" clearable>
          <el-option
            v-for="model in models"
            :key="model.provider"
            :label="`${model.name} / ${model.model}`"
            :value="model.provider"
          />
        </el-select>
      </el-form-item>

      <el-button type="primary" :icon="VideoPlay" :loading="loading" class="full-width" @click="runAiGeneration">
        开始 AI 一键生成项目
      </el-button>
    </el-form>

    <el-tag v-if="sseStatus" type="primary" effect="plain" class="sse-tag">{{ sseStatus }}</el-tag>

    <el-alert
      v-if="result"
      :title="result.message"
      :type="result.success ? 'success' : 'error'"
      show-icon
      :closable="false"
      class="result-alert"
    />
    <el-tag v-if="result?.results.some((item) => item.auditPath)" type="info" effect="plain" class="sse-tag">
      审计日志：{{ result.results.find((item) => item.auditPath)?.auditPath }}
    </el-tag>

    <el-collapse v-if="result" class="result-collapse">
      <el-collapse-item title="操作摘要" name="summary">
        <pre class="output-block">{{ JSON.stringify(result.results, null, 2) }}</pre>
        <div v-if="resultFiles.length" class="preview-actions" style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;">
          <template v-for="item in resultFiles" :key="`${item.operation}-${item.filePath}`">
            <el-button
              size="small"
              plain
              :loading="previewLoading"
              @click="previewFile(item.filePath)"
            >
              查看 {{ item.filePath }}
            </el-button>
            <el-button
              v-if="item.filePath.endsWith('.html')"
              type="primary"
              size="small"
              plain
              @click="previewHtmlFile(item.filePath)"
            >
              网页预览
            </el-button>
          </template>
          <el-button
            type="warning"
            size="small"
            plain
            :loading="openFolderLoading"
            @click="openFolderByPath(result.filePath || form.filePath || folderForm.baseDir)"
          >
            打开输出文件夹
          </el-button>
        </div>
      </el-collapse-item>
      <el-collapse-item v-if="folderResults.length" title="文件夹工作区结果" name="folder-workspace">
        <div class="folder-summary-grid">
          <el-card shadow="never" class="folder-stat">
            <span>扫描文件</span>
            <strong>{{ folderFileTree.length }}</strong>
          </el-card>
          <el-card shadow="never" class="folder-stat">
            <span>读取文件</span>
            <strong>{{ folderReadFiles.length }}</strong>
          </el-card>
          <el-card shadow="never" class="folder-stat">
            <span>计划变更</span>
            <strong>{{ folderChanges.length }}</strong>
          </el-card>
          <el-card shadow="never" class="folder-stat danger">
            <span>阻断/跳过</span>
            <strong>{{ folderBlockedFiles.length }}</strong>
          </el-card>
        </div>

        <div v-if="folderFileTree.length" class="folder-section">
          <div class="folder-section-title">文件树列表 (可预览)</div>
          <div class="file-list-detailed">
            <div v-for="file in folderFileTree.slice(0, 40)" :key="`tree-${file.filePath}`" class="file-tree-item">
              <span class="file-path-text">{{ file.relativePath || file.filePath }}</span>
              <div class="file-actions">
                <el-button size="small" plain :loading="previewLoading" @click="previewFile(file.filePath)">
                  查看
                </el-button>
                <el-button
                  v-if="file.filePath.endsWith('.html')"
                  type="primary"
                  size="small"
                  plain
                  @click="previewHtmlFile(file.filePath)"
                >
                  网页预览
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="folderReadFiles.length" class="folder-section">
          <div class="folder-section-title">读取内容摘要</div>
          <div class="change-list">
            <div v-for="file in folderReadFiles.slice(0, 8)" :key="`read-${file.filePath}`" class="change-item">
              <div class="change-title">
                <el-tag effect="plain">{{ file.relativePath || file.filePath }}</el-tag>
                <el-tag v-if="file.truncated" type="warning" effect="plain">已截断</el-tag>
              </div>
              <pre class="output-block diff-pre">{{ file.content }}</pre>
            </div>
          </div>
        </div>

        <div v-if="folderBlockedFiles.length" class="folder-section">
          <div class="folder-section-title">阻断 / 跳过路径</div>
          <div class="blocked-list">
            <el-alert
              v-for="file in folderBlockedFiles.slice(0, 12)"
              :key="`blocked-${file.filePath}-${file.reason}`"
              :title="file.filePath"
              :description="file.reason"
              type="warning"
              show-icon
              :closable="false"
            />
          </div>
        </div>

        <div v-if="folderChanges.length" class="folder-section">
          <div class="folder-section-title">变更计划与 diff</div>
          <div class="change-list">
            <div v-for="change in folderChanges" :key="`change-${change.filePath}`" class="change-item">
              <div class="change-title">
                <el-tag :type="change.action === 'create' ? 'success' : 'primary'" effect="plain">
                  {{ change.action }}
                </el-tag>
                <strong>{{ change.relativePath || change.filePath }}</strong>
                <el-button size="small" plain @click="previewFile(change.filePath)">查看文件</el-button>
                <el-button
                  v-if="change.filePath.endsWith('.html') || (change.relativePath && change.relativePath.endsWith('.html'))"
                  type="primary"
                  size="small"
                  plain
                  @click="previewHtmlFile(change.filePath)"
                >
                  网页预览
                </el-button>
              </div>
              <p v-if="change.reason" class="change-reason">{{ change.reason }}</p>
              <pre class="output-block diff-pre">{{ change.diff || change.after || change.content }}</pre>
            </div>
          </div>
        </div>

        <div v-if="folderBackups.length" class="folder-section">
          <div class="folder-section-title">写入前备份</div>
          <div class="file-list">
            <el-tag
              v-for="backup in folderBackups"
              :key="`${backup.filePath}-${backup.backupPath}`"
              type="info"
              effect="plain"
              size="small"
            >
              {{ backup.filePath }} → {{ backup.backupPath }}
            </el-tag>
          </div>
        </div>
      </el-collapse-item>
      <el-collapse-item v-if="diffPreview" title="生成/修改前后对比" name="diff">
        <div class="preview-title">
          <el-tag effect="plain">{{ diffPreview.filePath }}</el-tag>
          <el-tag v-if="diffPreview.beforeMissing" type="info" effect="plain">写入前无可读内容</el-tag>
          <el-tag v-if="diffPreview.beforeTruncated || diffPreview.afterTruncated" type="warning" effect="plain">
            内容可能已截断
          </el-tag>
          <el-button size="small" plain @click="copyDiff">复制 diff</el-button>
        </div>
        <div class="diff-view">
          <div
            v-for="(row, index) in diffPreview.rows"
            :key="`${row.type}-${row.lineNo}-${index}`"
            class="diff-line"
            :class="`diff-${row.type}`"
          >
            <span class="diff-mark">{{ row.type === "added" ? "+" : row.type === "removed" ? "-" : " " }}</span>
            <span class="diff-number">{{ row.lineNo }}</span>
            <code>{{ row.text || " " }}</code>
          </div>
        </div>
      </el-collapse-item>
      <el-collapse-item
        v-if="result.results.some((item) => item.content)"
        title="读取内容"
        name="content"
      >
        <pre class="output-block">{{ result.results.find((item) => item.content)?.content }}</pre>
      </el-collapse-item>
      <el-collapse-item
        v-if="result.results.some((item) => item.files?.length)"
        title="文件列表"
        name="files"
      >
        <div class="file-list">
          <el-tag
            v-for="file in result.results.flatMap((item) => item.files || [])"
            :key="file"
            effect="plain"
            size="small"
          >
            {{ file }}
          </el-tag>
        </div>
      </el-collapse-item>
      <el-collapse-item v-if="filePreview" title="文件内容预览" name="preview">
        <div class="preview-title">
          <el-tag effect="plain">{{ filePreview.filePath }}</el-tag>
          <el-tag v-if="filePreview.truncated" type="warning" effect="plain">已截断</el-tag>
        </div>
        <pre class="output-block">{{ filePreview.content }}</pre>
      </el-collapse-item>
    </el-collapse>

    <el-collapse v-if="auditPreview" class="result-collapse">
      <el-collapse-item title="审计日志预览" name="audit-preview">
        <div class="preview-title">
          <el-tag effect="plain">{{ auditPreview.path }}</el-tag>
          <el-tag v-if="auditPreview.truncated" type="warning" effect="plain">已截断</el-tag>
          <el-tag type="info" effect="plain">最近 {{ auditPreview.lines.length }} 条</el-tag>
          <el-button size="small" plain @click="copyAuditLog">复制审计日志</el-button>
        </div>
        <pre class="output-block">{{ auditPreview.lines.join("\n") || auditPreview.content }}</pre>
      </el-collapse-item>
    </el-collapse>

    <div v-if="events.length" class="event-section">
      <div class="section-title">事件时间线</div>
      <el-timeline>
        <el-timeline-item
          v-for="(event, index) in events"
          :key="`${eventKey(event)}-${index}`"
          :timestamp="event.createdAt"
          :type="event.status === 'FAILED' ? 'danger' : event.status === 'SUCCESS' ? 'success' : 'primary'"
        >
          <div class="event-row" :class="{ 'event-row-danger': event.status === 'FAILED' }">
            <el-tag effect="plain" size="small">{{ event.eventText || event.eventType }}</el-tag>
            <span>{{ event.message }}</span>
          </div>
        </el-timeline-item>
      </el-timeline>
      <el-button :icon="Refresh" size="small" plain @click="loadHistoryEvents(result?.platformRunId)">
        刷新历史事件
      </el-button>
    </div>
  </el-card>

  <!-- HTML Web Preview Dialog -->
  <el-dialog
    v-model="htmlPreviewVisible"
    :title="`网页效果预览 - ${htmlPreviewTitle}`"
    width="85%"
    destroy-on-close
    append-to-body
  >
    <div style="margin-bottom: 12px; display: flex; gap: 8px;">
      <el-button type="primary" size="small" @click="openPreviewInNewWindow">在新窗口打开</el-button>
      <el-button size="small" @click="previewKey++">刷新</el-button>
    </div>
    <iframe :key="previewKey" :src="htmlPreviewUrl" class="iframe-container"></iframe>
  </el-dialog>
</template>

<style scoped>
.code-agent-card {
  border-radius: 8px;
}

.code-agent-card-embedded {
  border: 0;
  background: transparent;
}

.code-agent-card-embedded :deep(.el-card__body) {
  padding: 0;
}

.code-agent-card-embedded .panel-alert:first-child {
  margin-top: 0;
}

.panel-head,
.event-row {
  display: flex;
  align-items: center;
}

.panel-head {
  justify-content: space-between;
  gap: 10px;
}

.panel-alert,
.quick-actions,
.result-alert,
.result-collapse,
.event-section,
.sse-tag {
  margin-top: 12px;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.mode-switch {
  width: 100%;
  margin-top: 12px;
}

.mode-switch :deep(.el-radio-button) {
  flex: 1;
}

.mode-switch :deep(.el-radio-button__inner) {
  width: 100%;
}

.code-agent-form {
  margin-top: 12px;
}

.folder-mode-note {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  border: 1px solid rgba(77, 163, 255, 0.2);
  border-radius: 10px;
  background:
    linear-gradient(135deg, rgba(77, 163, 255, 0.18), transparent 48%),
    #17191f;
  color: #9bd4ff;
  font-size: 12px;
}

.folder-template-picker {
  display: grid;
  gap: 8px;
  margin-top: 10px;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  background: #17191f;
}

.workspace-picker {
  display: grid;
  gap: 8px;
  margin-top: 10px;
  padding: 10px 12px;
  border: 1px solid rgba(77, 163, 255, 0.18);
  border-radius: 10px;
  background:
    radial-gradient(circle at 100% 0%, rgba(77, 163, 255, 0.12), transparent 42%),
    #17191f;
}

.workspace-copy {
  display: grid;
  gap: 2px;
}

.workspace-copy strong {
  color: #9bd4ff;
}

.workspace-copy span {
  color: #a1a1aa;
  font-size: 12px;
}

.workspace-controls,
.workspace-policy-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.workspace-controls .full-width {
  flex: 1;
  min-width: 180px;
}

.workspace-alert {
  margin-top: 0;
}

.folder-template-copy {
  display: grid;
  gap: 2px;
}

.folder-template-copy strong {
  color: #f4f4f5;
}

.folder-template-copy span,
.template-option span {
  color: #a1a1aa;
  font-size: 12px;
}

.folder-template-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.folder-template-actions :deep(.el-button) {
  margin-left: 0;
}

.template-option {
  display: grid;
  gap: 2px;
  line-height: 1.35;
}

.folder-switches,
.folder-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.folder-actions :deep(.el-button) {
  margin-left: 0;
}

.file-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.preview-actions,
.preview-title {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preview-actions {
  margin-top: 10px;
}

.preview-title {
  margin-bottom: 10px;
}

.folder-summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}

.folder-stat {
  border-radius: 10px;
}

.folder-stat :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
}

.folder-stat span {
  color: #a1a1aa;
  font-size: 12px;
}

.folder-stat strong {
  color: #8ab4f8;
  font-size: 20px;
}

.folder-stat.danger strong {
  color: #fb7185;
}

.folder-section {
  margin-top: 14px;
}

.folder-section-title {
  margin-bottom: 8px;
  color: #f4f4f5;
  font-weight: 800;
}

.blocked-list,
.change-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.change-item {
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  background: #17191f;
}

.change-title {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.change-reason {
  margin: 0 0 8px;
  color: #a1a1aa;
  font-size: 12px;
}

.diff-pre {
  max-height: 220px;
}

.diff-view {
  overflow: auto;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  background: #101218;
  font-family: Consolas, "Liberation Mono", monospace;
  font-size: 12px;
}

.diff-line {
  display: grid;
  grid-template-columns: 24px 46px minmax(0, 1fr);
  gap: 8px;
  min-height: 24px;
  padding: 3px 8px;
  white-space: pre-wrap;
}

.diff-added {
  background: rgba(74, 222, 128, 0.14);
  color: #9af4ba;
}

.diff-removed {
  background: rgba(251, 113, 133, 0.14);
  color: #fecdd3;
}

.diff-unchanged {
  color: #d4d4d8;
}

.diff-mark,
.diff-number {
  color: #a1a1aa;
  user-select: none;
}

.section-title {
  margin-bottom: 10px;
  color: #f4f4f5;
  font-weight: 800;
}

.event-row {
  flex-wrap: wrap;
  gap: 8px;
}

.event-row-danger {
  color: #fb7185;
  font-weight: 700;
}

.file-list-detailed {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 250px;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 8px;
  background: #101218;
}

.file-tree-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: #17191f;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  gap: 12px;
}

.file-path-text {
  font-size: 13px;
  color: #d4d4d8;
  word-break: break-all;
  font-family: Consolas, monospace;
}

.file-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.iframe-container {
  width: 100%;
  height: 60vh;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  background: #101218;
}
</style>
