<script setup lang="ts">
defineProps<{
  path?: string;
  content?: string;
}>();
</script>

<template>
  <div class="audit-preview">
    <div class="audit-head">
      <strong>审计日志</strong>
      <el-tag v-if="path" effect="plain" size="small">{{ path }}</el-tag>
    </div>
    <pre class="audit-block">{{ content || "执行后会在这里汇总 JSONL 审计日志入口。" }}</pre>
  </div>
</template>

<style scoped>
.audit-preview {
  display: grid;
  gap: 10px;
}

.audit-head {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.audit-block {
  max-height: 220px;
  margin: 0;
  padding: 12px;
  overflow: auto;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: #101218;
  color: #d4d4d8;
  font-size: 12px;
  line-height: 1.55;
  white-space: pre-wrap;
}
</style>
