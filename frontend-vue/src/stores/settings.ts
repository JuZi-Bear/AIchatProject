import { defineStore } from "pinia";

import type { FrontendSettings } from "@/types/settings";

const STORAGE_KEY = "ai-agent-pipeline.frontend-settings";

const defaultSettings: FrontendSettings = {
  selectedModelProvider: "deepseek",
  enabledPlugins: [],
  demoMode: true,
  maxRetryCount: 3,
  requireHumanApproval: false,
  offlineMode: false,
};

function readStoredSettings(): FrontendSettings {
  try {
    const rawValue = localStorage.getItem(STORAGE_KEY);

    if (!rawValue) {
      return { ...defaultSettings };
    }

    const parsed = JSON.parse(rawValue) as Partial<FrontendSettings>;

    return {
      ...defaultSettings,
      ...parsed,
      enabledPlugins: Array.isArray(parsed.enabledPlugins) ? parsed.enabledPlugins : [],
      maxRetryCount: Number(parsed.maxRetryCount ?? defaultSettings.maxRetryCount),
    };
  } catch {
    return { ...defaultSettings };
  }
}

export const useSettingsStore = defineStore("settings", {
  state: (): FrontendSettings => readStoredSettings(),
  actions: {
    persist() {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          selectedModelProvider: this.selectedModelProvider,
          enabledPlugins: this.enabledPlugins,
          demoMode: this.demoMode,
          maxRetryCount: this.maxRetryCount,
          requireHumanApproval: this.requireHumanApproval,
          offlineMode: this.offlineMode,
        }),
      );
    },
    setSelectedModelProvider(provider: string) {
      this.selectedModelProvider = provider;
      this.persist();
    },
    setEnabledPlugins(plugins: string[]) {
      this.enabledPlugins = [...plugins];
      this.persist();
    },
    togglePlugin(pluginName: string, enabled: boolean) {
      const current = new Set(this.enabledPlugins);

      if (enabled) {
        current.add(pluginName);
      } else {
        current.delete(pluginName);
      }

      this.enabledPlugins = [...current];
      this.persist();
    },
    setRunDefaults(settings: Partial<FrontendSettings>) {
      Object.assign(this, settings);
      this.persist();
    },
    hydratePluginDefaults(pluginNames: string[]) {
      if (this.enabledPlugins.length) {
        return;
      }

      this.enabledPlugins = [...pluginNames];
      this.persist();
    },
  },
});
