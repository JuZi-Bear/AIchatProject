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
const isBlocked = computed(() => {
  const text = `${props.event.eventText} ${props.event.message || ""} ${props.event.detailJson || ""}`.toLowerCase();

  return text.includes("blocked") || text.includes("forbidden") || text.includes("denied") || text.includes("阻断") || text.includes("违规");
});

const executionMode = computed(() => {
  if (!props.event.detailJson) {
    return "";
  }

  try {
    const detail = JSON.parse(props.event.detailJson) as {
      executionMode?: string;
      execution_mode?: string;
      detail?: { executionMode?: string; execution_mode?: string };
    };

    return detail.executionMode || detail.execution_mode || detail.detail?.executionMode || detail.detail?.execution_mode || "";
  } catch {
    return "";
  }
});
const connectionMappings = computed(() => {
  if (!props.event.detailJson) {
    return [] as Array<Record<string, unknown>>;
  }

  try {
    const detail = JSON.parse(props.event.detailJson) as Record<string, unknown>;
    const mappings = [
      ...(Array.isArray(detail.connectionMappings) ? detail.connectionMappings : []),
      ...(Array.isArray(detail.inputMappings) ? detail.inputMappings : []),
      ...(Array.isArray(detail.outputMappings) ? detail.outputMappings : []),
    ];

    return mappings as Array<Record<string, unknown>>;
  } catch {
    return [] as Array<Record<string, unknown>>;
  }
});

function executionModeLabel(mode: string) {
  const labels: Record<string, string> = {
    executed: "真实执行",
    simulated: "平台模拟",
    waiting: "等待确认",
  };

  return labels[mode] || mode;
}

function executionModeTagType(mode: string) {
  const types: Record<string, string> = {
    executed: "success",
    simulated: "info",
    waiting: "warning",
  };

  return types[mode] || "info";
}

function eventTagType(eventType: string) {
  if (eventType === "AGENT_FINISHED" || eventType === "RUNNER_FINISHED" || eventType === "TEST_FINISHED" || eventType === "REPORT_GENERATED" || eventType === "WORKFLOW_FINISHED") {
    return "success";
  }

  if (isBlocked.value || eventType === "AGENT_FAILED" || eventType === "ERROR_OCCURRED") {
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
  <article class="replay-event-card" :class="{ active, 'code-agent': isCodeAgent, blocked: isBlocked }">
    <div class="event-card-head">
      <div class="event-tags">
        <el-tag v-if="isCodeAgent" type="warning" effect="dark" size="small">文件操作节点</el-tag>
        <el-tag v-if="isBlocked" type="danger" effect="dark" size="small">安全阻断</el-tag>
        <el-tag v-if="executionMode" :type="executionModeTagType(executionMode)" effect="plain" size="small">
          {{ executionModeLabel(executionMode) }}
        </el-tag>
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
    <div v-if="connectionMappings.length" class="event-mapping-list">
      <span
        v-for="(mapping, index) in connectionMappings.slice(0, 5)"
        :key="`${mapping.fromNodeId}-${mapping.fromOutputField}-${mapping.toNodeId}-${mapping.toInputField}-${index}`"
        class="event-mapping-pill"
        :style="{ '--mapping-color': String(mapping.color || '#64748b') }"
      >
        {{ mapping.fromNodeName }}.{{ mapping.fromOutputField }} → {{ mapping.toNodeName }}.{{ mapping.toInputField }}
      </span>
      <em v-if="connectionMappings.length > 5">+{{ connectionMappings.length - 5 }}</em>
    </div>
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
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-left: 4px solid rgba(148, 163, 184, 0.62);
  border-radius: 15px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.014)),
    #17191f;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.035);
}

.replay-event-card.active {
  border-color: rgba(77, 163, 255, 0.5);
  border-left-color: #4da3ff;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    0 0 0 3px rgba(77, 163, 255, 0.14);
}

.replay-event-card.code-agent {
  border-left-color: #facc15;
  background:
    radial-gradient(circle at 100% 0%, rgba(250, 204, 21, 0.14), transparent 36%),
    #17191f;
}

.replay-event-card.code-agent.active {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.22);
}

.replay-event-card.blocked {
  border-color: rgba(251, 113, 133, 0.38);
  border-left-color: #fb7185;
  background:
    radial-gradient(circle at 100% 0%, rgba(251, 113, 133, 0.16), transparent 38%),
    #17191f;
}

.replay-event-card.blocked.active {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.18);
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
  color: var(--codex-muted);
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

p {
  margin: 0;
  color: #d4d4d8;
  line-height: 1.5;
}

.event-mapping-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.event-mapping-pill {
  max-width: 100%;
  overflow: hidden;
  padding: 4px 8px;
  border: 1px solid color-mix(in srgb, var(--mapping-color) 38%, #17191f);
  border-left: 4px solid var(--mapping-color);
  border-radius: 999px;
  background: color-mix(in srgb, var(--mapping-color) 18%, #17191f);
  color: #e4e4e7;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 11px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-mapping-list em {
  color: var(--codex-muted);
  font-size: 12px;
  font-style: normal;
  font-weight: 800;
}

.detail-collapse pre {
  max-height: 260px;
  margin: 0;
  overflow: auto;
  padding: 10px;
  border-radius: 8px;
  background: #111318;
  color: #e4e4e7;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  white-space: pre-wrap;
}
</style>
