<script setup lang="ts">
import { computed, reactive, watch } from "vue";
import { Check, Document, MagicStick, Search, Upload, Warning } from "@element-plus/icons-vue";

import type { WorkspaceAction, WorkspaceExtendedSettings } from "@/types/interaction";
import type { WorkspaceConfig, WorkspaceSafetyStatus } from "@/types/workspace";

const props = defineProps<{
  workspace?: WorkspaceConfig;
  folderPath: string;
  includePatterns: string;
  excludePatterns: string;
  outputFile: string;
  maxFiles: number;
  maxReadChars: number;
  dryRunDefault: boolean;
  backupBeforeWrite: boolean;
  safety: WorkspaceSafetyStatus;
  loading?: boolean;
}>();

const emit = defineEmits<{
  "update:folderPath": [value: string];
  "update:includePatterns": [value: string];
  "update:excludePatterns": [value: string];
  "update:outputFile": [value: string];
  saveWorkspace: [settings: WorkspaceExtendedSettings & { rootPath: string }];
  runAction: [action: WorkspaceAction];
}>();

const draft = reactive({
  folderPath: props.folderPath,
  includePatterns: props.includePatterns,
  excludePatterns: props.excludePatterns,
  outputFile: props.outputFile,
  maxFiles: props.maxFiles,
  maxReadChars: props.maxReadChars,
  dryRunDefault: props.dryRunDefault,
  backupBeforeWrite: props.backupBeforeWrite,
});

const actions: Array<{
  key: WorkspaceAction;
  title: string;
  description: string;
  icon: typeof Search;
}> = [
  { key: "scan", title: "文件夹扫描", description: "读取文件树和安全摘要。", icon: Search },
  { key: "markdown_summary", title: "生成 Markdown 汇总", description: "将结果整合到输出 Markdown。", icon: Document },
  { key: "dry_run_diff", title: "dry-run diff 预览", description: "只生成计划和 diff，不写入。", icon: MagicStick },
  { key: "apply", title: "应用到文件夹", description: "按已审核计划写入目录。", icon: Upload },
  { key: "blocked_check", title: "阻断路径安全测试", description: "验证敏感路径阻断。", icon: Warning },
];

const safetyType = computed(() => props.safety.type);

watch(
  () => [
    props.folderPath,
    props.includePatterns,
    props.excludePatterns,
    props.outputFile,
    props.maxFiles,
    props.maxReadChars,
    props.dryRunDefault,
    props.backupBeforeWrite,
  ],
  () => {
    draft.folderPath = props.folderPath;
    draft.includePatterns = props.includePatterns;
    draft.excludePatterns = props.excludePatterns;
    draft.outputFile = props.outputFile;
    draft.maxFiles = props.maxFiles;
    draft.maxReadChars = props.maxReadChars;
    draft.dryRunDefault = props.dryRunDefault;
    draft.backupBeforeWrite = props.backupBeforeWrite;
  },
);

function syncFolderFields() {
  emit("update:folderPath", draft.folderPath);
  emit("update:includePatterns", draft.includePatterns);
  emit("update:excludePatterns", draft.excludePatterns);
  emit("update:outputFile", draft.outputFile);
}

function saveWorkspace() {
  syncFolderFields();
  emit("saveWorkspace", {
    rootPath: draft.folderPath,
    includePatterns: draft.includePatterns,
    excludePatterns: draft.excludePatterns,
    outputFile: draft.outputFile,
    maxFiles: draft.maxFiles,
    maxReadChars: draft.maxReadChars,
    dryRunDefault: draft.dryRunDefault,
    backupBeforeWrite: draft.backupBeforeWrite,
  });
}

function runAction(action: WorkspaceAction) {
  syncFolderFields();
  emit("runAction", action);
}
</script>

<template>
  <section class="workspace-action-panel">
    <div class="workspace-summary">
      <strong>{{ workspace?.name || "当前文件夹" }}</strong>
      <span>{{ draft.folderPath || "未选择文件夹" }}</span>
      <el-tag :type="safetyType" effect="plain">{{ safety.message }}</el-tag>
    </div>

    <el-form label-position="top" class="workspace-form">
      <el-form-item label="Workspace root">
        <el-input v-model="draft.folderPath" placeholder="output/code_agent_workspace" />
      </el-form-item>

      <el-form-item label="include patterns">
        <el-input v-model="draft.includePatterns" placeholder="**/*.py, **/*.md" />
      </el-form-item>

      <el-form-item label="exclude patterns">
        <el-input v-model="draft.excludePatterns" placeholder=".env, .git/**, node_modules/**" />
      </el-form-item>

      <el-form-item label="默认 Markdown 输出文件">
        <el-input v-model="draft.outputFile" placeholder="code_agent_folder_result.md" />
      </el-form-item>

      <div class="limit-grid">
        <el-form-item label="max files">
          <el-input-number v-model="draft.maxFiles" :min="1" :max="500" controls-position="right" />
        </el-form-item>
        <el-form-item label="max read chars">
          <el-input-number v-model="draft.maxReadChars" :min="1000" :max="2000000" controls-position="right" />
        </el-form-item>
      </div>

      <div class="workspace-switches">
        <el-switch v-model="draft.dryRunDefault" active-text="默认 dry-run" inactive-text="直接写入" />
        <el-switch v-model="draft.backupBeforeWrite" active-text="写入前备份" inactive-text="不备份" />
      </div>

      <el-button type="primary" plain :icon="Check" :loading="loading" @click="saveWorkspace">
        保存 Workspace 设置
      </el-button>
    </el-form>

    <details class="action-list">
      <summary>
        <span>
          <strong>高级动作</strong>
          <small>默认一键生成会自动采用扫描、dry-run、备份、审计策略。</small>
        </span>
      </summary>
      <div class="action-list-body">
        <button
          v-for="action in actions"
          :key="action.key"
          type="button"
          class="action-card"
          :disabled="loading"
          @click="runAction(action.key)"
        >
          <el-icon><component :is="action.icon" /></el-icon>
          <span>
            <strong>{{ action.title }}</strong>
            <small>{{ action.description }}</small>
          </span>
        </button>
      </div>
    </details>
  </section>
</template>

<style scoped>
.workspace-action-panel {
  display: grid;
  gap: 14px;
}

.workspace-summary {
  display: grid;
  gap: 6px;
  padding: 12px;
  border: 1px solid #343741;
  border-radius: 16px;
  background: #22252d;
}

.workspace-summary strong {
  color: #f4f4f5;
}

.workspace-summary span {
  color: #a1a1aa;
  font-size: 12px;
  overflow-wrap: anywhere;
}

.workspace-form {
  display: grid;
  gap: 2px;
}

.limit-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.workspace-switches {
  display: grid;
  gap: 10px;
  margin-bottom: 10px;
}

.action-list {
  display: grid;
  gap: 8px;
}

.action-list summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px;
  border: 1px solid #343741;
  border-radius: 14px;
  background: #22252d;
  color: #f4f4f5;
  cursor: pointer;
  list-style: none;
}

.action-list summary::-webkit-details-marker {
  display: none;
}

.action-list summary::after {
  color: #a1a1aa;
  font-size: 18px;
  content: "+";
}

.action-list[open] summary::after {
  content: "-";
}

.action-list summary span {
  display: grid;
  gap: 3px;
}

.action-list summary strong {
  font-size: 14px;
  font-weight: 900;
}

.action-list summary small {
  color: #a1a1aa;
  font-size: 12px;
  line-height: 1.35;
}

.action-list-body {
  display: grid;
  gap: 8px;
  margin-top: 8px;
}

.action-card {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
  width: 100%;
  padding: 12px;
  border: 1px solid #343741;
  border-radius: 14px;
  background: #17191f;
  color: #f4f4f5;
  text-align: left;
  cursor: pointer;
}

.action-card:hover {
  border-color: #4da3ff;
  background: #22252d;
}

.action-card:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-card span {
  display: grid;
  gap: 3px;
}

.action-card small {
  color: #a1a1aa;
}

.workspace-action-panel :deep(.el-form-item__label) {
  color: #d4d4d8;
}

.workspace-action-panel :deep(.el-input__wrapper),
.workspace-action-panel :deep(.el-input-number__decrease),
.workspace-action-panel :deep(.el-input-number__increase) {
  background: #17191f;
  box-shadow: 0 0 0 1px #343741 inset;
}

.workspace-action-panel :deep(.el-input__inner) {
  color: #f4f4f5;
}
</style>
