export type HealthResponse = {
  status: string;
  service: string;
  version: string;
};

export type ApiResponse<T> = {
  success: boolean;
  message: string;
  data: T;
};

export type { ModelConfig } from "./model";
export type { PlatformRunRecord, PlatformStats, RawPlatformRunResponse } from "./platformRun";
export type { PluginConfig } from "./plugin";
export type { FrontendSettings } from "./settings";
export type { RunEvent } from "./runEvent";
export type { InstantiateWorkflowRequest, InstantiateWorkflowResponse, WorkflowTemplate } from "./workflow";
export type { AgentNodeData, ConnectionData, WorkflowEditorState, WorkflowTemplateData } from "./workflowEditor";
export type { CodeAgentOperation, CodeAgentOperationResult, CodeAgentRequest, CodeAgentResponse } from "./codeAgent";
export type {
  DemoCase,
  DemoCaseKey,
  DemoNarration,
  DemoRunState,
  DemoStage,
  DemoStageStatus,
} from "./demo";

export type {
  AgentOutputs,
  PluginOutputs,
  PluginResult,
  ReportViewModel,
  ReportDetail,
  ReportItem,
  RunHistoryItem,
  RunRequest,
  RunResponse,
  RunSummary,
  UIViewModel,
  WorkflowStep,
} from "./run";

export type ReportListItem = {
  name: string;
  path: string;
  size: number;
  modified_time: string;
};

export type ReportContent = {
  name: string;
  path: string;
  content: string;
};
