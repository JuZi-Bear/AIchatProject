<script setup lang="ts">
import { computed, reactive } from "vue";

import type { RequirementBuilderState, RequirementTemplate } from "@/types/runConsole";

const props = withDefaults(
  defineProps<{
    modelValue: string;
    disabled?: boolean;
  }>(),
  {
    disabled: false,
  },
);

const emit = defineEmits<{
  "update:modelValue": [value: string];
  "template-applied": [payload: { key: string; useCodeAgent: boolean; codeAgentOperation: string }];
}>();

const emptyState = (): RequirementBuilderState => ({
  goal: "",
  constraints: "",
  acceptanceCriteria: "",
  targetFiles: "",
  outputPreference: "返回可读代码、pytest 测试结果、质量评分和 Markdown 报告。",
  useCodeAgent: false,
  codeAgentOperation: "",
});

const templates: RequirementTemplate[] = [
  {
    key: "function_success",
    label: "普通函数生成",
    description: "适合稳定展示 Product -> Coder -> Tester -> Report。",
    state: {
      goal: "实现 add_numbers(a, b)，返回两个数字之和。",
      constraints: "对非数字输入抛出 ValueError；函数保持纯函数，不访问文件和网络。",
      acceptanceCriteria: "至少覆盖正常加法、负数、小数和非数字输入。",
      targetFiles: "output/generated_code.py",
      outputPreference: "生成 Python 函数、pytest 测试和 Markdown 报告。",
      useCodeAgent: false,
      codeAgentOperation: "",
    },
  },
  {
    key: "auto_repair",
    label: "自动修复案例",
    description: "适合突出失败、Sentry 分析和自动修复。",
    state: {
      goal: "实现 get_second_largest(nums)，返回列表中第二大的不同数字。",
      constraints: "需要处理重复数字、空列表、不足两个不同数字和非数字输入。",
      acceptanceCriteria: "pytest 必须覆盖重复数字、边界输入和异常路径。",
      targetFiles: "output/generated_code.py",
      outputPreference: "展示失败后的修复说明、最终测试状态和质量评分。",
      useCodeAgent: false,
      codeAgentOperation: "",
    },
  },
  {
    key: "code_agent_write",
    label: "CodeAgent 写文件",
    description: "适合展示文件生成、审计日志和 diff。",
    state: {
      goal: "使用 CodeAgent 生成一个演示文件，内容包含 my_func 示例函数。",
      constraints: "文件只能写入 output/code_agent_demo.txt，不允许访问 .env、.git 或 node_modules。",
      acceptanceCriteria: "执行后可以预览文件内容、查看审计日志，并展示写入前后 diff。",
      targetFiles: "output/code_agent_demo.txt",
      outputPreference: "突出 CodeAgent 操作摘要、SSE 事件和 JSONL 审计日志。",
      useCodeAgent: true,
      codeAgentOperation: "write_file",
    },
  },
  {
    key: "code_agent_blocked",
    label: "阻断路径测试",
    description: "适合展示安全白名单和违规路径高亮。",
    state: {
      goal: "测试 CodeAgent 读取 .env 时应被安全策略阻断。",
      constraints: "目标路径为 .env；禁止读取敏感配置；需要返回清晰阻断原因。",
      acceptanceCriteria: "页面应显示失败/阻断状态，事件时间线和审计日志应可追踪。",
      targetFiles: ".env",
      outputPreference: "突出阻断原因、失败事件和安全策略说明。",
      useCodeAgent: true,
      codeAgentOperation: "read_file",
    },
  },
  {
    key: "report_demo",
    label: "报告生成演示",
    description: "适合最终展示报告入口和结果复盘。",
    state: {
      goal: "实现 analyze_scores(scores)，返回最高分、最低分、平均分和及格率。",
      constraints: "处理空列表、非数字输入和分数越界；覆盖率尽量高于 80%。",
      acceptanceCriteria: "最终报告需要包含需求拆解、测试结果、质量评分和插件摘要。",
      targetFiles: "output/generated_code.py",
      outputPreference: "生成 Markdown 报告，并在 Vue 报告入口可查看。",
      useCodeAgent: false,
      codeAgentOperation: "",
    },
  },
];

const state = reactive<RequirementBuilderState>(emptyState());

const generatedRequirement = computed(() => {
  const sections = [
    ["任务目标", state.goal],
    ["约束条件", state.constraints],
    ["验收标准", state.acceptanceCriteria],
    ["目标文件/模块", state.targetFiles],
    ["输出格式偏好", state.outputPreference],
  ].filter(([, value]) => value.trim());

  if (state.useCodeAgent) {
    sections.push([
      "CodeAgent 文件操作",
      `需要触发 CodeAgent ${state.codeAgentOperation || "write_file/read_file/list_files"}，并展示 SSE 事件、审计日志、文件预览或 diff。`,
    ]);
  }

  return sections.map(([label, value]) => `${label}：${value.trim()}`).join("\n");
});

function applyTemplate(template: RequirementTemplate) {
  Object.assign(state, template.state);
  syncToRequirement();
  emit("template-applied", {
    key: template.key,
    useCodeAgent: template.state.useCodeAgent,
    codeAgentOperation: template.state.codeAgentOperation,
  });
}

function syncToRequirement() {
  emit("update:modelValue", generatedRequirement.value || props.modelValue);
}

function resetBuilder() {
  Object.assign(state, emptyState());
}
</script>

<template>
  <div class="requirement-builder">
    <div class="builder-head">
      <div>
        <strong>结构化需求构造器</strong>
        <span>用于比赛现场快速生成更完整的自然语言需求</span>
      </div>
      <el-tag type="primary" effect="plain">不改变 API 请求结构</el-tag>
    </div>

    <div class="template-row">
      <el-button
        v-for="template in templates"
        :key="template.key"
        size="small"
        plain
        :disabled="disabled"
        @click="applyTemplate(template)"
      >
        {{ template.label }}
      </el-button>
    </div>

    <el-form label-position="top" :disabled="disabled" class="builder-form">
      <el-form-item label="任务目标">
        <el-input v-model="state.goal" placeholder="例如：实现一个可测试的 Python 函数" />
      </el-form-item>
      <el-form-item label="约束条件">
        <el-input v-model="state.constraints" type="textarea" :rows="2" placeholder="边界条件、安全限制、禁止访问等" />
      </el-form-item>
      <el-form-item label="验收标准">
        <el-input v-model="state.acceptanceCriteria" type="textarea" :rows="2" placeholder="pytest、覆盖率、报告内容等" />
      </el-form-item>
      <div class="builder-grid">
        <el-form-item label="目标文件/模块">
          <el-input v-model="state.targetFiles" placeholder="output/generated_code.py" />
        </el-form-item>
        <el-form-item label="输出格式偏好">
          <el-input v-model="state.outputPreference" placeholder="代码、测试、质量评分、报告" />
        </el-form-item>
      </div>
      <div class="builder-grid compact">
        <el-form-item label="CodeAgent 文件操作">
          <el-switch v-model="state.useCodeAgent" active-text="需要" inactive-text="不需要" />
        </el-form-item>
        <el-form-item label="CodeAgent 操作类型">
          <el-select v-model="state.codeAgentOperation" :disabled="disabled || !state.useCodeAgent" placeholder="选择操作">
            <el-option label="write_file" value="write_file" />
            <el-option label="read_file" value="read_file" />
            <el-option label="list_files" value="list_files" />
          </el-select>
        </el-form-item>
      </div>
    </el-form>

    <div class="builder-preview">
      <div class="preview-title">
        <span>生成预览</span>
        <div>
          <el-button size="small" text :disabled="disabled" @click="resetBuilder">清空</el-button>
          <el-button size="small" type="primary" plain :disabled="disabled" @click="syncToRequirement">
            写入需求输入
          </el-button>
        </div>
      </div>
      <pre>{{ generatedRequirement || "选择模板或填写字段后，可一键写入下方需求输入。" }}</pre>
    </div>
  </div>
</template>

<style scoped>
.requirement-builder {
  display: grid;
  gap: 12px;
  padding: 12px;
  border: 1px solid #dbe4ef;
  border-radius: 10px;
  background: #f8fafc;
}

.builder-head,
.preview-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.builder-head div {
  display: grid;
  gap: 2px;
}

.builder-head strong {
  color: #0f172a;
  font-size: 14px;
}

.builder-head span {
  color: #64748b;
  font-size: 12px;
}

.template-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.builder-form {
  display: grid;
  gap: 4px;
}

.builder-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.builder-grid.compact {
  align-items: end;
}

.builder-preview {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #ffffff;
}

.preview-title {
  padding: 8px 10px;
  border-bottom: 1px solid #e2e8f0;
  color: #334155;
  font-weight: 800;
}

.builder-preview pre {
  max-height: 160px;
  margin: 0;
  overflow: auto;
  padding: 10px;
  color: #475569;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
  line-height: 1.55;
  white-space: pre-wrap;
}

@media (max-width: 1280px) {
  .builder-grid {
    grid-template-columns: 1fr;
  }
}
</style>
