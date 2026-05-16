<script setup lang="ts">
import type { ReportViewModel } from "@/types/run";

defineProps<{
  report?: ReportViewModel;
}>();
</script>

<template>
  <div class="report-preview">
    <el-descriptions :column="1" border>
      <el-descriptions-item label="report_path">
        {{ report?.report_path || "暂无报告" }}
      </el-descriptions-item>
    </el-descriptions>

    <el-empty v-if="!report?.report_markdown" description="暂无报告" />
    <el-collapse v-else class="report-collapse">
      <el-collapse-item title="完整 Markdown 报告" name="report">
        <pre class="report-markdown">{{ report.report_markdown }}</pre>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<style scoped>
.report-preview {
  display: grid;
  gap: 12px;
}

.report-collapse {
  border-top: 0;
}

.report-markdown {
  max-height: 560px;
  margin: 0;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: #0f172a;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 13px;
  line-height: 1.65;
}
</style>
