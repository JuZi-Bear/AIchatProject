export type HealthResponse = {
  status: string;
  service: string;
  version: string;
};

export type { ModelConfig } from "./model";
export type { PluginConfig } from "./plugin";
export type { FrontendSettings } from "./settings";
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
