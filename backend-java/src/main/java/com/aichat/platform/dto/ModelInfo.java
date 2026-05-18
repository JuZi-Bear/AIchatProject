package com.aichat.platform.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public record ModelInfo(
        String name,
        String provider,
        String model,

        @JsonProperty("base_url")
        String baseUrl,

        @JsonProperty("env_key")
        String envKey,

        Boolean enabled,

        @JsonProperty("offline_mode")
        Boolean offlineMode,

        @JsonProperty("api_key_configured")
        Boolean apiKeyConfigured,

        @JsonProperty("is_default")
        Boolean isDefault,

        @JsonProperty("default")
        Boolean defaultModel
) {
}
