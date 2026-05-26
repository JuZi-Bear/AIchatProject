export type ModelConfig = {
  id?: number;
  name: string;
  provider: string;
  model: string;
  base_url: string;
  baseUrl?: string;
  env_key?: string;
  envKey?: string;
  enabled?: boolean;
  offline_mode?: boolean;
  default?: boolean;
  is_default?: boolean;
  defaultModel?: boolean;
  api_key_configured?: boolean;
  apiKeyConfigured?: boolean;
  createdAt?: string;
  updatedAt?: string;
};

export type ModelSecretStatus = {
  provider: string;
  name: string;
  envKey: string;
  configured: boolean;
  stored: boolean;
  envConfigured: boolean;
  maskedKey: string;
  updatedAt: string;
  message: string;
};
