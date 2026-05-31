<script setup lang="ts">
import { Close } from "@element-plus/icons-vue";

defineProps<{
  visible: boolean;
  title: string;
  subtitle?: string;
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
  padding: 16px;
  overflow: auto;
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
