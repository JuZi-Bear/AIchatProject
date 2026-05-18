package com.aichat.platform.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public record FrontendSettings(
        String selectedModelProvider,
        List<String> enabledPlugins,
        boolean demoMode,
        int maxRetryCount,
        boolean requireHumanApproval,
        boolean offlineMode,
        String apiMode
) {
    public static FrontendSettings defaults() {
        return new FrontendSettings("deepseek", List.of(), true, 3, false, false, "java");
    }

    public FrontendSettings normalized() {
        FrontendSettings defaults = defaults();

        return new FrontendSettings(
                selectedModelProvider == null || selectedModelProvider.isBlank()
                        ? defaults.selectedModelProvider()
                        : selectedModelProvider,
                enabledPlugins == null ? defaults.enabledPlugins() : List.copyOf(enabledPlugins),
                demoMode,
                Math.max(0, maxRetryCount),
                requireHumanApproval,
                offlineMode,
                apiMode == null || apiMode.isBlank() ? defaults.apiMode() : apiMode
        );
    }
}
