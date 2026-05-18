package com.aichat.platform.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.util.List;

public record RunRequest(
        @NotBlank
        String requirement,

        @JsonProperty("model_provider")
        @NotBlank
        String modelProvider,

        @JsonProperty("enabled_plugins")
        @NotNull
        List<String> enabledPlugins,

        @JsonProperty("max_retry_count")
        @Min(0)
        int maxRetryCount,

        @JsonProperty("require_human_approval")
        boolean requireHumanApproval,

        @JsonProperty("demo_mode")
        boolean demoMode,

        @JsonProperty("offline_mode")
        boolean offlineMode
) {
}
