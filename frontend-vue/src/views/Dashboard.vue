<script setup lang="ts">
import { Refresh } from "@element-plus/icons-vue";
import { computed, onMounted, reactive, ref } from "vue";

import { getApiBaseUrl, getHealth } from "@/api/client";
import { getModels } from "@/api/models";
import { getPlugins } from "@/api/plugins";
import { getReports } from "@/api/reports";
import { getRuns } from "@/api/runs";
import DashboardStats from "@/components/DashboardStats.vue";
import ModelStatusPanel from "@/components/ModelStatusPanel.vue";
import PluginStatusPanel from "@/components/PluginStatusPanel.vue";
import QuickActions from "@/components/QuickActions.vue";
import RecentReports from "@/components/RecentReports.vue";
import RecentRuns from "@/components/RecentRuns.vue";
import { useSettingsStore } from "@/stores/settings";
import type { HealthResponse, ModelConfig, PluginConfig } from "@/types/api";
import type { ReportItem, RunHistoryItem } from "@/types/run";

const settingsStore = useSettingsStore();

const health = ref<HealthResponse | null>(null);
const runs = ref<RunHistoryItem[]>([]);
const reports = ref<ReportItem[]>([]);
const models = ref<ModelConfig[]>([]);
const plugins = ref<PluginConfig[]>([]);

const loading = reactive({
  health: false,
  runs: false,
  reports: false,
  models: false,
  plugins: false,
});

const errors = reactive({
  health: "",
  runs: "",
  reports: "",
  models: "",
  plugins: "",
});

const refreshLoading = computed(() => Object.values(loading).some(Boolean));

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

const recentRuns = computed(() => sortedRuns.value.slice(0, 5));
const recentReports = computed(() => sortedReports.value.slice(0, 5));

const apiConnected = computed(() => health.value?.status === "ok" && !errors.health);
const apiStatusLabel = computed(() => {
  if (loading.health && !health.value && !errors.health) {
    return "API 检测中";
  }

  return apiConnected.value ? "API 已连接" : "Python Agent Engine API 未连接";
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
  await Promise.allSettled([
    loadSection("health", getHealth, (data) => {
      health.value = data;
    }, "API 健康检查失败"),
    loadSection("runs", getRuns, (data) => {
      runs.value = data;
    }, "加载运行历史失败"),
    loadSection("reports", getReports, (data) => {
      reports.value = data;
    }, "加载报告列表失败"),
    loadSection("models", getModels, (data) => {
      models.value = data;
    }, "加载模型状态失败"),
    loadSection("plugins", getPlugins, (data) => {
      plugins.value = data;
    }, "加载插件状态失败"),
  ]);
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
          <el-tag type="primary" effect="plain">默认模型 {{ settingsStore.selectedModelProvider || "未选择" }}</el-tag>
          <el-tag type="success" effect="plain">启用插件 {{ settingsStore.enabledPlugins.length }}</el-tag>
          <el-tag effect="plain">Demo {{ settingsStore.demoMode ? "开启" : "关闭" }}</el-tag>
          <el-tag effect="plain">最大修复 {{ settingsStore.maxRetryCount }}</el-tag>
        </div>
      </div>
      <div class="hero-actions">
        <div class="api-base">{{ getApiBaseUrl() }}</div>
        <el-button :icon="Refresh" :loading="refreshLoading" @click="loadDashboard">刷新</el-button>
      </div>
    </div>

    <el-alert
      v-if="errors.health"
      title="Python Agent Engine API 未连接"
      :description="errors.health"
      type="error"
      show-icon
      :closable="false"
    />

    <DashboardStats
      :total-runs="runs.length"
      :success-runs="successRuns"
      :failed-runs="failedRuns"
      :average-quality-score="averageQualityScore"
      :latest-run="latestRun"
      :latest-report="latestReport"
    />

    <el-row :gutter="16">
      <el-col :span="15">
        <RecentRuns :runs="recentRuns" :loading="loading.runs" :error="errors.runs" />
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
</style>
