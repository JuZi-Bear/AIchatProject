package com.aichat.platform.config;

import com.aichat.platform.entity.ModelConfigEntity;
import com.aichat.platform.entity.PluginConfigEntity;
import com.aichat.platform.repository.ModelConfigRepository;
import com.aichat.platform.repository.PluginConfigRepository;
import java.util.List;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class PlatformDataInitializer implements CommandLineRunner {

    private final ModelConfigRepository modelConfigRepository;
    private final PluginConfigRepository pluginConfigRepository;

    public PlatformDataInitializer(
            ModelConfigRepository modelConfigRepository,
            PluginConfigRepository pluginConfigRepository
    ) {
        this.modelConfigRepository = modelConfigRepository;
        this.pluginConfigRepository = pluginConfigRepository;
    }

    @Override
    public void run(String... args) {
        initializeModels();
        initializePlugins();
    }

    private void initializeModels() {
        if (modelConfigRepository.count() > 0) {
            return;
        }

        modelConfigRepository.saveAll(List.of(
                model("DeepSeek", "deepseek", "deepseek-chat", "https://api.deepseek.com", "DEEPSEEK_API_KEY", true, true),
                model("Qwen", "qwen", "qwen-plus", "https://dashscope.aliyuncs.com/compatible-mode/v1", "QWEN_API_KEY", false, false),
                model("GLM", "glm", "glm-4", "https://open.bigmodel.cn/api/paas/v4", "GLM_API_KEY", false, false)
        ));
    }

    private void initializePlugins() {
        if (pluginConfigRepository.count() > 0) {
            return;
        }

        pluginConfigRepository.saveAll(List.of(
                plugin("Doc Agent", "生成接口说明、代码说明和运行报告补充内容。", true),
                plugin("Security Agent", "检查生成代码中的危险操作和基础安全风险。", true),
                plugin("Refactor Agent", "提出代码结构、可读性和可维护性改进建议。", false),
                plugin("UI Agent", "为前端或交互类需求提供界面结构建议。", false)
        ));
    }

    private ModelConfigEntity model(
            String name,
            String provider,
            String model,
            String baseUrl,
            String envKey,
            boolean enabled,
            boolean defaultModel
    ) {
        ModelConfigEntity entity = new ModelConfigEntity();
        entity.setName(name);
        entity.setProvider(provider);
        entity.setModel(model);
        entity.setBaseUrl(baseUrl);
        entity.setEnvKey(envKey);
        entity.setEnabled(enabled);
        entity.setDefaultModel(defaultModel);
        return entity;
    }

    private PluginConfigEntity plugin(String pluginName, String description, boolean enabled) {
        PluginConfigEntity entity = new PluginConfigEntity();
        entity.setPluginName(pluginName);
        entity.setDescription(description);
        entity.setEnabled(enabled);
        return entity;
    }
}
