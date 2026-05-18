<script setup lang="ts">
import { Refresh, Search, Star } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";

import {
  currentApiBaseUrl,
  currentApiMode,
  getApiDisconnectedHint,
  getApiModeLabel,
  getConfigSourceLabel,
  getDataModeLabel,
} from "@/api/client";
import { getModels } from "@/api/models";
import { useSettingsStore } from "@/stores/settings";
import type { ModelConfig } from "@/types/model";

const settingsStore = useSettingsStore();
const apiModeLabel = getApiModeLabel();
const dataModeLabel = getDataModeLabel();
const dataSourceLabel = getConfigSourceLabel();
const apiModeDescription =
  currentApiMode === "java"
    ? "当前通过 Java Spring Boot 平台服务读取 Java/MySQL 模型配置。"
    : "当前直连 Python FastAPI Agent Engine。";
const settingsStorageDescription =
  currentApiMode === "java"
    ? "默认模型会优先同步到 Java /api/settings；同步失败时回退到前端 localStorage。当前不会写回 Python 配置文件。"
    : "默认模型配置保存在前端 localStorage，将作为 RunConsole 的默认模型。当前不会写回 Python 配置文件。";
const models = ref<ModelConfig[]>([]);
const loading = ref(false);
const keyword = ref("");
const providerFilter = ref("all");
const enabledFilter = ref("all");

const providerOptions = computed(() => {
  const providers = new Set(models.value.map((model) => model.provider).filter(Boolean));
  return [...providers].sort();
});

const filteredModels = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase();

  return models.value.filter((model) => {
    if (providerFilter.value !== "all" && model.provider !== providerFilter.value) {
      return false;
    }

    if (enabledFilter.value === "enabled" && !model.enabled) {
      return false;
    }

    if (enabledFilter.value === "disabled" && model.enabled) {
      return false;
    }

    if (!normalizedKeyword) {
      return true;
    }

    return `${model.name} ${model.provider} ${model.model}`.toLowerCase().includes(normalizedKeyword);
  });
});

function isCurrentDefault(model: ModelConfig) {
  return settingsStore.selectedModelProvider === model.provider;
}

function isApiDefault(model: ModelConfig) {
  return Boolean(model.default || model.is_default);
}

function apiKeyWarning(model: ModelConfig) {
  if (model.api_key_configured === false) {
    return "API Key 未配置";
  }

  if (!model.env_key) {
    return "未声明 API Key 环境变量";
  }

  return "";
}

async function loadModels() {
  loading.value = true;

  try {
    await settingsStore.loadSettings();
    models.value = await getModels();
    const selectedExists = models.value.some((model) => model.provider === settingsStore.selectedModelProvider);
    const firstEnabled = models.value.find((model) => model.enabled) || models.value[0];

    if (!selectedExists && firstEnabled) {
      settingsStore.setSelectedModelProvider(firstEnabled.provider);
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : `${getApiDisconnectedHint()}，加载模型配置失败`);
  } finally {
    loading.value = false;
  }
}

function selectDefaultModel(model: ModelConfig) {
  settingsStore.setSelectedModelProvider(model.provider);
  ElMessage.success(`当前前端默认模型已设置为 ${model.name || model.provider}`);
}

onMounted(loadModels);
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <h1>Models</h1>
        <p>查看可用模型，并选择当前前端默认模型</p>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="loadModels">刷新</el-button>
    </div>

    <el-alert
      :title="settingsStorageDescription"
      type="info"
      show-icon
      :closable="false"
    />

    <div class="mode-tags">
      <el-tag type="warning" effect="plain">当前数据模式：{{ dataModeLabel }}</el-tag>
      <el-tag type="primary" effect="plain">当前数据来源：{{ dataSourceLabel }}</el-tag>
    </div>

    <el-alert
      :title="`当前 API 模式：${apiModeLabel}`"
      :description="`${apiModeDescription}API 地址：${currentApiBaseUrl}。模式由 .env 控制，如需切换请修改 VITE_API_MODE；后续可升级为运行时切换。`"
      type="warning"
      show-icon
      :closable="false"
    />

    <section class="panel">
      <div class="model-toolbar">
        <el-input v-model="keyword" :prefix-icon="Search" clearable placeholder="搜索模型名称 / provider / model" />
        <el-select v-model="providerFilter">
          <el-option label="全部 Provider" value="all" />
          <el-option v-for="provider in providerOptions" :key="provider" :label="provider" :value="provider" />
        </el-select>
        <el-select v-model="enabledFilter">
          <el-option label="全部状态" value="all" />
          <el-option label="可用" value="enabled" />
          <el-option label="未启用" value="disabled" />
        </el-select>
      </div>

      <el-empty v-if="!loading && !filteredModels.length" description="暂无模型配置" />
      <el-table v-else :data="filteredModels" stripe v-loading="loading">
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="provider" label="Provider" width="120" />
        <el-table-column prop="model" label="Model" min-width="180" />
        <el-table-column prop="base_url" label="Base URL" min-width="260" show-overflow-tooltip />
        <el-table-column prop="env_key" label="Env Key" width="170" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <div class="tag-stack">
              <el-tag :type="row.enabled ? 'success' : 'info'" effect="plain">
                {{ row.enabled ? "可用" : "未启用" }}
              </el-tag>
              <el-tag v-if="isApiDefault(row)" type="primary" effect="plain">后端默认</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="API Key" width="150">
          <template #default="{ row }">
            <el-tag v-if="apiKeyWarning(row)" type="warning" effect="plain">
              {{ apiKeyWarning(row) }}
            </el-tag>
            <el-tag v-else type="success" effect="plain">已声明</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="前端默认" width="140">
          <template #default="{ row }">
            <el-tag v-if="isCurrentDefault(row)" type="success" effect="dark">
              默认
            </el-tag>
            <el-button v-else size="small" :icon="Star" @click="selectDefaultModel(row)">
              设为默认
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </section>
  </section>
</template>

<style scoped>
.model-toolbar {
  display: grid;
  grid-template-columns: 1fr 180px 140px;
  gap: 10px;
  margin-bottom: 14px;
}

.mode-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

@media (max-width: 1280px) {
  .model-toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
