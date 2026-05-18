<script setup lang="ts">
import { Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";

import { getAgents } from "@/api/agents";
import { getApiModeLabel } from "@/api/client";
import { getWorkflowTemplates } from "@/api/workflows";
import CodeAgentPanel from "@/components/WorkflowEditor/CodeAgentPanel.vue";
import NodePropertiesPanel from "@/components/WorkflowEditor/NodePropertiesPanel.vue";
import EditorToolbar from "@/components/WorkflowEditor/Toolbar.vue";
import WorkflowCanvas from "@/components/WorkflowEditor/WorkflowCanvas.vue";
import { useWorkflowEditorStore } from "@/components/WorkflowEditor/WorkflowEditorStore";
import type { AgentMeta } from "@/types/agent";
import type { InstantiateWorkflowResponse, WorkflowTemplate } from "@/types/workflow";

const store = useWorkflowEditorStore();
const apiModeLabel = getApiModeLabel();
const agents = ref<AgentMeta[]>([]);
const templates = ref<WorkflowTemplate[]>([]);
const keyword = ref("");
const stageFilter = ref("all");
const lastInstantiateResult = ref<InstantiateWorkflowResponse | null>(null);

const loading = reactive({
  agents: false,
  templates: false,
});

const stageOptions = computed(() => {
  const stages = new Set(agents.value.map((agent) => agent.stage).filter(Boolean));
  return [...stages].sort();
});

const filteredAgents = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase();

  return agents.value.filter((agent) => {
    if (stageFilter.value !== "all" && agent.stage !== stageFilter.value) {
      return false;
    }

    if (!normalizedKeyword) {
      return true;
    }

    return `${agent.name} ${agent.key} ${agent.role} ${agent.description}`.toLowerCase().includes(normalizedKeyword);
  });
});

const enabledNodeCount = computed(() => store.nodes.filter((node) => node.enabled).length);

function startPaletteDrag(agent: AgentMeta, event: DragEvent) {
  event.dataTransfer?.setData("application/x-agent-key", agent.key);
  event.dataTransfer?.setData("text/plain", agent.key);

  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = "copy";
  }
}

async function loadAgents() {
  loading.agents = true;

  try {
    agents.value = await getAgents();
  } catch (error) {
    agents.value = [];
    ElMessage.error(error instanceof Error ? error.message : "加载 Agent Palette 失败");
  } finally {
    loading.agents = false;
  }
}

async function loadTemplates() {
  loading.templates = true;

  try {
    templates.value = await getWorkflowTemplates();
  } catch (error) {
    templates.value = [];
    ElMessage.error(error instanceof Error ? error.message : "加载 Workflow 模板失败");
  } finally {
    loading.templates = false;
  }
}

async function refreshAll() {
  await Promise.allSettled([loadAgents(), loadTemplates()]);
}

function handleInstantiated(result: InstantiateWorkflowResponse) {
  lastInstantiateResult.value = result;
}

onMounted(refreshAll);
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <h1>Workflow Editor</h1>
        <p>拖拽式工作流编辑器，用于选择 Agent、调整顺序、配置变量并生成模板任务视图</p>
      </div>
      <el-button :icon="Refresh" :loading="loading.agents || loading.templates" @click="refreshAll">刷新</el-button>
    </div>

    <div class="mode-tags">
      <el-tag type="primary" effect="plain">API 模式：{{ apiModeLabel }}</el-tag>
      <el-tag type="success" effect="plain">Agent Palette：{{ agents.length }}</el-tag>
      <el-tag type="success" effect="plain">Workflow 模板：{{ templates.length }}</el-tag>
      <el-tag type="warning" effect="plain">当前编辑器不改变默认 LangGraph 流程</el-tag>
    </div>

    <EditorToolbar
      :templates="templates"
      :loading-templates="loading.templates"
      @reload-templates="loadTemplates"
      @instantiated="handleInstantiated"
    />

    <el-alert
      v-if="lastInstantiateResult"
      :title="`已生成模板任务视图：${lastInstantiateResult.platformRunId}`"
      type="success"
      show-icon
      :closable="false"
    />

    <section class="editor-grid">
      <aside class="palette-panel panel" v-loading="loading.agents">
        <div class="panel-title">Agent Palette</div>
        <div class="palette-filters">
          <el-input v-model="keyword" :prefix-icon="Search" clearable placeholder="搜索 Agent" />
          <el-select v-model="stageFilter">
            <el-option label="全部阶段" value="all" />
            <el-option v-for="stage in stageOptions" :key="stage" :label="stage" :value="stage" />
          </el-select>
        </div>

        <el-empty v-if="!loading.agents && !filteredAgents.length" description="暂无可用 Agent" />
        <div v-else class="palette-list">
          <article
            v-for="agent in filteredAgents"
            :key="agent.key"
            class="palette-agent"
            draggable="true"
            @dragstart="startPaletteDrag(agent, $event)"
          >
            <div>
              <strong>{{ agent.name }}</strong>
              <span>{{ agent.key }} · {{ agent.stage }}</span>
            </div>
            <el-tag :type="agent.enabled ? 'success' : 'info'" effect="plain" size="small">
              {{ agent.enabled ? "enabled" : "disabled" }}
            </el-tag>
            <p>{{ agent.description || "暂无描述" }}</p>
          </article>
        </div>
      </aside>

      <main class="canvas-panel">
        <WorkflowCanvas :agents="agents" />
      </main>

      <aside class="right-panel">
        <NodePropertiesPanel />
        <CodeAgentPanel />
        <el-card shadow="never" class="preview-card">
          <template #header>实时预览</template>
          <div class="preview-metrics">
            <el-tag type="primary" effect="plain">节点 {{ store.nodes.length }}</el-tag>
            <el-tag type="success" effect="plain">启用 {{ enabledNodeCount }}</el-tag>
            <el-tag effect="plain">连线 {{ store.connections.length }}</el-tag>
          </div>
          <div class="preview-list">
            <article v-for="(node, index) in store.orderedNodes" :key="node.nodeId" class="preview-item">
              <span>{{ index + 1 }}</span>
              <div>
                <strong>{{ node.name }}</strong>
                <small>{{ node.stage }} · {{ node.enabled ? "启用" : "禁用" }}</small>
              </div>
            </article>
          </div>
          <el-empty v-if="!store.nodes.length" description="暂无节点顺序" />
        </el-card>
      </aside>
    </section>
  </section>
</template>

<style scoped>
.mode-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.editor-grid {
  display: grid;
  grid-template-columns: 280px minmax(580px, 1fr) 330px;
  gap: 14px;
  align-items: start;
}

.palette-panel {
  min-height: 650px;
}

.palette-filters {
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}

.palette-list {
  display: grid;
  gap: 9px;
}

.palette-agent {
  display: grid;
  gap: 8px;
  padding: 11px;
  border: 1px solid #dbe4ef;
  border-radius: 8px;
  background: #ffffff;
  cursor: grab;
}

.palette-agent:active {
  cursor: grabbing;
}

.palette-agent div {
  display: grid;
  gap: 2px;
}

.palette-agent strong {
  color: #0f172a;
  font-weight: 800;
}

.palette-agent span {
  color: #64748b;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.palette-agent p {
  margin: 0;
  color: #475569;
  font-size: 12px;
  line-height: 1.45;
}

.canvas-panel {
  min-width: 0;
}

.right-panel {
  display: grid;
  gap: 14px;
}

.preview-card {
  border-radius: 8px;
}

.preview-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.preview-list {
  display: grid;
  gap: 8px;
}

.preview-item {
  display: flex;
  gap: 9px;
  align-items: center;
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
}

.preview-item > span {
  display: grid;
  width: 24px;
  height: 24px;
  place-items: center;
  border-radius: 50%;
  background: #dbeafe;
  color: #1e40af;
  font-weight: 800;
}

.preview-item div {
  display: grid;
  gap: 2px;
}

.preview-item strong {
  color: #0f172a;
}

.preview-item small {
  color: #64748b;
}

@media (max-width: 1380px) {
  .editor-grid {
    grid-template-columns: 250px minmax(520px, 1fr) 310px;
  }
}
</style>
