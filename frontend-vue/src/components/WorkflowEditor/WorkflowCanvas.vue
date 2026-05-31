<script setup lang="ts">
import { Delete, Minus, Plus, Refresh } from "@element-plus/icons-vue";
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import AgentNode from "./AgentNode.vue";
import { useWorkflowEditorStore } from "./WorkflowEditorStore";

import type { AgentMeta } from "@/types/agent";
import type { ConnectionData, PendingConnectionData, WorkflowSelectionBox } from "@/types/workflowEditor";
import {
  classifyWorkflowField,
  workflowConnectionKey,
  workflowConnectionLabel,
  workflowPortColor,
} from "@/utils/workflowPorts";

type EdgeRenderMeta = {
  key: string;
  renderKey: string;
  fromNodeId: string;
  toNodeId: string;
  fromOutputField?: string;
  toInputField?: string;
  sourceName: string;
  targetName: string;
  label: string;
  edgeType?: string;
  condition?: string;
  maxIterations?: number;
  color: string;
  labelX: number;
  labelY: number;
  path: string;
  minimapPath: string;
  selected: boolean;
};

type StageLaneGuide = {
  key: string;
  label: string;
  x: number;
  index: number;
  nodeCount: number;
  active: boolean;
};

const props = defineProps<{
  agents: AgentMeta[];
  paletteAvoidanceWidth?: number;
}>();

const WORLD_WIDTH = 6000;
const WORLD_HEIGHT = 4200;
const GRID_SIZE = 24;
const NODE_WIDTH = 416;
const NODE_HEIGHT = 176;
const PORT_START_Y = 64;
const PORT_GAP = 30;
const FANOUT_OFFSET = 12;
const MINIMAP_WIDTH = 176;
const MINIMAP_HEIGHT = 120;
const STAGE_START_X = 320;
const STAGE_COLUMN_GAP = 500;
const STAGE_LANES = [
  { key: "analysis", label: "Analysis" },
  { key: "implementation", label: "Implementation" },
  { key: "testing", label: "Testing" },
  { key: "execution", label: "Execution" },
  { key: "repair", label: "Repair" },
  { key: "code_ops", label: "Code Ops" },
  { key: "report", label: "Report" },
];

const store = useWorkflowEditorStore();
const canvasRef = ref<HTMLElement | null>(null);
const minimapRef = ref<HTMLElement | null>(null);
const isSpacePressed = ref(false);
const isPanning = ref(false);
const ignoreNextClick = ref(false);
const selectionBox = ref<WorkflowSelectionBox | null>(null);
const pendingConnection = ref<PendingConnectionData | null>(null);
const hoveredConnectionKey = ref("");
const canvasSize = ref({ width: 0, height: 0 });
const minimapDragging = ref(false);
const showMinimap = ref(false);
const draggingNode = ref<{
  nodeId: string;
  startX: number;
  startY: number;
  nodeOrigins: Record<string, { x: number; y: number }>;
} | null>(null);
const panning = ref<{
  startX: number;
  startY: number;
  originX: number;
  originY: number;
} | null>(null);

const canvasNodes = computed(() => store.orderedNodes);
const zoomPercent = computed(() => `${Math.round(store.viewport.scale * 100)}%`);
const selectedCount = computed(() => store.selectedNodeIds.length);
const selectedConnection = computed(() => store.selectedConnectionId);
const selectedConnectionData = computed(() =>
  store.connections.find((connection) => workflowConnectionKey(connection) === store.selectedConnectionId) || null,
);
const showHandles = computed(() => store.connectionMode === "connecting");
const shouldRenderMinimap = computed(() => showMinimap.value && store.nodes.length > 8);
const visibleStageLanes = computed<StageLaneGuide[]>(() => {
  if (!store.showStageGuide || !store.nodes.length) {
    return [];
  }

  const counts = store.nodes.reduce<Record<string, number>>((stageCounts, node) => {
    const stageKey = stageKeyForNode(node);
    stageCounts[stageKey] = (stageCounts[stageKey] || 0) + 1;
    return stageCounts;
  }, {});

  return STAGE_LANES.map((lane, index) => ({
    ...lane,
    index,
    x: STAGE_START_X + index * STAGE_COLUMN_GAP,
    nodeCount: counts[lane.key] || 0,
    active: Boolean(counts[lane.key]),
  }));
});
const canvasStyle = computed(() => ({
  "--grid-size": `${GRID_SIZE * store.viewport.scale}px`,
  "--grid-x": `${store.viewport.x}px`,
  "--grid-y": `${store.viewport.y}px`,
  "--palette-safe-width": `${props.paletteAvoidanceWidth ?? 0}px`,
}));
const worldStyle = computed(() => ({
  width: `${WORLD_WIDTH}px`,
  height: `${WORLD_HEIGHT}px`,
  transform: `translate(${store.viewport.x}px, ${store.viewport.y}px) scale(${store.viewport.scale})`,
}));
const selectionBoxStyle = computed(() => {
  if (!selectionBox.value) {
    return {};
  }

  const left = Math.min(selectionBox.value.startX, selectionBox.value.currentX);
  const top = Math.min(selectionBox.value.startY, selectionBox.value.currentY);
  const width = Math.abs(selectionBox.value.currentX - selectionBox.value.startX);
  const height = Math.abs(selectionBox.value.currentY - selectionBox.value.startY);

  return {
    left: `${left}px`,
    top: `${top}px`,
    width: `${width}px`,
    height: `${height}px`,
  };
});
const minimapScale = computed(() => Math.min(MINIMAP_WIDTH / WORLD_WIDTH, MINIMAP_HEIGHT / WORLD_HEIGHT));
const minimapNodes = computed(() =>
  store.nodes.map((node) => ({
    ...node,
    selected: store.selectedNodeIds.includes(node.nodeId),
    style: {
      left: `${node.position.x * minimapScale.value}px`,
      top: `${node.position.y * minimapScale.value}px`,
      width: `${NODE_WIDTH * minimapScale.value}px`,
      height: `${NODE_HEIGHT * minimapScale.value}px`,
    },
  })),
);
const minimapViewportStyle = computed(() => {
  const scale = minimapScale.value;
  const worldX = Math.max(0, -store.viewport.x / store.viewport.scale);
  const worldY = Math.max(0, -store.viewport.y / store.viewport.scale);
  const width = Math.min(WORLD_WIDTH, canvasSize.value.width / store.viewport.scale);
  const height = Math.min(WORLD_HEIGHT, canvasSize.value.height / store.viewport.scale);

  return {
    left: `${worldX * scale}px`,
    top: `${worldY * scale}px`,
    width: `${width * scale}px`,
    height: `${height * scale}px`,
  };
});
const pendingConnectionPath = computed(() => {
  if (!pendingConnection.value) {
    return "";
  }

  const start = getNodeAnchor(pendingConnection.value.fromNodeId, "output", pendingConnection.value.fromOutputField);

  return start ? stableEdgePath(start, pendingConnection.value.pointer) : "";
});
const pendingConnectionColor = computed(() => pendingConnection.value?.color || "#1a73e8");
const renderedConnections = computed<EdgeRenderMeta[]>(() => {
  const nodeById = new Map(store.nodes.map((node) => [node.nodeId, node]));
  const visualOrder = new Map(
    [...store.nodes]
      .sort((left, right) => left.position.x - right.position.x || left.position.y - right.position.y)
      .map((node, index) => [node.nodeId, index]),
  );
  const validConnections = store.connections
    .filter((connection) => nodeById.has(connection.fromNodeId) && nodeById.has(connection.toNodeId))
    .map((connection, index) => ({ ...connection, index }))
    .sort((left, right) => {
      const leftSource = visualOrder.get(left.fromNodeId) ?? 0;
      const rightSource = visualOrder.get(right.fromNodeId) ?? 0;
      const leftTarget = nodeById.get(left.toNodeId);
      const rightTarget = nodeById.get(right.toNodeId);

      return (
        leftSource - rightSource ||
        (leftTarget?.position.y ?? 0) - (rightTarget?.position.y ?? 0) ||
        (leftTarget?.position.x ?? 0) - (rightTarget?.position.x ?? 0) ||
        left.index - right.index
      );
    });
  const outgoingGroups = new Map<string, typeof validConnections>();
  const incomingGroups = new Map<string, typeof validConnections>();

  validConnections.forEach((connection) => {
    const outputGroupKey = `${connection.fromNodeId}:${connection.fromOutputField || "*"}`;
    const inputGroupKey = `${connection.toNodeId}:${connection.toInputField || "*"}`;

    outgoingGroups.set(outputGroupKey, [...(outgoingGroups.get(outputGroupKey) || []), connection]);
    incomingGroups.set(inputGroupKey, [...(incomingGroups.get(inputGroupKey) || []), connection]);
  });

  return validConnections.map((connection) => {
    const key = connectionKey(connection);
    const sourceNode = nodeById.get(connection.fromNodeId);
    const targetNode = nodeById.get(connection.toNodeId);
    const outgoing = outgoingGroups.get(`${connection.fromNodeId}:${connection.fromOutputField || "*"}`) || [];
    const incoming = incomingGroups.get(`${connection.toNodeId}:${connection.toInputField || "*"}`) || [];
    const sourceRank = outgoing.findIndex((item) => item.index === connection.index);
    const targetRank = incoming.findIndex((item) => item.index === connection.index);
    const start = getNodeAnchor(
      connection.fromNodeId,
      "output",
      connection.fromOutputField,
      fanoutOffset(sourceRank, outgoing.length),
    );
    const end = getNodeAnchor(
      connection.toNodeId,
      "input",
      connection.toInputField,
      fanoutOffset(targetRank, incoming.length),
    );
    const path = start && end ? stableEdgePath(start, end) : "";
    const dataType = connection.dataType || classifyWorkflowField(connection.fromOutputField || connection.toInputField || "");
    const color = connection.color || workflowPortColor(connection.fromOutputField || connection.toInputField || "", dataType);

    return {
      key,
      renderKey: `${key}-${connection.index}`,
      fromNodeId: connection.fromNodeId,
      toNodeId: connection.toNodeId,
      fromOutputField: connection.fromOutputField,
      toInputField: connection.toInputField,
      sourceName: sourceNode?.name || connection.fromNodeId,
      targetName: targetNode?.name || connection.toNodeId,
      label: workflowConnectionLabel(connection, sourceNode?.name || "", targetNode?.name || ""),
      edgeType: connection.edgeType || "control",
      condition: connection.condition || "",
      maxIterations: connection.loopPolicy?.maxIterations,
      color,
      labelX: start && end ? start.x + (end.x - start.x) * 0.42 : 0,
      labelY: start && end ? start.y + (end.y - start.y) * 0.42 - 10 : 0,
      path,
      minimapPath: path ? scalePath(start!, end!, minimapScale.value) : "",
      selected: key === selectedConnection.value,
    };
  });
});
const activePortFieldsByNode = computed(() => {
  const activeKeys = new Set([selectedConnection.value, hoveredConnectionKey.value].filter(Boolean));
  const inputs = new Map<string, string[]>();
  const outputs = new Map<string, string[]>();

  store.connections.forEach((connection) => {
    if (!activeKeys.has(connectionKey(connection))) {
      return;
    }

    if (connection.fromOutputField) {
      outputs.set(connection.fromNodeId, [...(outputs.get(connection.fromNodeId) || []), connection.fromOutputField]);
    }

    if (connection.toInputField) {
      inputs.set(connection.toNodeId, [...(inputs.get(connection.toNodeId) || []), connection.toInputField]);
    }
  });

  return { inputs, outputs };
});

let resizeObserver: ResizeObserver | null = null;

function screenToWorld(event: Pick<PointerEvent | DragEvent | WheelEvent, "clientX" | "clientY">) {
  const rect = canvasRef.value?.getBoundingClientRect();

  if (!rect) {
    return { x: 0, y: 0 };
  }

  return {
    x: (event.clientX - rect.left - store.viewport.x) / store.viewport.scale,
    y: (event.clientY - rect.top - store.viewport.y) / store.viewport.scale,
  };
}

function canvasPoint(event: Pick<PointerEvent | DragEvent | WheelEvent, "clientX" | "clientY">) {
  const rect = canvasRef.value?.getBoundingClientRect();

  if (!rect) {
    return { x: 0, y: 0 };
  }

  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
  };
}

function connectionKey(connection: { fromNodeId: string; toNodeId: string }) {
  return workflowConnectionKey(connection as ConnectionData);
}

function stageKeyForNode(node: { agentKey: string; stage: string }) {
  const agentKey = node.agentKey.toLowerCase();
  const stage = node.stage.toLowerCase().replace(/\s+/g, "_");

  if (agentKey === "code_agent") {
    return "code_ops";
  }

  if (agentKey.includes("product")) {
    return "analysis";
  }

  if (agentKey.includes("coder")) {
    return "implementation";
  }

  if (agentKey.includes("tester")) {
    return "testing";
  }

  if (agentKey.includes("runner")) {
    return "execution";
  }

  if (agentKey.includes("sentry")) {
    return "repair";
  }

  if (agentKey.includes("report")) {
    return "report";
  }

  return STAGE_LANES.some((lane) => lane.key === stage) ? stage : "implementation";
}

function getNodeAnchor(nodeId: string, side: "input" | "output", field?: string, yOffset = 0) {
  const node = store.nodes.find((item) => item.nodeId === nodeId);

  if (!node) {
    return null;
  }

  const fields = side === "output" ? node.output_fields : node.input_fields;
  const fieldIndex = field ? fields.indexOf(field) : -1;
  const portY = fieldIndex >= 0 ? PORT_START_Y + fieldIndex * PORT_GAP : NODE_HEIGHT / 2;

  return {
    x: node.position.x + (side === "output" ? NODE_WIDTH : 0),
    y: node.position.y + portY + yOffset,
  };
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function fanoutOffset(index: number, count: number) {
  if (count <= 1 || index < 0) {
    return 0;
  }

  return clamp((index - (count - 1) / 2) * FANOUT_OFFSET, -26, 26);
}

function stableEdgePath(start: { x: number; y: number }, end: { x: number; y: number }) {
  const horizontalGap = end.x - start.x;
  const verticalGap = Math.abs(end.y - start.y);

  if (horizontalGap <= 72) {
    const laneX = Math.max(start.x + 92, end.x + 92);
    const midY = start.y + (end.y - start.y) / 2;
    const entryTension = clamp(Math.abs(laneX - end.x) * 0.42, 34, 84);

    return [
      `M ${start.x} ${start.y}`,
      `C ${start.x + 52} ${start.y} ${laneX} ${start.y} ${laneX} ${midY}`,
      `C ${laneX} ${end.y} ${end.x - entryTension} ${end.y} ${end.x} ${end.y}`,
    ].join(" ");
  }

  const tension = clamp(horizontalGap * 0.38 + verticalGap * 0.04, 42, 148);

  return `M ${start.x} ${start.y} C ${start.x + tension} ${start.y} ${end.x - tension} ${end.y} ${end.x} ${end.y}`;
}

function scalePath(start: { x: number; y: number }, end: { x: number; y: number }, scale: number) {
  return stableEdgePath(
    {
      x: start.x * scale,
      y: start.y * scale,
    },
    {
      x: end.x * scale,
      y: end.y * scale,
    },
  );
}

function handleWheel(event: WheelEvent) {
  event.preventDefault();
  const point = canvasPoint(event);
  const direction = event.deltaY > 0 ? -1 : 1;
  const nextScale = store.viewport.scale * (1 + direction * 0.1);
  store.zoomViewport(nextScale, point);
}

function zoomBy(delta: number) {
  const rect = canvasRef.value?.getBoundingClientRect();

  store.zoomViewport(store.viewport.scale + delta, rect ? { x: rect.width / 2, y: rect.height / 2 } : undefined);
}

function resetViewport() {
  store.resetViewport();
}

function autoLayout() {
  store.autoLayoutNodes();
}

function autoLayoutSelected() {
  store.autoLayoutSelectedNodes();
}

function deleteSelected() {
  if (store.selectedConnectionId) {
    store.deleteSelectedConnection();
    return;
  }

  store.deleteSelectedNodes();
}

function rebuildSequentialConnections() {
  store.rebuildSequentialConnections();
}

function markSelectedConnection(edgeType: ConnectionData["edgeType"]) {
  if (!selectedConnectionData.value) {
    return;
  }

  store.updateConnection(store.selectedConnectionId, {
    edgeType,
    condition:
      edgeType === "branch"
        ? selectedConnectionData.value.condition || "success == true"
        : selectedConnectionData.value.condition || "",
    loopPolicy:
      edgeType === "loop"
        ? {
            maxIterations: selectedConnectionData.value.loopPolicy?.maxIterations || 3,
            exitCondition: selectedConnectionData.value.loopPolicy?.exitCondition || "",
          }
        : selectedConnectionData.value.loopPolicy,
  });
}

function updateCanvasSize() {
  const rect = canvasRef.value?.getBoundingClientRect();

  if (!rect) {
    return;
  }

  canvasSize.value = {
    width: rect.width,
    height: rect.height,
  };
}

function startViewportPan(event: PointerEvent) {
  event.preventDefault();
  isPanning.value = true;
  ignoreNextClick.value = false;
  panning.value = {
    startX: event.clientX,
    startY: event.clientY,
    originX: store.viewport.x,
    originY: store.viewport.y,
  };
  window.addEventListener("pointermove", moveViewportPan);
  window.addEventListener("pointerup", stopViewportPan);
}

function moveViewportPan(event: PointerEvent) {
  if (!panning.value) {
    return;
  }

  const deltaX = event.clientX - panning.value.startX;
  const deltaY = event.clientY - panning.value.startY;

  if (Math.abs(deltaX) + Math.abs(deltaY) > 3) {
    ignoreNextClick.value = true;
  }

  store.setViewport({
    x: panning.value.originX + deltaX,
    y: panning.value.originY + deltaY,
  });
}

function stopViewportPan() {
  isPanning.value = false;
  panning.value = null;
  window.removeEventListener("pointermove", moveViewportPan);
  window.removeEventListener("pointerup", stopViewportPan);
}

function handleCanvasPointerDown(event: PointerEvent) {
  if (event.button === 1 || (event.button === 0 && isSpacePressed.value)) {
    startViewportPan(event);
    return;
  }

  if (event.button === 0) {
    startSelectionBox(event);
  }
}

function handleCanvasClick() {
  if (ignoreNextClick.value) {
    ignoreNextClick.value = false;
    return;
  }

  store.clearSelection();
  store.clearConnectionSelection();
}

function startSelectionBox(event: PointerEvent) {
  const point = canvasPoint(event);

  event.preventDefault();
  store.clearConnectionSelection();
  selectionBox.value = {
    startX: point.x,
    startY: point.y,
    currentX: point.x,
    currentY: point.y,
  };
  window.addEventListener("pointermove", moveSelectionBox);
  window.addEventListener("pointerup", stopSelectionBox);
}

function moveSelectionBox(event: PointerEvent) {
  if (!selectionBox.value) {
    return;
  }

  const point = canvasPoint(event);
  selectionBox.value.currentX = point.x;
  selectionBox.value.currentY = point.y;
}

function stopSelectionBox(event: PointerEvent) {
  if (!selectionBox.value) {
    return;
  }

  const start = selectionBox.value;
  const endPoint = canvasPoint(event);
  const movement = Math.abs(endPoint.x - start.startX) + Math.abs(endPoint.y - start.startY);

  if (movement > 6) {
    ignoreNextClick.value = true;
    const minScreenX = Math.min(start.startX, endPoint.x);
    const maxScreenX = Math.max(start.startX, endPoint.x);
    const minScreenY = Math.min(start.startY, endPoint.y);
    const maxScreenY = Math.max(start.startY, endPoint.y);
    const rect = canvasRef.value?.getBoundingClientRect();

    if (rect) {
      const worldTopLeft = {
        x: (minScreenX - store.viewport.x) / store.viewport.scale,
        y: (minScreenY - store.viewport.y) / store.viewport.scale,
      };
      const worldBottomRight = {
        x: (maxScreenX - store.viewport.x) / store.viewport.scale,
        y: (maxScreenY - store.viewport.y) / store.viewport.scale,
      };
      const selectedIds = store.nodes
        .filter((node) => {
          const nodeRight = node.position.x + NODE_WIDTH;
          const nodeBottom = node.position.y + NODE_HEIGHT;

          return (
            node.position.x <= worldBottomRight.x &&
            nodeRight >= worldTopLeft.x &&
            node.position.y <= worldBottomRight.y &&
            nodeBottom >= worldTopLeft.y
          );
        })
        .map((node) => node.nodeId);

      store.setSelection(selectedIds);
    }
  } else {
    store.clearSelection();
  }

  selectionBox.value = null;
  window.removeEventListener("pointermove", moveSelectionBox);
  window.removeEventListener("pointerup", stopSelectionBox);
}

function handleDrop(event: DragEvent) {
  const agentKey = event.dataTransfer?.getData("application/x-agent-key");

  if (!agentKey) {
    return;
  }

  const agent = props.agents.find((item) => item.key === agentKey);

  if (!agent) {
    return;
  }

  const worldPoint = screenToWorld(event);

  store.addAgentNode(agent, {
    x: Math.max(0, worldPoint.x - 115),
    y: Math.max(0, worldPoint.y - 48),
  });
}

function startConnection(nodeId: string, outputField: string, event: PointerEvent) {
  if (event.button !== 0) {
    return;
  }

  const dataType = classifyWorkflowField(outputField);
  const start = getNodeAnchor(nodeId, "output", outputField);

  if (!start) {
    return;
  }

  event.preventDefault();
  event.stopPropagation();
  pendingConnection.value = {
    fromNodeId: nodeId,
    fromOutputField: outputField,
    dataType,
    color: workflowPortColor(outputField, dataType),
    pointer: screenToWorld(event),
  };
  store.connectionMode = "connecting";
  store.selectNode(nodeId);
  window.addEventListener("pointermove", moveConnection);
  window.addEventListener("pointerup", cancelConnection);
}

function moveConnection(event: PointerEvent) {
  if (!pendingConnection.value) {
    return;
  }

  pendingConnection.value = {
    ...pendingConnection.value,
    pointer: screenToWorld(event),
  };
}

function finishConnection(toNodeId: string, inputField: string, event: PointerEvent) {
  if (!pendingConnection.value) {
    return;
  }

  event.preventDefault();
  event.stopPropagation();
  store.addConnection(pendingConnection.value.fromNodeId, toNodeId, pendingConnection.value.fromOutputField, inputField);
  ignoreNextClick.value = true;
  clearPendingConnection();
}

function clearPendingConnection() {
  pendingConnection.value = null;
  store.connectionMode = "idle";
  window.removeEventListener("pointermove", moveConnection);
  window.removeEventListener("pointerup", cancelConnection);
}

function cancelConnection() {
  clearPendingConnection();
}

function startDrag(nodeId: string, event: PointerEvent) {
  if (event.button === 1 || isSpacePressed.value) {
    startViewportPan(event);
    return;
  }

  if (event.ctrlKey || event.metaKey) {
    return;
  }

  const node = store.nodes.find((item) => item.nodeId === nodeId);

  if (!node) {
    return;
  }

  const worldPoint = screenToWorld(event);
  event.preventDefault();
  if (!store.selectedNodeIds.includes(nodeId)) {
    store.selectNode(nodeId);
  }
  store.commitHistory();
  const movingIds = store.selectedNodeIds.includes(nodeId) ? store.selectedNodeIds : [nodeId];
  const nodeOrigins = Object.fromEntries(
    store.nodes
      .filter((item) => movingIds.includes(item.nodeId))
      .map((item) => [item.nodeId, { ...item.position }]),
  );

  draggingNode.value = {
    nodeId,
    startX: worldPoint.x,
    startY: worldPoint.y,
    nodeOrigins,
  };
  window.addEventListener("pointermove", moveDrag);
  window.addEventListener("pointerup", stopDrag);
}

function moveDrag(event: PointerEvent) {
  if (!draggingNode.value) {
    return;
  }

  const worldPoint = screenToWorld(event);
  const deltaX = worldPoint.x - draggingNode.value.startX;
  const deltaY = worldPoint.y - draggingNode.value.startY;

  Object.entries(draggingNode.value.nodeOrigins).forEach(([nodeId, origin]) => {
    store.moveNodePosition(nodeId, {
      x: origin.x + deltaX,
      y: origin.y + deltaY,
    });
  });
}

function handleNodeSelect(nodeId: string, event: MouseEvent) {
  if (event.ctrlKey || event.metaKey) {
    store.toggleNodeSelection(nodeId);
    return;
  }

  store.selectNode(nodeId);
}

function activeInputFields(nodeId: string) {
  return activePortFieldsByNode.value.inputs.get(nodeId) || [];
}

function activeOutputFields(nodeId: string) {
  return activePortFieldsByNode.value.outputs.get(nodeId) || [];
}

function minimapPoint(event: Pick<PointerEvent, "clientX" | "clientY">) {
  const rect = minimapRef.value?.getBoundingClientRect();

  if (!rect) {
    return { x: 0, y: 0 };
  }

  return {
    x: Math.max(0, Math.min(MINIMAP_WIDTH, event.clientX - rect.left)),
    y: Math.max(0, Math.min(MINIMAP_HEIGHT, event.clientY - rect.top)),
  };
}

function focusMinimapPoint(event: PointerEvent) {
  const point = minimapPoint(event);
  const worldX = point.x / minimapScale.value;
  const worldY = point.y / minimapScale.value;

  store.setViewport({
    x: canvasSize.value.width / 2 - worldX * store.viewport.scale,
    y: canvasSize.value.height / 2 - worldY * store.viewport.scale,
  });
}

function startMinimapDrag(event: PointerEvent) {
  event.preventDefault();
  minimapDragging.value = true;
  focusMinimapPoint(event);
  window.addEventListener("pointermove", moveMinimapDrag);
  window.addEventListener("pointerup", stopMinimapDrag);
}

function moveMinimapDrag(event: PointerEvent) {
  if (!minimapDragging.value) {
    return;
  }

  focusMinimapPoint(event);
}

function stopMinimapDrag() {
  minimapDragging.value = false;
  window.removeEventListener("pointermove", moveMinimapDrag);
  window.removeEventListener("pointerup", stopMinimapDrag);
}

function stopDrag() {
  draggingNode.value = null;
  window.removeEventListener("pointermove", moveDrag);
  window.removeEventListener("pointerup", stopDrag);
}

function isEditableTarget(target: EventTarget | null) {
  return target instanceof HTMLElement && Boolean(target.closest("input, textarea, [contenteditable='true']"));
}

function handleKeydown(event: KeyboardEvent) {
  if (event.code === "Space" && !isEditableTarget(event.target)) {
    isSpacePressed.value = true;
    event.preventDefault();
  }

  if ((event.key === "Delete" || event.key === "Backspace") && !isEditableTarget(event.target)) {
    event.preventDefault();
    if (store.selectedConnectionId) {
      store.deleteSelectedConnection();
    } else if (store.selectedNodeIds.length) {
      store.deleteSelectedNodes();
    }
  }

  if (event.key === "Escape") {
    clearPendingConnection();
    store.clearSelection();
    store.clearConnectionSelection();
  }
}

function handleKeyup(event: KeyboardEvent) {
  if (event.code === "Space") {
    isSpacePressed.value = false;
  }
}

onMounted(() => {
  updateCanvasSize();
  if (canvasRef.value) {
    resizeObserver = new ResizeObserver(updateCanvasSize);
    resizeObserver.observe(canvasRef.value);
  }
  window.addEventListener("keydown", handleKeydown);
  window.addEventListener("keyup", handleKeyup);
});

onBeforeUnmount(() => {
  stopDrag();
  stopViewportPan();
  stopMinimapDrag();
  clearPendingConnection();
  resizeObserver?.disconnect();
  window.removeEventListener("keydown", handleKeydown);
  window.removeEventListener("keyup", handleKeyup);
});
</script>

<template>
  <section
    ref="canvasRef"
    class="workflow-canvas"
    :class="{ panning: isPanning, 'space-mode': isSpacePressed }"
    :style="canvasStyle"
    @click="handleCanvasClick"
    @contextmenu.prevent
    @dragover.prevent
    @drop.prevent="handleDrop"
    @pointerdown="handleCanvasPointerDown"
    @wheel="handleWheel"
  >
    <div v-if="!canvasNodes.length" class="canvas-empty">
      <strong>拖入 Agent 节点开始编排</strong>
      <span>滚轮缩放，按住空格拖拽或中键拖拽移动画布。</span>
    </div>

    <div class="workflow-world" :style="worldStyle">
      <div
        v-for="lane in visibleStageLanes"
        :key="lane.key"
        class="stage-lane"
        :class="{ active: lane.active }"
        :style="{ left: `${lane.x}px` }"
      >
        <div class="stage-lane-label">
          <span class="stage-index">{{ lane.index + 1 }}</span>
          <strong>{{ lane.label }}</strong>
          <em>{{ lane.nodeCount ? `${lane.nodeCount} node${lane.nodeCount > 1 ? "s" : ""}` : "待配置" }}</em>
        </div>
      </div>

      <svg class="connection-layer" :width="WORLD_WIDTH" :height="WORLD_HEIGHT">
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 14 12"
            markerWidth="13"
            markerHeight="11"
            refX="12"
            refY="5.5"
            orient="auto"
            markerUnits="userSpaceOnUse"
            overflow="visible"
          >
            <path d="M1,1.4 L10.5,5.5 L1,9.6 L4.2,5.5 Z" fill="context-stroke" />
          </marker>
          <marker
            id="arrow-selected"
            viewBox="0 0 15 13"
            markerWidth="14"
            markerHeight="12"
            refX="13"
            refY="6"
            orient="auto"
            markerUnits="userSpaceOnUse"
            overflow="visible"
          >
            <path d="M1.2,1.4 L13,6 L1.2,10.6 L5.2,6 Z" fill="context-stroke" />
          </marker>
          <marker
            id="arrow-pending"
            viewBox="0 0 15 13"
            markerWidth="14"
            markerHeight="12"
            refX="13"
            refY="6"
            orient="auto"
            markerUnits="userSpaceOnUse"
            overflow="visible"
          >
            <path d="M1.2,1.4 L13,6 L1.2,10.6 L5.2,6 Z" fill="context-stroke" />
          </marker>
          <filter id="connection-glow" x="-30%" y="-30%" width="160%" height="160%">
            <feDropShadow dx="0" dy="3" flood-color="#1a73e8" flood-opacity="0.28" stdDeviation="4" />
          </filter>
        </defs>
        <g
          v-for="connection in renderedConnections"
          :key="connection.renderKey"
          :style="{ '--edge-color': connection.color }"
          @click.stop="store.selectConnection(connection.key)"
          @mouseenter="hoveredConnectionKey = connection.key"
          @mouseleave="hoveredConnectionKey = ''"
          @pointerdown.stop
        >
          <title>{{ connection.label }}</title>
          <path
            class="connection-hit-path"
            :d="connection.path"
            fill="none"
            stroke="rgba(37, 99, 235, 0.001)"
            stroke-width="18"
          />
          <path class="connection-bg-path" :d="connection.path" fill="none" />
          <path
            class="connection-path"
            :class="{ selected: connection.selected }"
            :d="connection.path"
            fill="none"
            :filter="connection.selected ? 'url(#connection-glow)' : undefined"
            :marker-end="connection.selected ? 'url(#arrow-selected)' : 'url(#arrow)'"
            :stroke="connection.selected ? '#1a73e8' : connection.color"
            :stroke-width="connection.selected ? 3 : 2"
          />
          <text
            v-if="connection.selected"
            class="connection-label"
            :x="connection.labelX"
            :y="connection.labelY"
          >
            {{ connection.fromOutputField || "output" }} → {{ connection.toInputField || "input" }}
            <tspan v-if="connection.edgeType === 'branch' && connection.condition" dx="8">
              if {{ connection.condition }}
            </tspan>
            <tspan v-else-if="connection.edgeType === 'loop'" dx="8">
              loop max {{ connection.maxIterations || "?" }}
            </tspan>
          </text>
        </g>
        <path v-if="pendingConnectionPath" class="connection-bg-path pending-bg" :d="pendingConnectionPath" fill="none" />
        <path
          v-if="pendingConnectionPath"
          class="connection-path pending"
          :d="pendingConnectionPath"
          fill="none"
          marker-end="url(#arrow-pending)"
          :style="{ '--pending-edge-color': pendingConnectionColor }"
        />
      </svg>

      <AgentNode
        v-for="(node, index) in canvasNodes"
        :key="node.nodeId"
        :node="node"
        :index="index"
        :total="canvasNodes.length"
        :selected="store.selectedNodeIds.includes(node.nodeId)"
        :show-handles="showHandles"
        :active-input-fields="activeInputFields(node.nodeId)"
        :active-output-fields="activeOutputFields(node.nodeId)"
        @select="handleNodeSelect"
        @delete="store.deleteNode"
        @finish-connection="finishConnection"
        @start-drag="startDrag"
        @start-connection="startConnection"
        @move-up="store.moveNodeOrder($event, -1)"
        @move-down="store.moveNodeOrder($event, 1)"
      />
    </div>

    <div v-if="selectionBox" class="selection-box" :style="selectionBoxStyle" />

    <div
      v-if="shouldRenderMinimap"
      ref="minimapRef"
      class="canvas-minimap"
      @click.stop
      @pointerdown.stop="startMinimapDrag"
    >
      <div class="minimap-title">
        <span>Minimap</span>
        <strong>{{ store.nodes.length }} nodes</strong>
      </div>
      <div class="minimap-stage">
        <svg class="minimap-connections" :width="MINIMAP_WIDTH" :height="MINIMAP_HEIGHT">
          <path
            v-for="connection in renderedConnections"
            :key="`minimap-${connection.renderKey}`"
            :class="{ selected: connection.selected }"
            :d="connection.minimapPath"
            fill="none"
          />
        </svg>
        <span
          v-for="node in minimapNodes"
          :key="node.nodeId"
          class="minimap-node"
          :class="{ selected: node.selected, branch: node.stage === 'branch' || node.agentKey.startsWith('branch_') }"
          :style="node.style"
        />
        <span class="minimap-viewport" :style="minimapViewportStyle" />
      </div>
    </div>

    <div v-if="selectedCount > 1" class="selection-toolbar" @click.stop @pointerdown.stop>
      <strong>{{ selectedCount }} 个节点已选中</strong>
      <el-button size="small" :icon="Refresh" @click="autoLayoutSelected">整理选中</el-button>
      <el-button size="small" :icon="Delete" type="danger" plain @click="deleteSelected">删除选中</el-button>
      <el-button size="small" text @click="store.clearSelection">取消</el-button>
    </div>

    <div v-if="selectedConnection" class="connection-toolbar" @click.stop @pointerdown.stop>
      <strong>
        连接已选中
        <em v-if="selectedConnectionData?.edgeType">· {{ selectedConnectionData.edgeType }}</em>
      </strong>
      <el-button size="small" plain @click="markSelectedConnection('control')">控制边</el-button>
      <el-button size="small" plain @click="markSelectedConnection('branch')">分支边</el-button>
      <el-button size="small" plain @click="markSelectedConnection('loop')">循环边</el-button>
      <el-button size="small" :icon="Delete" type="danger" plain @click="store.deleteSelectedConnection">
        删除连接
      </el-button>
      <el-button size="small" text @click="store.clearConnectionSelection">取消</el-button>
    </div>

    <div class="canvas-controls" @click.stop @pointerdown.stop>
      <el-tooltip content="缩小" placement="top">
        <el-button :icon="Minus" size="small" circle @click="zoomBy(-0.1)" />
      </el-tooltip>
      <span class="zoom-value">{{ zoomPercent }}</span>
      <el-tooltip content="放大" placement="top">
        <el-button :icon="Plus" size="small" circle @click="zoomBy(0.1)" />
      </el-tooltip>
      <el-tooltip content="重置视角" placement="top">
        <el-button :icon="Refresh" size="small" circle @click="resetViewport" />
      </el-tooltip>
      <el-button size="small" :disabled="!store.nodes.length" @click="autoLayout">自动整理</el-button>
      <el-button size="small" :disabled="store.nodes.length < 2" @click="rebuildSequentialConnections">
        自动顺序连线
      </el-button>
      <el-button size="small" :disabled="store.nodes.length <= 8" @click="showMinimap = !showMinimap">
        {{ showMinimap ? "隐藏小地图" : "显示小地图" }}
      </el-button>
    </div>

    <div class="canvas-hint">
      输出点拖到输入点连线 · Del 删除选中 · Space / middle drag 平移 · Wheel 缩放 · Esc 取消
    </div>
  </section>
</template>

<style scoped>
.workflow-canvas {
  position: relative;
  height: 100%;
  min-height: 640px;
  overflow: hidden;
  border: 1px solid #343741;
  border-radius: 12px;
  background:
    linear-gradient(rgba(148, 163, 184, 0.12) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.12) 1px, transparent 1px),
    #101218;
  background-position: var(--grid-x) var(--grid-y);
  background-size: var(--grid-size) var(--grid-size);
  cursor: default;
  user-select: none;
}

.workflow-canvas.space-mode,
.workflow-canvas.panning {
  cursor: grab;
}

.workflow-canvas.panning {
  cursor: grabbing;
}

.workflow-world {
  position: absolute;
  top: 0;
  left: 0;
  transform-origin: 0 0;
}

.stage-lane {
  position: absolute;
  top: 96px;
  z-index: 0;
  width: 416px;
  height: 0;
  border-top: 1px solid rgba(148, 163, 184, 0.18);
  opacity: 0.56;
  pointer-events: none;
  transition:
    opacity 160ms ease,
    border-color 160ms ease;
}

.stage-lane.active {
  border-color: rgba(77, 163, 255, 0.34);
  opacity: 1;
}

.stage-lane-label {
  position: absolute;
  top: -36px;
  left: 0;
  display: inline-flex;
  max-width: 304px;
  align-items: center;
  gap: 7px;
  padding: 7px 10px 7px 8px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 12px;
  background: rgba(23, 25, 31, 0.9);
  color: #a1a1aa;
  font-size: 12px;
  letter-spacing: 0;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(8px);
}

.stage-lane.active .stage-lane-label {
  border-color: rgba(77, 163, 255, 0.24);
  background:
    radial-gradient(circle at 100% 0%, rgba(77, 163, 255, 0.16), transparent 44%),
    rgba(23, 25, 31, 0.94);
  box-shadow: 0 10px 24px rgba(77, 163, 255, 0.12);
}

.stage-index {
  display: grid;
  width: 20px;
  height: 20px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 50%;
  background: rgba(148, 163, 184, 0.16);
  color: #cbd5e1;
  font-size: 11px;
  font-weight: 900;
}

.stage-lane.active .stage-index {
  background: #4da3ff;
  color: #06121f;
}

.stage-lane-label strong {
  color: #f4f4f5;
  font-size: 12px;
  font-weight: 850;
  white-space: nowrap;
}

.stage-lane-label em {
  overflow: hidden;
  color: #a1a1aa;
  font-size: 11px;
  font-style: normal;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.canvas-empty {
  position: absolute;
  inset: 18px;
  z-index: 1;
  display: grid;
  place-content: center;
  gap: 8px;
  border: 1px dashed rgba(148, 163, 184, 0.34);
  border-radius: 10px;
  color: #a1a1aa;
  text-align: center;
  pointer-events: none;
}

.canvas-empty strong {
  color: #f4f4f5;
  font-size: 16px;
}

.connection-layer {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: auto;
}

.connection-path {
  stroke: var(--edge-color, #64748b);
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
  pointer-events: none;
  transition:
    stroke 0.16s ease,
    stroke-width 0.16s ease,
    filter 0.16s ease,
    opacity 0.16s ease;
}

.connection-bg-path {
  stroke: rgba(15, 23, 42, 0.04);
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 4;
  pointer-events: none;
}

.connection-bg-path.pending-bg {
  stroke-width: 5;
}

g:hover .connection-path {
  stroke: #1a73e8;
  stroke-width: 3;
  filter: url(#connection-glow);
}

.connection-hit-path {
  stroke-linecap: round;
  pointer-events: all;
  cursor: pointer;
}

.connection-path.selected {
  stroke: #1a73e8;
  stroke-width: 3;
  filter: url(#connection-glow);
}

.connection-path.pending {
  animation: pending-flow 0.9s linear infinite;
  stroke: var(--pending-edge-color, #1a73e8);
  stroke-dasharray: 14 10;
  stroke-width: 3;
  pointer-events: none;
  filter: url(#connection-glow);
}

.connection-label {
  paint-order: stroke;
  stroke: rgba(15, 17, 21, 0.92);
  stroke-width: 4px;
  fill: #1a73e8;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  font-weight: 850;
  pointer-events: none;
}

@keyframes pending-flow {
  from {
    stroke-dashoffset: 21;
  }

  to {
    stroke-dashoffset: 0;
  }
}

.selection-box {
  position: absolute;
  z-index: 9;
  border: 1px solid #2563eb;
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.1);
  box-shadow: inset 0 0 0 1px rgba(77, 163, 255, 0.24);
  pointer-events: none;
}

.canvas-minimap {
  position: absolute;
  right: 14px;
  bottom: 66px;
  z-index: 6;
  width: 196px;
  padding: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  background: rgba(23, 25, 31, 0.92);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22);
  cursor: crosshair;
  backdrop-filter: blur(12px);
}

.minimap-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
  color: #a1a1aa;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.minimap-title strong {
  color: #8ab4f8;
  text-transform: none;
}

.minimap-stage {
  position: relative;
  width: 176px;
  height: 120px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  background:
    linear-gradient(rgba(148, 163, 184, 0.12) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.12) 1px, transparent 1px),
    #101218;
  background-size: 12px 12px;
}

.minimap-connections {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

.minimap-connections path {
  stroke: #b6c2d2;
  stroke-linecap: round;
  stroke-width: 1.1;
}

.minimap-connections path.selected {
  stroke: #1a73e8;
  stroke-width: 2.6;
}

.minimap-node {
  position: absolute;
  z-index: 2;
  border: 1px solid #93c5fd;
  border-radius: 3px;
  background: #bfdbfe;
}

.minimap-node.branch {
  border-color: #f59e0b;
  background: #fde68a;
}

.minimap-node.selected {
  border-color: #2563eb;
  background: #60a5fa;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.24);
}

.minimap-viewport {
  position: absolute;
  z-index: 3;
  border: 2px solid #1d4ed8;
  border-radius: 4px;
  background: rgba(29, 78, 216, 0.08);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.78);
}

.selection-toolbar {
  position: absolute;
  top: 16px;
  left: 50%;
  z-index: 11;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border: 1px solid rgba(77, 163, 255, 0.24);
  border-radius: 999px;
  background: rgba(23, 25, 31, 0.94);
  box-shadow: 0 16px 38px rgba(0, 0, 0, 0.22);
  transform: translateX(-50%);
  backdrop-filter: blur(12px);
}

.connection-toolbar {
  position: absolute;
  top: 16px;
  left: 50%;
  z-index: 11;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border: 1px solid rgba(77, 163, 255, 0.24);
  border-radius: 999px;
  background: rgba(23, 25, 31, 0.94);
  box-shadow: 0 16px 38px rgba(0, 0, 0, 0.22);
  transform: translateX(-50%);
  backdrop-filter: blur(12px);
}

.connection-toolbar strong {
  color: #8ab4f8;
  font-size: 12px;
}

.selection-toolbar strong {
  color: #8ab4f8;
  font-size: 12px;
}

.canvas-controls {
  position: absolute;
  right: 16px;
  bottom: 16px;
  z-index: 7;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  background: rgba(23, 25, 31, 0.92);
  box-shadow: 0 14px 36px rgba(0, 0, 0, 0.22);
  backdrop-filter: blur(10px);
}

.zoom-value {
  min-width: 48px;
  color: #d4d4d8;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  font-weight: 800;
  text-align: center;
}

.canvas-hint {
  position: absolute;
  left: 18px;
  bottom: 18px;
  z-index: 7;
  padding: 7px 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  background: rgba(23, 25, 31, 0.86);
  color: #a1a1aa;
  font-size: 12px;
  backdrop-filter: blur(8px);
}
</style>
