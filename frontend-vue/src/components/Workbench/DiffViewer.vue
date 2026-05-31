<script setup lang="ts">
defineProps<{
  title?: string;
  diff?: string;
  before?: string;
  after?: string;
}>();
</script>

<template>
  <div class="diff-viewer">
    <div v-if="title" class="diff-title">{{ title }}</div>
    <pre v-if="diff" class="diff-block">{{ diff }}</pre>
    <div v-else class="diff-columns">
      <pre class="diff-block before">{{ before || "无写入前内容" }}</pre>
      <pre class="diff-block after">{{ after || "无写入后内容" }}</pre>
    </div>
  </div>
</template>

<style scoped>
.diff-viewer {
  display: grid;
  gap: 10px;
}

.diff-title {
  color: #f4f4f5;
  font-weight: 800;
}

.diff-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.diff-block {
  max-height: 260px;
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

.before {
  border-color: rgba(251, 113, 133, 0.18);
  background:
    linear-gradient(135deg, rgba(251, 113, 133, 0.16), transparent 46%),
    #101218;
}

.after {
  border-color: rgba(74, 222, 128, 0.18);
  background:
    linear-gradient(135deg, rgba(74, 222, 128, 0.14), transparent 46%),
    #101218;
}
</style>
