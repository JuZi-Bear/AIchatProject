export type WorkspaceConfig = {
  id?: number;
  name: string;
  rootPath: string;
  enabled: boolean;
  isDefault: boolean;
  description?: string;
  maxFiles: number;
  maxReadChars: number;
  dryRunDefault: boolean;
  backupBeforeWrite: boolean;
  createdAt?: string;
  updatedAt?: string;
};

export type WorkspaceLimitPolicy = {
  maxFiles: number;
  maxReadChars: number;
  dryRunDefault: boolean;
  backupBeforeWrite: boolean;
};

export type WorkspaceSafetyStatus = {
  mode: "configured" | "outside" | "disabled" | "unavailable" | "python-direct";
  workspace?: WorkspaceConfig;
  message: string;
  type: "success" | "warning" | "danger" | "info";
};

export function createDefaultWorkspace(): WorkspaceConfig {
  return {
    name: "CodeAgent Demo Workspace",
    rootPath: "output/code_agent_workspace",
    enabled: true,
    isDefault: true,
    description: "默认受控文件夹工作区。用于 CodeAgent dry-run、diff 预览、审计日志和回放演示。",
    maxFiles: 80,
    maxReadChars: 500000,
    dryRunDefault: true,
    backupBeforeWrite: true,
  };
}
