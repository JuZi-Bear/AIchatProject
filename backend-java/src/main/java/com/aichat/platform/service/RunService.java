package com.aichat.platform.service;

import com.aichat.platform.dto.RunRequest;
import com.aichat.platform.dto.RunResponse;
import com.aichat.platform.model.RunEventType;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class RunService {

    private final PythonAgentClient pythonAgentClient;
    private final RunRecordService runRecordService;
    private final RunEventService runEventService;

    public RunService(PythonAgentClient pythonAgentClient, RunRecordService runRecordService, RunEventService runEventService) {
        this.pythonAgentClient = pythonAgentClient;
        this.runRecordService = runRecordService;
        this.runEventService = runEventService;
    }

    public RunResponse createRun(RunRequest request) {
        String platformRunId = runRecordService.nextPlatformRunId();
        runRecordService.createRecord(platformRunId, request);
        runEventService.addEvent(
                platformRunId,
                null,
                RunEventType.RUN_CREATED,
                "CREATED",
                "Java 平台任务已创建",
                Map.of("modelProvider", request.modelProvider(), "demoMode", request.demoMode())
        );

        runRecordService.updateStatus(platformRunId, "RUNNING");
        runEventService.addStatusChangedEvent(platformRunId, "CREATED", "RUNNING");
        runEventService.addEvent(
                platformRunId,
                null,
                RunEventType.RUN_STARTED,
                "RUNNING",
                "Java 平台任务开始执行",
                Map.of("platformRunId", platformRunId)
        );

        try {
            runEventService.addEvent(
                    platformRunId,
                    null,
                    RunEventType.PYTHON_REQUEST_SENT,
                    "RUNNING",
                    "已请求 Python Agent Engine",
                    Map.of("modelProvider", request.modelProvider(), "enabledPlugins", request.enabledPlugins())
            );
            RunResponse response = pythonAgentClient.createRun(request);
            runEventService.addEvent(
                    platformRunId,
                    response.runId(),
                    RunEventType.PYTHON_RESPONSE_RECEIVED,
                    "RUNNING",
                    "收到 Python Agent Engine 响应",
                    Map.of("pythonRunId", response.runId() == null ? "" : response.runId())
            );
            RunResponse platformResponse = response.withPlatformRunId(platformRunId);
            runRecordService.save(platformRunId, request, platformResponse);
            boolean success = isSuccess(platformResponse);
            String finalStatus = success ? "SUCCESS" : "FAILED";
            runEventService.addStatusChangedEvent(platformRunId, "RUNNING", finalStatus);
            runEventService.addEvent(
                    platformRunId,
                    platformResponse.runId(),
                    success ? RunEventType.RUN_SUCCESS : RunEventType.RUN_FAILED,
                    finalStatus,
                    success ? "任务运行成功" : "任务运行失败",
                    platformResponse.runSummary() == null ? Map.of() : platformResponse.runSummary()
            );

            return platformResponse;
        } catch (Exception error) {
            runRecordService.updateStatus(platformRunId, "FAILED");
            runEventService.addEvent(
                    platformRunId,
                    null,
                    RunEventType.ERROR_OCCURRED,
                    "FAILED",
                    "调用 Python Agent Engine 发生异常",
                    Map.of("error", error.getMessage() == null ? error.getClass().getSimpleName() : error.getMessage())
            );
            runEventService.addStatusChangedEvent(platformRunId, "RUNNING", "FAILED");
            runEventService.addEvent(
                    platformRunId,
                    null,
                    RunEventType.RUN_FAILED,
                    "FAILED",
                    "任务运行失败",
                    Map.of("reason", "python_agent_engine_error")
            );
            throw error;
        }
    }

    public List<Map<String, Object>> getRuns() {
        return pythonAgentClient.getRuns();
    }

    public RunResponse getRun(String runId) {
        return pythonAgentClient.getRun(runId);
    }

    private boolean isSuccess(RunResponse response) {
        if (response.runSummary() == null) {
            return false;
        }

        Object success = response.runSummary().get("success");

        if (success instanceof Boolean boolValue) {
            return boolValue;
        }

        return Boolean.parseBoolean(String.valueOf(success));
    }
}
