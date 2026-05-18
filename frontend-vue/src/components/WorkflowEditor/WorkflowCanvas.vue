<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from "vue";

import AgentNode from "./AgentNode.vue";
import { useWorkflowEditorStore } from "./WorkflowEditorStore";

import type { AgentMeta } from "@/types/agent";

const props = defineProps<{
  agents: AgentMeta[];
}>();

const store = useWorkflowEditorStore();
const canvasRef = ref<HTMLElement | null>(null);
const dragging = ref<{
  nodeId: string;
  offsetX: number;
  offsetY: number;
} | null>(null);

const canvasNodes = computed(() => store.orderedNodes);

function nodeCenter(nodeId: string) {
  const node = store.nodes.find((item) => item.nodeId === nodeId);

  if (!node) {
    return { x: 0, y: 0 };
  }

  return {
    x: node.position.x + 115,
    y: node.position.y + 78,
  };
}

function handleDrop(event: DragEvent) {
  const agentKey = event.dataTransfer?.getData("application/x-agent-key");

  if (!agentKey || !canvasRef.value) {
    return;
  }

  const agent = props.agents.find((item) => item.key === agentKey);

  if (!agent) {
    return;
  }

  const rect = canvasRef.value.getBoundingClientRect();
  store.addAgentNode(agent, {
    x: Math.max(16, event.clientX - rect.left - 115),
    y: Math.max(16, event.clientY - rect.top - 48),
  });
}

function startDrag(nodeId: string, event: PointerEvent) {
  const node = store.nodes.find((item) => item.nodeId === nodeId);

  if (!node || !canvasRef.value) {
    return;
  }

  const rect = canvasRef.value.getBoundingClientRect();
  store.selectNode(nodeId);
  store.commitHistory();
  dragging.value = {
    nodeId,
    offsetX: event.clientX - rect.left - node.position.x,
    offsetY: event.clientY - rect.top - node.position.y,
  };
  window.addEventListener("pointermove", moveDrag);
  window.addEventListener("pointerup", stopDrag);
}

function moveDrag(event: PointerEvent) {
  if (!dragging.value || !canvasRef.value) {
    return;
  }

  const rect = canvasRef.value.getBoundingClientRect();
  store.moveNodePosition(dragging.value.nodeId, {
    x: event.clientX - rect.left - dragging.value.offsetX,
    y: event.clientY - rect.top - dragging.value.offsetY,
  });
}

function stopDrag() {
  dragging.value = null;
  window.removeEventListener("pointermove", moveDrag);
  window.removeEventListener("pointerup", stopDrag);
}

onBeforeUnmount(stopDrag);
</script>

<template>
  <section
    ref="canvasRef"
    class="workflow-canvas"
    @dragover.prevent
    @drop.prevent="handleDrop"
    @click="store.selectNode('')"
  >
    <div v-if="!canvasNodes.length" class="canvas-empty">
      <strong>拖入 Agent 节点开始编排</strong>
      <span>从左侧 Agent Palette 拖动节点到画布，也可以通过工具栏加载已有模板。</span>
    </div>

    <svg class="connection-layer" :width="'100%'" :height="'100%'">
      <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="#64748b" />
        </marker>
      </defs>
      <line
        v-for="connection in store.connections"
        :key="`${connection.fromNodeId}-${connection.toNodeId}`"
        :x1="nodeCenter(connection.fromNodeId).x"
        :y1="nodeCenter(connection.fromNodeId).y"
        :x2="nodeCenter(connection.toNodeId).x"
        :y2="nodeCenter(connection.toNodeId).y"
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
      :selected="store.selectedNodeId === node.nodeId"
      @select="store.selectNode"
      @delete="store.deleteNode"
      @start-drag="startDrag"
      @move-up="store.moveNodeOrder($event, -1)"
      @move-down="store.moveNodeOrder($event, 1)"
    />
  </section>
</template>

<style scoped>
.workflow-canvas {
  position: relative;
  min-height: 650px;
  overflow: auto;
  border: 1px solid #dbe4ef;
  border-radius: 8px;
  background:
    linear-gradient(#eef2f7 1px, transparent 1px),
    linear-gradient(90deg, #eef2f7 1px, transparent 1px),
    #ffffff;
  background-size: 24px 24px;
}

.canvas-empty {
  position: absolute;
  inset: 18px;
  display: grid;
  place-content: center;
  gap: 8px;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  color: #64748b;
  text-align: center;
}

.canvas-empty strong {
  color: #334155;
  font-size: 16px;
}

.connection-layer {
  position: absolute;
  inset: 0;
  min-width: 1000px;
  min-height: 650px;
  pointer-events: none;
}
</style>
