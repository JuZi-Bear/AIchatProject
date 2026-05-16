<script setup lang="ts">
import type { WorkflowStep } from "@/types/run";

defineProps<{
  steps?: WorkflowStep[];
}>();

function statusType(status: string) {
  const normalized = status.toLowerCase();

  if (normalized === "done") {
    return "success";
  }

  if (normalized === "running" || normalized === "repairing") {
    return "warning";
  }

  if (normalized === "failed") {
    return "danger";
  }

  if (normalized === "skipped") {
    return "info";
  }

  return "";
}
</script>

<template>
  <el-empty v-if="!steps?.length" description="暂无工作流节点" />
  <div v-else class="workflow-list">
    <div v-for="step in steps" :key="step.key" class="workflow-step">
      <div class="step-order">{{ step.order }}</div>
      <div class="step-body">
        <div class="step-header">
          <span>{{ step.label }}</span>
          <el-tag :type="statusType(step.status)" effect="plain" size="small">
            {{ step.status }}
          </el-tag>
        </div>
        <div class="step-summary">{{ step.summary || "等待输出" }}</div>
      </div>
    </div>
  </div>
</template>
