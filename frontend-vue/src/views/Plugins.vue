<script setup lang="ts">
import { Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";

import { getPlugins } from "@/api/plugins";
import { useSettingsStore } from "@/stores/settings";
import type { PluginConfig } from "@/types/plugin";

const settingsStore = useSettingsStore();
const plugins = ref<PluginConfig[]>([]);
const loading = ref(false);
const keyword = ref("");
const statusFilter = ref("all");

const filteredPlugins = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase();

  return plugins.value.filter((plugin) => {
    const enabled = isPluginEnabled(plugin);

    if (statusFilter.value === "enabled" && !enabled) {
      return false;
    }

    if (statusFilter.value === "disabled" && enabled) {
      return false;
    }

    if (!normalizedKeyword) {
      return true;
    }

    return `${plugin.display_name} ${plugin.name} ${plugin.description}`.toLowerCase().includes(normalizedKeyword);
  });
});

function pluginValue(plugin: PluginConfig) {
  return plugin.display_name || plugin.name;
}

function isPluginEnabled(plugin: PluginConfig) {
  return settingsStore.enabledPlugins.includes(pluginValue(plugin));
}

function resultTagType(status?: string) {
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

async function loadPlugins() {
  loading.value = true;

  try {
    plugins.value = await getPlugins();
    settingsStore.hydratePluginDefaults(
      plugins.value.filter((plugin) => plugin.enabled).map((plugin) => pluginValue(plugin)),
    );
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "加载插件配置失败");
  } finally {
    loading.value = false;
  }
}

function togglePlugin(plugin: PluginConfig, enabled: boolean) {
  settingsStore.togglePlugin(pluginValue(plugin), enabled);
  ElMessage.success(`${plugin.display_name || plugin.name} 已${enabled ? "启用" : "关闭"}`);
}

onMounted(loadPlugins);
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <h1>Plugins</h1>
        <p>查看插件列表，并管理本次前端默认启用状态</p>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="loadPlugins">刷新</el-button>
    </div>

    <el-alert
      title="当前配置保存于前端 localStorage，将在运行任务时生效；暂不写回 config/agents.yaml。"
      type="info"
      show-icon
      :closable="false"
    />

    <section class="panel">
      <div class="plugin-toolbar">
        <el-input v-model="keyword" :prefix-icon="Search" clearable placeholder="搜索插件名称 / key / 描述" />
        <el-select v-model="statusFilter">
          <el-option label="全部状态" value="all" />
          <el-option label="已启用" value="enabled" />
          <el-option label="已关闭" value="disabled" />
        </el-select>
      </div>

      <el-empty v-if="!loading && !filteredPlugins.length" description="暂无插件配置" />
      <div v-else class="plugin-grid" v-loading="loading">
        <el-card v-for="plugin in filteredPlugins" :key="plugin.name" shadow="never" class="plugin-card">
          <template #header>
            <div class="plugin-head">
              <div>
                <div class="plugin-title">{{ plugin.display_name || plugin.name }}</div>
                <div class="plugin-key">{{ plugin.name }}</div>
              </div>
              <el-switch
                :model-value="isPluginEnabled(plugin)"
                active-text="启用"
                inactive-text="关闭"
                @change="(value: string | number | boolean) => togglePlugin(plugin, Boolean(value))"
              />
            </div>
          </template>

          <p class="plugin-description">{{ plugin.description || "暂无说明" }}</p>
          <div class="plugin-status-row">
            <el-tag :type="isPluginEnabled(plugin) ? 'success' : 'info'" effect="plain">
              {{ isPluginEnabled(plugin) ? "运行时启用" : "运行时关闭" }}
            </el-tag>
            <el-tag :type="plugin.enabled ? 'success' : 'info'" effect="plain">
              后端配置：{{ plugin.enabled ? "启用" : "关闭" }}
            </el-tag>
          </div>

          <div class="plugin-result">
            <el-tag :type="resultTagType(plugin.latest_result?.status)" size="small" effect="plain">
              最近结果：{{ plugin.latest_result?.status || "暂无" }}
            </el-tag>
            <div class="plugin-result-summary">
              {{ plugin.latest_result?.summary || "当前 API 暂未返回最近一次执行结果" }}
            </div>
          </div>
        </el-card>
      </div>
    </section>
  </section>
</template>

<style scoped>
.plugin-toolbar {
  display: grid;
  grid-template-columns: 1fr 140px;
  gap: 10px;
  margin-bottom: 14px;
}

.plugin-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.plugin-card :deep(.el-card__header) {
  padding: 12px;
}

.plugin-card :deep(.el-card__body) {
  padding: 12px;
}

.plugin-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.plugin-title {
  color: #0f172a;
  font-weight: 800;
}

.plugin-key {
  margin-top: 4px;
  color: #64748b;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.plugin-description {
  min-height: 44px;
  margin: 0;
  color: #334155;
  line-height: 1.6;
}

.plugin-status-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.plugin-result {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.plugin-result-summary {
  margin-top: 8px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.5;
}

@media (max-width: 1280px) {
  .plugin-toolbar,
  .plugin-grid {
    grid-template-columns: 1fr;
  }
}
</style>
