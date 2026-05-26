import { apiClient, currentApiMode } from "./client";

import type { ApiResponse } from "@/types/api";
import type { ModelConfig, ModelSecretStatus } from "@/types/model";

type RawModelConfig = ModelConfig & {
  baseUrl?: string;
  envKey?: string;
  defaultModel?: boolean;
  apiKeyConfigured?: boolean;
};

function normalizeApiError(error: unknown) {
  const message = error instanceof Error ? error.message : "加载模型配置失败";
  return new Error(message);
}

function normalizeModel(model: RawModelConfig): ModelConfig {
  return {
    ...model,
    base_url: model.base_url || model.baseUrl || "",
    env_key: model.env_key || model.envKey || "",
    enabled: Boolean(model.enabled),
    is_default: Boolean(model.is_default ?? model.defaultModel ?? model.default),
    default: Boolean(model.default ?? model.defaultModel ?? model.is_default),
    api_key_configured: model.api_key_configured ?? model.apiKeyConfigured,
  };
}

export function getModels(): Promise<ModelConfig[]> {
  return apiClient
    .get<RawModelConfig[]>("/models")
    .then((response) => response.data.map(normalizeModel))
    .catch((error) => {
      throw normalizeApiError(error);
    });
}

function unwrapApiResponse<T>(response: ApiResponse<T>): T {
  if (!response.success) {
    throw new Error(response.message || "Java platform request failed");
  }

  return response.data;
}

function normalizeSecretStatus(status: Partial<ModelSecretStatus>): ModelSecretStatus {
  return {
    provider: status.provider || "",
    name: status.name || status.provider || "",
    envKey: status.envKey || "",
    configured: Boolean(status.configured),
    stored: Boolean(status.stored),
    envConfigured: Boolean(status.envConfigured),
    maskedKey: status.maskedKey || "",
    updatedAt: status.updatedAt || "",
    message: status.message || "",
  };
}

export function getModelSecrets(): Promise<ModelSecretStatus[]> {
  if (currentApiMode !== "java") {
    return Promise.resolve([]);
  }

  return apiClient
    .get<ApiResponse<Partial<ModelSecretStatus>[]>>("/platform/secrets/models")
    .then((response) => unwrapApiResponse(response.data).map(normalizeSecretStatus));
}

export function updateModelSecret(provider: string, apiKey: string): Promise<ModelSecretStatus> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("API Key 管理仅 Java Gateway 模式支持"));
  }

  return apiClient
    .post<ApiResponse<Partial<ModelSecretStatus>>>(`/platform/secrets/models/${provider}`, { apiKey })
    .then((response) => normalizeSecretStatus(unwrapApiResponse(response.data)));
}

export function clearModelSecret(provider: string): Promise<ModelSecretStatus> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("API Key 管理仅 Java Gateway 模式支持"));
  }

  return apiClient
    .delete<ApiResponse<Partial<ModelSecretStatus>>>(`/platform/secrets/models/${provider}`)
    .then((response) => normalizeSecretStatus(unwrapApiResponse(response.data)));
}
