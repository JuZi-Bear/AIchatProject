<script setup lang="ts">
import { Microphone, Plus, Top } from "@element-plus/icons-vue";
import { computed } from "vue";

import type { CodeAgentFolderTemplate } from "@/types/codeAgent";
import type { FolderWorkflowRunMode } from "@/types/interaction";
import type { ModelConfig } from "@/types/model";
import type { WorkspaceConfig, WorkspaceSafetyStatus } from "@/types/workspace";
import type { WorkflowTemplateData } from "@/types/workflowEditor";

const props = defineProps<{
  modelValue: string;
  running: boolean;
  demoMode: boolean;
  apiModeLabel: string;
  statusText: string;
  models: ModelConfig[];
  loadingOptions: boolean;
  modelProvider: string;
  runMode: FolderWorkflowRunMode;
  activePluginCount: number;
  workspaces: WorkspaceConfig[];
  workspaceId: number | null;
  workspaceLoading: boolean;
  folderPath: string;
  workspaceSafety: WorkspaceSafetyStatus;
  folderTemplates: CodeAgentFolderTemplate[];
  folderTemplateKey: string;
  platformTemplates: WorkflowTemplateData[];
  platformTemplateKey: string;
  templateLoading: boolean;
  outputFile: string;
  dryRun: boolean;
  backupBeforeWrite: boolean;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: string];
  "update:modelProvider": [value: string];
  "update:runMode": [value: FolderWorkflowRunMode];
  "update:workspaceId": [value: number | null];
  "update:folderPath": [value: string];
  "update:folderTemplateKey": [value: string];
  "update:platformTemplateKey": [value: string];
  "update:outputFile": [value: string];
  "update:dryRun": [value: boolean];
  "update:backupBeforeWrite": [value: boolean];
  submit: [];
  startDemo: [];
  openBuilder: [];
  openTools: [];
  openOutput: [];
  openWorkspace: [];
  workspaceChange: [];
  templateChange: [];
}>();

const safetyTagType = computed(() => props.workspaceSafety.type);
const selectedFolderTemplate = computed(() =>
  props.folderTemplates.find((template) => template.key === props.folderTemplateKey),
);
const selectedPlatformTemplate = computed(() =>
  props.platformTemplates.find((template) => template.workflowTemplateKey === props.platformTemplateKey),
);
const selectedWorkspace = computed(() =>
  props.workspaces.find((workspace) => workspace.id === props.workspaceId),
);
const usesPlatformTemplate = computed(
  () => props.runMode === "runtime_lite" || props.runMode === "dynamic_langgraph",
);
const workspaceLabel = computed(() => selectedWorkspace.value?.name || props.folderPath || "选择文件夹");
const templateLabel = computed(() =>
  usesPlatformTemplate.value
    ? selectedPlatformTemplate.value?.name || "平台模板"
    : selectedFolderTemplate.value?.name || "文件夹工作流",
);
const selectedModel = computed(() => props.models.find((model) => model.provider === props.modelProvider));
const modelLabel = computed(() => {
  const model = selectedModel.value;

  if (!model) {
    return props.modelProvider || "选择模型";
  }

  return `${model.name} / ${model.model}`;
});
const accessLabel = computed(() => {
  if (props.workspaceSafety.type === "danger") {
    return "受限路径";
  }

  if (props.workspaceSafety.type === "warning") {
    return "检查访问权限";
  }

  if (props.workspaceSafety.mode === "python-direct") {
    return "本地白名单";
  }

  return "完全访问权限";
});
const primaryButtonText = computed(() => {
  if (props.runMode === "code_agent_ai_generate") {
    return "AI 一键生成";
  }

  if (props.runMode === "agent_run") {
    return "开始运行";
  }

  if (props.runMode === "runtime_lite") {
    return "执行 Runtime";
  }

  if (props.runMode === "dynamic_langgraph") {
    return "执行图";
  }

  return props.dryRun ? "生成计划" : "运行工作流";
});

function updateRequirement(value: string) {
  emit("update:modelValue", value);
}

function updateModelProvider(value: string | number | boolean) {
  emit("update:modelProvider", String(value));
}

function updateWorkspaceId(value: string | number | boolean | undefined) {
  emit("update:workspaceId", typeof value === "number" ? value : null);
}

function updateFolderPath(value: string | number) {
  emit("update:folderPath", String(value));
}

function updateFolderTemplateKey(value: string | number | boolean) {
  emit("update:folderTemplateKey", String(value));
}

function updatePlatformTemplateKey(value: string | number | boolean) {
  emit("update:platformTemplateKey", String(value));
}

function updateOutputFile(value: string | number) {
  emit("update:outputFile", String(value));
}

function updateDryRun(value: string | number | boolean) {
  emit("update:dryRun", Boolean(value));
}

function updateBackupBeforeWrite(value: string | number | boolean) {
  emit("update:backupBeforeWrite", Boolean(value));
}
</script>

<template>
  <section class="composer-bar">
    <div class="composer-input-shell">
      <el-input
        :model-value="modelValue"
        type="textarea"
        :autosize="{ minRows: 1, maxRows: 5 }"
        resize="none"
        class="composer-input"
        placeholder="描述你想生成或修改的项目"
        :disabled="running"
        @update:model-value="updateRequirement"
        @keydown.ctrl.enter.prevent="$emit('submit')"
        @keydown.meta.enter.prevent="$emit('submit')"
      />
    </div>

    <div class="composer-control-row">
      <div class="composer-left-controls">
        <button class="composer-icon-button" type="button" title="打开工具" @click="$emit('openTools')">
          <el-icon><Plus /></el-icon>
        </button>
        <button
          class="access-control"
          :class="`tone-${safetyTagType}`"
          type="button"
          :title="`${workspaceLabel} · ${templateLabel} · ${workspaceSafety.message}`"
          @click="$emit('openWorkspace')"
        >
          <span class="access-shield">!</span>
          <span>{{ accessLabel }}</span>
          <span class="access-caret">⌄</span>
        </button>
      </div>

      <div class="composer-right-controls">
        <el-select
          :model-value="modelProvider"
          class="inline-model-select"
          :loading="loadingOptions"
          placeholder="AI 模型"
          :disabled="running"
          :title="modelLabel"
          @update:model-value="updateModelProvider"
        >
          <el-option
            v-for="model in models"
            :key="model.provider"
            :label="`${model.name} / ${model.model}`"
            :value="model.provider"
          />
        </el-select>
        <button class="composer-icon-button muted" type="button" title="语音输入占位" disabled>
          <el-icon><Microphone /></el-icon>
        </button>
        <el-button
          class="send-button"
          :icon="Top"
          circle
          type="primary"
          :loading="running"
          :disabled="running || !modelValue.trim()"
          :title="primaryButtonText"
          @click="$emit('submit')"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.composer-bar {
  display: grid;
  gap: 4px;
  padding: 14px 14px 10px;
  border: 1px solid rgba(255, 255, 255, 0.055);
  border-radius: 28px;
  background:
    radial-gradient(circle at 100% 100%, rgba(77, 163, 255, 0.06), transparent 30%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.052), rgba(255, 255, 255, 0.018)),
    #272727;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.045),
    0 18px 46px rgba(0, 0, 0, 0.34);
  backdrop-filter: blur(12px);
}

.composer-input-shell {
  min-height: 38px;
  padding: 0 4px;
}

.composer-control-row,
.composer-left-controls,
.composer-right-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.composer-control-row {
  justify-content: space-between;
  min-height: 38px;
}

.composer-left-controls,
.composer-right-controls {
  min-width: 0;
}

.composer-input :deep(.el-textarea__inner) {
  min-height: 34px !important;
  padding: 0;
  border: 0;
  background: transparent !important;
  box-shadow: none !important;
  color: #f4f4f5;
  font-size: 15.5px;
  font-weight: 520;
  line-height: 1.55;
  caret-color: #f4f4f5;
}

.composer-input :deep(.el-textarea__inner::placeholder) {
  color: #b7b7bd;
  opacity: 0.9;
}

.composer-input :deep(.el-textarea__inner:focus) {
  box-shadow: none !important;
}

.composer-input :deep(.el-textarea__inner:hover) {
  box-shadow: none !important;
}

.composer-icon-button,
.access-control {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  background: transparent;
  color: #e5e7eb;
  cursor: pointer;
  transition:
    background 150ms ease,
    color 150ms ease,
    opacity 150ms ease,
    transform 150ms ease;
}

.composer-icon-button {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  color: #c9c9ce;
  font-size: 18px;
}

.composer-icon-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.075);
  color: #ffffff;
}

.composer-icon-button:disabled {
  cursor: default;
  opacity: 0.48;
}

.access-control {
  gap: 7px;
  min-height: 30px;
  padding: 0 7px;
  border-radius: 999px;
  color: #f97316;
  font-size: 13px;
  font-weight: 750;
}

.access-control:hover {
  background: rgba(249, 115, 22, 0.1);
}

.access-control.tone-success {
  color: #4ade80;
}

.access-control.tone-warning,
.access-control.tone-info {
  color: #f97316;
}

.access-control.tone-danger {
  color: #fb7185;
}

.access-shield {
  display: inline-grid;
  width: 17px;
  height: 17px;
  place-items: center;
  border: 1px solid currentColor;
  border-radius: 7px 7px 9px 9px;
  font-size: 11px;
  line-height: 1;
}

.access-caret {
  margin-left: -3px;
  color: currentColor;
  opacity: 0.82;
}

.inline-model-select {
  width: 176px;
}

.inline-model-select :deep(.el-select__wrapper) {
  min-height: 30px;
  border-radius: 999px;
  background: transparent !important;
  box-shadow: none !important;
}

.inline-model-select :deep(.el-select__selected-item),
.inline-model-select :deep(.el-select__placeholder) {
  justify-content: flex-end;
  color: #f4f4f5;
  font-size: 14px;
  font-weight: 700;
}

.inline-model-select :deep(.el-select__suffix) {
  color: #a1a1aa;
}

.send-button {
  width: 40px !important;
  height: 40px !important;
  border-radius: 999px !important;
  background: #f4f4f5 !important;
  color: #111113 !important;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.28) !important;
}

.send-button:hover,
.send-button:focus {
  background: #ffffff !important;
  color: #08090b !important;
  transform: translateY(-1px);
}

@media (max-width: 720px) {
  .composer-control-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .composer-right-controls {
    width: 100%;
    justify-content: space-between;
  }

  .inline-model-select {
    flex: 1;
    width: auto;
  }
}
</style>
