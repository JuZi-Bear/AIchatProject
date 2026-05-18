package com.aichat.platform.controller;

import com.aichat.platform.dto.ApiResponse;
import com.aichat.platform.service.PythonAgentClient;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/agents")
public class AgentController {

    private final PythonAgentClient pythonAgentClient;

    public AgentController(PythonAgentClient pythonAgentClient) {
        this.pythonAgentClient = pythonAgentClient;
    }

    @GetMapping
    public ApiResponse<List<Map<String, Object>>> getAgents() {
        return ApiResponse.ok(pythonAgentClient.getAgents());
    }
}
