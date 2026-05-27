type RunKindSource = {
  runner_mode?: string;
  runnerMode?: string;
  model_provider?: string;
  modelProvider?: string;
  run_id?: string;
  platform_run_id?: string;
  platformRunId?: string;
};

function normalized(value?: string) {
  return (value || "").trim().toLowerCase();
}

function runIdOf(run?: RunKindSource | null) {
  return normalized(run?.platformRunId || run?.platform_run_id || run?.run_id);
}

export function isWorkflowTemplateRun(run?: RunKindSource | null) {
  const runnerMode = normalized(run?.runnerMode || run?.runner_mode);
  const modelProvider = normalized(run?.modelProvider || run?.model_provider);
  const runId = runIdOf(run);

  return runnerMode === "workflow_template" || modelProvider === "workflow_template" || runId.startsWith("workflow_template_");
}

export function isWorkflowRuntimeRun(run?: RunKindSource | null) {
  const runnerMode = normalized(run?.runnerMode || run?.runner_mode);
  const modelProvider = normalized(run?.modelProvider || run?.model_provider);
  const runId = runIdOf(run);

  return runnerMode === "workflow_runtime" || modelProvider === "workflow_runtime" || runId.startsWith("workflow_runtime_");
}

export function isCodeAgentRun(run?: RunKindSource | null) {
  const runnerMode = normalized(run?.runnerMode || run?.runner_mode);
  const modelProvider = normalized(run?.modelProvider || run?.model_provider);
  const runId = runIdOf(run);

  return runnerMode === "code_agent" || modelProvider === "code_agent" || runId.startsWith("code_agent");
}

export function runKindLabel(run?: RunKindSource | null) {
  if (isWorkflowRuntimeRun(run)) {
    return "模板执行";
  }

  if (isWorkflowTemplateRun(run)) {
    return "模板回放";
  }

  if (isCodeAgentRun(run)) {
    return "CodeAgent";
  }

  return "Agent 运行";
}

export function runKindTagType(run?: RunKindSource | null) {
  if (isWorkflowRuntimeRun(run)) {
    return "success";
  }

  if (isWorkflowTemplateRun(run)) {
    return "primary";
  }

  if (isCodeAgentRun(run)) {
    return "warning";
  }

  return "info";
}

export function runnerDisplayLabel(runnerMode?: string) {
  if (runnerMode === "cpp") {
    return "C++ Sandbox Runner";
  }

  if (runnerMode === "code_agent") {
    return "Simple CodeAgent";
  }

  if (runnerMode === "workflow_template") {
    return "Workflow Template Replay";
  }

  if (runnerMode === "workflow_runtime") {
    return "Workflow Runtime Lite";
  }

  return "Python Runner";
}

export function runnerTagType(runnerMode?: string) {
  if (runnerMode === "cpp") {
    return "success";
  }

  if (runnerMode === "code_agent") {
    return "warning";
  }

  if (runnerMode === "workflow_template") {
    return "primary";
  }

  if (runnerMode === "workflow_runtime") {
    return "success";
  }

  return "info";
}
