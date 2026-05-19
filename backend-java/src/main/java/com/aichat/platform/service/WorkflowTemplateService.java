package com.aichat.platform.service;

import com.aichat.platform.entity.WorkflowTemplateEntity;
import com.aichat.platform.repository.WorkflowTemplateRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.springframework.stereotype.Service;

@Service
public class WorkflowTemplateService {

    private final WorkflowTemplateRepository workflowTemplateRepository;
    private final ObjectMapper objectMapper;

    public WorkflowTemplateService(WorkflowTemplateRepository workflowTemplateRepository, ObjectMapper objectMapper) {
        this.workflowTemplateRepository = workflowTemplateRepository;
        this.objectMapper = objectMapper;
    }

    public List<Map<String, Object>> listTemplates() {
        return workflowTemplateRepository.findAllByOrderByUpdatedAtDesc()
                .stream()
                .map(this::toResponse)
                .toList();
    }

    public Optional<Map<String, Object>> getTemplate(String templateKey) {
        return workflowTemplateRepository.findByTemplateKey(templateKey).map(this::toResponse);
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> saveTemplate(Map<String, Object> request) {
        if (request == null) {
            throw new IllegalArgumentException("template request is required");
        }

        String templateKey = firstNonBlank(
                asString(request.get("workflowTemplateKey")),
                asString(request.get("templateKey")),
                asString(request.get("key"))
        );

        if (templateKey.isBlank()) {
            throw new IllegalArgumentException("workflowTemplateKey is required");
        }

        Object rawNodes = request.get("nodes");
        List<Map<String, Object>> nodes = rawNodes instanceof List<?> list
                ? list.stream()
                        .filter(item -> item instanceof Map<?, ?>)
                        .map(item -> (Map<String, Object>) item)
                        .toList()
                : List.of();

        if (nodes.isEmpty()) {
            throw new IllegalArgumentException("workflow template must contain at least one node");
        }

        WorkflowTemplateEntity entity = workflowTemplateRepository.findByTemplateKey(templateKey)
                .orElseGet(WorkflowTemplateEntity::new);
        entity.setTemplateKey(templateKey);
        entity.setName(firstNonBlank(asString(request.get("name")), templateKey));
        entity.setDescription(asString(request.get("description")));
        entity.setTemplateJson(serializeObject(request));
        entity.setAgentSequenceJson(serializeObject(extractValues(nodes, "agentKey")));
        entity.setStageSequenceJson(serializeObject(extractValues(nodes, "stage")));
        entity.setEnabled(true);
        entity.setVersion(firstNonBlank(asString(request.get("version")), "1.0"));

        return toResponse(workflowTemplateRepository.save(entity));
    }

    private List<String> extractValues(List<Map<String, Object>> nodes, String key) {
        return nodes.stream()
                .map(node -> asString(node.get(key)))
                .filter(value -> !value.isBlank())
                .toList();
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> toResponse(WorkflowTemplateEntity entity) {
        Map<String, Object> templateData = parseJsonMap(entity.getTemplateJson());
        Map<String, Object> response = new LinkedHashMap<>(templateData);
        response.put("id", entity.getId());
        response.put("workflowTemplateKey", firstNonBlank(asString(templateData.get("workflowTemplateKey")), entity.getTemplateKey()));
        response.put("templateKey", entity.getTemplateKey());
        response.put("key", entity.getTemplateKey());
        response.put("name", firstNonBlank(asString(templateData.get("name")), entity.getName()));
        response.put("description", firstNonBlank(asString(templateData.get("description")), entity.getDescription()));
        response.put("nodes", templateData.getOrDefault("nodes", List.of()));
        response.put("connections", templateData.getOrDefault("connections", List.of()));
        response.put("version", firstNonBlank(asString(templateData.get("version")), entity.getVersion(), "1.0"));
        response.put("enabled", entity.isEnabled());
        response.put("agent_sequence", parseStringList(entity.getAgentSequenceJson()));
        response.put("stage_sequence", parseStringList(entity.getStageSequenceJson()));
        response.put("source", "java-mysql");
        response.put("createdAt", entity.getCreatedAt() == null ? "" : entity.getCreatedAt().toString());
        response.put("updatedAt", entity.getUpdatedAt() == null ? "" : entity.getUpdatedAt().toString());

        return response;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> parseJsonMap(String rawJson) {
        if (rawJson == null || rawJson.isBlank()) {
            return Map.of();
        }

        try {
            Object parsed = objectMapper.readValue(rawJson, Object.class);
            if (parsed instanceof Map<?, ?> parsedMap) {
                return (Map<String, Object>) parsedMap;
            }
        } catch (Exception ignored) {
            // Broken template JSON should not break list rendering.
        }

        return Map.of();
    }

    private List<String> parseStringList(String rawJson) {
        if (rawJson == null || rawJson.isBlank()) {
            return List.of();
        }

        try {
            Object parsed = objectMapper.readValue(rawJson, Object.class);
            if (parsed instanceof List<?> list) {
                return list.stream().map(this::asString).filter(value -> !value.isBlank()).toList();
            }
        } catch (Exception ignored) {
            // Broken sequence JSON should return an empty sequence.
        }

        return List.of();
    }

    private String serializeObject(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException error) {
            return "{}";
        }
    }

    private String asString(Object value) {
        return value == null ? "" : String.valueOf(value);
    }

    private String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }

        return "";
    }
}
