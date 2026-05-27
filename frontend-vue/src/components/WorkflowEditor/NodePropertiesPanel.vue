<script setup lang="ts">
import { ElMessage } from "element-plus";
import { computed, reactive, ref, watch } from "vue";

import { useWorkflowEditorStore } from "./WorkflowEditorStore";
import type { ConnectionData } from "@/types/workflowEditor";
import {
  classifyWorkflowField,
  workflowConnectionKey,
  workflowPortColor,
  workflowPortTypeLabel,
} from "@/utils/workflowPorts";

const props = withDefaults(
  defineProps<{
    embedded?: boolean;
  }>(),
  {
    embedded: false,
  },
);

const store = useWorkflowEditorStore();
const selectedNode = computed(() => store.selectedNode);
const activeTab = ref("basic");
const form = reactive({
  agentKey: "",
  name: "",
  role: "",
  stage: "",
  enabled: true,
  description: "",
  inputFieldsText: "",
  outputFieldsText: "",
  codeOperation: "write_file" as
    | "read_file"
    | "write_file"
    | "list_files"
    | "scan_folder"
    | "read_folder"
    | "plan_folder_changes"
    | "apply_folder_changes",
  codeTargetPath: "output/code_agent_demo.txt",
  codeContent: "",
  codeAuditPath: "output/code_agent_audit.jsonl",
  codeIncludePatterns: "**/*.md, **/*.txt, **/*.py, **/*.ts, **/*.vue",
  codeExcludePatterns: ".env, .git/**, node_modules/**, dist/**, target/**",
  codeOutputFile: "code_agent_folder_result.md",
  codeDryRun: true,
  codeBackupBeforeWrite: true,
  approvalQuestion: "是否批准继续执行后续节点？",
  approvalApproveLabel: "批准继续",
  approvalRejectLabel: "拒绝停止",
  approvalRequired: true,
  customRole: "自定义智能体",
  customPromptRef: "",
  customVersion: "1.0",
});

const selectedIndex = computed(() =>
  selectedNode.value ? store.orderedNodes.findIndex((node) => node.nodeId === selectedNode.value?.nodeId) : -1,
);
const selectedWarnings = computed(() => {
  if (!selectedNode.value) {
    return [];
  }

  return store.validateWorkflow().filter((issue) => issue.nodeId === selectedNode.value?.nodeId);
});
const inboundConnections = computed(() =>
  selectedNode.value
    ? store.connections.filter((connection) => connection.toNodeId === selectedNode.value?.nodeId)
    : [],
);
const outboundConnections = computed(() =>
  selectedNode.value
    ? store.connections.filter((connection) => connection.fromNodeId === selectedNode.value?.nodeId)
    : [],
);
const inputBindingMap = computed(() => {
  const map = new Map<string, ConnectionData[]>();

  inboundConnections.value.forEach((connection) => {
    const key = connection.toInputField || "default";
    map.set(key, [...(map.get(key) || []), connection]);
  });

  return map;
});
const outputBindingMap = computed(() => {
  const map = new Map<string, ConnectionData[]>();

  outboundConnections.value.forEach((connection) => {
    const key = connection.fromOutputField || "default";
    map.set(key, [...(map.get(key) || []), connection]);
  });

  return map;
});
const isCodeAgentNode = computed(() => selectedNode.value?.agentKey === "code_agent" || selectedNode.value?.nodeType === "code_agent");
const isHumanApprovalNode = computed(
  () => selectedNode.value?.agentKey === "human_approval" || selectedNode.value?.nodeType === "human_approval",
);
const isCustomAgentNode = computed(
  () => selectedNode.value?.agentKey === "custom_agent" || selectedNode.value?.nodeType === "custom_agent",
);

function fieldsToText(fields: string[]) {
  return fields.join("\n");
}

function textToFields(value: string) {
  return value
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function nodeName(nodeId: string) {
  return store.nodes.find((node) => node.nodeId === nodeId)?.name || nodeId;
}

function nodeOutputFields(nodeId: string) {
  return store.nodes.find((node) => node.nodeId === nodeId)?.output_fields || [];
}

function nodeInputFields(nodeId: string) {
  return store.nodes.find((node) => node.nodeId === nodeId)?.input_fields || [];
}

function fieldColor(field = "") {
  return workflowPortColor(field, classifyWorkflowField(field));
}

function fieldTypeLabel(field = "") {
  return workflowPortTypeLabel(field, classifyWorkflowField(field));
}

function updateConnectionMapping(connection: ConnectionData, patch: Partial<ConnectionData>) {
  const fromOutputField = patch.fromOutputField ?? connection.fromOutputField;
  const toInputField = patch.toInputField ?? connection.toInputField;
  const dataType = classifyWorkflowField(fromOutputField || toInputField || "");

  store.updateConnection(workflowConnectionKey(connection), {
    ...patch,
    dataType,
    color: workflowPortColor(fromOutputField || toInputField || "", dataType),
    label: `${fromOutputField || "output"} → ${toInputField || "input"}`,
  });
}

function updateConnectionFromOutput(connection: ConnectionData, value: string | number) {
  updateConnectionMapping(connection, { fromOutputField: String(value) });
}

function updateConnectionToInput(connection: ConnectionData, value: string | number) {
  updateConnectionMapping(connection, { toInputField: String(value) });
}

watch(
  selectedNode,
  (node) => {
    form.name = node?.name || "";
    form.agentKey = node?.agentKey || "";
    form.role = node?.role || "";
    form.stage = node?.stage || "";
    form.enabled = node?.enabled ?? true;
    form.description = node?.description || "";
    form.inputFieldsText = fieldsToText(node?.input_fields || []);
    form.outputFieldsText = fieldsToText(node?.output_fields || []);
    form.codeOperation = node?.codeAgentConfig?.operation || "write_file";
    form.codeTargetPath = node?.codeAgentConfig?.target_path || "output/code_agent_demo.txt";
    form.codeContent = node?.codeAgentConfig?.content || "";
    form.codeAuditPath = node?.codeAgentConfig?.audit_log_path || "output/code_agent_audit.jsonl";
    form.codeIncludePatterns = node?.codeAgentConfig?.includePatterns || "**/*.md, **/*.txt, **/*.py, **/*.ts, **/*.vue";
    form.codeExcludePatterns = node?.codeAgentConfig?.excludePatterns || ".env, .git/**, node_modules/**, dist/**, target/**";
    form.codeOutputFile = node?.codeAgentConfig?.outputFile || "code_agent_folder_result.md";
    form.codeDryRun = node?.codeAgentConfig?.dryRun ?? true;
    form.codeBackupBeforeWrite = node?.codeAgentConfig?.backupBeforeWrite ?? true;
    form.approvalQuestion = node?.humanApprovalConfig?.question || "是否批准继续执行后续节点？";
    form.approvalApproveLabel = node?.humanApprovalConfig?.approveLabel || "批准继续";
    form.approvalRejectLabel = node?.humanApprovalConfig?.rejectLabel || "拒绝停止";
    form.approvalRequired = node?.humanApprovalConfig?.required ?? true;
    form.customRole = node?.customAgentMeta?.role || node?.role || "自定义智能体";
    form.customPromptRef = node?.customAgentMeta?.promptRef || "";
    form.customVersion = node?.customAgentMeta?.version || "1.0";
    activeTab.value = "basic";
  },
  { immediate: true },
);

function saveNode() {
  if (!selectedNode.value) {
    return;
  }

  store.updateNode(selectedNode.value.nodeId, {
    agentKey:
      isCustomAgentNode.value && form.agentKey.trim()
        ? form.agentKey.trim()
        : selectedNode.value.agentKey,
    name: form.name.trim() || selectedNode.value.name,
    role: form.role.trim(),
    stage: form.stage.trim() || "custom",
    enabled: form.enabled,
    description: form.description.trim(),
    input_fields: textToFields(form.inputFieldsText),
    output_fields: textToFields(form.outputFieldsText),
    codeAgentConfig:
      isCodeAgentNode.value
        ? {
            operation: form.codeOperation,
            target_path: form.codeTargetPath.trim(),
            content: form.codeContent,
            audit_log_path: form.codeAuditPath.trim() || "output/code_agent_audit.jsonl",
            includePatterns: form.codeIncludePatterns,
            excludePatterns: form.codeExcludePatterns,
            outputFile: form.codeOutputFile,
            dryRun: form.codeDryRun,
            backupBeforeWrite: form.codeBackupBeforeWrite,
          }
        : selectedNode.value.codeAgentConfig,
    humanApprovalConfig:
      isHumanApprovalNode.value
        ? {
            question: form.approvalQuestion.trim(),
            approveLabel: form.approvalApproveLabel.trim() || "批准继续",
            rejectLabel: form.approvalRejectLabel.trim() || "拒绝停止",
            required: form.approvalRequired,
          }
        : selectedNode.value.humanApprovalConfig,
    customAgentMeta:
      isCustomAgentNode.value
        ? {
            role: form.customRole.trim() || "自定义智能体",
            promptRef: form.customPromptRef.trim(),
            version: form.customVersion.trim() || "1.0",
          }
        : selectedNode.value.customAgentMeta,
  });
  ElMessage.success("节点属性已更新");
}
</script>

<template>
  <el-card shadow="never" class="properties-card" :class="{ embedded: props.embedded }">
    <template v-if="!props.embedded" #header>
      <div class="panel-head">
        <span>节点属性</span>
        <el-tag v-if="selectedNode" type="primary" effect="plain">{{ selectedNode.agentKey }}</el-tag>
      </div>
    </template>

    <el-empty v-if="!selectedNode" description="请选择画布中的节点" />
    <template v-else>
      <el-tabs v-model="activeTab" class="node-tabs">
        <el-tab-pane label="基础信息" name="basic">
          <el-form label-position="top" class="properties-form">
            <el-form-item v-if="isCustomAgentNode" label="Agent Key">
              <el-input v-model="form.agentKey" placeholder="my_custom_agent" />
            </el-form-item>
            <el-form-item label="节点名称">
              <el-input v-model="form.name" />
            </el-form-item>
            <el-form-item label="角色">
              <el-input v-model="form.role" placeholder="需求分析智能体 / 自定义智能体" />
            </el-form-item>
            <el-form-item label="执行阶段">
              <el-input v-model="form.stage" placeholder="analysis / implementation / testing / repair / report" />
            </el-form-item>
            <el-form-item label="是否启用">
              <el-switch v-model="form.enabled" active-text="启用" inactive-text="禁用" />
            </el-form-item>
            <el-form-item label="节点说明">
              <el-input v-model="form.description" type="textarea" :rows="3" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="输入输出" name="io">
          <el-collapse>
            <el-collapse-item title="输入字段" name="input">
              <el-input
                v-model="form.inputFieldsText"
                type="textarea"
                :rows="4"
                placeholder="每行一个字段，或用逗号分隔"
              />
            </el-collapse-item>
            <el-collapse-item title="输出字段" name="output">
              <el-input
                v-model="form.outputFieldsText"
                type="textarea"
                :rows="4"
                placeholder="每行一个字段，或用逗号分隔"
              />
            </el-collapse-item>
          </el-collapse>
        </el-tab-pane>

        <el-tab-pane label="映射关系" name="mapping">
          <div class="mapping-stack">
            <section class="mapping-section">
              <div class="mapping-title">
                <strong>输入来源</strong>
                <span>{{ inboundConnections.length }} 条上游连接</span>
              </div>
              <article v-for="field in textToFields(form.inputFieldsText)" :key="`input-map-${field}`" class="field-map-card">
                <div class="field-map-head">
                  <span class="field-dot" :style="{ background: fieldColor(field) }" />
                  <strong>{{ field }}</strong>
                  <el-tag size="small" effect="plain">{{ fieldTypeLabel(field) }}</el-tag>
                </div>
                <template v-if="inputBindingMap.get(field)?.length">
                  <div
                    v-for="connection in inputBindingMap.get(field)"
                    :key="workflowConnectionKey(connection)"
                    class="mapping-row"
                  >
                    <span>{{ nodeName(connection.fromNodeId) }}</span>
                    <el-select
                      :model-value="connection.fromOutputField"
                      size="small"
                      class="mapping-select"
                      @change="updateConnectionFromOutput(connection, $event)"
                    >
                      <el-option
                        v-for="option in nodeOutputFields(connection.fromNodeId)"
                        :key="option"
                        :label="option"
                        :value="option"
                      />
                    </el-select>
                    <span>→</span>
                    <el-select
                      :model-value="connection.toInputField"
                      size="small"
                      class="mapping-select"
                      @change="updateConnectionToInput(connection, $event)"
                    >
                      <el-option
                        v-for="option in nodeInputFields(connection.toNodeId)"
                        :key="option"
                        :label="option"
                        :value="option"
                      />
                    </el-select>
                  </div>
                </template>
                <span v-else class="unbound-text">未绑定上游输出</span>
              </article>
            </section>

            <section class="mapping-section">
              <div class="mapping-title">
                <strong>输出分发</strong>
                <span>{{ outboundConnections.length }} 条下游连接</span>
              </div>
              <article v-for="field in textToFields(form.outputFieldsText)" :key="`output-map-${field}`" class="field-map-card">
                <div class="field-map-head">
                  <span class="field-dot" :style="{ background: fieldColor(field) }" />
                  <strong>{{ field }}</strong>
                  <el-tag size="small" effect="plain">{{ fieldTypeLabel(field) }}</el-tag>
                </div>
                <template v-if="outputBindingMap.get(field)?.length">
                  <div
                    v-for="connection in outputBindingMap.get(field)"
                    :key="workflowConnectionKey(connection)"
                    class="mapping-row"
                  >
                    <el-select
                      :model-value="connection.fromOutputField"
                      size="small"
                      class="mapping-select"
                      @change="updateConnectionFromOutput(connection, $event)"
                    >
                      <el-option
                        v-for="option in nodeOutputFields(connection.fromNodeId)"
                        :key="option"
                        :label="option"
                        :value="option"
                      />
                    </el-select>
                    <span>→</span>
                    <span>{{ nodeName(connection.toNodeId) }}</span>
                    <el-select
                      :model-value="connection.toInputField"
                      size="small"
                      class="mapping-select"
                      @change="updateConnectionToInput(connection, $event)"
                    >
                      <el-option
                        v-for="option in nodeInputFields(connection.toNodeId)"
                        :key="option"
                        :label="option"
                        :value="option"
                      />
                    </el-select>
                  </div>
                </template>
                <span v-else class="unbound-text">未分发到下游输入</span>
              </article>
            </section>
          </div>
        </el-tab-pane>

        <el-tab-pane v-if="isCodeAgentNode" label="Code" name="code-agent">
          <el-alert
            title="文件操作受 allowed_paths 白名单和 blocked_paths 阻断规则保护。"
            type="warning"
            show-icon
            :closable="false"
            class="tab-alert"
          />
          <el-form label-position="top" class="properties-form">
            <el-form-item label="operation">
              <el-select v-model="form.codeOperation" class="full-width">
                <el-option label="read_file" value="read_file" />
                <el-option label="write_file" value="write_file" />
                <el-option label="list_files" value="list_files" />
                <el-option label="scan_folder" value="scan_folder" />
                <el-option label="read_folder" value="read_folder" />
                <el-option label="plan_folder_changes" value="plan_folder_changes" />
                <el-option label="apply_folder_changes" value="apply_folder_changes" />
              </el-select>
            </el-form-item>
            <el-form-item label="target_path">
              <el-input v-model="form.codeTargetPath" placeholder="output/code_agent_demo.txt" />
            </el-form-item>
            <el-form-item v-if="form.codeOperation === 'write_file' || form.codeOperation.includes('folder')" label="content">
              <el-input v-model="form.codeContent" type="textarea" :rows="4" placeholder="# demo content" />
            </el-form-item>
            <template v-if="form.codeOperation.includes('folder')">
              <el-form-item label="include patterns">
                <el-input v-model="form.codeIncludePatterns" placeholder="**/*.py, **/*.md" />
              </el-form-item>
              <el-form-item label="exclude patterns">
                <el-input v-model="form.codeExcludePatterns" placeholder=".env, .git/**, node_modules/**" />
              </el-form-item>
              <el-form-item label="output file">
                <el-input v-model="form.codeOutputFile" placeholder="code_agent_folder_result.md" />
              </el-form-item>
              <div class="inline-switches">
                <el-switch v-model="form.codeDryRun" active-text="dry-run" inactive-text="apply" />
                <el-switch v-model="form.codeBackupBeforeWrite" active-text="备份" inactive-text="不备份" />
              </div>
            </template>
            <el-form-item label="audit_log_path">
              <el-input v-model="form.codeAuditPath" placeholder="output/code_agent_audit.jsonl" />
            </el-form-item>
            <div class="code-hints">
              <el-tag type="success" effect="plain">allowed_paths</el-tag>
              <span>output / reports / runs / docs 等演示安全目录</span>
              <el-tag type="danger" effect="plain">blocked_paths</el-tag>
              <span>.env / .git / node_modules / 构建产物等敏感路径</span>
            </div>
          </el-form>
        </el-tab-pane>

        <el-tab-pane v-if="isHumanApprovalNode" label="人工确认" name="human-approval">
          <el-alert
            title="当前是平台层审批节点：用于模板回放、SSE 事件和人工确认记录，不改 LangGraph 动态拓扑。"
            type="info"
            show-icon
            :closable="false"
            class="tab-alert"
          />
          <el-form label-position="top" class="properties-form">
            <el-form-item label="询问内容">
              <el-input v-model="form.approvalQuestion" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item label="批准按钮文案">
              <el-input v-model="form.approvalApproveLabel" />
            </el-form-item>
            <el-form-item label="拒绝按钮文案">
              <el-input v-model="form.approvalRejectLabel" />
            </el-form-item>
            <el-form-item label="是否必须确认">
              <el-switch v-model="form.approvalRequired" active-text="必须确认" inactive-text="可跳过" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane v-if="isCustomAgentNode" label="自定义 Agent" name="custom-agent">
          <el-alert
            title="自定义 Agent 第一阶段只保存到模板 JSON，不自动注册到 Python Agent Registry。"
            type="warning"
            show-icon
            :closable="false"
            class="tab-alert"
          />
          <el-form label-position="top" class="properties-form">
            <el-form-item label="自定义角色">
              <el-input v-model="form.customRole" />
            </el-form-item>
            <el-form-item label="Prompt 模板引用">
              <el-input v-model="form.customPromptRef" placeholder="prompts/my_custom_agent.md" />
            </el-form-item>
            <el-form-item label="版本">
              <el-input v-model="form.customVersion" placeholder="1.0" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="预览" name="preview">
          <div class="preview-stack">
            <article class="preview-card">
              <span>执行位置</span>
              <strong>#{{ selectedIndex + 1 }}</strong>
            </article>
            <article class="preview-card">
              <span>输入 / 输出</span>
              <strong>{{ textToFields(form.inputFieldsText).length }} / {{ textToFields(form.outputFieldsText).length }}</strong>
            </article>
            <el-alert
              v-for="issue in selectedWarnings"
              :key="`${issue.title}-${issue.message}`"
              :title="issue.title"
              :description="issue.message"
              :type="issue.severity === 'error' ? 'error' : 'warning'"
              show-icon
              :closable="false"
            />
            <el-empty v-if="!selectedWarnings.length" description="当前节点暂无风险提示" />
          </div>
        </el-tab-pane>
      </el-tabs>

      <el-button type="primary" class="full-width save-button" @click="saveNode">保存修改</el-button>
    </template>
  </el-card>
</template>

<style scoped>
.properties-card {
  border-radius: 14px;
}

.properties-card.embedded {
  border: 0;
  border-radius: 0;
}

.properties-card.embedded :deep(.el-card__body) {
  padding: 0;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.node-tabs :deep(.el-tabs__header) {
  margin-bottom: 12px;
}

.properties-form {
  display: grid;
  gap: 2px;
}

.tab-alert {
  margin-bottom: 12px;
}

.code-hints {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 8px;
  align-items: center;
  color: #5f6368;
  font-size: 12px;
  line-height: 1.45;
}

.inline-switches {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 2px 0 12px;
}

.mapping-stack {
  display: grid;
  gap: 14px;
}

.mapping-section {
  display: grid;
  gap: 8px;
}

.mapping-title,
.field-map-head,
.mapping-row {
  display: flex;
  align-items: center;
}

.mapping-title {
  justify-content: space-between;
  gap: 10px;
}

.mapping-title strong {
  color: #202124;
  font-size: 13px;
}

.mapping-title span {
  color: #5f6368;
  font-size: 12px;
}

.field-map-card {
  display: grid;
  gap: 8px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #ffffff;
}

.field-map-head {
  gap: 8px;
}

.field-map-head strong {
  flex: 1;
  overflow: hidden;
  color: #202124;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.field-dot {
  width: 10px;
  height: 10px;
  flex: 0 0 auto;
  border-radius: 50%;
  box-shadow: 0 0 0 2px #ffffff, 0 0 0 3px rgba(100, 116, 139, 0.18);
}

.mapping-row {
  flex-wrap: wrap;
  gap: 6px;
  padding: 7px;
  border-radius: 10px;
  background: #f8fafd;
  color: #5f6368;
  font-size: 12px;
}

.mapping-row > span {
  color: #334155;
  font-weight: 700;
}

.mapping-select {
  width: 126px;
}

.unbound-text {
  padding: 7px 9px;
  border-radius: 10px;
  background: #f8fafc;
  color: #94a3b8;
  font-size: 12px;
}

.preview-stack {
  display: grid;
  gap: 10px;
}

.preview-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border: 1px solid #dadce0;
  border-radius: 12px;
  background: #f8fafd;
}

.preview-card span {
  color: #5f6368;
  font-size: 12px;
}

.preview-card strong {
  color: #1a73e8;
  font-size: 18px;
}

.save-button {
  margin-top: 14px;
}
</style>
