package com.aichat.platform.controller;

import com.aichat.platform.dto.PluginInfo;
import com.aichat.platform.entity.PluginConfigEntity;
import com.aichat.platform.repository.PluginConfigRepository;
import com.aichat.platform.service.PythonAgentClient;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/plugins")
public class PluginController {

    private final PythonAgentClient pythonAgentClient;
    private final PluginConfigRepository pluginConfigRepository;

    public PluginController(PythonAgentClient pythonAgentClient, PluginConfigRepository pluginConfigRepository) {
        this.pythonAgentClient = pythonAgentClient;
        this.pluginConfigRepository = pluginConfigRepository;
    }

    @GetMapping
    public List<PluginInfo> getPlugins() {
        if (pluginConfigRepository.count() > 0) {
            return pluginConfigRepository.findAll().stream()
                    .map(this::toPluginInfo)
                    .toList();
        }

        return pythonAgentClient.getPlugins();
    }

    private PluginInfo toPluginInfo(PluginConfigEntity entity) {
        return new PluginInfo(
                entity.getPluginName(),
                entity.getPluginName(),
                entity.getDescription(),
                entity.isEnabled(),
                null
        );
    }
}
