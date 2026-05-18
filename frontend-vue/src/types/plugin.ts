export type PluginConfig = {
  id?: number;
  name: string;
  pluginName?: string;
  display_name: string;
  displayName?: string;
  description: string;
  enabled: boolean;
  latest_result?: {
    status?: string;
    summary?: string;
    detail?: string;
  };
  latestResult?: {
    status?: string;
    summary?: string;
    detail?: string;
  };
  createdAt?: string;
  updatedAt?: string;
};
