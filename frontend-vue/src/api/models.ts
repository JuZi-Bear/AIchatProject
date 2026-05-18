import { apiClient } from "./client";

import type { ModelConfig } from "@/types/model";

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
