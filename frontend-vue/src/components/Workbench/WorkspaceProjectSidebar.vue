<script setup lang="ts">
import { computed, ref } from "vue";
import { Folder, Plus, Search, Setting, Tools } from "@element-plus/icons-vue";

import type { WorkspaceConfig } from "@/types/workspace";

const props = defineProps<{
  workspaces: WorkspaceConfig[];
  selectedWorkspaceId: number | null;
  folderPath: string;
  isJavaMode: boolean;
  loading?: boolean;
}>();

const emit = defineEmits<{
  newChat: [];
  selectWorkspace: [workspace: WorkspaceConfig];
  createWorkspace: [rootPath: string];
  updateFolderPath: [rootPath: string];
  openWorkspacePanel: [];
  openTools: [];
  openSettings: [];
}>();

const searchText = ref("");
const newFolderPath = ref("");
const showFolderCreate = ref(false);

const filteredWorkspaces = computed(() => {
  const keyword = searchText.value.trim().toLowerCase();

  if (!keyword) {
    return props.workspaces;
  }

  return props.workspaces.filter((workspace) =>
    `${workspace.name} ${workspace.rootPath}`.toLowerCase().includes(keyword),
  );
});

function submitFolderPath() {
  const rootPath = newFolderPath.value.trim();
  if (!rootPath) {
    showFolderCreate.value = true;
    return;
  }

  emit("updateFolderPath", rootPath);
  emit("createWorkspace", rootPath);
  showFolderCreate.value = false;
}
</script>

<template>
  <aside class="workspace-sidebar">
    <button class="new-chat-button" type="button" @click="$emit('newChat')">
      <el-icon><Plus /></el-icon>
      <span>新对话</span>
    </button>

    <el-input v-model="searchText" class="sidebar-search" placeholder="搜索 Workspace" clearable>
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
    </el-input>

    <div class="sidebar-actions">
      <button type="button" @click="$emit('openTools')">
        <el-icon><Tools /></el-icon>
        <span>工具</span>
      </button>
      <button type="button" @click="$emit('openWorkspacePanel')">
        <el-icon><Folder /></el-icon>
        <span>Workspace</span>
      </button>
    </div>

    <section class="folder-create" :class="{ expanded: showFolderCreate }">
      <button class="compact-create-button" type="button" @click="showFolderCreate = !showFolderCreate">
        <el-icon><Plus /></el-icon>
        <span>{{ isJavaMode ? "新增 / 使用 Workspace" : "使用本地路径" }}</span>
      </button>
      <div v-if="showFolderCreate" class="folder-create-form">
        <el-input
          v-model="newFolderPath"
          placeholder="粘贴文件夹路径"
          size="small"
          :disabled="loading"
          @keydown.enter.prevent="submitFolderPath"
        />
        <el-button size="small" type="primary" :loading="loading" class="full-width" @click="submitFolderPath">
          {{ isJavaMode ? "创建 / 使用" : "使用路径" }}
        </el-button>
        <p class="hint">
          {{ isJavaMode ? "保存为平台 Workspace。" : "使用本地 settings.yaml 白名单。" }}
        </p>
      </div>
    </section>

    <section class="workspace-list-section">
      <div class="section-title">项目</div>
      <div v-if="!filteredWorkspaces.length" class="empty-workspace">
        {{ isJavaMode ? "暂无 Workspace" : "Python Direct" }}
      </div>
      <button
        v-for="workspace in filteredWorkspaces"
        :key="workspace.id || workspace.rootPath"
        type="button"
        class="workspace-row"
        :class="{ active: workspace.id === selectedWorkspaceId || workspace.rootPath === folderPath }"
        @click="$emit('selectWorkspace', workspace)"
      >
        <el-icon><Folder /></el-icon>
        <span class="workspace-main">
          <strong>{{ workspace.name }}</strong>
          <small>{{ workspace.rootPath }}</small>
        </span>
        <em v-if="workspace.isDefault">默认</em>
      </button>
    </section>

    <button class="settings-button" type="button" @click="$emit('openSettings')">
      <el-icon><Setting /></el-icon>
      <span>设置</span>
    </button>
  </aside>
</template>

<style scoped>
.workspace-sidebar {
  position: sticky;
  top: 0;
  align-self: start;
  display: grid;
  gap: 8px;
  width: 264px;
  height: 100%;
  min-height: 0;
  padding: 10px;
  border-right: 1px solid #343741;
  border-radius: 0;
  background: #1f2023;
  color: #f4f4f5;
}

.new-chat-button,
.sidebar-actions button,
.workspace-row,
.settings-button {
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.new-chat-button,
.settings-button {
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 32px;
  padding: 0 8px;
  font-size: 15px;
  font-weight: 800;
}

.sidebar-search :deep(.el-input__wrapper) {
  min-height: 38px;
  border-radius: 14px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.025)),
    #2a2c32;
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.055),
    0 12px 28px rgba(0, 0, 0, 0.16);
}

.sidebar-search :deep(.el-input__inner) {
  color: #f1f3f4;
}

.sidebar-actions {
  display: grid;
  gap: 3px;
}

.sidebar-actions button {
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 32px;
  padding: 7px 8px;
  border-radius: 10px;
  color: #e8eaed;
  font-weight: 700;
}

.sidebar-actions button:hover,
.new-chat-button:hover,
.settings-button:hover {
  background: rgba(255, 255, 255, 0.055);
}

.folder-create {
  display: grid;
  gap: 7px;
  padding: 3px 0 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.compact-create-button {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 100%;
  min-height: 32px;
  padding: 7px 8px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: #f4f4f5;
  cursor: pointer;
  font-weight: 750;
  text-align: left;
}

.compact-create-button:hover {
  background: rgba(255, 255, 255, 0.055);
}

.folder-create-form {
  display: grid;
  gap: 7px;
  padding: 6px;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.035);
}

.section-title {
  margin: 7px 8px 2px;
  color: #9aa0a6;
  font-size: 12px;
  font-weight: 900;
}

.full-width {
  width: 100%;
}

.hint,
.empty-workspace {
  margin: 0;
  color: #9aa0a6;
  font-size: 12px;
  line-height: 1.45;
}

.workspace-list-section {
  display: grid;
  align-content: start;
  gap: 3px;
  min-height: 0;
}

.workspace-row {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr) auto;
  gap: 7px;
  align-items: center;
  width: 100%;
  min-height: 40px;
  padding: 6px 8px;
  border-radius: 10px;
  text-align: left;
  color: #bdc1c6;
}

.workspace-row:hover,
.workspace-row.active {
  background:
    radial-gradient(circle at 100% 0%, rgba(77, 163, 255, 0.16), transparent 42%),
    #2a2c32;
  color: #ffffff;
  box-shadow: inset 0 0 0 1px rgba(77, 163, 255, 0.12);
}

.workspace-main {
  display: grid;
  gap: 1px;
  min-width: 0;
}

.workspace-main strong,
.workspace-main small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.workspace-main small {
  color: #9aa0a6;
  font-size: 11px;
}

.workspace-row em {
  color: #9aa0a6;
  font-size: 11px;
  font-style: normal;
}

.settings-button {
  align-self: end;
  margin-top: auto;
  color: #f1f3f4;
}

@media (max-width: 1080px) {
  .workspace-sidebar {
    position: static;
    width: 100%;
    min-height: auto;
    border-right: 0;
    border-radius: 18px;
  }
}
</style>
