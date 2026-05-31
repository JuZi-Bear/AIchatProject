import type { CodeAgentFolderTemplate, CodeAgentResponse } from "./codeAgent";
import type { RunResponse } from "./run";
import type { RunEvent } from "./runEvent";
import type { WorkspaceSafetyStatus } from "./workspace";
import type { WorkflowTemplateData } from "./workflowEditor";

export type ArtifactType = "file" | "diff" | "audit" | "preview" | "report" | "replay" | "skill";

export type ArtifactItem = {
  id: string;
  type: ArtifactType;
  title: string;
  subtitle?: string;
  path?: string;
  status?: "ready" | "running" | "blocked" | "failed" | "empty";
  content?: string;
  meta?: Record<string, unknown>;
};

export type TimelineItem = {
  id: string;
  kind: "user" | "system" | "tool" | "event" | "result" | "error";
  title: string;
  message?: string;
  status?: string;
  agent?: string;
  timestamp?: string;
  artifactIds?: string[];
  meta?: Record<string, unknown>;
};

export type ToolInvocation = {
  id: string;
  tool: "workflow" | "code_agent" | "dynamic_workflow" | "skill_export";
  title: string;
  status: "idle" | "running" | "success" | "failed" | "waiting";
  startedAt?: string;
  finishedAt?: string;
  request?: Record<string, unknown>;
  response?: RunResponse | CodeAgentResponse | Record<string, unknown>;
  events?: RunEvent[];
};

export type InteractionSession = {
  id: string;
  title: string;
  requirement: string;
  status: "idle" | "running" | "success" | "failed" | "waiting";
  timeline: TimelineItem[];
  artifacts: ArtifactItem[];
  toolInvocations: ToolInvocation[];
};

export type ComposerDraft = {
  text: string;
  mode: "workflow" | "code_agent";
  demoMode: boolean;
};

export type ComposerPrimaryMode = "code_agent_ai_generate" | "folder_workflow" | "agent_run";

export type FolderWorkflowRunMode =
  | ComposerPrimaryMode
  | "runtime_lite"
  | "dynamic_langgraph";

export type WorkspaceDefaultPolicy = {
  includePatterns: string;
  excludePatterns: string;
  outputFile: string;
  dryRunDefault: boolean;
  backupBeforeWrite: boolean;
};

export type FolderWorkflowContext = {
  runMode: FolderWorkflowRunMode;
  workspaceId: number | null;
  folderPath: string;
  folderTemplateKey: string;
  platformTemplateKey: string;
  modelProvider: string;
  outputFile: string;
  includePatterns: string;
  excludePatterns: string;
  recursive: boolean;
  dryRun: boolean;
  backupBeforeWrite: boolean;
  safety: WorkspaceSafetyStatus;
};

export type FolderWorkflowTemplateSelection = {
  folderTemplates: CodeAgentFolderTemplate[];
  platformTemplates: WorkflowTemplateData[];
};

export type ConversationMessage = {
  id: string;
  role: "user" | "assistant" | "tool" | "system";
  title: string;
  content: string;
  status?: "idle" | "running" | "success" | "failed" | "waiting" | "blocked";
  timestamp?: string;
  meta?: Record<string, unknown>;
};

export type ToolInvocationItem = {
  id: string;
  name: string;
  mode: FolderWorkflowRunMode | "code_agent";
  status: "running" | "success" | "failed" | "waiting";
  summary: string;
  artifacts?: ArtifactItem[];
};

export type ToolTranscriptItem = {
  id: string;
  title: string;
  tool: "scan" | "generate" | "plan" | "apply" | "audit" | "runtime";
  status: "queued" | "running" | "success" | "failed" | "blocked";
  summary: string;
};

export type LocalIconKey =
  | "settings"
  | "workspace"
  | "tools"
  | "output"
  | "events"
  | "scan"
  | "markdown"
  | "diff"
  | "apply"
  | "blocked"
  | "fallback";

export type WorkspaceNavigationItem = {
  id: number | string;
  name: string;
  rootPath: string;
  isDefault?: boolean;
  enabled?: boolean;
  status?: "active" | "disabled" | "outside" | "python-direct";
};

export type WorkspaceAction = "scan" | "markdown_summary" | "dry_run_diff" | "apply" | "blocked_check";

export type WorkspacePanelMode = "settings" | "actions";

export type WorkspaceExtendedSettings = {
  includePatterns: string;
  excludePatterns: string;
  outputFile: string;
  maxFiles: number;
  maxReadChars: number;
  dryRunDefault: boolean;
  backupBeforeWrite: boolean;
};

export type WorkbenchSidePanelName = "workspace" | "settings" | "builder" | "tools" | "output" | "events";
