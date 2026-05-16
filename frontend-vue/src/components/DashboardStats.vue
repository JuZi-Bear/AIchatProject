<script setup lang="ts">
import type { ReportItem, RunHistoryItem } from "@/types/run";

const props = defineProps<{
  totalRuns: number;
  successRuns: number;
  failedRuns: number;
  averageQualityScore: number;
  latestRun?: RunHistoryItem | null;
  latestReport?: ReportItem | null;
}>();

function latestRunLabel() {
  if (!props.latestRun) {
    return "暂无运行记录";
  }

  return props.latestRun.success ? "最近成功" : "最近失败";
}
</script>

<template>
  <el-row :gutter="12" class="dashboard-stats">
    <el-col :span="4">
      <el-card shadow="never" class="stat-card">
        <el-statistic title="历史运行总数" :value="totalRuns" />
      </el-card>
    </el-col>
    <el-col :span="4">
      <el-card shadow="never" class="stat-card">
        <el-statistic title="成功运行数量" :value="successRuns" />
      </el-card>
    </el-col>
    <el-col :span="4">
      <el-card shadow="never" class="stat-card">
        <el-statistic title="失败运行数量" :value="failedRuns" />
      </el-card>
    </el-col>
    <el-col :span="4">
      <el-card shadow="never" class="stat-card">
        <el-statistic title="平均质量评分" :value="averageQualityScore" :precision="1" />
      </el-card>
    </el-col>
    <el-col :span="4">
      <el-card shadow="never" class="stat-card">
        <div class="stat-title">最近一次运行状态</div>
        <el-tag v-if="latestRun" :type="latestRun.success ? 'success' : 'danger'" effect="plain">
          {{ latestRunLabel() }}
        </el-tag>
        <div v-else class="muted-value">暂无运行记录</div>
      </el-card>
    </el-col>
    <el-col :span="4">
      <el-card shadow="never" class="stat-card">
        <div class="stat-title">最近一次报告</div>
        <div v-if="latestReport" class="compact-value">{{ latestReport.report_name }}</div>
        <div v-else class="muted-value">暂无报告</div>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.dashboard-stats {
  row-gap: 12px;
}

.stat-card {
  height: 100%;
  border-radius: 8px;
}

.stat-title {
  margin-bottom: 12px;
  color: #64748b;
  font-size: 13px;
}

.compact-value {
  overflow-wrap: anywhere;
  color: #0f172a;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.45;
}

.muted-value {
  color: #94a3b8;
  font-size: 13px;
}
</style>
