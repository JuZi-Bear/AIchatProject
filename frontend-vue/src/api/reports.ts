import { apiClient } from "./client";

import type { ReportDetail, ReportItem } from "@/types/run";

type RawReportItem = {
  name?: string;
  path?: string;
  size?: number;
  modified_time?: string;
  created_at?: string;
};

type RawReportDetail = {
  name?: string;
  path?: string;
  content?: string;
};

function runIdFromReportName(reportName?: string) {
  const match = (reportName || "").match(/(run_\d{8}_\d{6}(?:_model\d+)?)/);
  return match?.[1] || "";
}

function normalizeReportItem(item: RawReportItem): ReportItem {
  const reportName = item.name || "";

  return {
    report_name: reportName,
    name: reportName,
    path: item.path || "",
    created_at: item.created_at || item.modified_time || "",
    modified_time: item.modified_time,
    file_size: item.size,
    size: item.size,
    run_id: runIdFromReportName(reportName),
  };
}

function normalizeReportDetail(item: RawReportDetail): ReportDetail {
  const reportName = item.name || "";

  return {
    report_name: reportName,
    name: reportName,
    path: item.path || "",
    content: item.content || "",
    run_id: runIdFromReportName(reportName),
  };
}

export function getReports(): Promise<ReportItem[]> {
  return apiClient.get<RawReportItem[]>("/reports").then((response) => response.data.map(normalizeReportItem));
}

export function getReport(reportName: string): Promise<ReportDetail> {
  return apiClient.get<RawReportDetail>(`/reports/${reportName}`).then((response) => normalizeReportDetail(response.data));
}
