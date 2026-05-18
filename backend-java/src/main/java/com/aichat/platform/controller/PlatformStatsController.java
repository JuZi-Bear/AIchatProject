package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.service.PlatformStatsService;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/platform/stats")
public class PlatformStatsController {

    private final PlatformStatsService platformStatsService;

    public PlatformStatsController(PlatformStatsService platformStatsService) {
        this.platformStatsService = platformStatsService;
    }

    @GetMapping
    public ApiResponse<Map<String, Object>> getStats() {
        return ApiResponse.ok(platformStatsService.getStats());
    }
}
