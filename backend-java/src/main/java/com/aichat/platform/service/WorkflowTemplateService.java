package com.aichat.platform.service;

import com.aichat.platform.entity.WorkflowTemplateEntity;
import com.aichat.platform.entity.RunRecordEntity;
import com.aichat.platform.repository.WorkflowTemplateRepository;
import com.aichat.platform.repository.RunRecordRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.springframework.stereotype.Service;

@Service
public class WorkflowTemplateService {

    private static final DateTimeFormatter RUN_ID_FORMATTER =
            DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss").withZone(ZoneOffset.UTC);

    private final WorkflowTemplateRepository workflowTemplateRepository;
    private final RunRecordRepository runRecordRepository;
    private final RunEventService runEventService;
    private final ObjectMapper objectMapper;

    public WorkflowTemplateService(
            WorkflowTemplateRepository workflowTemplateRepository,
            RunRecordRepository runRecordRepository,
            RunEventService runEventService,
            ObjectMapper objectMapper
    ) {
        this.workflowTemplateRepository = workflowTemplateRepository;
        this.runRecordRepository = runRecordRepository;
        this.runEventService = runEventService;
        this.objectMapper = objectMapper;
    }

    public List<Map<String, Object>> listTemplates() {
        return workflowTemplateRepository.findAllByOrderByUpdatedAtDesc()
                .stream()
                .map(this::toResponse)
                .toList();
    }

    public Optional<Map<String, Object>> getTemplate(String templateKey) {
        return workflowTemplateRepository.findByTemplateKey(templateKey).map(this::toResponse);
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> saveTemplate(Map<String, Object> request) {
        if (request == null) {
            throw new IllegalArgumentException("template request is required");
        }

        String templateKey = firstNonBlank(
                asString(request.get("workflowTemplateKey")),
                asString(request.get("templateKey")),
                asString(request.get("key"))
        );

        if (templateKey.isBlank()) {
            throw new IllegalArgumentException("workflowTemplateKey is required");
        }

        Object rawNodes = request.get("nodes");
        List<Map<String, Object>> nodes = rawNodes instanceof List<?> list
                ? list.stream()
                        .filter(item -> item instanceof Map<?, ?>)
                        .map(item -> (Map<String, Object>) item)
                        .toList()
                : List.of();

        if (nodes.isEmpty()) {
            throw new IllegalArgumentException("workflow template must contain at least one node");
        }

        Optional<WorkflowTemplateEntity> existingEntity = workflowTemplateRepository.findByTemplateKey(templateKey);
        WorkflowTemplateEntity entity = existingEntity.orElseGet(WorkflowTemplateEntity::new);
        String nextVersion = existingEntity
                .map(existing -> nextVersion(existing.getVersion()))
                .orElse(firstNonBlank(asString(request.get("version")), "1.0"));
        Map<String, Object> normalizedRequest = new LinkedHashMap<>(request);
        normalizedRequest.put("workflowTemplateKey", templateKey);
        normalizedRequest.put("templateKey", templateKey);
        normalizedRequest.put("key", templateKey);
        normalizedRequest.put("version", nextVersion);

        entity.setTemplateKey(templateKey);
        entity.setName(firstNonBlank(asString(normalizedRequest.get("name")), templateKey));
        entity.setDescription(asString(normalizedRequest.get("description")));
        entity.setTemplateJson(serializeObject(normalizedRequest));
        entity.setAgentSequenceJson(serializeObject(extractValues(nodes, "agentKey")));
        entity.setStageSequenceJson(serializeObject(extractValues(nodes, "stage")));
        entity.setEnabled(true);
        entity.setVersion(nextVersion);

        return toResponse(workflowTemplateRepository.save(entity));
    }

    public Optional<Map<String, Object>> deleteTemplate(String templateKey) {
        Optional<WorkflowTemplateEntity> entity = workflowTemplateRepository.findByTemplateKey(templateKey);
        entity.ifPresent(workflowTemplateRepository::delete);
        return entity.map(this::toResponse);
    }

    @SuppressWarnings("unchecked")
    public Optional<Map<String, Object>> instantiateTemplate(String templateKey, Map<String, Object> request) {
        return workflowTemplateRepository.findByTemplateKey(templateKey).map(entity -> {
            Map<String, Object> template = toResponse(entity);
            Map<String, Object> safeRequest = request == null ? Map.of() : request;
            Map<String, Object> inputData = safeRequest.get("inputData") instanceof Map<?, ?> inputDataMap
                    ? (Map<String, Object>) inputDataMap
                    : safeRequest.get("input_data") instanceof Map<?, ?> snakeInputDataMap
                            ? (Map<String, Object>) snakeInputDataMap
                            : Map.of();
            List<Map<String, Object>> nodes = template.get("nodes") instanceof List<?> nodeList
                    ? nodeList.stream()
                            .filter(item -> item instanceof Map<?, ?>)
                            .map(item -> (Map<String, Object>) item)
                            .toList()
                    : List.of();
            String platformRunId = "workflow_template_" + RUN_ID_FORMATTER.format(Instant.now())
                    + "_" + UUID.randomUUID().toString().substring(0, 8);
            String requirement = firstNonBlank(
                    asString(inputData.get("requirement")),
                    "基于 Workflow 模板生成可回放任务视图: " + asString(template.get("name"))
            );
            List<Map<String, Object>> workflowEvents = buildWorkflowEvents(platformRunId, template, nodes);
            boolean waitingForHuman = containsHumanApproval(nodes);
            Map<String, Object> runSummary = buildTemplateRunSummary(platformRunId, template, workflowEvents);
            Map<String, Object> uiViewModel = buildTemplateUiViewModel(template, nodes, workflowEvents);

            RunRecordEntity record = new RunRecordEntity();
            record.setPlatformRunId(platformRunId);
            record.setPythonRunId("");
            record.setStatus(waitingForHuman ? "WAITING_FOR_HUMAN" : "SUCCESS");
            record.setRequirement(requirement);
            record.setModelProvider("workflow_template");
            record.setModelName("Workflow Template Replay");
            record.setModelBaseUrl("");
            record.setSuccess(!waitingForHuman);
            record.setRetryCount(0);
            record.setTestSuccess(true);
            record.setCoveragePercent(0);
            record.setQualityScore(100);
            record.setSecurityStatus("not_applicable");
            record.setReportPath("");
            record.setStatePath("");
            record.setRunnerMode("workflow_template");
            record.setRunnerWarning("模板实例化不会执行 LangGraph 或模型调用");
            record.setRunSummaryJson(serializeObject(runSummary));
            record.setUiViewModelJson(serializeObject(uiViewModel));
            record.setPluginResultsJson("[]");
            record.setErrorSummary("");
            record.setApproved(!waitingForHuman);
            record.setRequireHumanApproval(waitingForHuman);
            record.setRawResponse(serializeObject(Map.of(
                    "platformRunId", platformRunId,
                    "template", template,
                    "input_data", inputData,
                    "run_summary", runSummary,
                    "ui_view_model", uiViewModel,
                    "workflow_events", workflowEvents
            )));
            runRecordRepository.save(record);
            workflowEvents.forEach(event -> runEventService.addPythonWorkflowEvent(platformRunId, "", event));

            Map<String, Object> response = new LinkedHashMap<>();
            response.put("platformRunId", platformRunId);
            response.put("run_id", platformRunId);
            response.put("template_key", templateKey);
            response.put("input_data", inputData);
            response.put("workflow_events", workflowEvents);
            response.put("run_summary", runSummary);
            response.put("ui_view_model", uiViewModel);

            return response;
        });
    }

    private List<String> extractValues(List<Map<String, Object>> nodes, String key) {
        return nodes.stream()
                .map(node -> asString(node.get(key)))
                .filter(value -> !value.isBlank())
                .toList();
    }

    private List<Map<String, Object>> buildWorkflowEvents(
            String platformRunId,
            Map<String, Object> template,
            List<Map<String, Object>> nodes
    ) {
        List<Map<String, Object>> events = new java.util.ArrayList<>();
        events.add(workflowEvent(
                "WORKFLOW_STARTED",
                "Workflow 模板任务开始",
                "workflow",
                "RUNNING",
                "从 MySQL Workflow 模板生成可回放任务视图",
                Map.of("platformRunId", platformRunId, "templateKey", asString(template.get("templateKey")))
        ));

        for (Map<String, Object> node : nodes) {
            String agentKey = asString(node.get("agentKey"));
            String nodeName = firstNonBlank(asString(node.get("name")), agentKey);
            String stage = asString(node.get("stage"));
            boolean humanApprovalNode = "human_approval".equals(agentKey)
                    || "human_approval".equals(asString(node.get("nodeType")));

            if (humanApprovalNode) {
                events.add(workflowEvent(
                        "HUMAN_APPROVAL_REQUIRED",
                        nodeName + " 等待人工确认",
                        "human_approval",
                        "WAITING_FOR_HUMAN",
                        firstNonBlank(
                                asString(nestedValue(node, "humanApprovalConfig", "question")),
                                "请确认是否继续执行后续节点"
                        ),
                        Map.of(
                                "nodeId", asString(node.get("nodeId")),
                                "stage", stage,
                                "approval", node.get("humanApprovalConfig") == null ? Map.of() : node.get("humanApprovalConfig")
                        )
                ));
                break;
            }

            events.add(workflowEvent(
                    "AGENT_STARTED",
                    nodeName + " 开始执行",
                    agentKey,
                    "RUNNING",
                    "模板回放节点进入阶段: " + firstNonBlank(stage, "custom"),
                    Map.of("nodeId", asString(node.get("nodeId")), "stage", stage)
            ));
            events.add(workflowEvent(
                    "AGENT_FINISHED",
                    nodeName + " 执行完成",
                    agentKey,
                    "SUCCESS",
                    "模板回放节点已完成",
                    Map.of(
                            "nodeId", asString(node.get("nodeId")),
                            "input_fields", node.getOrDefault("input_fields", List.of()),
                            "output_fields", node.getOrDefault("output_fields", List.of())
                    )
            ));
        }

        boolean waitingForHuman = containsHumanApproval(nodes);
        events.add(workflowEvent(
                waitingForHuman ? "STATUS_CHANGED" : "WORKFLOW_FINISHED",
                waitingForHuman ? "Workflow 模板等待人工确认" : "Workflow 模板任务完成",
                "workflow",
                waitingForHuman ? "WAITING_FOR_HUMAN" : "SUCCESS",
                waitingForHuman ? "平台任务已暂停，等待用户批准或拒绝" : "可回放任务视图已生成",
                Map.of("platformRunId", platformRunId, "nodeCount", nodes.size())
        ));

        return events;
    }

    private boolean containsHumanApproval(List<Map<String, Object>> nodes) {
        return nodes.stream().anyMatch(node ->
                "human_approval".equals(asString(node.get("agentKey")))
                        || "human_approval".equals(asString(node.get("nodeType")))
        );
    }

    private Map<String, Object> workflowEvent(
            String eventType,
            String eventText,
            String agent,
            String status,
            String message,
            Object detail
    ) {
        Map<String, Object> event = new LinkedHashMap<>();
        event.put("event_type", eventType);
        event.put("event_text", eventText);
        event.put("agent", agent);
        event.put("status", status);
        event.put("message", message);
        event.put("detail", detail);
        event.put("created_at", java.time.LocalDateTime.now().toString());

        return event;
    }

    private Map<String, Object> buildTemplateRunSummary(
            String platformRunId,
            Map<String, Object> template,
            List<Map<String, Object>> workflowEvents
    ) {
        boolean waitingForHuman = workflowEvents.stream()
                .anyMatch(event -> "WAITING_FOR_HUMAN".equals(asString(event.get("status"))));
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("success", !waitingForHuman);
        summary.put("retry_count", 0);
        summary.put("test_success", true);
        summary.put("coverage_percent", 0);
        summary.put("quality_score", 100);
        summary.put("security_status", "not_applicable");
        summary.put("model_provider", "workflow_template");
        summary.put("runner_mode", "workflow_template");
        summary.put("runner_warning", "模板实例化不会执行 LangGraph 或模型调用");
        summary.put("status", waitingForHuman ? "WAITING_FOR_HUMAN" : "SUCCESS");
        summary.put("require_human_approval", waitingForHuman);
        summary.put("approved", !waitingForHuman);
        summary.put("report_path", "");
        summary.put("platformRunId", platformRunId);
        summary.put("workflow_template", template.get("templateKey"));
        summary.put("workflow_template_name", template.get("name"));
        summary.put("event_count", workflowEvents.size());
        summary.put("last_event", workflowEvents.isEmpty() ? Map.of() : workflowEvents.get(workflowEvents.size() - 1));

        return summary;
    }

    private Map<String, Object> buildTemplateUiViewModel(
            Map<String, Object> template,
            List<Map<String, Object>> nodes,
            List<Map<String, Object>> workflowEvents
    ) {
        List<Map<String, Object>> workflowSteps = new java.util.ArrayList<>();

        for (int index = 0; index < nodes.size(); index += 1) {
            Map<String, Object> node = nodes.get(index);
            Map<String, Object> step = new LinkedHashMap<>();
            step.put("key", firstNonBlank(asString(node.get("nodeId")), asString(node.get("agentKey")) + "_" + (index + 1)));
            step.put("agent_key", asString(node.get("agentKey")));
            step.put("label", firstNonBlank(asString(node.get("name")), asString(node.get("agentKey"))));
            boolean waitingNode = "human_approval".equals(asString(node.get("agentKey")))
                    || "human_approval".equals(asString(node.get("nodeType")));
            step.put("status", waitingNode ? "waiting" : "done");
            step.put("summary", waitingNode ? "等待人工确认" : "模板回放节点已完成");
            step.put("order", index + 1);
            workflowSteps.add(step);
        }

        Map<String, Object> uiViewModel = new LinkedHashMap<>();
        uiViewModel.put("workflow_template", template);
        uiViewModel.put("workflow_steps", workflowSteps);
        uiViewModel.put("workflow_events", workflowEvents);
        uiViewModel.put("agent_outputs", Map.of(
                "stdout", serializeObject(template),
                "error_summary", ""
        ));
        uiViewModel.put("plugin_outputs", Map.of("plugin_results", List.of()));
        uiViewModel.put("report", Map.of());
        uiViewModel.put("raw", template);

        return uiViewModel;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> toResponse(WorkflowTemplateEntity entity) {
        Map<String, Object> templateData = parseJsonMap(entity.getTemplateJson());
        Map<String, Object> response = new LinkedHashMap<>(templateData);
        response.put("id", entity.getId());
        response.put("workflowTemplateKey", firstNonBlank(asString(templateData.get("workflowTemplateKey")), entity.getTemplateKey()));
        response.put("templateKey", entity.getTemplateKey());
        response.put("key", entity.getTemplateKey());
        response.put("name", firstNonBlank(asString(templateData.get("name")), entity.getName()));
        response.put("description", firstNonBlank(asString(templateData.get("description")), entity.getDescription()));
        response.put("nodes", templateData.getOrDefault("nodes", List.of()));
        response.put("connections", templateData.getOrDefault("connections", List.of()));
        response.put("version", firstNonBlank(asString(templateData.get("version")), entity.getVersion(), "1.0"));
        response.put("enabled", entity.isEnabled());
        response.put("agent_sequence", parseStringList(entity.getAgentSequenceJson()));
        response.put("stage_sequence", parseStringList(entity.getStageSequenceJson()));
        response.put("source", "java-mysql");
        response.put("createdAt", entity.getCreatedAt() == null ? "" : entity.getCreatedAt().toString());
        response.put("updatedAt", entity.getUpdatedAt() == null ? "" : entity.getUpdatedAt().toString());

        return response;
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
            // Broken template JSON should not break list rendering.
        }

        return Map.of();
    }

    private List<String> parseStringList(String rawJson) {
        if (rawJson == null || rawJson.isBlank()) {
            return List.of();
        }

        try {
            Object parsed = objectMapper.readValue(rawJson, Object.class);
            if (parsed instanceof List<?> list) {
                return list.stream().map(this::asString).filter(value -> !value.isBlank()).toList();
            }
        } catch (Exception ignored) {
            // Broken sequence JSON should return an empty sequence.
        }

        return List.of();
    }

    private String serializeObject(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException error) {
            return "{}";
        }
    }

    private String asString(Object value) {
        return value == null ? "" : String.valueOf(value);
    }

    @SuppressWarnings("unchecked")
    private Object nestedValue(Map<String, Object> source, String firstKey, String secondKey) {
        Object nested = source.get(firstKey);

        if (nested instanceof Map<?, ?> nestedMap) {
            return ((Map<String, Object>) nestedMap).get(secondKey);
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

    private String nextVersion(String currentVersion) {
        String normalizedVersion = firstNonBlank(currentVersion, "1.0");
        String[] parts = normalizedVersion.split("\\.");

        if (parts.length == 0) {
            return "1.1";
        }

        try {
            int lastIndex = parts.length - 1;
            int patch = Integer.parseInt(parts[lastIndex]);
            parts[lastIndex] = String.valueOf(patch + 1);
            return String.join(".", parts);
        } catch (NumberFormatException error) {
            return normalizedVersion + ".1";
        }
    }
}
