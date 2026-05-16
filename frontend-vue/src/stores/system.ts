import { defineStore } from "pinia";

import { getHealth } from "@/api/client";
import { getModels } from "@/api/models";
import { getPlugins } from "@/api/plugins";
import { getReports } from "@/api/reports";
import { getRuns } from "@/api/runs";
import type {
  HealthResponse,
  ModelConfig,
  PluginConfig,
} from "@/types/api";
import type { ReportItem, RunHistoryItem } from "@/types/run";

type SystemState = {
  health: HealthResponse | null;
  models: ModelConfig[];
  plugins: PluginConfig[];
  runs: RunHistoryItem[];
  reports: ReportItem[];
  loading: boolean;
  error: string;
};

export const useSystemStore = defineStore("system", {
  state: (): SystemState => ({
    health: null,
    models: [],
    plugins: [],
    runs: [],
    reports: [],
    loading: false,
    error: "",
  }),
  getters: {
    successfulRuns: (state) => state.runs.filter((run) => run.success).length,
    enabledPlugins: (state) => state.plugins.filter((plugin) => plugin.enabled).length,
  },
  actions: {
    async loadOverview() {
      this.loading = true;
      this.error = "";

      try {
        const [health, models, plugins, runs, reports] = await Promise.all([
          getHealth(),
          getModels(),
          getPlugins(),
          getRuns(),
          getReports(),
        ]);

        this.health = health;
        this.models = models;
        this.plugins = plugins;
        this.runs = runs;
        this.reports = reports;
      } catch (error) {
        this.error = error instanceof Error ? error.message : "API 请求失败";
      } finally {
        this.loading = false;
      }
    },
  },
});
