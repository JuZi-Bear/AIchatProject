import type { RunEvent } from "./runEvent";
import type { RunResponse } from "./run";

export type RequirementBuilderState = {
  goal: string;
  constraints: string;
  acceptanceCriteria: string;
  targetFiles: string;
  outputPreference: string;
  useCodeAgent: boolean;
  codeAgentOperation: string;
};

export type RequirementTemplate = {
  key: string;
  label: string;
  description: string;
  state: RequirementBuilderState;
};

export type OutputShortcutLink = {
  label: string;
  path: string;
  disabled?: boolean;
};

export type RunResultHighlight = {
  response?: RunResponse | null;
  requirement?: string;
  liveEvents?: RunEvent[];
  isJavaMode?: boolean;
  running?: boolean;
  errorDetail?: string;
};
