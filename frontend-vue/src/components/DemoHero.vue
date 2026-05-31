<script setup lang="ts">
const props = defineProps<{
  modelProvider: string;
  demoCaseLabel: string;
  running?: boolean;
  success?: boolean;
  hasResult?: boolean;
  errorDetail?: string;
}>();

function statusText() {
  if (props.running) {
    return "AI 工作流执行中";
  }

  if (props.errorDetail) {
    return "演示运行失败";
  }

  if (!props.hasResult) {
    return "等待开始演示";
  }

  return props.success ? "演示运行成功" : "演示运行未通过";
}

function statusType() {
  if (props.running) {
    return "primary";
  }

  if (props.errorDetail || props.success === false) {
    return "danger";
  }

  if (props.success) {
    return "success";
  }

  return "info";
}
</script>

<template>
  <section class="demo-hero">
    <div>
      <div class="eyebrow">AI 多智能体自主开发流水线</div>
      <h1>AI Multi-Agent Pipeline</h1>
      <p>从自然语言需求到代码生成、自动测试、错误分析与自愈修复的闭环系统。</p>
      <div class="hero-tags">
        <el-tag type="primary" effect="plain">当前模型 {{ modelProvider || "未选择" }}</el-tag>
        <el-tag type="warning" effect="plain">演示案例 {{ demoCaseLabel || "自定义输入" }}</el-tag>
        <el-tag :type="statusType()" effect="dark">{{ statusText() }}</el-tag>
      </div>
    </div>
  </section>
</template>

<style scoped>
.demo-hero {
  padding: 18px;
  border: 1px solid #c7d2fe;
  border-radius: 8px;
  background:
    radial-gradient(circle at 100% 0%, rgba(77, 163, 255, 0.14), transparent 34%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.014)),
    #17191f;
}

.eyebrow {
  color: #0f766e;
  font-size: 13px;
  font-weight: 800;
}

.demo-hero h1 {
  margin: 6px 0 0;
  color: #0f172a;
  font-size: 28px;
}

.demo-hero p {
  max-width: 780px;
  margin: 8px 0 0;
  color: #475569;
  font-size: 15px;
  line-height: 1.6;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}
</style>
