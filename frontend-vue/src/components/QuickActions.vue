<script setup lang="ts">
import { Connection, Files, List, Operation, SetUp, Share } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";

const router = useRouter();

const actions = [
  { label: "新建运行任务", path: "/runs/new", icon: Operation, type: "primary" },
  { label: "查看历史记录", path: "/history", icon: List, type: "success" },
  { label: "查看报告", path: "/reports", icon: Files, type: "warning" },
  { label: "配置模型", path: "/models", icon: Connection, type: "info" },
  { label: "配置插件", path: "/plugins", icon: SetUp, type: "info" },
  { label: "创建新工作流任务", path: "/workflows/templates", icon: Operation, type: "primary" },
  { label: "编辑工作流", path: "/workflows/editor", icon: Operation, type: "primary" },
  { label: "查看 Agent 注册中心", path: "/agents", icon: Share, type: "info" },
] as const;
</script>

<template>
  <el-card shadow="never" class="dashboard-card">
    <template #header>快捷操作</template>
    <div class="action-grid">
      <el-button
        v-for="action in actions"
        :key="action.path"
        :icon="action.icon"
        :type="action.type"
        @click="router.push(action.path)"
      >
        {{ action.label }}
      </el-button>
    </div>
  </el-card>
</template>

<style scoped>
.dashboard-card {
  border-radius: 8px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}

.action-grid :deep(.el-button) {
  width: 100%;
  margin: 0;
}
</style>
