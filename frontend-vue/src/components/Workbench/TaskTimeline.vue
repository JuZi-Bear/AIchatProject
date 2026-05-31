<script setup lang="ts">
import { computed, ref } from "vue";
import { ElMessage } from "element-plus";
import { CopyDocument, Document, Files, FolderOpened, MagicStick, View, Warning } from "@element-plus/icons-vue";

import { getCodeAgentPreviewUrl, openCodeAgentFolder } from "@/api/codeAgent";
import WebPreviewFrame from "@/components/Workbench/WebPreviewFrame.vue";

import type {
  CodeAgentBlockedFile,
  CodeAgentFolderChange,
  CodeAgentOperationResult,
  CodeAgentResponse,
} from "@/types/codeAgent";
import type { FolderWorkflowContext } from "@/types/interaction";
import type { RunResponse } from "@/types/run";
import type { RunEvent } from "@/types/runEvent";

const props = defineProps<{
  requirement: string;
  folderContext: FolderWorkflowContext;
  templateName: string;
  running: boolean;
  errorDetail: string;
  response: RunResponse | null;
  liveEvents: RunEvent[];
  codeAgentResponse: CodeAgentResponse | null;
}>();

type SkillExportArtifact = {
  skillName: string;
  skillPath: string;
  files: string[];
};

const previewDialog = ref<{ visible: boolean; title: string; src: string }>({
  visible: false,
  title: "",
  src: "",
});
const openingFolder = ref(false);

const hasActivity = computed(
  () =>
    Boolean(
      props.requirement ||
        props.running ||
        props.errorDetail ||
        props.response ||
        props.codeAgentResponse ||
        props.liveEvents.length,
    ),
);

const isAiGenerate = computed(() => props.folderContext.runMode === "code_agent_ai_generate");
const workspaceText = computed(() => props.folderContext.folderPath || "未选择 Workspace");
const activeTemplateText = computed(() => {
  if (isAiGenerate.value) {
    return "CodeAgent AI 一键生成";
  }

  return props.templateName || "文件夹工作流模板";
});
const safetyLabel = computed(() => {
  if (props.folderContext.safety.type === "danger") {
    return "路径受限";
  }
  if (props.folderContext.safety.type === "warning") {
    return "需要确认";
  }
  if (props.folderContext.safety.mode === "python-direct") {
    return "本地白名单";
  }
  return "已配置 Workspace";
});

const codeAgentResults = computed<CodeAgentOperationResult[]>(() => props.codeAgentResponse?.results || []);
const htmlFiles = computed(() => {
  const paths = codeAgentResults.value.flatMap((result) => [
    result.filePath,
    ...(result.files || []),
    ...(result.changes || []).map((change) => change.filePath),
    ...(result.fileTree || []).map((file) => file.filePath),
    ...(result.folderFiles || []).map((file) => file.filePath),
  ]);

  return Array.from(new Set(paths.filter((path): path is string => Boolean(path && path.endsWith(".html")))));
});
const folderChanges = computed<CodeAgentFolderChange[]>(() =>
  codeAgentResults.value.flatMap((result) => result.changes || []),
);
const blockedFiles = computed<CodeAgentBlockedFile[]>(() =>
  codeAgentResults.value.flatMap((result) => result.blockedFiles || []),
);
const auditPath = computed(
  () => props.codeAgentResponse?.auditPath || codeAgentResults.value.find((result) => result.auditPath)?.auditPath || "",
);
const outputFolder = computed(
  () => codeAgentResults.value.find((result) => result.baseDir)?.baseDir || props.folderContext.folderPath || "output",
);
const createdFiles = computed(() =>
  Array.from(
    new Set(
      codeAgentResults.value
        .flatMap((result) => [result.filePath, ...(result.files || [])])
        .filter((path): path is string => Boolean(path)),
    ),
  ),
);
const editedStats = computed(() => {
  let additions = 0;
  let deletions = 0;

  folderChanges.value.forEach((change) => {
    const diff = change.diff || "";
    diff.split(/\r?\n/).forEach((line) => {
      if (line.startsWith("+++") || line.startsWith("---")) {
        return;
      }
      if (line.startsWith("+")) {
        additions += 1;
      } else if (line.startsWith("-")) {
        deletions += 1;
      }
    });
  });

  return { additions, deletions };
});
const latestEvents = computed(() => props.liveEvents.slice(-4).reverse());
const replayPath = computed(() => {
  const platformRunId =
    props.codeAgentResponse?.platformRunId || props.response?.platform_run_id || props.response?.platformRunId || "";

  return platformRunId ? `/replay/${platformRunId}` : "";
});
const reportPath = computed(
  () => props.response?.run_summary?.report_path || props.response?.ui_view_model?.report?.report_path || "",
);
const skillExports = computed<SkillExportArtifact[]>(() => {
  const rows: SkillExportArtifact[] = [];

  props.liveEvents.forEach((event) => {
    const detail = parseDetail(event.detailJson);
    const skillPath = String(detail?.skillPath || detail?.skill_path || "");

    if (!skillPath) {
      return;
    }

    rows.push({
      skillName: String(detail?.skillName || detail?.skill_name || skillPath.split(/[\\/]/).pop() || "workflow-skill"),
      skillPath,
      files: Array.isArray(detail?.files) ? detail.files.map(String) : [],
    });
  });

  return rows;
});

function parseDetail(detailJson?: string) {
  if (!detailJson) {
    return null;
  }

  try {
    return JSON.parse(detailJson) as Record<string, unknown>;
  } catch {
    return null;
  }
}

function openPreview(filePath: string) {
  previewDialog.value = {
    visible: true,
    title: filePath,
    src: getCodeAgentPreviewUrl(filePath),
  };
}

function openPreviewInNewTab(filePath: string) {
  window.open(getCodeAgentPreviewUrl(filePath), "_blank", "noopener,noreferrer");
}

async function copyText(value: string, label = "内容") {
  if (!value) {
    return;
  }

  try {
    await navigator.clipboard.writeText(value);
    ElMessage.success(`${label}已复制`);
  } catch {
    ElMessage.info(value);
  }
}

async function openFolder(path: string) {
  openingFolder.value = true;
  try {
    const response = await openCodeAgentFolder(path || "output");
    if (response.success) {
      ElMessage.success(response.message || "已打开文件夹");
    } else {
      ElMessage.error(response.message || "打开文件夹失败");
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "打开文件夹失败");
  } finally {
    openingFolder.value = false;
  }
}

function fileName(path: string) {
  return path.split(/[\\/]/).pop() || path;
}
</script>

<template>
  <section class="task-transcript">
    <div v-if="!hasActivity" class="empty-transcript">
      <span class="empty-dot" />
      <p>选择 Workspace，输入目标，点击 AI 一键生成。</p>
      <small>工具调用、文件变更、网页预览和 Skill 导出会像 Codex 一样显示在这里。</small>
    </div>

    <template v-else>
      <article class="transcript-message system-message">
        <div class="message-body">
          <strong>Workspace context</strong>
          <p>
            {{ workspaceText }} · {{ activeTemplateText }} · {{ folderContext.dryRun ? "dry-run" : "write" }} ·
            {{ folderContext.backupBeforeWrite ? "backup" : "no backup" }}
          </p>
        </div>
        <span class="status-pill">{{ safetyLabel }}</span>
      </article>

      <article class="transcript-message user-message">
        <div class="avatar user-avatar">U</div>
        <div class="message-body">
          <strong>User request</strong>
          <p>{{ requirement || "描述你想生成或改造的项目。" }}</p>
        </div>
      </article>

      <article class="transcript-message assistant-message">
        <div class="avatar assistant-avatar">AI</div>
        <div class="message-body markdown-body">
          <p>我会按当前上下文执行：</p>
          <ul>
            <li>读取 Workspace 与安全策略。</li>
            <li>{{ isAiGenerate ? "生成可预览的项目文件。" : "生成文件夹扫描、diff 和 Markdown 输出。" }}</li>
            <li>记录审计日志，并把产物放入 Output 与 Replay。</li>
          </ul>
        </div>
      </article>

      <article v-if="running" class="tool-call-card running-card">
        <div class="artifact-icon glow-blue">
          <el-icon><MagicStick /></el-icon>
        </div>
        <div>
          <strong>正在执行</strong>
          <p>等待工具返回结果，Java 模式下事件会继续写入 RunEvent / SSE。</p>
        </div>
        <span class="status-pill primary">running</span>
      </article>

      <article v-if="errorDetail" class="tool-call-card error-card">
        <div class="artifact-icon glow-red">
          <el-icon><Warning /></el-icon>
        </div>
        <div>
          <strong>任务失败</strong>
          <p>{{ errorDetail }}</p>
        </div>
        <span class="status-pill danger">error</span>
      </article>

      <article v-if="codeAgentResponse" class="tool-call-card">
        <div class="artifact-icon glow-yellow">
          <el-icon><MagicStick /></el-icon>
        </div>
        <div>
          <strong>{{ isAiGenerate ? "CodeAgent AI 一键生成" : "CodeAgent tool invocation" }}</strong>
          <p>{{ codeAgentResponse.message || "CodeAgent 文件操作完成。" }}</p>
        </div>
        <span class="status-pill" :class="codeAgentResponse.success ? 'success' : 'danger'">
          {{ codeAgentResponse.success ? "success" : "failed" }}
        </span>
      </article>

      <article v-if="htmlFiles.length" class="artifact-card preview-card">
        <div class="artifact-icon glow-blue">
          <el-icon><View /></el-icon>
        </div>
        <div class="artifact-content">
          <strong>网页预览</strong>
          <span>网站 · {{ fileName(htmlFiles[0]) }}</span>
        </div>
        <el-dropdown trigger="click">
          <button class="artifact-action-button" type="button">打开方式⌄</button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="openPreview(htmlFiles[0])">内嵌预览</el-dropdown-item>
              <el-dropdown-item @click="openPreviewInNewTab(htmlFiles[0])">浏览器打开</el-dropdown-item>
              <el-dropdown-item @click="copyText(getCodeAgentPreviewUrl(htmlFiles[0]), '预览链接')">
                复制链接
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </article>

      <article v-if="folderChanges.length || createdFiles.length" class="artifact-card changes-card">
        <div class="artifact-icon">
          <el-icon><Files /></el-icon>
        </div>
        <div class="artifact-content">
          <div class="artifact-title-row">
            <strong>已编辑 {{ folderChanges.length || createdFiles.length }} 个文件</strong>
            <span class="diff-stat">
              <b>+{{ editedStats.additions }}</b>
              <em>-{{ editedStats.deletions }}</em>
            </span>
          </div>
          <div class="change-list">
            <div
              v-for="change in folderChanges.slice(0, 4)"
              :key="`${change.filePath}-${change.action}`"
              class="change-row"
            >
              <span>{{ change.relativePath || change.filePath }}</span>
              <small>{{ change.action }}</small>
            </div>
            <div v-for="file in !folderChanges.length ? createdFiles.slice(0, 4) : []" :key="file" class="change-row">
              <span>{{ file }}</span>
              <small>file</small>
            </div>
          </div>
          <button v-if="folderChanges.length > 4" class="text-action" type="button">
            再显示 {{ folderChanges.length - 4 }} 个文件
          </button>
        </div>
      </article>

      <article v-if="blockedFiles.length" class="artifact-card blocked-card">
        <div class="artifact-icon glow-red">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="artifact-content">
          <strong>阻断路径安全测试</strong>
          <span>{{ blockedFiles.length }} 个路径被阻断，未写入。</span>
          <div class="change-list compact">
            <div v-for="file in blockedFiles.slice(0, 3)" :key="file.filePath" class="change-row">
              <span>{{ file.filePath }}</span>
              <small>{{ file.reason }}</small>
            </div>
          </div>
        </div>
      </article>

      <article v-if="auditPath" class="artifact-card">
        <div class="artifact-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="artifact-content">
          <strong>JSONL 审计日志</strong>
          <span>{{ auditPath }}</span>
        </div>
        <button class="artifact-action-button" type="button" @click="copyText(auditPath, '审计日志路径')">复制</button>
      </article>

      <article v-if="codeAgentResponse" class="artifact-card">
        <div class="artifact-icon">
          <el-icon><FolderOpened /></el-icon>
        </div>
        <div class="artifact-content">
          <strong>打开输出文件夹</strong>
          <span>{{ outputFolder }}</span>
        </div>
        <button class="artifact-action-button" type="button" :disabled="openingFolder" @click="openFolder(outputFolder)">
          打开
        </button>
      </article>

      <article v-for="skill in skillExports" :key="skill.skillPath" class="artifact-card skill-card">
        <div class="artifact-icon glow-blue">
          <el-icon><MagicStick /></el-icon>
        </div>
        <div class="artifact-content">
          <strong>Skill 导出完成：{{ skill.skillName }}</strong>
          <span>{{ skill.skillPath }}</span>
          <div v-if="skill.files.length" class="mini-tags">
            <em v-for="file in skill.files.slice(0, 4)" :key="file">{{ file }}</em>
          </div>
        </div>
        <button class="artifact-action-button" type="button" @click="copyText(skill.skillPath, 'Skill 路径')">复制</button>
      </article>

      <article v-if="replayPath || reportPath" class="artifact-card result-card">
        <div class="artifact-icon glow-green">
          <el-icon><Document /></el-icon>
        </div>
        <div class="artifact-content">
          <strong>任务结果</strong>
          <span>{{ reportPath || "运行事件和产物已记录，可进入 Replay 查看。" }}</span>
        </div>
        <router-link v-if="replayPath" class="artifact-action-button" :to="replayPath">Replay</router-link>
      </article>

      <article v-if="latestEvents.length" class="event-summary-card">
        <strong>最近事件</strong>
        <div class="event-lines">
          <span v-for="event in latestEvents" :key="event.id || `${event.eventType}-${event.createdAt}`">
            {{ event.eventText || event.eventType }} · {{ event.status || "event" }}
          </span>
        </div>
      </article>
    </template>

    <el-dialog v-model="previewDialog.visible" :title="previewDialog.title" width="86%" append-to-body destroy-on-close>
      <WebPreviewFrame :src="previewDialog.src" :title="previewDialog.title" />
    </el-dialog>
  </section>
</template>

<style scoped>
.task-transcript {
  display: grid;
  align-content: start;
  gap: 14px;
  min-height: 0;
  padding: 18px 4px 26px;
  background: transparent !important;
}

.empty-transcript {
  display: contents;
}

.empty-transcript .empty-dot {
  display: none;
}

.empty-transcript p {
  width: max-content;
  max-width: min(100%, 560px);
  margin: 20vh auto 0;
  color: #f4f4f5;
  font-size: 17px;
  font-weight: 760;
  text-align: center;
}

.empty-transcript small {
  display: block;
  max-width: 420px;
  margin: 8px auto 0;
  color: #8e8e95;
  line-height: 1.6;
  text-align: center;
}

.empty-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #8e8e95;
}

.transcript-message,
.tool-call-card,
.artifact-card,
.event-summary-card {
  width: min(100%, 860px);
  margin: 0 auto;
}

.transcript-message {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 12px;
  align-items: start;
  padding: 8px 0;
  color: #f4f4f5;
}

.system-message {
  grid-template-columns: minmax(0, 1fr) auto;
  padding: 14px 16px;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.035);
}

.avatar {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
}

.user-avatar {
  background: #2f333c;
  color: #ffffff;
}

.assistant-avatar {
  background:
    radial-gradient(circle at 30% 20%, rgba(77, 163, 255, 0.95), transparent 38%),
    linear-gradient(135deg, #1f6feb, #34d399);
  color: #ffffff;
}

.message-body {
  min-width: 0;
}

.message-body strong,
.artifact-content strong,
.tool-call-card strong,
.event-summary-card strong {
  color: #f4f4f5;
  font-weight: 760;
}

.message-body p,
.message-body ul {
  margin: 4px 0 0;
  color: #d4d4d8;
  line-height: 1.62;
}

.markdown-body ul {
  padding-left: 20px;
}

.tool-call-card,
.artifact-card,
.event-summary-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 14px;
  align-items: center;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 16px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.048), rgba(255, 255, 255, 0.018)),
    #17191f;
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.18);
}

.tool-call-card p,
.artifact-content span {
  display: block;
  margin: 4px 0 0;
  overflow-wrap: anywhere;
  color: #a1a1aa;
  line-height: 1.5;
}

.running-card {
  border-color: rgba(77, 163, 255, 0.28);
}

.error-card,
.blocked-card {
  border-color: rgba(251, 113, 133, 0.34);
  background:
    radial-gradient(circle at 100% 0%, rgba(251, 113, 133, 0.14), transparent 42%),
    #1f1519;
}

.preview-card,
.skill-card {
  border-color: rgba(77, 163, 255, 0.3);
}

.changes-card {
  align-items: start;
}

.result-card {
  border-color: rgba(74, 222, 128, 0.25);
}

.artifact-icon {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: 13px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.026)),
    #111318;
  color: #d4d4d8;
  font-size: 20px;
}

.glow-blue {
  color: #bfdbfe;
  background:
    radial-gradient(circle at 35% 20%, rgba(77, 163, 255, 0.62), transparent 45%),
    #102033;
}

.glow-yellow {
  color: #fde68a;
  background:
    radial-gradient(circle at 35% 20%, rgba(250, 204, 21, 0.46), transparent 45%),
    #282110;
}

.glow-green {
  color: #bbf7d0;
  background:
    radial-gradient(circle at 35% 20%, rgba(74, 222, 128, 0.45), transparent 45%),
    #102318;
}

.glow-red {
  color: #fecdd3;
  background:
    radial-gradient(circle at 35% 20%, rgba(251, 113, 133, 0.5), transparent 45%),
    #2a1218;
}

.status-pill {
  align-self: start;
  padding: 4px 9px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.07);
  color: #d4d4d8;
  font-size: 12px;
  font-weight: 750;
  white-space: nowrap;
}

.status-pill.primary {
  background: rgba(77, 163, 255, 0.15);
  color: #93c5fd;
}

.status-pill.success {
  background: rgba(74, 222, 128, 0.14);
  color: #86efac;
}

.status-pill.danger {
  background: rgba(251, 113, 133, 0.14);
  color: #fda4af;
}

.artifact-action-button,
.text-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 0 12px;
  border: 0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.07);
  color: #f4f4f5;
  cursor: pointer;
  font-weight: 720;
  text-decoration: none;
  white-space: nowrap;
}

.artifact-action-button:hover,
.text-action:hover {
  background: rgba(255, 255, 255, 0.11);
}

.artifact-action-button:disabled {
  cursor: default;
  opacity: 0.48;
}

.artifact-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.diff-stat {
  display: inline-flex;
  gap: 6px;
  color: #a1a1aa;
  font-size: 13px;
  font-weight: 780;
}

.diff-stat b {
  color: #34d399;
}

.diff-stat em {
  color: #fb7185;
  font-style: normal;
}

.change-list {
  display: grid;
  gap: 2px;
  margin-top: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
}

.change-list.compact {
  margin-top: 10px;
}

.change-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  padding: 8px 10px;
  background: rgba(0, 0, 0, 0.16);
}

.change-row + .change-row {
  border-top: 1px solid rgba(255, 255, 255, 0.055);
}

.change-row span {
  overflow: hidden;
  color: #f4f4f5;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.change-row small {
  color: #a1a1aa;
}

.mini-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 9px;
}

.mini-tags em {
  padding: 3px 7px;
  border-radius: 999px;
  background: rgba(77, 163, 255, 0.12);
  color: #93c5fd;
  font-size: 11px;
  font-style: normal;
  font-weight: 760;
}

.event-summary-card {
  grid-template-columns: minmax(0, 1fr);
  opacity: 0.82;
}

.event-lines {
  display: grid;
  gap: 6px;
  margin-top: 4px;
}

.event-lines span {
  overflow: hidden;
  color: #a1a1aa;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 720px) {
  .tool-call-card,
  .artifact-card,
  .transcript-message {
    grid-template-columns: minmax(0, 1fr);
  }

  .artifact-icon,
  .avatar {
    display: none;
  }

  .artifact-action-button {
    justify-self: start;
  }
}
</style>
