<script setup lang="ts">
import {
  Connection,
  DataAnalysis,
  Files,
  Folder,
  House,
  List,
  Operation,
  Plus,
  Search,
  SetUp,
  Setting,
  Share,
} from "@element-plus/icons-vue";
import { computed } from "vue";

import type { LocalIconKey } from "@/types/codex";

const props = defineProps<{
  name: LocalIconKey;
}>();

const iconMap = {
  dashboard: House,
  run: Operation,
  workflow: Operation,
  editor: DataAnalysis,
  artifacts: Files,
  history: List,
  models: Connection,
  workspace: Folder,
  plugins: SetUp,
  agents: Share,
  settings: Setting,
  search: Search,
  new: Plus,
};

const iconComponent = computed(() => iconMap[props.name] || Operation);
</script>

<template>
  <el-icon class="codex-icon">
    <component :is="iconComponent" />
  </el-icon>
</template>

<style scoped>
.codex-icon {
  color: currentColor;
}
</style>
