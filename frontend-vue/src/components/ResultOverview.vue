<script setup lang="ts">
import { computed } from "vue";

import type { RunResponse } from "@/types/run";
import { runnerDisplayLabel } from "@/utils/runKind";

const props = defineProps<{
  response?: RunResponse | null;
  requirement?: string;
}>();

const summary = computed(() => props.response?.run_summary);
const uiViewModel = computed(() => props.response?.ui_view_model);
const errorSummary = computed(
  () =>
    uiViewModel.value?.agent_outputs?.error_summary ||
    uiViewModel.value?.agent_outputs?.error_log ||
    "无错误摘要",
);
const requirementText = computed(() => {
  const rawState = uiViewModel.value?.raw?.state;

  if (rawState && typeof rawState === "object" && "requirement" in rawState) {
    return String((rawState as Record<string, unknown>).requirement || "");
  }

  return props.requirement || summary.value?.requirement || "未记录";
});
const runnerLabel = computed(() => runnerDisplayLabel(summary.value?.runner_mode));
</script>

<template>
  <el-empty v-if="!response" description="等待运行结果" />
  <div v-else class="result-overview">
    <div class="overview-grid">
      <div class="overview-item wide">
        <span>run_id</span>
        <strong>{{ response.run_id || "未生成" }}</strong>
      </div>
      <div class="overview-item">
        <span>成功状态</span>
        <el-tag :type="summary?.success ? 'success' : 'danger'" effect="plain">
          {{ summary?.success ? "成功" : "失败" }}
        </el-tag>
      </div>
      <div class="overview-item">
        <span>修复次数</span>
        <strong>{{ summary?.retry_count ?? 0 }}</strong>
      </div>
      <div class="overview-item">
        <span>测试状态</span>
        <el-tag :type="summary?.test_success ? 'success' : 'danger'" effect="plain">
          {{ summary?.test_success ? "通过" : "未通过" }}
        </el-tag>
      </div>
      <div class="overview-item">
        <span>覆盖率</span>
        <strong>{{ summary?.coverage_percent ?? 0 }}%</strong>
      </div>
      <div class="overview-item">
        <span>质量评分</span>
        <strong>{{ summary?.quality_score ?? 0 }}</strong>
      </div>
      <div class="overview-item">
        <span>Runner</span>
        <strong>{{ runnerLabel }}</strong>
      </div>
    </div>

    <el-collapse class="overview-collapse">
      <el-collapse-item title="用户需求" name="requirement">
        <p class="inline-long">{{ requirementText }}</p>
      </el-collapse-item>
      <el-collapse-item title="报告路径" name="report">
        <p class="inline-long">{{ summary?.report_path || "暂无报告" }}</p>
      </el-collapse-item>
      <el-collapse-item title="错误摘要 / Runner Warning" name="error">
        <p v-if="summary?.runner_warning" class="inline-long warning-text">{{ summary.runner_warning }}</p>
        <p class="inline-long">{{ errorSummary }}</p>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<style scoped>
.result-overview {
  display: grid;
  gap: 12px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
}

.overview-item {
  display: grid;
  gap: 6px;
  min-height: 76px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #f8fafc;
}

.overview-item.wide {
  grid-column: span 2;
}

.overview-item span {
  color: #64748b;
  font-size: 12px;
}

.overview-item strong {
  overflow: hidden;
  color: #0f172a;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.overview-collapse {
  border-radius: 10px;
  background: #ffffff;
}

.inline-long {
  margin: 0;
  overflow-wrap: anywhere;
  line-height: 1.6;
}

.warning-text {
  color: #b45309;
}

@media (max-width: 1280px) {
  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
