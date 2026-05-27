package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.service.PlatformDynamicWorkflowService;
import com.aichat.platform.service.PlatformWorkflowRuntimeService;
import com.aichat.platform.service.WorkflowSkillExportService;
import com.aichat.platform.service.WorkflowTemplateService;
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
@RequestMapping("/api/platform/workflows")
public class PlatformWorkflowController {

    private final WorkflowTemplateService workflowTemplateService;
    private final PlatformWorkflowRuntimeService platformWorkflowRuntimeService;
    private final PlatformDynamicWorkflowService platformDynamicWorkflowService;
    private final WorkflowSkillExportService workflowSkillExportService;

    public PlatformWorkflowController(
            WorkflowTemplateService workflowTemplateService,
            PlatformWorkflowRuntimeService platformWorkflowRuntimeService,
            PlatformDynamicWorkflowService platformDynamicWorkflowService,
            WorkflowSkillExportService workflowSkillExportService
    ) {
        this.workflowTemplateService = workflowTemplateService;
        this.platformWorkflowRuntimeService = platformWorkflowRuntimeService;
        this.platformDynamicWorkflowService = platformDynamicWorkflowService;
        this.workflowSkillExportService = workflowSkillExportService;
    }

    @GetMapping("/templates")
    public ApiResponse<List<Map<String, Object>>> listTemplates() {
        return ApiResponse.ok(workflowTemplateService.listTemplates());
    }

    @GetMapping("/templates/{templateKey}")
    public ApiResponse<Map<String, Object>> getTemplate(@PathVariable String templateKey) {
        return workflowTemplateService.getTemplate(templateKey)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.fail("workflow template not found: " + templateKey));
    }

    @PostMapping("/templates")
    public ApiResponse<Map<String, Object>> saveTemplate(@RequestBody Map<String, Object> request) {
        return ApiResponse.ok(workflowTemplateService.saveTemplate(request));
    }

    @PostMapping("/templates/{templateKey}/instantiate")
    public ApiResponse<Map<String, Object>> instantiateTemplate(
            @PathVariable String templateKey,
            @RequestBody(required = false) Map<String, Object> request
    ) {
        return workflowTemplateService.instantiateTemplate(templateKey, request)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.fail("workflow template not found: " + templateKey));
    }

    @PostMapping("/templates/{templateKey}/execute")
    public ApiResponse<Map<String, Object>> executeTemplate(
            @PathVariable String templateKey,
            @RequestBody(required = false) Map<String, Object> request
    ) {
        return platformWorkflowRuntimeService.executeTemplate(templateKey, request)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.fail("workflow template not found: " + templateKey));
    }

    @PostMapping("/templates/{templateKey}/validate-langgraph")
    public ApiResponse<Map<String, Object>> validateDynamicLangGraphTemplate(
            @PathVariable String templateKey,
            @RequestBody(required = false) Map<String, Object> request
    ) {
        return platformDynamicWorkflowService.validateTemplate(templateKey, request)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.fail("workflow template not found: " + templateKey));
    }

    @PostMapping("/templates/{templateKey}/execute-langgraph")
    public ApiResponse<Map<String, Object>> executeDynamicLangGraphTemplate(
            @PathVariable String templateKey,
            @RequestBody(required = false) Map<String, Object> request
    ) {
        return platformDynamicWorkflowService.executeTemplate(templateKey, request)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.fail("workflow template not found: " + templateKey));
    }

    @PostMapping("/runs/{platformRunId}/resume")
    public ApiResponse<Map<String, Object>> resumeDynamicLangGraphRun(
            @PathVariable String platformRunId,
            @RequestBody(required = false) Map<String, Object> request
    ) {
        return platformDynamicWorkflowService.resumeRun(platformRunId, request)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.fail("dynamic workflow run not found: " + platformRunId));
    }

    @PostMapping("/templates/{templateKey}/export-skill")
    public ApiResponse<Map<String, Object>> exportWorkflowSkill(@PathVariable String templateKey) {
        return workflowSkillExportService.exportSkill(templateKey)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.fail("workflow template not found: " + templateKey));
    }

    @DeleteMapping("/templates/{templateKey}")
    public ApiResponse<Map<String, Object>> deleteTemplate(@PathVariable String templateKey) {
        return workflowTemplateService.deleteTemplate(templateKey)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.fail("workflow template not found: " + templateKey));
    }
}
