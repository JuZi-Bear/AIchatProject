package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.model.RunEventType;
import com.aichat.platform.service.PythonAgentClient;
import com.aichat.platform.service.RunEventService;
import com.aichat.platform.service.RunRecordService;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import jakarta.servlet.http.HttpServletRequest;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
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
        runRecordService.saveCodeAgentRecord(platformRunId, safeRequest, data);
        persistWorkflowEvents(platformRunId, data.get("events"));
        completeCodeAgentRun(platformRunId, data);

        return ApiResponse.ok(data);
    }

    @PostMapping("/open-folder")
    public ApiResponse<Map<String, Object>> openFolder(@RequestBody Map<String, Object> request) {
        Map<String, Object> response = pythonAgentClient.openFolder(request == null ? new LinkedHashMap<>() : request);
        return ApiResponse.ok(response);
    }

    @PostMapping("/ai-generate")
    public ApiResponse<Map<String, Object>> aiGenerateProject(@RequestBody Map<String, Object> request) {
        Map<String, Object> response = pythonAgentClient.aiGenerateProject(request == null ? new LinkedHashMap<>() : request);
        return ApiResponse.ok(response);
    }

    @GetMapping("/preview/serve/**")
    public ResponseEntity<byte[]> servePreviewFile(HttpServletRequest request) {
        String uri = request.getRequestURI();
        String targetPart = "/preview/serve/";
        int index = uri.indexOf(targetPart);
        if (index == -1) {
            return ResponseEntity.badRequest().build();
        }
        String pathWithinController = uri.substring(index + targetPart.length());
        String decodedPath = URLDecoder.decode(pathWithinController, StandardCharsets.UTF_8);
        return pythonAgentClient.servePreviewFile(decodedPath);
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

    private void completeCodeAgentRun(String platformRunId, Map<String, Object> data) {
        boolean success = Boolean.parseBoolean(asString(data.get("success")));
        Map<String, Object> detail = new LinkedHashMap<>();
        detail.put("operation", asString(data.get("operation")));
        detail.put("filePath", asString(data.get("filePath")));
        detail.put("message", asString(data.get("message")));
        detail.put("agent", asString(data.get("agent")));

        runEventService.addEvent(
                platformRunId,
                "",
                success ? RunEventType.RUN_SUCCESS : RunEventType.RUN_FAILED,
                success ? "SUCCESS" : "FAILED",
                success ? "CodeAgent 文件操作完成" : "CodeAgent 文件操作失败",
                detail
        );
    }

    private String asString(Object value) {
        return value == null ? "" : String.valueOf(value);
    }
}
