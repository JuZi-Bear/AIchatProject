<script setup lang="ts">
import { Delete, Lock, Refresh, Search, Star } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";

import {
  currentApiBaseUrl,
  currentApiMode,
  getApiDisconnectedHint,
  getApiModeLabel,
  getConfigSourceLabel,
  getDataModeLabel,
} from "@/api/client";
import { clearModelSecret, getModelSecrets, getModels, updateModelSecret } from "@/api/models";
import { useSettingsStore } from "@/stores/settings";
import type { ModelConfig, ModelSecretStatus } from "@/types/model";

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
const secretStatuses = ref<ModelSecretStatus[]>([]);
const loading = ref(false);
const secretSaving = ref(false);
const secretDialogVisible = ref(false);
const selectedSecretModel = ref<ModelConfig | null>(null);
const secretForm = reactive({
  apiKey: "",
});
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
const secretStatusByProvider = computed(() => {
  const entries = secretStatuses.value.map((status) => [status.provider, status] as const);
  return new Map(entries);
});

function isCurrentDefault(model: ModelConfig) {
  return settingsStore.selectedModelProvider === model.provider;
}

function isApiDefault(model: ModelConfig) {
  return Boolean(model.default || model.is_default);
}

function apiKeyWarning(model: ModelConfig) {
  const secretStatus = secretStatusByProvider.value.get(model.provider);

  if (secretStatus?.configured) {
    return "";
  }

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
    const [modelsResult, secretsResult] = await Promise.allSettled([getModels(), getModelSecrets()]);
    models.value = modelsResult.status === "fulfilled" ? modelsResult.value : [];
    secretStatuses.value = secretsResult.status === "fulfilled" ? secretsResult.value : [];

    if (modelsResult.status === "rejected") {
      throw modelsResult.reason;
    }

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

function openSecretDialog(model: ModelConfig) {
  if (currentApiMode !== "java") {
    ElMessage.warning("Python Direct 模式请继续使用 .env 配置 API Key");
    return;
  }

  selectedSecretModel.value = model;
  secretForm.apiKey = "";
  secretDialogVisible.value = true;
}

async function saveSecret() {
  if (!selectedSecretModel.value) {
    return;
  }

  if (!secretForm.apiKey.trim()) {
    ElMessage.warning("请输入 API Key");
    return;
  }

  secretSaving.value = true;

  try {
    await updateModelSecret(selectedSecretModel.value.provider, secretForm.apiKey.trim());
    ElMessage.success("API Key 已加密保存到 Java 平台层");
    secretDialogVisible.value = false;
    secretForm.apiKey = "";
    await loadModels();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存 API Key 失败");
  } finally {
    secretSaving.value = false;
  }
}

async function clearSecret(model: ModelConfig) {
  if (currentApiMode !== "java") {
    ElMessage.warning("Python Direct 模式请直接修改 .env");
    return;
  }

  secretSaving.value = true;

  try {
    await clearModelSecret(model.provider);
    ElMessage.success("平台层 API Key 已清除");
    await loadModels();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "清除 API Key 失败");
  } finally {
    secretSaving.value = false;
  }
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
        <el-table-column label="API Key" width="220">
          <template #default="{ row }">
            <div class="secret-cell">
              <el-tag v-if="apiKeyWarning(row)" type="warning" effect="plain">
                {{ apiKeyWarning(row) }}
              </el-tag>
              <el-tag v-else type="success" effect="plain">
                {{ secretStatusByProvider.get(row.provider)?.stored ? "平台已保存" : "已声明" }}
              </el-tag>
              <span v-if="secretStatusByProvider.get(row.provider)?.maskedKey" class="masked-key">
                {{ secretStatusByProvider.get(row.provider)?.maskedKey }}
              </span>
              <div class="secret-actions">
                <el-button size="small" :icon="Lock" plain @click="openSecretDialog(row)">更新</el-button>
                <el-button
                  v-if="secretStatusByProvider.get(row.provider)?.stored"
                  size="small"
                  :icon="Delete"
                  type="danger"
                  plain
                  :loading="secretSaving"
                  @click="clearSecret(row)"
                >
                  清除
                </el-button>
              </div>
            </div>
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

    <el-dialog v-model="secretDialogVisible" title="更新模型 API Key" width="520px">
      <el-alert
        title="密钥只会通过 POST 提交一次，GET 接口只返回 masked 状态；不会保存到浏览器 localStorage。"
        type="warning"
        show-icon
        :closable="false"
        class="secret-hint"
      />
      <el-descriptions v-if="selectedSecretModel" :column="1" border class="secret-desc">
        <el-descriptions-item label="Provider">{{ selectedSecretModel.provider }}</el-descriptions-item>
        <el-descriptions-item label="Env Key">{{ selectedSecretModel.env_key || "未声明" }}</el-descriptions-item>
      </el-descriptions>
      <el-form label-position="top">
        <el-form-item label="API Key">
          <el-input
            v-model="secretForm.apiKey"
            type="password"
            show-password
            clearable
            autocomplete="new-password"
            placeholder="输入新的模型 API Key"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="secretDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="secretSaving" @click="saveSecret">加密保存</el-button>
      </template>
    </el-dialog>
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

.secret-cell {
  display: grid;
  gap: 6px;
}

.masked-key {
  color: #5f6368;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.secret-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.secret-actions :deep(.el-button) {
  margin-left: 0;
}

.secret-hint,
.secret-desc {
  margin-bottom: 12px;
}

@media (max-width: 1280px) {
  .model-toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
