export type ModelConfig = {
  name: string;
  provider: string;
  model: string;
  base_url: string;
  env_key?: string;
  enabled?: boolean;
  offline_mode?: boolean;
  default?: boolean;
  is_default?: boolean;
  api_key_configured?: boolean;
};
