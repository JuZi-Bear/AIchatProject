import { defineStore } from "pinia";

import { currentApiMode } from "@/api/client";
import { getSettings as fetchSettings, saveSettings as persistSettings } from "@/api/settings";
import type { FrontendSettings } from "@/types/settings";

const STORAGE_KEY = "ai-agent-pipeline.frontend-settings";

const defaultSettings: FrontendSettings = {
  selectedModelProvider: "deepseek",
  enabledPlugins: [],
  demoMode: true,
  maxRetryCount: 3,
  requireHumanApproval: false,
  offlineMode: false,
  apiMode: currentApiMode,
};

function normalizeSettings(settings: Partial<FrontendSettings>): FrontendSettings {
  return {
    ...defaultSettings,
    ...settings,
    enabledPlugins: Array.isArray(settings.enabledPlugins) ? settings.enabledPlugins : [],
    maxRetryCount: Number(settings.maxRetryCount ?? defaultSettings.maxRetryCount),
    apiMode: settings.apiMode || currentApiMode,
  };
}

function readStoredSettings(): FrontendSettings {
  try {
    const rawValue = localStorage.getItem(STORAGE_KEY);

    if (!rawValue) {
      return { ...defaultSettings };
    }

    const parsed = JSON.parse(rawValue) as Partial<FrontendSettings>;

    return normalizeSettings(parsed);
  } catch {
    return { ...defaultSettings };
  }
}

function snapshot(settings: FrontendSettings): FrontendSettings {
  return {
    selectedModelProvider: settings.selectedModelProvider,
    enabledPlugins: [...settings.enabledPlugins],
    demoMode: settings.demoMode,
    maxRetryCount: settings.maxRetryCount,
    requireHumanApproval: settings.requireHumanApproval,
    offlineMode: settings.offlineMode,
    apiMode: currentApiMode,
  };
}

export const useSettingsStore = defineStore("settings", {
  state: (): FrontendSettings => readStoredSettings(),
  actions: {
    persistLocal() {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(snapshot(this)),
      );
    },
    async persistRemote() {
      if (currentApiMode !== "java") {
        return;
      }

      try {
        await persistSettings(snapshot(this));
      } catch {
        // Java settings is an optional platform sync layer; localStorage remains the fallback.
      }
    },
    persist() {
      this.apiMode = currentApiMode;
      this.persistLocal();
      void this.saveSettings();
    },
    async loadSettings() {
      try {
        Object.assign(this, normalizeSettings(await fetchSettings()));
        this.apiMode = currentApiMode;
        this.persistLocal();
      } catch {
        // Keep the current localStorage values when the platform settings layer is unavailable.
      }
    },
    async saveSettings() {
      this.apiMode = currentApiMode;
      this.persistLocal();

      try {
        Object.assign(this, normalizeSettings(await persistSettings(snapshot(this))));
        this.persistLocal();
      } catch {
        // localStorage is already written, so the UI can keep working offline.
      }
    },
    async hydrateRemoteSettings() {
      await this.loadSettings();
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
