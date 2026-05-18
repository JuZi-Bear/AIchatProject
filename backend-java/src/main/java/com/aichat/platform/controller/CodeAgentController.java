package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.service.PythonAgentClient;
import com.aichat.platform.service.RunEventService;
import com.aichat.platform.service.RunRecordService;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/code-agent")
public class CodeAgentController {

    private final PythonAgentClient pythonAgentClient;
    private final RunEventService runEventService;
    private final RunRecordService runRecordService;

    public CodeAgentController(
            PythonAgentClient pythonAgentClient,
            RunEventService runEventService,
            RunRecordService runRecordService
    ) {
        this.pythonAgentClient = pythonAgentClient;
        this.runEventService = runEventService;
        this.runRecordService = runRecordService;
    }

    @PostMapping("/execute")
    public ApiResponse<Map<String, Object>> executeCodeAgent(@RequestBody Map<String, Object> request) {
        Map<String, Object> safeRequest = request == null ? new LinkedHashMap<>() : new LinkedHashMap<>(request);
        String platformRunId = asString(safeRequest.get("platformRunId"));

        if (platformRunId.isBlank()) {
            platformRunId = asString(safeRequest.get("platform_run_id"));
        }

        if (platformRunId.isBlank()) {
            platformRunId = runRecordService.nextPlatformRunId();
        }

        safeRequest.put("platformRunId", platformRunId);
        Map<String, Object> response = pythonAgentClient.executeCodeAgent(safeRequest);
        Map<String, Object> data = response == null ? new LinkedHashMap<>() : new LinkedHashMap<>(response);
        data.put("platformRunId", platformRunId);
        persistWorkflowEvents(platformRunId, data.get("events"));

        return ApiResponse.ok(data);
    }

    @SuppressWarnings("unchecked")
    private void persistWorkflowEvents(String platformRunId, Object rawEvents) {
        if (!(rawEvents instanceof List<?> events)) {
            return;
        }

        for (Object event : events) {
            if (event instanceof Map<?, ?> eventMap) {
                runEventService.addPythonWorkflowEvent(platformRunId, "", (Map<String, Object>) eventMap);
            }
        }
    }

    private String asString(Object value) {
        return value == null ? "" : String.valueOf(value);
    }
}
