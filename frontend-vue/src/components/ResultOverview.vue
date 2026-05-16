<script setup lang="ts">
import { computed } from "vue";

import type { RunResponse } from "@/types/run";

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
</script>

<template>
  <el-empty v-if="!response" description="等待运行结果" />
  <div v-else class="result-overview">
    <el-descriptions :column="2" border>
      <el-descriptions-item label="run_id">{{ response.run_id || "未生成" }}</el-descriptions-item>
      <el-descriptions-item label="用户需求">
        <span class="inline-long">{{ requirementText }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="是否成功">
        <el-tag :type="summary?.success ? 'success' : 'danger'" effect="plain">
          {{ summary?.success ? "成功" : "失败" }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="修复次数">{{ summary?.retry_count ?? 0 }}</el-descriptions-item>
      <el-descriptions-item label="测试是否通过">
        <el-tag :type="summary?.test_success ? 'success' : 'danger'" effect="plain">
          {{ summary?.test_success ? "通过" : "未通过" }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="覆盖率">{{ summary?.coverage_percent ?? 0 }}%</el-descriptions-item>
      <el-descriptions-item label="质量评分">{{ summary?.quality_score ?? 0 }}</el-descriptions-item>
      <el-descriptions-item label="报告路径">
        <span class="inline-long">{{ summary?.report_path || "暂无报告" }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="错误摘要" :span="2">
        <span class="inline-long">{{ errorSummary }}</span>
      </el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<style scoped>
.result-overview :deep(.el-descriptions__cell) {
  vertical-align: top;
}

.inline-long {
  overflow-wrap: anywhere;
  line-height: 1.6;
}
</style>
