package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.service.WorkflowTemplateService;
import java.util.List;
import java.util.Map;
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

    public PlatformWorkflowController(WorkflowTemplateService workflowTemplateService) {
        this.workflowTemplateService = workflowTemplateService;
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
}
