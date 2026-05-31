<script setup lang="ts">
import CodeAgentPanel from "@/components/WorkflowEditor/CodeAgentPanel.vue";

import type { CodeAgentResponse } from "@/types/codeAgent";

defineEmits<{
  executed: [response: CodeAgentResponse];
}>();
</script>

<template>
  <div class="code-agent-tool-drawer">
    <CodeAgentPanel always-visible embedded @executed="$emit('executed', $event)" />
  </div>
</template>

<style scoped>
.code-agent-tool-drawer {
  min-width: 0;
}
</style>
