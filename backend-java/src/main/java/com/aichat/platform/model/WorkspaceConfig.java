package com.aichat.platform.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public record WorkspaceConfig(
        Long id,
        String name,
        String rootPath,
        boolean enabled,
        @JsonProperty("isDefault")
        boolean isDefault,
        String description,
        int maxFiles,
        int maxReadChars,
        boolean dryRunDefault,
        boolean backupBeforeWrite,
        String createdAt,
        String updatedAt
) {

    public WorkspaceConfig normalized() {
        String normalizedName = blankToDefault(name, "Default Workspace");
        String normalizedRootPath = blankToDefault(rootPath, "output/code_agent_workspace");
        int normalizedMaxFiles = maxFiles > 0 ? maxFiles : 80;
        int normalizedMaxReadChars = maxReadChars > 0 ? maxReadChars : 500000;

        return new WorkspaceConfig(
                id,
                normalizedName,
                normalizedRootPath,
                enabled,
                isDefault,
                description == null ? "" : description,
                normalizedMaxFiles,
                normalizedMaxReadChars,
                dryRunDefault,
                backupBeforeWrite,
                createdAt,
                updatedAt
        );
    }

    public static WorkspaceConfig defaults() {
        return new WorkspaceConfig(
                null,
                "CodeAgent Demo Workspace",
                "output/code_agent_workspace",
                true,
                true,
                "默认受控文件夹工作区。用于 CodeAgent dry-run、diff 预览、审计日志和回放演示。",
                80,
                500000,
                true,
                true,
                null,
                null
        );
    }

    private static String blankToDefault(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value.trim();
    }
}
