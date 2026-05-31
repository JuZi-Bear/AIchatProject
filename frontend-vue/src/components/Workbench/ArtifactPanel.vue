<script setup lang="ts">
import { computed, ref } from "vue";
import { ElMessage } from "element-plus";

import { getCodeAgentPreviewUrl, openCodeAgentFolder } from "@/api/codeAgent";
import AuditLogPreview from "@/components/Workbench/AuditLogPreview.vue";
import CodeAgentArtifacts from "@/components/Workbench/CodeAgentArtifacts.vue";
import DiffViewer from "@/components/Workbench/DiffViewer.vue";
import WebPreviewFrame from "@/components/Workbench/WebPreviewFrame.vue";

import type { CodeAgentResponse } from "@/types/codeAgent";
import type { ArtifactItem } from "@/types/interaction";
import type { RunResponse } from "@/types/run";
import type { RunEvent } from "@/types/runEvent";

const props = defineProps<{
  runResponse: RunResponse | null;
  codeAgentResponse: CodeAgentResponse | null;
  liveEvents: RunEvent[];
  isJavaMode: boolean;
}>();

const previewDialog = ref<{ visible: boolean; title: string; src: string }>({
  visible: false,
  title: "",
  src: "",
});
const selectedDiff = ref<ArtifactItem | null>(null);
const diffDialogVisible = computed({
  get: () => Boolean(selectedDiff.value),
  set: (visible: boolean) => {
    if (!visible) {
      selectedDiff.value = null;
    }
  },
});
const openingFolder = ref(false);

const platformRunId = computed(() => props.runResponse?.platform_run_id || props.runResponse?.platformRunId || "");
const reportPath = computed(() => props.runResponse?.run_summary?.report_path || props.runResponse?.ui_view_model.report?.report_path || "");

const runArtifacts = computed<ArtifactItem[]>(() => {
  const rows: ArtifactItem[] = [];

  if (platformRunId.value) {
    rows.push({
      id: `replay-${platformRunId.value}`,
      type: "replay",
      title: "Replay 回放",
      subtitle: platformRunId.value,
      path: `/replay/${platformRunId.value}`,
      status: "ready",
    });
  }

  if (reportPath.value) {
    rows.push({
      id: `report-${reportPath.value}`,
      type: "report",
      title: "Markdown 报告",
      subtitle: reportPath.value,
      path: "/reports",
      status: "ready",
    });
  }

  if (props.liveEvents.length) {
    rows.push({
      id: "events",
      type: "audit",
      title: "RunEvent / SSE",
      subtitle: `${props.liveEvents.length} events`,
      status: "ready",
    });
  }

  return rows;
});

const codeDiffArtifacts = computed<ArtifactItem[]>(() => {
  if (!props.codeAgentResponse) {
    return [];
  }

  return props.codeAgentResponse.results.flatMap((result, resultIndex) =>
    (result.changes || []).map((change, changeIndex) => ({
      id: `diff-${resultIndex}-${changeIndex}-${change.filePath}`,
      type: "diff" as const,
      title: change.relativePath || change.filePath,
      subtitle: change.reason || `${change.action} change`,
      path: change.filePath,
      content: change.diff || "",
      status: change.action === "skip" ? "blocked" : "ready",
      meta: {
        before: change.before,
        after: change.after,
      },
    })),
  );
});

const htmlFiles = computed(() => {
  if (!props.codeAgentResponse) {
    return [];
  }

  return props.codeAgentResponse.results
    .flatMap((result) => [
      result.filePath,
      ...(result.files || []),
      ...(result.changes || []).map((change) => change.filePath),
      ...(result.fileTree || []).map((file) => file.filePath),
    ])
    .filter((path): path is string => Boolean(path && path.endsWith(".html")));
});

function openPreview(filePath: string) {
  previewDialog.value = {
    visible: true,
    title: filePath,
    src: getCodeAgentPreviewUrl(filePath),
  };
}

async function openOutputFolder(path = "output") {
  openingFolder.value = true;
  try {
    const response = await openCodeAgentFolder(path);
    if (response.success) {
      ElMessage.success(response.message || "已打开输出文件夹");
    } else {
      ElMessage.error(response.message || "打开输出文件夹失败");
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "打开输出文件夹失败");
  } finally {
    openingFolder.value = false;
  }
}
</script>

<template>
  <aside class="artifact-panel">
    <div class="artifact-head">
      <div>
        <h2>Artifacts</h2>
        <p>文件、diff、审计日志、网页预览、报告和回放集中在这里。</p>
      </div>
      <el-tag :type="isJavaMode ? 'success' : 'info'" effect="plain">
        {{ isJavaMode ? "Java Gateway" : "Python Direct" }}
      </el-tag>
    </div>

    <div class="artifact-section">
      <div class="artifact-section-title">运行产物</div>
      <el-empty v-if="!runArtifacts.length" description="暂无运行产物" :image-size="72" />
      <template v-else>
        <router-link
          v-for="artifact in runArtifacts"
          :key="artifact.id"
          class="artifact-row"
          :to="artifact.path || '#'"
        >
          <span>{{ artifact.title }}</span>
          <small>{{ artifact.subtitle }}</small>
        </router-link>
      </template>
    </div>

    <div class="artifact-section">
      <div class="artifact-section-title">CodeAgent 产物</div>
      <CodeAgentArtifacts :response="codeAgentResponse" />
      <div v-if="htmlFiles.length" class="artifact-actions">
        <el-button v-for="file in htmlFiles.slice(0, 4)" :key="file" size="small" type="primary" plain @click="openPreview(file)">
          预览 {{ file.split("/").pop() }}
        </el-button>
      </div>
      <div v-if="codeDiffArtifacts.length" class="diff-list">
        <button
          v-for="artifact in codeDiffArtifacts.slice(0, 6)"
          :key="artifact.id"
          class="diff-button"
          type="button"
          @click="selectedDiff = artifact"
        >
          <strong>{{ artifact.title }}</strong>
          <span>{{ artifact.subtitle }}</span>
        </button>
      </div>
    </div>

    <div class="artifact-section">
      <div class="artifact-section-title">快捷操作</div>
      <el-button class="full-width" plain :loading="openingFolder" @click="openOutputFolder('output')">
        打开 output 文件夹
      </el-button>
      <el-button class="full-width" plain :loading="openingFolder" @click="openOutputFolder('generated-skills')">
        打开 generated-skills
      </el-button>
    </div>

    <AuditLogPreview :path="codeAgentResponse?.auditPath" />

    <el-dialog v-model="previewDialog.visible" :title="previewDialog.title" width="86%" append-to-body destroy-on-close>
      <WebPreviewFrame :src="previewDialog.src" :title="previewDialog.title" />
    </el-dialog>

    <el-dialog v-model="diffDialogVisible" title="Diff 预览" width="78%" append-to-body destroy-on-close>
      <DiffViewer
        v-if="selectedDiff"
        :title="selectedDiff.title"
        :diff="selectedDiff.content"
        :before="String(selectedDiff.meta?.before || '')"
        :after="String(selectedDiff.meta?.after || '')"
      />
    </el-dialog>
  </aside>
</template>

<style scoped>
.artifact-panel {
  display: grid;
  align-content: start;
  gap: 16px;
  min-width: 0;
}

.artifact-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 18px;
  background:
    radial-gradient(circle at 100% 0%, rgba(77, 163, 255, 0.1), transparent 36%),
    #17191f;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.035),
    0 12px 34px rgba(0, 0, 0, 0.18);
}

.artifact-head h2 {
  margin: 0;
  color: var(--codex-text);
  font-size: 18px;
}

.artifact-head p {
  margin: 6px 0 0;
  color: var(--codex-muted);
  font-size: 13px;
  line-height: 1.5;
}

.artifact-section {
  display: grid;
  gap: 10px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.014)),
    #17191f;
}

.artifact-section-title {
  color: var(--codex-text);
  font-weight: 800;
}

.artifact-row {
  display: grid;
  gap: 3px;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 12px;
  background: #111318;
}

.artifact-row span {
  color: #1a73e8;
  font-weight: 800;
}

.artifact-row small {
  overflow: hidden;
  color: var(--codex-muted);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.artifact-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.diff-list {
  display: grid;
  gap: 8px;
}

.diff-button {
  display: grid;
  gap: 3px;
  width: 100%;
  padding: 10px;
  border: 1px solid rgba(77, 163, 255, 0.18);
  border-radius: 12px;
  background:
    radial-gradient(circle at 100% 0%, rgba(77, 163, 255, 0.1), transparent 42%),
    #111318;
  color: var(--codex-text);
  text-align: left;
  cursor: pointer;
}

.diff-button:hover {
  border-color: #1a73e8;
}

.diff-button strong,
.diff-button span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.diff-button span {
  color: var(--codex-muted);
  font-size: 12px;
}

.full-width + .full-width {
  margin-left: 0;
}
</style>
