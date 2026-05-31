<script setup lang="ts">
defineProps<{
  src: string;
  title?: string;
}>();
</script>

<template>
  <div class="web-preview-frame">
    <div class="preview-bar">
      <strong>{{ title || "网页预览" }}</strong>
      <a :href="src" target="_blank" rel="noreferrer">新窗口打开</a>
    </div>
    <iframe :src="src" class="preview-frame" />
  </div>
</template>

<style scoped>
.web-preview-frame {
  display: grid;
  gap: 10px;
}

.preview-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.preview-bar a {
  color: #8ab4f8;
  font-size: 12px;
  font-weight: 800;
}

.preview-frame {
  width: 100%;
  height: min(70vh, 680px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  background: #101218;
}
</style>
