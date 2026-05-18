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
