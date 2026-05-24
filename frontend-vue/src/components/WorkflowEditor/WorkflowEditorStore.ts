import { defineStore } from "pinia";

import type { AgentMeta } from "@/types/agent";
import type {
  AgentNodeData,
  ConnectionData,
  WorkflowEditorState,
  WorkflowTemplateData,
  WorkflowViewport,
} from "@/types/workflowEditor";
import type { WorkflowTemplate } from "@/types/workflow";

const STORAGE_KEY = "ai-agent-pipeline.workflow-editor.templates";
const DEFAULT_VIEWPORT: WorkflowViewport = {
  x: 40,
  y: 40,
  scale: 1,
};
const MIN_SCALE = 0.4;
const MAX_SCALE = 1.8;
const LAYOUT_START_X = 56;
const LAYOUT_START_Y = 56;
const LAYOUT_COLUMN_GAP = 276;
const LAYOUT_ROW_GAP = 168;
const LAYOUT_COLUMNS = 4;

const agentLabels: Record<string, string> = {
  product: "Product Agent",
  coder: "Coder Agent",
  tester: "Tester Agent",
  runner: "Runner",
  code_agent: "CodeAgent",
  branch_if: "If",
  branch_and: "And",
  branch_or: "Or",
  sentry: "Sentry Agent",
  plugins: "Plugin Executor",
  quality: "Quality Evaluator",
  report: "Report Generator",
};

function createNodeId(agentKey: string) {
  return `${agentKey}_${Date.now()}_${Math.random().toString(16).slice(2, 8)}`;
}

function cloneTemplate(template: WorkflowTemplateData): WorkflowTemplateData {
  return JSON.parse(JSON.stringify(template)) as WorkflowTemplateData;
}

function readSavedTemplates(): WorkflowTemplateData[] {
  try {
    const rawValue = localStorage.getItem(STORAGE_KEY);
    return rawValue ? (JSON.parse(rawValue) as WorkflowTemplateData[]) : [];
  } catch {
    return [];
  }
}

function writeSavedTemplates(templates: WorkflowTemplateData[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(templates));
}

function buildSequentialConnections(nodes: AgentNodeData[]): ConnectionData[] {
  return nodes.slice(0, -1).map((node, index) => ({
    fromNodeId: node.nodeId,
    toNodeId: nodes[index + 1].nodeId,
  }));
}

function normalizeTemplateKey(value: string) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_]+/g, "_")
    .replace(/^_+|_+$/g, "") || `custom_${Date.now()}`;
}

function compactPosition(index: number) {
  return {
    x: LAYOUT_START_X + (index % LAYOUT_COLUMNS) * LAYOUT_COLUMN_GAP,
    y: LAYOUT_START_Y + Math.floor(index / LAYOUT_COLUMNS) * LAYOUT_ROW_GAP,
  };
}

function clampScale(scale: number) {
  return Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale));
}

function defaultViewport(): WorkflowViewport {
  return { ...DEFAULT_VIEWPORT };
}

export const useWorkflowEditorStore = defineStore("workflow-editor", {
  state: (): WorkflowEditorState => ({
    workflowTemplateKey: "custom_workflow",
    workflowName: "自定义工作流",
    workflowDescription: "通过 Vue Workflow Editor 生成的工作流模板。",
    nodes: [],
    connections: [],
    viewport: defaultViewport(),
    selectedNodeId: "",
    selectedNodeIds: [],
    undoStack: [],
    redoStack: [],
    savedTemplates: readSavedTemplates(),
  }),
  getters: {
    selectedNode(state): AgentNodeData | null {
      return state.nodes.find((node) => node.nodeId === state.selectedNodeId) || null;
    },
    orderedNodes(state): AgentNodeData[] {
      return state.nodes;
    },
    canUndo(state): boolean {
      return state.undoStack.length > 0;
    },
    canRedo(state): boolean {
      return state.redoStack.length > 0;
    },
  },
  actions: {
    snapshot(): WorkflowTemplateData {
      return {
        workflowTemplateKey: this.workflowTemplateKey,
        name: this.workflowName,
        description: this.workflowDescription,
        nodes: this.nodes.map((node) => ({ ...node, position: { ...node.position } })),
        connections: this.connections.map((connection) => ({ ...connection })),
        version: "1.0",
      };
    },
    commitHistory() {
      this.undoStack.push(cloneTemplate(this.snapshot()));
      this.redoStack = [];
    },
    restore(template: WorkflowTemplateData) {
      this.workflowTemplateKey = template.workflowTemplateKey;
      this.workflowName = template.name;
      this.workflowDescription = template.description;
      this.nodes = template.nodes.map((node) => ({ ...node, position: { ...node.position } }));
      this.connections = template.connections.map((connection) => ({ ...connection }));
      this.viewport = defaultViewport();
      this.setSelection(this.nodes[0]?.nodeId ? [this.nodes[0].nodeId] : []);
    },
    refreshConnections() {
      this.connections = buildSequentialConnections(this.nodes);
    },
    newBlankWorkflow() {
      this.commitHistory();
      this.workflowTemplateKey = "custom_workflow";
      this.workflowName = "自定义工作流";
      this.workflowDescription = "通过 Vue Workflow Editor 生成的工作流模板。";
      this.nodes = [];
      this.connections = [];
      this.viewport = defaultViewport();
      this.clearSelection();
    },
    loadTemplate(template: WorkflowTemplate) {
      this.commitHistory();
      this.workflowTemplateKey = template.key;
      this.workflowName = template.name;
      this.workflowDescription = template.description;
      this.nodes = template.agent_sequence.map((agentKey, index) => ({
        nodeId: `${template.key}_${agentKey}_${index + 1}`,
        agentKey,
        name: agentLabels[agentKey] || agentKey,
        position: compactPosition(index),
        input_fields: index === 0 ? ["requirement"] : [`${template.agent_sequence[index - 1]}_result`],
        output_fields: [`${agentKey}_result`],
        stage: template.stage_sequence[index] || "未分类",
        enabled: template.enabled,
        description: `${template.name} 的 ${agentLabels[agentKey] || agentKey} 节点`,
      }));
      this.refreshConnections();
      this.viewport = defaultViewport();
      this.setSelection(this.nodes[0]?.nodeId ? [this.nodes[0].nodeId] : []);
    },
    loadTemplateData(template: WorkflowTemplateData) {
      this.commitHistory();
      this.restore(cloneTemplate(template));
    },
    addAgentNode(agent: AgentMeta, position: { x: number; y: number }) {
      this.commitHistory();
      const node: AgentNodeData = {
        nodeId: createNodeId(agent.key),
        agentKey: agent.key,
        name: agent.name || agent.key,
        position,
        input_fields: [...agent.input_fields],
        output_fields: [...agent.output_fields],
        stage: agent.stage || "custom",
        enabled: agent.enabled,
        description: agent.description || "",
      };

      this.nodes.push(node);
      this.refreshConnections();
      this.setSelection([node.nodeId]);
    },
    selectNode(nodeId: string) {
      this.setSelection(nodeId ? [nodeId] : []);
    },
    setSelection(nodeIds: string[]) {
      const validIds = new Set(this.nodes.map((node) => node.nodeId));
      this.selectedNodeIds = [...new Set(nodeIds)].filter((nodeId) => validIds.has(nodeId));
      this.selectedNodeId = this.selectedNodeIds[this.selectedNodeIds.length - 1] || "";
    },
    toggleNodeSelection(nodeId: string) {
      if (!this.nodes.some((node) => node.nodeId === nodeId)) {
        return;
      }

      if (this.selectedNodeIds.includes(nodeId)) {
        this.setSelection(this.selectedNodeIds.filter((id) => id !== nodeId));
      } else {
        this.setSelection([...this.selectedNodeIds, nodeId]);
      }
    },
    clearSelection() {
      this.selectedNodeId = "";
      this.selectedNodeIds = [];
    },
    updateNode(nodeId: string, patch: Partial<AgentNodeData>) {
      const node = this.nodes.find((item) => item.nodeId === nodeId);

      if (!node) {
        return;
      }

      this.commitHistory();
      Object.assign(node, patch);
      this.refreshConnections();
    },
    moveNodePosition(nodeId: string, position: { x: number; y: number }) {
      const node = this.nodes.find((item) => item.nodeId === nodeId);

      if (!node) {
        return;
      }

      node.position = {
        x: Math.max(16, position.x),
        y: Math.max(16, position.y),
      };
    },
    deleteNode(nodeId: string) {
      this.commitHistory();
      this.nodes = this.nodes.filter((node) => node.nodeId !== nodeId);
      this.refreshConnections();
      this.setSelection(this.selectedNodeIds.filter((id) => id !== nodeId));
    },
    deleteSelectedNodes() {
      if (!this.selectedNodeIds.length) {
        return;
      }

      this.commitHistory();
      const selectedIds = new Set(this.selectedNodeIds);
      this.nodes = this.nodes.filter((node) => !selectedIds.has(node.nodeId));
      this.refreshConnections();
      this.clearSelection();
    },
    moveNodeOrder(nodeId: string, direction: -1 | 1) {
      const index = this.nodes.findIndex((node) => node.nodeId === nodeId);
      const nextIndex = index + direction;

      if (index < 0 || nextIndex < 0 || nextIndex >= this.nodes.length) {
        return;
      }

      this.commitHistory();
      const [node] = this.nodes.splice(index, 1);
      this.nodes.splice(nextIndex, 0, node);
      this.refreshConnections();
    },
    autoLayoutNodes() {
      if (!this.nodes.length) {
        return;
      }

      this.commitHistory();
      this.nodes = this.nodes.map((node, index) => ({
        ...node,
        position: compactPosition(index),
      }));
      this.refreshConnections();
      this.viewport = defaultViewport();
      this.setSelection(this.nodes[0]?.nodeId ? [this.nodes[0].nodeId] : []);
    },
    autoLayoutSelectedNodes() {
      const selectedNodes = this.nodes.filter((node) => this.selectedNodeIds.includes(node.nodeId));

      if (selectedNodes.length < 2) {
        return;
      }

      this.commitHistory();
      const minX = Math.min(...selectedNodes.map((node) => node.position.x));
      const minY = Math.min(...selectedNodes.map((node) => node.position.y));

      selectedNodes.forEach((node, index) => {
        node.position = {
          x: minX + (index % LAYOUT_COLUMNS) * LAYOUT_COLUMN_GAP,
          y: minY + Math.floor(index / LAYOUT_COLUMNS) * LAYOUT_ROW_GAP,
        };
      });

      this.refreshConnections();
    },
    setViewport(viewport: Partial<WorkflowViewport>) {
      this.viewport = {
        x: viewport.x ?? this.viewport.x,
        y: viewport.y ?? this.viewport.y,
        scale: clampScale(viewport.scale ?? this.viewport.scale),
      };
    },
    panViewport(deltaX: number, deltaY: number) {
      this.viewport = {
        ...this.viewport,
        x: this.viewport.x + deltaX,
        y: this.viewport.y + deltaY,
      };
    },
    resetViewport() {
      this.viewport = defaultViewport();
    },
    zoomViewport(nextScale: number, anchor?: { x: number; y: number }) {
      const scale = clampScale(nextScale);

      if (!anchor) {
        this.viewport = {
          ...this.viewport,
          scale,
        };
        return;
      }

      const worldX = (anchor.x - this.viewport.x) / this.viewport.scale;
      const worldY = (anchor.y - this.viewport.y) / this.viewport.scale;

      this.viewport = {
        x: anchor.x - worldX * scale,
        y: anchor.y - worldY * scale,
        scale,
      };
    },
    undo() {
      const previous = this.undoStack.pop();

      if (!previous) {
        return;
      }

      this.redoStack.push(cloneTemplate(this.snapshot()));
      this.restore(previous);
    },
    redo() {
      const next = this.redoStack.pop();

      if (!next) {
        return;
      }

      this.undoStack.push(cloneTemplate(this.snapshot()));
      this.restore(next);
    },
    saveCurrentTemplate(key: string, name: string, description: string) {
      this.workflowTemplateKey = normalizeTemplateKey(key);
      this.workflowName = name.trim() || this.workflowName;
      this.workflowDescription = description.trim() || this.workflowDescription;
      const template = cloneTemplate(this.snapshot());
      const existingIndex = this.savedTemplates.findIndex(
        (item) => item.workflowTemplateKey === template.workflowTemplateKey,
      );

      if (existingIndex >= 0) {
        this.savedTemplates.splice(existingIndex, 1, template);
      } else {
        this.savedTemplates.unshift(template);
      }

      writeSavedTemplates(this.savedTemplates);
      return template;
    },
    exportTemplateData(): WorkflowTemplateData {
      return cloneTemplate(this.snapshot());
    },
  },
});
