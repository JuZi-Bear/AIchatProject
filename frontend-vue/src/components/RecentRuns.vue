<script setup lang="ts">
import { useRouter } from "vue-router";

import type { RunHistoryItem } from "@/types/run";
import { runKindLabel, runKindTagType } from "@/utils/runKind";

defineProps<{
  runs: RunHistoryItem[];
  loading?: boolean;
  error?: string;
}>();

const router = useRouter();

function shortRequirement(requirement: string) {
  if (!requirement) {
    return "无需求摘要";
  }

  return requirement.length > 54 ? `${requirement.slice(0, 54)}...` : requirement;
}

function qualityType(score: number) {
  if (score >= 85) {
    return "success";
  }

  if (score >= 60) {
    return "warning";
  }

  return "danger";
}

function openHistory(runId: string) {
  router.push({ path: "/history", query: runId ? { run_id: runId } : {} });
}
</script>

<template>
  <el-card shadow="never" class="dashboard-card" v-loading="loading">
    <template #header>
      <div class="card-header">
        <span>最近运行记录</span>
        <el-button text type="primary" @click="router.push('/history')">全部历史</el-button>
      </div>
    </template>

    <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
    <el-empty v-else-if="!runs.length && !loading" description="暂无运行记录" />

    <div v-else class="recent-run-list">
      <article v-for="run in runs" :key="run.run_id" class="recent-run-item" @click="openHistory(run.run_id)">
        <div class="run-head">
          <span class="run-id">{{ run.run_id }}</span>
          <el-tag :type="run.success ? 'success' : 'danger'" effect="plain" size="small">
            {{ run.success ? "成功" : "失败" }}
          </el-tag>
        </div>
        <div class="run-requirement">{{ shortRequirement(run.requirement) }}</div>
        <div class="run-meta">
          <el-tag :type="runKindTagType(run)" size="small" effect="plain">{{ runKindLabel(run) }}</el-tag>
          <el-tag size="small" effect="plain">{{ run.model_provider || "model" }}</el-tag>
          <el-tag :type="run.retry_count > 0 ? 'warning' : 'info'" size="small" effect="plain">
            修复 {{ run.retry_count }}
          </el-tag>
          <el-tag :type="qualityType(run.quality_score)" size="small" effect="plain">
            质量 {{ run.quality_score }}
          </el-tag>
          <span class="created-at">{{ run.created_at || "未记录时间" }}</span>
        </div>
      </article>
    </div>
  </el-card>
</template>

<style scoped>
.dashboard-card {
  height: 100%;
  border-radius: 8px;
}

.card-header,
.run-head,
.run-meta {
  display: flex;
  align-items: center;
}

.card-header,
.run-head {
  justify-content: space-between;
  gap: 10px;
}

.recent-run-list {
  display: grid;
  gap: 10px;
}

.recent-run-item {
  padding: 11px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fbfdff;
  cursor: pointer;
}

.recent-run-item:hover {
  border-color: #3b82f6;
}

.run-id {
  min-width: 0;
  overflow: hidden;
  color: #0f172a;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.run-requirement {
  margin-top: 7px;
  color: #334155;
  line-height: 1.5;
}

.run-meta {
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 9px;
}

.created-at {
  margin-left: auto;
  color: #64748b;
  font-size: 12px;
}
</style>
