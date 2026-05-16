<script setup lang="ts">
import { computed } from "vue";

import type { RunResponse } from "@/types/run";

const props = defineProps<{
  response?: RunResponse | null;
  requirement: string;
  enabledPlugins: string[];
  errorDetail?: string;
}>();

const narrationItems = computed(() => {
  const summary = props.response?.run_summary;

  if (props.errorDetail) {
    return [
      "本次演示请求未完成，优先检查 Python Agent Engine API 是否已启动。",
      "Vue 前端已捕获错误并保持页面可用，不会影响其他页面演示。",
    ];
  }

  if (!summary) {
    return [
      "本项目解决从自然语言需求到可测试代码交付的自动化问题。",
      "演示开始后，Product、Coder、Tester、Runner、Sentry、Quality 和 Report 会组成闭环流水线。",
      "如果测试失败，系统会进入错误分析与自动修复流程。",
    ];
  }

  const pluginsText = props.enabledPlugins.length
    ? `插件模块参与：${props.enabledPlugins.join("、")}。`
    : "本次未启用额外插件模块。";

  return [
    `用户需求：${props.requirement || summary.requirement || "已提交自然语言开发任务"}`,
    "参与 Agent：Product 需求拆解、Coder 代码生成、Tester 测试生成、Runner 验证、Quality 评分与 Report 报告。",
    summary.retry_count > 0
      ? `自动修复已触发 ${summary.retry_count} 次，系统完成错误分析并尝试自愈。`
      : "本次任务一次运行成功，未触发自动修复。",
    `测试结果：${summary.test_success ? "pytest 通过" : "pytest 未通过"}，覆盖率 ${summary.coverage_percent}%。`,
    `质量评分：${summary.quality_score}/100，安全状态 ${summary.security_status || "unknown"}。`,
    pluginsText,
    summary.report_path ? "最终 Markdown 报告已生成，可用于答辩复盘。" : "当前结果暂未返回报告路径。",
  ].slice(0, 8);
});
</script>

<template>
  <el-card shadow="never" class="narration-card">
    <template #header>答辩讲解提示</template>
    <ol class="narration-list">
      <li v-for="item in narrationItems" :key="item">{{ item }}</li>
    </ol>
  </el-card>
</template>

<style scoped>
.narration-card {
  border-radius: 8px;
}

.narration-list {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 20px;
}

.narration-list li {
  color: #334155;
  line-height: 1.55;
}
</style>
