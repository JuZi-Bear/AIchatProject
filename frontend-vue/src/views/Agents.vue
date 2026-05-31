<script setup lang="ts">
import { Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";

import { getApiModeLabel } from "@/api/client";
import { getAgents } from "@/api/agents";
import { getPlatformWorkflowTemplates } from "@/api/workflows";
import type { AgentMeta } from "@/types/agent";
import type { AgentNodeData } from "@/types/workflowEditor";

const agents = ref<AgentMeta[]>([]);
const templateAgents = ref<AgentMeta[]>([]);
const loading = ref(false);
const keyword = ref("");
const stageFilter = ref("all");
const apiModeLabel = getApiModeLabel();

const stageOptions = computed(() => {
  const stages = new Set(agents.value.map((agent) => agent.stage).filter(Boolean));
  templateAgents.value.map((agent) => agent.stage).filter(Boolean).forEach((stage) => stages.add(stage));
  return [...stages].sort();
});

const allAgents = computed(() => [...agents.value, ...templateAgents.value]);

const filteredAgents = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase();

  return allAgents.value.filter((agent) => {
    if (stageFilter.value !== "all" && agent.stage !== stageFilter.value) {
      return false;
    }

    if (!normalizedKeyword) {
      return true;
    }

    return `${agent.name} ${agent.key} ${agent.role} ${agent.description}`.toLowerCase().includes(normalizedKeyword);
  });
});

async function loadAgents() {
  loading.value = true;

  try {
    const [registeredResult, templateResult] = await Promise.allSettled([
      getAgents(),
      getPlatformWorkflowTemplates(),
    ]);
    agents.value = registeredResult.status === "fulfilled" ? registeredResult.value : [];
    templateAgents.value =
      templateResult.status === "fulfilled"
        ? templateResult.value.flatMap((template) =>
            template.nodes
              .filter((node: AgentNodeData) => node.nodeType === "custom_agent" || node.agentKey === "custom_agent")
              .map((node: AgentNodeData) => ({
                key: `${template.workflowTemplateKey}:${node.agentKey}`,
                name: node.name,
                role: node.customAgentMeta?.role || node.role || "模板内自定义 Agent",
                description: `${node.description || "模板内自定义 Agent 节点"}（来源：${template.name}）`,
                input_fields: node.input_fields || [],
                output_fields: node.output_fields || [],
                stage: node.stage || "custom",
                enabled: node.enabled,
                version: node.customAgentMeta?.version || template.version || "1.0",
              })),
          )
        : [];

    if (registeredResult.status === "rejected") {
      throw registeredResult.reason;
    }
  } catch (error) {
    agents.value = [];
    ElMessage.error(error instanceof Error ? error.message : "加载 Agent 注册中心失败");
  } finally {
    loading.value = false;
  }
}

onMounted(loadAgents);
</script>

<template>
  <section class="page-stack">
    <div class="page-header">
      <div>
        <h1>Agents</h1>
        <p>查看 Python Agent Engine 注册中心元信息</p>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="loadAgents">刷新</el-button>
    </div>

    <div class="mode-tags">
      <el-tag type="primary" effect="plain">API 模式：{{ apiModeLabel }}</el-tag>
      <el-tag type="success" effect="plain">已注册 Agent：{{ agents.length }}</el-tag>
      <el-tag type="warning" effect="plain">模板自定义 Agent：{{ templateAgents.length }}</el-tag>
    </div>

    <section class="panel">
      <div class="agent-filters">
        <el-input v-model="keyword" :prefix-icon="Search" clearable placeholder="搜索 Agent 名称 / key / 角色" />
        <el-select v-model="stageFilter" class="stage-select">
          <el-option label="全部阶段" value="all" />
          <el-option v-for="stage in stageOptions" :key="stage" :label="stage" :value="stage" />
        </el-select>
      </div>

      <el-empty v-if="!loading && !filteredAgents.length" description="暂无 Agent 元信息" />
      <div v-else class="agent-grid" v-loading="loading">
        <article v-for="agent in filteredAgents" :key="agent.key" class="agent-card">
          <div class="agent-card-head">
            <div>
              <div class="agent-name">{{ agent.name }}</div>
              <div class="agent-key">{{ agent.key }} · v{{ agent.version }}</div>
            </div>
            <el-tag :type="agent.enabled ? 'success' : 'info'" effect="plain">
              {{ agent.enabled ? "enabled" : "disabled" }}
            </el-tag>
          </div>

          <div class="agent-meta">
            <el-tag type="primary" effect="plain">{{ agent.stage || "stage" }}</el-tag>
            <el-tag effect="plain">{{ agent.role || "未记录角色" }}</el-tag>
          </div>

          <p>{{ agent.description || "暂无描述" }}</p>

          <div class="field-block">
            <span>输入字段</span>
            <div>
              <el-tag v-for="field in agent.input_fields" :key="field" size="small" effect="plain">{{ field }}</el-tag>
              <el-tag v-if="!agent.input_fields.length" size="small" effect="plain">无</el-tag>
            </div>
          </div>

          <div class="field-block">
            <span>输出字段</span>
            <div>
              <el-tag v-for="field in agent.output_fields" :key="field" size="small" type="success" effect="plain">
                {{ field }}
              </el-tag>
              <el-tag v-if="!agent.output_fields.length" size="small" effect="plain">无</el-tag>
            </div>
          </div>
        </article>
      </div>
    </section>
  </section>
</template>

<style scoped>
.mode-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.agent-filters {
  display: grid;
  grid-template-columns: 1fr 180px;
  gap: 10px;
  margin-bottom: 14px;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}

.agent-card {
  display: grid;
  gap: 10px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 15px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.014)),
    #17191f;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.035);
}

.agent-card-head,
.agent-meta,
.field-block div {
  display: flex;
  align-items: center;
}

.agent-card-head {
  justify-content: space-between;
  gap: 12px;
}

.agent-name {
  color: var(--codex-text);
  font-size: 16px;
  font-weight: 800;
}

.agent-key {
  margin-top: 3px;
  color: var(--codex-muted);
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 12px;
}

.agent-meta,
.field-block div {
  flex-wrap: wrap;
  gap: 6px;
}

.agent-card p {
  margin: 0;
  color: #d4d4d8;
  line-height: 1.55;
}

.field-block {
  display: grid;
  gap: 6px;
}

.field-block span {
  color: var(--codex-muted);
  font-size: 12px;
  font-weight: 700;
}

@media (max-width: 900px) {
  .agent-filters {
    grid-template-columns: 1fr;
  }
}
</style>
