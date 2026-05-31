<script setup lang="ts">
import { useRouter } from "vue-router";

import type { ReportItem } from "@/types/run";

defineProps<{
  reports: ReportItem[];
  loading?: boolean;
  error?: string;
}>();

const router = useRouter();

function openReports(reportName: string) {
  router.push({ path: "/reports", query: reportName ? { report: reportName } : {} });
}
</script>

<template>
  <el-card shadow="never" class="dashboard-card" v-loading="loading">
    <template #header>
      <div class="card-header">
        <span>最近报告</span>
        <el-button text type="primary" @click="router.push('/reports')">全部报告</el-button>
      </div>
    </template>

    <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
    <el-empty v-else-if="!reports.length && !loading" description="暂无报告" />

    <div v-else class="report-list">
      <article
        v-for="report in reports"
        :key="report.report_name"
        class="report-item"
        @click="openReports(report.report_name)"
      >
        <div class="report-name">{{ report.report_name }}</div>
        <div class="report-meta">
          <el-tag v-if="report.run_id" size="small" effect="plain">{{ report.run_id }}</el-tag>
          <span>{{ report.created_at || "未记录时间" }}</span>
        </div>
      </article>
    </div>
  </el-card>
</template>

<style scoped>
.dashboard-card {
  height: 100%;
  border-radius: 8px;
}

.card-header,
.report-meta {
  display: flex;
  align-items: center;
}

.card-header {
  justify-content: space-between;
  gap: 10px;
}

.report-list {
  display: grid;
  gap: 10px;
}

.report-item {
  padding: 11px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #17191f;
  cursor: pointer;
}

.report-item:hover {
  border-color: #3b82f6;
}

.report-name {
  overflow-wrap: anywhere;
  color: #0f172a;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  font-weight: 800;
  line-height: 1.45;
}

.report-meta {
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 9px;
  color: #64748b;
  font-size: 12px;
}
</style>
