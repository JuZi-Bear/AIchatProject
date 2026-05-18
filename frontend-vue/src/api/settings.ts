import { apiClient, currentApiMode } from "./client";

import type { ApiResponse } from "@/types/api";
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

function normalizeSettings(settings: Partial<FrontendSettings> = {}): FrontendSettings {
  return {
    ...defaultSettings,
    ...settings,
    enabledPlugins: Array.isArray(settings.enabledPlugins) ? settings.enabledPlugins : [],
    maxRetryCount: Number(settings.maxRetryCount ?? defaultSettings.maxRetryCount),
    apiMode: currentApiMode,
  };
}

function readLocalSettings(): FrontendSettings {
  try {
    const rawValue = localStorage.getItem(STORAGE_KEY);

    if (!rawValue) {
      return { ...defaultSettings };
    }

    return normalizeSettings(JSON.parse(rawValue) as Partial<FrontendSettings>);
  } catch {
    return { ...defaultSettings };
  }
}

function writeLocalSettings(settings: FrontendSettings) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(normalizeSettings(settings)));
}

function unwrapApiResponse<T>(response: ApiResponse<T>): T {
  if (!response.success) {
    throw new Error(response.message || "Java settings request failed");
  }

  return response.data;
}

export function getSettings(): Promise<FrontendSettings> {
  if (currentApiMode !== "java") {
    return Promise.resolve(readLocalSettings());
  }

  return apiClient
    .get<ApiResponse<FrontendSettings>>("/settings")
    .then((response) => normalizeSettings(unwrapApiResponse(response.data)))
    .catch(() => readLocalSettings());
}

export function saveSettings(payload: FrontendSettings): Promise<FrontendSettings> {
  const normalizedPayload = normalizeSettings(payload);
  writeLocalSettings(normalizedPayload);

  if (currentApiMode !== "java") {
    return Promise.resolve(normalizedPayload);
  }

  return apiClient
    .post<ApiResponse<FrontendSettings>>("/settings", normalizedPayload)
    .then((response) => {
      const savedSettings = normalizeSettings(unwrapApiResponse(response.data));
      writeLocalSettings(savedSettings);
      return savedSettings;
    })
    .catch(() => normalizedPayload);
}
