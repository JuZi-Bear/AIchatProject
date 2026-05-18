package com.aichat.platform.controller;

import com.aichat.platform.dto.RunRequest;
import com.aichat.platform.dto.RunResponse;
import com.aichat.platform.service.PythonAgentClient;
import com.aichat.platform.service.RunService;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class RunProxyController {

    private final PythonAgentClient pythonAgentClient;
    private final RunService runService;

    public RunProxyController(PythonAgentClient pythonAgentClient, RunService runService) {
        this.pythonAgentClient = pythonAgentClient;
        this.runService = runService;
    }

    @GetMapping("/agent/health")
    public Map<String, Object> agentHealth() {
        return pythonAgentClient.getHealth();
    }

    @PostMapping("/runs")
    public RunResponse createRun(@Valid @RequestBody RunRequest request) {
        return runService.createRun(request);
    }

    @GetMapping("/runs")
    public List<Map<String, Object>> getRuns() {
        return runService.getRuns();
    }

    @GetMapping("/runs/{runId}")
    public RunResponse getRun(@PathVariable String runId) {
        return runService.getRun(runId);
    }

    @GetMapping("/reports")
    public List<Map<String, Object>> getReports() {
        return pythonAgentClient.getReports();
    }

    @GetMapping("/reports/{reportName}")
    public Map<String, Object> getReport(@PathVariable String reportName) {
        return pythonAgentClient.getReport(reportName);
    }
}
