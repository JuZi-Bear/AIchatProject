package com.aichat.platform.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public record RunResponse(
        @JsonProperty("run_id")
        String runId,

        @JsonProperty("platform_run_id")
        String platformRunId,

        @JsonProperty("run_summary")
        Map<String, Object> runSummary,

        @JsonProperty("ui_view_model")
        Map<String, Object> uiViewModel,

        Map<String, Object> state
) {
    public RunResponse withPlatformRunId(String platformRunId) {
        return new RunResponse(runId, platformRunId, runSummary, uiViewModel, state);
    }
}
