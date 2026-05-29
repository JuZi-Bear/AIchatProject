<script setup lang="ts">
import { computed, ref } from "vue";
import { openCodeAgentFolder } from "@/api/codeAgent";
import { ElMessage } from "element-plus";

import type { RunResultHighlight } from "@/types/runConsole";
import type { RunEvent } from "@/types/runEvent";

const props = withDefaults(defineProps<RunResultHighlight>(), {
  response: null,
  requirement: "",
  liveEvents: () => [],
  isJavaMode: false,
  running: false,
  errorDetail: "",
});

type NormalizedEvent = {
  eventType: string;
  eventText: string;
  agent: string;
  status: string;
  message: string;
  createdAt: string;
  detailJson?: string;
};

const summary = computed(() => props.response?.run_summary);
const platformRunId = computed(() => props.response?.platform_run_id || props.response?.platformRunId || "");
const reportPath = computed(() => summary.value?.report_path || props.response?.ui_view_model.report?.report_path || "");
const workflowEvents = computed<NormalizedEvent[]>(() =>
  (props.response?.ui_view_model.workflow_events || []).map((event) => {
    const record = event as Record<string, unknown>;

    return {
      eventType: String(record.eventType || record.event_type || ""),
      eventText: String(record.eventText || record.event_text || record.eventType || record.event_type || ""),
      agent: String(record.agent || ""),
      status: String(record.status || ""),
      message: String(record.message || ""),
      createdAt: String(record.createdAt || record.created_at || ""),
      detailJson: typeof record.detailJson === "string" ? record.detailJson : JSON.stringify(record.detail || {}),
    };
  }),
);
const normalizedLiveEvents = computed<NormalizedEvent[]>(() =>
  props.liveEvents.map((event: RunEvent) => ({
    eventType: event.eventType,
    eventText: event.eventText,
    agent: event.agent || "",
    status: event.status || "",
    message: event.message || "",
    createdAt: event.createdAt || "",
    detailJson: event.detailJson,
  })),
);
const allEvents = computed(() => [...workflowEvents.value, ...normalizedLiveEvents.value]);
const codeAgentEvents = computed(() =>
  allEvents.value.filter((event) => {
    const text = `${event.agent} ${event.eventType} ${event.eventText} ${event.message} ${event.detailJson || ""}`.toLowerCase();

    return text.includes("codeagent") || text.includes("code_agent") || text.includes("file");
  }),
);
const latestEvent = computed(() => allEvents.value[allEvents.value.length - 1]);
const statusType = computed(() => {
  if (props.errorDetail || summary.value?.success === false) {
    return "danger";
  }

  if (props.running) {
    return "primary";
  }

  return summary.value?.success ? "success" : "info";
});
const statusText = computed(() => {
  if (props.errorDetail) {
    return "运行失败";
  }

  if (props.running) {
    return "执行中";
  }

  if (!props.response) {
    return "等待运行";
  }

  return summary.value?.success ? "运行成功" : "运行失败";
});
const blockedCodeAgent = computed(() =>
  codeAgentEvents.value.some((event) =>
    /阻断|禁止|blocked|denied|failed|error/i.test(`${event.eventText} ${event.status} ${event.message} ${event.detailJson || ""}`),
  ),
);
const highlightMessage = computed(() => {
  if (props.errorDetail) {
    return props.errorDetail;
  }

  if (props.running) {
    return "AI 工作流正在执行，完成后这里会显示质量评分、事件数量和报告入口。";
  }

  if (!props.response) {
    return "选择模板或填写结构化需求后开始运行，结果会在这里形成一屏可讲的演示摘要。";
  }

  return latestEvent.value?.message || "运行完成，可查看事件、报告 and 回放。";
});

const openFolderLoading = ref(false);
async function openOutputDirectory() {
  openFolderLoading.value = true;
  try {
    const res = await openCodeAgentFolder("output");
    if (res.success) {
      ElMessage.success(res.message || "已成功打开输出文件夹");
    } else {
      ElMessage.error(res.message || "打开输出文件夹失败");
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "打开输出文件夹失败");
  } finally {
    openFolderLoading.value = false;
  }
}
</script>

<template>
  <section class="result-highlight" :class="`state-${statusType}`">
    <div class="highlight-main">
      <div class="status-badge">
        <span>{{ statusText }}</span>
        <strong>{{ summary?.quality_score ?? 0 }}</strong>
        <small>quality</small>
      </div>

      <div class="highlight-copy">
        <div class="highlight-title">
          <strong>运行结果高光区</strong>
          <el-tag :type="statusType" effect="dark">{{ statusText }}</el-tag>
          <el-tag v-if="blockedCodeAgent" type="danger" effect="plain">CodeAgent 阻断</el-tag>
          <el-tag v-if="platformRunId" type="primary" effect="plain">Java RunEvent</el-tag>
        </div>
        <p>{{ highlightMessage }}</p>
        <div class="requirement-snippet">{{ requirement || summary?.requirement || "暂无需求输入" }}</div>
      </div>
    </div>

    <div class="metric-grid">
      <div class="metric-item">
        <span>测试状态</span>
        <strong>{{ summary?.test_success ? "通过" : response ? "未通过" : "--" }}</strong>
      </div>
      <div class="metric-item">
        <span>覆盖率</span>
        <strong>{{ summary?.coverage_percent ?? 0 }}%</strong>
      </div>
      <div class="metric-item">
        <span>修复次数</span>
        <strong>{{ summary?.retry_count ?? 0 }}</strong>
      </div>
      <div class="metric-item">
        <span>事件数量</span>
        <strong>{{ allEvents.length }}</strong>
      </div>
      <div class="metric-item">
        <span>CodeAgent</span>
        <strong>{{ codeAgentEvents.length ? `${codeAgentEvents.length} events` : "未触发" }}</strong>
      </div>
      <div class="metric-item">
        <span>报告</span>
        <strong>{{ reportPath ? "已生成" : "暂无" }}</strong>
      </div>
    </div>

    <div class="shortcut-row">
      <router-link v-if="platformRunId" :to="{ path: '/history', query: { run_id: platformRunId } }">
        History：{{ platformRunId }}
      </router-link>
      <router-link v-if="platformRunId" :to="`/replay/${platformRunId}`">Replay 回放</router-link>
      <router-link v-if="reportPath" to="/reports">报告中心</router-link>
      <a href="#" @click.prevent="openOutputDirectory" style="border-color: #fbd38d; color: #dd6b20;">
        {{ openFolderLoading ? '正在打开...' : '打开输出目录' }}
      </a>
      <span v-if="!platformRunId && isJavaMode" class="muted">运行完成后显示 Java 平台入口</span>
      <span v-if="!isJavaMode" class="muted">Python Direct 模式不展示 Java Replay 入口</span>
    </div>
  </section>
</template>

<style scoped>
.result-highlight {
  display: grid;
  gap: 14px;
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #dbe4ef;
  border-radius: 14px;
  background:
    linear-gradient(135deg, rgba(232, 240, 254, 0.9), rgba(255, 255, 255, 0.72)),
    #ffffff;
  box-shadow: 0 18px 46px rgba(15, 23, 42, 0.08);
}

.result-highlight.state-success {
  border-color: #bbf7d0;
  background:
    linear-gradient(135deg, rgba(230, 244, 234, 0.95), rgba(255, 255, 255, 0.72)),
    #ffffff;
}

.result-highlight.state-danger {
  border-color: #fecaca;
  background:
    linear-gradient(135deg, rgba(252, 232, 230, 0.95), rgba(255, 255, 255, 0.76)),
    #ffffff;
}

.highlight-main,
.highlight-title,
.shortcut-row {
  display: flex;
  align-items: center;
}

.highlight-main {
  gap: 16px;
}

.status-badge {
  display: grid;
  width: 112px;
  height: 112px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 28px;
  background: #1a73e8;
  color: #ffffff;
  box-shadow: 0 18px 34px rgba(26, 115, 232, 0.28);
}

.state-success .status-badge {
  background: #34a853;
  box-shadow: 0 18px 34px rgba(52, 168, 83, 0.24);
}

.state-danger .status-badge {
  background: #ea4335;
  box-shadow: 0 18px 34px rgba(234, 67, 53, 0.22);
}

.status-badge span,
.status-badge small {
  font-size: 12px;
  font-weight: 800;
}

.status-badge strong {
  font-size: 34px;
  line-height: 1;
}

.highlight-copy {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.highlight-title {
  flex-wrap: wrap;
  gap: 8px;
}

.highlight-title strong {
  color: #0f172a;
  font-size: 18px;
}

.highlight-copy p {
  margin: 0;
  color: #334155;
  line-height: 1.55;
}

.requirement-snippet {
  display: -webkit-box;
  overflow: hidden;
  color: #64748b;
  font-size: 13px;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 8px;
}

.metric-item {
  display: grid;
  gap: 4px;
  padding: 10px;
  border: 1px solid rgba(203, 213, 225, 0.76);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.82);
}

.metric-item span {
  color: #64748b;
  font-size: 12px;
}

.metric-item strong {
  overflow: hidden;
  color: #0f172a;
  font-size: 16px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.shortcut-row {
  flex-wrap: wrap;
  gap: 10px;
}

.shortcut-row a {
  padding: 7px 10px;
  border: 1px solid #bfdbfe;
  border-radius: 999px;
  background: #ffffff;
  color: #1a73e8;
  font-size: 12px;
  font-weight: 800;
  text-decoration: none;
}

.shortcut-row a:hover {
  border-color: #1a73e8;
}

.muted {
  color: #64748b;
  font-size: 12px;
}

@media (max-width: 1280px) {
  .metric-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
