package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.service.ModelSecretService;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/platform/secrets")
public class PlatformSecretController {

    private final ModelSecretService modelSecretService;

    public PlatformSecretController(ModelSecretService modelSecretService) {
        this.modelSecretService = modelSecretService;
    }

    @GetMapping("/models")
    public ApiResponse<List<Map<String, Object>>> listModelSecretStatus() {
        return ApiResponse.ok(modelSecretService.listModelSecretStatus());
    }

    @PostMapping("/models/{provider}")
    public ApiResponse<Map<String, Object>> updateModelSecret(
            @PathVariable String provider,
            @RequestBody Map<String, Object> request
    ) {
        String apiKey = request == null ? "" : String.valueOf(request.getOrDefault("apiKey", ""));

        return ApiResponse.ok(modelSecretService.updateModelSecret(provider, apiKey));
    }

    @DeleteMapping("/models/{provider}")
    public ApiResponse<Map<String, Object>> clearModelSecret(@PathVariable String provider) {
        return ApiResponse.ok(modelSecretService.clearModelSecret(provider));
    }
}
