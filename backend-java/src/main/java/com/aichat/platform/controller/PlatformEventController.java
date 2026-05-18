package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.entity.RunEventEntity;
import com.aichat.platform.service.RunEventService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/platform/events")
public class PlatformEventController {

    private final RunEventService runEventService;

    public PlatformEventController(RunEventService runEventService) {
        this.runEventService = runEventService;
    }

    @GetMapping("/recent")
    public ApiResponse<List<RunEventEntity>> listRecentEvents(@RequestParam(defaultValue = "20") int limit) {
        return ApiResponse.ok(runEventService.listRecentEvents(limit));
    }
}
