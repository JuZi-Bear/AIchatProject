package com.aichat.platform.controller;

import com.aichat.platform.dto.ModelInfo;
import com.aichat.platform.entity.ModelConfigEntity;
import com.aichat.platform.repository.ModelConfigRepository;
import com.aichat.platform.service.PythonAgentClient;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/models")
public class ModelController {

    private final PythonAgentClient pythonAgentClient;
    private final ModelConfigRepository modelConfigRepository;
    private final com.aichat.platform.service.ModelSecretService modelSecretService;

    public ModelController(
            PythonAgentClient pythonAgentClient,
            ModelConfigRepository modelConfigRepository,
            com.aichat.platform.service.ModelSecretService modelSecretService
    ) {
        this.pythonAgentClient = pythonAgentClient;
        this.modelConfigRepository = modelConfigRepository;
        this.modelSecretService = modelSecretService;
    }

    @GetMapping
    public List<ModelInfo> getModels() {
        if (modelConfigRepository.count() > 0) {
            return modelConfigRepository.findAll().stream()
                    .map(this::toModelInfo)
                    .toList();
        }

        return pythonAgentClient.getModels();
    }

    private ModelInfo toModelInfo(ModelConfigEntity entity) {
        return new ModelInfo(
                entity.getName(),
                entity.getProvider(),
                entity.getModel(),
                entity.getBaseUrl(),
                entity.getEnvKey(),
                entity.isEnabled(),
                null,
                modelSecretService.hasStoredSecret(entity)
                        || (entity.getEnvKey() != null && System.getenv(entity.getEnvKey()) != null),
                entity.isDefaultModel(),
                entity.isDefaultModel()
        );
    }
}
