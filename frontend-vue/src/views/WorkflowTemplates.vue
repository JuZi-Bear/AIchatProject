<script setup lang="ts">
import { Operation, Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";

import { getApiModeLabel } from "@/api/client";
import { getWorkflowTemplates, instantiateWorkflow } from "@/api/workflows";
import type { InstantiateWorkflowResponse, WorkflowTemplate } from "@/types/workflow";

const apiModeLabel = getApiModeLabel();
const templates = ref<WorkflowTemplate[]>([]);
const selectedTemplate = ref<WorkflowTemplate | null>(null);
const keyword = ref("");
const stageFilter = ref("all");
const requirement = ref("");
const loading = ref(false);
const creating = ref(false);
const createResult = ref<InstantiateWorkflowResponse | null>(null);
const createError = ref("");

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
    templates.value = await getWorkflowTemplates();
    selectedTemplate.value = selectedTemplate.value || templates.value[0] || null;
  } catch (error) {
    templates.value = [];
    selectedTemplate.value = null;
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
  border-radius: 8px;
  background: #ffffff;
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.template-card.active {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.12);
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
  color: #0f172a;
  font-size: 16px;
  font-weight: 800;
}

.template-key {
  margin-top: 3px;
  color: #64748b;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.template-card p {
  margin: 0;
  color: #334155;
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
  background: #eff6ff;
  color: #1d4ed8;
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
  color: #64748b;
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
  color: #334155;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 13px;
  line-height: 1.55;
}

@media (max-width: 1100px) {
  .workflow-layout,
  .workflow-filters {
    grid-template-columns: 1fr;
  }
}
</style>
