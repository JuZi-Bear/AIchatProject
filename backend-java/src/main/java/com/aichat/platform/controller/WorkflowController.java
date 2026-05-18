package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.service.PythonAgentClient;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/workflows")
public class WorkflowController {

    private final PythonAgentClient pythonAgentClient;

    public WorkflowController(PythonAgentClient pythonAgentClient) {
        this.pythonAgentClient = pythonAgentClient;
    }

    @GetMapping("/templates")
    public ApiResponse<List<Map<String, Object>>> getWorkflowTemplates() {
        return ApiResponse.ok(pythonAgentClient.getWorkflowTemplates());
    }

    @PostMapping("/instantiate")
    public ApiResponse<Map<String, Object>> instantiateWorkflow(@RequestBody Map<String, Object> request) {
        return ApiResponse.ok(pythonAgentClient.instantiateWorkflow(request));
    }
}
