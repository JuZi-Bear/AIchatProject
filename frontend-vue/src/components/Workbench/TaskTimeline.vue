<script setup lang="ts">
import { computed } from "vue";

import type { CodeAgentResponse } from "@/types/codeAgent";
import type { FolderWorkflowContext } from "@/types/interaction";
import type { RunResponse } from "@/types/run";
import type { RunEvent } from "@/types/runEvent";

const props = defineProps<{
  requirement: string;
  folderContext: FolderWorkflowContext;
  templateName: string;
  running: boolean;
  errorDetail: string;
  response: RunResponse | null;
  liveEvents: RunEvent[];
  codeAgentResponse: CodeAgentResponse | null;
}>();

type TimelineRow = {
  id: string;
  type: "user" | "system" | "tool" | "event" | "result" | "error";
  title: string;
  message: string;
  tag?: string;
  status?: string;
  timestamp?: string;
};

function eventLabel(event: RunEvent) {
  return event.eventText || event.eventType || "运行事件";
}

function rowTone(type: TimelineRow["type"], status = "") {
  if (type === "error" || /FAILED|ERROR|阻断|失败/i.test(status)) {
    return "danger";
  }

  if (type === "result" || /SUCCESS|FINISHED|完成/i.test(status)) {
    return "success";
  }

  if (type === "tool") {
    return "warning";
  }

  if (type === "event") {
    return "primary";
  }

  return "info";
}

const rows = computed<TimelineRow[]>(() => {
  const isAiGenerate = props.folderContext.runMode === "code_agent_ai_generate";
  const resultRows: TimelineRow[] = [
    {
      id: "workspace-context",
      type: "system",
      title: "Workspace context",
      message:
        props.folderContext.runMode === "agent_run"
          ? `普通 Agent 运行，model=${props.folderContext.modelProvider || "default"}`
          : isAiGenerate
            ? `folder=${props.folderContext.folderPath || "未选择"} · mode=CodeAgent AI 一键生成 · audit=on · workspace safety=${props.folderContext.safety.mode}`
            : `folder=${props.folderContext.folderPath || "未选择"} · template=${props.templateName || "未选择"} · ${props.folderContext.dryRun ? "dry-run 预览" : "write 应用"} · ${props.folderContext.backupBeforeWrite ? "写入前备份" : "不备份"}`,
      tag: props.folderContext.runMode,
      status: props.folderContext.safety.mode.toUpperCase(),
    },
    {
      id: "user-requirement",
      type: "user",
      title: "User request",
      message: props.requirement || "选择 Workspace 后，在底部输入你想生成或改造的项目目标。",
      tag: "input",
    },
  ];

  if (!props.response && !props.codeAgentResponse && !props.liveEvents.length && !props.errorDetail) {
    resultRows.push({
      id: "default-plan",
      type: "system",
      title: "Default CodeAgent plan",
      message: isAiGenerate
        ? "默认将执行：读取 Workspace 上下文 → AI 生成项目文件 → 写入受控目录 → 记录审计 → 输出预览入口。"
        : "默认将执行：扫描文件夹 → 生成 dry-run 计划和 diff → 写入前备份 → 输出 Markdown 和审计。",
      tag: isAiGenerate ? "ai-generate" : "folder-workflow",
      status: "READY",
    });
  }

  if (props.running) {
    resultRows.push({
      id: "running",
      type: "system",
      title: "AI workflow is running",
      message: "正在等待后端返回运行结果，Java 模式下会继续接收 SSE 事件。",
      tag: "running",
      status: "RUNNING",
    });
  }

  if (props.errorDetail) {
    resultRows.push({
      id: "error",
      type: "error",
      title: "Run failed",
      message: props.errorDetail,
      tag: "error",
      status: "FAILED",
    });
  }

  if (props.codeAgentResponse) {
    const aiGenerateResult = props.codeAgentResponse.operation.includes("generate") || isAiGenerate;
    const folderResult = props.codeAgentResponse.results.find(
      (item) =>
        String(item.operation).includes("folder") ||
        Boolean(item.fileTree?.length) ||
        Boolean(item.changes?.length) ||
        Boolean(item.blockedFiles?.length),
    );

    resultRows.push({
      id: `code-agent-${props.codeAgentResponse.platformRunId || props.codeAgentResponse.operation}`,
      type: "tool",
      title: aiGenerateResult ? "CodeAgent AI generation" : "CodeAgent tool invocation",
      message: aiGenerateResult
        ? `AI 一键生成完成：files=${props.codeAgentResponse.results.filter((item) => item.filePath).length}, audit=${props.codeAgentResponse.auditPath || folderResult?.auditPath || "none"}`
        : folderResult
        ? `文件夹操作完成：files=${folderResult.fileTree?.length || folderResult.folderFiles?.length || 0}, changes=${folderResult.changes?.length || 0}, blocked=${folderResult.blockedFiles?.length || 0}, audit=${folderResult.auditPath || props.codeAgentResponse.auditPath || "none"}`
        : props.codeAgentResponse.message || "CodeAgent 文件操作完成",
      tag: props.codeAgentResponse.operation,
      status: props.codeAgentResponse.success ? "SUCCESS" : "FAILED",
    });

    if (folderResult?.changes?.length) {
      resultRows.push({
        id: "folder-changes",
        type: "result",
        title: props.folderContext.dryRun ? "Planned file changes" : "Applied file changes",
        message: `${folderResult.changes.length} 个文件变更，${props.folderContext.dryRun ? "当前为预览计划，尚未写入文件。" : "已应用到受控文件夹并记录审计日志。"}`,
        tag: props.folderContext.dryRun ? "dry-run" : "write",
        status: "SUCCESS",
      });
    }

    if (folderResult?.blockedFiles?.length) {
      resultRows.push({
        id: "folder-blocked",
        type: "error",
        title: "Blocked paths",
        message: `${folderResult.blockedFiles.length} 个路径被安全策略阻断。`,
        tag: "blocked",
        status: "FAILED",
      });
    }
  }

  props.liveEvents.forEach((event, index) => {
    resultRows.push({
      id: `event-${event.id || index}-${event.createdAt}`,
      type: "event",
      title: eventLabel(event),
      message: event.message || event.detailJson || "无事件描述",
      tag: event.agent || event.eventType,
      status: event.status || event.eventType,
      timestamp: event.createdAt,
    });
  });

  if (props.response) {
    const summary = props.response.run_summary;
    resultRows.push({
      id: "result-summary",
      type: "result",
      title: summary?.success ? "Workflow completed" : "Workflow finished with issues",
      message: `quality=${summary?.quality_score ?? 0}, retry=${summary?.retry_count ?? 0}, report=${summary?.report_path || "none"}`,
      tag: "result",
      status: summary?.success ? "SUCCESS" : "FAILED",
    });
  }

  return resultRows;
});
</script>

<template>
  <section class="task-timeline">
    <div class="timeline-head">
      <div>
        <h2>任务会话</h2>
        <p>像 Codex 一样，把输入、工具调用、事件和结果放在一条执行流里。</p>
      </div>
      <el-tag effect="plain">{{ rows.length }} items</el-tag>
    </div>

    <div class="timeline-list">
      <article v-for="row in rows" :key="row.id" class="timeline-row" :class="`row-${row.type}`">
        <div class="timeline-rail">
          <span :class="`dot dot-${rowTone(row.type, row.status)}`" />
        </div>
        <div class="timeline-card">
          <div class="timeline-card-head">
            <strong>{{ row.title }}</strong>
            <div class="timeline-tags">
              <el-tag v-if="row.tag" :type="rowTone(row.type, row.status)" effect="plain" size="small">
                {{ row.tag }}
              </el-tag>
              <el-tag v-if="row.status" effect="plain" size="small">{{ row.status }}</el-tag>
            </div>
          </div>
          <p>{{ row.message }}</p>
          <small v-if="row.timestamp">{{ row.timestamp }}</small>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.task-timeline {
  display: grid;
  align-content: start;
  gap: 14px;
  min-height: 0;
}

.timeline-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.timeline-head h2 {
  margin: 0;
  color: #f4f4f5;
  font-size: 20px;
}

.timeline-head p {
  margin: 6px 0 0;
  color: #a1a1aa;
  line-height: 1.5;
}

.timeline-list {
  display: grid;
  gap: 10px;
}

.timeline-row {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 8px;
}

.timeline-rail {
  position: relative;
  display: flex;
  justify-content: center;
}

.timeline-rail::after {
  position: absolute;
  top: 18px;
  bottom: -18px;
  width: 2px;
  border-radius: 999px;
  background: #343741;
  content: "";
}

.timeline-row:last-child .timeline-rail::after {
  display: none;
}

.dot {
  z-index: 1;
  width: 12px;
  height: 12px;
  margin-top: 14px;
  border: 3px solid #0f1115;
  border-radius: 999px;
  background: #5f6368;
  box-shadow: 0 0 0 1px #343741;
}

.dot-primary {
  background: #1a73e8;
}

.dot-success {
  background: #34a853;
}

.dot-warning {
  background: #fbbc04;
}

.dot-danger {
  background: #ea4335;
}

.timeline-card {
  display: grid;
  gap: 8px;
  padding: 14px;
  border: 1px solid #343741;
  border-radius: 16px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent 44%),
    #17191f;
  box-shadow: none;
}

.timeline-card-head,
.timeline-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.timeline-card-head {
  justify-content: space-between;
}

.timeline-card strong {
  color: #f4f4f5;
}

.timeline-card p {
  margin: 0;
  color: #d4d4d8;
  line-height: 1.58;
  overflow-wrap: anywhere;
}

.timeline-card small {
  color: #a1a1aa;
}

.row-user .timeline-card {
  border-color: rgba(77, 163, 255, 0.5);
  background: #151c27;
}

.row-tool .timeline-card {
  border-color: rgba(250, 204, 21, 0.45);
  background: #1f1d16;
}

.row-result .timeline-card {
  border-color: rgba(74, 222, 128, 0.42);
  background: #132018;
}

.row-error .timeline-card {
  border-color: rgba(251, 113, 133, 0.55);
  background: #22161a;
}

.task-timeline :deep(.el-tag) {
  border-color: #343741;
  background: #22252d;
  color: #d4d4d8;
}
</style>
