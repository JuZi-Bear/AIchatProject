<script setup lang="ts">
import { Download, FolderOpened, Plus, Refresh, Upload } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, reactive, ref } from "vue";

import { currentApiMode } from "@/api/client";
import { instantiateWorkflow, savePlatformWorkflowTemplate } from "@/api/workflows";
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
const templateSelection = ref("");
const saveDialogVisible = ref(false);
const instantiateDialogVisible = ref(false);
const instantiating = ref(false);
const savingPlatform = ref(false);
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
</style>
