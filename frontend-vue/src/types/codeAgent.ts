import type { RunEvent } from "./runEvent";

export type CodeAgentOperation = "read_file" | "write_file" | "list_files";

export type CodeAgentRequest = {
  operation: CodeAgentOperation;
  filePath: string;
  content?: string;
  recursive?: boolean;
  platformRunId?: string;
};

export type CodeAgentOperationResult = {
  success: boolean;
  operation: CodeAgentOperation | string;
  filePath: string;
  message: string;
  content?: string;
  files?: string[];
  auditPath?: string;
  truncated?: boolean;
  events?: RunEvent[];
};

export type CodeAgentResponse = {
  success: boolean;
  agent: string;
  operation: CodeAgentOperation | "batch" | string;
  filePath: string;
  message: string;
  auditPath?: string;
  platformRunId?: string;
  results: CodeAgentOperationResult[];
  events: RunEvent[];
};
