<script setup lang="ts">
import { Close, Expand, Fold, Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";

import { getAgents } from "@/api/agents";
import { currentApiMode, getApiModeLabel } from "@/api/client";
import { getPlatformWorkflowTemplates, getWorkflowTemplates } from "@/api/workflows";
import CodeAgentPanel from "@/components/WorkflowEditor/CodeAgentPanel.vue";
import NodePropertiesPanel from "@/components/WorkflowEditor/NodePropertiesPanel.vue";
import EditorToolbar from "@/components/WorkflowEditor/Toolbar.vue";
import WorkflowCanvas from "@/components/WorkflowEditor/WorkflowCanvas.vue";
import { useWorkflowEditorStore } from "@/components/WorkflowEditor/WorkflowEditorStore";
import type { AgentMeta } from "@/types/agent";
import type { InstantiateWorkflowResponse, WorkflowTemplate } from "@/types/workflow";
import type { WorkflowTemplateData } from "@/types/workflowEditor";

const store = useWorkflowEditorStore();
const apiModeLabel = getApiModeLabel();
const isJavaMode = currentApiMode === "java";
const agents = ref<AgentMeta[]>([]);
const templates = ref<WorkflowTemplate[]>([]);
const platformTemplates = ref<WorkflowTemplateData[]>([]);
const keyword = ref("");
const stageFilter = ref("all");
const lastInstantiateResult = ref<InstantiateWorkflowResponse | null>(null);
const paletteCollapsed = ref(localStorage.getItem("ai-agent-pipeline.workflow-editor.palette-collapsed") === "true");

const loading = reactive({
  agents: false,
  templates: false,
});

const branchAgents: AgentMeta[] = [
  {
    key: "branch_if",
    name: "If",
    role: "条件分支节点",
    description: "根据条件表达式选择 true / false 分支，适合演示条件执行路径。",
    input_fields: ["condition", "input"],
    output_fields: ["true_path", "false_path"],
    stage: "branch",
    enabled: true,
    version: "1.0",
  },
  {
    key: "branch_and",
    name: "And",
    role: "并行汇合节点",
    description: "要求多个上游条件同时满足后继续执行，适合质量门禁或审批组合。",
    input_fields: ["left", "right"],
    output_fields: ["and_result"],
    stage: "branch",
    enabled: true,
    version: "1.0",
  },
  {
    key: "branch_or",
    name: "Or",
    role: "任一条件节点",
    description: "任一上游条件满足即可继续执行，适合兜底路径和多方案选择。",
    input_fields: ["left", "right"],
    output_fields: ["or_result"],
    stage: "branch",
    enabled: true,
    version: "1.0",
  },
];

const paletteAgents = computed(() => [...agents.value, ...branchAgents]);
const selectedNode = computed(() => store.selectedNode);
const selectedIsCodeAgent = computed(() => selectedNode.value?.agentKey === "code_agent");

const stageOptions = computed(() => {
  const stages = new Set(paletteAgents.value.map((agent) => agent.stage).filter(Boolean));
  return [...stages].sort();
});

const filteredAgents = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase();

  return paletteAgents.value.filter((agent) => {
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

  const [apiTemplatesResult, platformTemplatesResult] = await Promise.allSettled([
    getWorkflowTemplates(),
    getPlatformWorkflowTemplates(),
  ]);

  if (apiTemplatesResult.status === "fulfilled") {
    templates.value = apiTemplatesResult.value;
  } else {
    templates.value = [];
    ElMessage.error(apiTemplatesResult.reason instanceof Error ? apiTemplatesResult.reason.message : "加载 API Workflow 模板失败");
  }

  if (platformTemplatesResult.status === "fulfilled") {
    platformTemplates.value = platformTemplatesResult.value;
  } else {
    platformTemplates.value = [];
    if (isJavaMode) {
      ElMessage.error(
        platformTemplatesResult.reason instanceof Error
          ? platformTemplatesResult.reason.message
          : "加载 MySQL Workflow 模板失败",
      );
    }
  }

  loading.templates = false;
}

async function refreshAll() {
  await Promise.allSettled([loadAgents(), loadTemplates()]);
}

function handleInstantiated(result: InstantiateWorkflowResponse) {
  lastInstantiateResult.value = result;
}

function togglePalette() {
  paletteCollapsed.value = !paletteCollapsed.value;
  localStorage.setItem("ai-agent-pipeline.workflow-editor.palette-collapsed", String(paletteCollapsed.value));
}

function closeInspector() {
  store.selectNode("");
}

onMounted(refreshAll);
</script>

<template>
  <section class="page-stack workflow-editor-page">
    <div class="page-header">
      <div>
        <h1>Workflow Editor</h1>
        <p>Figma 风无限画布：拖拽 Agent、配置节点、保存模板并生成任务视图</p>
      </div>
      <el-button :icon="Refresh" :loading="loading.agents || loading.templates" @click="refreshAll">刷新</el-button>
    </div>

    <div class="mode-tags">
      <el-tag type="primary" effect="plain">API 模式：{{ apiModeLabel }}</el-tag>
      <el-tag type="success" effect="plain">Agent Palette：{{ agents.length }}</el-tag>
      <el-tag type="success" effect="plain">Workflow 模板：{{ templates.length }}</el-tag>
      <el-tag v-if="isJavaMode" type="success" effect="plain">MySQL 模板：{{ platformTemplates.length }}</el-tag>
      <el-tag type="warning" effect="plain">当前编辑器不改变默认 LangGraph 流程</el-tag>
    </div>

    <EditorToolbar
      :templates="templates"
      :platform-templates="platformTemplates"
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

    <section class="editor-workspace">
      <WorkflowCanvas :agents="paletteAgents" />

      <aside class="floating-palette" :class="{ collapsed: paletteCollapsed }" v-loading="loading.agents">
        <button class="palette-toggle" type="button" @click="togglePalette">
          <el-icon><component :is="paletteCollapsed ? Expand : Fold" /></el-icon>
          <span>{{ paletteCollapsed ? "展开" : "收起" }}</span>
        </button>

        <div v-show="paletteCollapsed" class="palette-rail">
          <strong>Agents</strong>
          <span>{{ filteredAgents.length }}</span>
        </div>

        <div v-show="!paletteCollapsed" class="palette-content">
          <div class="palette-head">
            <div>
              <strong>Agent Palette</strong>
              <span>拖入画布生成工作流节点</span>
            </div>
            <el-tag type="primary" effect="plain">{{ filteredAgents.length }} nodes</el-tag>
          </div>

          <div class="palette-filters">
            <el-input v-model="keyword" :prefix-icon="Search" clearable placeholder="搜索 Agent / CodeAgent / Branch" />
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
              :class="{ branch: agent.stage === 'branch', code: agent.key === 'code_agent' }"
              draggable="true"
              @dragstart="startPaletteDrag(agent, $event)"
            >
              <div class="palette-agent-main">
                <strong>{{ agent.name }}</strong>
                <span>{{ agent.key }} · {{ agent.stage }}</span>
              </div>
              <el-tag
                :type="agent.stage === 'branch' ? 'warning' : agent.enabled ? 'success' : 'info'"
                effect="plain"
                size="small"
              >
                {{ agent.enabled ? "enabled" : "disabled" }}
              </el-tag>
              <p>{{ agent.description || "暂无描述" }}</p>
            </article>
          </div>
        </div>
      </aside>

      <transition name="inspector-slide">
        <aside v-if="selectedNode" class="inspector-panel" @click.stop>
          <div class="inspector-head">
            <div>
              <span>Node Inspector</span>
              <strong>{{ selectedNode.name }}</strong>
            </div>
            <div class="inspector-actions">
              <el-tag type="primary" effect="plain">{{ selectedNode.agentKey }}</el-tag>
              <el-button :icon="Close" text circle @click="closeInspector" />
            </div>
          </div>

          <div class="inspector-scroll">
            <NodePropertiesPanel embedded />
            <CodeAgentPanel v-if="selectedIsCodeAgent" always-visible />

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
          </div>
        </aside>
      </transition>
    </section>
  </section>
</template>

<style scoped>
.workflow-editor-page {
  gap: 12px;
}

.mode-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.editor-workspace {
  position: relative;
  height: clamp(680px, calc(100vh - 210px), 900px);
  border-radius: 12px;
}

.floating-palette {
  position: absolute;
  top: 14px;
  bottom: 14px;
  left: 14px;
  z-index: 12;
  display: grid;
  grid-template-rows: auto 1fr;
  width: 322px;
  padding: 12px;
  overflow: hidden;
  border: 1px solid rgba(203, 213, 225, 0.9);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 18px 46px rgba(15, 23, 42, 0.14);
  backdrop-filter: blur(14px);
  transition:
    width 220ms cubic-bezier(0.2, 0, 0, 1),
    padding 220ms cubic-bezier(0.2, 0, 0, 1),
    box-shadow 180ms ease;
}

.floating-palette.collapsed {
  width: 64px;
  padding: 10px 8px;
}

.palette-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  height: 34px;
  border: 1px solid #dbeafe;
  border-radius: 999px;
  background: #eff6ff;
  color: #1d4ed8;
  cursor: pointer;
  font-size: 12px;
  font-weight: 800;
  transition:
    transform 160ms ease,
    background 160ms ease;
}

.palette-toggle:hover {
  background: #dbeafe;
  transform: translateY(-1px);
}

.floating-palette.collapsed .palette-toggle span {
  display: none;
}

.palette-rail {
  display: grid;
  place-items: center;
  align-content: center;
  gap: 12px;
  min-height: 0;
  color: #1e40af;
}

.palette-rail strong {
  writing-mode: vertical-rl;
  letter-spacing: 0;
  font-size: 13px;
}

.palette-rail span {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 50%;
  background: #dbeafe;
  color: #1d4ed8;
  font-weight: 900;
}

.palette-content {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
  gap: 10px;
  min-height: 0;
  padding-top: 10px;
}

.palette-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.palette-head div {
  display: grid;
  gap: 2px;
}

.palette-head strong {
  color: #0f172a;
  font-size: 15px;
}

.palette-head span {
  color: #64748b;
  font-size: 12px;
}

.palette-filters {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.palette-list {
  display: grid;
  gap: 8px;
  min-height: 0;
  overflow: auto;
  padding: 2px 2px 4px;
}

.palette-agent {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  padding: 10px;
  border: 1px solid #dbe4ef;
  border-radius: 10px;
  background: #ffffff;
  cursor: grab;
  transition:
    transform 160ms ease,
    box-shadow 160ms ease,
    border-color 160ms ease;
}

.palette-agent:hover {
  border-color: #93c5fd;
  box-shadow: 0 10px 22px rgba(30, 64, 175, 0.1);
  transform: translateY(-2px);
}

.palette-agent:active {
  cursor: grabbing;
}

.palette-agent.branch {
  border-color: #fed7aa;
  background: #fff7ed;
}

.palette-agent.code {
  border-color: #fecaca;
  background: #fffafa;
}

.palette-agent-main {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.palette-agent strong {
  overflow: hidden;
  color: #0f172a;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.palette-agent span {
  overflow: hidden;
  color: #64748b;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.palette-agent p {
  grid-column: 1 / -1;
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: #475569;
  font-size: 12px;
  line-height: 1.45;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.inspector-panel {
  position: absolute;
  top: 14px;
  right: 14px;
  bottom: 14px;
  z-index: 14;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  width: min(398px, calc(100% - 104px));
  overflow: hidden;
  border: 1px solid rgba(203, 213, 225, 0.94);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 22px 58px rgba(15, 23, 42, 0.18);
  backdrop-filter: blur(16px);
}

.inspector-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid #e2e8f0;
}

.inspector-head div:first-child {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.inspector-head span {
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.inspector-head strong {
  overflow: hidden;
  color: #0f172a;
  font-size: 17px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inspector-actions {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 6px;
}

.inspector-scroll {
  display: grid;
  align-content: start;
  gap: 12px;
  min-height: 0;
  overflow: auto;
  padding: 12px;
}

.preview-card {
  border-radius: 10px;
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
  min-width: 0;
}

.preview-item strong {
  overflow: hidden;
  color: #0f172a;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-item small {
  color: #64748b;
}

.inspector-slide-enter-active,
.inspector-slide-leave-active {
  transition:
    opacity 180ms ease,
    transform 220ms cubic-bezier(0.2, 0, 0, 1);
}

.inspector-slide-enter-from,
.inspector-slide-leave-to {
  opacity: 0;
  transform: translateX(18px) scale(0.98);
}

@media (max-width: 1180px) {
  .floating-palette:not(.collapsed) {
    width: 286px;
  }

  .inspector-panel {
    width: min(360px, calc(100% - 96px));
  }
}
</style>
