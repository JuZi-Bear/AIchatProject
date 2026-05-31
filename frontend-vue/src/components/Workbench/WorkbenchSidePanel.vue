<script setup lang="ts">
import { Close } from "@element-plus/icons-vue";

defineProps<{
  visible: boolean;
  title: string;
  subtitle?: string;
  statusText?: string;
  eventCount?: number;
  outputCount?: number;
  workspaceLabel?: string;
  modelLabel?: string;
}>();

const emit = defineEmits<{
  close: [];
}>();
</script>

<template>
  <Transition name="side-panel">
    <aside v-if="visible" class="workbench-side-panel">
      <header class="side-panel-head">
        <div>
          <h2>{{ title }}</h2>
          <p v-if="subtitle">{{ subtitle }}</p>
        </div>
        <el-button :icon="Close" circle text @click="emit('close')" />
      </header>
      <section class="side-panel-summary">
        <div class="summary-section">
          <span class="summary-title">进度</span>
          <div class="progress-row complete">
            <span class="progress-dot">✓</span>
            <span>检查当前 Composer、Workspace 和工具状态</span>
          </div>
          <div class="progress-row" :class="{ complete: Boolean(outputCount) }">
            <span class="progress-dot">{{ outputCount ? "✓" : "○" }}</span>
            <span>产物 / 输出 {{ outputCount || 0 }}</span>
          </div>
          <div class="progress-row" :class="{ complete: Boolean(eventCount) }">
            <span class="progress-dot">{{ eventCount ? "✓" : "○" }}</span>
            <span>事件 {{ eventCount || 0 }}</span>
          </div>
        </div>
        <div class="summary-section">
          <span class="summary-title">环境信息</span>
          <div class="env-row"><span>状态</span><strong>{{ statusText || "ready" }}</strong></div>
          <div class="env-row"><span>工作区</span><strong>{{ workspaceLabel || "未选择" }}</strong></div>
          <div class="env-row"><span>模型</span><strong>{{ modelLabel || "default" }}</strong></div>
        </div>
      </section>
      <div class="side-panel-body">
        <slot />
      </div>
    </aside>
  </Transition>
</template>

<style scoped>
.workbench-side-panel {
  position: absolute;
  top: 16px;
  right: 96px;
  bottom: 16px;
  z-index: 26;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  width: min(420px, calc(100% - 132px));
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 24px;
  background:
    radial-gradient(circle at 100% 0%, rgba(77, 163, 255, 0.1), transparent 30%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.012)),
    rgba(23, 25, 31, 0.98);
  color: #f4f4f5;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.045),
    0 24px 68px rgba(0, 0, 0, 0.42);
  backdrop-filter: blur(12px);
}

.side-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 18px 12px;
  border-bottom: 1px solid #343741;
}

.side-panel-head h2 {
  margin: 0;
  color: #f4f4f5;
  font-size: 18px;
}

.side-panel-head p {
  margin: 5px 0 0;
  color: #a1a1aa;
  font-size: 13px;
  line-height: 1.45;
}

.side-panel-body {
  min-height: 0;
  padding: 14px 16px 16px;
  overflow: auto;
}

.side-panel-summary {
  display: grid;
  gap: 12px;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.018);
}

.summary-section {
  display: grid;
  gap: 8px;
}

.summary-title {
  color: #8e8e95;
  font-size: 13px;
  font-weight: 850;
}

.progress-row,
.env-row {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr);
  gap: 8px;
  align-items: center;
  color: #a1a1aa;
  font-size: 13px;
  line-height: 1.4;
}

.progress-row.complete {
  color: #d7d7dc;
}

.progress-dot {
  display: grid;
  width: 18px;
  height: 18px;
  place-items: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: #c9c9ce;
  font-size: 11px;
  font-weight: 900;
}

.progress-row.complete .progress-dot {
  background: rgba(244, 244, 245, 0.72);
  color: #17191f;
}

.env-row {
  grid-template-columns: 72px minmax(0, 1fr);
}

.env-row span {
  color: #8e8e95;
}

.env-row strong {
  overflow: hidden;
  color: #f4f4f5;
  font-weight: 720;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.side-panel-enter-active,
.side-panel-leave-active {
  transition:
    opacity 180ms ease,
    transform 220ms cubic-bezier(0.2, 0, 0, 1);
}

.side-panel-enter-from,
.side-panel-leave-to {
  opacity: 0;
  transform: translateX(24px) scale(0.98);
}

@media (max-width: 980px) {
  .workbench-side-panel {
    inset: 12px;
    width: auto;
    border-radius: 20px;
  }
}
</style>
