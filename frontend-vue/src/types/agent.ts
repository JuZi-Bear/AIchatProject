export type AgentMeta = {
  key: string;
  name: string;
  role: string;
  description: string;
  input_fields: string[];
  output_fields: string[];
  stage: string;
  enabled: boolean;
  version: string;
};
