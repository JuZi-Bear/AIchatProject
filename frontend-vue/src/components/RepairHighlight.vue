<script setup lang="ts">
import { computed } from "vue";

import type { RunResponse } from "@/types/run";

const props = defineProps<{
  response?: RunResponse | null;
  running?: boolean;
  errorDetail?: string;
}>();

const summary = computed(() => props.response?.run_summary);
const agentOutputs = computed(() => props.response?.ui_view_model.agent_outputs);
const hasRepair = computed(() => (summary.value?.retry_count || 0) > 0);

function compactText(value?: string, fallback = "暂无摘要") {
  if (!value) {
    return fallback;
  }

  const normalized = value.replace(/\s+/g, " ").trim();
  return normalized.length > 180 ? `${normalized.slice(0, 180)}...` : normalized;
}
</script>

<template>
  <section class="repair-highlight" :class="{ success: summary?.success, failed: summary?.success === false }">
    <div class="highlight-head">
      <div>
        <div class="panel-title">自动修复高光时刻</div>
        <p>比赛演示重点：展示系统如何从失败反馈进入错误分析与自愈修复。</p>
      </div>
      <el-tag v-if="running" type="primary" effect="dark">运行中</el-tag>
      <el-tag v-else-if="errorDetail" type="danger" effect="dark">演示运行失败</el-tag>
      <el-tag v-else-if="hasRepair" type="warning" effect="dark">已触发自动修复</el-tag>
      <el-tag v-else type="success" effect="dark">一次运行成功</el-tag>
    </div>

    <el-alert
      v-if="errorDetail"
      title="演示运行失败"
      :description="`${errorDetail}。请检查 Python Agent Engine API 是否启动。`"
      type="error"
      show-icon
      :closable="false"
    />

    <div v-else-if="running" class="highlight-grid">
      <div class="highlight-card active">
        <span>当前阶段</span>
        <strong>AI 工作流执行中</strong>
        <p>后端返回后将回放工作流、修复过程、质量评分和报告结果。</p>
      </div>
    </div>

    <div v-else-if="hasRepair" class="highlight-grid">
      <div class="highlight-card danger">
        <span>第一次运行失败</span>
        <strong>测试或运行反馈触发修复</strong>
        <p>{{ compactText(agentOutputs?.error_summary, "系统捕获到失败反馈，并进入错误分析流程。") }}</p>
      </div>
      <div class="highlight-card warning">
        <span>Sentry Agent 分析结果</span>
        <strong>定位失败原因</strong>
        <p>{{ compactText(agentOutputs?.sentry_result, "Sentry Agent 已基于错误摘要生成修复方向。") }}</p>
      </div>
      <div class="highlight-card primary">
        <span>Coder Agent 修复动作</span>
        <strong>生成修复版代码</strong>
        <p>{{ compactText(agentOutputs?.code, "Coder Agent 根据分析结果完成代码修复。") }}</p>
      </div>
      <div class="highlight-card success">
        <span>最终测试结果</span>
        <strong>{{ summary?.test_success ? "pytest 通过" : "pytest 未通过" }}</strong>
        <p>修复次数 {{ summary?.retry_count || 0 }}，覆盖率 {{ summary?.coverage_percent || 0 }}%，质量评分 {{ summary?.quality_score || 0 }}。</p>
      </div>
    </div>

    <div v-else class="highlight-grid">
      <div class="highlight-card success">
        <span>本次任务一次运行成功</span>
        <strong>未触发自动修复</strong>
        <p>代码生成、测试执行、质量评分和报告生成流程顺利完成。</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.repair-highlight {
  padding: 16px;
  border: 1px solid #facc15;
  border-radius: 8px;
  background: #fffbeb;
}

.highlight-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.highlight-head p {
  margin: 4px 0 0;
  color: #78350f;
}

.highlight-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.highlight-card {
  min-height: 126px;
  padding: 12px;
  border: 1px solid #fde68a;
  border-radius: 8px;
  background: #ffffff;
}

.highlight-card span {
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
}

.highlight-card strong {
  display: block;
  margin-top: 8px;
  color: #0f172a;
  font-size: 17px;
}

.highlight-card p {
  display: -webkit-box;
  margin: 8px 0 0;
  overflow: hidden;
  color: #475569;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.highlight-card.danger {
  border-color: #fecaca;
  background: #fff7f7;
}

.highlight-card.warning {
  border-color: #fde68a;
  background: #fffbeb;
}

.highlight-card.primary {
  border-color: #bfdbfe;
  background: #eff6ff;
}

.highlight-card.success {
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.highlight-card.active {
  border-color: #bfdbfe;
  background: #eff6ff;
}
</style>
