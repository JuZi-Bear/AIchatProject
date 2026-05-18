<script setup lang="ts">
defineProps<{
  currentIndex: number;
  total: number;
  playing: boolean;
  speedMs: number;
}>();

const emit = defineEmits<{
  previous: [];
  next: [];
  play: [];
  pause: [];
  reset: [];
  "update:speedMs": [value: number];
}>();

const speedOptions = [
  { label: "500ms", value: 500 },
  { label: "800ms", value: 800 },
  { label: "1200ms", value: 1200 },
];

function updateSpeed(value: string | number) {
  emit("update:speedMs", Number(value));
}
</script>

<template>
  <el-card shadow="never" class="replay-control-card">
    <div class="control-row">
      <div>
        <div class="control-title">逐步回放</div>
        <div class="control-subtitle">当前 {{ total ? currentIndex + 1 : 0 }} / {{ total }}</div>
      </div>
      <div class="control-actions">
        <el-button size="small" :disabled="!total || currentIndex <= 0" @click="emit('previous')">上一步</el-button>
        <el-button size="small" :disabled="!total || currentIndex >= total - 1" @click="emit('next')">下一步</el-button>
        <el-button v-if="!playing" size="small" type="primary" :disabled="!total || currentIndex >= total - 1" @click="emit('play')">
          自动播放
        </el-button>
        <el-button v-else size="small" type="warning" @click="emit('pause')">暂停</el-button>
        <el-button size="small" :disabled="!total" @click="emit('reset')">重置</el-button>
        <el-select
          :model-value="speedMs"
          size="small"
          class="speed-select"
          @update:model-value="updateSpeed"
        >
          <el-option v-for="option in speedOptions" :key="option.value" :label="option.label" :value="option.value" />
        </el-select>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.replay-control-card :deep(.el-card__body) {
  padding: 12px;
}

.control-row,
.control-actions {
  display: flex;
  align-items: center;
}

.control-row {
  justify-content: space-between;
  gap: 12px;
}

.control-title {
  color: #0f172a;
  font-weight: 800;
}

.control-subtitle {
  margin-top: 3px;
  color: #64748b;
  font-size: 12px;
}

.control-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.speed-select {
  width: 110px;
}
</style>
