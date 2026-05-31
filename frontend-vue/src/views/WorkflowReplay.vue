<script setup lang="ts">
import { ArrowLeft, Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getWorkflowReplay } from "@/api/replay";
import { currentApiMode } from "@/api/client";
import { approvePlatformRun } from "@/api/runs";
import { resumePlatformDynamicLangGraphRun } from "@/api/workflows";
import ReplayControlPanel from "@/components/ReplayControlPanel.vue";
import ReplayEventCard from "@/components/ReplayEventCard.vue";
import WorkflowReplayTimeline from "@/components/WorkflowReplayTimeline.vue";
import type { ReplayFilterState, WorkflowReplayData } from "@/types/replay";

const route = useRoute();
const router = useRouter();
const platformRunId = computed(() => String(route.params.platformRunId || ""));
const replay = ref<WorkflowReplayData | null>(null);
const loading = ref(false);
const errorDetail = ref("");
const currentIndex = ref(0);
const playing = ref(false);
const speedMs = ref(800);
const approvalComment = ref("");
const approving = ref(false);
const filters = ref<ReplayFilterState>({
  agent: "all",
  status: "all",
  keyword: "",
});
let playTimer: ReturnType<typeof window.setInterval> | null = null;

const allEvents = computed(() => replay.value?.events || []);
const events = computed(() => {
  const keyword = filters.value.keyword.trim().toLowerCase();

  return allEvents.value.filter((event) => {
    if (filters.value.agent !== "all") {
      const agent = event.agent || (event.platformRunId?.startsWith("code_agent") ? "code_agent" : "");

      if (agent !== filters.value.agent) {
        return false;
      }
    }

    if (filters.value.status !== "all" && event.status !== filters.value.status) {
      return false;
    }

    if (!keyword) {
      return true;
    }

    return `${event.eventText} ${event.message || ""} ${event.detailJson || ""}`.toLowerCase().includes(keyword);
  });
});
const currentEvent = computed(() => events.value[currentIndex.value] || null);
const codeAgentEventCount = computed(
  () => allEvents.value.filter((event) => event.agent === "code_agent" || event.platformRunId?.startsWith("code_agent")).length,
);
const failedEventCount = computed(
  () => allEvents.value.filter((event) => event.status === "FAILED" || event.eventType.includes("FAILED") || event.eventType === "ERROR_OCCURRED").length,
);
const waitingForHuman = computed(() => replay.value?.status === "WAITING_FOR_HUMAN");
const runtimeSummary = computed(() => {
  const uiSummary = replay.value?.uiViewModel?.runtime_summary;
  const runSummary = replay.value?.runSummary || {};
  const nodeCounts =
    (uiSummary && typeof uiSummary === "object" && "node_counts" in uiSummary
      ? (uiSummary as Record<string, unknown>).node_counts
      : runSummary.runtime_node_counts) || {};

  return {
    mode:
      (uiSummary && typeof uiSummary === "object" ? String((uiSummary as Record<string, unknown>).mode || "") : "") ||
      String(runSummary.runtime_mode || ""),
    nodeCounts: nodeCounts as Record<string, unknown>,
    reportPath:
      (uiSummary && typeof uiSummary === "object"
        ? String((uiSummary as Record<string, unknown>).report_path || "")
        : "") || String(runSummary.report_path || ""),
    codeAgent:
      (uiSummary && typeof uiSummary === "object" && "code_agent" in uiSummary
        ? ((uiSummary as Record<string, unknown>).code_agent as Record<string, unknown>)
        : {}) || {},
    connectionMappings:
      (uiSummary && typeof uiSummary === "object" && Array.isArray((uiSummary as Record<string, unknown>).connection_mappings)
        ? ((uiSummary as Record<string, unknown>).connection_mappings as Array<Record<string, unknown>>)
        : Array.isArray(runSummary.connection_mappings)
          ? (runSummary.connection_mappings as Array<Record<string, unknown>>)
          : []),
  };
});
const isRuntimeLiteReplay = computed(() => runtimeSummary.value.mode === "workflow_runtime_lite");
const isDynamicLangGraphReplay = computed(() => runtimeSummary.value.mode === "dynamic_langgraph");
const agentOptions = [
  { label: "全部 Agent", value: "all" },
  { label: "CodeAgent", value: "code_agent" },
  { label: "Product", value: "product" },
  { label: "Coder", value: "coder" },
  { label: "Tester", value: "tester" },
  { label: "Runner", value: "runner" },
  { label: "Sentry", value: "sentry" },
  { label: "Quality", value: "quality" },
  { label: "Report", value: "report" },
  { label: "Workflow", value: "workflow" },
];
const statusOptions = [
  { label: "全部状态", value: "all" },
  { label: "SUCCESS", value: "SUCCESS" },
  { label: "FAILED", value: "FAILED" },
  { label: "RUNNING", value: "RUNNING" },
  { label: "WAITING_FOR_HUMAN", value: "WAITING_FOR_HUMAN" },
  { label: "APPROVED", value: "APPROVED" },
  { label: "REJECTED", value: "REJECTED" },
];
const durationText = computed(() => {
  const durationMs = replay.value?.durationMs || 0;
  if (!durationMs) {
    return "未记录";
  }

  if (durationMs < 1000) {
    return `${durationMs} ms`;
  }

  return `${Math.round((durationMs / 1000) * 10) / 10} s`;
});

function statusTagType(status?: string) {
  if (status === "SUCCESS") {
    return "success";
  }

  if (status === "FAILED") {
    return "danger";
  }

  if (status === "RUNNING") {
    return "primary";
  }

  if (status === "CANCELLED") {
    return "warning";
  }

  if (status === "WAITING_FOR_HUMAN") {
    return "warning";
  }

  if (status === "APPROVED") {
    return "success";
  }

  if (status === "REJECTED") {
    return "danger";
  }

  return "info";
}

function clearPlayTimer() {
  if (playTimer) {
    window.clearInterval(playTimer);
    playTimer = null;
  }
}

function pauseReplay() {
  playing.value = false;
  clearPlayTimer();
}

function nextStep() {
  if (!events.value.length) {
    return;
  }

  if (currentIndex.value >= events.value.length - 1) {
    pauseReplay();
    return;
  }

  currentIndex.value += 1;
}

function previousStep() {
  pauseReplay();
  currentIndex.value = Math.max(0, currentIndex.value - 1);
}

function resetReplay() {
  pauseReplay();
  currentIndex.value = 0;
}

function resetFilters() {
  filters.value = {
    agent: "all",
    status: "all",
    keyword: "",
  };
  resetReplay();
}

function showCodeAgentOnly() {
  filters.value.agent = "code_agent";
  filters.value.status = "all";
  filters.value.keyword = "";
  resetReplay();
}

function playReplay() {
  if (!events.value.length || currentIndex.value >= events.value.length - 1) {
    return;
  }

  clearPlayTimer();
  playing.value = true;
  playTimer = window.setInterval(nextStep, speedMs.value);
}

async function loadReplay() {
  if (!platformRunId.value) {
    errorDetail.value = "缺少 platformRunId";
    return;
  }

  loading.value = true;
  errorDetail.value = "";
  pauseReplay();

  try {
    replay.value = await getWorkflowReplay(platformRunId.value);
    currentIndex.value = events.value.length ? 0 : -1;
  } catch (error) {
    replay.value = null;
    errorDetail.value = error instanceof Error ? error.message : "加载工作流回放失败";
    ElMessage.error(errorDetail.value);
  } finally {
    loading.value = false;
  }
}

async function submitApproval(approved: boolean) {
  if (currentApiMode !== "java" || !platformRunId.value) {
    ElMessage.warning("人工确认仅 Java Gateway 模式支持");
    return;
  }

  approving.value = true;

  try {
    if (isDynamicLangGraphReplay.value) {
      await resumePlatformDynamicLangGraphRun(platformRunId.value, approved, approvalComment.value);
      ElMessage.success(approved ? "Dynamic LangGraph 已恢复执行" : "Dynamic LangGraph 已拒绝继续");
    } else {
      await approvePlatformRun(platformRunId.value, approved, approvalComment.value);
      ElMessage.success(approved ? "已批准继续执行" : "已拒绝继续执行");
    }
    await loadReplay();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "提交人工确认失败");
  } finally {
    approving.value = false;
  }
}

watch(speedMs, () => {
  if (playing.value) {
    playReplay();
  }
});

watch(filters, () => {
  pauseReplay();
  currentIndex.value = events.value.length ? 0 : -1;
}, { deep: true });

onMounted(loadReplay);

onBeforeUnmount(() => {
  clearPlayTimer();
});
</script>

<template>
  <section class="page-stack replay-page">
    <div class="page-header">
      <div>
        <h1>Execution Transcript</h1>
        <p>按 Codex 风执行记录查看事件、当前节点、产物和人工确认。</p>
      </div>
      <div class="header-actions">
        <el-button :icon="ArrowLeft" @click="router.push('/history')">返回历史</el-button>
        <el-button :icon="Refresh" :loading="loading" @click="loadReplay">刷新</el-button>
      </div>
    </div>

    <el-alert
      v-if="errorDetail"
      :title="errorDetail"
      type="error"
      show-icon
      :closable="false"
    />

    <template v-if="replay">
      <el-card shadow="never" class="replay-summary-card">
        <div class="summary-grid">
          <div>
            <span>Platform Run</span>
            <strong>{{ replay.platformRunId }}</strong>
          </div>
          <div>
            <span>Python Run</span>
            <strong>{{ replay.pythonRunId || "未记录" }}</strong>
          </div>
          <div>
            <span>状态</span>
            <el-tag :type="statusTagType(replay.status)" effect="plain">{{ replay.statusText || replay.status }}</el-tag>
          </div>
          <div>
            <span>质量评分</span>
            <strong>{{ replay.qualityScore }}</strong>
          </div>
          <div>
            <span>事件数量</span>
            <strong>{{ events.length }} / {{ allEvents.length }}</strong>
          </div>
          <div>
            <span>持续时间</span>
            <strong>{{ durationText }}</strong>
          </div>
        </div>
        <div class="requirement-block">{{ replay.requirement || "无需求摘要" }}</div>
      </el-card>

      <el-card v-if="isRuntimeLiteReplay || isDynamicLangGraphReplay" shadow="never" class="runtime-summary-card">
        <template #header>
          <div class="runtime-summary-head">
            <span>{{ isDynamicLangGraphReplay ? "Dynamic LangGraph 汇总" : "Workflow Runtime Lite 汇总" }}</span>
            <el-tag :type="isDynamicLangGraphReplay ? 'warning' : 'success'" effect="plain">
              {{ isDynamicLangGraphReplay ? "受控 LangGraph" : "模板执行" }}
            </el-tag>
          </div>
        </template>
        <div class="runtime-summary-grid">
          <div>
            <span>真实执行</span>
            <strong>{{ runtimeSummary.nodeCounts.executed || 0 }}</strong>
          </div>
          <div>
            <span>平台模拟</span>
            <strong>{{ runtimeSummary.nodeCounts.simulated || 0 }}</strong>
          </div>
          <div>
            <span>等待确认</span>
            <strong>{{ runtimeSummary.nodeCounts.waiting || 0 }}</strong>
          </div>
          <div>
            <span>报告路径</span>
            <strong>{{ runtimeSummary.reportPath || "未生成" }}</strong>
          </div>
          <div>
            <span>审计日志</span>
            <strong>{{ runtimeSummary.codeAgent.auditPath || "无" }}</strong>
          </div>
          <div>
            <span>CodeAgent 写入</span>
            <strong>{{ runtimeSummary.codeAgent.actualWrites ?? 0 }}</strong>
          </div>
        </div>
        <div v-if="runtimeSummary.connectionMappings.length" class="runtime-mapping-strip">
          <strong>字段级数据流</strong>
          <span
            v-for="(mapping, index) in runtimeSummary.connectionMappings.slice(0, 6)"
            :key="`${mapping.fromNodeId}-${mapping.fromOutputField}-${mapping.toNodeId}-${mapping.toInputField}-${index}`"
            class="runtime-mapping-pill"
            :style="{ '--mapping-color': String(mapping.color || '#64748b') }"
          >
            {{ mapping.fromNodeName }}.{{ mapping.fromOutputField }} → {{ mapping.toNodeName }}.{{ mapping.toInputField }}
          </span>
          <em v-if="runtimeSummary.connectionMappings.length > 6">+{{ runtimeSummary.connectionMappings.length - 6 }}</em>
        </div>
      </el-card>

      <el-card shadow="never" class="replay-filter-card">
        <div class="filter-row">
          <div class="filter-title">
            <strong>事件筛选</strong>
            <span>CodeAgent {{ codeAgentEventCount }} · 异常 {{ failedEventCount }}</span>
          </div>
          <el-select v-model="filters.agent" class="filter-select">
            <el-option v-for="option in agentOptions" :key="option.value" :label="option.label" :value="option.value" />
          </el-select>
          <el-select v-model="filters.status" class="filter-select">
            <el-option v-for="option in statusOptions" :key="option.value" :label="option.label" :value="option.value" />
          </el-select>
          <el-input
            v-model="filters.keyword"
            class="filter-keyword"
            :prefix-icon="Search"
            clearable
            placeholder="搜索 eventText / message / detailJson"
          />
          <el-button type="warning" plain @click="showCodeAgentOnly">只看 CodeAgent</el-button>
          <el-button text @click="resetFilters">重置</el-button>
        </div>
      </el-card>

      <el-card v-if="waitingForHuman" shadow="never" class="approval-card">
        <div class="approval-copy">
          <strong>等待人工确认</strong>
          <span>该任务包含 Human Approval 节点。确认结果会写入 RunEvent，并进入 SSE / Replay 事件链。</span>
        </div>
        <el-input
          v-model="approvalComment"
          type="textarea"
          :rows="2"
          placeholder="可选：输入确认说明或拒绝原因"
        />
        <div class="approval-actions">
          <el-button type="success" :loading="approving" @click="submitApproval(true)">批准继续</el-button>
          <el-button type="danger" plain :loading="approving" @click="submitApproval(false)">拒绝停止</el-button>
        </div>
      </el-card>

      <ReplayControlPanel
        :current-index="Math.max(currentIndex, 0)"
        :total="events.length"
        :playing="playing"
        :speed-ms="speedMs"
        @previous="previousStep"
        @next="nextStep"
        @play="playReplay"
        @pause="pauseReplay"
        @reset="resetReplay"
        @update:speed-ms="(value) => (speedMs = value)"
      />

      <el-row :gutter="16" align="top">
        <el-col :lg="15" :md="24">
          <section class="panel replay-main-panel" v-loading="loading">
            <div class="panel-title">事件回放时间线（{{ events.length }} 条）</div>
            <WorkflowReplayTimeline :events="events" :current-index="currentIndex" />
          </section>
        </el-col>
        <el-col :lg="9" :md="24">
          <section class="panel current-event-panel">
            <div class="panel-title">当前播放事件</div>
            <ReplayEventCard v-if="currentEvent" :event="currentEvent" active />
            <el-empty v-else description="暂无当前事件" />
          </section>
          <section class="panel replay-artifact-panel">
            <div class="panel-title">Replay Artifacts</div>
            <div class="artifact-list">
              <router-link class="artifact-link" :to="`/replay/${replay.platformRunId}`">
                <strong>Replay</strong>
                <span>{{ replay.platformRunId }}</span>
              </router-link>
              <router-link v-if="runtimeSummary.reportPath" class="artifact-link" to="/reports">
                <strong>Report</strong>
                <span>{{ runtimeSummary.reportPath }}</span>
              </router-link>
              <div v-if="runtimeSummary.codeAgent.auditPath" class="artifact-link static">
                <strong>Audit</strong>
                <span>{{ runtimeSummary.codeAgent.auditPath }}</span>
              </div>
              <div v-if="runtimeSummary.connectionMappings.length" class="artifact-link static">
                <strong>Field mapping</strong>
                <span>{{ runtimeSummary.connectionMappings.length }} links</span>
              </div>
            </div>
          </section>
        </el-col>
      </el-row>
    </template>

    <el-empty v-else-if="!loading && !errorDetail" description="暂无回放数据" />
  </section>
</template>

<style scoped>
.replay-page {
  gap: 14px;
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.replay-summary-card :deep(.el-card__body) {
  padding: 14px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
}

.summary-grid div {
  display: grid;
  gap: 5px;
  min-width: 0;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 14px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.014)),
    #17191f;
}

.summary-grid span {
  color: var(--codex-muted);
  font-size: 12px;
}

.summary-grid strong {
  overflow-wrap: anywhere;
  color: var(--codex-text);
  font-size: 14px;
}

.requirement-block {
  margin-top: 12px;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 14px;
  background: #17191f;
  color: #d4d4d8;
  line-height: 1.55;
}

.runtime-summary-card :deep(.el-card__body) {
  padding: 12px;
}

.runtime-summary-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.runtime-summary-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
}

.runtime-summary-grid div {
  display: grid;
  gap: 5px;
  min-width: 0;
  padding: 10px;
  border: 1px solid rgba(77, 163, 255, 0.22);
  border-radius: 14px;
  background:
    radial-gradient(circle at 100% 0%, rgba(77, 163, 255, 0.12), transparent 38%),
    #17191f;
}

.runtime-summary-grid span {
  color: #9bd4ff;
  font-size: 12px;
  font-weight: 700;
}

.runtime-summary-grid strong {
  overflow-wrap: anywhere;
  color: var(--codex-text);
  font-size: 14px;
}

.runtime-mapping-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #dbeafe;
}

.runtime-mapping-strip strong {
  color: #1d4ed8;
  font-size: 12px;
}

.runtime-mapping-pill {
  max-width: 100%;
  overflow: hidden;
  padding: 5px 9px;
  border: 1px solid color-mix(in srgb, var(--mapping-color) 32%, #17191f);
  border-left: 4px solid var(--mapping-color);
  border-radius: 999px;
  background: color-mix(in srgb, var(--mapping-color) 8%, #17191f);
  color: #334155;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 11px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.runtime-mapping-strip em {
  color: #64748b;
  font-size: 12px;
  font-style: normal;
  font-weight: 800;
}

.replay-filter-card :deep(.el-card__body) {
  padding: 12px;
}

.approval-card :deep(.el-card__body) {
  display: grid;
  gap: 10px;
  padding: 12px;
}

.approval-copy {
  display: grid;
  gap: 3px;
}

.approval-copy strong {
  color: #92400e;
}

.approval-copy span {
  color: #64748b;
  font-size: 12px;
}

.approval-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.approval-actions :deep(.el-button) {
  margin-left: 0;
}

.filter-row {
  display: grid;
  grid-template-columns: auto 150px 140px minmax(220px, 1fr) auto auto;
  gap: 10px;
  align-items: center;
}

.filter-title {
  display: grid;
  gap: 2px;
  min-width: 150px;
}

.filter-title strong {
  color: var(--codex-text);
}

.filter-title span {
  color: var(--codex-muted);
  font-size: 12px;
}

.filter-select,
.filter-keyword {
  width: 100%;
}

.replay-main-panel,
.current-event-panel {
  min-height: 520px;
}

.replay-artifact-panel {
  margin-top: 16px;
}

.artifact-list {
  display: grid;
  gap: 8px;
}

.artifact-link {
  display: grid;
  gap: 3px;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 12px;
  background: #17191f;
}

.artifact-link strong {
  color: #1a73e8;
}

.artifact-link span {
  overflow: hidden;
  color: #5f6368;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.artifact-link.static strong {
  color: #202124;
}

@media (max-width: 1280px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .runtime-summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .filter-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .filter-row {
    grid-template-columns: 1fr;
  }
}
</style>
