export type CodexNavItem = {
  path: string;
  label: string;
  iconKey: LocalIconKey;
  badge?: string | number;
};

export type CodexTranscriptRole = "user" | "assistant" | "tool" | "result" | "error" | "system";

export type CodexTranscriptItem = {
  id: string;
  role: CodexTranscriptRole;
  title: string;
  content?: string;
  timestamp?: string;
  status?: "idle" | "running" | "success" | "failed" | "blocked" | "waiting";
  toolCall?: CodexToolCall;
  artifacts?: CodexArtifact[];
};

export type CodexToolCall = {
  toolName: string;
  operation: string;
  status: "queued" | "running" | "success" | "failed" | "blocked";
  summary?: string;
  detailJson?: string;
};

export type CodexArtifact = {
  id: string;
  type: "file" | "diff" | "audit" | "preview" | "report" | "replay" | "skill";
  title: string;
  path?: string;
  url?: string;
  description?: string;
};

export type CodexSidePanel = "workspace" | "tools" | "output" | "events" | "settings" | null;

export type ComposerSubmitMode =
  | "code_agent_ai_generate"
  | "folder_workflow"
  | "agent_run"
  | "runtime_lite"
  | "dynamic_langgraph";

export type LocalIconKey =
  | "dashboard"
  | "run"
  | "workflow"
  | "editor"
  | "artifacts"
  | "history"
  | "models"
  | "workspace"
  | "plugins"
  | "agents"
  | "settings"
  | "search"
  | "new";
