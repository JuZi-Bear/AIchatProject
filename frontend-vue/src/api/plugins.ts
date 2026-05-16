import { apiClient } from "./client";

import type { PluginConfig } from "@/types/plugin";

function normalizeApiError(error: unknown) {
  const message = error instanceof Error ? error.message : "加载插件配置失败";
  return new Error(message);
}

export function getPlugins(): Promise<PluginConfig[]> {
  return apiClient
    .get<PluginConfig[]>("/plugins")
    .then((response) => response.data)
    .catch((error) => {
      throw normalizeApiError(error);
    });
}
