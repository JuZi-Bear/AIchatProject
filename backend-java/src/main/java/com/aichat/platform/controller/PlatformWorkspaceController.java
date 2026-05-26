package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.model.WorkspaceConfig;
import com.aichat.platform.service.WorkspaceConfigService;
import java.util.List;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/platform/workspaces")
public class PlatformWorkspaceController {

    private final WorkspaceConfigService workspaceConfigService;

    public PlatformWorkspaceController(WorkspaceConfigService workspaceConfigService) {
        this.workspaceConfigService = workspaceConfigService;
    }

    @GetMapping
    public ApiResponse<List<WorkspaceConfig>> listWorkspaces() {
        return ApiResponse.ok(workspaceConfigService.listWorkspaces());
    }

    @PostMapping
    public ApiResponse<WorkspaceConfig> createWorkspace(@RequestBody WorkspaceConfig request) {
        return ApiResponse.ok(workspaceConfigService.createWorkspace(request));
    }

    @PutMapping("/{id}")
    public ApiResponse<WorkspaceConfig> updateWorkspace(
            @PathVariable Long id,
            @RequestBody WorkspaceConfig request
    ) {
        return workspaceConfigService.updateWorkspace(id, request)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.fail("workspace not found: " + id));
    }

    @DeleteMapping("/{id}")
    public ApiResponse<WorkspaceConfig> deleteWorkspace(@PathVariable Long id) {
        return workspaceConfigService.deleteWorkspace(id)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.fail("workspace not found: " + id));
    }
}
