<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  outputs?: Record<string, string>;
}>();

const rows = computed(() =>
  Object.entries(props.outputs || {}).filter(([, value]) => value && String(value).trim()),
);
</script>

<template>
  <el-empty v-if="!rows.length" description="暂无 Agent 输出" />
  <el-collapse v-else>
    <el-collapse-item v-for="[key, value] in rows" :key="key" :title="key">
      <pre class="output-block">{{ value }}</pre>
    </el-collapse-item>
  </el-collapse>
</template>
