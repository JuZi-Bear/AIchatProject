package com.aichat.platform.service;

import com.aichat.platform.entity.RunRecordEntity;
import com.aichat.platform.repository.RunRecordRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.springframework.stereotype.Service;

@Service
public class PlatformDynamicWorkflowService {

    private final WorkflowTemplateService workflowTemplateService;
    private final PythonAgentClient pythonAgentClient;
    private final RunRecordRepository runRecordRepository;
    private final RunEventService runEventService;
    private final ReportIndexService reportIndexService;
    private final ObjectMapper objectMapper;

    public PlatformDynamicWorkflowService(
            WorkflowTemplateService workflowTemplateService,
            PythonAgentClient pythonAgentClient,
            RunRecordRepository runRecordRepository,
            RunEventService runEventService,
            ReportIndexService reportIndexService,
            ObjectMapper objectMapper
    ) {
        this.workflowTemplateService = workflowTemplateService;
        this.pythonAgentClient = pythonAgentClient;
        this.runRecordRepository = runRecordRepository;
        this.runEventService = runEventService;
        this.reportIndexService = reportIndexService;
        this.objectMapper = objectMapper;
    }

    public Optional<Map<String, Object>> validateTemplate(String templateKey, Map<String, Object> request) {
        return workflowTemplateService.getTemplate(templateKey).map(template -> {
            Map<String, Object> payload = buildPythonPayload(template, request, "");
            return pythonAgentClient.validateDynamicWorkflow(payload);
        });
    }

    public Optional<Map<String, Object>> executeTemplate(String templateKey, Map<String, Object> request) {
        return workflowTemplateService.getTemplate(templateKey).map(template -> {
            String platformRunId = "dynamic_langgraph_" + Instant.now().toEpochMilli();
            Map<String, Object> response = pythonAgentClient.executeDynamicWorkflow(buildPythonPayload(template, request, platformRunId));
            saveOrUpdateRunRecord(platformRunId, template, response, false);
            return response;
        });
    }

    public Optional<Map<String, Object>> resumeRun(String platformRunId, Map<String, Object> request) {
        return runRecordRepository.findByPlatformRunId(platformRunId).map(record -> {
            Map<String, Object> response = pythonAgentClient.resumeDynamicWorkflow(platformRunId, request == null ? Map.of() : request);
            Map<String, Object> template = extractTemplate(record);
            saveOrUpdateRunRecord(platformRunId, template, response, true);
            return response;
        });
    }

    private Map<String, Object> buildPythonPayload(Map<String, Object> template, Map<String, Object> request, String platformRunId) {
        Map<String, Object> safeRequest = request == null ? Map.of() : request;
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("template", template);
        payload.put("input_data", inputData(safeRequest));

        if (platformRunId != null && !platformRunId.isBlank()) {
            payload.put("platform_run_id", platformRunId);
            payload.put("run_id", platformRunId);
        }

        return payload;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> inputData(Map<String, Object> request) {
        Object inputData = request.get("input_data");

        if (inputData instanceof Map<?, ?> inputMap) {
            return (Map<String, Object>) inputMap;
        }

        inputData = request.get("inputData");

        if (inputData instanceof Map<?, ?> inputMap) {
            return (Map<String, Object>) inputMap;
        }

        return request;
    }

    private void saveOrUpdateRunRecord(
            String platformRunId,
            Map<String, Object> template,
            Map<String, Object> response,
            boolean appendOnlyNewEvents
    ) {
        RunRecordEntity record = runRecordRepository.findByPlatformRunId(platformRunId).orElseGet(RunRecordEntity::new);
        Map<String, Object> runSummary = mapValue(response.get("run_summary"));
        Map<String, Object> uiViewModel = mapValue(response.get("ui_view_model"));
        String status = firstNonBlank(asString(response.get("status")), asString(runSummary.get("status")), "UNKNOWN");
        boolean success = "SUCCESS".equals(status);
        boolean waiting = "WAITING_FOR_HUMAN".equals(status);
        String reportPath = firstNonBlank(asString(runSummary.get("report_path")), asString(nestedValue(uiViewModel, "runtime_summary", "report_path")));

        record.setPlatformRunId(platformRunId);
        record.setPythonRunId(firstNonBlank(asString(response.get("run_id")), platformRunId));
        record.setStatus(status);
        record.setRequirement(firstNonBlank(
                asString(nestedValue(response, "input_data", "requirement")),
                "Dynamic LangGraph: " + firstNonBlank(asString(template.get("name")), asString(template.get("templateKey")))
        ));
        record.setModelProvider("dynamic_langgraph");
        record.setModelName("Dynamic LangGraph Runtime");
        record.setModelBaseUrl("");
        record.setSuccess(success);
        record.setRetryCount(0);
        record.setTestSuccess(success || waiting);
        record.setCoveragePercent(0);
        record.setQualityScore(success ? 100 : waiting ? 80 : 0);
        record.setSecurityStatus(success ? "dynamic_completed" : waiting ? "waiting_for_human" : "dynamic_failed");
        record.setReportPath(reportPath);
        record.setStatePath(asString(runSummary.get("state_path")));
        record.setRunnerMode("dynamic_langgraph");
        record.setRunnerWarning("Python Agent Engine 动态编译受控 LangGraph 执行图");
        record.setRunSummaryJson(serializeObject(runSummary));
        record.setUiViewModelJson(serializeObject(uiViewModel));
        record.setPluginResultsJson("[]");
        record.setErrorSummary(success || waiting ? "" : firstNonBlank(asString(runSummary.get("runner_warning")), "Dynamic LangGraph 执行失败"));
        record.setApproved(success);
        record.setRequireHumanApproval(waiting);
        record.setRawResponse(serializeObject(Map.of(
                "template", template,
                "response", response
        )));
        RunRecordEntity savedRecord = runRecordRepository.save(record);
        persistWorkflowEvents(platformRunId, asString(response.get("run_id")), listValue(response.get("workflow_events")), appendOnlyNewEvents);
        reportIndexService.saveReportIndexFromRunRecord(savedRecord);
    }

    private void persistWorkflowEvents(
            String platformRunId,
            String pythonRunId,
            List<Map<String, Object>> events,
            boolean appendOnlyNewEvents
    ) {
        int offset = appendOnlyNewEvents ? runEventService.listEventsByRun(platformRunId).size() : 0;

        for (int index = offset; index < events.size(); index += 1) {
            runEventService.addPythonWorkflowEvent(platformRunId, pythonRunId, events.get(index));
        }
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> extractTemplate(RunRecordEntity record) {
        try {
            Object parsed = objectMapper.readValue(record.getRawResponse(), Object.class);

            if (parsed instanceof Map<?, ?> parsedMap) {
                Object template = ((Map<String, Object>) parsedMap).get("template");

                if (template instanceof Map<?, ?> templateMap) {
                    return (Map<String, Object>) templateMap;
                }
            }
        } catch (Exception ignored) {
            // Template metadata is optional for resume persistence.
        }

        return Map.of();
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> mapValue(Object value) {
        return value instanceof Map<?, ?> map ? (Map<String, Object>) map : Map.of();
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> listValue(Object value) {
        if (!(value instanceof List<?> list)) {
            return List.of();
        }

        return list.stream()
                .filter(item -> item instanceof Map<?, ?>)
                .map(item -> (Map<String, Object>) item)
                .toList();
    }

    @SuppressWarnings("unchecked")
    private Object nestedValue(Map<String, Object> source, String key, String nestedKey) {
        Object value = source.get(key);

        if (value instanceof Map<?, ?> map) {
            return ((Map<String, Object>) map).get(nestedKey);
        }

        return null;
    }

    private String serializeObject(Object value) {
        try {
            return objectMapper.writeValueAsString(value == null ? Map.of() : value);
        } catch (JsonProcessingException error) {
            return "{}";
        }
    }

    private String asString(Object value) {
        return value == null ? "" : String.valueOf(value);
    }

    private String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }

        return "";
    }
}
