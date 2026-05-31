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
const codeAgentHintOpen = ref(false);
const paletteAvoidanceWidth = computed(() => (paletteCollapsed.value ? 80 : 310));

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
  {
    key: "human_approval",
    name: "Human Approval",
    role: "人工确认节点",
    description: "在平台层暂停工作流，等待用户批准、拒绝或补充说明。",
    input_fields: ["approval_context"],
    output_fields: ["approval_result", "human_comment"],
    stage: "approval",
    enabled: true,
    version: "1.0",
  },
  {
    key: "custom_agent",
    name: "Custom Agent",
    role: "自定义模板智能体",
    description: "仅保存到 Workflow 模板中的可视化 Agent 节点，后续可升级为动态 Agent。",
    input_fields: ["input"],
    output_fields: ["custom_result"],
    stage: "custom",
    enabled: true,
    version: "1.0",
  },
];

const paletteAgents = computed(() => [...agents.value, ...branchAgents]);
const selectedNode = computed(() => store.selectedNode);
const selectedIsCodeAgent = computed(() => selectedNode.value?.agentKey === "code_agent");
const editorSteps = ["选择模板", "拖拽或调整节点", "检查流程", "保存模板", "生成任务"];
const activeStep = computed(() => {
  if (!store.nodes.length) {
    return 0;
  }

  if (store.validateWorkflow().some((issue) => issue.severity === "error")) {
    return 2;
  }

  if (lastInstantiateResult.value) {
    return 4;
  }

  return 3;
});
const stageOptions = [
  { label: "全部", value: "all" },
  { label: "Analysis", value: "analysis" },
  { label: "Implementation", value: "implementation" },
  { label: "Testing", value: "testing" },
  { label: "Execution", value: "execution" },
  { label: "Repair", value: "repair" },
  { label: "Code Ops", value: "code_ops" },
  { label: "Approval", value: "approval" },
  { label: "Custom", value: "custom" },
  { label: "Report", value: "report" },
];

const filteredAgents = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase();

  return paletteAgents.value.filter((agent) => {
    if (stageFilter.value !== "all" && normalizeStage(agent) !== stageFilter.value) {
      return false;
    }

    if (!normalizedKeyword) {
      return true;
    }

    return `${agent.name} ${agent.key} ${agent.role} ${agent.description}`.toLowerCase().includes(normalizedKeyword);
  });
});

const workflowStats = computed(() => ({
  agents: agents.value.length,
  templates: templates.value.length + platformTemplates.value.length + store.savedTemplates.length,
}));

function normalizeStage(agent: Pick<AgentMeta, "key" | "stage">) {
  const key = agent.key.toLowerCase();
  const stage = (agent.stage || "").toLowerCase();

  if (key === "code_agent") {
    return "code_ops";
  }

  if (key.includes("product")) {
    return "analysis";
  }

  if (key.includes("coder")) {
    return "implementation";
  }

  if (key.includes("tester")) {
    return "testing";
  }

  if (key.includes("runner")) {
    return "execution";
  }

  if (key.includes("sentry")) {
    return "repair";
  }

  if (key.includes("report")) {
    return "report";
  }

  if (key === "human_approval") {
    return "approval";
  }

  if (key === "custom_agent") {
    return "custom";
  }

  return stage === "branch" ? "repair" : stage || "implementation";
}

function stageLabel(agent: Pick<AgentMeta, "key" | "stage">) {
  return stageOptions.find((option) => option.value === normalizeStage(agent))?.label || agent.stage || "Custom";
}

function startPaletteDrag(agent: AgentMeta, event: DragEvent) {
  store.clearSelection();
  store.clearConnectionSelection();
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

onMounted(() => {
  if (window.innerWidth < 1180 && !paletteCollapsed.value) {
    paletteCollapsed.value = true;
    localStorage.setItem("ai-agent-pipeline.workflow-editor.palette-collapsed", "true");
  }

  void refreshAll();
});
</script>

<template>
  <section class="page-stack workflow-editor-page">
    <div class="page-header">
      <div>
        <h1>Workflow Editor</h1>
        <p>可视化编排 Agent 节点，生成单人演示工作流</p>
      </div>
      <div class="header-meta">
        <el-tag type="primary" effect="plain">{{ apiModeLabel }}</el-tag>
        <el-tag type="success" effect="plain">Workflow {{ workflowStats.templates }}</el-tag>
        <el-tag type="success" effect="plain">Agents {{ workflowStats.agents }}</el-tag>
        <el-button :icon="Refresh" :loading="loading.agents || loading.templates" plain @click="refreshAll">
          刷新
        </el-button>
      </div>
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

    <section class="editor-guide">
      <div
        v-for="(step, index) in editorSteps"
        :key="step"
        class="guide-step"
        :class="{ active: index === activeStep, done: index < activeStep }"
      >
        <span>{{ index + 1 }}</span>
        <strong>{{ step }}</strong>
      </div>
    </section>

    <section class="code-agent-hint" :class="{ open: codeAgentHintOpen }">
      <button type="button" class="hint-toggle" @click="codeAgentHintOpen = !codeAgentHintOpen">
        <div>
          <strong>CodeAgent 文件操作节点</strong>
          <span>读取项目文件、跨文件写入、JSONL 审计和安全阻断</span>
        </div>
        <el-tag type="primary" effect="plain">{{ codeAgentHintOpen ? "收起" : "展开" }}</el-tag>
      </button>
      <div v-if="codeAgentHintOpen" class="hint-body">
        <el-tag effect="plain">read_file</el-tag>
        <el-tag effect="plain">write_file</el-tag>
        <el-tag effect="plain">list_files</el-tag>
        <span>受 allowed_paths 白名单限制，自动阻断 .env 等敏感路径，事件可在 RunConsole / Replay 中查看。</span>
      </div>
    </section>

    <section class="editor-workspace">
      <WorkflowCanvas :agents="paletteAgents" :palette-avoidance-width="paletteAvoidanceWidth" />

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
            <el-input v-model="keyword" :prefix-icon="Search" clearable placeholder="搜索节点" />
            <el-select v-model="stageFilter">
              <el-option label="全部阶段" value="all" />
            <el-option v-for="stage in stageOptions" :key="stage.value" :label="stage.label" :value="stage.value" />
          </el-select>
          </div>

          <el-empty v-if="!loading.agents && !filteredAgents.length" description="暂无可用 Agent" />
          <div v-else class="palette-list">
            <article
              v-for="agent in filteredAgents"
              :key="agent.key"
              class="palette-agent"
              :class="{
                branch: agent.stage === 'branch',
                code: agent.key === 'code_agent',
                approval: agent.key === 'human_approval',
                custom: agent.key === 'custom_agent',
              }"
              draggable="true"
              @dragstart="startPaletteDrag(agent, $event)"
            >
              <div class="palette-agent-main">
                <strong>{{ agent.name }}</strong>
                <span>{{ stageLabel(agent) }} · {{ agent.key }}</span>
              </div>
              <el-tag
                :type="agent.stage === 'branch' ? 'warning' : agent.enabled ? 'success' : 'info'"
                effect="plain"
                size="small"
              >
                {{ agent.enabled ? "enabled" : "disabled" }}
              </el-tag>
              <p>
                {{
                  agent.key === "code_agent"
                    ? "文件读取 / 跨文件修改 / 审计日志"
                    : agent.key === "human_approval"
                      ? "人工确认 / 审批暂停 / 继续或拒绝"
                      : agent.key === "custom_agent"
                        ? "前端可编辑 / 保存到模板 / 暂不动态执行"
                    : agent.description || "暂无描述"
                }}
              </p>
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
            <el-collapse v-if="selectedIsCodeAgent" class="code-agent-executor">
              <el-collapse-item title="执行 CodeAgent 节点" name="code-agent-exec">
                <CodeAgentPanel always-visible />
              </el-collapse-item>
            </el-collapse>
          </div>
        </aside>
      </transition>
    </section>
  </section>
</template>

<style scoped>
.workflow-editor-page {
  gap: 12px;
  color: #202124;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.page-header h1 {
  margin: 0;
  color: #f4f4f5;
}

.page-header p {
  margin: 4px 0 0;
  color: #a1a1aa;
}

.header-meta {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.editor-guide {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}

.guide-step {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  min-width: 0;
  padding: 8px 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: #17191f;
  color: #a1a1aa;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.16);
}

.guide-step span {
  display: grid;
  width: 22px;
  height: 22px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 50%;
  background: rgba(148, 163, 184, 0.16);
  color: #cbd5e1;
  font-weight: 800;
}

.guide-step strong {
  overflow: hidden;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.guide-step.done span {
  background: rgba(74, 222, 128, 0.18);
  color: #9af4ba;
}

.guide-step.active {
  border-color: rgba(77, 163, 255, 0.28);
  background:
    radial-gradient(circle at 100% 0%, rgba(77, 163, 255, 0.16), transparent 44%),
    #17191f;
  color: #9bd4ff;
}

.guide-step.active span {
  background: #4da3ff;
  color: #06121f;
}

.code-agent-hint {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  background: #17191f;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.16);
}

.hint-toggle {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 14px;
  border: 0;
  background: transparent;
  cursor: pointer;
  text-align: left;
}

.hint-toggle div {
  display: grid;
  gap: 2px;
}

.hint-toggle strong {
  color: #f4f4f5;
}

.hint-toggle span,
.hint-body span {
  color: #5f6368;
  font-size: 12px;
}

.hint-body {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  padding: 0 14px 12px;
}

.editor-workspace {
  position: relative;
  height: clamp(660px, calc(100vh - 222px), 940px);
  border-radius: 16px;
}

.floating-palette {
  position: absolute;
  top: 14px;
  bottom: 14px;
  left: 14px;
  z-index: 10;
  display: grid;
  grid-template-rows: auto 1fr;
  width: 260px;
  padding: 10px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  background: rgba(23, 25, 31, 0.94);
  box-shadow: 0 18px 46px rgba(0, 0, 0, 0.24);
  backdrop-filter: blur(14px);
  transition:
    width 220ms cubic-bezier(0.2, 0, 0, 1),
    padding 220ms cubic-bezier(0.2, 0, 0, 1),
    box-shadow 180ms ease;
}

.floating-palette.collapsed {
  width: 58px;
  padding: 10px 8px;
}

.palette-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  height: 34px;
  border: 1px solid rgba(77, 163, 255, 0.2);
  border-radius: 999px;
  background: rgba(77, 163, 255, 0.12);
  color: #9bd4ff;
  cursor: pointer;
  font-size: 12px;
  font-weight: 800;
  transition:
    transform 160ms ease,
    background 160ms ease;
}

.palette-toggle:hover {
  background: rgba(77, 163, 255, 0.2);
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
  color: #9bd4ff;
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
  background: rgba(77, 163, 255, 0.14);
  color: #9bd4ff;
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
  color: #f4f4f5;
  font-size: 15px;
}

.palette-head span {
  color: #a1a1aa;
  font-size: 12px;
}

.palette-filters {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.palette-list {
  display: grid;
  gap: 10px;
  min-height: 0;
  overflow: auto;
  padding: 2px 2px 4px;
}

.palette-agent {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  padding: 10px 11px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: #17191f;
  cursor: grab;
  transition:
    transform 160ms ease,
    box-shadow 160ms ease,
    border-color 160ms ease;
}

.palette-agent:hover {
  border-color: #8ab4f8;
  box-shadow: 0 10px 22px rgba(26, 115, 232, 0.1);
  transform: translateY(-2px);
}

.palette-agent:active {
  cursor: grabbing;
}

.palette-agent.branch {
  border-color: #fbbc04;
  background:
    linear-gradient(135deg, rgba(250, 204, 21, 0.12), transparent 46%),
    #17191f;
}

.palette-agent.approval {
  border-color: #a78bfa;
  background:
    linear-gradient(90deg, rgba(167, 139, 250, 0.34) 0, rgba(167, 139, 250, 0.34) 5px, transparent 5px),
    #17191f;
}

.palette-agent.custom {
  border-color: #94a3b8;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0.28) 0, rgba(148, 163, 184, 0.28) 5px, transparent 5px),
    #17191f;
}

.palette-agent.code {
  border-color: #8ab4f8;
  background:
    linear-gradient(90deg, rgba(77, 163, 255, 0.34) 0, rgba(77, 163, 255, 0.34) 5px, transparent 5px),
    #17191f;
}

.palette-agent-main {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.palette-agent strong {
  overflow: hidden;
  color: #f4f4f5;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.palette-agent span {
  overflow: hidden;
  color: #a1a1aa;
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
  color: #a1a1aa;
  font-size: 12px;
  line-height: 1.45;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}

.inspector-panel {
  position: absolute;
  top: 14px;
  right: 14px;
  bottom: 14px;
  z-index: 14;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  width: min(320px, calc(100% - 104px));
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  background: rgba(23, 25, 31, 0.96);
  box-shadow: 0 22px 58px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(16px);
}

.inspector-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.inspector-head div:first-child {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.inspector-head span {
  color: #a1a1aa;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.inspector-head strong {
  overflow: hidden;
  color: #f4f4f5;
  font-size: 16px;
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

.code-agent-executor {
  border-radius: 14px;
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
    width: 260px;
  }

  .inspector-panel {
    width: min(360px, calc(100% - 96px));
  }

  .editor-guide {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.workflow-editor-page {
  color: var(--codex-text);
}

.workflow-editor-page :deep(.page-header h1),
.page-header h1 {
  color: var(--codex-text);
}

.workflow-editor-page :deep(.page-header p),
.page-header p,
.palette-head span,
.palette-agent span,
.palette-agent p,
.hint-toggle span,
.hint-body span,
.inspector-head span {
  color: var(--codex-muted);
}

.guide-step,
.code-agent-hint,
.floating-palette,
.inspector-panel,
.palette-agent {
  border-color: var(--codex-border);
  background: rgba(23, 25, 31, 0.94);
  color: var(--codex-text);
  box-shadow: 0 22px 58px rgba(0, 0, 0, 0.32);
}

.guide-step span,
.palette-rail span {
  background: var(--codex-elevated);
  color: var(--codex-muted);
}

.guide-step.active,
.palette-toggle {
  border-color: rgba(77, 163, 255, 0.48);
  background: rgba(77, 163, 255, 0.14);
  color: var(--codex-accent);
}

.guide-step.active span {
  background: var(--codex-accent);
  color: #06121f;
}

.hint-toggle strong,
.palette-head strong,
.palette-agent strong,
.inspector-head strong {
  color: var(--codex-text);
}

.palette-agent:hover {
  border-color: var(--codex-accent);
  box-shadow: 0 14px 30px rgba(77, 163, 255, 0.14);
}

.palette-agent.branch {
  border-color: rgba(250, 204, 21, 0.42);
  background: linear-gradient(90deg, rgba(250, 204, 21, 0.22) 0, rgba(250, 204, 21, 0.22) 5px, transparent 5px),
    rgba(23, 25, 31, 0.94);
}

.palette-agent.approval {
  border-color: rgba(167, 139, 250, 0.44);
  background: linear-gradient(90deg, rgba(167, 139, 250, 0.24) 0, rgba(167, 139, 250, 0.24) 5px, transparent 5px),
    rgba(23, 25, 31, 0.94);
}

.palette-agent.custom {
  border-color: rgba(148, 163, 184, 0.5);
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.22) 0, rgba(148, 163, 184, 0.22) 5px, transparent 5px),
    rgba(23, 25, 31, 0.94);
}

.palette-agent.code {
  border-color: rgba(77, 163, 255, 0.52);
  background: linear-gradient(90deg, rgba(77, 163, 255, 0.24) 0, rgba(77, 163, 255, 0.24) 5px, transparent 5px),
    rgba(23, 25, 31, 0.94);
}

.inspector-head {
  border-bottom-color: var(--codex-border);
}
</style>
