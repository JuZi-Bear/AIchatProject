import { apiClient, currentApiMode } from "./client";

import type { ApiResponse } from "@/types/api";
import type { WorkspaceConfig } from "@/types/workspace";

function ensureJavaMode() {
  if (currentApiMode !== "java") {
    throw new Error("Workspace 配置仅 Java Gateway + MySQL 模式支持");
  }
}

function unwrapWorkspaceResponse<T>(response: ApiResponse<T>): T {
  if (!response.success) {
    throw new Error(response.message || "Workspace request failed");
  }

  return response.data;
}

export function getWorkspaces(): Promise<WorkspaceConfig[]> {
  ensureJavaMode();
  return apiClient
    .get<ApiResponse<WorkspaceConfig[]>>("/platform/workspaces")
    .then((response) => unwrapWorkspaceResponse(response.data));
}

export function createWorkspace(payload: WorkspaceConfig): Promise<WorkspaceConfig> {
  ensureJavaMode();
  return apiClient
    .post<ApiResponse<WorkspaceConfig>>("/platform/workspaces", payload)
    .then((response) => unwrapWorkspaceResponse(response.data));
}

export function updateWorkspace(id: number, payload: WorkspaceConfig): Promise<WorkspaceConfig> {
  ensureJavaMode();
  return apiClient
    .put<ApiResponse<WorkspaceConfig>>(`/platform/workspaces/${id}`, payload)
    .then((response) => unwrapWorkspaceResponse(response.data));
}

export function deleteWorkspace(id: number): Promise<WorkspaceConfig> {
  ensureJavaMode();
  return apiClient
    .delete<ApiResponse<WorkspaceConfig>>(`/platform/workspaces/${id}`)
    .then((response) => unwrapWorkspaceResponse(response.data));
}
