<script setup lang="ts">
import {
  Check,
  Close,
  Clock,
  Loading,
  Minus,
  RefreshRight,
} from "@element-plus/icons-vue";
import { computed } from "vue";

import type { WorkflowStep } from "@/types/run";

const props = defineProps<{
  workflowSteps?: WorkflowStep[];
  workflowEvents?: Array<Record<string, unknown>>;
}>();

const statusText: Record<string, string> = {
  waiting: "等待中",
  running: "运行中",
  done: "已完成",
  failed: "失败",
  repairing: "修复中",
  skipped: "已跳过",
};

const sortedSteps = computed(() =>
  [...(props.workflowSteps || [])].sort((left, right) => left.order - right.order),
);

const activeKey = computed(() => {
  const activeStep = sortedSteps.value.find((step) =>
    ["running", "repairing", "failed"].includes(step.status.toLowerCase()),
  );

  if (activeStep) {
    return activeStep.key;
  }

  return [...sortedSteps.value].reverse().find((step) => step.status.toLowerCase() === "done")?.key;
});

const stepAgentMap: Record<string, string> = {
  product: "product",
  coder: "coder",
  tester: "tester",
  runner: "runner",
  sentry: "sentry",
  quality: "quality",
  report: "report",
};

const eventHints = computed(() => {
  const hints: Record<string, string> = {};

  for (const event of props.workflowEvents || []) {
    const agent = String(event.agent || "");
    const targetKey = Object.entries(stepAgentMap).find(([, value]) => value === agent)?.[0];

    if (targetKey) {
      hints[targetKey] = String(event.event_text || event.eventText || event.message || "");
    }
  }

  return hints;
});

function normalizeStatus(status: string) {
  return status.toLowerCase();
}

function displayStatus(status: string) {
  return statusText[normalizeStatus(status)] || status || "等待中";
}

function statusIcon(status: string) {
  const normalized = normalizeStatus(status);

  if (normalized === "done") {
    return Check;
  }

  if (normalized === "failed") {
    return Close;
  }

  if (normalized === "running") {
    return Loading;
  }

  if (normalized === "repairing") {
    return RefreshRight;
  }

  if (normalized === "skipped") {
    return Minus;
  }

  return Clock;
}
</script>

<template>
  <el-empty v-if="!sortedSteps.length" description="暂无工作流节点" />
  <div v-else class="timeline-grid">
    <article
      v-for="step in sortedSteps"
      :key="step.key"
      class="timeline-step"
      :class="[`status-${normalizeStatus(step.status)}`, { active: activeKey === step.key }]"
    >
      <div class="timeline-icon">
        <el-icon><component :is="statusIcon(step.status)" /></el-icon>
      </div>
      <div class="timeline-content">
        <div class="timeline-head">
          <span>{{ step.label }}</span>
          <el-tag size="small" effect="plain">{{ displayStatus(step.status) }}</el-tag>
        </div>
        <p>{{ step.summary || "等待输出" }}</p>
        <div v-if="eventHints[step.key]" class="event-hint">{{ eventHints[step.key] }}</div>
      </div>
    </article>
  </div>
</template>

<style scoped>
.timeline-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 10px;
}

.timeline-step {
  display: flex;
  gap: 12px;
  min-height: 118px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-left-width: 5px;
  border-radius: 8px;
  background: #ffffff;
}

.timeline-step.active {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.timeline-icon {
  display: grid;
  flex: 0 0 auto;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 50%;
  background: #f1f5f9;
  color: #64748b;
}

.timeline-content {
  min-width: 0;
  flex: 1;
}

.timeline-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-weight: 800;
}

.timeline-content p {
  display: -webkit-box;
  margin: 8px 0 0;
  overflow: hidden;
  color: #64748b;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.event-hint {
  margin-top: 8px;
  color: #475569;
  font-size: 12px;
  line-height: 1.45;
}

.status-done {
  border-left-color: #22c55e;
  background: #f7fef9;
}

.status-done .timeline-icon {
  background: #dcfce7;
  color: #15803d;
}

.status-failed {
  border-left-color: #ef4444;
  background: #fff7f7;
}

.status-failed .timeline-icon {
  background: #fee2e2;
  color: #b91c1c;
}

.status-running {
  border-left-color: #3b82f6;
  background: #f8fbff;
}

.status-running .timeline-icon {
  background: #dbeafe;
  color: #1d4ed8;
}

.status-repairing {
  border-left-color: #f59e0b;
  background: #fffaf0;
}

.status-repairing .timeline-icon {
  background: #fef3c7;
  color: #b45309;
}

.status-waiting,
.status-skipped {
  border-left-color: #94a3b8;
  background: #f8fafc;
}
</style>
