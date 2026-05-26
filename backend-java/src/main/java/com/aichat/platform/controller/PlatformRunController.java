package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.entity.RunEventEntity;
import com.aichat.platform.entity.RunRecordEntity;
import com.aichat.platform.service.RunEventService;
import com.aichat.platform.service.RunRecordService;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/platform/runs")
public class PlatformRunController {

    private final RunRecordService runRecordService;
    private final RunEventService runEventService;

    public PlatformRunController(RunRecordService runRecordService, RunEventService runEventService) {
        this.runRecordService = runRecordService;
        this.runEventService = runEventService;
    }

    @GetMapping
    public ApiResponse<List<RunRecordEntity>> listPlatformRuns() {
        return ApiResponse.ok(runRecordService.listRecords());
    }

    @GetMapping("/{platformRunId}")
    public ApiResponse<RunRecordEntity> getPlatformRun(@PathVariable String platformRunId) {
        RunRecordEntity record = runRecordService.getRecord(platformRunId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "platform run not found: " + platformRunId));

        return ApiResponse.ok(record);
    }

    @PostMapping("/{platformRunId}/cancel")
    public ApiResponse<RunRecordEntity> cancelPlatformRun(@PathVariable String platformRunId) {
        runRecordService.getRecord(platformRunId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "platform run not found: " + platformRunId));

        return ApiResponse.ok(runRecordService.cancelRun(platformRunId));
    }

    @PostMapping("/{platformRunId}/approval")
    public ApiResponse<RunRecordEntity> approvePlatformRun(
            @PathVariable String platformRunId,
            @RequestBody(required = false) Map<String, Object> request
    ) {
        runRecordService.getRecord(platformRunId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "platform run not found: " + platformRunId));

        Map<String, Object> safeRequest = request == null ? Map.of() : request;
        boolean approved = Boolean.parseBoolean(String.valueOf(safeRequest.getOrDefault("approved", false)));
        String comment = String.valueOf(safeRequest.getOrDefault("comment", ""));

        return ApiResponse.ok(runRecordService.approveRun(platformRunId, approved, comment));
    }

    @GetMapping("/{platformRunId}/events")
    public ApiResponse<List<RunEventEntity>> listRunEvents(@PathVariable String platformRunId) {
        return ApiResponse.ok(runEventService.listEventsByRun(platformRunId));
    }

    @GetMapping("/{platformRunId}/replay")
    public ApiResponse<Map<String, Object>> getWorkflowReplay(@PathVariable String platformRunId) {
        return ApiResponse.ok(runRecordService.getReplayData(platformRunId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "platform run not found: " + platformRunId)));
    }
}
