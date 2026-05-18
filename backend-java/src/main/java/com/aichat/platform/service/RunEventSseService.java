package com.aichat.platform.service;

import com.aichat.platform.entity.RunEventEntity;
import com.aichat.platform.model.RunEventType;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@Service
public class RunEventSseService {

    private static final Logger log = LoggerFactory.getLogger(RunEventSseService.class);
    private static final long TIMEOUT_MS = 10 * 60 * 1000L;

    private final Map<String, CopyOnWriteArrayList<SseEmitter>> emitters = new ConcurrentHashMap<>();

    public SseEmitter subscribe(String platformRunId) {
        SseEmitter emitter = new SseEmitter(TIMEOUT_MS);
        emitters.computeIfAbsent(platformRunId, ignored -> new CopyOnWriteArrayList<>()).add(emitter);

        emitter.onTimeout(() -> removeEmitter(platformRunId, emitter));
        emitter.onCompletion(() -> removeEmitter(platformRunId, emitter));
        emitter.onError(error -> removeEmitter(platformRunId, emitter));

        sendConnectedEvent(platformRunId, emitter);
        return emitter;
    }

    public void sendEvent(String platformRunId, RunEventEntity event) {
        CopyOnWriteArrayList<SseEmitter> runEmitters = emitters.get(platformRunId);
        if (runEmitters == null || runEmitters.isEmpty()) {
            return;
        }

        for (SseEmitter emitter : runEmitters) {
            sendEventToEmitter(emitter, event);
        }

        if (isTerminalEvent(event)) {
            sendFinalEvent(platformRunId, event);
            complete(platformRunId);
        }
    }

    public void sendEventToEmitter(SseEmitter emitter, RunEventEntity event) {
        sendToEmitter(event.getPlatformRunId(), emitter, "run-event", event.getId(), event);
    }

    public void sendErrorEvent(SseEmitter emitter, String platformRunId, String message) {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("platformRunId", platformRunId);
        payload.put("message", message);
        payload.put("createdAt", LocalDateTime.now().toString());
        sendToEmitter(platformRunId, emitter, "stream-error", null, payload);
    }

    public void complete(String platformRunId) {
        CopyOnWriteArrayList<SseEmitter> runEmitters = emitters.remove(platformRunId);
        if (runEmitters == null) {
            return;
        }

        for (SseEmitter emitter : runEmitters) {
            try {
                emitter.complete();
            } catch (Exception error) {
                log.debug("Failed to complete SSE emitter for {}", platformRunId, error);
            }
        }
    }

    public void completeEmitter(String platformRunId, SseEmitter emitter) {
        removeEmitter(platformRunId, emitter);
        try {
            emitter.complete();
        } catch (Exception error) {
            log.debug("Failed to complete SSE emitter for {}", platformRunId, error);
        }
    }

    private void sendConnectedEvent(String platformRunId, SseEmitter emitter) {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("platformRunId", platformRunId);
        payload.put("message", "SSE 连接已建立");
        payload.put("createdAt", LocalDateTime.now().toString());
        sendToEmitter(platformRunId, emitter, "connected", null, payload);
    }

    private void sendFinalEvent(String platformRunId, RunEventEntity event) {
        CopyOnWriteArrayList<SseEmitter> runEmitters = emitters.get(platformRunId);
        if (runEmitters == null || runEmitters.isEmpty()) {
            return;
        }

        for (SseEmitter emitter : runEmitters) {
            sendToEmitter(platformRunId, emitter, "final", event.getId(), event);
        }
    }

    private void sendToEmitter(String platformRunId, SseEmitter emitter, String eventName, Long eventId, Object payload) {
        try {
            SseEmitter.SseEventBuilder builder = SseEmitter.event()
                    .name(eventName)
                    .data(payload);

            if (eventId != null) {
                builder.id(String.valueOf(eventId));
            }

            emitter.send(builder);
        } catch (IOException | IllegalStateException error) {
            log.debug("Failed to send SSE event {} for {}", eventName, platformRunId, error);
            removeEmitter(platformRunId, emitter);
        }
    }

    private boolean isTerminalEvent(RunEventEntity event) {
        RunEventType eventType = event.getEventType();
        return eventType == RunEventType.RUN_SUCCESS
                || eventType == RunEventType.RUN_FAILED
                || eventType == RunEventType.RUN_CANCELLED;
    }

    private void removeEmitter(String platformRunId, SseEmitter emitter) {
        CopyOnWriteArrayList<SseEmitter> runEmitters = emitters.get(platformRunId);
        if (runEmitters == null) {
            return;
        }

        runEmitters.remove(emitter);
        if (runEmitters.isEmpty()) {
            emitters.remove(platformRunId, runEmitters);
        }
    }
}
