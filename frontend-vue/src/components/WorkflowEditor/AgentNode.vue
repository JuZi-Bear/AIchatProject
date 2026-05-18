<script setup lang="ts">
import { Bottom, Delete, Top } from "@element-plus/icons-vue";

import type { AgentNodeData } from "@/types/workflowEditor";

defineProps<{
  node: AgentNodeData;
  index: number;
  total: number;
  selected: boolean;
}>();

const emit = defineEmits<{
  select: [nodeId: string];
  delete: [nodeId: string];
  startDrag: [nodeId: string, event: PointerEvent];
  moveUp: [nodeId: string];
  moveDown: [nodeId: string];
}>();
</script>

<template>
  <article
    class="agent-node"
    :class="{ selected, disabled: !node.enabled }"
    :style="{ left: `${node.position.x}px`, top: `${node.position.y}px` }"
    @pointerdown.stop="emit('startDrag', node.nodeId, $event)"
    @click.stop="emit('select', node.nodeId)"
  >
    <div class="node-header">
      <div class="node-order">{{ index + 1 }}</div>
      <div class="node-title">
        <strong>{{ node.name }}</strong>
        <span>{{ node.agentKey }}</span>
      </div>
      <el-tag :type="node.enabled ? 'success' : 'info'" effect="plain" size="small">
        {{ node.enabled ? "启用" : "禁用" }}
      </el-tag>
    </div>

    <p>{{ node.description || "暂无节点说明" }}</p>

    <div class="node-tags">
      <el-tag type="primary" effect="plain" size="small">{{ node.stage || "stage" }}</el-tag>
      <el-tag effect="plain" size="small">in {{ node.input_fields.length }}</el-tag>
      <el-tag type="success" effect="plain" size="small">out {{ node.output_fields.length }}</el-tag>
    </div>

    <div class="node-actions" @pointerdown.stop @click.stop>
      <el-tooltip content="提前执行" placement="bottom">
        <el-button :icon="Top" size="small" circle :disabled="index === 0" @click="emit('moveUp', node.nodeId)" />
      </el-tooltip>
      <el-tooltip content="延后执行" placement="bottom">
        <el-button
          :icon="Bottom"
          size="small"
          circle
          :disabled="index === total - 1"
          @click="emit('moveDown', node.nodeId)"
        />
      </el-tooltip>
      <el-tooltip content="删除节点" placement="bottom">
        <el-button :icon="Delete" size="small" circle type="danger" @click="emit('delete', node.nodeId)" />
      </el-tooltip>
    </div>
  </article>
</template>

<style scoped>
.agent-node {
  position: absolute;
  z-index: 2;
  display: grid;
  width: 230px;
  gap: 9px;
  padding: 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  cursor: grab;
  user-select: none;
}

.agent-node:active {
  cursor: grabbing;
}

.agent-node.selected {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.16), 0 10px 24px rgba(15, 23, 42, 0.08);
}

.agent-node.disabled {
  background: #f8fafc;
  opacity: 0.72;
}

.node-header,
.node-tags,
.node-actions {
  display: flex;
  align-items: center;
}

.node-header {
  gap: 9px;
}

.node-order {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 50%;
  background: #dbeafe;
  color: #1e40af;
  font-weight: 800;
}

.node-title {
  min-width: 0;
  flex: 1;
}

.node-title strong,
.node-title span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-title strong {
  color: #0f172a;
}

.node-title span {
  margin-top: 2px;
  color: #64748b;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.agent-node p {
  min-height: 36px;
  margin: 0;
  overflow: hidden;
  color: #475569;
  display: -webkit-box;
  font-size: 12px;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.node-tags {
  flex-wrap: wrap;
  gap: 5px;
}

.node-actions {
  justify-content: flex-end;
  gap: 6px;
}
</style>
