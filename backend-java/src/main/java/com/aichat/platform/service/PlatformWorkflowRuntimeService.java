package com.aichat.platform.service;

import com.aichat.platform.entity.RunRecordEntity;
import com.aichat.platform.model.RunEventType;
import com.aichat.platform.repository.RunRecordRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.LocalDateTime;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.springframework.stereotype.Service;

@Service
public class PlatformWorkflowRuntimeService {

    private final WorkflowTemplateService workflowTemplateService;
    private final RunRecordRepository runRecordRepository;
    private final RunEventService runEventService;
    private final PythonAgentClient pythonAgentClient;
    private final ObjectMapper objectMapper;

    public PlatformWorkflowRuntimeService(
            WorkflowTemplateService workflowTemplateService,
            RunRecordRepository runRecordRepository,
            RunEventService runEventService,
            PythonAgentClient pythonAgentClient,
            ObjectMapper objectMapper
    ) {
        this.workflowTemplateService = workflowTemplateService;
        this.runRecordRepository = runRecordRepository;
        this.runEventService = runEventService;
        this.pythonAgentClient = pythonAgentClient;
        this.objectMapper = objectMapper;
    }

    @SuppressWarnings("unchecked")
    public Optional<Map<String, Object>> executeTemplate(String templateKey, Map<String, Object> request) {
        return workflowTemplateService.getTemplate(templateKey).map(template -> {
            Map<String, Object> safeRequest = request == null ? Map.of() : request;
            Map<String, Object> inputData = safeRequest.get("inputData") instanceof Map<?, ?> inputDataMap
                    ? (Map<String, Object>) inputDataMap
                    : safeRequest.get("input_data") instanceof Map<?, ?> snakeInputDataMap
                            ? (Map<String, Object>) snakeInputDataMap
                            : Map.of();
            List<Map<String, Object>> nodes = mapList(template.get("nodes"));
            List<Map<String, Object>> connections = mapList(template.get("connections"));
            List<Map<String, Object>> orderedNodes = orderNodes(nodes, connections);
            List<Map<String, Object>> workflowEvents = new ArrayList<>();
            List<String> warnings = buildConnectionWarnings(nodes, connections, orderedNodes);
            String platformRunId = "workflow_runtime_" + java.time.Instant.now().toEpochMilli();
            String requirement = firstNonBlank(
                    asString(inputData.get("requirement")),
                    "执行 Workflow Runtime Lite: " + asString(template.get("name"))
            );

            RunRecordEntity record = createInitialRecord(platformRunId, requirement, template);
            runRecordRepository.save(record);
            appendWorkflowEvent(workflowEvents, platformRunId, workflowEvent(
                    "WORKFLOW_STARTED",
                    "Workflow Runtime Lite 开始执行",
                    "workflow",
                    "RUNNING",
                    "平台层按模板节点顺序执行可控节点",
                    Map.of(
                            "templateKey", templateKey,
                            "runtimeMode", "workflow_runtime_lite",
                            "warnings", warnings
                    )
            ));

            String status = "SUCCESS";
            boolean success = true;
            boolean waitingForHuman = false;
            String errorSummary = "";

            for (Map<String, Object> node : orderedNodes) {
                String nodeType = firstNonBlank(asString(node.get("nodeType")), asString(node.get("agentKey")));
                String agentKey = firstNonBlank(asString(node.get("agentKey")), nodeType);
                String nodeName = firstNonBlank(asString(node.get("name")), agentKey);

                if (isHumanApprovalNode(node)) {
                    status = "WAITING_FOR_HUMAN";
                    success = false;
                    waitingForHuman = true;
                    appendWorkflowEvent(workflowEvents, platformRunId, workflowEvent(
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
                                    "executionMode", "waiting",
                                    "approval", node.get("humanApprovalConfig") == null ? Map.of() : node.get("humanApprovalConfig")
                            )
                    ));
                    break;
                }

                appendWorkflowEvent(workflowEvents, platformRunId, workflowEvent(
                        "AGENT_STARTED",
                        nodeName + " 开始执行",
                        agentKey,
                        "RUNNING",
                        nodeExecutionMode(node) + " 节点进入执行阶段",
                        Map.of(
                                "nodeId", asString(node.get("nodeId")),
                                "stage", asString(node.get("stage")),
                                "executionMode", nodeExecutionMode(node)
                        )
                ));

                if (isCodeAgentNode(node)) {
                    Map<String, Object> codeAgentResponse;

                    try {
                        codeAgentResponse = executeCodeAgentNode(platformRunId, node);
                        persistPythonWorkflowEvents(platformRunId, codeAgentResponse.get("events"), workflowEvents);
                    } catch (Exception error) {
                        status = "FAILED";
                        success = false;
                        errorSummary = "CodeAgent 节点调用 Python Agent Engine 失败: " + error.getMessage();
                        appendWorkflowEvent(workflowEvents, platformRunId, workflowEvent(
                                "AGENT_FAILED",
                                nodeName + " 调用失败",
                                "code_agent",
                                "FAILED",
                                errorSummary,
                                Map.of("nodeId", asString(node.get("nodeId")), "executionMode", "executed")
                        ));
                        break;
                    }

                    if (!asBoolean(codeAgentResponse.get("success"))) {
                        status = "FAILED";
                        success = false;
                        errorSummary = firstNonBlank(asString(codeAgentResponse.get("message")), "CodeAgent 节点执行失败");
                        appendWorkflowEvent(workflowEvents, platformRunId, workflowEvent(
                                "AGENT_FAILED",
                                nodeName + " 执行失败",
                                "code_agent",
                                "FAILED",
                                errorSummary,
                                Map.of("nodeId", asString(node.get("nodeId")), "executionMode", "executed")
                        ));
                        break;
                    }

                    appendWorkflowEvent(workflowEvents, platformRunId, workflowEvent(
                            "AGENT_FINISHED",
                            nodeName + " 执行完成",
                            "code_agent",
                            "SUCCESS",
                            firstNonBlank(asString(codeAgentResponse.get("message")), "CodeAgent 文件操作完成"),
                            Map.of(
                                    "nodeId", asString(node.get("nodeId")),
                                    "executionMode", "executed",
                                    "operation", asString(codeAgentResponse.get("operation")),
                                    "filePath", asString(codeAgentResponse.get("filePath"))
                            )
                    ));
                } else {
                    appendWorkflowEvent(workflowEvents, platformRunId, workflowEvent(
                            "AGENT_FINISHED",
                            nodeName + " 平台事件节点完成",
                            agentKey,
                            "SUCCESS",
                            "Workflow Runtime Lite 第一版不调用该 Agent 的真实 LangGraph 逻辑",
                            Map.of(
                                    "nodeId", asString(node.get("nodeId")),
                                    "stage", asString(node.get("stage")),
                                    "executionMode", "simulated"
                            )
                    ));
                }
            }

            if (!waitingForHuman && success) {
                appendWorkflowEvent(workflowEvents, platformRunId, workflowEvent(
                        "WORKFLOW_FINISHED",
                        "Workflow Runtime Lite 执行完成",
                        "workflow",
                        "SUCCESS",
                        "平台层模板执行链路已完成",
                        Map.of("templateKey", templateKey, "nodeCount", orderedNodes.size())
                ));
            }

            RunRecordEntity savedRecord = finalizeRecord(
                    record,
                    status,
                    success,
                    waitingForHuman,
                    errorSummary,
                    template,
                    orderedNodes,
                    workflowEvents,
                    warnings
            );

            Map<String, Object> response = new LinkedHashMap<>();
            response.put("platformRunId", platformRunId);
            response.put("run_id", platformRunId);
            response.put("template_key", templateKey);
            response.put("status", savedRecord.getStatus());
            response.put("events", workflowEvents);
            response.put("workflow_events", workflowEvents);
            response.put("warnings", warnings);
            response.put("run_summary", parseJsonMap(savedRecord.getRunSummaryJson()));
            response.put("ui_view_model", parseJsonMap(savedRecord.getUiViewModelJson()));

            return response;
        });
    }

    private RunRecordEntity createInitialRecord(String platformRunId, String requirement, Map<String, Object> template) {
        RunRecordEntity record = new RunRecordEntity();
        record.setPlatformRunId(platformRunId);
        record.setPythonRunId("");
        record.setStatus("RUNNING");
        record.setRequirement(requirement);
        record.setModelProvider("workflow_runtime");
        record.setModelName("Workflow Runtime Lite");
        record.setModelBaseUrl("");
        record.setSuccess(false);
        record.setRetryCount(0);
        record.setTestSuccess(false);
        record.setCoveragePercent(0);
        record.setQualityScore(0);
        record.setSecurityStatus("runtime_pending");
        record.setReportPath("");
        record.setStatePath("");
        record.setRunnerMode("workflow_runtime");
        record.setRunnerWarning("平台层演示执行器，不动态改写 LangGraph");
        record.setRunSummaryJson("{}");
        record.setUiViewModelJson("{}");
        record.setPluginResultsJson("[]");
        record.setErrorSummary("");
        record.setApproved(false);
        record.setRequireHumanApproval(false);
        record.setRawResponse(serializeObject(Map.of("template", template)));
        return record;
    }

    private RunRecordEntity finalizeRecord(
            RunRecordEntity record,
            String status,
            boolean success,
            boolean waitingForHuman,
            String errorSummary,
            Map<String, Object> template,
            List<Map<String, Object>> nodes,
            List<Map<String, Object>> workflowEvents,
            List<String> warnings
    ) {
        record.setStatus(status);
        record.setSuccess(success);
        record.setTestSuccess(success || waitingForHuman);
        record.setQualityScore(success ? 100 : waitingForHuman ? 80 : 0);
        record.setSecurityStatus(success ? "runtime_completed" : waitingForHuman ? "waiting_for_human" : "runtime_failed");
        record.setErrorSummary(errorSummary);
        record.setApproved(success && !waitingForHuman);
        record.setRequireHumanApproval(waitingForHuman);
        record.setRunnerWarning(warnings.isEmpty() ? "平台层演示执行器，不动态改写 LangGraph" : String.join("; ", warnings));
        record.setRunSummaryJson(serializeObject(buildRunSummary(record, template, workflowEvents, warnings)));
        record.setUiViewModelJson(serializeObject(buildUiViewModel(template, nodes, workflowEvents)));
        record.setRawResponse(serializeObject(Map.of(
                "template", template,
                "workflow_events", workflowEvents,
                "warnings", warnings,
                "status", status
        )));
        return runRecordRepository.save(record);
    }

    private Map<String, Object> executeCodeAgentNode(String platformRunId, Map<String, Object> node) {
        Map<String, Object> config = nestedMap(node, "codeAgentConfig");
        String operation = firstNonBlank(asString(config.get("operation")), "write_file");
        String targetPath = firstNonBlank(
                asString(config.get("target_path")),
                asString(config.get("baseDir")),
                "output/code_agent_runtime.txt"
        );
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("platformRunId", platformRunId);
        request.put("operation", operation);
        request.put("filePath", targetPath);
        request.put("content", firstNonBlank(asString(config.get("content")), "# Workflow Runtime Lite CodeAgent output\n"));
        request.put("includePatterns", config.getOrDefault("includePatterns", "**/*.md, **/*.txt, **/*.py"));
        request.put("excludePatterns", config.getOrDefault("excludePatterns", ".env, .git/**, node_modules/**, dist/**, target/**"));
        request.put("outputFile", firstNonBlank(asString(config.get("outputFile")), "workflow_runtime_result.md"));
        request.put("dryRun", config.getOrDefault("dryRun", true));
        request.put("backupBeforeWrite", config.getOrDefault("backupBeforeWrite", true));

        return pythonAgentClient.executeCodeAgent(request);
    }

    private void appendWorkflowEvent(List<Map<String, Object>> workflowEvents, String platformRunId, Map<String, Object> event) {
        workflowEvents.add(event);
        runEventService.addPythonWorkflowEvent(platformRunId, "", event);
    }

    @SuppressWarnings("unchecked")
    private void persistPythonWorkflowEvents(
            String platformRunId,
            Object rawEvents,
            List<Map<String, Object>> workflowEvents
    ) {
        if (!(rawEvents instanceof List<?> events)) {
            return;
        }

        for (Object event : events) {
            if (event instanceof Map<?, ?> eventMap) {
                Map<String, Object> typedEvent = (Map<String, Object>) eventMap;
                workflowEvents.add(typedEvent);
                runEventService.addPythonWorkflowEvent(platformRunId, "", typedEvent);
            }
        }
    }

    private List<Map<String, Object>> orderNodes(List<Map<String, Object>> nodes, List<Map<String, Object>> connections) {
        if (nodes.isEmpty() || connections.isEmpty()) {
            return nodes;
        }

        Map<String, Map<String, Object>> nodeById = new LinkedHashMap<>();
        Map<String, Integer> indegree = new HashMap<>();
        Map<String, List<String>> outgoing = new HashMap<>();

        for (Map<String, Object> node : nodes) {
            String nodeId = asString(node.get("nodeId"));
            nodeById.put(nodeId, node);
            indegree.put(nodeId, 0);
            outgoing.put(nodeId, new ArrayList<>());
        }

        for (Map<String, Object> connection : connections) {
            String from = asString(connection.get("fromNodeId"));
            String to = asString(connection.get("toNodeId"));

            if (nodeById.containsKey(from) && nodeById.containsKey(to) && !from.equals(to)) {
                outgoing.get(from).add(to);
                indegree.put(to, indegree.getOrDefault(to, 0) + 1);
            }
        }

        ArrayDeque<String> queue = new ArrayDeque<>();
        nodes.stream()
                .map(node -> asString(node.get("nodeId")))
                .filter(nodeId -> indegree.getOrDefault(nodeId, 0) == 0)
                .forEach(queue::add);

        List<Map<String, Object>> ordered = new ArrayList<>();
        Set<String> visited = new HashSet<>();

        while (!queue.isEmpty()) {
            String nodeId = queue.removeFirst();

            if (!visited.add(nodeId)) {
                continue;
            }

            ordered.add(nodeById.get(nodeId));
            outgoing.getOrDefault(nodeId, List.of())
                    .stream()
                    .sorted(Comparator.comparing(target -> asString(nodeById.get(target).get("position"))))
                    .forEach(target -> {
                        int next = indegree.getOrDefault(target, 0) - 1;
                        indegree.put(target, next);

                        if (next <= 0) {
                            queue.add(target);
                        }
                    });
        }

        if (ordered.size() != nodes.size()) {
            return nodes;
        }

        return ordered;
    }

    private List<String> buildConnectionWarnings(
            List<Map<String, Object>> nodes,
            List<Map<String, Object>> connections,
            List<Map<String, Object>> orderedNodes
    ) {
        List<String> warnings = new ArrayList<>();
        Set<String> nodeIds = new HashSet<>();
        nodes.forEach(node -> nodeIds.add(asString(node.get("nodeId"))));

        for (Map<String, Object> connection : connections) {
            String from = asString(connection.get("fromNodeId"));
            String to = asString(connection.get("toNodeId"));

            if (!nodeIds.contains(from) || !nodeIds.contains(to)) {
                warnings.add("存在断裂连线，Runtime Lite 已忽略无效连接");
                break;
            }

            if (from.equals(to)) {
                warnings.add("存在自连接，Runtime Lite 已按节点顺序兜底");
                break;
            }
        }

        if (orderedNodes.size() != nodes.size()) {
            warnings.add("检测到循环或复杂分支，Runtime Lite 已回退为模板节点顺序");
        }

        if (connections.size() > Math.max(0, nodes.size() - 1)) {
            warnings.add("检测到多分支连接，Runtime Lite 第一版只按拓扑顺序串行展开");
        }

        return warnings.stream().distinct().toList();
    }

    private Map<String, Object> buildRunSummary(
            RunRecordEntity record,
            Map<String, Object> template,
            List<Map<String, Object>> workflowEvents,
            List<String> warnings
    ) {
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("success", record.isSuccess());
        summary.put("retry_count", 0);
        summary.put("test_success", record.isTestSuccess());
        summary.put("coverage_percent", 0);
        summary.put("quality_score", record.getQualityScore());
        summary.put("security_status", record.getSecurityStatus());
        summary.put("model_provider", "workflow_runtime");
        summary.put("runner_mode", "workflow_runtime");
        summary.put("runner_warning", record.getRunnerWarning());
        summary.put("status", record.getStatus());
        summary.put("require_human_approval", record.isRequireHumanApproval());
        summary.put("approved", record.isApproved());
        summary.put("report_path", "");
        summary.put("platformRunId", record.getPlatformRunId());
        summary.put("workflow_template", template.get("templateKey"));
        summary.put("workflow_template_name", template.get("name"));
        summary.put("runtime_mode", "workflow_runtime_lite");
        summary.put("warnings", warnings);
        summary.put("event_count", workflowEvents.size());
        summary.put("last_event", workflowEvents.isEmpty() ? Map.of() : workflowEvents.get(workflowEvents.size() - 1));
        return summary;
    }

    private Map<String, Object> buildUiViewModel(
            Map<String, Object> template,
            List<Map<String, Object>> nodes,
            List<Map<String, Object>> workflowEvents
    ) {
        List<Map<String, Object>> workflowSteps = new ArrayList<>();

        for (int index = 0; index < nodes.size(); index += 1) {
            Map<String, Object> node = nodes.get(index);
            Map<String, Object> step = new LinkedHashMap<>();
            step.put("key", firstNonBlank(asString(node.get("nodeId")), asString(node.get("agentKey")) + "_" + (index + 1)));
            step.put("agent_key", asString(node.get("agentKey")));
            step.put("label", firstNonBlank(asString(node.get("name")), asString(node.get("agentKey"))));
            step.put("status", stepStatus(node, workflowEvents));
            step.put("summary", nodeExecutionMode(node) + " 节点");
            step.put("order", index + 1);
            workflowSteps.add(step);
        }

        Map<String, Object> uiViewModel = new LinkedHashMap<>();
        uiViewModel.put("workflow_template", template);
        uiViewModel.put("workflow_steps", workflowSteps);
        uiViewModel.put("workflow_events", workflowEvents);
        uiViewModel.put("agent_outputs", Map.of(
                "stdout", "Workflow Runtime Lite 平台层执行结果",
                "error_summary", ""
        ));
        uiViewModel.put("plugin_outputs", Map.of("plugin_results", List.of()));
        uiViewModel.put("report", Map.of());
        uiViewModel.put("raw", template);
        return uiViewModel;
    }

    private String stepStatus(Map<String, Object> node, List<Map<String, Object>> workflowEvents) {
        String nodeId = asString(node.get("nodeId"));

        return workflowEvents.stream()
                .filter(event -> nodeId.equals(asString(nestedValue(event, "detail", "nodeId"))))
                .map(event -> asString(event.get("status")))
                .filter(status -> !status.isBlank())
                .reduce((first, second) -> second)
                .map(status -> switch (status) {
                    case "SUCCESS", "APPROVED" -> "done";
                    case "FAILED", "REJECTED" -> "failed";
                    case "WAITING_FOR_HUMAN" -> "running";
                    default -> "done";
                })
                .orElse("waiting");
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
        event.put("created_at", LocalDateTime.now().toString());
        return event;
    }

    private boolean isCodeAgentNode(Map<String, Object> node) {
        return "code_agent".equals(asString(node.get("agentKey"))) || "code_agent".equals(asString(node.get("nodeType")));
    }

    private boolean isHumanApprovalNode(Map<String, Object> node) {
        return "human_approval".equals(asString(node.get("agentKey"))) || "human_approval".equals(asString(node.get("nodeType")));
    }

    private String nodeExecutionMode(Map<String, Object> node) {
        if (isCodeAgentNode(node)) {
            return "executed";
        }

        if (isHumanApprovalNode(node)) {
            return "waiting";
        }

        return "simulated";
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> mapList(Object value) {
        if (!(value instanceof List<?> list)) {
            return List.of();
        }

        return list.stream()
                .filter(item -> item instanceof Map<?, ?>)
                .map(item -> (Map<String, Object>) item)
                .toList();
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> nestedMap(Map<String, Object> source, String key) {
        Object value = source.get(key);
        return value instanceof Map<?, ?> map ? (Map<String, Object>) map : Map.of();
    }

    private Object nestedValue(Map<String, Object> source, String key, String nestedKey) {
        Object value = source.get(key);

        if (value instanceof Map<?, ?> map) {
            return map.get(nestedKey);
        }

        return null;
    }

    private Map<String, Object> parseJsonMap(String rawJson) {
        if (rawJson == null || rawJson.isBlank()) {
            return Map.of();
        }

        try {
            Object parsed = objectMapper.readValue(rawJson, Object.class);

            if (parsed instanceof Map<?, ?> parsedMap) {
                @SuppressWarnings("unchecked")
                Map<String, Object> typed = (Map<String, Object>) parsedMap;
                return typed;
            }
        } catch (Exception ignored) {
            // Runtime response should survive broken optional JSON.
        }

        return Map.of();
    }

    private boolean asBoolean(Object value) {
        if (value instanceof Boolean bool) {
            return bool;
        }

        return Boolean.parseBoolean(asString(value));
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
