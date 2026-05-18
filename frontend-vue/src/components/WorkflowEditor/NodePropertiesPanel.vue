<script setup lang="ts">
import { ElMessage } from "element-plus";
import { computed, reactive, watch } from "vue";

import { useWorkflowEditorStore } from "./WorkflowEditorStore";

const store = useWorkflowEditorStore();
const selectedNode = computed(() => store.selectedNode);
const form = reactive({
  name: "",
  stage: "",
  enabled: true,
  description: "",
  inputFieldsText: "",
  outputFieldsText: "",
});

function fieldsToText(fields: string[]) {
  return fields.join("\n");
}

function textToFields(value: string) {
  return value
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

watch(
  selectedNode,
  (node) => {
    form.name = node?.name || "";
    form.stage = node?.stage || "";
    form.enabled = node?.enabled ?? true;
    form.description = node?.description || "";
    form.inputFieldsText = fieldsToText(node?.input_fields || []);
    form.outputFieldsText = fieldsToText(node?.output_fields || []);
  },
  { immediate: true },
);

function saveNode() {
  if (!selectedNode.value) {
    return;
  }

  store.updateNode(selectedNode.value.nodeId, {
    name: form.name.trim() || selectedNode.value.name,
    stage: form.stage.trim() || "custom",
    enabled: form.enabled,
    description: form.description.trim(),
    input_fields: textToFields(form.inputFieldsText),
    output_fields: textToFields(form.outputFieldsText),
  });
  ElMessage.success("节点属性已更新");
}
</script>

<template>
  <el-card shadow="never" class="properties-card">
    <template #header>
      <div class="panel-head">
        <span>节点属性</span>
        <el-tag v-if="selectedNode" type="primary" effect="plain">{{ selectedNode.agentKey }}</el-tag>
      </div>
    </template>

    <el-empty v-if="!selectedNode" description="请选择画布中的节点" />
    <el-form v-else label-position="top" class="properties-form">
      <el-form-item label="节点名称">
        <el-input v-model="form.name" />
      </el-form-item>

      <el-form-item label="执行阶段">
        <el-input v-model="form.stage" placeholder="analysis / generation / testing / report" />
      </el-form-item>

      <el-form-item label="是否启用">
        <el-switch v-model="form.enabled" active-text="启用" inactive-text="禁用" />
      </el-form-item>

      <el-form-item label="输入字段">
        <el-input v-model="form.inputFieldsText" type="textarea" :rows="4" placeholder="每行一个字段，或用逗号分隔" />
      </el-form-item>

      <el-form-item label="输出字段">
        <el-input v-model="form.outputFieldsText" type="textarea" :rows="4" placeholder="每行一个字段，或用逗号分隔" />
      </el-form-item>

      <el-form-item label="节点说明">
        <el-input v-model="form.description" type="textarea" :rows="5" />
      </el-form-item>

      <el-button type="primary" class="full-width" @click="saveNode">保存修改</el-button>
    </el-form>
  </el-card>
</template>

<style scoped>
.properties-card {
  border-radius: 8px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.properties-form {
  display: grid;
  gap: 2px;
}
</style>
