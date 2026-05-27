package com.aichat.platform.service;

import com.aichat.platform.entity.RunRecordEntity;
import com.aichat.platform.model.RunEventType;
import com.aichat.platform.repository.RunRecordRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
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
    private final ReportIndexService reportIndexService;
    private final ObjectMapper objectMapper;

    public PlatformWorkflowRuntimeService(
            WorkflowTemplateService workflowTemplateService,
            RunRecordRepository runRecordRepository,
            RunEventService runEventService,
            PythonAgentClient pythonAgentClient,
            ReportIndexService reportIndexService,
            ObjectMapper objectMapper
    ) {
        this.workflowTemplateService = workflowTemplateService;
        this.runRecordRepository = runRecordRepository;
        this.runEventService = runEventService;
        this.pythonAgentClient = pythonAgentClient;
        this.reportIndexService = reportIndexService;
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
            List<Map<String, Object>> connectionMappings = buildConnectionMappings(nodes, connections);
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
                            "warnings", warnings,
                            "connectionMappings", connectionMappings
                    )
            ));

            String status = "SUCCESS";
            boolean success = true;
            boolean waitingForHuman = false;
            String errorSummary = "";
            String reportPath = "";
            Map<String, Object> codeAgentSummary = Map.of();

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
                                "executionMode", nodeExecutionMode(node),
                                "inputMappings", mappingsForNode(connectionMappings, asString(node.get("nodeId")), "input"),
                                "outputMappings", mappingsForNode(connectionMappings, asString(node.get("nodeId")), "output")
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

                    codeAgentSummary = summarizeCodeAgentResponse(codeAgentResponse);
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

            if (containsReportNode(orderedNodes)) {
                try {
                    Map<String, Object> reportNode = firstReportNode(orderedNodes);
                    reportPath = generateRuntimeReport(
                            platformRunId,
                            template,
                            orderedNodes,
                            workflowEvents,
                            status,
                            warnings,
                            codeAgentSummary
                    );
                    appendWorkflowEvent(workflowEvents, platformRunId, workflowEvent(
                            "REPORT_GENERATED",
                            "Report Generator 生成 Runtime Lite 演示报告",
                            "report",
                            "SUCCESS",
                            "已生成平台层 Runtime Lite Markdown 报告: " + reportPath,
                            Map.of(
                                    "nodeId", asString(reportNode.get("nodeId")),
                                    "executionMode", "executed",
                                    "reportPath", reportPath,
                                    "runtimeStatus", status
                            )
                    ));
                } catch (Exception error) {
                    warnings.add("Runtime Lite 报告生成失败: " + error.getMessage());
                    appendWorkflowEvent(workflowEvents, platformRunId, workflowEvent(
                            "AGENT_FAILED",
                            "Report Generator 报告生成失败",
                            "report",
                            "FAILED",
                            "Runtime Lite 报告生成失败: " + error.getMessage(),
                            Map.of("executionMode", "executed")
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
                    warnings,
                    reportPath,
                    codeAgentSummary
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
            List<String> warnings,
            String reportPath,
            Map<String, Object> codeAgentSummary
    ) {
        record.setStatus(status);
        record.setSuccess(success);
        record.setTestSuccess(success || waitingForHuman);
        record.setQualityScore(success ? 100 : waitingForHuman ? 80 : 0);
        record.setSecurityStatus(success ? "runtime_completed" : waitingForHuman ? "waiting_for_human" : "runtime_failed");
        record.setErrorSummary(errorSummary);
        record.setApproved(success && !waitingForHuman);
        record.setRequireHumanApproval(waitingForHuman);
        record.setReportPath(reportPath);
        record.setRunnerWarning(warnings.isEmpty() ? "平台层演示执行器，不动态改写 LangGraph" : String.join("; ", warnings));
        record.setRunSummaryJson(serializeObject(buildRunSummary(record, template, workflowEvents, warnings, reportPath)));
        record.setUiViewModelJson(serializeObject(buildUiViewModel(template, nodes, workflowEvents, codeAgentSummary, reportPath)));
        record.setRawResponse(serializeObject(Map.of(
                "template", template,
                "workflow_events", workflowEvents,
                "warnings", warnings,
                "status", status,
                "report_path", reportPath,
                "code_agent_summary", codeAgentSummary
        )));
        RunRecordEntity savedRecord = runRecordRepository.save(record);
        reportIndexService.saveReportIndexFromRunRecord(savedRecord);
        return savedRecord;
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

    private Map<String, Object> summarizeCodeAgentResponse(Map<String, Object> response) {
        List<Map<String, Object>> results = mapList(response.get("results"));
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("success", asBoolean(response.get("success")));
        summary.put("operation", asString(response.get("operation")));
        summary.put("filePath", asString(response.get("filePath")));
        summary.put("message", asString(response.get("message")));
        summary.put("auditPath", firstNonBlank(
                asString(response.get("auditPath")),
                results.stream()
                        .map(result -> asString(result.get("auditPath")))
                        .filter(value -> !value.isBlank())
                        .findFirst()
                        .orElse("")
        ));
        summary.put("resultCount", results.size());
        summary.put("blockedFiles", results.stream().mapToInt(result -> mapList(result.get("blockedFiles")).size()).sum());
        summary.put("plannedChanges", results.stream().mapToInt(result -> mapList(result.get("changes")).size()).sum());
        summary.put("actualWrites", results.stream()
                .map(result -> nestedMap(result, "summary").get("actualWrites"))
                .mapToInt(value -> {
                    try {
                        return Integer.parseInt(asString(value));
                    } catch (NumberFormatException error) {
                        return 0;
                    }
                })
                .sum());
        return summary;
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

    private List<Map<String, Object>> buildConnectionMappings(
            List<Map<String, Object>> nodes,
            List<Map<String, Object>> connections
    ) {
        if (nodes.isEmpty() || connections.isEmpty()) {
            return List.of();
        }

        Map<String, Map<String, Object>> nodeById = new LinkedHashMap<>();
        nodes.forEach(node -> nodeById.put(asString(node.get("nodeId")), node));
        List<Map<String, Object>> mappings = new ArrayList<>();

        for (Map<String, Object> connection : connections) {
            String fromNodeId = asString(connection.get("fromNodeId"));
            String toNodeId = asString(connection.get("toNodeId"));
            Map<String, Object> sourceNode = nodeById.get(fromNodeId);
            Map<String, Object> targetNode = nodeById.get(toNodeId);

            if (sourceNode == null || targetNode == null || fromNodeId.equals(toNodeId)) {
                continue;
            }

            String fromOutputField = firstNonBlank(
                    asString(connection.get("fromOutputField")),
                    firstStringValue(sourceNode.get("output_fields")),
                    "output"
            );
            String toInputField = firstNonBlank(
                    asString(connection.get("toInputField")),
                    firstStringValue(targetNode.get("input_fields")),
                    "input"
            );
            String dataType = firstNonBlank(
                    asString(connection.get("dataType")),
                    classifyWorkflowField(firstNonBlank(fromOutputField, toInputField))
            );
            String color = firstNonBlank(asString(connection.get("color")), workflowFieldColor(dataType));
            Map<String, Object> mapping = new LinkedHashMap<>();

            mapping.put("fromNodeId", fromNodeId);
            mapping.put("fromNodeName", firstNonBlank(asString(sourceNode.get("name")), asString(sourceNode.get("agentKey")), fromNodeId));
            mapping.put("fromOutputField", fromOutputField);
            mapping.put("toNodeId", toNodeId);
            mapping.put("toNodeName", firstNonBlank(asString(targetNode.get("name")), asString(targetNode.get("agentKey")), toNodeId));
            mapping.put("toInputField", toInputField);
            mapping.put("dataType", dataType);
            mapping.put("color", color);
            mapping.put("label", firstNonBlank(asString(connection.get("label")), fromOutputField + " -> " + toInputField));
            mappings.add(mapping);
        }

        return mappings;
    }

    private List<Map<String, Object>> mappingsForNode(List<Map<String, Object>> mappings, String nodeId, String direction) {
        return mappings.stream()
                .filter(mapping -> "input".equals(direction)
                        ? nodeId.equals(asString(mapping.get("toNodeId")))
                        : nodeId.equals(asString(mapping.get("fromNodeId"))))
                .toList();
    }

    private List<String> buildConnectionWarnings(
            List<Map<String, Object>> nodes,
            List<Map<String, Object>> connections,
            List<Map<String, Object>> orderedNodes
    ) {
        List<String> warnings = new ArrayList<>();
        Set<String> nodeIds = new HashSet<>();
        Map<String, Map<String, Object>> nodeById = new LinkedHashMap<>();
        nodes.forEach(node -> {
            String nodeId = asString(node.get("nodeId"));
            nodeIds.add(nodeId);
            nodeById.put(nodeId, node);
        });

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

            Map<String, Object> sourceNode = nodeById.get(from);
            Map<String, Object> targetNode = nodeById.get(to);
            String fromOutputField = asString(connection.get("fromOutputField"));
            String toInputField = asString(connection.get("toInputField"));

            if (!fromOutputField.isBlank() && sourceNode != null && !stringList(sourceNode.get("output_fields")).contains(fromOutputField)) {
                warnings.add("存在指向不存在输出字段的连线: " + fromOutputField);
            }

            if (!toInputField.isBlank() && targetNode != null && !stringList(targetNode.get("input_fields")).contains(toInputField)) {
                warnings.add("存在指向不存在输入字段的连线: " + toInputField);
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
            List<String> warnings,
            String reportPath
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
        summary.put("report_path", reportPath);
        summary.put("platformRunId", record.getPlatformRunId());
        summary.put("workflow_template", template.get("templateKey"));
        summary.put("workflow_template_name", template.get("name"));
        summary.put("runtime_mode", "workflow_runtime_lite");
        summary.put("warnings", warnings);
        summary.put("runtime_node_counts", runtimeNodeCounts(workflowEvents));
        summary.put("connection_mappings", buildConnectionMappings(mapList(template.get("nodes")), mapList(template.get("connections"))));
        summary.put("event_count", workflowEvents.size());
        summary.put("last_event", workflowEvents.isEmpty() ? Map.of() : workflowEvents.get(workflowEvents.size() - 1));
        return summary;
    }

    private Map<String, Object> buildUiViewModel(
            Map<String, Object> template,
            List<Map<String, Object>> nodes,
            List<Map<String, Object>> workflowEvents,
            Map<String, Object> codeAgentSummary,
            String reportPath
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
        uiViewModel.put("runtime_summary", Map.of(
                "mode", "workflow_runtime_lite",
                "node_counts", runtimeNodeCounts(workflowEvents),
                "code_agent", codeAgentSummary,
                "report_path", reportPath,
                "connection_mappings", buildConnectionMappings(nodes, mapList(template.get("connections")))
        ));
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

    private boolean isReportNode(Map<String, Object> node) {
        String agentKey = asString(node.get("agentKey"));
        String nodeType = asString(node.get("nodeType"));
        String stage = asString(node.get("stage"));

        return "report".equals(agentKey)
                || "report_generator".equals(agentKey)
                || "report".equals(nodeType)
                || "report".equals(stage);
    }

    private boolean containsReportNode(List<Map<String, Object>> nodes) {
        return nodes.stream().anyMatch(this::isReportNode);
    }

    private Map<String, Object> firstReportNode(List<Map<String, Object>> nodes) {
        return nodes.stream().filter(this::isReportNode).findFirst().orElse(Map.of());
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

    private Map<String, Object> runtimeNodeCounts(List<Map<String, Object>> workflowEvents) {
        Set<String> executed = new HashSet<>();
        Set<String> simulated = new HashSet<>();
        Set<String> waiting = new HashSet<>();

        for (Map<String, Object> event : workflowEvents) {
            String mode = firstNonBlank(
                    asString(nestedValue(event, "detail", "executionMode")),
                    asString(nestedValue(event, "detail", "execution_mode"))
            );
            String nodeId = firstNonBlank(
                    asString(nestedValue(event, "detail", "nodeId")),
                    asString(event.get("agent")) + "_" + workflowEvents.indexOf(event)
            );

            if ("executed".equals(mode)) {
                executed.add(nodeId);
            } else if ("simulated".equals(mode)) {
                simulated.add(nodeId);
            } else if ("waiting".equals(mode)) {
                waiting.add(nodeId);
            }
        }

        return Map.of(
                "executed", executed.size(),
                "simulated", simulated.size(),
                "waiting", waiting.size()
        );
    }

    private String generateRuntimeReport(
            String platformRunId,
            Map<String, Object> template,
            List<Map<String, Object>> nodes,
            List<Map<String, Object>> workflowEvents,
            String status,
            List<String> warnings,
            Map<String, Object> codeAgentSummary
    ) {
        try {
            Path reportsDir = Path.of("reports").toAbsolutePath().normalize();
            Files.createDirectories(reportsDir);
            String reportName = platformRunId + "_runtime_lite_report.md";
            Path reportPath = reportsDir.resolve(reportName).normalize();
            String markdown = buildRuntimeReportMarkdown(platformRunId, template, nodes, workflowEvents, status, warnings, codeAgentSummary);
            Files.writeString(reportPath, markdown, StandardCharsets.UTF_8);
            return "reports/" + reportName;
        } catch (IOException error) {
            throw new IllegalStateException(error.getMessage(), error);
        }
    }

    private String buildRuntimeReportMarkdown(
            String platformRunId,
            Map<String, Object> template,
            List<Map<String, Object>> nodes,
            List<Map<String, Object>> workflowEvents,
            String status,
            List<String> warnings,
            Map<String, Object> codeAgentSummary
    ) {
        StringBuilder markdown = new StringBuilder();
        markdown.append("# Workflow Runtime Lite 演示报告\n\n");
        markdown.append("- Platform Run ID: `").append(platformRunId).append("`\n");
        markdown.append("- Template: `").append(firstNonBlank(asString(template.get("name")), asString(template.get("templateKey")))).append("`\n");
        markdown.append("- Status: `").append(status).append("`\n");
        markdown.append("- Runtime Mode: `workflow_runtime_lite`\n");
        markdown.append("- Generated At: `").append(LocalDateTime.now()).append("`\n\n");

        markdown.append("## 节点顺序\n\n");
        for (int index = 0; index < nodes.size(); index += 1) {
            Map<String, Object> node = nodes.get(index);
            markdown.append(index + 1)
                    .append(". **")
                    .append(firstNonBlank(asString(node.get("name")), asString(node.get("agentKey"))))
                    .append("** - `")
                    .append(nodeExecutionMode(node))
                    .append("` - `")
                    .append(firstNonBlank(asString(node.get("stage")), "custom"))
                    .append("`\n");
        }

        markdown.append("\n## Runtime 事件摘要\n\n");
        Map<String, Object> counts = runtimeNodeCounts(workflowEvents);
        markdown.append("- Executed events: ").append(counts.get("executed")).append("\n");
        markdown.append("- Simulated events: ").append(counts.get("simulated")).append("\n");
        markdown.append("- Waiting events: ").append(counts.get("waiting")).append("\n");
        markdown.append("- Total events: ").append(workflowEvents.size()).append("\n\n");

        markdown.append("## 字段级输入输出映射\n\n");
        List<Map<String, Object>> connectionMappings = buildConnectionMappings(nodes, mapList(template.get("connections")));
        if (connectionMappings.isEmpty()) {
            markdown.append("本次模板没有配置字段级输入输出映射。\n\n");
        } else {
            connectionMappings.forEach(mapping -> markdown
                    .append("- `")
                    .append(asString(mapping.get("fromNodeName")))
                    .append(".")
                    .append(asString(mapping.get("fromOutputField")))
                    .append("` -> `")
                    .append(asString(mapping.get("toNodeName")))
                    .append(".")
                    .append(asString(mapping.get("toInputField")))
                    .append("` (")
                    .append(asString(mapping.get("dataType")))
                    .append(")\n"));
            markdown.append("\n");
        }

        markdown.append("## CodeAgent 摘要\n\n");
        if (codeAgentSummary.isEmpty()) {
            markdown.append("本次 Runtime Lite 未执行 CodeAgent 节点。\n\n");
        } else {
            markdown.append("- Operation: `").append(asString(codeAgentSummary.get("operation"))).append("`\n");
            markdown.append("- File Path: `").append(asString(codeAgentSummary.get("filePath"))).append("`\n");
            markdown.append("- Audit Path: `").append(asString(codeAgentSummary.get("auditPath"))).append("`\n");
            markdown.append("- Planned Changes: ").append(asString(codeAgentSummary.get("plannedChanges"))).append("\n");
            markdown.append("- Actual Writes: ").append(asString(codeAgentSummary.get("actualWrites"))).append("\n");
            markdown.append("- Blocked Files: ").append(asString(codeAgentSummary.get("blockedFiles"))).append("\n\n");
        }

        if (!warnings.isEmpty()) {
            markdown.append("## Warnings\n\n");
            warnings.forEach(warning -> markdown.append("- ").append(warning).append("\n"));
            markdown.append("\n");
        }

        markdown.append("## 最近事件\n\n");
        workflowEvents.stream().skip(Math.max(0, workflowEvents.size() - 12)).forEach(event -> markdown
                .append("- `")
                .append(asString(event.get("status")))
                .append("` ")
                .append(asString(event.get("event_text")))
                .append(" - ")
                .append(asString(event.get("message")))
                .append("\n"));

        return markdown.toString();
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

    private List<String> stringList(Object value) {
        if (!(value instanceof List<?> list)) {
            return List.of();
        }

        return list.stream()
                .map(this::asString)
                .filter(item -> !item.isBlank())
                .toList();
    }

    private String firstStringValue(Object value) {
        return stringList(value).stream().findFirst().orElse("");
    }

    private String classifyWorkflowField(String field) {
        String normalized = field == null ? "" : field.toLowerCase();

        if (normalized.contains("requirement") || normalized.contains("input") || normalized.contains("prompt")) {
            return "requirement";
        }

        if (normalized.contains("product") || normalized.contains("plan") || normalized.contains("spec")) {
            return "product";
        }

        if (normalized.contains("code") || normalized.contains("diff") || normalized.contains("patch")) {
            return "code";
        }

        if (normalized.contains("test") || normalized.contains("pytest") || normalized.contains("coverage") || normalized.contains("quality")) {
            return "test";
        }

        if (normalized.contains("error") || normalized.contains("stderr") || normalized.contains("exception") || normalized.contains("sentry")) {
            return "error";
        }

        if (normalized.contains("file") || normalized.contains("path") || normalized.contains("audit") || normalized.contains("folder")) {
            return "file";
        }

        if (normalized.contains("report") || normalized.contains("markdown") || normalized.contains("summary")) {
            return "report";
        }

        if (normalized.contains("approval") || normalized.contains("human") || normalized.contains("approved")) {
            return "approval";
        }

        return "custom";
    }

    private String workflowFieldColor(String dataType) {
        return switch (firstNonBlank(dataType, "custom")) {
            case "requirement" -> "#1a73e8";
            case "product" -> "#4285f4";
            case "code" -> "#34a853";
            case "test" -> "#f9ab00";
            case "error" -> "#ea4335";
            case "file" -> "#0f9d58";
            case "report" -> "#7c3aed";
            case "approval" -> "#f97316";
            default -> "#64748b";
        };
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
