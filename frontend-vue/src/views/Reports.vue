<script setup lang="ts">
import { CopyDocument, Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import { getReport, getReports } from "@/api/reports";
import type { ReportDetail, ReportItem } from "@/types/run";

const reports = ref<ReportItem[]>([]);
const selectedReport = ref<ReportDetail | null>(null);
const selectedReportName = ref("");
const loading = ref(false);
const contentLoading = ref(false);
const keyword = ref("");
const route = useRoute();

const filteredReports = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase();

  return reports.value
    .filter((report) => {
      if (!normalizedKeyword) {
        return true;
      }

      return `${report.report_name} ${report.run_id || ""} ${report.path}`.toLowerCase().includes(normalizedKeyword);
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
    ElMessage.error(error instanceof Error ? error.message : "加载报告列表失败");
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
    ElMessage.error(error instanceof Error ? error.message : "加载报告内容失败");
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
                <el-tag v-if="report.run_id" size="small" effect="plain">{{ report.run_id }}</el-tag>
              </div>
              <div class="report-meta">
                <span>{{ report.created_at || "未记录时间" }}</span>
                <span>{{ formatSize(report.file_size) }}</span>
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
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #ffffff;
  cursor: pointer;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}

.report-item:hover,
.report-item.active {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
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
  color: #0f172a;
  font-weight: 800;
}

.report-meta {
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

.markdown-preview {
  max-height: calc(100vh - 285px);
  margin: 0;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: #0f172a;
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
