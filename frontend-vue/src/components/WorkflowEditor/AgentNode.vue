<script setup lang="ts">
import { Bottom, Delete, Top } from "@element-plus/icons-vue";
import { computed } from "vue";

import type { AgentNodeData } from "@/types/workflowEditor";
import { classifyWorkflowField, workflowPortColor, workflowPortTypeLabel } from "@/utils/workflowPorts";

const props = defineProps<{
  node: AgentNodeData;
  index: number;
  total: number;
  selected: boolean;
  showHandles?: boolean;
  activeInputFields?: string[];
  activeOutputFields?: string[];
}>();

const emit = defineEmits<{
  select: [nodeId: string, event: MouseEvent];
  delete: [nodeId: string];
  startDrag: [nodeId: string, event: PointerEvent];
  startConnection: [nodeId: string, outputField: string, event: PointerEvent];
  finishConnection: [nodeId: string, inputField: string, event: PointerEvent];
  moveUp: [nodeId: string];
  moveDown: [nodeId: string];
}>();

const MAX_VISIBLE_PORTS = 4;

function buildPorts(fields: string[], activeFields: string[] = []) {
  const activeSet = new Set(activeFields);

  return fields.map((field, index) => {
    const dataType = classifyWorkflowField(field);

    return {
      field,
      index,
      dataType,
      label: workflowPortTypeLabel(field, dataType),
      color: workflowPortColor(field, dataType),
      active: activeSet.has(field),
      extra: index >= MAX_VISIBLE_PORTS,
    };
  });
}

const inputPorts = computed(() => buildPorts(props.node.input_fields, props.activeInputFields || []));
const outputPorts = computed(() => buildPorts(props.node.output_fields, props.activeOutputFields || []));
const hiddenInputCount = computed(() => Math.max(0, props.node.input_fields.length - MAX_VISIBLE_PORTS));
const hiddenOutputCount = computed(() => Math.max(0, props.node.output_fields.length - MAX_VISIBLE_PORTS));
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
    <div class="port-stack input-stack" @pointerdown.stop @click.stop>
      <button
        v-for="port in inputPorts"
        :key="`input-${port.field}`"
        class="field-port input-field-port"
        :class="{ active: port.active, extra: port.extra }"
        :style="{ '--port-color': port.color }"
        :title="`输入：${port.field}`"
        type="button"
        @pointerup.stop="emit('finishConnection', node.nodeId, port.field, $event)"
      >
        <span class="port-dot" />
        <span class="port-name">{{ port.field }}</span>
        <small>{{ port.label }}</small>
      </button>
      <span v-if="hiddenInputCount" class="port-more input-more">+{{ hiddenInputCount }}</span>
    </div>

    <div class="port-stack output-stack" @pointerdown.stop @click.stop>
      <button
        v-for="port in outputPorts"
        :key="`output-${port.field}`"
        class="field-port output-field-port"
        :class="{ active: port.active, extra: port.extra }"
        :style="{ '--port-color': port.color }"
        :title="`输出：${port.field}`"
        type="button"
        @pointerdown.stop="emit('startConnection', node.nodeId, port.field, $event)"
      >
        <small>{{ port.label }}</small>
        <span class="port-name">{{ port.field }}</span>
        <span class="port-dot" />
      </button>
      <span v-if="hiddenOutputCount" class="port-more output-more">+{{ hiddenOutputCount }}</span>
    </div>

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
  width: 416px;
  min-height: 176px;
  gap: 8px;
  padding: 14px 134px 12px;
  border: 1px solid rgba(148, 163, 184, 0.5);
  border-radius: 15px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.07), transparent 32%),
    #272d36;
  box-shadow:
    0 14px 34px rgba(15, 23, 42, 0.22),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
  cursor: grab;
  user-select: none;
}

.agent-node:active {
  cursor: grabbing;
}

.agent-node.selected {
  border-color: #1a73e8;
  box-shadow:
    0 0 0 3px rgba(26, 115, 232, 0.22),
    0 18px 42px rgba(26, 115, 232, 0.22),
    inset 0 1px 0 rgba(255, 255, 255, 0.16);
}

.port-stack {
  position: absolute;
  z-index: 5;
  top: 52px;
  display: grid;
  gap: 6px;
  pointer-events: none;
}

.input-stack {
  left: 12px;
}

.output-stack {
  right: 12px;
  justify-items: end;
}

.field-port {
  display: grid;
  width: 124px;
  min-height: 24px;
  align-items: center;
  gap: 4px;
  padding: 3px 6px;
  border: 1px solid rgba(148, 163, 184, 0.48);
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.78);
  color: #cbd5e1;
  cursor: crosshair;
  opacity: 0.9;
  pointer-events: auto;
  transition:
    opacity 160ms ease,
    transform 160ms ease,
    box-shadow 160ms ease,
    background 160ms ease,
    border-color 160ms ease,
    color 160ms ease;
}

.input-field-port {
  grid-template-columns: auto minmax(0, 1fr) auto;
  text-align: left;
}

.output-field-port {
  grid-template-columns: auto minmax(0, 1fr) auto;
  text-align: right;
}

.port-dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: var(--port-color);
  box-shadow:
    0 0 0 2px #313842,
    0 0 0 3px color-mix(in srgb, var(--port-color) 40%, transparent),
    0 0 12px color-mix(in srgb, var(--port-color) 38%, transparent);
}

.port-name {
  overflow: hidden;
  color: #f8fafc;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 9.5px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.field-port small {
  color: #94a3b8;
  font-size: 8.5px;
  font-weight: 850;
}

.field-port.extra {
  display: none;
}

.port-more {
  display: none;
  width: max-content;
  padding: 2px 6px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.76);
  color: #cbd5e1;
  font-size: 10px;
  font-weight: 850;
}

.agent-node:not(:hover):not(.selected):not(.show-handles) .field-port.active,
.agent-node:hover .field-port,
.agent-node.selected .field-port,
.agent-node.show-handles .field-port,
.field-port:hover {
  opacity: 1;
  pointer-events: auto;
}

.agent-node:hover .field-port.extra,
.agent-node.selected .field-port.extra,
.agent-node.show-handles .field-port.extra {
  display: grid;
}

.agent-node:not(:hover):not(.selected):not(.show-handles) .port-more {
  display: inline-flex;
  opacity: 0.72;
}

.field-port:hover,
.field-port.active {
  border-color: color-mix(in srgb, var(--port-color) 72%, #ffffff);
  background: color-mix(in srgb, var(--port-color) 18%, #111827);
  box-shadow: 0 8px 18px color-mix(in srgb, var(--port-color) 22%, transparent);
  color: var(--port-color);
  transform: translateY(-1px);
}

.agent-node.branch .field-port .port-dot {
  background: #f59e0b;
}

.agent-node.branch {
  border-color: #fbbc04;
  background:
    linear-gradient(135deg, rgba(251, 188, 4, 0.22), transparent 42%),
    #313842;
}

.agent-node.code {
  border-color: #8ab4f8;
  background:
    linear-gradient(90deg, #1a73e8 0, #1a73e8 6px, transparent 6px),
    linear-gradient(135deg, rgba(26, 115, 232, 0.18), transparent 48%),
    #272d36;
}

.agent-node.code .node-order {
  background: rgba(77, 163, 255, 0.18);
  color: #9bd4ff;
}

.agent-node.approval {
  border-color: #a78bfa;
  background:
    linear-gradient(90deg, #a78bfa 0, #a78bfa 6px, transparent 6px),
    #272d36;
}

.agent-node.approval .node-order {
  background: rgba(167, 139, 250, 0.2);
  color: #c4b5fd;
}

.agent-node.custom {
  border-color: #cbd5e1;
  background:
    linear-gradient(90deg, #94a3b8 0, #94a3b8 6px, transparent 6px),
    #272d36;
}

.agent-node.custom .node-order {
  background: rgba(148, 163, 184, 0.18);
  color: #cbd5e1;
}

.agent-node.branch .node-order {
  border-radius: 8px;
  background: rgba(250, 204, 21, 0.18);
  color: #fde68a;
  transform: rotate(45deg);
}

.agent-node.branch .node-order span {
  transform: rotate(-45deg);
}

.agent-node.disabled {
  background: #475569;
  opacity: 0.72;
}

.node-header,
.node-tags,
.node-actions {
  display: flex;
  align-items: center;
}

.node-header {
  gap: 8px;
}

.node-order {
  display: grid;
  width: 26px;
  height: 26px;
  place-items: center;
  border-radius: 50%;
  background: rgba(248, 250, 252, 0.12);
  color: #e2e8f0;
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
  color: #f8fafc;
  font-size: 13px;
}

.node-title span {
  margin-top: 2px;
  color: #cbd5e1;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 10.5px;
}

.agent-node p {
  min-height: 18px;
  margin: 0;
  overflow: hidden;
  color: #cbd5e1;
  display: -webkit-box;
  font-size: 11.5px;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}

.node-tags {
  flex-wrap: wrap;
  gap: 4px;
}

.node-actions {
  justify-content: flex-end;
  gap: 6px;
}

.agent-node :deep(.el-tag) {
  border-color: rgba(226, 232, 240, 0.28);
  background: rgba(15, 23, 42, 0.34);
  color: #e2e8f0;
}
</style>
