export type RunEvent = {
  id: number;
  platformRunId: string;
  pythonRunId?: string;
  eventType: string;
  eventText: string;
  agent?: string;
  status?: string;
  message?: string;
  detailJson?: string;
  createdAt: string;
};
