export type NodePosition = {
  x: number;
  y: number;
};

export type AgentNodeData = {
  nodeId: string;
  agentKey: string;
  name: string;
  position: NodePosition;
  input_fields: string[];
  output_fields: string[];
  stage: string;
  enabled: boolean;
  description: string;
};

export type ConnectionData = {
  fromNodeId: string;
  toNodeId: string;
};

export type WorkflowTemplateData = {
  workflowTemplateKey: string;
  name: string;
  description: string;
  nodes: AgentNodeData[];
  connections: ConnectionData[];
  version: string;
};

export type WorkflowEditorState = {
  workflowTemplateKey: string;
  workflowName: string;
  workflowDescription: string;
  nodes: AgentNodeData[];
  connections: ConnectionData[];
  selectedNodeId: string;
  undoStack: WorkflowTemplateData[];
  redoStack: WorkflowTemplateData[];
  savedTemplates: WorkflowTemplateData[];
};
