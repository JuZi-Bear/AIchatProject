package com.aichat.platform.service;

import com.aichat.platform.dto.RunRequest;
import com.aichat.platform.dto.RunResponse;
import com.aichat.platform.entity.ReportIndexEntity;
import com.aichat.platform.entity.RunRecordEntity;
import com.aichat.platform.model.RunEventType;
import com.aichat.platform.repository.RunRecordRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.springframework.stereotype.Service;

@Service
public class RunRecordService {

    private static final DateTimeFormatter RUN_ID_FORMATTER =
            DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss").withZone(ZoneOffset.UTC);

    private final RunRecordRepository runRecordRepository;
    private final ObjectMapper objectMapper;
    private final ReportIndexService reportIndexService;
    private final RunEventService runEventService;

    public RunRecordService(
            RunRecordRepository runRecordRepository,
            ObjectMapper objectMapper,
            ReportIndexService reportIndexService,
            RunEventService runEventService
    ) {
        this.runRecordRepository = runRecordRepository;
        this.objectMapper = objectMapper;
        this.reportIndexService = reportIndexService;
        this.runEventService = runEventService;
    }

    public String nextPlatformRunId() {
        return "platform_" + RUN_ID_FORMATTER.format(Instant.now()) + "_" + UUID.randomUUID().toString().substring(0, 8);
    }

    public RunRecordEntity createRecord(String platformRunId, RunRequest request) {
        RunRecordEntity record = new RunRecordEntity();
        record.setPlatformRunId(platformRunId);
        record.setStatus("CREATED");
        record.setRequirement(request.requirement());
        record.setModelProvider(request.modelProvider());
        record.setRetryCount(0);
        record.setRunnerMode("python");
        record.setRequireHumanApproval(request.requireHumanApproval());

        return runRecordRepository.save(record);
    }

    public RunRecordEntity updateStatus(String platformRunId, String status) {
        RunRecordEntity record = runRecordRepository.findByPlatformRunId(platformRunId)
                .orElseThrow(() -> new IllegalArgumentException("platform run not found: " + platformRunId));
        record.setStatus(status);

        return runRecordRepository.save(record);
    }

    public RunRecordEntity save(String platformRunId, RunRequest request, RunResponse response) {
        Map<String, Object> summary = response.runSummary() == null ? Map.of() : response.runSummary();
        Map<String, Object> uiViewModel = response.uiViewModel() == null ? Map.of() : response.uiViewModel();
        Map<String, Object> state = response.state() == null ? Map.of() : response.state();
        RunRecordEntity record = runRecordRepository.findByPlatformRunId(platformRunId)
                .orElseGet(RunRecordEntity::new);
        record.setPlatformRunId(platformRunId);
        record.setPythonRunId(response.runId());
        record.setStatus(asBoolean(summary.get("success")) ? "SUCCESS" : "FAILED");
        record.setRequirement(request.requirement());
        record.setModelProvider(firstNonBlank(asString(summary.get("model_provider")), request.modelProvider()));
        record.setModelName(firstNonBlank(asString(summary.get("model_name")), asString(state.get("model_name"))));
        record.setModelBaseUrl(firstNonBlank(asString(summary.get("model_base_url")), asString(state.get("model_base_url"))));
        record.setSuccess(asBoolean(summary.get("success")));
        record.setRetryCount(asInt(summary.get("retry_count")));
        record.setTestSuccess(asBoolean(summary.get("test_success")));
        record.setCoveragePercent(asDouble(summary.get("coverage_percent")));
        record.setQualityScore(asDouble(summary.get("quality_score")));
        record.setSecurityStatus(asString(summary.get("security_status")));
        record.setReportPath(asString(summary.get("report_path")));
        record.setStatePath(asString(summary.get("state_path")));
        record.setRunnerMode(firstNonBlank(asString(summary.get("runner_mode")), asString(state.get("runner_mode")), "python"));
        record.setRunnerWarning(firstNonBlank(asString(summary.get("runner_warning")), asString(state.get("runner_warning"))));
        record.setRunSummaryJson(serializeObject(summary));
        record.setUiViewModelJson(serializeObject(uiViewModel));
        record.setPluginResultsJson(serializeObject(extractPluginResults(uiViewModel, state)));
        record.setErrorSummary(firstNonBlank(
                asString(summary.get("error_summary")),
                asString(nestedValue(uiViewModel, "agent_outputs", "error_summary")),
                asString(state.get("error_summary")),
                asString(state.get("error_log"))
        ));
        record.setApproved(asBoolean(firstNonNull(state.get("approved"), summary.get("approved"))));
        record.setRequireHumanApproval(asBoolean(firstNonNull(
                state.get("require_human_approval"),
                summary.get("require_human_approval"),
                request.requireHumanApproval()
        )));
        record.setRawResponse(serializeResponse(response));

        RunRecordEntity savedRecord = runRecordRepository.save(record);
        savePythonWorkflowEvents(savedRecord.getPlatformRunId(), savedRecord.getPythonRunId(), state, uiViewModel);
        Optional<ReportIndexEntity> reportIndex = reportIndexService.saveReportIndexFromRunRecord(savedRecord);
        reportIndex.ifPresent(index -> runEventService.addEvent(
                savedRecord.getPlatformRunId(),
                savedRecord.getPythonRunId(),
                RunEventType.REPORT_INDEXED,
                savedRecord.getStatus(),
                "报告已建立平台索引",
                Map.of(
                        "reportName", firstNonBlank(index.getReportName()),
                        "reportPath", firstNonBlank(index.getReportPath())
                )
        ));

        return savedRecord;
    }

    public RunRecordEntity saveCodeAgentRecord(
            String platformRunId,
            Map<String, Object> request,
            Map<String, Object> response
    ) {
        Map<String, Object> safeRequest = request == null ? Map.of() : request;
        Map<String, Object> safeResponse = response == null ? Map.of() : response;
        boolean success = asBoolean(safeResponse.get("success"));
        String operation = firstNonBlank(asString(safeResponse.get("operation")), asString(safeRequest.get("operation")));
        String filePath = firstNonBlank(
                asString(safeResponse.get("filePath")),
                asString(safeRequest.get("filePath")),
                asString(safeRequest.get("file_path"))
        );
        String message = asString(safeResponse.get("message"));
        Object workflowEvents = safeResponse.get("events");
        String securityStatus = success ? "path_policy_passed" : "path_policy_blocked_or_failed";

        RunRecordEntity record = runRecordRepository.findByPlatformRunId(platformRunId)
                .orElseGet(RunRecordEntity::new);
        record.setPlatformRunId(platformRunId);
        record.setPythonRunId("");
        record.setStatus(success ? "SUCCESS" : "FAILED");
        record.setRequirement(buildCodeAgentRequirement(operation, filePath));
        record.setModelProvider("code_agent");
        record.setModelName("Simple CodeAgent");
        record.setModelBaseUrl("");
        record.setSuccess(success);
        record.setRetryCount(0);
        record.setTestSuccess(success);
        record.setCoveragePercent(0);
        record.setQualityScore(success ? 100 : 0);
        record.setSecurityStatus(securityStatus);
        record.setReportPath("");
        record.setStatePath("");
        record.setRunnerMode("code_agent");
        record.setRunnerWarning(success ? "" : message);
        record.setRunSummaryJson(serializeObject(buildCodeAgentSummary(
                success,
                operation,
                filePath,
                message,
                securityStatus,
                workflowEvents
        )));
        record.setUiViewModelJson(serializeObject(buildCodeAgentUiViewModel(success, message, workflowEvents, safeResponse)));
        record.setPluginResultsJson("[]");
        record.setErrorSummary(success ? "" : message);
        record.setApproved(true);
        record.setRequireHumanApproval(false);
        record.setRawResponse(serializeObject(safeResponse));

        return runRecordRepository.save(record);
    }

    @SuppressWarnings("unchecked")
    private void savePythonWorkflowEvents(
            String platformRunId,
            String pythonRunId,
            Map<String, Object> state,
            Map<String, Object> uiViewModel
    ) {
        Object workflowEvents = state.get("workflow_events");

        if (!(workflowEvents instanceof List<?>)) {
            workflowEvents = uiViewModel.get("workflow_events");
        }

        if (!(workflowEvents instanceof List<?> eventList)) {
            return;
        }

        for (Object event : eventList) {
            if (event instanceof Map<?, ?> eventMap) {
                runEventService.addPythonWorkflowEvent(platformRunId, pythonRunId, (Map<String, Object>) eventMap);
            }
        }
    }

    public List<RunRecordEntity> listRecords() {
        return runRecordRepository.findAllByOrderByCreatedAtDesc();
    }

    public Optional<RunRecordEntity> getRecord(String platformRunId) {
        return runRecordRepository.findByPlatformRunId(platformRunId);
    }

    public Optional<Map<String, Object>> getReplayData(String platformRunId) {
        return getRecord(platformRunId).map(record -> {
            List<Map<String, Object>> events = runEventService.listEventsByRun(platformRunId)
                    .stream()
                    .map(this::eventToReplayRow)
                    .toList();
            Map<String, Object> replay = new LinkedHashMap<>();
            replay.put("platformRunId", record.getPlatformRunId());
            replay.put("pythonRunId", record.getPythonRunId());
            replay.put("requirement", record.getRequirement());
            replay.put("status", firstNonBlank(record.getStatus(), record.isSuccess() ? "SUCCESS" : "FAILED"));
            replay.put("statusText", statusText(asString(replay.get("status"))));
            replay.put("success", record.isSuccess());
            replay.put("qualityScore", record.getQualityScore());
            replay.put("durationMs", calculateDurationMs(events));
            replay.put("events", events);
            replay.put("runSummary", parseJsonMap(record.getRunSummaryJson()));
            replay.put("uiViewModel", parseJsonMap(record.getUiViewModelJson()));

            return replay;
        });
    }

    public RunRecordEntity cancelRun(String platformRunId) {
        RunRecordEntity record = runRecordRepository.findByPlatformRunId(platformRunId)
                .orElseThrow(() -> new IllegalArgumentException("platform run not found: " + platformRunId));
        String oldStatus = firstNonBlank(record.getStatus(), "UNKNOWN");

        if (isTerminalStatus(oldStatus)) {
            runEventService.addEvent(
                    platformRunId,
                    record.getPythonRunId(),
                    RunEventType.ERROR_OCCURRED,
                    oldStatus,
                    "任务已结束，无法取消",
                    Map.of("currentStatus", oldStatus)
            );

            return record;
        }

        record.setStatus("CANCELLED");
        RunRecordEntity savedRecord = runRecordRepository.save(record);
        runEventService.addStatusChangedEvent(platformRunId, oldStatus, "CANCELLED");
        runEventService.addEvent(
                platformRunId,
                savedRecord.getPythonRunId(),
                RunEventType.RUN_CANCELLED,
                "CANCELLED",
                "任务已取消",
                Map.of("oldStatus", oldStatus, "newStatus", "CANCELLED")
        );

        return savedRecord;
    }

    private boolean isTerminalStatus(String status) {
        return "SUCCESS".equals(status) || "FAILED".equals(status) || "CANCELLED".equals(status);
    }

    private String buildCodeAgentRequirement(String operation, String filePath) {
        return "CodeAgent " + firstNonBlank(operation, "operation") + " -> " + firstNonBlank(filePath, "project file");
    }

    private Map<String, Object> buildCodeAgentSummary(
            boolean success,
            String operation,
            String filePath,
            String message,
            String securityStatus,
            Object workflowEvents
    ) {
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("success", success);
        summary.put("retry_count", 0);
        summary.put("test_success", success);
        summary.put("coverage_percent", 0);
        summary.put("quality_score", success ? 100 : 0);
        summary.put("security_status", securityStatus);
        summary.put("model_provider", "code_agent");
        summary.put("runner_mode", "code_agent");
        summary.put("runner_warning", success ? "" : message);
        summary.put("report_path", "");
        summary.put("event_count", listSize(workflowEvents));
        summary.put("last_event", lastWorkflowEvent(workflowEvents));
        summary.put("code_agent_operation", operation);
        summary.put("code_agent_file_path", filePath);
        summary.put("message", message);

        return summary;
    }

    private Map<String, Object> buildCodeAgentUiViewModel(
            boolean success,
            String message,
            Object workflowEvents,
            Map<String, Object> response
    ) {
        Map<String, Object> workflowStep = new LinkedHashMap<>();
        workflowStep.put("key", "code_agent");
        workflowStep.put("label", "CodeAgent 文件操作");
        workflowStep.put("status", success ? "done" : "failed");
        workflowStep.put("summary", message);
        workflowStep.put("order", 1);

        Map<String, Object> agentOutputs = new LinkedHashMap<>();
        agentOutputs.put("stdout", serializeObject(response));
        agentOutputs.put("error_summary", success ? "" : message);
        agentOutputs.put("code_agent_result", response);

        Map<String, Object> uiViewModel = new LinkedHashMap<>();
        uiViewModel.put("workflow_steps", List.of(workflowStep));
        uiViewModel.put("workflow_events", workflowEvents instanceof List<?> ? workflowEvents : List.of());
        uiViewModel.put("agent_outputs", agentOutputs);
        uiViewModel.put("raw", response);

        return uiViewModel;
    }

    private int listSize(Object value) {
        return value instanceof List<?> listValue ? listValue.size() : 0;
    }

    private Object lastWorkflowEvent(Object value) {
        if (value instanceof List<?> listValue && !listValue.isEmpty()) {
            return listValue.get(listValue.size() - 1);
        }

        return Map.of();
    }

    private Map<String, Object> eventToReplayRow(com.aichat.platform.entity.RunEventEntity event) {
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("id", event.getId());
        row.put("platformRunId", event.getPlatformRunId());
        row.put("pythonRunId", event.getPythonRunId());
        row.put("eventType", event.getEventType() == null ? "" : event.getEventType().name());
        row.put("eventText", event.getEventText());
        row.put("agent", event.getAgent());
        row.put("status", event.getStatus());
        row.put("message", event.getMessage());
        row.put("detailJson", event.getDetailJson());
        row.put("createdAt", event.getCreatedAt() == null ? "" : event.getCreatedAt().toString());

        return row;
    }

    private long calculateDurationMs(List<Map<String, Object>> events) {
        if (events.size() < 2) {
            return 0;
        }

        LocalDateTime start = parseDate(asString(events.get(0).get("createdAt")));
        LocalDateTime end = parseDate(asString(events.get(events.size() - 1).get("createdAt")));

        if (start == null || end == null) {
            return 0;
        }

        return Math.max(0, Duration.between(start, end).toMillis());
    }

    private LocalDateTime parseDate(String value) {
        try {
            return LocalDateTime.parse(value);
        } catch (Exception error) {
            return null;
        }
    }

    private String statusText(String status) {
        return switch (status) {
            case "SUCCESS" -> "成功";
            case "FAILED" -> "失败";
            case "RUNNING" -> "运行中";
            case "CREATED" -> "已创建";
            case "CANCELLED" -> "已取消";
            default -> status == null || status.isBlank() ? "未知" : status;
        };
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> parseJsonMap(String rawJson) {
        if (rawJson == null || rawJson.isBlank()) {
            return Map.of();
        }

        try {
            Object parsed = objectMapper.readValue(rawJson, Object.class);
            if (parsed instanceof Map<?, ?> parsedMap) {
                return (Map<String, Object>) parsedMap;
            }
        } catch (Exception ignored) {
            // Replay should still return base data if stored JSON cannot be parsed.
        }

        return Map.of();
    }

    private boolean asBoolean(Object value) {
        if (value instanceof Boolean boolValue) {
            return boolValue;
        }

        return Boolean.parseBoolean(String.valueOf(value));
    }

    private int asInt(Object value) {
        if (value instanceof Number numberValue) {
            return numberValue.intValue();
        }

        try {
            return Integer.parseInt(String.valueOf(value));
        } catch (NumberFormatException error) {
            return 0;
        }
    }

    private double asDouble(Object value) {
        if (value instanceof Number numberValue) {
            return numberValue.doubleValue();
        }

        try {
            return Double.parseDouble(String.valueOf(value));
        } catch (NumberFormatException error) {
            return 0;
        }
    }

    private String asString(Object value) {
        return value == null ? "" : String.valueOf(value);
    }

    private Object extractPluginResults(Map<String, Object> uiViewModel, Map<String, Object> state) {
        Object pluginResults = nestedValue(uiViewModel, "plugin_outputs", "plugin_results");

        if (pluginResults != null) {
            return pluginResults;
        }

        pluginResults = state.get("plugin_results");

        if (pluginResults != null) {
            return pluginResults;
        }

        return Map.of(
                "doc_result", asString(state.get("doc_result")),
                "security_result", asString(state.get("security_result")),
                "refactor_result", asString(state.get("refactor_result")),
                "ui_result", asString(state.get("ui_result"))
        );
    }

    @SuppressWarnings("unchecked")
    private Object nestedValue(Map<String, Object> source, String firstKey, String secondKey) {
        Object nested = source.get(firstKey);

        if (nested instanceof Map<?, ?> nestedMap) {
            return ((Map<String, Object>) nestedMap).get(secondKey);
        }

        return null;
    }

    private Object firstNonNull(Object... values) {
        for (Object value : values) {
            if (value != null) {
                return value;
            }
        }

        return null;
    }

    private String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }

        return "";
    }

    private String serializeResponse(RunResponse response) {
        return serializeObject(response);
    }

    private String serializeObject(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException error) {
            return "{}";
        }
    }
}
