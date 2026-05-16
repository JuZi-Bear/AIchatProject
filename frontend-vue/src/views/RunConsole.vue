<script setup lang="ts">
import { ElMessage } from "element-plus";
import { computed, onMounted, reactive, ref, watch } from "vue";

import AgentOutputTabs from "@/components/AgentOutputTabs.vue";
import DemoHero from "@/components/DemoHero.vue";
import DemoNarrationPanel from "@/components/DemoNarrationPanel.vue";
import DemoResultSummary from "@/components/DemoResultSummary.vue";
import DemoWorkflowStage from "@/components/DemoWorkflowStage.vue";
import RepairHighlight from "@/components/RepairHighlight.vue";
import ReportPreview from "@/components/ReportPreview.vue";
import ResultOverview from "@/components/ResultOverview.vue";
import SummaryCards from "@/components/SummaryCards.vue";
import WorkflowTimeline from "@/components/WorkflowTimeline.vue";
import { getModels } from "@/api/models";
import { getPlugins } from "@/api/plugins";
import { postRun } from "@/api/runs";
import { useSettingsStore } from "@/stores/settings";
import type { DemoCase, DemoCaseKey } from "@/types/demo";
import type { ModelConfig } from "@/types/model";
import type { PluginConfig } from "@/types/plugin";
import type { RunRequest, RunResponse } from "@/types/run";

const demoCases: DemoCase[] = [
  {
    key: "simple_success",
    label: "简单成功案例",
    description: "适合快速展示从需求到测试通过的标准闭环。",
    requirement: "写一个函数 add_numbers(a, b)，返回两个数字之和，并对非数字输入抛出 ValueError。",
  },
  {
    key: "auto_repair",
    label: "翻车自动修复案例",
    description: "适合突出测试失败、错误分析和自动修复高光时刻。",
    requirement: "写一个函数 get_second_largest(nums)，返回列表中第二大的不同数字；需要处理重复数字、空列表和不足两个不同数字的情况。",
  },
  {
    key: "comprehensive",
    label: "综合案例",
    description: "适合展示多 Agent 协作、插件结果、质量评分和报告产出。",
    requirement: "实现 analyze_scores(scores)，返回最高分、最低分、平均分、及格率，并处理空列表、非数字输入和分数越界情况。",
  },
  {
    key: "custom",
    label: "自定义输入",
    description: "保留当前输入内容，用于现场临时命题。",
    requirement: "",
  },
];

const settingsStore = useSettingsStore();
const models = ref<ModelConfig[]>([]);
const plugins = ref<PluginConfig[]>([]);
const loadingOptions = ref(false);
const running = ref(false);
const result = ref<RunResponse | null>(null);
const errorDetail = ref("");
const lastRequirement = ref("");
const selectedDemoCaseKey = ref<DemoCaseKey>("auto_repair");

const form = reactive<RunRequest>({
  requirement: "",
  model_provider: settingsStore.selectedModelProvider,
  enabled_plugins: [...settingsStore.enabledPlugins],
  max_retry_count: settingsStore.maxRetryCount,
  require_human_approval: settingsStore.requireHumanApproval,
  demo_mode: settingsStore.demoMode,
  offline_mode: settingsStore.offlineMode,
});

const selectedSummary = computed(() => result.value?.run_summary || null);
const workflowSteps = computed(() => result.value?.ui_view_model.workflow_steps || []);
const reportView = computed(() => result.value?.ui_view_model.report || {});
const selectedDemoCase = computed(
  () => demoCases.find((demoCase) => demoCase.key === selectedDemoCaseKey.value) || demoCases[0],
);
const demoCaseLabel = computed(() => selectedDemoCase.value.label);
const currentRunStepHint = computed(() => {
  if (running.value) {
    return "当前阶段提示：AI 工作流执行中，等待后端返回完整运行结果。";
  }

  if (errorDetail.value) {
    return "当前阶段提示：演示运行失败，请检查 Python Agent Engine API 是否启动。";
  }

  if (result.value) {
    return "当前阶段提示：运行完成，正在展示工作流回放、修复高光、质量评分和报告结果。";
  }

  return "当前阶段提示：选择演示案例后点击一键开始演示。";
});

function pluginValue(plugin: PluginConfig) {
  return plugin.display_name || plugin.name;
}

function normalizeError(error: unknown) {
  const possibleError = error as {
    message?: string;
    response?: {
      status?: number;
      data?: unknown;
    };
  };

  if (possibleError.response?.data) {
    const data = possibleError.response.data;

    if (typeof data === "string") {
      return data;
    }

    if (typeof data === "object" && data && "detail" in data) {
      return `HTTP ${possibleError.response.status || ""} ${String((data as { detail?: unknown }).detail)}`;
    }

    return JSON.stringify(data, null, 2);
  }

  return possibleError.message || "运行失败";
}

function applyDemoCase(caseKey = selectedDemoCaseKey.value) {
  const demoCase = demoCases.find((item) => item.key === caseKey);

  if (!demoCase || demoCase.key === "custom") {
    return;
  }

  form.demo_mode = true;
  form.requirement = demoCase.requirement;
  form.max_retry_count = demoCase.key === "simple_success" ? 1 : Math.max(form.max_retry_count, 3);
}

function handleDemoCaseChange(caseKey: DemoCaseKey) {
  selectedDemoCaseKey.value = caseKey;
  applyDemoCase(caseKey);
}

async function loadOptions() {
  loadingOptions.value = true;

  try {
    const [modelRows, pluginRows] = await Promise.all([getModels(), getPlugins()]);
    models.value = modelRows;
    plugins.value = pluginRows;

    settingsStore.hydratePluginDefaults(
      pluginRows.filter((plugin) => plugin.enabled).map((plugin) => pluginValue(plugin)),
    );

    const selectedModel = modelRows.find((model) => model.provider === settingsStore.selectedModelProvider);
    const firstEnabledModel = modelRows.find((model) => model.enabled) || modelRows[0];
    if (selectedModel || firstEnabledModel) {
      form.model_provider = (selectedModel || firstEnabledModel).provider;
    }

    form.enabled_plugins = settingsStore.enabledPlugins.length
      ? [...settingsStore.enabledPlugins]
      : pluginRows.filter((plugin) => plugin.enabled).map((plugin) => pluginValue(plugin));
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "加载模型和插件失败");
  } finally {
    loadingOptions.value = false;
  }
}

async function submitRun() {
  if (running.value) {
    return;
  }

  if (!form.requirement.trim()) {
    ElMessage.warning("请先输入需求");
    return;
  }

  running.value = true;
  result.value = null;
  errorDetail.value = "";
  lastRequirement.value = form.requirement.trim();

  try {
    settingsStore.setRunDefaults({
      demoMode: form.demo_mode,
      maxRetryCount: form.max_retry_count,
      requireHumanApproval: form.require_human_approval,
      offlineMode: form.offline_mode,
    });

    result.value = await postRun({
      ...form,
      requirement: form.requirement.trim(),
    });
    ElMessage.success("运行完成");
  } catch (error) {
    errorDetail.value = normalizeError(error);
    ElMessage.error(errorDetail.value);
  } finally {
    running.value = false;
  }
}

async function startDemoRun() {
  form.demo_mode = true;
  applyDemoCase();

  if (selectedDemoCaseKey.value === "custom" && !form.requirement.trim()) {
    ElMessage.warning("自定义演示需要先输入需求");
    return;
  }

  await submitRun();
}

onMounted(async () => {
  await loadOptions();

  if (form.demo_mode && !form.requirement.trim()) {
    applyDemoCase();
  }
});

watch(
  () => [form.demo_mode, form.max_retry_count, form.require_human_approval, form.offline_mode],
  () => {
    settingsStore.setRunDefaults({
      demoMode: form.demo_mode,
      maxRetryCount: form.max_retry_count,
      requireHumanApproval: form.require_human_approval,
      offlineMode: form.offline_mode,
    });
  },
);
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <h1>RunConsole</h1>
        <p>提交一次 AI 工作流运行请求</p>
      </div>
    </div>

    <el-row :gutter="16">
      <el-col :lg="8" :md="24">
        <section class="panel">
          <div class="panel-title">运行参数</div>
          <el-form label-position="top" :disabled="running">
            <el-form-item label="演示模式">
              <el-switch v-model="form.demo_mode" active-text="启用比赛演示模式" />
            </el-form-item>

            <el-form-item v-if="form.demo_mode" label="演示案例选择">
              <el-select
                v-model="selectedDemoCaseKey"
                class="full-width"
                placeholder="选择演示案例"
                @change="handleDemoCaseChange"
              >
                <el-option
                  v-for="demoCase in demoCases"
                  :key="demoCase.key"
                  :label="demoCase.label"
                  :value="demoCase.key"
                >
                  <div class="demo-case-option">
                    <strong>{{ demoCase.label }}</strong>
                    <span>{{ demoCase.description }}</span>
                  </div>
                </el-option>
              </el-select>
              <div class="form-help">{{ selectedDemoCase.description }}</div>
            </el-form-item>

            <el-form-item label="需求输入">
              <el-input
                v-model="form.requirement"
                type="textarea"
                :rows="8"
                placeholder="例如：写一个函数 get_second_largest(nums)，返回第二大的不同数字"
              />
            </el-form-item>

            <el-form-item label="模型选择">
              <el-select v-model="form.model_provider" class="full-width" :loading="loadingOptions">
                <el-option
                  v-for="model in models"
                  :key="model.provider"
                  :label="`${model.name} / ${model.model}${model.provider === settingsStore.selectedModelProvider ? '（前端默认）' : ''}`"
                  :value="model.provider"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="插件选择">
              <el-select
                v-model="form.enabled_plugins"
                multiple
                class="full-width"
                :loading="loadingOptions"
              >
                <el-option
                  v-for="plugin in plugins"
                  :key="plugin.name"
                  :label="plugin.display_name"
                  :value="pluginValue(plugin)"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="最大修复次数">
              <el-input-number v-model="form.max_retry_count" :min="0" :max="10" />
            </el-form-item>

            <div class="switch-grid">
              <el-switch v-model="form.require_human_approval" active-text="人工审批" />
              <el-switch v-model="form.offline_mode" active-text="离线模式" />
            </div>

            <el-button
              v-if="form.demo_mode"
              type="warning"
              class="full-width action-button"
              :loading="running"
              :disabled="running"
              @click="startDemoRun"
            >
              一键开始演示
            </el-button>

            <el-button
              type="primary"
              class="full-width action-button"
              :loading="running"
              :disabled="running"
              @click="submitRun"
            >
              开始运行
            </el-button>
          </el-form>
        </section>
      </el-col>

      <el-col :lg="16" :md="24">
        <el-alert
          v-if="running"
          title="AI 工作流执行中"
          :description="currentRunStepHint"
          type="info"
          show-icon
          :closable="false"
          class="run-alert"
        />

        <el-alert
          v-if="errorDetail"
          :title="form.demo_mode ? '演示运行失败' : '运行失败'"
          :description="`${errorDetail}。请检查 Python Agent Engine API 是否启动。`"
          type="error"
          show-icon
          :closable="false"
          class="run-alert"
        />

        <div v-if="form.demo_mode" class="demo-mode-stack">
          <DemoHero
            :model-provider="form.model_provider"
            :demo-case-label="demoCaseLabel"
            :running="running"
            :success="selectedSummary?.success"
            :has-result="Boolean(result)"
            :error-detail="errorDetail"
          />

          <DemoWorkflowStage :response="result" :running="running" :error-detail="errorDetail" />
          <RepairHighlight :response="result" :running="running" :error-detail="errorDetail" />
          <DemoResultSummary :response="result" />
          <DemoNarrationPanel
            :response="result"
            :requirement="lastRequirement || form.requirement"
            :enabled-plugins="form.enabled_plugins"
            :error-detail="errorDetail"
          />

          <el-collapse class="demo-collapse">
            <el-collapse-item title="Agent 输出详情" name="agent-outputs">
              <AgentOutputTabs :response="result" />
            </el-collapse-item>
            <el-collapse-item title="报告入口" name="report-preview">
              <ReportPreview :report="reportView" />
            </el-collapse-item>
          </el-collapse>
        </div>

        <template v-else>
          <section class="panel">
            <div class="panel-title">顶部状态摘要</div>
            <SummaryCards :summary="selectedSummary" />
          </section>

          <section class="panel">
            <div class="panel-title">Agent 工作流节点</div>
            <WorkflowTimeline :workflow-steps="workflowSteps" />
          </section>

          <section class="panel">
            <div class="panel-title">最终结果总览</div>
            <ResultOverview :response="result" :requirement="lastRequirement || form.requirement" />
          </section>

          <section class="panel">
            <div class="panel-title">Agent 输出详情</div>
            <AgentOutputTabs :response="result" />
          </section>

          <section class="panel">
            <div class="panel-title">报告入口</div>
            <ReportPreview :report="reportView" />
          </section>
        </template>
      </el-col>
    </el-row>
  </section>
</template>

<style scoped>
.run-alert {
  margin-bottom: 16px;
}

.demo-case-option {
  display: grid;
  gap: 2px;
  padding: 4px 0;
}

.demo-case-option span,
.form-help {
  color: #64748b;
  font-size: 12px;
}

.form-help {
  margin-top: 6px;
  line-height: 1.45;
}

.demo-mode-stack {
  display: grid;
  gap: 14px;
}

.demo-collapse {
  border-radius: 8px;
  background: #ffffff;
}
</style>
