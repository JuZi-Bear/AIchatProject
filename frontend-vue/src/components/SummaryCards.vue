<script setup lang="ts">
import { computed } from "vue";

import type { RunSummary } from "@/types/run";
import { runnerDisplayLabel, runnerTagType } from "@/utils/runKind";

const props = defineProps<{
  summary?: Partial<RunSummary> | null;
}>();

const successText = computed(() => {
  if (props.summary?.success === undefined) {
    return "未运行";
  }

  return props.summary.success ? "成功" : "失败";
});

const successType = computed(() => {
  if (props.summary?.success === undefined) {
    return "info";
  }

  return props.summary.success ? "success" : "danger";
});

const testType = computed(() => {
  if (props.summary?.test_success === undefined) {
    return "info";
  }

  return props.summary.test_success ? "success" : "danger";
});

const runnerLabel = computed(() => runnerDisplayLabel(props.summary?.runner_mode));
const runnerType = computed(() => runnerTagType(props.summary?.runner_mode));
</script>

<template>
  <div class="summary-cards">
    <el-card shadow="never" class="summary-card">
      <template #header>运行状态</template>
      <el-tag :type="successType" size="large" effect="dark">{{ successText }}</el-tag>
      <div class="summary-meta">模型：{{ summary?.model_provider || "未选择" }}</div>
    </el-card>

    <el-card shadow="never" class="summary-card">
      <template #header>修复次数</template>
      <el-statistic :value="summary?.retry_count ?? 0" />
      <div class="summary-meta">自动修复循环</div>
    </el-card>

    <el-card shadow="never" class="summary-card">
      <template #header>测试状态</template>
      <el-tag :type="testType" size="large" effect="plain">
        {{ summary?.test_success === undefined ? "未运行" : summary.test_success ? "通过" : "未通过" }}
      </el-tag>
      <div class="summary-meta">覆盖率：{{ summary?.coverage_percent ?? 0 }}%</div>
    </el-card>

    <el-card shadow="never" class="summary-card">
      <template #header>质量评分</template>
      <el-statistic :value="summary?.quality_score ?? 0" suffix="/ 100" />
      <div class="summary-meta">{{ summary?.security_status || "等待安全检查" }}</div>
    </el-card>

    <el-card shadow="never" class="summary-card">
      <template #header>Runner</template>
      <el-tag :type="runnerType" size="large" effect="plain">
        {{ runnerLabel }}
      </el-tag>
      <div class="summary-meta warning-text">{{ summary?.runner_warning || "无回退提示" }}</div>
    </el-card>

    <el-card shadow="never" class="summary-card wide">
      <template #header>报告路径</template>
      <div class="summary-path">{{ summary?.report_path || "暂无报告" }}</div>
    </el-card>
  </div>
</template>

<style scoped>
.summary-cards {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.summary-card {
  min-height: 132px;
}

.summary-card :deep(.el-card__header) {
  padding: 10px 14px;
  color: #475569;
  font-weight: 700;
}

.summary-card :deep(.el-card__body) {
  padding: 14px;
}

.summary-card.wide {
  grid-column: span 4;
  min-height: 88px;
}

.summary-meta {
  margin-top: 10px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.5;
}

.summary-path {
  color: #334155;
  font-family: "Cascadia Code", Consolas, monospace;
  overflow-wrap: anywhere;
}

.warning-text {
  color: #b45309;
}

@media (max-width: 1280px) {
  .summary-cards {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .summary-card.wide {
    grid-column: span 2;
  }
}
</style>
