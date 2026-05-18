package com.aichat.platform.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public record PluginInfo(
        String name,

        @JsonProperty("display_name")
        String displayName,

        String description,
        Boolean enabled,

        @JsonProperty("latest_result")
        Map<String, Object> latestResult
) {
}
