package com.aichat.platform.service;

import com.aichat.platform.config.AgentEngineProperties;
import com.aichat.platform.dto.ModelInfo;
import com.aichat.platform.dto.PluginInfo;
import com.aichat.platform.dto.RunRequest;
import com.aichat.platform.dto.RunResponse;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class PythonAgentClient {

    private final RestClient restClient;

    public PythonAgentClient(RestClient.Builder builder, AgentEngineProperties properties) {
        this.restClient = builder.baseUrl(properties.getBaseUrl()).build();
    }

    public Map<String, Object> getHealth() {
        return restClient.get()
                .uri("/health")
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                });
    }

    public List<ModelInfo> getModels() {
        ModelInfo[] models = restClient.get()
                .uri("/models")
                .retrieve()
                .body(ModelInfo[].class);
        return models == null ? List.of() : Arrays.asList(models);
    }

    public List<PluginInfo> getPlugins() {
        PluginInfo[] plugins = restClient.get()
                .uri("/plugins")
                .retrieve()
                .body(PluginInfo[].class);
        return plugins == null ? List.of() : Arrays.asList(plugins);
    }

    public List<Map<String, Object>> getAgents() {
        List<Map<String, Object>> agents = restClient.get()
                .uri("/agents")
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                });
        return agents == null ? List.of() : agents;
    }

    public List<Map<String, Object>> getWorkflowTemplates() {
        List<Map<String, Object>> templates = restClient.get()
                .uri("/api/workflows/templates")
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                });
        return templates == null ? List.of() : templates;
    }

    public Map<String, Object> instantiateWorkflow(Map<String, Object> request) {
        return restClient.post()
                .uri("/api/workflows/instantiate")
                .body(request)
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                });
    }

    public Map<String, Object> executeCodeAgent(Map<String, Object> request) {
        return restClient.post()
                .uri("/api/code-agent/execute")
                .body(request)
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                });
    }

    public RunResponse createRun(RunRequest request) {
        return restClient.post()
                .uri("/runs")
                .body(request)
                .retrieve()
                .body(RunResponse.class);
    }

    public List<Map<String, Object>> getRuns() {
        List<Map<String, Object>> runs = restClient.get()
                .uri("/runs")
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                });
        return runs == null ? List.of() : runs;
    }

    public RunResponse getRun(String runId) {
        return restClient.get()
                .uri(uriBuilder -> uriBuilder.path("/runs/{runId}").build(runId))
                .retrieve()
                .body(RunResponse.class);
    }

    public List<Map<String, Object>> getReports() {
        List<Map<String, Object>> reports = restClient.get()
                .uri("/reports")
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                });
        return reports == null ? List.of() : reports;
    }

    public Map<String, Object> getReport(String reportName) {
        return restClient.get()
                .uri(uriBuilder -> uriBuilder.path("/reports/{reportName}").build(reportName))
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                });
    }
}
