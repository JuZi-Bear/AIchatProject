<script setup lang="ts">
import { ArrowLeft, Refresh } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getWorkflowReplay } from "@/api/replay";
import ReplayControlPanel from "@/components/ReplayControlPanel.vue";
import ReplayEventCard from "@/components/ReplayEventCard.vue";
import WorkflowReplayTimeline from "@/components/WorkflowReplayTimeline.vue";
import type { WorkflowReplayData } from "@/types/replay";

const route = useRoute();
const router = useRouter();
const platformRunId = computed(() => String(route.params.platformRunId || ""));
const replay = ref<WorkflowReplayData | null>(null);
const loading = ref(false);
const errorDetail = ref("");
const currentIndex = ref(0);
const playing = ref(false);
const speedMs = ref(800);
let playTimer: ReturnType<typeof window.setInterval> | null = null;

const events = computed(() => replay.value?.events || []);
const currentEvent = computed(() => events.value[currentIndex.value] || null);
const durationText = computed(() => {
  const durationMs = replay.value?.durationMs || 0;
  if (!durationMs) {
    return "未记录";
  }

  if (durationMs < 1000) {
    return `${durationMs} ms`;
  }

  return `${Math.round((durationMs / 1000) * 10) / 10} s`;
});

function statusTagType(status?: string) {
  if (status === "SUCCESS") {
    return "success";
  }

  if (status === "FAILED") {
    return "danger";
  }

  if (status === "RUNNING") {
    return "primary";
  }

  if (status === "CANCELLED") {
    return "warning";
  }

  return "info";
}

function clearPlayTimer() {
  if (playTimer) {
    window.clearInterval(playTimer);
    playTimer = null;
  }
}

function pauseReplay() {
  playing.value = false;
  clearPlayTimer();
}

function nextStep() {
  if (!events.value.length) {
    return;
  }

  if (currentIndex.value >= events.value.length - 1) {
    pauseReplay();
    return;
  }

  currentIndex.value += 1;
}

function previousStep() {
  pauseReplay();
  currentIndex.value = Math.max(0, currentIndex.value - 1);
}

function resetReplay() {
  pauseReplay();
  currentIndex.value = 0;
}

function playReplay() {
  if (!events.value.length || currentIndex.value >= events.value.length - 1) {
    return;
  }

  clearPlayTimer();
  playing.value = true;
  playTimer = window.setInterval(nextStep, speedMs.value);
}

async function loadReplay() {
  if (!platformRunId.value) {
    errorDetail.value = "缺少 platformRunId";
    return;
  }

  loading.value = true;
  errorDetail.value = "";
  pauseReplay();

  try {
    replay.value = await getWorkflowReplay(platformRunId.value);
    currentIndex.value = replay.value.events.length ? 0 : -1;
  } catch (error) {
    replay.value = null;
    errorDetail.value = error instanceof Error ? error.message : "加载工作流回放失败";
    ElMessage.error(errorDetail.value);
  } finally {
    loading.value = false;
  }
}

watch(speedMs, () => {
  if (playing.value) {
    playReplay();
  }
});

onMounted(loadReplay);

onBeforeUnmount(() => {
  clearPlayTimer();
});
</script>

<template>
  <section class="page-stack replay-page">
    <div class="page-header">
      <div>
        <h1>Workflow Replay</h1>
        <p>按事件时间线回放一次 AI 多智能体工作流</p>
      </div>
      <div class="header-actions">
        <el-button :icon="ArrowLeft" @click="router.push('/history')">返回历史</el-button>
        <el-button :icon="Refresh" :loading="loading" @click="loadReplay">刷新</el-button>
      </div>
    </div>

    <el-alert
      v-if="errorDetail"
      :title="errorDetail"
      type="error"
      show-icon
      :closable="false"
    />

    <template v-if="replay">
      <el-card shadow="never" class="replay-summary-card">
        <div class="summary-grid">
          <div>
            <span>Platform Run</span>
            <strong>{{ replay.platformRunId }}</strong>
          </div>
          <div>
            <span>Python Run</span>
            <strong>{{ replay.pythonRunId || "未记录" }}</strong>
          </div>
          <div>
            <span>状态</span>
            <el-tag :type="statusTagType(replay.status)" effect="plain">{{ replay.statusText || replay.status }}</el-tag>
          </div>
          <div>
            <span>质量评分</span>
            <strong>{{ replay.qualityScore }}</strong>
          </div>
          <div>
            <span>事件数量</span>
            <strong>{{ replay.events.length }}</strong>
          </div>
          <div>
            <span>持续时间</span>
            <strong>{{ durationText }}</strong>
          </div>
        </div>
        <div class="requirement-block">{{ replay.requirement || "无需求摘要" }}</div>
      </el-card>

      <ReplayControlPanel
        :current-index="Math.max(currentIndex, 0)"
        :total="events.length"
        :playing="playing"
        :speed-ms="speedMs"
        @previous="previousStep"
        @next="nextStep"
        @play="playReplay"
        @pause="pauseReplay"
        @reset="resetReplay"
        @update:speed-ms="(value) => (speedMs = value)"
      />

      <el-row :gutter="16" align="top">
        <el-col :lg="15" :md="24">
          <section class="panel replay-main-panel" v-loading="loading">
            <div class="panel-title">事件回放时间线</div>
            <WorkflowReplayTimeline :events="events" :current-index="currentIndex" />
          </section>
        </el-col>
        <el-col :lg="9" :md="24">
          <section class="panel current-event-panel">
            <div class="panel-title">当前播放事件</div>
            <ReplayEventCard v-if="currentEvent" :event="currentEvent" active />
            <el-empty v-else description="暂无当前事件" />
          </section>
        </el-col>
      </el-row>
    </template>

    <el-empty v-else-if="!loading && !errorDetail" description="暂无回放数据" />
  </section>
</template>

<style scoped>
.replay-page {
  gap: 14px;
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.replay-summary-card :deep(.el-card__body) {
  padding: 14px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
}

.summary-grid div {
  display: grid;
  gap: 5px;
  min-width: 0;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
}

.summary-grid span {
  color: #64748b;
  font-size: 12px;
}

.summary-grid strong {
  overflow-wrap: anywhere;
  color: #0f172a;
  font-size: 14px;
}

.requirement-block {
  margin-top: 12px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #ffffff;
  color: #334155;
  line-height: 1.55;
}

.replay-main-panel,
.current-event-panel {
  min-height: 520px;
}

@media (max-width: 1280px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
