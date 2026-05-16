export type PluginConfig = {
  name: string;
  display_name: string;
  description: string;
  enabled: boolean;
  latest_result?: {
    status?: string;
    summary?: string;
    detail?: string;
  };
};
