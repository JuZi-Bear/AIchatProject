import type { RunSummary, UIViewModel } from "./run";

export type WorkflowTemplate = {
  key: string;
  name: string;
  description: string;
  agent_sequence: string[];
  stage_sequence: string[];
  enabled: boolean;
  version: string;
  md_path?: string;
  markdown?: string;
};

export type InstantiateWorkflowRequest = {
  template_key: string;
  input_data: Record<string, unknown>;
  template_data?: Record<string, unknown>;
};

export type InstantiateWorkflowResponse = {
  platformRunId: string;
  platform_run_id?: string;
  run_id?: string;
  template_key: string;
  input_data: Record<string, unknown>;
  workflow_events: Array<Record<string, unknown>>;
  run_summary: Partial<RunSummary> & Record<string, unknown>;
  ui_view_model: UIViewModel & Record<string, unknown>;
};

export type WorkflowRuntimeNodeEvent = {
  event_type?: string;
  event_text?: string;
  agent?: string;
  status?: string;
  message?: string;
  detail?: Record<string, unknown> | unknown;
  created_at?: string;
} & Record<string, unknown>;

export type RuntimeNodeExecutionMode = "executed" | "simulated" | "waiting";

export type WorkflowRuntimeSummary = {
  mode?: string;
  node_counts?: {
    executed?: number;
    simulated?: number;
    waiting?: number;
  };
  code_agent?: Record<string, unknown>;
  report_path?: string;
  connection_mappings?: Array<Record<string, unknown>>;
};

export type WorkflowRuntimeExecutionResult = InstantiateWorkflowResponse & {
  status?: string;
  events?: WorkflowRuntimeNodeEvent[];
  warnings?: string[];
  validation_result?: DynamicLangGraphValidationResult;
};

export type DynamicLangGraphValidationResult = {
  valid: boolean;
  errors: Array<Record<string, unknown>>;
  warnings: Array<Record<string, unknown>>;
  issues: Array<Record<string, unknown>>;
  node_count?: number;
  edge_count?: number;
  template_key?: string;
};

export type DynamicLangGraphExecutionResult = WorkflowRuntimeExecutionResult & {
  validation_result?: DynamicLangGraphValidationResult;
};

export type WorkflowSkillExportResult = {
  templateKey: string;
  skillName: string;
  skillPath: string;
  files: string[];
  installed: false;
  warnings: string[];
};
