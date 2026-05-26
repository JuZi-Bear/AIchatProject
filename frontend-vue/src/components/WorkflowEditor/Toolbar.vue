<script setup lang="ts">
import { Delete, Download, FolderOpened, MoreFilled, Plus, Refresh, Upload, View } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { currentApiMode } from "@/api/client";
import {
  deletePlatformWorkflowTemplate,
  executePlatformWorkflowTemplate,
  instantiatePlatformWorkflowTemplate,
  instantiateWorkflow,
  savePlatformWorkflowTemplate,
} from "@/api/workflows";
import type { InstantiateWorkflowResponse, WorkflowTemplate } from "@/types/workflow";
import type { WorkflowTemplateData, WorkflowValidationIssue } from "@/types/workflowEditor";

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
const executingRuntime = ref(false);
const executingSelectedPlatform = ref(false);
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

function escapeHtml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

async function confirmNewBlankWorkflow() {
  try {
    await ElMessageBox.confirm("确认清空当前画布并新建空白 Workflow？", "新建空白", {
      confirmButtonText: "确认清空",
      cancelButtonText: "取消",
      type: "warning",
    });
    store.newBlankWorkflow();
    ElMessage.success("已新建空白 Workflow");
  } catch {
    // User cancelled.
  }
}

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
      store.autoLayoutNodes();
      ElMessage.success("已加载并整理 API Workflow 模板");
    }
  } else if (source === "platform") {
    const template = props.platformTemplates.find((item) => item.workflowTemplateKey === key);

    if (template) {
      store.loadTemplateData(template);
      store.autoLayoutNodes();
      ElMessage.success("已加载并整理 MySQL Workflow 模板");
    }
  } else {
    const template = store.savedTemplates.find((item) => item.workflowTemplateKey === key);

    if (template) {
      store.loadTemplateData(template);
      store.autoLayoutNodes();
      ElMessage.success("已加载并整理本地 Workflow 模板");
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

function issueHtml(issues: WorkflowValidationIssue[]) {
  const errors = issues.filter((issue) => issue.severity === "error");
  const warnings = issues.filter((issue) => issue.severity === "warning");
  const list = (items: WorkflowValidationIssue[]) =>
    items.map((issue) => `<li><strong>${escapeHtml(issue.title)}</strong>：${escapeHtml(issue.message)}</li>`).join("");

  return `
    <div class="workflow-check-result">
      ${errors.length ? `<p><b>阻断问题 ${errors.length} 个</b></p><ul>${list(errors)}</ul>` : ""}
      ${warnings.length ? `<p><b>提醒 ${warnings.length} 个</b></p><ul>${list(warnings)}</ul>` : ""}
    </div>
  `;
}

async function runWorkflowCheck(showSuccess = true) {
  const issues = store.validateWorkflow();
  const errors = issues.filter((issue) => issue.severity === "error");

  if (issues.length) {
    await ElMessageBox.alert(issueHtml(issues), errors.length ? "流程检查未通过" : "流程检查提醒", {
      confirmButtonText: "知道了",
      type: errors.length ? "error" : "warning",
      dangerouslyUseHTMLString: true,
    });
  } else if (showSuccess) {
    ElMessage.success("流程检查通过，可以保存模板或生成任务");
  }

  return errors.length === 0;
}

function previewExecutionOrder() {
  if (!store.nodes.length) {
    ElMessage.warning("当前画布暂无节点");
    return;
  }

  const rows = store.orderedNodes
    .map((node, index) => `<li><b>${index + 1}. ${escapeHtml(node.name)}</b><br/><span>${escapeHtml(node.stage)} · ${escapeHtml(node.agentKey)}</span></li>`)
    .join("");

  ElMessageBox.alert(`<ol class="execution-preview">${rows}</ol>`, "预览执行顺序", {
    confirmButtonText: "关闭",
    dangerouslyUseHTMLString: true,
  });
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

async function executeSelectedPlatformTemplate() {
  const template = selectedTemplateInfo.value;

  if (!template || template.source !== "platform") {
    ElMessage.warning("只有 MySQL 模板支持 Runtime Lite 执行");
    return;
  }

  executingSelectedPlatform.value = true;

  try {
    const result = await executePlatformWorkflowTemplate(template.key, {
      requirement: `执行 Workflow Runtime Lite: ${template.name}`,
      editor_mode: true,
      runtime_mode: "workflow_runtime_lite",
    });
    lastResult.value = result;
    emit("instantiated", result);
    detailDialogVisible.value = false;
    ElMessage.success("Workflow Runtime Lite 已执行，正在打开回放");
    await router.push(`/replay/${result.platformRunId}`);
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "执行 Workflow Runtime Lite 失败");
  } finally {
    executingSelectedPlatform.value = false;
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

async function openInstantiateDialog() {
  if (await runWorkflowCheck(false)) {
    instantiateDialogVisible.value = true;
  }
}

async function createTask() {
  if (!(await runWorkflowCheck(false))) {
    return;
  }

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

async function executeCurrentWorkflowRuntime() {
  if (!isJavaMode) {
    ElMessage.warning("执行模板工作流仅 Java Gateway 模式支持");
    return;
  }

  if (!(await runWorkflowCheck(false))) {
    return;
  }

  executingRuntime.value = true;
  lastResult.value = null;

  try {
    const template = store.saveCurrentTemplate(
      store.workflowTemplateKey || `runtime_${Date.now()}`,
      store.workflowName || "Runtime Lite Workflow",
      store.workflowDescription,
    );
    await savePlatformWorkflowTemplate(template);
    emit("reloadTemplates");

    const result = await executePlatformWorkflowTemplate(template.workflowTemplateKey, {
      requirement:
        instantiateForm.requirement.trim() ||
        `执行 Workflow Runtime Lite: ${template.name || template.workflowTemplateKey}`,
      editor_mode: true,
      runtime_mode: "workflow_runtime_lite",
    });
    lastResult.value = result;
    emit("instantiated", result);
    ElMessage.success("Workflow Runtime Lite 已执行，正在打开回放");
    await router.push(`/replay/${result.platformRunId}`);
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "执行 Workflow Runtime Lite 失败");
  } finally {
    executingRuntime.value = false;
  }
}
</script>

<template>
  <el-card shadow="never" class="toolbar-card">
    <div class="toolbar-grid">
      <section class="toolbar-group">
        <span class="group-label">工作流操作</span>
        <div class="group-actions">
          <el-button :icon="Plus" plain @click="confirmNewBlankWorkflow">新建空白</el-button>
          <el-select v-model="templateSelection" placeholder="加载 Workflow 模板" class="template-select">
            <el-option v-for="option in templateOptions" :key="option.value" :label="option.label" :value="option.value" />
          </el-select>
          <el-button :icon="FolderOpened" :loading="props.loadingTemplates" plain @click="loadSelectedTemplate">
            加载模板
          </el-button>
          <el-button :disabled="!store.nodes.length" plain @click="store.autoLayoutNodes">自动整理</el-button>
        </div>
      </section>

      <section class="toolbar-group">
        <span class="group-label">预览与校验</span>
        <div class="group-actions">
          <el-button :icon="View" plain @click="runWorkflowCheck()">检查流程</el-button>
          <el-button plain @click="previewExecutionOrder">预览执行顺序</el-button>
        </div>
      </section>

      <section class="toolbar-group primary-group">
        <span class="group-label">主要动作</span>
        <div class="group-actions">
          <el-button :icon="Upload" type="primary" plain @click="openSaveDialog">保存模板</el-button>
          <el-button
            v-if="isJavaMode"
            type="primary"
            :loading="executingRuntime"
            @click="executeCurrentWorkflowRuntime"
          >
            执行模板工作流
          </el-button>
          <el-button type="success" class="create-task-button" @click="openInstantiateDialog">生成任务</el-button>
          <el-dropdown trigger="click">
            <el-button :icon="MoreFilled" circle plain />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :icon="View" :disabled="!selectedTemplateInfo" @click="showTemplateDetails">
                  模板详情
                </el-dropdown-item>
                <el-dropdown-item :icon="Refresh" @click="emit('reloadTemplates')">刷新模板</el-dropdown-item>
                <el-dropdown-item :icon="Download" @click="exportJson">导出 JSON</el-dropdown-item>
                <el-dropdown-item
                  v-if="isJavaMode"
                  :icon="Delete"
                  :disabled="selectedTemplateInfo?.source !== 'platform'"
                  @click="deleteSelectedPlatformTemplate"
                >
                  删除 MySQL 模板
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </section>
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
        type="primary"
        :loading="executingSelectedPlatform"
        @click="executeSelectedPlatformTemplate"
      >
        执行模板工作流
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
  border: 1px solid #dadce0;
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 8px 22px rgba(60, 64, 67, 0.08);
}

.toolbar-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(280px, 0.75fr) auto;
  gap: 16px;
  align-items: end;
}

.toolbar-group {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.group-label {
  color: #5f6368;
  font-size: 12px;
  font-weight: 800;
}

.group-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.primary-group {
  justify-self: end;
}

.template-select {
  width: min(280px, 100%);
}

.create-task-button {
  min-width: 104px;
  font-weight: 800;
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

:global(.workflow-check-result ul),
:global(.execution-preview) {
  margin: 8px 0 0;
  padding-left: 20px;
}

:global(.workflow-check-result li),
:global(.execution-preview li) {
  margin: 8px 0;
  line-height: 1.5;
}

:global(.execution-preview span) {
  color: #5f6368;
  font-size: 12px;
}

@media (max-width: 1180px) {
  .toolbar-grid {
    grid-template-columns: 1fr;
  }

  .primary-group {
    justify-self: stretch;
  }
}
</style>
