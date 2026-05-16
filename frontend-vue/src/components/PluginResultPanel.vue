<script setup lang="ts">
import { computed } from "vue";

import type { PluginOutputs, PluginResult } from "@/types/run";

const props = defineProps<{
  pluginOutputs?: PluginOutputs;
}>();

const legacyFields = [
  ["Doc Agent", "doc_result"],
  ["Security Agent", "security_result"],
  ["Refactor Agent", "refactor_result"],
  ["UI Agent", "ui_result"],
] as const;

const pluginRows = computed<PluginResult[]>(() => {
  const pluginResults = props.pluginOutputs?.plugin_results;

  if (Array.isArray(pluginResults) && pluginResults.length) {
    return pluginResults;
  }

  return legacyFields.map(([pluginName, fieldName]) => {
    const detail = String(props.pluginOutputs?.[fieldName] || "");

    return {
      plugin_name: pluginName,
      status: detail ? "success" : "disabled",
      summary: detail ? "已生成插件结果" : "暂无输出",
      detail,
    };
  });
});

function pluginName(row: PluginResult) {
  return row.plugin_name || row.name || "Unknown Plugin";
}

function tagType(status?: string) {
  if (status === "success") {
    return "success";
  }

  if (status === "failed") {
    return "danger";
  }

  if (status === "warning") {
    return "warning";
  }

  return "info";
}
</script>

<template>
  <div class="plugin-grid">
    <el-card v-for="row in pluginRows" :key="pluginName(row)" shadow="never" class="plugin-card">
      <template #header>
        <div class="plugin-head">
          <span>{{ pluginName(row) }}</span>
          <el-tag :type="tagType(row.status)" effect="plain" size="small">
            {{ row.status || "unknown" }}
          </el-tag>
        </div>
      </template>
      <div class="plugin-summary">{{ row.summary || "无摘要" }}</div>
      <pre v-if="row.detail" class="plugin-detail">{{ row.detail }}</pre>
    </el-card>
  </div>
</template>

<style scoped>
.plugin-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.plugin-card :deep(.el-card__header) {
  padding: 10px 12px;
}

.plugin-card :deep(.el-card__body) {
  padding: 12px;
}

.plugin-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-weight: 700;
}

.plugin-summary {
  color: #334155;
  line-height: 1.6;
}

.plugin-detail {
  max-height: 220px;
  margin: 10px 0 0;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: #475569;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  line-height: 1.55;
}

@media (max-width: 1280px) {
  .plugin-grid {
    grid-template-columns: 1fr;
  }
}
</style>
