import axios from "axios";

import type { HealthResponse } from "@/types/api";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

export const apiClient = axios.create({
  baseURL,
  timeout: 600000,
  headers: {
    "Content-Type": "application/json",
  },
});

export function getHealth() {
  return apiClient.get<HealthResponse>("/health").then((response) => response.data);
}

export function getApiBaseUrl() {
  return baseURL;
}
