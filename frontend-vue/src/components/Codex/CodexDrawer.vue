<script setup lang="ts">
defineProps<{
  open: boolean;
  title: string;
}>();

const emit = defineEmits<{
  close: [];
}>();
</script>

<template>
  <Transition name="codex-drawer">
    <aside v-if="open" class="codex-drawer">
      <header class="codex-drawer-header">
        <h2>{{ title }}</h2>
        <button type="button" @click="emit('close')">Close</button>
      </header>
      <div class="codex-drawer-body">
        <slot />
      </div>
    </aside>
  </Transition>
</template>

<style scoped>
.codex-drawer {
  position: fixed;
  top: 78px;
  right: 18px;
  z-index: 90;
  display: grid;
  width: min(420px, calc(100vw - 36px));
  max-height: calc(100vh - 96px);
  grid-template-rows: auto minmax(0, 1fr);
  overflow: hidden;
  border: 1px solid var(--codex-border);
  border-radius: 22px;
  background: var(--codex-elevated);
  box-shadow: var(--codex-shadow);
}

.codex-drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid var(--codex-border);
}

.codex-drawer-header h2 {
  margin: 0;
  font-size: 16px;
}

.codex-drawer-header button {
  border: 0;
  background: transparent;
  color: var(--codex-muted);
  cursor: pointer;
}

.codex-drawer-body {
  min-height: 0;
  padding: 16px;
  overflow: auto;
}

.codex-drawer-enter-active,
.codex-drawer-leave-active {
  transition:
    opacity 160ms ease,
    transform 180ms cubic-bezier(0.2, 0, 0, 1);
}

.codex-drawer-enter-from,
.codex-drawer-leave-to {
  opacity: 0;
  transform: translateX(18px);
}
</style>
