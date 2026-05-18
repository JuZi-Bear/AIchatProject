import axios from "axios";

import type { HealthResponse } from "@/types/api";

export type ApiMode = "python" | "java";

function normalizeApiMode(mode?: string): ApiMode {
  return mode === "java" ? "java" : "python";
}

const legacyApiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const pythonApiBaseUrl = import.meta.env.VITE_PYTHON_API_BASE_URL || legacyApiBaseUrl || "http://127.0.0.1:8001";
const javaApiBaseUrl = import.meta.env.VITE_JAVA_API_BASE_URL || "http://127.0.0.1:8088/api";

export const currentApiMode = normalizeApiMode(import.meta.env.VITE_API_MODE);
export const currentApiBaseUrl = currentApiMode === "java" ? javaApiBaseUrl : pythonApiBaseUrl;
export const currentHealthPath = currentApiMode === "java" ? "/agent/health" : "/health";

export const apiClient = axios.create({
  baseURL: currentApiBaseUrl,
  timeout: 600000,
  headers: {
    "Content-Type": "application/json",
  },
});

export function getHealth() {
  return apiClient.get<HealthResponse>(currentHealthPath).then((response) => response.data);
}

export function getApiBaseUrl() {
  return currentApiBaseUrl;
}

export function getApiModeLabel() {
  return currentApiMode === "java" ? "Java Gateway" : "Python Direct";
}

export function getDataModeLabel() {
  return currentApiMode === "java" ? "Java Gateway + MySQL" : "Python Direct";
}

export function getConfigSourceLabel() {
  return currentApiMode === "java" ? "Java MySQL 持久化" : "Python 文件配置";
}

export function getApiDisconnectedHint() {
  return currentApiMode === "java"
    ? "Java 平台服务未连接，请检查 8088 服务"
    : "Python Agent Engine 未连接，请检查 8001 服务";
}
