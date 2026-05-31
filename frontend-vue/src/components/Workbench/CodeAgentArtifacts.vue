<script setup lang="ts">
import { computed } from "vue";

import type { CodeAgentResponse } from "@/types/codeAgent";
import type { ArtifactItem } from "@/types/interaction";

const props = defineProps<{
  response: CodeAgentResponse | null;
}>();

const artifacts = computed<ArtifactItem[]>(() => {
  if (!props.response) {
    return [];
  }

  const rows: ArtifactItem[] = [];

  props.response.results.forEach((result, index) => {
    if (result.filePath) {
      rows.push({
        id: `code-file-${index}-${result.filePath}`,
        type: result.filePath.endsWith(".html") ? "preview" : "file",
        title: result.filePath,
        subtitle: result.message,
        path: result.filePath,
        status: result.success ? "ready" : "failed",
      });
    }

    if (result.auditPath) {
      rows.push({
        id: `code-audit-${index}-${result.auditPath}`,
        type: "audit",
        title: "JSONL 审计日志",
        subtitle: result.auditPath,
        path: result.auditPath,
        status: "ready",
      });
    }

    (result.changes || []).forEach((change, changeIndex) => {
      rows.push({
        id: `code-diff-${index}-${changeIndex}-${change.filePath}`,
        type: "diff",
        title: change.relativePath || change.filePath,
        subtitle: `${change.action} · ${change.reason || "CodeAgent 变更计划"}`,
        path: change.filePath,
        status: change.action === "skip" ? "blocked" : "ready",
        content: change.diff || "",
        meta: { before: change.before, after: change.after },
      });
    });
  });

  return rows;
});
</script>

<template>
  <div class="code-agent-artifacts">
    <div v-if="!artifacts.length" class="empty-artifact">CodeAgent 执行后会显示文件、diff、审计日志和网页预览。</div>
    <article v-for="artifact in artifacts" :key="artifact.id" class="artifact-chip" :class="`artifact-${artifact.type}`">
      <div>
        <strong>{{ artifact.title }}</strong>
        <span>{{ artifact.subtitle || artifact.type }}</span>
      </div>
      <el-tag effect="plain" size="small">{{ artifact.type }}</el-tag>
    </article>
  </div>
</template>

<style scoped>
.code-agent-artifacts {
  display: grid;
  gap: 8px;
}

.empty-artifact {
  padding: 12px;
  border: 1px dashed rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  color: var(--codex-muted);
  font-size: 13px;
}

.artifact-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 12px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.014)),
    #17191f;
}

.artifact-chip strong,
.artifact-chip span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.artifact-chip strong {
  color: var(--codex-text);
  font-size: 13px;
}

.artifact-chip span {
  margin-top: 2px;
  color: var(--codex-muted);
  font-size: 12px;
}

.artifact-diff {
  border-color: rgba(77, 163, 255, 0.22);
  background:
    radial-gradient(circle at 100% 0%, rgba(77, 163, 255, 0.12), transparent 42%),
    #17191f;
}
</style>
