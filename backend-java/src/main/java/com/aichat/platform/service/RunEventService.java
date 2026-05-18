package com.aichat.platform.service;

import com.aichat.platform.entity.RunEventEntity;
import com.aichat.platform.model.RunEventType;
import com.aichat.platform.repository.RunEventRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

@Service
public class RunEventService {

    private final RunEventRepository runEventRepository;
    private final RunEventSseService runEventSseService;
    private final ObjectMapper objectMapper;

    public RunEventService(
            RunEventRepository runEventRepository,
            RunEventSseService runEventSseService,
            ObjectMapper objectMapper
    ) {
        this.runEventRepository = runEventRepository;
        this.runEventSseService = runEventSseService;
        this.objectMapper = objectMapper;
    }

    public void addEvent(
            String platformRunId,
            String pythonRunId,
            RunEventType eventType,
            String status,
            String message,
            Object detail
    ) {
        try {
            RunEventEntity event = new RunEventEntity();
            event.setPlatformRunId(platformRunId);
            event.setPythonRunId(blankToNull(pythonRunId));
            event.setEventType(eventType);
            event.setEventText(eventType.getDescription());
            event.setAgent("");
            event.setStatus(status);
            event.setMessage(message);
            event.setDetailJson(serializeDetail(detail));
            RunEventEntity savedEvent = runEventRepository.save(event);
            runEventSseService.sendEvent(platformRunId, savedEvent);
        } catch (Exception ignored) {
            // Event logging is observability only and must never break a workflow run.
        }
    }

    public List<RunEventEntity> listEventsByRun(String platformRunId) {
        return runEventRepository.findByPlatformRunIdOrderByCreatedAtAsc(platformRunId);
    }

    public List<RunEventEntity> listRecentEvents(int limit) {
        int size = Math.max(1, Math.min(limit, 100));

        if (size == 20) {
            return runEventRepository.findTop20ByOrderByCreatedAtDesc();
        }

        return runEventRepository.findAllByOrderByCreatedAtDesc(PageRequest.of(0, size));
    }

    public void addPythonWorkflowEvent(String platformRunId, String pythonRunId, Map<String, Object> workflowEvent) {
        if (workflowEvent == null || workflowEvent.isEmpty()) {
            return;
        }

        try {
            RunEventType eventType = parseEventType(asString(workflowEvent.get("event_type")));
            RunEventEntity event = new RunEventEntity();
            event.setPlatformRunId(platformRunId);
            event.setPythonRunId(blankToNull(pythonRunId));
            event.setEventType(eventType);
            event.setEventText(firstNonBlank(asString(workflowEvent.get("event_text")), eventType.getDescription()));
            event.setAgent(asString(workflowEvent.get("agent")));
            event.setStatus(asString(workflowEvent.get("status")));
            event.setMessage(asString(workflowEvent.get("message")));
            event.setDetailJson(serializeDetail(buildWorkflowEventDetail(workflowEvent)));
            event.setCreatedAt(parseCreatedAt(asString(workflowEvent.get("created_at"))));
            RunEventEntity savedEvent = runEventRepository.save(event);
            runEventSseService.sendEvent(platformRunId, savedEvent);
        } catch (Exception ignored) {
            // Python workflow event persistence is observability only.
        }
    }

    public void addStatusChangedEvent(String platformRunId, String oldStatus, String newStatus) {
        String safeOldStatus = oldStatus == null || oldStatus.isBlank() ? "UNKNOWN" : oldStatus;
        String safeNewStatus = newStatus == null || newStatus.isBlank() ? "UNKNOWN" : newStatus;
        addEvent(
                platformRunId,
                null,
                RunEventType.STATUS_CHANGED,
                safeNewStatus,
                "任务状态从 " + safeOldStatus + " 变更为 " + safeNewStatus,
                Map.of("oldStatus", safeOldStatus, "newStatus", safeNewStatus)
        );
    }

    private String serializeDetail(Object detail) {
        if (detail == null) {
            return "{}";
        }

        try {
            return objectMapper.writeValueAsString(detail);
        } catch (JsonProcessingException error) {
            return "{}";
        }
    }

    private String blankToNull(String value) {
        return value == null || value.isBlank() ? null : value;
    }

    private RunEventType parseEventType(String value) {
        try {
            return RunEventType.valueOf(value);
        } catch (IllegalArgumentException error) {
            return RunEventType.STATUS_CHANGED;
        }
    }

    private Map<String, Object> buildWorkflowEventDetail(Map<String, Object> workflowEvent) {
        Object detail = workflowEvent.get("detail");
        if (detail == null) {
            detail = Map.of();
        }

        return Map.of(
                "agent", asString(workflowEvent.get("agent")),
                "created_at", asString(workflowEvent.get("created_at")),
                "detail", detail
        );
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

    private LocalDateTime parseCreatedAt(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }

        try {
            return LocalDateTime.parse(value);
        } catch (Exception error) {
            return null;
        }
    }
}
