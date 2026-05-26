import type { RunEvent } from "./runEvent";

export type CodeAgentOperation =
  | "read_file"
  | "write_file"
  | "list_files"
  | "scan_folder"
  | "read_folder"
  | "plan_folder_changes"
  | "apply_folder_changes"
  | "backup_folder_changes"
  | "export_folder_result";

export type CodeAgentFolderChange = {
  filePath: string;
  relativePath?: string;
  action: "create" | "update" | "skip" | string;
  before?: string;
  after?: string;
  content?: string;
  diff?: string;
  reason?: string;
};

export type CodeAgentFolderTemplate = {
  key: string;
  name: string;
  description: string;
  source: "builtin" | "api" | "platform";
  baseDir: string;
  includePatterns: string;
  excludePatterns: string;
  outputFile: string;
  content: string;
  recursive: boolean;
  dryRun: boolean;
  backupBeforeWrite: boolean;
  recommendedOperation: Extract<
    CodeAgentOperation,
    "scan_folder" | "read_folder" | "plan_folder_changes" | "apply_folder_changes"
  >;
};

export type CodeAgentFolderFile = {
  filePath: string;
  relativePath?: string;
  sizeBytes?: number;
  extension?: string;
  content?: string;
  truncated?: boolean;
};

export type CodeAgentBlockedFile = {
  filePath: string;
  reason: string;
};

export type CodeAgentRequest = {
  operation: CodeAgentOperation;
  filePath: string;
  content?: string;
  recursive?: boolean;
  platformRunId?: string;
  includePatterns?: string[] | string;
  excludePatterns?: string[] | string;
  outputFile?: string;
  dryRun?: boolean;
  backupBeforeWrite?: boolean;
  changes?: CodeAgentFolderChange[];
};

export type CodeAgentOperationResult = {
  success: boolean;
  operation: CodeAgentOperation | string;
  filePath: string;
  message: string;
  content?: string;
  files?: string[];
  fileTree?: CodeAgentFolderFile[];
  folderFiles?: CodeAgentFolderFile[];
  blockedFiles?: CodeAgentBlockedFile[];
  changes?: CodeAgentFolderChange[];
  backups?: Array<{ filePath: string; backupPath: string }>;
  summary?: Record<string, unknown>;
  baseDir?: string;
  dryRun?: boolean;
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
