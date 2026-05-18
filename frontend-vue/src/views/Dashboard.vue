<script setup lang="ts">
import { Refresh } from "@element-plus/icons-vue";
import { computed, onMounted, reactive, ref } from "vue";

import {
  currentApiBaseUrl,
  currentApiMode,
  getApiDisconnectedHint,
  getApiModeLabel,
  getConfigSourceLabel,
  getDataModeLabel,
  getHealth,
} from "@/api/client";
import { getRecentEvents } from "@/api/events";
import { getModels } from "@/api/models";
import { getPlatformStats } from "@/api/platform";
import { getPlugins } from "@/api/plugins";
import { getReports } from "@/api/reports";
import { getPlatformRuns, getRuns, platformRunToHistoryItem } from "@/api/runs";
import DashboardStats from "@/components/DashboardStats.vue";
import ModelStatusPanel from "@/components/ModelStatusPanel.vue";
import PluginStatusPanel from "@/components/PluginStatusPanel.vue";
import QuickActions from "@/components/QuickActions.vue";
import RecentReports from "@/components/RecentReports.vue";
import RecentRuns from "@/components/RecentRuns.vue";
import { useSettingsStore } from "@/stores/settings";
import type { HealthResponse, ModelConfig, PluginConfig } from "@/types/api";
import type { PlatformRunRecord, PlatformStats } from "@/types/platformRun";
import type { ReportItem, RunHistoryItem } from "@/types/run";
import type { RunEvent } from "@/types/runEvent";

const settingsStore = useSettingsStore();
const apiModeLabel = getApiModeLabel();
const apiBaseUrl = currentApiBaseUrl;
const isJavaMode = currentApiMode === "java";
const dataModeLabel = getDataModeLabel();
const dataSourceLabel = getConfigSourceLabel();

const health = ref<HealthResponse | null>(null);
const runs = ref<RunHistoryItem[]>([]);
const reports = ref<ReportItem[]>([]);
const models = ref<ModelConfig[]>([]);
const plugins = ref<PluginConfig[]>([]);
const platformRuns = ref<PlatformRunRecord[]>([]);
const platformStats = ref<PlatformStats | null>(null);
const recentEvents = ref<RunEvent[]>([]);

const loading = reactive({
  health: false,
  runs: false,
  reports: false,
  models: false,
  plugins: false,
  platformRuns: false,
  platformStats: false,
  events: false,
});

const errors = reactive({
  health: "",
  runs: "",
  reports: "",
  models: "",
  plugins: "",
  platformRuns: "",
  platformStats: "",
  events: "",
});

const refreshLoading = computed(() => Object.values(loading).some(Boolean));
const runLoading = computed(() => loading.runs || loading.platformRuns);
const runError = computed(() => errors.runs || errors.platformRuns);

const sortedRuns = computed(() =>
  [...runs.value].sort((left, right) => (right.created_at || "").localeCompare(left.created_at || "")),
);

const sortedReports = computed(() =>
  [...reports.value].sort((left, right) => (right.created_at || "").localeCompare(left.created_at || "")),
);

const latestRun = computed(() => sortedRuns.value[0] || null);
const latestReport = computed(() => sortedReports.value[0] || null);

const successRuns = computed(() => runs.value.filter((run) => run.success).length);
const failedRuns = computed(() => runs.value.length - successRuns.value);
const averageQualityScore = computed(() => {
  if (!runs.value.length) {
    return 0;
  }

  const total = runs.value.reduce((sum, run) => sum + Number(run.quality_score || 0), 0);
  return Math.round((total / runs.value.length) * 10) / 10;
});
const dashboardTotalRuns = computed(() => (isJavaMode && platformStats.value ? platformStats.value.totalRuns : runs.value.length));
const dashboardSuccessRuns = computed(() => (isJavaMode && platformStats.value ? platformStats.value.successRuns : successRuns.value));
const dashboardFailedRuns = computed(() => (isJavaMode && platformStats.value ? platformStats.value.failedRuns : failedRuns.value));
const dashboardAverageQualityScore = computed(() =>
  isJavaMode && platformStats.value ? platformStats.value.averageQualityScore : averageQualityScore.value,
);

const recentRuns = computed(() => sortedRuns.value.slice(0, 5));
const recentReports = computed(() => sortedReports.value.slice(0, 5));
const recentPlatformRuns = computed(() => platformRuns.value.slice(0, 5));
const recentPlatformEvents = computed(() => recentEvents.value.slice(0, 10));

const apiConnected = computed(() => health.value?.status === "ok" && !errors.health);
const apiStatusLabel = computed(() => {
  if (loading.health && !health.value && !errors.health) {
    return "API 检测中";
  }

  return apiConnected.value ? "API 已连接" : "API 未连接";
});
const apiStatusType = computed(() => {
  if (loading.health && !health.value && !errors.health) {
    return "info";
  }

  return apiConnected.value ? "success" : "danger";
});

function errorMessage(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback;
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

async function loadSection<T>(
  key: keyof typeof loading,
  request: () => Promise<T>,
  assign: (data: T) => void,
  fallback: string,
) {
  loading[key] = true;
  errors[key] = "";

  try {
    assign(await request());
  } catch (error) {
    errors[key] = errorMessage(error, fallback);
  } finally {
    loading[key] = false;
  }
}

async function loadDashboard() {
  const requests = [
    settingsStore.loadSettings(),
    loadSection("health", getHealth, (data) => {
      health.value = data;
    }, "API 健康检查失败"),
    loadSection("reports", getReports, (data) => {
      reports.value = data;
    }, "加载报告列表失败"),
    loadSection("models", getModels, (data) => {
      models.value = data;
    }, "加载模型状态失败"),
    loadSection("plugins", getPlugins, (data) => {
      plugins.value = data;
    }, "加载插件状态失败"),
  ];

  if (isJavaMode) {
    requests.push(
      loadSection("platformRuns", getPlatformRuns, (data) => {
        platformRuns.value = data;
        runs.value = data.map(platformRunToHistoryItem);
      }, "加载 Java MySQL 平台运行记录失败"),
      loadSection("platformStats", getPlatformStats, (data) => {
        platformStats.value = data;
      }, "加载 Java MySQL 平台统计失败"),
      loadSection("events", () => getRecentEvents(10), (data) => {
        recentEvents.value = data;
      }, "加载最近平台事件失败"),
    );
  } else {
    requests.push(
      loadSection("runs", getRuns, (data) => {
        platformRuns.value = [];
        runs.value = data;
      }, "加载运行历史失败"),
    );
  }

  await Promise.allSettled(requests);
}

async function refreshRecentEvents() {
  if (!isJavaMode) {
    return;
  }

  await loadSection("events", () => getRecentEvents(10), (data) => {
    recentEvents.value = data;
  }, "加载最近平台事件失败");
}

onMounted(() => {
  loadDashboard();
});
</script>

<template>
  <section class="page-stack dashboard-page">
    <div class="dashboard-hero">
      <div>
        <h1>AI Multi-Agent Pipeline</h1>
        <p>基于多智能体协作的自主开发流水线</p>
        <div class="hero-meta">
          <el-tag :type="apiStatusType" effect="plain">{{ apiStatusLabel }}</el-tag>
          <el-tag type="warning" effect="plain">API 模式 {{ apiModeLabel }}</el-tag>
          <el-tag type="warning" effect="plain">数据模式 {{ dataModeLabel }}</el-tag>
          <el-tag type="primary" effect="plain">数据来源 {{ dataSourceLabel }}</el-tag>
          <el-tag type="primary" effect="plain">默认模型 {{ settingsStore.selectedModelProvider || "未选择" }}</el-tag>
          <el-tag type="success" effect="plain">启用插件 {{ settingsStore.enabledPlugins.length }}</el-tag>
          <el-tag effect="plain">Demo {{ settingsStore.demoMode ? "开启" : "关闭" }}</el-tag>
          <el-tag effect="plain">最大修复 {{ settingsStore.maxRetryCount }}</el-tag>
        </div>
      </div>
      <div class="hero-actions">
        <div class="api-mode-line">{{ currentApiMode === "java" ? "通过 Java 平台服务代理" : "直连 Python Agent Engine" }}</div>
        <div class="api-base">{{ apiBaseUrl }}</div>
        <el-button :icon="Refresh" :loading="refreshLoading" @click="loadDashboard">刷新</el-button>
      </div>
    </div>

    <el-alert
      v-if="errors.health"
      :title="getApiDisconnectedHint()"
      :description="errors.health"
      type="error"
      show-icon
      :closable="false"
    />

    <DashboardStats
      :total-runs="dashboardTotalRuns"
      :success-runs="dashboardSuccessRuns"
      :failed-runs="dashboardFailedRuns"
      :average-quality-score="dashboardAverageQualityScore"
      :latest-run="latestRun"
      :latest-report="latestReport"
    />

    <el-card v-if="isJavaMode" shadow="never" class="platform-record-card" v-loading="loading.platformRuns || loading.platformStats">
      <template #header>
        <div class="platform-record-head">
          <span>Java 平台记录</span>
          <div class="platform-record-tags">
            <el-tag type="primary" effect="plain">MySQL 运行记录 {{ platformRuns.length }}</el-tag>
            <el-tag type="primary" effect="plain">MySQL 报告索引 {{ platformStats?.totalReports ?? reports.length }}</el-tag>
            <el-tag type="success" effect="plain">测试通过 {{ platformStats?.testSuccessRuns ?? 0 }}</el-tag>
            <el-tag type="warning" effect="plain">自动修复 {{ platformStats?.repairedRuns ?? 0 }}</el-tag>
            <el-tag type="success" effect="plain">Settings：Java MySQL</el-tag>
            <el-tag type="success" effect="plain">Models：Java MySQL</el-tag>
            <el-tag type="success" effect="plain">Plugins：Java MySQL</el-tag>
          </div>
        </div>
      </template>

      <el-alert
        v-if="errors.platformRuns"
        :title="errors.platformRuns"
        type="error"
        show-icon
        :closable="false"
      />
      <el-alert
        v-if="errors.platformStats"
        :title="`${errors.platformStats}，已回退为前端运行列表计算统计`"
        type="warning"
        show-icon
        :closable="false"
        class="platform-stats-warning"
      />
      <el-empty v-else-if="!platformRuns.length && !loading.platformRuns" description="暂无 Java 平台运行记录" />
      <div v-else class="platform-run-list">
        <article v-for="record in recentPlatformRuns" :key="record.platformRunId" class="platform-run-item">
          <div>
            <div class="platform-run-id">{{ record.platformRunId }}</div>
            <div class="platform-run-subtitle">{{ record.pythonRunId || "尚无 Python run_id" }}</div>
          </div>
          <div class="platform-run-tags">
            <el-tag :type="record.success ? 'success' : 'danger'" effect="plain" size="small">
              {{ record.success ? "成功" : "失败" }}
            </el-tag>
            <el-tag effect="plain" size="small">质量 {{ record.qualityScore }}</el-tag>
            <el-tag :type="record.retryCount > 0 ? 'warning' : 'info'" effect="plain" size="small">
              修复 {{ record.retryCount }}
            </el-tag>
            <router-link :to="{ path: '/history', query: { run_id: record.platformRunId } }">
              <el-button size="small" text>查看详情</el-button>
            </router-link>
            <router-link :to="`/replay/${record.platformRunId}`">
              <el-button size="small" type="primary" plain>回放</el-button>
            </router-link>
          </div>
        </article>
      </div>
    </el-card>

    <el-card v-if="isJavaMode" shadow="never" class="platform-record-card" v-loading="loading.events">
      <template #header>
        <div class="platform-record-head">
          <span>最近平台事件</span>
          <div class="platform-record-tags">
            <el-tag type="primary" effect="plain">最近 {{ recentPlatformEvents.length }} 条</el-tag>
            <el-button size="small" :icon="Refresh" :loading="loading.events" @click="refreshRecentEvents">
              刷新最近事件
            </el-button>
          </div>
        </div>
      </template>
      <el-alert
        v-if="errors.events"
        :title="errors.events"
        type="warning"
        show-icon
        :closable="false"
      />
      <el-empty v-else-if="!recentPlatformEvents.length && !loading.events" description="暂无平台事件" />
      <div v-else class="platform-event-list">
        <article v-for="event in recentPlatformEvents" :key="event.id" class="platform-event-item">
          <div>
            <div class="platform-run-id">{{ event.platformRunId }}</div>
            <div class="platform-run-subtitle">{{ event.createdAt || "未记录时间" }}</div>
          </div>
          <div class="platform-event-main">
            <el-tag v-if="event.agent" :type="agentTagType(event.agent)" effect="plain" size="small">
              {{ agentLabel(event.agent) }}
            </el-tag>
            <el-tag :type="eventTagType(event.eventType)" effect="plain" size="small">
              {{ event.eventText || event.eventType }}
            </el-tag>
            <span>{{ event.message || "无事件描述" }}</span>
          </div>
        </article>
      </div>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="15">
        <RecentRuns :runs="recentRuns" :loading="runLoading" :error="runError" />
      </el-col>
      <el-col :span="9">
        <RecentReports :reports="recentReports" :loading="loading.reports" :error="errors.reports" />
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <ModelStatusPanel
          :models="models"
          :selected-model-provider="settingsStore.selectedModelProvider"
          :loading="loading.models"
          :error="errors.models"
        />
      </el-col>
      <el-col :span="12">
        <PluginStatusPanel
          :plugins="plugins"
          :enabled-plugins="settingsStore.enabledPlugins"
          :loading="loading.plugins"
          :error="errors.plugins"
        />
      </el-col>
    </el-row>

    <QuickActions />
  </section>
</template>

<style scoped>
.dashboard-page {
  gap: 14px;
}

.dashboard-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 18px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #ffffff;
}

.dashboard-hero h1 {
  margin: 0;
  color: #0f172a;
  font-size: 25px;
}

.dashboard-hero p {
  margin: 6px 0 0;
  color: #64748b;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.hero-actions {
  display: grid;
  justify-items: end;
  gap: 10px;
}

.api-base {
  color: #64748b;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.api-mode-line {
  color: #475569;
  font-size: 13px;
  font-weight: 600;
}

.platform-record-card :deep(.el-card__body) {
  padding: 12px;
}

.platform-record-head,
.platform-record-tags,
.platform-run-item,
.platform-run-tags {
  display: flex;
  align-items: center;
}

.platform-record-head {
  justify-content: space-between;
}

.platform-record-tags {
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
}

.platform-run-list {
  display: grid;
  gap: 8px;
}

.platform-event-list {
  display: grid;
  gap: 8px;
}

.platform-stats-warning {
  margin-bottom: 10px;
}

.platform-run-item {
  justify-content: space-between;
  gap: 12px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
}

.platform-event-item {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) 2fr;
  gap: 12px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
}

.platform-run-id {
  color: #0f172a;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 13px;
  font-weight: 700;
}

.platform-run-subtitle {
  margin-top: 3px;
  color: #64748b;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.platform-run-tags {
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
}

.platform-run-tags a {
  text-decoration: none;
}

.platform-event-main {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  color: #334155;
  font-size: 13px;
}
</style>
