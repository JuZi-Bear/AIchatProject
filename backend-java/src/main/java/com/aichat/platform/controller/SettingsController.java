package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.model.FrontendSettings;
import com.aichat.platform.service.SettingsService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/settings")
public class SettingsController {

    private final SettingsService settingsService;

    public SettingsController(SettingsService settingsService) {
        this.settingsService = settingsService;
    }

    @GetMapping
    public ApiResponse<FrontendSettings> getSettings() {
        return ApiResponse.ok(settingsService.getSettings());
    }

    @PostMapping
    public ApiResponse<FrontendSettings> saveSettings(@RequestBody FrontendSettings settings) {
        return ApiResponse.ok(settingsService.saveSettings(settings));
    }
}
