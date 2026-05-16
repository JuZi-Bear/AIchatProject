export type RunSummary = {
  run_id?: string;
  requirement?: string;
  success: boolean;
  retry_count: number;
  test_success: boolean;
  coverage_percent: number;
  quality_score: number;
  security_status: string;
  enabled_plugins: string[];
  model_provider: string;
  model_name?: string;
  report_path: string;
  state_path?: string;
};

export type WorkflowStep = {
  key: string;
  label: string;
  status: "waiting" | "running" | "done" | "failed" | "repairing" | "skipped" | string;
  summary: string;
  order: number;
};

export type PluginResult = {
  plugin_name?: string;
  name?: string;
  status?: "success" | "warning" | "failed" | "disabled" | string;
  summary?: string;
  detail?: string;
};

export type AgentOutputs = {
  product_result?: string;
  code?: string;
  tester_result?: string;
  sentry_result?: string;
  stdout?: string;
  error_summary?: string;
  error_log?: string;
};

export type PluginOutputs = {
  plugin_results?: PluginResult[];
  doc_result?: string;
  security_result?: string;
  refactor_result?: string;
  ui_result?: string;
  [key: string]: unknown;
};

export type ReportViewModel = {
  report_path?: string;
  report_markdown?: string;
  run_id?: string;
};

export type UIViewModel = {
  header?: Record<string, unknown>;
  summary_cards?: Partial<RunSummary> & Record<string, unknown>;
  workflow_steps?: WorkflowStep[];
  agent_outputs?: AgentOutputs;
  plugin_outputs?: PluginOutputs;
  report?: ReportViewModel;
  result_index?: Record<string, unknown>;
  raw?: Record<string, unknown>;
};

export type RunResponse = {
  run_id: string;
  state?: Record<string, unknown>;
  run_summary: RunSummary;
  ui_view_model: UIViewModel;
};

export type RunHistoryItem = {
  run_id: string;
  run_summary?: RunSummary;
  success: boolean;
  retry_count: number;
  test_success: boolean;
  coverage_percent: number;
  quality_score: number;
  model_provider: string;
  model_name: string;
  requirement: string;
  created_at: string;
  report_path: string;
  state_path: string;
};

export type ReportItem = {
  report_name: string;
  name: string;
  path: string;
  created_at: string;
  modified_time?: string;
  file_size?: number;
  size?: number;
  run_id?: string;
};

export type ReportDetail = {
  report_name: string;
  name: string;
  path: string;
  content: string;
  run_id?: string;
};

export type RunRequest = {
  requirement: string;
  model_provider: string;
  enabled_plugins: string[];
  max_retry_count: number;
  require_human_approval: boolean;
  demo_mode: boolean;
  offline_mode: boolean;
};
