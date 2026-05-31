<script setup lang="ts">
defineProps<{
  title?: string;
  subtitle?: string;
}>();
</script>

<template>
  <section class="codex-panel">
    <header v-if="title || subtitle" class="codex-panel-header">
      <div>
        <h2 v-if="title">{{ title }}</h2>
        <p v-if="subtitle">{{ subtitle }}</p>
      </div>
      <slot name="actions" />
    </header>
    <slot />
  </section>
</template>

<style scoped>
.codex-panel {
  min-width: 0;
  padding: 18px;
  border: 1px solid var(--codex-border);
  border-radius: var(--codex-radius);
  background: var(--codex-surface);
  color: var(--codex-text);
  box-shadow: 0 12px 34px rgba(0, 0, 0, 0.18);
}

.codex-panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
}

.codex-panel h2 {
  margin: 0;
  color: var(--codex-text);
  font-size: 16px;
  font-weight: 800;
}

.codex-panel p {
  margin: 6px 0 0;
  color: var(--codex-muted);
  line-height: 1.5;
}
</style>
