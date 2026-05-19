<script setup lang="ts">
import { Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import AgentOutputTabs from "@/components/AgentOutputTabs.vue";
import ReportPreview from "@/components/ReportPreview.vue";
import ResultOverview from "@/components/ResultOverview.vue";
import SummaryCards from "@/components/SummaryCards.vue";
import WorkflowTimeline from "@/components/WorkflowTimeline.vue";
import { currentApiMode, getApiDisconnectedHint, getConfigSourceLabel, getDataModeLabel } from "@/api/client";
import { getRunEvents } from "@/api/events";
import { subscribeRunEvents, type RunEventSubscription } from "@/api/eventStream";
import {
  getPlatformRunDetail,
  getPlatformRuns,
  getRun,
  getRuns,
  platformRunToHistoryItem,
  platformRunToRunResponse,
} from "@/api/runs";
import type { PlatformRunRecord } from "@/types/platformRun";
import type { RunHistoryItem, RunResponse } from "@/types/run";
import type { RunEvent } from "@/types/runEvent";
import { isWorkflowTemplateRun, runKindLabel, runKindTagType } from "@/utils/runKind";

const runs = ref<RunHistoryItem[]>([]);
const platformRuns = ref<PlatformRunRecord[]>([]);
const selectedRun = ref<RunResponse | null>(null);
const selectedPlatformRun = ref<PlatformRunRecord | null>(null);
const selectedEvents = ref<RunEvent[]>([]);
const selectedRunId = ref("");
const loading = ref(false);
const detailLoading = ref(false);
const eventsLoading = ref(false);
const eventStreaming = ref(false);
const eventStreamConnected = ref(false);
const eventStreamError = ref("");
const keyword = ref("");
const statusFilter = ref("all");
const modelFilter = ref("all");
const route = useRoute();
const router = useRouter();
const isJavaMode = currentApiMode === "java";
const dataModeLabel = getDataModeLabel();
const dataSourceLabel = getConfigSourceLabel();
const selectedRawResponseText = computed(() => {
  const rawResponse = selectedPlatformRun.value?.rawResponse;

  if (!rawResponse) {
    return "";
  }

  return typeof rawResponse === "string" ? rawResponse : JSON.stringify(rawResponse, null, 2);
});
const selectedRunSummaryJson = computed(() => selectedPlatformRun.value?.runSummaryJson || "");
const selectedUIViewModelJson = computed(() => selectedPlatformRun.value?.uiViewModelJson || "");
const selectedPluginResultsJson = computed(() => selectedPlatformRun.value?.pluginResultsJson || "");
const selectedPlatformRunId = computed(() => selectedPlatformRun.value?.platformRunId || "");
const selectedRunEnded = computed(() => {
  const status = selectedPlatformRun.value?.status;
  return status === "SUCCESS" || status === "FAILED" || status === "CANCELLED";
});
const selectedIsTemplateReplay = computed(() => isWorkflowTemplateRun(selectedPlatformRun.value || selectedRun.value?.run_summary));
let eventSubscription: RunEventSubscription | null = null;

const modelOptions = computed(() => {
  const providers = new Set(runs.value.map((run) => run.model_provider).filter(Boolean));
  return [...providers].sort();
});

const filteredRuns = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase();

  return runs.value
    .filter((run) => {
      if (statusFilter.value === "success" && !run.success) {
        return false;
      }

      if (statusFilter.value === "failed" && run.success) {
        return false;
      }

      if (modelFilter.value !== "all" && run.model_provider !== modelFilter.value) {
        return false;
      }

      if (!normalizedKeyword) {
        return true;
      }

      return `${run.requirement} ${run.run_id} ${run.report_path}`.toLowerCase().includes(normalizedKeyword);
    })
    .sort((left, right) => (right.created_at || "").localeCompare(left.created_at || ""));
});

function shortRequirement(requirement: string) {
  if (!requirement) {
    return "无需求摘要";
  }

  return requirement.length > 72 ? `${requirement.slice(0, 72)}...` : requirement;
}

function retryType(retryCount: number) {
  return retryCount > 0 ? "warning" : "info";
}

function qualityType(qualityScore: number) {
  if (qualityScore >= 85) {
    return "success";
  }

  if (qualityScore >= 60) {
    return "warning";
  }

  return "danger";
}

function eventTagType(eventType: string) {
  if (eventType === "RUN_SUCCESS" || eventType === "REPORT_INDEXED") {
    return "success";
  }

  if (eventType === "RUN_FAILED" || eventType === "ERROR_OCCURRED") {
    return "danger";
  }

  if (eventType === "RUN_CANCELLED") {
    return "warning";
  }

  if (eventType === "RUN_STARTED" || eventType === "PYTHON_REQUEST_SENT" || eventType === "PYTHON_RESPONSE_RECEIVED") {
    return "primary";
  }

  return "info";
}

function agentLabel(agent?: string) {
  const labels: Record<string, string> = {
    product: "Product",
    coder: "Coder",
    tester: "Tester",
    sentry: "Sentry",
    runner: "Runner",
    quality: "Quality",
    report: "Report",
    workflow: "Workflow",
  };

  return labels[agent || ""] || agent || "";
}

function agentTagType(agent?: string) {
  const types: Record<string, string> = {
    product: "primary",
    coder: "success",
    tester: "warning",
    sentry: "danger",
    runner: "info",
    quality: "success",
    report: "primary",
    workflow: "info",
  };

  return types[agent || ""] || "info";
}

async function loadRunEvents(platformRunId: string) {
  if (!isJavaMode || !platformRunId) {
    selectedEvents.value = [];
    return;
  }

  eventsLoading.value = true;

  try {
    selectedEvents.value = await getRunEvents(platformRunId);
  } catch (error) {
    selectedEvents.value = [];
    ElMessage.warning(error instanceof Error ? error.message : "加载任务事件失败");
  } finally {
    eventsLoading.value = false;
  }
}

function isTerminalEvent(event: RunEvent) {
  return event.eventType === "RUN_SUCCESS" || event.eventType === "RUN_FAILED" || event.eventType === "RUN_CANCELLED";
}

function appendRunEvent(event: RunEvent) {
  const existingIndex = selectedEvents.value.findIndex((item) => item.id === event.id && item.id > 0);

  if (existingIndex >= 0) {
    selectedEvents.value.splice(existingIndex, 1, event);
  } else {
    selectedEvents.value.push(event);
  }

  selectedEvents.value.sort((left, right) => (left.createdAt || "").localeCompare(right.createdAt || ""));
}

function stopEventStream() {
  eventSubscription?.close();
  eventSubscription = null;
  eventStreaming.value = false;
  eventStreamConnected.value = false;
}

function startEventStream() {
  const platformRunId = selectedPlatformRunId.value;

  if (!isJavaMode || !platformRunId) {
    return;
  }

  if (selectedRunEnded.value) {
    ElMessage.info("任务已结束，可查看历史事件");
    return;
  }

  stopEventStream();
  eventStreamError.value = "";
  eventStreaming.value = true;

  eventSubscription = subscribeRunEvents(
    platformRunId,
    (event) => {
      appendRunEvent(event);
      if (isTerminalEvent(event)) {
        stopEventStream();
      }
    },
    (error) => {
      eventStreamError.value = error.message;
      stopEventStream();
      loadRunEvents(platformRunId);
      ElMessage.warning(`${error.message}，已回退查询历史事件`);
    },
    () => {
      eventStreamConnected.value = true;
    },
  );

  if (!eventSubscription.supported) {
    eventStreaming.value = false;
    loadRunEvents(platformRunId);
  }
}

async function loadRuns() {
  loading.value = true;

  try {
    if (isJavaMode) {
      platformRuns.value = await getPlatformRuns();
      runs.value = platformRuns.value.map(platformRunToHistoryItem);
    } else {
      platformRuns.value = [];
      runs.value = await getRuns();
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : `${getApiDisconnectedHint()}，加载历史记录失败`);
  } finally {
    loading.value = false;
  }
}

async function openRun(run: RunHistoryItem) {
  if (!run.run_id) {
    ElMessage.warning("该历史记录缺少 run_id");
    return;
  }

  selectedRunId.value = run.run_id;
  detailLoading.value = true;
  stopEventStream();
  eventStreamError.value = "";

  try {
    if (isJavaMode) {
      const platformRunId = run.platform_run_id || run.run_id;
      selectedPlatformRun.value = await getPlatformRunDetail(platformRunId);
      selectedRun.value = platformRunToRunResponse(selectedPlatformRun.value);
      await loadRunEvents(platformRunId);
    } else {
      selectedPlatformRun.value = null;
      selectedEvents.value = [];
      selectedRun.value = await getRun(run.run_id);
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : `${getApiDisconnectedHint()}，加载运行详情失败`);
  } finally {
    detailLoading.value = false;
  }
}

function openReplay(run: RunHistoryItem) {
  const platformRunId = run.platform_run_id || run.run_id;

  if (!isJavaMode) {
    ElMessage.info("工作流回放仅 Java Gateway + MySQL 模式支持");
    return;
  }

  if (!platformRunId) {
    ElMessage.warning("该历史记录缺少 platformRunId");
    return;
  }

  router.push(`/replay/${platformRunId}`);
}

onMounted(async () => {
  await loadRuns();

  const queryRunId = typeof route.query.run_id === "string" ? route.query.run_id : "";

  if (queryRunId) {
    const matchedRun = runs.value.find((run) => run.run_id === queryRunId || run.python_run_id === queryRunId);

    if (matchedRun) {
      openRun(matchedRun);
    }
  }
});

onBeforeUnmount(() => {
  stopEventStream();
});
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <h1>RunHistory</h1>
        <p>查看历史运行记录，并加载某次运行的完整 ui_view_model 详情</p>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="loadRuns">刷新</el-button>
    </div>

    <div class="mode-tags">
      <el-tag type="warning" effect="plain">当前数据模式：{{ dataModeLabel }}</el-tag>
      <el-tag type="primary" effect="plain">当前数据来源：{{ dataSourceLabel }}</el-tag>
    </div>

    <el-row :gutter="16" align="top">
      <el-col :lg="10" :md="24">
        <section class="panel history-panel">
          <div class="history-filters">
            <el-input v-model="keyword" :prefix-icon="Search" clearable placeholder="搜索 requirement / run_id" />
            <el-select v-model="statusFilter" class="filter-select">
              <el-option label="全部状态" value="all" />
              <el-option label="成功" value="success" />
              <el-option label="失败" value="failed" />
            </el-select>
            <el-select v-model="modelFilter" class="filter-select">
              <el-option label="全部模型" value="all" />
              <el-option v-for="provider in modelOptions" :key="provider" :label="provider" :value="provider" />
            </el-select>
          </div>

          <el-empty v-if="!loading && !filteredRuns.length" description="暂无历史记录" />
          <div v-else class="history-list" v-loading="loading">
            <article
              v-for="run in filteredRuns"
              :key="run.run_id"
              class="history-item"
              :class="{ active: selectedRunId === run.run_id }"
              @click="openRun(run)"
            >
              <div class="history-item-head">
                <span class="run-id">{{ run.platform_run_id || run.run_id }}</span>
                <el-tag :type="run.success ? 'success' : 'danger'" effect="plain" size="small">
                  {{ run.success ? "成功" : "失败" }}
                </el-tag>
              </div>
              <div class="run-kind-row">
                <el-tag :type="runKindTagType(run)" effect="plain" size="small">{{ runKindLabel(run) }}</el-tag>
                <el-tag v-if="isWorkflowTemplateRun(run)" type="primary" effect="plain" size="small">
                  不执行 LangGraph
                </el-tag>
              </div>
              <div v-if="run.python_run_id" class="python-run-id">Python run：{{ run.python_run_id }}</div>
              <div class="requirement-text">{{ shortRequirement(run.requirement) }}</div>
              <div class="history-meta">
                <el-tag size="small" effect="plain">{{ run.model_provider || "model" }}</el-tag>
                <el-tag :type="retryType(run.retry_count)" size="small" effect="plain">
                  修复 {{ run.retry_count }}
                </el-tag>
                <el-tag :type="run.test_success ? 'success' : 'danger'" size="small" effect="plain">
                  pytest {{ run.test_success ? "通过" : "未过" }}
                </el-tag>
                <el-tag :type="qualityType(run.quality_score)" size="small" effect="plain">
                  质量 {{ run.quality_score }}
                </el-tag>
              </div>
              <div class="history-submeta">
                <span>{{ run.created_at || "未记录时间" }}</span>
                <span>{{ run.coverage_percent }}%</span>
              </div>
              <div class="report-path">{{ run.report_path || "暂无报告路径" }}</div>
              <div v-if="isJavaMode" class="history-actions">
                <el-button size="small" type="primary" plain @click.stop="openReplay(run)">回放工作流</el-button>
              </div>
            </article>
          </div>
        </section>
      </el-col>

      <el-col :lg="14" :md="24">
        <section class="panel detail-panel" v-loading="detailLoading">
          <template v-if="selectedRun">
            <div class="panel-title">
              {{ isJavaMode ? "Java 平台详情" : "历史详情" }}：{{ selectedPlatformRun?.platformRunId || selectedRun.run_id }}
            </div>
            <el-alert
              v-if="isJavaMode"
              :title="selectedPlatformRun?.rawResponse ? '已读取 Java MySQL 记录，并解析 rawResponse 展示详情' : '该平台记录缺少 rawResponse，已使用摘要字段兼容展示'"
              type="info"
              show-icon
              :closable="false"
              class="detail-source-alert"
            />
            <el-alert
              v-if="selectedIsTemplateReplay"
              title="这是 Workflow 模板回放任务：由 Java/MySQL 模板生成运行记录和事件，用于演示与复盘，不执行 LangGraph、不调用模型。"
              type="info"
              show-icon
              :closable="false"
              class="detail-source-alert"
            />
            <div v-if="isJavaMode" class="event-title-row">
              <div>
                <div class="subsection-title">事件时间线</div>
                <div class="event-stream-status">
                  {{ eventStreaming ? "正在订阅实时事件" : "展示历史事件，可手动订阅实时更新" }}
                </div>
              </div>
              <div class="event-stream-actions">
                <el-tag :type="eventStreamConnected ? 'success' : 'info'" effect="plain">
                  {{ eventStreamConnected ? "SSE 已连接" : "SSE 未连接" }}
                </el-tag>
                <el-button size="small" type="primary" :disabled="eventStreaming || selectedRunEnded" @click="startEventStream">
                  订阅实时事件
                </el-button>
                <el-button size="small" :disabled="!eventStreaming" @click="stopEventStream">停止订阅</el-button>
              </div>
            </div>
            <section v-if="isJavaMode" class="event-timeline-panel" v-loading="eventsLoading">
              <el-alert
                v-if="eventStreamError"
                :title="`${eventStreamError}，已回退查询历史事件`"
                type="warning"
                show-icon
                :closable="false"
                class="detail-source-alert"
              />
              <el-empty v-if="!selectedEvents.length && !eventsLoading" description="暂无任务事件" />
              <el-timeline v-else>
                <el-timeline-item
                  v-for="event in selectedEvents"
                  :key="event.id"
                  :timestamp="event.createdAt"
                  placement="top"
                >
                  <div class="event-timeline-item">
                    <div class="event-line-head">
                      <el-tag v-if="event.agent" :type="agentTagType(event.agent)" effect="plain" size="small">
                        {{ agentLabel(event.agent) }}
                      </el-tag>
                      <el-tag :type="eventTagType(event.eventType)" effect="plain" size="small">
                        {{ event.eventText || event.eventType }}
                      </el-tag>
                      <el-tag effect="plain" size="small">{{ event.status || "UNKNOWN" }}</el-tag>
                    </div>
                    <div class="event-message">{{ event.message || "无事件描述" }}</div>
                    <div v-if="event.pythonRunId" class="event-python-run">Python run：{{ event.pythonRunId }}</div>
                    <el-collapse v-if="event.detailJson && event.detailJson !== '{}'" class="event-detail-collapse">
                      <el-collapse-item title="detailJson" :name="`event-${event.id}`">
                        <pre class="raw-response-block">{{ event.detailJson }}</pre>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </section>
            <div v-if="isJavaMode && selectedPlatformRun" class="enhanced-field-grid">
              <el-tag effect="plain">modelName：{{ selectedPlatformRun.modelName || "未记录" }}</el-tag>
              <el-tag effect="plain">modelBaseUrl：{{ selectedPlatformRun.modelBaseUrl || "未记录" }}</el-tag>
              <el-tag :type="selectedPlatformRun.testSuccess ? 'success' : 'danger'" effect="plain">
                testSuccess：{{ selectedPlatformRun.testSuccess ? "true" : "false" }}
              </el-tag>
              <el-tag effect="plain">coverage：{{ selectedPlatformRun.coveragePercent || 0 }}%</el-tag>
              <el-tag effect="plain">security：{{ selectedPlatformRun.securityStatus || "未记录" }}</el-tag>
              <el-tag :type="selectedPlatformRun.approved ? 'success' : 'info'" effect="plain">
                approved：{{ selectedPlatformRun.approved ? "true" : "false" }}
              </el-tag>
              <el-tag :type="selectedPlatformRun.requireHumanApproval ? 'warning' : 'info'" effect="plain">
                humanApproval：{{ selectedPlatformRun.requireHumanApproval ? "true" : "false" }}
              </el-tag>
            </div>
            <el-alert
              v-if="isJavaMode && selectedPlatformRun?.errorSummary"
              :title="selectedPlatformRun.errorSummary"
              type="warning"
              show-icon
              :closable="false"
              class="detail-source-alert"
            />
            <el-collapse
              v-if="isJavaMode && (selectedRunSummaryJson || selectedUIViewModelJson || selectedPluginResultsJson)"
              class="raw-response-collapse"
            >
              <el-collapse-item v-if="selectedRunSummaryJson" title="runSummaryJson" name="run-summary-json">
                <pre class="raw-response-block">{{ selectedRunSummaryJson }}</pre>
              </el-collapse-item>
              <el-collapse-item v-if="selectedUIViewModelJson" title="uiViewModelJson" name="ui-view-model-json">
                <pre class="raw-response-block">{{ selectedUIViewModelJson }}</pre>
              </el-collapse-item>
              <el-collapse-item v-if="selectedPluginResultsJson" title="pluginResultsJson" name="plugin-results-json">
                <pre class="raw-response-block">{{ selectedPluginResultsJson }}</pre>
              </el-collapse-item>
            </el-collapse>
            <el-collapse v-if="isJavaMode && selectedRawResponseText" class="raw-response-collapse">
              <el-collapse-item title="Java rawResponse" name="raw-response">
                <pre class="raw-response-block">{{ selectedRawResponseText }}</pre>
              </el-collapse-item>
            </el-collapse>
            <SummaryCards :summary="selectedRun.run_summary" />
            <div class="subsection-title">Agent 工作流节点</div>
            <WorkflowTimeline
              :workflow-steps="selectedRun.ui_view_model?.workflow_steps"
              :workflow-events="selectedRun.ui_view_model?.workflow_events"
            />
            <div class="subsection-title">最终结果总览</div>
            <ResultOverview :response="selectedRun" />
            <div class="subsection-title">Agent 输出详情</div>
            <AgentOutputTabs :response="selectedRun" />
            <div class="subsection-title">报告入口</div>
            <ReportPreview :report="selectedRun.ui_view_model?.report" />
          </template>
          <el-empty v-else description="点击左侧历史记录查看详情" />
        </section>
      </el-col>
    </el-row>
  </section>
</template>

<style scoped>
.history-panel,
.detail-panel {
  min-height: calc(100vh - 150px);
}

.mode-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.history-filters {
  display: grid;
  grid-template-columns: 1fr 120px 130px;
  gap: 10px;
  margin-bottom: 12px;
}

.history-list {
  display: grid;
  gap: 10px;
  max-height: calc(100vh - 240px);
  overflow: auto;
  padding-right: 4px;
}

.history-item {
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #ffffff;
  cursor: pointer;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}

.history-item:hover,
.history-item.active {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.history-item-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.run-id {
  color: #0f172a;
  font-family: "Cascadia Code", Consolas, monospace;
  font-weight: 800;
}

.python-run-id {
  margin-top: 5px;
  color: #64748b;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.requirement-text {
  margin-top: 8px;
  color: #334155;
  line-height: 1.55;
}

.history-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.run-kind-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.history-submeta {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  color: #64748b;
  font-size: 12px;
}

.report-path {
  margin-top: 8px;
  overflow-wrap: anywhere;
  color: #64748b;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.history-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.detail-source-alert {
  margin-bottom: 12px;
}

.enhanced-field-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.raw-response-collapse {
  margin-bottom: 12px;
}

.event-title-row,
.event-stream-actions {
  display: flex;
  align-items: center;
}

.event-title-row {
  justify-content: space-between;
  gap: 12px;
  margin-top: 12px;
}

.event-stream-status {
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
}

.event-stream-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.event-timeline-panel {
  margin-bottom: 14px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #ffffff;
}

.event-timeline-item {
  display: grid;
  gap: 8px;
}

.event-line-head {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.event-message {
  color: #334155;
  line-height: 1.5;
}

.event-python-run {
  color: #64748b;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.event-detail-collapse {
  max-width: 100%;
}

.raw-response-block {
  max-height: 360px;
  margin: 0;
  overflow: auto;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  color: #0f172a;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

@media (max-width: 1280px) {
  .history-filters {
    grid-template-columns: 1fr;
  }

  .history-list {
    max-height: 520px;
  }
}
</style>
