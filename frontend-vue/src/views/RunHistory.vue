<script setup lang="ts">
import { Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import AgentOutputTabs from "@/components/AgentOutputTabs.vue";
import ReportPreview from "@/components/ReportPreview.vue";
import ResultOverview from "@/components/ResultOverview.vue";
import SummaryCards from "@/components/SummaryCards.vue";
import WorkflowTimeline from "@/components/WorkflowTimeline.vue";
import { getRun, getRuns } from "@/api/runs";
import type { RunHistoryItem, RunResponse } from "@/types/run";

const runs = ref<RunHistoryItem[]>([]);
const selectedRun = ref<RunResponse | null>(null);
const selectedRunId = ref("");
const loading = ref(false);
const detailLoading = ref(false);
const keyword = ref("");
const statusFilter = ref("all");
const modelFilter = ref("all");
const route = useRoute();

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

async function loadRuns() {
  loading.value = true;

  try {
    runs.value = await getRuns();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "加载历史记录失败");
  } finally {
    loading.value = false;
  }
}

async function openRun(runId?: string) {
  if (!runId) {
    ElMessage.warning("该历史记录缺少 run_id");
    return;
  }

  selectedRunId.value = runId;
  detailLoading.value = true;

  try {
    selectedRun.value = await getRun(runId);
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "加载运行详情失败");
  } finally {
    detailLoading.value = false;
  }
}

onMounted(async () => {
  await loadRuns();

  const queryRunId = typeof route.query.run_id === "string" ? route.query.run_id : "";

  if (queryRunId) {
    openRun(queryRunId);
  }
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
              @click="openRun(run.run_id)"
            >
              <div class="history-item-head">
                <span class="run-id">{{ run.run_id }}</span>
                <el-tag :type="run.success ? 'success' : 'danger'" effect="plain" size="small">
                  {{ run.success ? "成功" : "失败" }}
                </el-tag>
              </div>
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
            </article>
          </div>
        </section>
      </el-col>

      <el-col :lg="14" :md="24">
        <section class="panel detail-panel" v-loading="detailLoading">
          <template v-if="selectedRun">
            <div class="panel-title">历史详情：{{ selectedRun.run_id }}</div>
            <SummaryCards :summary="selectedRun.run_summary" />
            <div class="subsection-title">Agent 工作流节点</div>
            <WorkflowTimeline :workflow-steps="selectedRun.ui_view_model?.workflow_steps" />
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

@media (max-width: 1280px) {
  .history-filters {
    grid-template-columns: 1fr;
  }

  .history-list {
    max-height: 520px;
  }
}
</style>
