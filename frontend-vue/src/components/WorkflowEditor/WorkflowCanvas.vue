<script setup lang="ts">
import { Delete, Minus, Plus, Refresh } from "@element-plus/icons-vue";
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import AgentNode from "./AgentNode.vue";
import { useWorkflowEditorStore } from "./WorkflowEditorStore";

import type { AgentMeta } from "@/types/agent";
import type { WorkflowSelectionBox } from "@/types/workflowEditor";

const props = defineProps<{
  agents: AgentMeta[];
}>();

const WORLD_WIDTH = 6000;
const WORLD_HEIGHT = 4200;
const GRID_SIZE = 24;
const NODE_WIDTH = 256;
const NODE_HEIGHT = 154;
const MINIMAP_WIDTH = 210;
const MINIMAP_HEIGHT = 148;

const store = useWorkflowEditorStore();
const canvasRef = ref<HTMLElement | null>(null);
const minimapRef = ref<HTMLElement | null>(null);
const isSpacePressed = ref(false);
const isPanning = ref(false);
const ignoreNextClick = ref(false);
const selectionBox = ref<WorkflowSelectionBox | null>(null);
const canvasSize = ref({ width: 0, height: 0 });
const minimapDragging = ref(false);
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
const canvasStyle = computed(() => ({
  "--grid-size": `${GRID_SIZE * store.viewport.scale}px`,
  "--grid-x": `${store.viewport.x}px`,
  "--grid-y": `${store.viewport.y}px`,
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

function nodePorts(connection: { fromNodeId: string; toNodeId: string }) {
  const fromNode = store.nodes.find((item) => item.nodeId === connection.fromNodeId);
  const toNode = store.nodes.find((item) => item.nodeId === connection.toNodeId);

  if (!fromNode || !toNode) {
    return {
      start: { x: 0, y: 0 },
      end: { x: 0, y: 0 },
    };
  }

  const fromRight = fromNode.position.x <= toNode.position.x;
  const verticalGap = Math.abs(fromNode.position.x - toNode.position.x) < 80;

  if (verticalGap) {
    return {
      start: { x: fromNode.position.x + 115, y: fromNode.position.y + 150 },
      end: { x: toNode.position.x + 115, y: toNode.position.y },
    };
  }

  return {
    start: {
      x: fromNode.position.x + (fromRight ? 232 : 0),
      y: fromNode.position.y + 74,
    },
    end: {
      x: toNode.position.x + (fromRight ? 0 : 232),
      y: toNode.position.y + 74,
    },
  };
}

function connectionPath(connection: { fromNodeId: string; toNodeId: string }) {
  const { start, end } = nodePorts(connection);
  const dx = Math.max(80, Math.abs(end.x - start.x) * 0.45);
  const direction = end.x >= start.x ? 1 : -1;

  if (Math.abs(end.x - start.x) < 80) {
    const midY = start.y + (end.y - start.y) * 0.5;
    return `M ${start.x} ${start.y} C ${start.x} ${midY}, ${end.x} ${midY}, ${end.x} ${end.y}`;
  }

  return `M ${start.x} ${start.y} C ${start.x + dx * direction} ${start.y}, ${end.x - dx * direction} ${end.y}, ${end.x} ${end.y}`;
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
  store.deleteSelectedNodes();
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
}

function startSelectionBox(event: PointerEvent) {
  const point = canvasPoint(event);

  event.preventDefault();
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

  if (event.key === "Escape") {
    store.clearSelection();
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
      <svg class="connection-layer" :width="WORLD_WIDTH" :height="WORLD_HEIGHT">
        <defs>
          <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#64748b" />
          </marker>
        </defs>
        <path
          v-for="connection in store.connections"
          :key="`${connection.fromNodeId}-${connection.toNodeId}`"
          :d="connectionPath(connection)"
          fill="none"
          stroke="#64748b"
          stroke-width="2"
          marker-end="url(#arrow)"
        />
      </svg>

      <AgentNode
        v-for="(node, index) in canvasNodes"
        :key="node.nodeId"
        :node="node"
        :index="index"
        :total="canvasNodes.length"
        :selected="store.selectedNodeIds.includes(node.nodeId)"
        @select="handleNodeSelect"
        @delete="store.deleteNode"
        @start-drag="startDrag"
        @move-up="store.moveNodeOrder($event, -1)"
        @move-down="store.moveNodeOrder($event, 1)"
      />
    </div>

    <div v-if="selectionBox" class="selection-box" :style="selectionBoxStyle" />

    <div
      v-if="store.nodes.length"
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
    </div>

    <div class="canvas-hint">Space + drag / middle drag 平移 · Wheel 缩放 · Esc 关闭属性</div>
  </section>
</template>

<style scoped>
.workflow-canvas {
  position: relative;
  height: 100%;
  min-height: 680px;
  overflow: hidden;
  border: 1px solid #dbe4ef;
  border-radius: 12px;
  background:
    linear-gradient(#e8eef7 1px, transparent 1px),
    linear-gradient(90deg, #e8eef7 1px, transparent 1px),
    #ffffff;
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

.canvas-empty {
  position: absolute;
  inset: 18px;
  z-index: 1;
  display: grid;
  place-content: center;
  gap: 8px;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  color: #64748b;
  text-align: center;
  pointer-events: none;
}

.canvas-empty strong {
  color: #334155;
  font-size: 16px;
}

.connection-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.selection-box {
  position: absolute;
  z-index: 9;
  border: 1px solid #2563eb;
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.1);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.65);
  pointer-events: none;
}

.canvas-minimap {
  position: absolute;
  right: 16px;
  bottom: 74px;
  z-index: 8;
  width: 234px;
  padding: 10px;
  border: 1px solid #dbe4ef;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 16px 42px rgba(15, 23, 42, 0.16);
  cursor: crosshair;
  backdrop-filter: blur(12px);
}

.minimap-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
  color: #64748b;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.minimap-title strong {
  color: #1d4ed8;
  text-transform: none;
}

.minimap-stage {
  position: relative;
  width: 210px;
  height: 148px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background:
    linear-gradient(#eff6ff 1px, transparent 1px),
    linear-gradient(90deg, #eff6ff 1px, transparent 1px),
    #f8fafc;
  background-size: 12px 12px;
}

.minimap-node {
  position: absolute;
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
  border: 1px solid #bfdbfe;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 16px 38px rgba(30, 64, 175, 0.16);
  transform: translateX(-50%);
  backdrop-filter: blur(12px);
}

.selection-toolbar strong {
  color: #1e40af;
  font-size: 12px;
}

.canvas-controls {
  position: absolute;
  right: 16px;
  bottom: 16px;
  z-index: 8;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border: 1px solid #dbe4ef;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.12);
  backdrop-filter: blur(10px);
}

.zoom-value {
  min-width: 48px;
  color: #334155;
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
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: rgba(248, 250, 252, 0.88);
  color: #64748b;
  font-size: 12px;
  backdrop-filter: blur(8px);
}
</style>
