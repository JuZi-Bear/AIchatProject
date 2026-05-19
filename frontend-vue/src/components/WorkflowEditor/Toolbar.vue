<script setup lang="ts">
import { Delete, Download, FolderOpened, Plus, Refresh, Upload, View } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { currentApiMode } from "@/api/client";
import {
  deletePlatformWorkflowTemplate,
  instantiatePlatformWorkflowTemplate,
  instantiateWorkflow,
  savePlatformWorkflowTemplate,
} from "@/api/workflows";
import type { InstantiateWorkflowResponse, WorkflowTemplate } from "@/types/workflow";
import type { WorkflowTemplateData } from "@/types/workflowEditor";

import { useWorkflowEditorStore } from "./WorkflowEditorStore";

const props = defineProps<{
  templates: WorkflowTemplate[];
  platformTemplates: WorkflowTemplateData[];
  loadingTemplates: boolean;
}>();

const emit = defineEmits<{
  reloadTemplates: [];
  instantiated: [result: InstantiateWorkflowResponse];
}>();

const store = useWorkflowEditorStore();
const router = useRouter();
const templateSelection = ref("");
const saveDialogVisible = ref(false);
const detailDialogVisible = ref(false);
const instantiateDialogVisible = ref(false);
const instantiating = ref(false);
const savingPlatform = ref(false);
const deletingPlatform = ref(false);
const instantiatingPlatform = ref(false);
const lastResult = ref<InstantiateWorkflowResponse | null>(null);
const isJavaMode = currentApiMode === "java";

const saveForm = reactive({
  key: "",
  name: "",
  description: "",
});

const instantiateForm = reactive({
  requirement: "",
});

const templateOptions = computed(() => [
  ...props.templates.map((template) => ({
    value: `api::${template.key}`,
    label: `API · ${template.name}`,
  })),
  ...props.platformTemplates.map((template) => ({
    value: `platform::${template.workflowTemplateKey}`,
    label: `MySQL · ${template.name}`,
  })),
  ...store.savedTemplates.map((template) => ({
    value: `local::${template.workflowTemplateKey}`,
    label: `Local · ${template.name}`,
  })),
]);

const selectedTemplateInfo = computed(() => {
  if (!templateSelection.value) {
    return null;
  }

  const [source, key] = templateSelection.value.split("::");

  if (source === "api") {
    const template = props.templates.find((item) => item.key === key);

    if (!template) {
      return null;
    }

    return {
      source,
      sourceLabel: "API 内置模板",
      key: template.key,
      name: template.name,
      description: template.description,
      version: template.version,
      updatedAt: "",
      nodes: [],
      connections: [],
      agentSequence: template.agent_sequence,
      stageSequence: template.stage_sequence,
    };
  }

  if (source === "platform") {
    const template = props.platformTemplates.find((item) => item.workflowTemplateKey === key);

    if (!template) {
      return null;
    }

    return {
      source,
      sourceLabel: "Java MySQL 模板",
      key: template.workflowTemplateKey,
      name: template.name,
      description: template.description,
      version: template.version,
      updatedAt: template.updatedAt || "",
      nodes: template.nodes,
      connections: template.connections,
      agentSequence: template.nodes.map((node) => node.agentKey).filter(Boolean),
      stageSequence: template.nodes.map((node) => node.stage).filter(Boolean),
    };
  }

  const template = store.savedTemplates.find((item) => item.workflowTemplateKey === key);

  if (!template) {
    return null;
  }

  return {
    source,
    sourceLabel: "浏览器本地模板",
    key: template.workflowTemplateKey,
    name: template.name,
    description: template.description,
    version: template.version,
    updatedAt: template.updatedAt || "",
    nodes: template.nodes,
    connections: template.connections,
    agentSequence: template.nodes.map((node) => node.agentKey).filter(Boolean),
    stageSequence: template.nodes.map((node) => node.stage).filter(Boolean),
  };
});

function loadSelectedTemplate() {
  if (!templateSelection.value) {
    ElMessage.warning("请选择要加载的 Workflow 模板");
    return;
  }

  const [source, key] = templateSelection.value.split("::");

  if (source === "api") {
    const template = props.templates.find((item) => item.key === key);

    if (template) {
      store.loadTemplate(template);
      ElMessage.success("已加载 API Workflow 模板");
    }
  } else if (source === "platform") {
    const template = props.platformTemplates.find((item) => item.workflowTemplateKey === key);

    if (template) {
      store.loadTemplateData(template);
      ElMessage.success("已加载 MySQL Workflow 模板");
    }
  } else {
    const template = store.savedTemplates.find((item) => item.workflowTemplateKey === key);

    if (template) {
      store.loadTemplateData(template);
      ElMessage.success("已加载本地 Workflow 模板");
    }
  }
}

function showTemplateDetails() {
  if (!selectedTemplateInfo.value) {
    ElMessage.warning("请选择要查看的 Workflow 模板");
    return;
  }

  detailDialogVisible.value = true;
}

async function deleteSelectedPlatformTemplate() {
  const template = selectedTemplateInfo.value;

  if (!template || template.source !== "platform") {
    ElMessage.warning("只有 MySQL 模板支持从平台删除");
    return;
  }

  try {
    await ElMessageBox.confirm(`确认删除 MySQL 模板 ${template.name}？`, "删除 Workflow 模板", {
      confirmButtonText: "删除",
      cancelButtonText: "取消",
      type: "warning",
    });

    deletingPlatform.value = true;
    await deletePlatformWorkflowTemplate(template.key);
    templateSelection.value = "";
    detailDialogVisible.value = false;
    emit("reloadTemplates");
    ElMessage.success("MySQL Workflow 模板已删除");
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error(error instanceof Error ? error.message : "删除 MySQL Workflow 模板失败");
    }
  } finally {
    deletingPlatform.value = false;
  }
}

async function instantiateSelectedPlatformTemplate() {
  const template = selectedTemplateInfo.value;

  if (!template || template.source !== "platform") {
    ElMessage.warning("只有 MySQL 模板支持生成可回放任务");
    return;
  }

  instantiatingPlatform.value = true;

  try {
    const result = await instantiatePlatformWorkflowTemplate(template.key, {
      requirement: `从 MySQL Workflow 模板生成回放任务: ${template.name}`,
      editor_mode: true,
      replay_only: true,
    });
    lastResult.value = result;
    emit("instantiated", result);
    detailDialogVisible.value = false;
    ElMessage.success("已生成可回放任务视图");
    await router.push(`/replay/${result.platformRunId}`);
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "生成可回放任务失败");
  } finally {
    instantiatingPlatform.value = false;
  }
}

function openSaveDialog() {
  saveForm.key = store.workflowTemplateKey;
  saveForm.name = store.workflowName;
  saveForm.description = store.workflowDescription;
  saveDialogVisible.value = true;
}

function saveTemplate() {
  store.saveCurrentTemplate(saveForm.key, saveForm.name, saveForm.description);
  saveDialogVisible.value = false;
  ElMessage.success("Workflow 模板已保存到浏览器 localStorage");
}

async function saveTemplateToPlatform() {
  savingPlatform.value = true;

  try {
    const template = store.saveCurrentTemplate(saveForm.key, saveForm.name, saveForm.description);
    await savePlatformWorkflowTemplate(template);
    saveDialogVisible.value = false;
    emit("reloadTemplates");
    ElMessage.success("Workflow 模板已保存到 Java + MySQL");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存 Workflow 模板到 MySQL 失败");
  } finally {
    savingPlatform.value = false;
  }
}

function exportJson() {
  const data = JSON.stringify(store.exportTemplateData(), null, 2);
  const blob = new Blob([data], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${store.workflowTemplateKey || "workflow-template"}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function formatJson(value: unknown) {
  return JSON.stringify(value, null, 2);
}

async function createTask() {
  instantiating.value = true;
  lastResult.value = null;

  try {
    const templateData = JSON.parse(JSON.stringify(store.exportTemplateData())) as Record<string, unknown>;
    const result = await instantiateWorkflow(
      store.workflowTemplateKey || `custom_${Date.now()}`,
      {
        requirement: instantiateForm.requirement.trim(),
        editor_mode: true,
      },
      templateData,
    );
    lastResult.value = result;
    instantiateDialogVisible.value = false;
    emit("instantiated", result);
    ElMessage.success("已通过 Workflow 模板生成任务视图");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "实例化 Workflow 任务失败");
  } finally {
    instantiating.value = false;
  }
}
</script>

<template>
  <el-card shadow="never" class="toolbar-card">
    <div class="toolbar-row">
      <el-button :icon="Plus" @click="store.newBlankWorkflow">新建空白</el-button>
      <el-button :disabled="!store.canUndo" @click="store.undo">撤销</el-button>
      <el-button :disabled="!store.canRedo" @click="store.redo">重做</el-button>
      <el-select v-model="templateSelection" placeholder="加载 Workflow 模板" class="template-select">
        <el-option v-for="option in templateOptions" :key="option.value" :label="option.label" :value="option.value" />
      </el-select>
      <el-button :icon="FolderOpened" :loading="props.loadingTemplates" @click="loadSelectedTemplate">加载模板</el-button>
      <el-button :icon="View" :disabled="!selectedTemplateInfo" @click="showTemplateDetails">模板详情</el-button>
      <el-button
        v-if="isJavaMode"
        :icon="Delete"
        type="danger"
        plain
        :loading="deletingPlatform"
        :disabled="selectedTemplateInfo?.source !== 'platform'"
        @click="deleteSelectedPlatformTemplate"
      >
        删除 MySQL
      </el-button>
      <el-button :icon="Refresh" :loading="props.loadingTemplates" @click="emit('reloadTemplates')">刷新模板</el-button>
      <el-button :icon="Upload" type="primary" plain @click="openSaveDialog">保存模板</el-button>
      <el-button :icon="Download" plain @click="exportJson">导出 JSON</el-button>
      <el-button type="success" @click="instantiateDialogVisible = true">生成任务</el-button>
    </div>

    <el-alert
      v-if="lastResult"
      :title="`最近生成任务视图：${lastResult.platformRunId}`"
      type="success"
      show-icon
      :closable="false"
      class="toolbar-result"
    />
  </el-card>

  <el-dialog v-model="saveDialogVisible" title="保存 Workflow 模板" width="520px">
    <el-alert
      :title="isJavaMode ? 'Java Gateway 模式下可同步保存到 MySQL。' : 'Python Direct 模式仅支持保存到本地浏览器。'"
      type="info"
      show-icon
      :closable="false"
      class="dialog-hint"
    />
    <el-form label-position="top">
      <el-form-item label="模板 Key">
        <el-input v-model="saveForm.key" placeholder="custom_workflow_key" />
      </el-form-item>
      <el-form-item label="模板名称">
        <el-input v-model="saveForm.name" />
      </el-form-item>
      <el-form-item label="模板描述">
        <el-input v-model="saveForm.description" type="textarea" :rows="4" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="saveDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="saveTemplate">保存到本地</el-button>
      <el-button v-if="isJavaMode" type="success" :loading="savingPlatform" @click="saveTemplateToPlatform">
        保存到 MySQL
      </el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="detailDialogVisible" title="Workflow 模板详情" width="760px">
    <el-empty v-if="!selectedTemplateInfo" description="暂无模板详情" />
    <section v-else class="template-detail">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="模板名称">{{ selectedTemplateInfo.name }}</el-descriptions-item>
        <el-descriptions-item label="模板 Key">
          <code>{{ selectedTemplateInfo.key }}</code>
        </el-descriptions-item>
        <el-descriptions-item label="来源">{{ selectedTemplateInfo.sourceLabel }}</el-descriptions-item>
        <el-descriptions-item label="版本">{{ selectedTemplateInfo.version }}</el-descriptions-item>
        <el-descriptions-item label="节点数">{{ selectedTemplateInfo.nodes.length }}</el-descriptions-item>
        <el-descriptions-item label="连线数">{{ selectedTemplateInfo.connections.length }}</el-descriptions-item>
        <el-descriptions-item label="更新时间" :span="2">
          {{ selectedTemplateInfo.updatedAt || "无" }}
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">
          {{ selectedTemplateInfo.description || "暂无描述" }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="detail-section">
        <strong>Agent 顺序</strong>
        <div class="tag-list">
          <el-tag v-for="agent in selectedTemplateInfo.agentSequence" :key="agent" effect="plain">
            {{ agent }}
          </el-tag>
          <el-tag v-if="!selectedTemplateInfo.agentSequence.length" type="info" effect="plain">无</el-tag>
        </div>
      </div>

      <div class="detail-section">
        <strong>阶段顺序</strong>
        <div class="tag-list">
          <el-tag v-for="stage in selectedTemplateInfo.stageSequence" :key="stage" type="success" effect="plain">
            {{ stage }}
          </el-tag>
          <el-tag v-if="!selectedTemplateInfo.stageSequence.length" type="info" effect="plain">无</el-tag>
        </div>
      </div>

      <el-collapse>
        <el-collapse-item title="节点 JSON" name="nodes">
          <pre class="json-preview">{{ formatJson(selectedTemplateInfo.nodes) }}</pre>
        </el-collapse-item>
        <el-collapse-item title="连线 JSON" name="connections">
          <pre class="json-preview">{{ formatJson(selectedTemplateInfo.connections) }}</pre>
        </el-collapse-item>
      </el-collapse>
    </section>
    <template #footer>
      <el-button @click="detailDialogVisible = false">关闭</el-button>
      <el-button
        v-if="isJavaMode && selectedTemplateInfo?.source === 'platform'"
        type="success"
        :loading="instantiatingPlatform"
        @click="instantiateSelectedPlatformTemplate"
      >
        生成可回放任务
      </el-button>
      <el-button
        v-if="isJavaMode && selectedTemplateInfo?.source === 'platform'"
        type="danger"
        :loading="deletingPlatform"
        @click="deleteSelectedPlatformTemplate"
      >
        删除 MySQL 模板
      </el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="instantiateDialogVisible" title="生成 Workflow 任务视图" width="560px">
    <el-alert
      title="当前实例化只生成模板任务视图，不直接执行 LangGraph。"
      type="info"
      show-icon
      :closable="false"
      class="dialog-hint"
    />
    <el-form label-position="top">
      <el-form-item label="任务需求">
        <el-input
          v-model="instantiateForm.requirement"
          type="textarea"
          :rows="5"
          placeholder="输入本次任务需求，用于生成模板任务视图"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="instantiateDialogVisible = false">取消</el-button>
      <el-button type="success" :loading="instantiating" @click="createTask">提交 API</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.toolbar-card {
  border-radius: 8px;
}

.toolbar-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.template-select {
  width: 260px;
}

.toolbar-result,
.dialog-hint {
  margin-top: 12px;
}

.template-detail {
  display: grid;
  gap: 14px;
}

.detail-section {
  display: grid;
  gap: 8px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.json-preview {
  max-height: 260px;
  margin: 0;
  overflow: auto;
  padding: 10px;
  border-radius: 8px;
  background: #0f172a;
  color: #dbeafe;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  line-height: 1.55;
}
</style>
