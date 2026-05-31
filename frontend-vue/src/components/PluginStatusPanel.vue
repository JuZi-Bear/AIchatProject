<script setup lang="ts">
import type { PluginConfig } from "@/types/plugin";

defineProps<{
  plugins: PluginConfig[];
  enabledPlugins: string[];
  loading?: boolean;
  error?: string;
}>();

function pluginValue(plugin: PluginConfig) {
  return plugin.display_name || plugin.name;
}

function isFrontendEnabled(plugin: PluginConfig, enabledPlugins: string[]) {
  return enabledPlugins.includes(pluginValue(plugin));
}
</script>

<template>
  <el-card shadow="never" class="dashboard-card" v-loading="loading">
    <template #header>
      <div class="card-header">
        <span>插件状态</span>
        <div class="plugin-counts">
          <el-tag effect="plain">总数 {{ plugins.length }}</el-tag>
          <el-tag type="success" effect="plain">前端启用 {{ enabledPlugins.length }}</el-tag>
        </div>
      </div>
    </template>

    <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
    <el-empty v-else-if="!plugins.length && !loading" description="暂无插件配置" />

    <div v-else class="plugin-list">
      <article v-for="plugin in plugins" :key="pluginValue(plugin)" class="plugin-item">
        <div>
          <div class="plugin-title">{{ pluginValue(plugin) }}</div>
          <div class="plugin-desc">{{ plugin.description || "暂无插件说明" }}</div>
        </div>
        <div class="tag-row">
          <el-tag :type="isFrontendEnabled(plugin, enabledPlugins) ? 'success' : 'info'" effect="plain" size="small">
            {{ isFrontendEnabled(plugin, enabledPlugins) ? "运行启用" : "运行关闭" }}
          </el-tag>
          <el-tag :type="plugin.enabled ? 'success' : 'info'" effect="plain" size="small">
            API {{ plugin.enabled ? "启用" : "关闭" }}
          </el-tag>
        </div>
      </article>
    </div>
  </el-card>
</template>

<style scoped>
.dashboard-card {
  height: 100%;
  border-radius: 8px;
}

.card-header,
.plugin-counts,
.plugin-item,
.tag-row {
  display: flex;
  align-items: center;
}

.card-header {
  justify-content: space-between;
  gap: 10px;
}

.plugin-counts,
.tag-row {
  flex-wrap: wrap;
  gap: 6px;
}

.plugin-list {
  display: grid;
  gap: 9px;
}

.plugin-item {
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #17191f;
}

.plugin-title {
  color: #0f172a;
  font-weight: 800;
}

.plugin-desc {
  margin-top: 3px;
  color: #64748b;
  line-height: 1.45;
}

.tag-row {
  justify-content: flex-end;
}
</style>
