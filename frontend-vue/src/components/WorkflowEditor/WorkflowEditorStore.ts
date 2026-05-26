import { defineStore } from "pinia";

import type { AgentMeta } from "@/types/agent";
import type {
  AgentNodeData,
  ConnectionData,
  WorkflowValidationIssue,
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
const LAYOUT_START_X = 320;
const LAYOUT_START_Y = 196;
const LAYOUT_COLUMN_GAP = 336;
const LAYOUT_ROW_GAP = 158;

const agentLabels: Record<string, string> = {
  product: "Product Agent",
  coder: "Coder Agent",
  tester: "Tester Agent",
  runner: "Runner",
  code_agent: "CodeAgent",
  custom_agent: "Custom Agent",
  human_approval: "Human Approval",
  branch_if: "If",
  branch_and: "And",
  branch_or: "Or",
  sentry: "Sentry Agent",
  plugins: "Plugin Executor",
  quality: "Quality Evaluator",
  report: "Report Generator",
};

const stagePriority: Record<string, number> = {
  product: 0,
  analysis: 0,
  coder: 1,
  implementation: 1,
  tester: 2,
  testing: 2,
  runner: 3,
  execution: 3,
  sentry: 4,
  repair: 4,
  code_agent: 5,
  code_ops: 5,
  approval: 6,
  human_approval: 6,
  report: 7,
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

function connectionKey(connection: ConnectionData) {
  return `${connection.fromNodeId}->${connection.toNodeId}`;
}

function normalizeTemplateKey(value: string) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_]+/g, "_")
    .replace(/^_+|_+$/g, "") || `custom_${Date.now()}`;
}

function laneIndexForNode(node: Pick<AgentNodeData, "agentKey" | "stage">) {
  const normalizedAgent = node.agentKey.toLowerCase();
  const normalizedStage = node.stage.toLowerCase().replace(/\s+/g, "_");

  if (normalizedAgent === "code_agent") {
    return stagePriority.code_agent;
  }

  if (normalizedAgent === "human_approval") {
    return stagePriority.human_approval;
  }

  if (normalizedAgent.includes("product")) {
    return stagePriority.product;
  }

  if (normalizedAgent.includes("coder")) {
    return stagePriority.coder;
  }

  if (normalizedAgent.includes("tester")) {
    return stagePriority.tester;
  }

  if (normalizedAgent.includes("runner")) {
    return stagePriority.runner;
  }

  if (normalizedAgent.includes("sentry")) {
    return stagePriority.sentry;
  }

  if (normalizedAgent.includes("report")) {
    return stagePriority.report;
  }

  return stagePriority[normalizedStage] ?? 1;
}

function compactPosition(index: number, node?: Pick<AgentNodeData, "agentKey" | "stage">) {
  const lane = node ? laneIndexForNode(node) : index;

  return {
    x: LAYOUT_START_X + lane * LAYOUT_COLUMN_GAP,
    y: LAYOUT_START_Y + Math.floor(index / 7) * LAYOUT_ROW_GAP,
  };
}

function clampScale(scale: number) {
  return Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale));
}

function defaultViewport(): WorkflowViewport {
  return { ...DEFAULT_VIEWPORT };
}

function layoutViewport(): WorkflowViewport {
  return {
    x: 24,
    y: 34,
    scale: 0.9,
  };
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
    selectedConnectionId: "",
    connectionMode: "idle",
    showStageGuide: false,
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
      this.showStageGuide = false;
      this.selectedConnectionId = "";
      this.connectionMode = "idle";
      this.setSelection(this.nodes[0]?.nodeId ? [this.nodes[0].nodeId] : []);
    },
    refreshConnections() {
      this.connections = buildSequentialConnections(this.nodes);
      this.selectedConnectionId = "";
    },
    rebuildSequentialConnections() {
      this.commitHistory();
      this.refreshConnections();
      this.showStageGuide = false;
    },
    newBlankWorkflow() {
      this.commitHistory();
      this.workflowTemplateKey = "custom_workflow";
      this.workflowName = "自定义工作流";
      this.workflowDescription = "通过 Vue Workflow Editor 生成的工作流模板。";
      this.nodes = [];
      this.connections = [];
      this.viewport = defaultViewport();
      this.showStageGuide = false;
      this.clearSelection();
      this.clearConnectionSelection();
    },
    loadTemplate(template: WorkflowTemplate) {
      this.commitHistory();
      this.workflowTemplateKey = template.key;
      this.workflowName = template.name;
      this.workflowDescription = template.description;
      this.nodes = template.agent_sequence.map((agentKey, index) => ({
        nodeId: `${template.key}_${agentKey}_${index + 1}`,
        agentKey,
        nodeType:
          agentKey === "code_agent"
            ? "code_agent"
            : agentKey === "human_approval"
              ? "human_approval"
              : agentKey.startsWith("branch_")
                ? "branch"
                : "agent",
        name: agentLabels[agentKey] || agentKey,
        role: "",
        position: compactPosition(index, {
          agentKey,
          stage: template.stage_sequence[index] || "未分类",
        }),
        input_fields: index === 0 ? ["requirement"] : [`${template.agent_sequence[index - 1]}_result`],
        output_fields: [`${agentKey}_result`],
        stage: template.stage_sequence[index] || "未分类",
        enabled: template.enabled,
        description: `${template.name} 的 ${agentLabels[agentKey] || agentKey} 节点`,
        codeAgentConfig:
          agentKey === "code_agent"
            ? {
                operation: "write_file",
                target_path: "output/code_agent_demo.txt",
                content: "",
                audit_log_path: "output/code_agent_audit.jsonl",
              }
            : undefined,
        humanApprovalConfig:
          agentKey === "human_approval"
            ? {
                question: "是否批准继续执行后续节点？",
                approveLabel: "批准继续",
                rejectLabel: "拒绝停止",
                required: true,
              }
            : undefined,
      }));
      this.refreshConnections();
      this.viewport = defaultViewport();
      this.showStageGuide = false;
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
        nodeType: agent.key === "code_agent"
          ? "code_agent"
          : agent.key === "human_approval"
            ? "human_approval"
            : agent.key === "custom_agent"
              ? "custom_agent"
              : agent.key.startsWith("branch_")
                ? "branch"
                : "agent",
        name: agent.name || agent.key,
        role: agent.role || "",
        position,
        input_fields: [...agent.input_fields],
        output_fields: [...agent.output_fields],
        stage: agent.stage || "custom",
        enabled: agent.enabled,
        description: agent.description || "",
        codeAgentConfig:
          agent.key === "code_agent"
            ? {
                operation: "write_file",
                target_path: "output/code_agent_demo.txt",
                content: "",
                audit_log_path: "output/code_agent_audit.jsonl",
              }
            : undefined,
        humanApprovalConfig:
          agent.key === "human_approval"
            ? {
                question: "是否批准继续执行后续节点？",
                approveLabel: "批准继续",
                rejectLabel: "拒绝停止",
                required: true,
              }
            : undefined,
        customAgentMeta:
          agent.key === "custom_agent"
            ? {
                role: agent.role || "自定义智能体",
                promptRef: "",
                version: "1.0",
              }
            : undefined,
      };

      this.nodes.push(node);
      this.showStageGuide = false;
      const previousNode = this.nodes[this.nodes.length - 2];

      if (previousNode) {
        const nextConnection = {
          fromNodeId: previousNode.nodeId,
          toNodeId: node.nodeId,
        };

        if (!this.connections.some((connection) => connectionKey(connection) === connectionKey(nextConnection))) {
          this.connections.push(nextConnection);
        }
      }

      this.setSelection([node.nodeId]);
    },
    selectNode(nodeId: string) {
      this.setSelection(nodeId ? [nodeId] : []);
    },
    setSelection(nodeIds: string[]) {
      const validIds = new Set(this.nodes.map((node) => node.nodeId));
      this.selectedNodeIds = [...new Set(nodeIds)].filter((nodeId) => validIds.has(nodeId));
      this.selectedNodeId = this.selectedNodeIds[this.selectedNodeIds.length - 1] || "";
      this.selectedConnectionId = "";
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
    selectConnection(connectionId: string) {
      if (!this.connections.some((connection) => connectionKey(connection) === connectionId)) {
        this.selectedConnectionId = "";
        return;
      }

      this.selectedNodeId = "";
      this.selectedNodeIds = [];
      this.selectedConnectionId = connectionId;
    },
    clearConnectionSelection() {
      this.selectedConnectionId = "";
      this.connectionMode = "idle";
    },
    addConnection(fromNodeId: string, toNodeId: string) {
      if (!fromNodeId || !toNodeId || fromNodeId === toNodeId) {
        return;
      }

      const fromExists = this.nodes.some((node) => node.nodeId === fromNodeId);
      const toExists = this.nodes.some((node) => node.nodeId === toNodeId);

      if (!fromExists || !toExists) {
        return;
      }

      const nextConnection: ConnectionData = { fromNodeId, toNodeId };
      const nextKey = connectionKey(nextConnection);

      if (this.connections.some((connection) => connectionKey(connection) === nextKey)) {
        this.selectConnection(nextKey);
        return;
      }

      this.commitHistory();
      this.connections.push(nextConnection);
      this.showStageGuide = false;
      this.selectConnection(nextKey);
    },
    deleteConnection(connectionId: string) {
      if (!connectionId) {
        return;
      }

      const nextConnections = this.connections.filter((connection) => connectionKey(connection) !== connectionId);

      if (nextConnections.length === this.connections.length) {
        return;
      }

      this.commitHistory();
      this.connections = nextConnections;
      this.showStageGuide = false;
      this.selectedConnectionId = "";
    },
    deleteSelectedConnection() {
      if (!this.selectedConnectionId) {
        return;
      }

      this.deleteConnection(this.selectedConnectionId);
    },
    updateNode(nodeId: string, patch: Partial<AgentNodeData>) {
      const node = this.nodes.find((item) => item.nodeId === nodeId);

      if (!node) {
        return;
      }

      this.commitHistory();
      Object.assign(node, patch);
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
      this.showStageGuide = false;
    },
    deleteNode(nodeId: string) {
      this.commitHistory();
      this.nodes = this.nodes.filter((node) => node.nodeId !== nodeId);
      this.connections = this.connections.filter(
        (connection) => connection.fromNodeId !== nodeId && connection.toNodeId !== nodeId,
      );
      this.showStageGuide = false;
      this.selectedConnectionId = "";
      this.setSelection(this.selectedNodeIds.filter((id) => id !== nodeId));
    },
    deleteSelectedNodes() {
      if (!this.selectedNodeIds.length) {
        return;
      }

      this.commitHistory();
      const selectedIds = new Set(this.selectedNodeIds);
      this.nodes = this.nodes.filter((node) => !selectedIds.has(node.nodeId));
      this.connections = this.connections.filter(
        (connection) => !selectedIds.has(connection.fromNodeId) && !selectedIds.has(connection.toNodeId),
      );
      this.showStageGuide = false;
      this.clearSelection();
      this.clearConnectionSelection();
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
      this.showStageGuide = false;
    },
    autoLayoutNodes() {
      if (!this.nodes.length) {
        return;
      }

      this.commitHistory();
      const laneRows = new Map<number, number>();
      const outgoingGroups = new Map<string, ConnectionData[]>();
      const incomingGroups = new Map<string, ConnectionData[]>();

      this.connections.forEach((connection) => {
        outgoingGroups.set(connection.fromNodeId, [...(outgoingGroups.get(connection.fromNodeId) || []), connection]);
        incomingGroups.set(connection.toNodeId, [...(incomingGroups.get(connection.toNodeId) || []), connection]);
      });

      this.nodes = [...this.nodes]
        .sort((left, right) => laneIndexForNode(left) - laneIndexForNode(right))
        .map((node) => {
        const lane = laneIndexForNode(node);
        const row = laneRows.get(lane) || 0;
        laneRows.set(lane, row + 1);
        const incoming = incomingGroups.get(node.nodeId) || [];
        const primaryParent = incoming[0]?.fromNodeId;
        const siblings = primaryParent ? outgoingGroups.get(primaryParent) || [] : [];
        const branchIndex = primaryParent ? siblings.findIndex((connection) => connection.toNodeId === node.nodeId) : -1;
        const branchOffset =
          siblings.length > 1 && branchIndex >= 0 ? (branchIndex - (siblings.length - 1) / 2) * 48 : 0;

        return {
          ...node,
          position: {
            x: LAYOUT_START_X + lane * LAYOUT_COLUMN_GAP,
            y: LAYOUT_START_Y + row * LAYOUT_ROW_GAP + branchOffset,
          },
        };
      });
      this.viewport = layoutViewport();
      this.showStageGuide = true;
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
          x: minX + index * LAYOUT_COLUMN_GAP,
          y: minY,
        };
      });
      this.showStageGuide = true;
    },
    validateWorkflow(): WorkflowValidationIssue[] {
      const issues: WorkflowValidationIssue[] = [];
      const nodeIds = new Set(this.nodes.map((node) => node.nodeId));

      if (!this.nodes.length) {
        return [
          {
            severity: "error",
            title: "没有节点",
            message: "请先从 Agent Palette 拖入至少一个节点，或加载 Workflow 模板。",
          },
        ];
      }

      const missingSourceConnections = this.connections.filter((connection) => !nodeIds.has(connection.fromNodeId));
      const missingTargetConnections = this.connections.filter((connection) => !nodeIds.has(connection.toNodeId));
      const selfConnections = this.connections.filter((connection) => connection.fromNodeId === connection.toNodeId);
      const seenConnections = new Set<string>();
      const duplicateConnections = this.connections.filter((connection) => {
        const key = connectionKey(connection);

        if (seenConnections.has(key)) {
          return true;
        }

        seenConnections.add(key);
        return false;
      });

      if (missingSourceConnections.length) {
        issues.push({
          severity: "error",
          title: "连线 source 不存在",
          message: `发现 ${missingSourceConnections.length} 条连线的起点节点不存在，请删除后重新连接。`,
        });
      }

      if (missingTargetConnections.length) {
        issues.push({
          severity: "error",
          title: "连线 target 不存在",
          message: `发现 ${missingTargetConnections.length} 条连线的终点节点不存在，请删除后重新连接。`,
        });
      }

      if (duplicateConnections.length) {
        issues.push({
          severity: "warning",
          title: "存在重复连线",
          message: `发现 ${duplicateConnections.length} 条重复连线，建议删除重复项以保持流程清晰。`,
        });
      }

      if (selfConnections.length) {
        issues.push({
          severity: "error",
          title: "存在自连接",
          message: `发现 ${selfConnections.length} 条节点连接到自己的连线，请删除后重新连接。`,
        });
      }

      const validConnections = this.connections.filter(
        (connection) =>
          nodeIds.has(connection.fromNodeId) &&
          nodeIds.has(connection.toNodeId) &&
          connection.fromNodeId !== connection.toNodeId,
      );
      const incoming = new Set(validConnections.map((connection) => connection.toNodeId));
      const outgoing = new Set(validConnections.map((connection) => connection.fromNodeId));
      const entryNodes = this.nodes.filter((node) => !incoming.has(node.nodeId));

      if (!entryNodes.length) {
        issues.push({
          severity: "error",
          title: "没有入口节点",
          message: "当前流程没有明确入口，请保留至少一个无上游连线的起始节点。",
        });
      }

      if (this.nodes.length > 1) {
        this.nodes
          .filter((node) => !incoming.has(node.nodeId) && !outgoing.has(node.nodeId))
          .forEach((node) => {
            issues.push({
              severity: "error",
              title: "存在孤立节点",
              message: `${node.name} 没有上游或下游连线。`,
              nodeId: node.nodeId,
            });
          });
      }

      const outgoingGroups = validConnections.reduce<Record<string, ConnectionData[]>>((groups, connection) => {
        groups[connection.fromNodeId] = [...(groups[connection.fromNodeId] || []), connection];
        return groups;
      }, {});

      Object.entries(outgoingGroups)
        .filter(([, connections]) => connections.length > 3)
        .forEach(([nodeId, connections]) => {
          const sourceNode = this.nodes.find((node) => node.nodeId === nodeId);
          const targetNodes = connections
            .map((connection) => this.nodes.find((node) => node.nodeId === connection.toNodeId))
            .filter((node): node is AgentNodeData => Boolean(node));
          const minY = Math.min(...targetNodes.map((node) => node.position.y));
          const maxY = Math.max(...targetNodes.map((node) => node.position.y));

          if (targetNodes.length && maxY - minY < (connections.length - 1) * 36) {
            issues.push({
              severity: "warning",
              title: "多分支布局过密",
              message: `${sourceNode?.name || nodeId} 有 ${connections.length} 条下游连线，建议点击自动整理让分支上下分散。`,
              nodeId,
            });
          }
        });

      this.nodes
        .filter((node) => !node.enabled)
        .forEach((node) => {
          issues.push({
            severity: "warning",
            title: "存在禁用节点",
            message: `${node.name} 当前为禁用状态，生成任务时可能不符合演示预期。`,
            nodeId: node.nodeId,
          });
        });

      this.nodes
        .filter((node) => node.agentKey === "code_agent" || node.nodeType === "code_agent")
        .forEach((node) => {
          if (!node.codeAgentConfig?.operation) {
            issues.push({
              severity: "error",
              title: "CodeAgent 缺少 operation",
              message: `${node.name} 需要配置 read_file / write_file / list_files 或文件夹操作。`,
              nodeId: node.nodeId,
            });
          }

          if (!node.codeAgentConfig?.target_path?.trim()) {
            issues.push({
              severity: "error",
              title: "CodeAgent 缺少 target_path",
              message: `${node.name} 需要配置目标文件或目录路径。`,
              nodeId: node.nodeId,
            });
          }
        });

      this.nodes
        .filter((node) => node.agentKey === "human_approval" || node.nodeType === "human_approval")
        .forEach((node) => {
          if (!node.humanApprovalConfig?.question?.trim()) {
            issues.push({
              severity: "warning",
              title: "Human Approval 缺少问题文案",
              message: `${node.name} 建议配置清晰的人工确认问题，方便演示暂停点。`,
              nodeId: node.nodeId,
            });
          }
        });

      this.nodes
        .filter((node) => node.agentKey === "custom_agent" || node.nodeType === "custom_agent")
        .forEach((node) => {
          if (!node.name.trim() || !node.stage.trim()) {
            issues.push({
              severity: "warning",
              title: "自定义 Agent 元信息不完整",
              message: "自定义 Agent 建议配置名称和阶段，当前仅作为模板可视化节点保存。",
              nodeId: node.nodeId,
            });
          }
        });

      return issues;
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
