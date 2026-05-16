<script setup lang="ts">
import { computed } from "vue";

import type { RunResponse } from "@/types/run";

const props = defineProps<{
  response?: RunResponse | null;
}>();

const summary = computed(() => props.response?.run_summary);
const success = computed(() => Boolean(summary.value?.success));
const resultType = computed(() => (success.value ? "success" : "danger"));
</script>

<template>
  <el-empty v-if="!summary" description="运行完成后展示最终质量结果" />
  <section v-else class="demo-result" :class="{ success, failed: !success }">
    <div class="result-status">
      <div>
        <span>最终结果</span>
        <strong>{{ success ? "成功" : "失败" }}</strong>
      </div>
      <el-tag :type="resultType" effect="dark" size="large">
        {{ summary.test_success ? "pytest 通过" : "pytest 未通过" }}
      </el-tag>
    </div>

    <el-row :gutter="12">
      <el-col :span="6">
        <el-card shadow="never" class="result-card">
          <el-statistic title="修复次数" :value="summary.retry_count" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="result-card">
          <el-statistic title="覆盖率" :value="summary.coverage_percent" suffix="%" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="result-card score-card">
          <el-statistic title="质量评分" :value="summary.quality_score" suffix="/100" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="result-card">
          <div class="card-title">安全状态</div>
          <el-tag :type="summary.security_status === 'pass' ? 'success' : 'warning'" effect="plain">
            {{ summary.security_status || "unknown" }}
          </el-tag>
        </el-card>
      </el-col>
    </el-row>

    <div class="report-line">
      <span>报告路径</span>
      <code>{{ summary.report_path || "暂无报告" }}</code>
    </div>
  </section>
</template>

<style scoped>
.demo-result {
  padding: 16px;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  background: #f0fdf4;
}

.demo-result.failed {
  border-color: #fecaca;
  background: #fff7f7;
}

.result-status {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.result-status span,
.card-title,
.report-line span {
  color: #64748b;
  font-size: 13px;
  font-weight: 800;
}

.result-status strong {
  display: block;
  margin-top: 2px;
  color: #0f172a;
  font-size: 28px;
}

.result-card {
  min-height: 98px;
  border-radius: 8px;
}

.score-card {
  border-color: #22c55e;
}

.report-line {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-top: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #ffffff;
}

.report-line code {
  overflow-wrap: anywhere;
  color: #0f172a;
  font-family: "Cascadia Code", Consolas, monospace;
}
</style>
