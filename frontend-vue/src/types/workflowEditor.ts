export type NodePosition = {
  x: number;
  y: number;
};

export type WorkflowViewport = {
  x: number;
  y: number;
  scale: number;
};

export type WorkflowSelectionBox = {
  startX: number;
  startY: number;
  currentX: number;
  currentY: number;
};

export type WorkflowConnectionMode = "idle" | "connecting";

export type WorkflowDataType =
  | "requirement"
  | "product"
  | "code"
  | "test"
  | "error"
  | "file"
  | "report"
  | "approval"
  | "custom";

export type WorkflowPortDirection = "input" | "output";

export type WorkflowPortRef = {
  nodeId: string;
  field: string;
  direction: WorkflowPortDirection;
};

export type PendingConnectionData = {
  fromNodeId: string;
  fromOutputField?: string;
  dataType?: WorkflowDataType;
  color?: string;
  pointer: NodePosition;
};

export type AgentNodeData = {
  nodeId: string;
  agentKey: string;
  nodeType?: "agent" | "code_agent" | "human_approval" | "condition" | "join" | "loop" | "report" | "custom_agent" | "branch";
  executionMode?: "real" | "simulated" | "paused";
  langGraphKey?: string;
  name: string;
  role?: string;
  position: NodePosition;
  input_fields: string[];
  output_fields: string[];
  stage: string;
  enabled: boolean;
  description: string;
  codeAgentConfig?: {
    operation?:
      | "read_file"
      | "write_file"
      | "list_files"
      | "scan_folder"
      | "read_folder"
      | "plan_folder_changes"
      | "apply_folder_changes";
    target_path?: string;
    content?: string;
    audit_log_path?: string;
    baseDir?: string;
    includePatterns?: string;
    excludePatterns?: string;
    outputFile?: string;
    dryRun?: boolean;
    backupBeforeWrite?: boolean;
  };
  humanApprovalConfig?: {
    question: string;
    approveLabel: string;
    rejectLabel: string;
    required: boolean;
  };
  customAgentMeta?: {
    role: string;
    promptRef?: string;
    version?: string;
  };
  pausePolicy?: {
    enabled?: boolean;
    resumeFields?: string[];
  };
  loopPolicy?: {
    maxIterations?: number;
    exitCondition?: string;
  };
};

export type WorkflowEdgeType = "data" | "control" | "branch" | "loop" | "resume";

export type ConnectionData = {
  fromNodeId: string;
  toNodeId: string;
  fromOutputField?: string;
  toInputField?: string;
  dataType?: WorkflowDataType;
  color?: string;
  label?: string;
  edgeType?: WorkflowEdgeType;
  condition?: string;
  loopPolicy?: {
    maxIterations?: number;
    exitCondition?: string;
  };
};

export type WorkflowTemplateData = {
  workflowTemplateKey: string;
  name: string;
  description: string;
  nodes: AgentNodeData[];
  connections: ConnectionData[];
  version: string;
  source?: string;
  createdAt?: string;
  updatedAt?: string;
};

export type WorkflowValidationIssue = {
  severity: "error" | "warning";
  title: string;
  message: string;
  nodeId?: string;
  edge?: Partial<ConnectionData>;
};

export type WorkflowEditorState = {
  workflowTemplateKey: string;
  workflowName: string;
  workflowDescription: string;
  nodes: AgentNodeData[];
  connections: ConnectionData[];
  viewport: WorkflowViewport;
  selectedNodeId: string;
  selectedNodeIds: string[];
  selectedConnectionId: string;
  connectionMode: WorkflowConnectionMode;
  showStageGuide: boolean;
  undoStack: WorkflowTemplateData[];
  redoStack: WorkflowTemplateData[];
  savedTemplates: WorkflowTemplateData[];
};
