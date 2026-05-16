import { apiClient } from "./client";

import type { ModelConfig } from "@/types/model";

function normalizeApiError(error: unknown) {
  const message = error instanceof Error ? error.message : "加载模型配置失败";
  return new Error(message);
}

export function getModels(): Promise<ModelConfig[]> {
  return apiClient
    .get<ModelConfig[]>("/models")
    .then((response) => response.data)
    .catch((error) => {
      throw normalizeApiError(error);
    });
}
