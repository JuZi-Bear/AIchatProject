<script setup lang="ts">
import { Bottom, Delete, Top } from "@element-plus/icons-vue";

import type { AgentNodeData } from "@/types/workflowEditor";

defineProps<{
  node: AgentNodeData;
  index: number;
  total: number;
  selected: boolean;
  showHandles?: boolean;
}>();

const emit = defineEmits<{
  select: [nodeId: string, event: MouseEvent];
  delete: [nodeId: string];
  startDrag: [nodeId: string, event: PointerEvent];
  startConnection: [nodeId: string, event: PointerEvent];
  finishConnection: [nodeId: string, event: PointerEvent];
  moveUp: [nodeId: string];
  moveDown: [nodeId: string];
}>();
</script>

<template>
  <article
    class="agent-node"
    :class="{
      selected,
      disabled: !node.enabled,
      branch: node.stage === 'branch' || node.agentKey.startsWith('branch_'),
      code: node.agentKey === 'code_agent',
      approval: node.agentKey === 'human_approval',
      custom: node.agentKey === 'custom_agent',
      'show-handles': showHandles,
    }"
    :style="{ left: `${node.position.x}px`, top: `${node.position.y}px` }"
    @pointerdown.stop="emit('startDrag', node.nodeId, $event)"
    @click.stop="emit('select', node.nodeId, $event)"
  >
    <button
      class="node-port input-port"
      aria-label="输入连接点"
      title="输入连接点"
      type="button"
      @pointerdown.stop
      @pointerup.stop="emit('finishConnection', node.nodeId, $event)"
      @click.stop
    />
    <button
      class="node-port output-port"
      aria-label="输出连接点"
      title="从这里拖出连接"
      type="button"
      @pointerdown.stop="emit('startConnection', node.nodeId, $event)"
      @click.stop
    />

    <div class="node-header">
      <div class="node-order"><span>{{ index + 1 }}</span></div>
      <div class="node-title">
        <strong>{{ node.name }}</strong>
        <span>{{ node.stage || node.agentKey }}</span>
      </div>
      <el-tag
        :type="
          node.stage === 'branch' || node.agentKey.startsWith('branch_')
            ? 'warning'
            : node.agentKey === 'human_approval'
              ? 'primary'
              : node.enabled
                ? 'success'
                : 'info'
        "
        effect="plain"
        size="small"
      >
        {{ node.enabled ? "启用" : "禁用" }}
      </el-tag>
    </div>

    <p>{{ node.description || "暂无节点说明" }}</p>

    <div class="node-tags">
      <el-tag effect="plain" size="small">in {{ node.input_fields.length }}</el-tag>
      <el-tag type="success" effect="plain" size="small">out {{ node.output_fields.length }}</el-tag>
      <el-tag v-if="node.agentKey === 'code_agent'" type="primary" effect="plain" size="small">file ops</el-tag>
      <el-tag v-if="node.agentKey === 'human_approval'" type="primary" effect="plain" size="small">ask human</el-tag>
      <el-tag v-if="node.agentKey === 'custom_agent'" type="info" effect="plain" size="small">custom</el-tag>
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
  box-sizing: border-box;
  width: 256px;
  gap: 8px;
  padding: 14px;
  border: 1px solid #dadce0;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 10px 24px rgba(60, 64, 67, 0.08);
  cursor: grab;
  user-select: none;
}

.agent-node:active {
  cursor: grabbing;
}

.agent-node.selected {
  border-color: #1a73e8;
  box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.14), 0 14px 30px rgba(26, 115, 232, 0.12);
}

.node-port {
  position: absolute;
  z-index: 4;
  display: grid;
  width: 9px;
  height: 9px;
  padding: 0;
  place-items: center;
  border: 2px solid rgba(255, 255, 255, 0.98);
  border-radius: 999px;
  background: #1a73e8;
  box-shadow: 0 0 0 1px rgba(26, 115, 232, 0.2), 0 6px 14px rgba(26, 115, 232, 0.14);
  cursor: crosshair;
  opacity: 0;
  pointer-events: none;
  transition:
    opacity 160ms ease,
    transform 160ms ease,
    box-shadow 160ms ease,
    background 160ms ease;
}

.node-port::after {
  width: 3px;
  height: 3px;
  border-radius: 999px;
  background: #ffffff;
  content: "";
}

.input-port {
  top: 72px;
  left: -5px;
  background: #8ab4f8;
  box-shadow: 0 0 0 1px rgba(138, 180, 248, 0.28), 0 6px 14px rgba(26, 115, 232, 0.1);
}

.output-port {
  top: 72px;
  right: -5px;
}

.agent-node:hover .node-port,
.agent-node.selected .node-port,
.agent-node.show-handles .node-port,
.node-port:hover {
  opacity: 1;
  pointer-events: auto;
}

.node-port:hover {
  background: #1a73e8;
  box-shadow: 0 0 0 5px rgba(26, 115, 232, 0.14), 0 10px 20px rgba(26, 115, 232, 0.28);
  transform: scale(1.24);
}

.agent-node.branch .node-port {
  background: #f59e0b;
  box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.36), 0 6px 14px rgba(245, 158, 11, 0.2);
}

.agent-node.branch {
  border-color: #fbbc04;
  background:
    linear-gradient(135deg, rgba(251, 188, 4, 0.12), transparent 42%),
    #ffffff;
}

.agent-node.code {
  border-color: #8ab4f8;
  background:
    linear-gradient(90deg, #e8f0fe 0, #e8f0fe 6px, transparent 6px),
    #ffffff;
}

.agent-node.code .node-order {
  background: #e8f0fe;
  color: #1a73e8;
}

.agent-node.approval {
  border-color: #a78bfa;
  background:
    linear-gradient(90deg, #f3e8ff 0, #f3e8ff 6px, transparent 6px),
    #ffffff;
}

.agent-node.approval .node-order {
  background: #f3e8ff;
  color: #7c3aed;
}

.agent-node.custom {
  border-color: #cbd5e1;
  background:
    linear-gradient(90deg, #f1f5f9 0, #f1f5f9 6px, transparent 6px),
    #ffffff;
}

.agent-node.custom .node-order {
  background: #f1f5f9;
  color: #475569;
}

.agent-node.branch .node-order {
  border-radius: 8px;
  background: #fef3c7;
  color: #92400e;
  transform: rotate(45deg);
}

.agent-node.branch .node-order span {
  transform: rotate(-45deg);
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
  gap: 10px;
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

.node-order span {
  display: block;
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
  color: #202124;
  font-size: 14px;
}

.node-title span {
  margin-top: 2px;
  color: #5f6368;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 11px;
}

.agent-node p {
  min-height: 22px;
  margin: 0;
  overflow: hidden;
  color: #5f6368;
  display: -webkit-box;
  font-size: 12px;
  line-height: 1.45;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
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
