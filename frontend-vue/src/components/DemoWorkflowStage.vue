<script setup lang="ts">
import {
  Check,
  Close,
  Clock,
  Loading,
  RefreshRight,
} from "@element-plus/icons-vue";
import { computed } from "vue";

import type { DemoStage, DemoStageStatus } from "@/types/demo";
import type { RunResponse } from "@/types/run";

const props = defineProps<{
  response?: RunResponse | null;
  running?: boolean;
  errorDetail?: string;
}>();

const baseStages: DemoStage[] = [
  { key: "requirement", label: "需求输入", summary: "接收自然语言需求", status: "waiting", order: 1 },
  { key: "product", label: "Product Agent 需求拆解", summary: "拆解目标、边界和验收标准", status: "waiting", order: 2 },
  { key: "coder", label: "Coder Agent 代码生成", summary: "生成可运行 Python 实现", status: "waiting", order: 3 },
  { key: "tester", label: "Tester Agent 测试生成", summary: "生成 pytest 测试用例", status: "waiting", order: 4 },
  { key: "runner", label: "Runner 运行验证", summary: "保存代码并运行测试", status: "waiting", order: 5 },
  { key: "sentry", label: "Sentry Agent 错误分析", summary: "失败时定位错误原因", status: "waiting", order: 6 },
  { key: "repair", label: "Coder Agent 自动修复", summary: "根据错误摘要进行自愈修复", status: "waiting", order: 7 },
  { key: "quality", label: "Quality 质量评分", summary: "计算覆盖率、安全和质量分", status: "waiting", order: 8 },
  { key: "report", label: "Report 报告生成", summary: "生成 Markdown 复盘报告", status: "waiting", order: 9 },
];

const statusText: Record<DemoStageStatus, string> = {
  waiting: "等待中",
  running: "运行中",
  done: "已完成",
  failed: "失败",
  repairing: "修复中",
  skipped: "已跳过",
};

const stages = computed(() => {
  if (props.running) {
    return baseStages.map((stage) => ({
      ...stage,
      status: stage.order < 5 ? "done" : stage.order === 5 ? "running" : "waiting",
    })) satisfies DemoStage[];
  }

  if (props.errorDetail) {
    return baseStages.map((stage) => ({
      ...stage,
      status: stage.order < 5 ? "done" : stage.order === 5 ? "failed" : "waiting",
    })) satisfies DemoStage[];
  }

  const summary = props.response?.run_summary;

  if (!summary) {
    return baseStages;
  }

  const hasRepair = (summary.retry_count || 0) > 0;
  const success = Boolean(summary.success);

  return baseStages.map((stage) => {
    if (stage.key === "sentry" || stage.key === "repair") {
      return {
        ...stage,
        status: hasRepair ? (stage.key === "repair" ? "repairing" : "done") : "skipped",
      };
    }

    if (stage.key === "runner" && !success) {
      return { ...stage, status: "failed" };
    }

    if (stage.key === "quality" || stage.key === "report") {
      return { ...stage, status: success ? "done" : "failed" };
    }

    return { ...stage, status: "done" };
  }) satisfies DemoStage[];
});

function statusIcon(status: DemoStageStatus) {
  if (status === "done") {
    return Check;
  }

  if (status === "failed") {
    return Close;
  }

  if (status === "running") {
    return Loading;
  }

  if (status === "repairing") {
    return RefreshRight;
  }

  return Clock;
}
</script>

<template>
  <section class="demo-stage-panel">
    <div class="panel-title">AI 工作流阶段</div>
    <div class="stage-grid">
      <article
        v-for="stage in stages"
        :key="stage.key"
        class="stage-card"
        :class="[`status-${stage.status}`]"
      >
        <div class="stage-icon">
          <el-icon><component :is="statusIcon(stage.status)" /></el-icon>
        </div>
        <div class="stage-body">
          <div class="stage-head">
            <span>{{ stage.label }}</span>
            <el-tag size="small" effect="plain">{{ statusText[stage.status] }}</el-tag>
          </div>
          <p>{{ stage.summary }}</p>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.demo-stage-panel {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #ffffff;
}

.stage-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.stage-card {
  display: flex;
  gap: 10px;
  min-height: 102px;
  padding: 11px;
  border: 1px solid #e2e8f0;
  border-left-width: 5px;
  border-radius: 8px;
  background: #fbfdff;
}

.stage-icon {
  display: grid;
  flex: 0 0 auto;
  width: 32px;
  height: 32px;
  place-items: center;
  border-radius: 50%;
  background: #f1f5f9;
  color: #64748b;
}

.stage-body {
  min-width: 0;
  flex: 1;
}

.stage-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  color: #0f172a;
  font-weight: 800;
}

.stage-body p {
  margin: 7px 0 0;
  color: #64748b;
  line-height: 1.45;
}

.status-done {
  border-left-color: #22c55e;
  background: #f7fef9;
}

.status-failed {
  border-left-color: #ef4444;
  background: #fff7f7;
}

.status-running {
  border-left-color: #3b82f6;
  background: #f8fbff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.status-repairing {
  border-left-color: #f59e0b;
  background: #fffaf0;
}

.status-skipped,
.status-waiting {
  border-left-color: #94a3b8;
  background: #f8fafc;
}
</style>
