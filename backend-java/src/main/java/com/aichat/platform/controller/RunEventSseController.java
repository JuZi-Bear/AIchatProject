package com.aichat.platform.controller;

import com.aichat.platform.entity.RunEventEntity;
import com.aichat.platform.entity.RunRecordEntity;
import com.aichat.platform.service.RunEventService;
import com.aichat.platform.service.RunEventSseService;
import com.aichat.platform.service.RunRecordService;
import java.util.List;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@RequestMapping("/api/platform/runs")
public class RunEventSseController {

    private static final int HISTORY_REPLAY_LIMIT = 50;

    private final RunEventSseService runEventSseService;
    private final RunEventService runEventService;
    private final RunRecordService runRecordService;

    public RunEventSseController(
            RunEventSseService runEventSseService,
            RunEventService runEventService,
            RunRecordService runRecordService
    ) {
        this.runEventSseService = runEventSseService;
        this.runEventService = runEventService;
        this.runRecordService = runRecordService;
    }

    @GetMapping(path = "/{platformRunId}/events/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamRunEvents(@PathVariable String platformRunId) {
        SseEmitter emitter = runEventSseService.subscribe(platformRunId);

        RunRecordEntity record = runRecordService.getRecord(platformRunId).orElse(null);
        if (record == null) {
            runEventSseService.sendErrorEvent(emitter, platformRunId, "任务不存在：" + platformRunId);
            runEventSseService.completeEmitter(platformRunId, emitter);
            return emitter;
        }

        List<RunEventEntity> events = runEventService.listEventsByRun(platformRunId);
        int startIndex = Math.max(0, events.size() - HISTORY_REPLAY_LIMIT);
        events.subList(startIndex, events.size()).forEach(event -> runEventSseService.sendEventToEmitter(emitter, event));

        if (isTerminalStatus(record.getStatus())) {
            runEventSseService.completeEmitter(platformRunId, emitter);
        }

        return emitter;
    }

    private boolean isTerminalStatus(String status) {
        return "SUCCESS".equals(status) || "FAILED".equals(status) || "CANCELLED".equals(status);
    }
}
