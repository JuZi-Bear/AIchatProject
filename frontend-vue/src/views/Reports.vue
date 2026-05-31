<script setup lang="ts">
import { CopyDocument, Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import { currentApiMode, getApiDisconnectedHint, getConfigSourceLabel, getDataModeLabel } from "@/api/client";
import { getReport, getReports } from "@/api/reports";
import type { ReportDetail, ReportItem } from "@/types/run";

const reports = ref<ReportItem[]>([]);
const selectedReport = ref<ReportDetail | null>(null);
const selectedReportName = ref("");
const loading = ref(false);
const contentLoading = ref(false);
const keyword = ref("");
const route = useRoute();
const isJavaMode = currentApiMode === "java";
const dataModeLabel = getDataModeLabel();
const dataSourceLabel = getConfigSourceLabel();

const filteredReports = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase();

  return reports.value
    .filter((report) => {
      if (!normalizedKeyword) {
        return true;
      }

      return `${report.report_name} ${report.run_id || ""} ${report.platformRunId || ""} ${report.requirement || ""} ${report.path}`
        .toLowerCase()
        .includes(normalizedKeyword);
    })
    .sort((left, right) => (right.created_at || "").localeCompare(left.created_at || ""));
});

function formatSize(size?: number) {
  if (!size) {
    return "0 B";
  }

  if (size < 1024) {
    return `${size} B`;
  }

  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }

  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

async function loadReports() {
  loading.value = true;

  try {
    reports.value = await getReports();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : `${getApiDisconnectedHint()}，加载报告列表失败`);
  } finally {
    loading.value = false;
  }
}

async function openReport(reportName: string) {
  if (!reportName) {
    ElMessage.warning("报告名为空");
    return;
  }

  selectedReportName.value = reportName;
  contentLoading.value = true;

  try {
    selectedReport.value = await getReport(reportName);
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : `${getApiDisconnectedHint()}，加载报告内容失败`);
  } finally {
    contentLoading.value = false;
  }
}

async function copyReport() {
  if (!selectedReport.value?.content) {
    ElMessage.warning("暂无可复制的报告内容");
    return;
  }

  try {
    await navigator.clipboard.writeText(selectedReport.value.content);
    ElMessage.success("报告内容已复制");
  } catch {
    ElMessage.error("复制失败，请手动选择报告内容复制");
  }
}

onMounted(async () => {
  await loadReports();

  const queryReport = typeof route.query.report === "string" ? route.query.report : "";

  if (queryReport) {
    openReport(queryReport);
  }
});
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <h1>Reports</h1>
        <p>查看 Markdown 报告列表，并加载单份报告内容</p>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="loadReports">刷新</el-button>
    </div>

    <div class="mode-tags">
      <el-tag type="warning" effect="plain">当前数据模式：{{ dataModeLabel }}</el-tag>
      <el-tag type="primary" effect="plain">
        当前数据来源：{{ isJavaMode ? "Java MySQL 报告索引" : dataSourceLabel }}
      </el-tag>
    </div>

    <el-row :gutter="16" align="top">
      <el-col :lg="9" :md="24">
        <section class="panel report-list-panel">
          <el-input v-model="keyword" :prefix-icon="Search" clearable placeholder="搜索报告名 / run_id" />

          <el-empty v-if="!loading && !filteredReports.length" description="暂无报告" />
          <div v-else class="report-list" v-loading="loading">
            <article
              v-for="report in filteredReports"
              :key="report.report_name"
              class="report-item"
              :class="{ active: selectedReportName === report.report_name }"
              @click="openReport(report.report_name)"
            >
              <div class="report-item-head">
                <span class="report-name">{{ report.report_name }}</span>
                <div class="report-tags">
                  <el-tag v-if="report.platformRunId" size="small" effect="plain">{{ report.platformRunId }}</el-tag>
                  <el-tag v-if="report.run_id" size="small" effect="plain">{{ report.run_id }}</el-tag>
                  <el-tag
                    v-if="isJavaMode && typeof report.success === 'boolean'"
                    :type="report.success ? 'success' : 'danger'"
                    size="small"
                    effect="plain"
                  >
                    {{ report.success ? "成功" : "失败" }}
                  </el-tag>
                </div>
              </div>
              <div class="report-meta">
                <span>{{ report.created_at || "未记录时间" }}</span>
                <span v-if="isJavaMode">质量 {{ report.qualityScore ?? 0 }}</span>
                <span v-else>{{ formatSize(report.file_size) }}</span>
              </div>
              <div v-if="isJavaMode" class="requirement-text">
                {{ report.requirement || "暂无需求摘要" }}
              </div>
              <div class="report-path">{{ report.path }}</div>
            </article>
          </div>
        </section>
      </el-col>

      <el-col :lg="15" :md="24">
        <section class="panel report-detail-panel" v-loading="contentLoading">
          <template v-if="selectedReport">
            <div class="report-detail-head">
              <div>
                <div class="panel-title">{{ selectedReport.report_name }}</div>
                <div class="report-path">{{ selectedReport.path }}</div>
              </div>
              <el-button :icon="CopyDocument" @click="copyReport">复制报告</el-button>
            </div>

            <div v-if="isJavaMode" class="platform-report-summary">
              <el-tag v-if="selectedReport.platformRunId" type="primary" effect="plain">
                platformRunId：{{ selectedReport.platformRunId }}
              </el-tag>
              <el-tag v-if="selectedReport.pythonRunId" effect="plain">
                pythonRunId：{{ selectedReport.pythonRunId }}
              </el-tag>
              <el-tag
                v-if="typeof selectedReport.success === 'boolean'"
                :type="selectedReport.success ? 'success' : 'danger'"
                effect="plain"
              >
                {{ selectedReport.success ? "成功" : "失败" }}
              </el-tag>
              <el-tag :type="(selectedReport.qualityScore || 0) >= 85 ? 'success' : 'warning'" effect="plain">
                质量 {{ selectedReport.qualityScore ?? 0 }}
              </el-tag>
              <span class="created-at">{{ selectedReport.created_at || "未记录时间" }}</span>
            </div>

            <el-alert
              v-if="selectedReport.error"
              :title="selectedReport.error"
              type="warning"
              show-icon
              :closable="false"
              class="report-warning"
            />

            <div v-if="isJavaMode" class="requirement-detail">
              {{ selectedReport.requirement || "暂无需求摘要" }}
            </div>

            <el-collapse model-value="report">
              <el-collapse-item title="Markdown 报告内容" name="report">
                <pre class="markdown-preview">{{ selectedReport.content }}</pre>
              </el-collapse-item>
            </el-collapse>
          </template>
          <el-empty v-else description="选择左侧报告查看内容" />
        </section>
      </el-col>
    </el-row>
  </section>
</template>

<style scoped>
.report-list-panel,
.report-detail-panel {
  min-height: calc(100vh - 150px);
}

.mode-tags,
.report-tags,
.platform-report-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.report-list {
  display: grid;
  gap: 10px;
  max-height: calc(100vh - 220px);
  margin-top: 12px;
  overflow: auto;
  padding-right: 4px;
}

.report-item {
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 15px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.014)),
    #17191f;
  cursor: pointer;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}

.report-item:hover,
.report-item.active {
  border-color: rgba(77, 163, 255, 0.42);
  box-shadow: 0 0 0 3px rgba(77, 163, 255, 0.12);
}

.report-item-head,
.report-meta,
.report-detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.report-name {
  overflow-wrap: anywhere;
  color: var(--codex-text);
  font-weight: 800;
}

.report-meta {
  margin-top: 10px;
  color: var(--codex-muted);
  font-size: 12px;
}

.requirement-text,
.requirement-detail {
  color: #d4d4d8;
  line-height: 1.55;
}

.requirement-text {
  margin-top: 8px;
  font-size: 13px;
}

.platform-report-summary {
  align-items: center;
  margin: 12px 0;
}

.created-at {
  color: var(--codex-muted);
  font-size: 12px;
}

.report-warning,
.requirement-detail {
  margin-bottom: 12px;
}

.report-path {
  margin-top: 8px;
  overflow-wrap: anywhere;
  color: var(--codex-muted);
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.markdown-preview {
  max-height: calc(100vh - 285px);
  margin: 0;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: #e4e4e7;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 13px;
  line-height: 1.65;
}

@media (max-width: 1280px) {
  .report-list {
    max-height: 460px;
  }
}
</style>
