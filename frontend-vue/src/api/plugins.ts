import { apiClient } from "./client";

import type { PluginConfig } from "@/types/plugin";

type RawPluginConfig = PluginConfig & {
  pluginName?: string;
  displayName?: string;
  latestResult?: PluginConfig["latest_result"];
};

function normalizeApiError(error: unknown) {
  const message = error instanceof Error ? error.message : "加载插件配置失败";
  return new Error(message);
}

function normalizePlugin(plugin: RawPluginConfig): PluginConfig {
  const name = plugin.name || plugin.pluginName || "";
  const displayName = plugin.display_name || plugin.displayName || name;

  return {
    ...plugin,
    name,
    display_name: displayName,
    description: plugin.description || "暂无说明",
    enabled: Boolean(plugin.enabled),
    latest_result: plugin.latest_result || plugin.latestResult,
  };
}

export function getPlugins(): Promise<PluginConfig[]> {
  return apiClient
    .get<RawPluginConfig[]>("/plugins")
    .then((response) => response.data.map(normalizePlugin))
    .catch((error) => {
      throw normalizeApiError(error);
    });
}
