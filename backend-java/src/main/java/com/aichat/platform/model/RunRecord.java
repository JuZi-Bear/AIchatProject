package com.aichat.platform.model;

import com.aichat.platform.dto.RunResponse;
import java.time.Instant;

public record RunRecord(
        String platformRunId,
        String pythonRunId,
        String requirement,
        String modelProvider,
        boolean success,
        int retryCount,
        double qualityScore,
        String reportPath,
        Instant createdAt,
        RunResponse rawResponse
) {
}
