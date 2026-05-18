package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.entity.ReportIndexEntity;
import com.aichat.platform.service.PythonAgentClient;
import com.aichat.platform.service.ReportIndexService;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/platform")
public class PlatformReportController {

    private final ReportIndexService reportIndexService;
    private final PythonAgentClient pythonAgentClient;

    public PlatformReportController(ReportIndexService reportIndexService, PythonAgentClient pythonAgentClient) {
        this.reportIndexService = reportIndexService;
        this.pythonAgentClient = pythonAgentClient;
    }

    @GetMapping("/reports")
    public ApiResponse<List<ReportIndexEntity>> listPlatformReports() {
        return ApiResponse.ok(reportIndexService.listReports());
    }

    @GetMapping("/reports/{reportName}")
    public ApiResponse<Map<String, Object>> getPlatformReport(@PathVariable String reportName) {
        Map<String, Object> result = new LinkedHashMap<>();
        reportIndexService.getReportByName(reportName).ifPresent(index -> result.put("reportIndex", index));

        try {
            Map<String, Object> report = pythonAgentClient.getReport(reportName);
            result.put("reportName", reportName);
            result.put("report", report);
            result.put("content", report == null ? "" : report.getOrDefault("content", ""));
        } catch (Exception error) {
            result.put("reportName", reportName);
            result.put("content", "");
            result.put("error", "failed to load report content from Python Agent Engine: " + error.getMessage());
        }

        return ApiResponse.ok(result);
    }

    @GetMapping("/runs/{platformRunId}/reports")
    public ApiResponse<List<ReportIndexEntity>> getReportsByPlatformRunId(@PathVariable String platformRunId) {
        return ApiResponse.ok(reportIndexService.getReportsByPlatformRunId(platformRunId));
    }
}
