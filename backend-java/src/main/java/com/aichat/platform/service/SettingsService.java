package com.aichat.platform.service;

import com.aichat.platform.entity.FrontendSettingsEntity;
import com.aichat.platform.model.FrontendSettings;
import com.aichat.platform.repository.FrontendSettingsRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class SettingsService {

    private final FrontendSettingsRepository frontendSettingsRepository;
    private final ObjectMapper objectMapper;

    public SettingsService(FrontendSettingsRepository frontendSettingsRepository, ObjectMapper objectMapper) {
        this.frontendSettingsRepository = frontendSettingsRepository;
        this.objectMapper = objectMapper;
    }

    public FrontendSettings getSettings() {
        return frontendSettingsRepository.findTopByOrderByIdAsc()
                .map(this::toModel)
                .orElseGet(FrontendSettings::defaults);
    }

    public FrontendSettings saveSettings(FrontendSettings nextSettings) {
        FrontendSettings normalized = (nextSettings == null ? FrontendSettings.defaults() : nextSettings).normalized();
        FrontendSettingsEntity entity = frontendSettingsRepository.findTopByOrderByIdAsc()
                .orElseGet(FrontendSettingsEntity::new);

        entity.setSelectedModelProvider(normalized.selectedModelProvider());
        entity.setEnabledPluginsJson(toJson(normalized.enabledPlugins()));
        entity.setDemoMode(normalized.demoMode());
        entity.setMaxRetryCount(normalized.maxRetryCount());
        entity.setRequireHumanApproval(normalized.requireHumanApproval());
        entity.setOfflineMode(normalized.offlineMode());
        entity.setApiMode(normalized.apiMode());

        return toModel(frontendSettingsRepository.save(entity));
    }

    private FrontendSettings toModel(FrontendSettingsEntity entity) {
        return new FrontendSettings(
                entity.getSelectedModelProvider(),
                fromJson(entity.getEnabledPluginsJson()),
                entity.isDemoMode(),
                entity.getMaxRetryCount(),
                entity.isRequireHumanApproval(),
                entity.isOfflineMode(),
                entity.getApiMode()
        ).normalized();
    }

    private String toJson(List<String> values) {
        try {
            return objectMapper.writeValueAsString(values == null ? List.of() : values);
        } catch (JsonProcessingException error) {
            throw new IllegalStateException("failed to serialize frontend settings", error);
        }
    }

    private List<String> fromJson(String rawJson) {
        if (rawJson == null || rawJson.isBlank()) {
            return List.of();
        }

        try {
            return objectMapper.readValue(rawJson, new TypeReference<>() {
            });
        } catch (JsonProcessingException error) {
            return List.of();
        }
    }
}
