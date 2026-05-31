<script setup lang="ts">
import type { ModelConfig } from "@/types/model";

defineProps<{
  models: ModelConfig[];
  selectedModelProvider: string;
  loading?: boolean;
  error?: string;
}>();

function modelTitle(model: ModelConfig) {
  return model.name || model.provider || model.model || "unknown-model";
}

function isCurrentModel(model: ModelConfig, selectedProvider: string) {
  return [model.provider, model.name, model.model].filter(Boolean).includes(selectedProvider);
}

function hasApiKeyWarning(model: ModelConfig) {
  if (model.api_key_configured === false) {
    return true;
  }

  return !model.offline_mode && !model.env_key;
}

function enabledCount(models: ModelConfig[]) {
  return models.filter((model) => model.enabled).length;
}
</script>

<template>
  <el-card shadow="never" class="dashboard-card" v-loading="loading">
    <template #header>
      <div class="card-header">
        <span>模型状态</span>
        <el-tag type="success" effect="plain">可用 {{ enabledCount(models) }}</el-tag>
      </div>
    </template>

    <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
    <el-empty v-else-if="!models.length && !loading" description="暂无模型配置" />

    <div v-else class="model-panel">
      <div class="current-model">
        <span>当前前端默认模型</span>
        <el-tag type="primary" effect="plain">{{ selectedModelProvider || "未选择" }}</el-tag>
      </div>

      <div class="model-list">
        <article v-for="model in models" :key="`${model.provider}-${model.model}-${model.name}`" class="model-item">
          <div class="model-main">
            <div>
              <div class="model-title">{{ modelTitle(model) }}</div>
              <div class="model-subtitle">{{ model.provider || "provider" }} / {{ model.model || "model" }}</div>
            </div>
            <div class="tag-row">
              <el-tag :type="model.enabled ? 'success' : 'info'" effect="plain" size="small">
                {{ model.enabled ? "可用" : "未启用" }}
              </el-tag>
              <el-tag v-if="isCurrentModel(model, selectedModelProvider)" type="primary" effect="plain" size="small">
                前端默认
              </el-tag>
              <el-tag v-if="hasApiKeyWarning(model)" type="warning" effect="plain" size="small">
                API Key 缺失
              </el-tag>
            </div>
          </div>
        </article>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.dashboard-card {
  height: 100%;
  border-radius: 8px;
}

.card-header,
.current-model,
.model-main,
.tag-row {
  display: flex;
  align-items: center;
}

.card-header,
.current-model,
.model-main {
  justify-content: space-between;
  gap: 10px;
}

.current-model {
  padding: 10px 12px;
  border-radius: 8px;
  background: #101218;
  color: #475569;
}

.model-list {
  display: grid;
  gap: 9px;
  margin-top: 10px;
}

.model-item {
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #17191f;
}

.model-title {
  color: #0f172a;
  font-weight: 800;
}

.model-subtitle {
  margin-top: 3px;
  overflow-wrap: anywhere;
  color: #64748b;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.tag-row {
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
}
</style>
