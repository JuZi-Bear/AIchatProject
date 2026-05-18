<script setup lang="ts">
import ReplayEventCard from "@/components/ReplayEventCard.vue";
import type { ReplayEvent } from "@/types/replay";

defineProps<{
  events: ReplayEvent[];
  currentIndex: number;
}>();
</script>

<template>
  <el-empty v-if="!events.length" description="暂无回放事件" />
  <el-timeline v-else class="replay-timeline">
    <el-timeline-item
      v-for="(event, index) in events"
      :key="event.id || `${event.eventType}-${event.createdAt}-${index}`"
      :timestamp="event.createdAt"
      placement="top"
      :class="{ future: index > currentIndex }"
    >
      <ReplayEventCard :event="event" :active="index === currentIndex" />
    </el-timeline-item>
  </el-timeline>
</template>

<style scoped>
.replay-timeline {
  padding-top: 6px;
}

.replay-timeline :deep(.future) {
  opacity: 0.45;
}
</style>
