<script setup lang="ts">
import {
  Bell,
  Document,
  Folder,
  FolderOpened,
  Setting,
  Tools,
} from "@element-plus/icons-vue";

import type { WorkbenchSidePanelName } from "@/types/interaction";

const props = defineProps<{
  activePanel: WorkbenchSidePanelName | null;
  eventCount?: number;
  outputCount?: number;
}>();

const emit = defineEmits<{
  toggle: [panel: WorkbenchSidePanelName];
}>();

const items: Array<{
  key: WorkbenchSidePanelName;
  label: string;
  icon: typeof Setting;
}> = [
  { key: "settings", label: "设置", icon: Setting },
  { key: "workspace", label: "工作区", icon: Folder },
  { key: "tools", label: "CodeAgent", icon: Tools },
  { key: "output", label: "Output", icon: FolderOpened },
  { key: "events", label: "事件", icon: Bell },
];

function badgeFor(key: WorkbenchSidePanelName) {
  if (key === "events") {
    return props.eventCount || 0;
  }

  if (key === "output") {
    return props.outputCount || 0;
  }

  return 0;
}
</script>

<template>
  <nav class="workbench-side-rail" aria-label="工作台侧栏">
    <button
      v-for="item in items"
      :key="item.key"
      class="rail-button"
      :class="{ active: activePanel === item.key }"
      type="button"
      :title="item.label"
      @click="emit('toggle', item.key)"
    >
      <el-badge :value="badgeFor(item.key)" :hidden="badgeFor(item.key) <= 0" :max="99">
        <el-icon><component :is="item.icon" /></el-icon>
      </el-badge>
      <span>{{ item.label }}</span>
    </button>
    <div class="rail-separator" />
    <el-tooltip content="核心区域保持对话和输入框，其他功能用侧栏随用随开。" placement="left">
      <el-icon class="rail-help"><Document /></el-icon>
    </el-tooltip>
  </nav>
</template>

<style scoped>
.workbench-side-rail {
  position: absolute;
  top: 18px;
  right: 18px;
  z-index: 30;
  display: grid;
  gap: 8px;
  width: 64px;
  padding: 8px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 22px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.055), rgba(255, 255, 255, 0.02)),
    rgba(23, 25, 31, 0.96);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.045),
    0 18px 52px rgba(0, 0, 0, 0.34);
  backdrop-filter: blur(10px);
}

.rail-button {
  display: grid;
  place-items: center;
  gap: 4px;
  min-height: 52px;
  border: 0;
  border-radius: 16px;
  background: transparent;
  color: #a1a1aa;
  cursor: pointer;
  transition:
    background 160ms ease,
    color 160ms ease,
    transform 160ms ease;
}

.rail-button:hover,
.rail-button.active {
  background:
    radial-gradient(circle at 100% 0%, rgba(77, 163, 255, 0.2), transparent 46%),
    rgba(77, 163, 255, 0.1);
  color: #4da3ff;
  box-shadow: inset 0 0 0 1px rgba(77, 163, 255, 0.14);
}

.rail-button:active {
  transform: scale(0.97);
}

.rail-button span {
  max-width: 48px;
  overflow: hidden;
  font-size: 11px;
  font-weight: 800;
  line-height: 1;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rail-button :deep(.el-icon) {
  font-size: 18px;
}

.rail-separator {
  height: 1px;
  margin: 2px 6px;
  background: #343741;
}

.rail-help {
  justify-self: center;
  color: #71717a;
}

@media (max-width: 980px) {
  .workbench-side-rail {
    top: auto;
    right: 12px;
    bottom: 12px;
    grid-template-columns: repeat(5, 1fr);
    width: auto;
    border-radius: 18px;
  }

  .rail-button {
    min-width: 48px;
  }

  .rail-button span,
  .rail-separator,
  .rail-help {
    display: none;
  }
}
</style>
