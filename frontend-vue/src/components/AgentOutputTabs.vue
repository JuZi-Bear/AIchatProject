<script setup lang="ts">
import { computed } from "vue";

import PluginResultPanel from "@/components/PluginResultPanel.vue";
import ReportPreview from "@/components/ReportPreview.vue";
import type { RunResponse, UIViewModel } from "@/types/run";

const props = defineProps<{
  response?: RunResponse | null;
  uiViewModel?: UIViewModel;
}>();

const viewModel = computed(() => props.uiViewModel || props.response?.ui_view_model || {});
const agentOutputs = computed(() => viewModel.value.agent_outputs || {});
const pluginOutputs = computed(() => viewModel.value.plugin_outputs || {});
const report = computed(() => viewModel.value.report || {});
const rawJson = computed(() => JSON.stringify(props.response || viewModel.value, null, 2));
</script>

<template>
  <el-tabs type="border-card" class="agent-tabs">
    <el-tab-pane label="Product Agent">
      <pre class="code-block">{{ agentOutputs.product_result || "暂无 Product Agent 输出" }}</pre>
    </el-tab-pane>

    <el-tab-pane label="Coder Agent">
      <pre class="code-block language-python"><code>{{ agentOutputs.code || "暂无代码输出" }}</code></pre>
    </el-tab-pane>

    <el-tab-pane label="Tester Agent">
      <pre class="code-block">{{ agentOutputs.tester_result || "暂无 Tester Agent 输出" }}</pre>
      <pre v-if="agentOutputs.stdout" class="code-block secondary">{{ agentOutputs.stdout }}</pre>
    </el-tab-pane>

    <el-tab-pane label="Sentry Agent">
      <pre class="code-block">{{ agentOutputs.sentry_result || "未触发 Sentry Agent" }}</pre>
      <pre v-if="agentOutputs.error_summary" class="code-block secondary">
{{ agentOutputs.error_summary }}
      </pre>
      <pre v-if="agentOutputs.error_log" class="code-block secondary">{{ agentOutputs.error_log }}</pre>
    </el-tab-pane>

    <el-tab-pane label="Plugins">
      <PluginResultPanel :plugin-outputs="pluginOutputs" />
    </el-tab-pane>

    <el-tab-pane label="Report">
      <ReportPreview :report="report" />
    </el-tab-pane>

    <el-tab-pane label="Raw JSON">
      <pre class="code-block">{{ rawJson }}</pre>
    </el-tab-pane>
  </el-tabs>
</template>

<style scoped>
.agent-tabs {
  width: 100%;
}

.code-block {
  max-height: 520px;
  margin: 0;
  overflow: auto;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  white-space: pre-wrap;
  word-break: break-word;
  color: #0f172a;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 13px;
  line-height: 1.65;
}

.code-block.secondary {
  margin-top: 10px;
  background: #fffaf0;
}
</style>
