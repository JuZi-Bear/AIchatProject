<script setup lang="ts">
import { computed } from "vue";

import type { ReplayEvent } from "@/types/replay";

const props = defineProps<{
  event: ReplayEvent;
  active?: boolean;
}>();

const isCodeAgent = computed(
  () => props.event.agent === "code_agent" || props.event.platformRunId?.startsWith("code_agent"),
);

function eventTagType(eventType: string) {
  if (eventType === "AGENT_FINISHED" || eventType === "RUNNER_FINISHED" || eventType === "TEST_FINISHED" || eventType === "REPORT_GENERATED" || eventType === "WORKFLOW_FINISHED") {
    return "success";
  }

  if (eventType === "AGENT_FAILED" || eventType === "ERROR_OCCURRED") {
    return "danger";
  }

  if (eventType === "REPAIR_STARTED" || eventType === "REPAIR_FINISHED") {
    return "warning";
  }

  if (eventType === "QUALITY_EVALUATED") {
    return "primary";
  }

  return "primary";
}

function agentLabel(agent?: string) {
  const labels: Record<string, string> = {
    product: "Product",
    coder: "Coder",
    tester: "Tester",
    runner: "Runner",
    sentry: "Sentry",
    quality: "Quality",
    report: "Report",
    workflow: "Workflow",
    code_agent: "CodeAgent",
  };

  return labels[agent || ""] || agent || "Platform";
}

function agentTagType(agent?: string) {
  const types: Record<string, string> = {
    product: "primary",
    coder: "success",
    tester: "warning",
    runner: "info",
    sentry: "danger",
    quality: "success",
    report: "primary",
    workflow: "info",
    code_agent: "warning",
  };

  return types[agent || ""] || "info";
}
</script>

<template>
  <article class="replay-event-card" :class="{ active, 'code-agent': isCodeAgent }">
    <div class="event-card-head">
      <div class="event-tags">
        <el-tag v-if="isCodeAgent" type="warning" effect="dark" size="small">文件操作节点</el-tag>
        <el-tag :type="agentTagType(props.event.agent)" effect="plain" size="small">
          {{ agentLabel(props.event.agent) }}
        </el-tag>
        <el-tag :type="eventTagType(props.event.eventType)" effect="plain" size="small">
          {{ props.event.eventText || props.event.eventType }}
        </el-tag>
        <el-tag effect="plain" size="small">{{ props.event.status || "UNKNOWN" }}</el-tag>
      </div>
      <span class="event-time">{{ props.event.createdAt || "未记录时间" }}</span>
    </div>
    <p>{{ props.event.message || "无事件描述" }}</p>
    <el-collapse v-if="props.event.detailJson && props.event.detailJson !== '{}'" class="detail-collapse">
      <el-collapse-item title="detailJson" name="detail">
        <pre>{{ props.event.detailJson }}</pre>
      </el-collapse-item>
    </el-collapse>
  </article>
</template>

<style scoped>
.replay-event-card {
  display: grid;
  gap: 8px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-left: 5px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
}

.replay-event-card.active {
  border-color: #2563eb;
  border-left-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.14);
}

.replay-event-card.code-agent {
  border-left-color: #f59e0b;
  background: #fffbeb;
}

.replay-event-card.code-agent.active {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.22);
}

.event-card-head,
.event-tags {
  display: flex;
  align-items: center;
}

.event-card-head {
  justify-content: space-between;
  gap: 12px;
}

.event-tags {
  flex-wrap: wrap;
  gap: 8px;
}

.event-time {
  color: #64748b;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

p {
  margin: 0;
  color: #334155;
  line-height: 1.5;
}

.detail-collapse pre {
  max-height: 260px;
  margin: 0;
  overflow: auto;
  padding: 10px;
  border-radius: 8px;
  background: #f8fafc;
  color: #0f172a;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  white-space: pre-wrap;
}
</style>
