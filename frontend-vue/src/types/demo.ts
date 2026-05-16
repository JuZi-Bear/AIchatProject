import type { RunResponse } from "./run";

export type DemoCaseKey = "simple_success" | "auto_repair" | "comprehensive" | "custom";

export type DemoCase = {
  key: DemoCaseKey;
  label: string;
  description: string;
  requirement: string;
};

export type DemoStageStatus = "waiting" | "running" | "done" | "failed" | "repairing" | "skipped";

export type DemoStage = {
  key: string;
  label: string;
  summary: string;
  status: DemoStageStatus;
  order: number;
};

export type DemoNarration = {
  items: string[];
};

export type DemoRunState = {
  running: boolean;
  errorDetail?: string;
  response?: RunResponse | null;
};
