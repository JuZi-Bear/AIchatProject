<script setup lang="ts">
import { Operation, Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { currentApiMode, getApiModeLabel } from "@/api/client";
import {
  executePlatformWorkflowTemplate,
  exportPlatformWorkflowSkill,
  getPlatformWorkflowTemplates,
  getWorkflowTemplates,
  instantiateWorkflow,
} from "@/api/workflows";
import type { InstantiateWorkflowResponse, WorkflowSkillExportResult, WorkflowTemplate } from "@/types/workflow";
import type { WorkflowTemplateData } from "@/types/workflowEditor";

const apiModeLabel = getApiModeLabel();
const router = useRouter();
const templates = ref<WorkflowTemplate[]>([]);
const platformTemplates = ref<WorkflowTemplateData[]>([]);
const selectedTemplate = ref<WorkflowTemplate | null>(null);
const selectedPlatformTemplate = ref<WorkflowTemplateData | null>(null);
const keyword = ref("");
const stageFilter = ref("all");
const requirement = ref("");
const loading = ref(false);
const creating = ref(false);
const executingRuntime = ref(false);
const exportingSkillKey = ref("");
const createResult = ref<InstantiateWorkflowResponse | null>(null);
const skillExportResult = ref<WorkflowSkillExportResult | null>(null);
const createError = ref("");
const isJavaMode = currentApiMode === "java";

const stageOptions = computed(() => {
  const stages = new Set<string>();
  templates.value.forEach((template) => template.stage_sequence.forEach((stage) => stages.add(stage)));
  return [...stages].sort();
});

const filteredTemplates = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase();

  return templates.value.filter((template) => {
    if (stageFilter.value !== "all" && !template.stage_sequence.includes(stageFilter.value)) {
      return false;
    }

    if (!normalizedKeyword) {
      return true;
    }

    return `${template.key} ${template.name} ${template.description} ${template.agent_sequence.join(" ")}`
      .toLowerCase()
      .includes(normalizedKeyword);
  });
});

function selectTemplate(template: WorkflowTemplate) {
  selectedTemplate.value = template;
  createResult.value = null;
  createError.value = "";
}

async function loadTemplates() {
  loading.value = true;

  try {
    const [apiTemplates, mysqlTemplates] = await Promise.all([
      getWorkflowTemplates(),
      isJavaMode ? getPlatformWorkflowTemplates() : Promise.resolve([]),
    ]);
    templates.value = apiTemplates;
    platformTemplates.value = mysqlTemplates;
    selectedTemplate.value = selectedTemplate.value || templates.value[0] || null;
    selectedPlatformTemplate.value = selectedPlatformTemplate.value || platformTemplates.value[0] || null;
  } catch (error) {
    templates.value = [];
    platformTemplates.value = [];
    selectedTemplate.value = null;
    selectedPlatformTemplate.value = null;
    ElMessage.error(error instanceof Error ? error.message : "加载 Workflow 模板失败");
  } finally {
    loading.value = false;
  }
}

async function createTemplateTask() {
  if (!selectedTemplate.value) {
    ElMessage.warning("请先选择一个 Workflow 模板");
    return;
  }

  creating.value = true;
  createResult.value = null;
  createError.value = "";

  try {
    createResult.value = await instantiateWorkflow(selectedTemplate.value.key, {
      requirement: requirement.value.trim(),
      template_name: selectedTemplate.value.name,
    });
    ElMessage.success("已生成 Workflow 模板任务视图");
  } catch (error) {
    createError.value = error instanceof Error ? error.message : "生成 Workflow 模板任务失败";
    ElMessage.error(createError.value);
  } finally {
    creating.value = false;
  }
}

function runtimeResultMessage(result: InstantiateWorkflowResponse) {
  const summary = result.run_summary || {};
  const status = String(summary.status || "");
  const reportPath = String(summary.report_path || "");
  const waiting = status === "WAITING_FOR_HUMAN" || Boolean(summary.require_human_approval);
  const reportText = reportPath ? `，报告已生成：${reportPath}` : "";

  return waiting
    ? `Workflow Runtime Lite 已执行，当前等待人工确认${reportText}`
    : `Workflow Runtime Lite 已执行，正在打开回放${reportText}`;
}

async function executePlatformTemplate(template = selectedPlatformTemplate.value) {
  if (!template) {
    ElMessage.warning("请先选择一个 Java MySQL Workflow 模板");
    return;
  }

  executingRuntime.value = true;
  createResult.value = null;
  createError.value = "";

  try {
    const result = await executePlatformWorkflowTemplate(template.workflowTemplateKey, {
      requirement: requirement.value.trim() || `执行 Workflow Runtime Lite: ${template.name}`,
      template_name: template.name,
      runtime_mode: "workflow_runtime_lite",
    });
    createResult.value = result;
    ElMessage.success(runtimeResultMessage(result));
    await router.push(`/replay/${result.platformRunId}`);
  } catch (error) {
    createError.value = error instanceof Error ? error.message : "执行 Workflow Runtime Lite 失败";
    ElMessage.error(createError.value);
  } finally {
    executingRuntime.value = false;
  }
}

async function exportSkill(template: WorkflowTemplateData) {
  if (!isJavaMode) {
    ElMessage.warning("Skill 导出仅 Java Gateway 模式支持");
    return;
  }

  exportingSkillKey.value = template.workflowTemplateKey;
  skillExportResult.value = null;

  try {
    const result = await exportPlatformWorkflowSkill(template.workflowTemplateKey);
    skillExportResult.value = result;
    ElMessage.success(`已导出 Skill：${result.skillName}`);
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "导出 Workflow Skill 失败");
  } finally {
    exportingSkillKey.value = "";
  }
}

async function copySkillPath() {
  if (!skillExportResult.value?.skillPath) {
    return;
  }

  try {
    await navigator.clipboard.writeText(skillExportResult.value.skillPath);
    ElMessage.success("Skill 路径已复制");
  } catch {
    ElMessage.info(skillExportResult.value.skillPath);
  }
}

onMounted(loadTemplates);
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <h1>Workflow Templates</h1>
        <p>查看和选择 Python Agent Engine 的可复用工作流模板</p>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="loadTemplates">刷新</el-button>
    </div>

    <div class="mode-tags">
      <el-tag type="primary" effect="plain">API 模式：{{ apiModeLabel }}</el-tag>
      <el-tag type="success" effect="plain">模板数量：{{ templates.length }}</el-tag>
      <el-tag type="warning" effect="plain">当前为模板实例化预览，不直接运行 LangGraph</el-tag>
    </div>

    <section class="panel">
      <div class="workflow-filters">
        <el-input v-model="keyword" :prefix-icon="Search" clearable placeholder="搜索模板名称 / key / Agent" />
        <el-select v-model="stageFilter" class="stage-select">
          <el-option label="全部阶段" value="all" />
          <el-option v-for="stage in stageOptions" :key="stage" :label="stage" :value="stage" />
        </el-select>
      </div>

      <el-empty v-if="!loading && !filteredTemplates.length" description="暂无 Workflow 模板" />
      <div v-else class="workflow-layout" v-loading="loading">
        <div class="template-list">
          <article
            v-for="template in filteredTemplates"
            :key="template.key"
            class="template-card"
            :class="{ active: selectedTemplate?.key === template.key }"
            @click="selectTemplate(template)"
          >
            <div class="template-head">
              <div>
                <div class="template-name">{{ template.name }}</div>
                <div class="template-key">{{ template.key }} · v{{ template.version }}</div>
              </div>
              <el-tag :type="template.enabled ? 'success' : 'info'" effect="plain">
                {{ template.enabled ? "enabled" : "disabled" }}
              </el-tag>
            </div>
            <p>{{ template.description }}</p>
            <div class="tag-line">
              <el-tag v-for="agent in template.agent_sequence" :key="`${template.key}-${agent}`" size="small" effect="plain">
                {{ agent }}
              </el-tag>
            </div>
            <div class="stage-line">
              <span v-for="stage in template.stage_sequence" :key="`${template.key}-${stage}`">{{ stage }}</span>
            </div>
          </article>
        </div>

        <aside class="template-detail">
          <el-empty v-if="!selectedTemplate" description="请选择 Workflow 模板" />
          <template v-else>
            <el-card shadow="never" class="detail-card">
              <template #header>
                <div class="detail-head">
                  <span>{{ selectedTemplate.name }}</span>
                  <el-tag type="primary" effect="plain">{{ selectedTemplate.key }}</el-tag>
                </div>
              </template>

              <div class="detail-section">
                <span>Agent 流程</span>
                <div class="tag-line">
                  <el-tag
                    v-for="(agent, index) in selectedTemplate.agent_sequence"
                    :key="`${agent}-${index}`"
                    type="success"
                    effect="plain"
                  >
                    {{ index + 1 }}. {{ agent }}
                  </el-tag>
                </div>
              </div>

              <div class="detail-section">
                <span>阶段顺序</span>
                <div class="stage-line">
                  <span v-for="stage in selectedTemplate.stage_sequence" :key="stage">{{ stage }}</span>
                </div>
              </div>

              <div class="detail-section">
                <span>任务输入</span>
                <el-input
                  v-model="requirement"
                  type="textarea"
                  :rows="4"
                  maxlength="500"
                  show-word-limit
                  placeholder="可输入本次任务需求，用于生成模板任务视图"
                />
              </div>

              <el-button type="primary" :icon="Operation" :loading="creating" @click="createTemplateTask">
                创建新工作流任务
              </el-button>

              <el-alert
                v-if="createError"
                :title="createError"
                type="error"
                show-icon
                :closable="false"
                class="result-alert"
              />
              <el-alert
                v-if="createResult"
                :title="`已生成：${createResult.platformRunId}`"
                type="success"
                show-icon
                :closable="false"
                class="result-alert"
              >
                <template #default>
                  <div class="result-body">
                    模板：{{ createResult.template_key }}，
                    工作流节点：{{ createResult.ui_view_model.workflow_steps?.length || 0 }}
                  </div>
                </template>
              </el-alert>
            </el-card>

            <el-collapse class="markdown-collapse">
              <el-collapse-item title="查看模板 Markdown 描述" name="markdown">
                <pre class="markdown-preview">{{ selectedTemplate.markdown || "暂无模板 Markdown 内容" }}</pre>
              </el-collapse-item>
            </el-collapse>
          </template>
        </aside>
      </div>
    </section>

    <section v-if="isJavaMode" class="panel runtime-panel">
      <div class="runtime-head">
        <div>
          <h2>Java MySQL 模板执行</h2>
          <p>可执行 Runtime Lite，也可把 MySQL 模板导出为本地 Codex Skill 包。</p>
        </div>
        <el-tag type="primary" effect="plain">Runtime Lite</el-tag>
      </div>

      <el-alert
        v-if="skillExportResult"
        type="success"
        show-icon
        :closable="false"
        class="skill-export-alert"
      >
        <template #title>
          已导出 Skill：{{ skillExportResult.skillName }}
        </template>
        <div class="skill-export-result">
          <span>路径：<code>{{ skillExportResult.skillPath }}</code></span>
          <el-button size="small" text type="primary" @click="copySkillPath">复制路径</el-button>
          <div class="tag-line">
            <el-tag v-for="file in skillExportResult.files" :key="file" size="small" effect="plain">{{ file }}</el-tag>
          </div>
          <small>已生成但未自动安装到 Codex。</small>
        </div>
      </el-alert>

      <el-empty v-if="!loading && !platformTemplates.length" description="暂无 Java MySQL Workflow 模板" />
      <div v-else class="platform-template-grid" v-loading="loading">
        <article
          v-for="template in platformTemplates"
          :key="template.workflowTemplateKey"
          class="platform-template-card"
          :class="{ active: selectedPlatformTemplate?.workflowTemplateKey === template.workflowTemplateKey }"
          @click="selectedPlatformTemplate = template"
        >
          <div class="template-head">
            <div>
              <div class="template-name">{{ template.name }}</div>
              <div class="template-key">{{ template.workflowTemplateKey }} · v{{ template.version }}</div>
            </div>
            <el-tag type="success" effect="plain">{{ template.nodes.length }} nodes</el-tag>
          </div>
          <p>{{ template.description || "暂无描述" }}</p>
          <div class="stage-line">
            <span v-for="stage in [...new Set(template.nodes.map((node) => node.stage))]" :key="stage">
              {{ stage }}
            </span>
          </div>
          <el-button
            type="primary"
            :icon="Operation"
            :loading="executingRuntime && selectedPlatformTemplate?.workflowTemplateKey === template.workflowTemplateKey"
            @click.stop="executePlatformTemplate(template)"
          >
            执行
          </el-button>
          <el-button
            type="success"
            plain
            :loading="exportingSkillKey === template.workflowTemplateKey"
            @click.stop="exportSkill(template)"
          >
            导出 Skill
          </el-button>
        </article>
      </div>
    </section>
  </section>
</template>

<style scoped>
.mode-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.workflow-filters {
  display: grid;
  grid-template-columns: 1fr 190px;
  gap: 10px;
  margin-bottom: 14px;
}

.workflow-layout {
  display: grid;
  grid-template-columns: minmax(340px, 1fr) minmax(360px, 0.9fr);
  gap: 14px;
}

.template-list {
  display: grid;
  gap: 10px;
}

.template-card {
  display: grid;
  gap: 10px;
  padding: 14px;
  border: 1px solid #e2e8f0;
  border-radius: 15px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.014)),
    #17191f;
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.template-card.active {
  border-color: rgba(77, 163, 255, 0.48);
  box-shadow: 0 0 0 3px rgba(77, 163, 255, 0.12);
}

.template-head,
.detail-head,
.tag-line {
  display: flex;
  align-items: center;
}

.template-head,
.detail-head {
  justify-content: space-between;
  gap: 12px;
}

.template-name {
  color: var(--codex-text);
  font-size: 16px;
  font-weight: 800;
}

.template-key {
  margin-top: 3px;
  color: var(--codex-muted);
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.template-card p {
  margin: 0;
  color: #d4d4d8;
  line-height: 1.55;
}

.tag-line {
  flex-wrap: wrap;
  gap: 6px;
}

.stage-line {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.stage-line span {
  padding: 3px 8px;
  border: 1px solid #dbeafe;
  border-radius: 999px;
  background: rgba(77, 163, 255, 0.12);
  color: #9bd4ff;
  font-size: 12px;
  font-weight: 700;
}

.template-detail {
  display: grid;
  align-content: start;
  gap: 12px;
}

.detail-card {
  border-radius: 8px;
}

.detail-section {
  display: grid;
  gap: 8px;
  margin-bottom: 14px;
}

.detail-section > span {
  color: var(--codex-muted);
  font-size: 12px;
  font-weight: 800;
}

.result-alert {
  margin-top: 12px;
}

.result-body {
  margin-top: 4px;
  font-size: 13px;
}

.markdown-collapse {
  border-radius: 8px;
}

.markdown-preview {
  max-height: 360px;
  margin: 0;
  overflow: auto;
  color: #e4e4e7;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 13px;
  line-height: 1.55;
}

.runtime-panel {
  display: grid;
  gap: 14px;
}

.skill-export-alert {
  border-radius: 12px;
}

.skill-export-result {
  display: grid;
  gap: 8px;
  margin-top: 8px;
}

.skill-export-result code {
  color: #174ea6;
  font-family: "Cascadia Code", Consolas, monospace;
}

.runtime-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.runtime-head h2 {
  margin: 0 0 6px;
  color: #202124;
  font-size: 20px;
}

.runtime-head p {
  margin: 0;
  color: #5f6368;
  line-height: 1.6;
}

.platform-template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}

.platform-template-card {
  display: grid;
  gap: 10px;
  padding: 14px;
  border: 1px solid rgba(77, 163, 255, 0.2);
  border-radius: 15px;
  background:
    radial-gradient(circle at 100% 0%, rgba(77, 163, 255, 0.12), transparent 38%),
    #17191f;
  cursor: pointer;
}

.platform-template-card.active {
  border-color: #1a73e8;
  box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.12);
}

.platform-template-card p {
  margin: 0;
  color: #d4d4d8;
  line-height: 1.55;
}

@media (max-width: 1100px) {
  .workflow-layout,
  .workflow-filters {
    grid-template-columns: 1fr;
  }
}
</style>
