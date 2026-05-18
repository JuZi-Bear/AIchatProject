<script setup lang="ts">
import { Refresh, VideoPlay } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onBeforeUnmount, reactive, ref } from "vue";

import { executeCodeAgent } from "@/api/codeAgent";
import { currentApiMode } from "@/api/client";
import { subscribeRunEvents, type RunEventSubscription } from "@/api/eventStream";
import { getRunEvents } from "@/api/events";
import { useWorkflowEditorStore } from "@/components/WorkflowEditor/WorkflowEditorStore";
import type { CodeAgentOperation, CodeAgentResponse } from "@/types/codeAgent";
import type { RunEvent } from "@/types/runEvent";

const props = withDefaults(
  defineProps<{
    alwaysVisible?: boolean;
  }>(),
  {
    alwaysVisible: false,
  },
);

const store = useWorkflowEditorStore();
const selectedNode = computed(() => store.selectedNode);
const visible = computed(() => props.alwaysVisible || selectedNode.value?.agentKey === "code_agent");
const loading = ref(false);
const previewLoading = ref(false);
const auditLoading = ref(false);
const sseStatus = ref("");
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
const demoWriteContent = `# CodeAgent demo file

def my_func():
    return "created by CodeAgent"
`;

const form = reactive({
  operation: "read_file" as CodeAgentOperation,
  filePath: "output/code_agent_demo.txt",
  content: "",
  recursive: false,
});

const operationOptions = [
  { label: "read_file", value: "read_file" },
  { label: "write_file", value: "write_file" },
  { label: "list_files", value: "list_files" },
] as const;

const resultFiles = computed(
  () => result.value?.results.filter((item) => item.filePath && item.operation !== "list_files") || [],
);
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
  form.operation = "write_file";
  form.filePath = demoWritePath;
  form.content = demoWriteContent;
  form.recursive = false;
}

async function runBlockedPathCheck() {
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

onBeforeUnmount(closeSubscription);
</script>

<template>
  <el-card v-if="visible" shadow="never" class="code-agent-card">
    <template #header>
      <div class="panel-head">
        <span>CodeAgent 文件操作</span>
        <el-tag type="warning" effect="plain">简化执行模块</el-tag>
      </div>
    </template>

    <el-alert
      title="仅支持项目目录内 read_file / write_file / list_files，不是完整 Codex。Java 模式下事件会进入 RunEvent + SSE。"
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
      <el-button size="small" type="danger" plain :loading="loading" @click="runBlockedPathCheck">
        测试阻断路径 .env
      </el-button>
      <el-button size="small" plain :loading="auditLoading" @click="previewAuditLog">
        预览审计日志
      </el-button>
    </div>

    <el-form label-position="top" class="code-agent-form">
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
        <div v-if="resultFiles.length" class="preview-actions">
          <el-button
            v-for="item in resultFiles"
            :key="`${item.operation}-${item.filePath}`"
            size="small"
            plain
            :loading="previewLoading"
            @click="previewFile(item.filePath)"
          >
            查看 {{ item.filePath }}
          </el-button>
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
</template>

<style scoped>
.code-agent-card {
  border-radius: 8px;
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

.code-agent-form {
  margin-top: 12px;
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

.diff-view {
  overflow: auto;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
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
  background: #dcfce7;
  color: #166534;
}

.diff-removed {
  background: #fee2e2;
  color: #991b1b;
}

.diff-unchanged {
  color: #475569;
}

.diff-mark,
.diff-number {
  color: #64748b;
  user-select: none;
}

.section-title {
  margin-bottom: 10px;
  color: #475569;
  font-weight: 800;
}

.event-row {
  flex-wrap: wrap;
  gap: 8px;
}

.event-row-danger {
  color: #b91c1c;
  font-weight: 700;
}
</style>
