<script setup lang="ts">
import { Delete, Edit, Plus, Refresh, Star } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";

import { currentApiMode, getApiDisconnectedHint, getApiModeLabel } from "@/api/client";
import { createWorkspace, deleteWorkspace, getWorkspaces, updateWorkspace } from "@/api/workspaces";
import type { WorkspaceConfig } from "@/types/workspace";
import { createDefaultWorkspace } from "@/types/workspace";

const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const workspaces = ref<WorkspaceConfig[]>([]);
const form = reactive<WorkspaceConfig>(createDefaultWorkspace());

const enabledWorkspaces = computed(() => workspaces.value.filter((workspace) => workspace.enabled));
const defaultWorkspace = computed(
  () => workspaces.value.find((workspace) => workspace.isDefault) || enabledWorkspaces.value[0],
);

function resetForm(workspace?: WorkspaceConfig) {
  const next = workspace || createDefaultWorkspace();
  editingId.value = workspace?.id ?? null;
  form.id = next.id;
  form.name = next.name;
  form.rootPath = next.rootPath;
  form.enabled = next.enabled;
  form.isDefault = next.isDefault;
  form.description = next.description || "";
  form.maxFiles = next.maxFiles || 80;
  form.maxReadChars = next.maxReadChars || 500000;
  form.dryRunDefault = next.dryRunDefault;
  form.backupBeforeWrite = next.backupBeforeWrite;
}

async function loadWorkspaces() {
  if (currentApiMode !== "java") {
    workspaces.value = [];
    return;
  }

  loading.value = true;

  try {
    workspaces.value = await getWorkspaces();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : `${getApiDisconnectedHint()}，加载 Workspace 失败`);
  } finally {
    loading.value = false;
  }
}

function openCreateDialog() {
  resetForm();
  dialogVisible.value = true;
}

function openEditDialog(workspace: WorkspaceConfig) {
  resetForm(workspace);
  dialogVisible.value = true;
}

async function saveWorkspace() {
  if (!form.name.trim() || !form.rootPath.trim()) {
    ElMessage.warning("请填写 Workspace 名称和根目录");
    return;
  }

  saving.value = true;

  try {
    const payload = { ...form, name: form.name.trim(), rootPath: form.rootPath.trim() };

    if (editingId.value) {
      await updateWorkspace(editingId.value, payload);
    } else {
      await createWorkspace(payload);
    }

    ElMessage.success("Workspace 配置已保存");
    dialogVisible.value = false;
    await loadWorkspaces();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存 Workspace 失败");
  } finally {
    saving.value = false;
  }
}

async function setDefaultWorkspace(workspace: WorkspaceConfig) {
  if (!workspace.id) {
    return;
  }

  try {
    await updateWorkspace(workspace.id, { ...workspace, enabled: true, isDefault: true });
    ElMessage.success(`默认 Workspace 已切换到 ${workspace.name}`);
    await loadWorkspaces();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "设置默认 Workspace 失败");
  }
}

async function removeWorkspace(workspace: WorkspaceConfig) {
  if (!workspace.id) {
    return;
  }

  try {
    await ElMessageBox.confirm(`确认删除 Workspace「${workspace.name}」？`, "删除 Workspace", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
    await deleteWorkspace(workspace.id);
    ElMessage.success("Workspace 已删除");
    await loadWorkspaces();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error(error instanceof Error ? error.message : "删除 Workspace 失败");
    }
  }
}

onMounted(loadWorkspaces);
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <h1>Workspace</h1>
        <p>管理 CodeAgent 文件夹模式使用的受控工作区</p>
      </div>
      <div class="header-actions">
        <el-tag :type="currentApiMode === 'java' ? 'success' : 'warning'" effect="plain">
          {{ getApiModeLabel() }}
        </el-tag>
        <el-button :icon="Refresh" :loading="loading" @click="loadWorkspaces">刷新</el-button>
        <el-button type="primary" :icon="Plus" :disabled="currentApiMode !== 'java'" @click="openCreateDialog">
          新增 Workspace
        </el-button>
      </div>
    </div>

    <el-alert
      v-if="currentApiMode !== 'java'"
      title="Python Direct 模式继续使用 config/settings.yaml 中的 CodeAgent 白名单。Workspace 配置仅 Java Gateway + MySQL 模式支持。"
      type="warning"
      show-icon
      :closable="false"
    />

    <el-card shadow="never" class="workspace-summary">
      <div>
        <span>当前默认工作区</span>
        <strong>{{ defaultWorkspace?.name || "暂无 Workspace" }}</strong>
        <p>{{ defaultWorkspace?.rootPath || "请在 Java Gateway 模式下新增受控工作区。" }}</p>
      </div>
      <div class="summary-tags">
        <el-tag type="primary" effect="plain">启用 {{ enabledWorkspaces.length }}</el-tag>
        <el-tag type="success" effect="plain">dry-run 优先</el-tag>
        <el-tag type="warning" effect="plain">Python 仍做最终安全裁判</el-tag>
      </div>
    </el-card>

    <el-empty v-if="!loading && !workspaces.length" description="暂无 Workspace 配置" />

    <div v-else class="workspace-grid">
      <el-card
        v-for="workspace in workspaces"
        :key="workspace.id || workspace.rootPath"
        shadow="never"
        class="workspace-card"
        :class="{ disabled: !workspace.enabled, default: workspace.isDefault }"
      >
        <div class="workspace-card-head">
          <div>
            <div class="workspace-title">
              <strong>{{ workspace.name }}</strong>
              <el-tag v-if="workspace.isDefault" type="success" effect="plain" size="small">默认</el-tag>
              <el-tag v-if="!workspace.enabled" type="info" effect="plain" size="small">禁用</el-tag>
            </div>
            <p>{{ workspace.description || "受控文件夹工作区" }}</p>
          </div>
          <el-button
            :icon="Star"
            circle
            :disabled="workspace.isDefault"
            @click="setDefaultWorkspace(workspace)"
          />
        </div>

        <div class="workspace-path">{{ workspace.rootPath }}</div>

        <div class="workspace-policy">
          <el-tag effect="plain">max files {{ workspace.maxFiles }}</el-tag>
          <el-tag effect="plain">max chars {{ workspace.maxReadChars }}</el-tag>
          <el-tag :type="workspace.dryRunDefault ? 'primary' : 'warning'" effect="plain">
            {{ workspace.dryRunDefault ? "默认 dry-run" : "允许直接写入" }}
          </el-tag>
          <el-tag :type="workspace.backupBeforeWrite ? 'success' : 'warning'" effect="plain">
            {{ workspace.backupBeforeWrite ? "写入前备份" : "不自动备份" }}
          </el-tag>
        </div>

        <div class="workspace-actions">
          <el-button size="small" :icon="Edit" plain @click="openEditDialog(workspace)">编辑</el-button>
          <el-button size="small" :icon="Delete" type="danger" plain @click="removeWorkspace(workspace)">
            删除
          </el-button>
        </div>
      </el-card>
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑 Workspace' : '新增 Workspace'" width="560px">
      <el-form label-position="top">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="CodeAgent Demo Workspace" />
        </el-form-item>
        <el-form-item label="根目录">
          <el-input v-model="form.rootPath" placeholder="output/code_agent_workspace" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="最大文件数">
            <el-input-number v-model="form.maxFiles" :min="1" :max="1000" />
          </el-form-item>
          <el-form-item label="最大读取字符">
            <el-input-number v-model="form.maxReadChars" :min="1000" :step="10000" />
          </el-form-item>
        </div>
        <div class="switch-grid">
          <el-switch v-model="form.enabled" active-text="启用" inactive-text="禁用" />
          <el-switch v-model="form.isDefault" active-text="设为默认" inactive-text="普通工作区" />
          <el-switch v-model="form.dryRunDefault" active-text="默认 dry-run" inactive-text="直接写入" />
          <el-switch v-model="form.backupBeforeWrite" active-text="写入前备份" inactive-text="不备份" />
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveWorkspace">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.header-actions,
.summary-tags,
.workspace-title,
.workspace-actions,
.workspace-policy,
.switch-grid {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.workspace-summary {
  border-radius: 14px;
}

.workspace-summary :deep(.el-card__body) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.workspace-summary span,
.workspace-card p {
  color: #5f6368;
}

.workspace-summary strong {
  display: block;
  margin-top: 4px;
  color: #202124;
  font-size: 22px;
}

.workspace-summary p,
.workspace-card p {
  margin: 6px 0 0;
}

.workspace-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.workspace-card {
  border-radius: 14px;
}

.workspace-card.default {
  border-color: #34a853;
}

.workspace-card.disabled {
  opacity: 0.72;
}

.workspace-card-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.workspace-title strong {
  color: #202124;
  font-size: 16px;
}

.workspace-path {
  margin: 14px 0;
  padding: 10px 12px;
  border: 1px solid #d2e3fc;
  border-radius: 10px;
  background:
    linear-gradient(135deg, rgba(77, 163, 255, 0.14), transparent 42%),
    #17191f;
  color: #174ea6;
  font-family: Consolas, "Liberation Mono", monospace;
  font-size: 13px;
}

.workspace-policy {
  margin-bottom: 14px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.switch-grid {
  align-items: flex-start;
  flex-direction: column;
}
</style>
