package com.aichat.platform.service;

import com.aichat.platform.entity.ModelConfigEntity;
import com.aichat.platform.repository.ModelConfigRepository;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.springframework.stereotype.Service;

@Service
public class ModelSecretService {

    private static final int GCM_TAG_BITS = 128;
    private static final int IV_BYTES = 12;

    private final ModelConfigRepository modelConfigRepository;
    private final SecureRandom secureRandom = new SecureRandom();

    public ModelSecretService(ModelConfigRepository modelConfigRepository) {
        this.modelConfigRepository = modelConfigRepository;
    }

    public List<Map<String, Object>> listModelSecretStatus() {
        return modelConfigRepository.findAll().stream()
                .map(this::toSecretStatus)
                .toList();
    }

    public Map<String, Object> updateModelSecret(String provider, String apiKey) {
        if (provider == null || provider.isBlank()) {
            throw new IllegalArgumentException("provider is required");
        }

        if (apiKey == null || apiKey.isBlank()) {
            throw new IllegalArgumentException("apiKey is required");
        }

        ModelConfigEntity entity = modelConfigRepository.findByProvider(provider)
                .orElseThrow(() -> new IllegalArgumentException("model provider not found: " + provider));
        entity.setApiKeyCipher(encrypt(apiKey));
        entity.setApiKeyUpdatedAt(LocalDateTime.now());

        return toSecretStatus(modelConfigRepository.save(entity));
    }

    public Map<String, Object> clearModelSecret(String provider) {
        ModelConfigEntity entity = modelConfigRepository.findByProvider(provider)
                .orElseThrow(() -> new IllegalArgumentException("model provider not found: " + provider));
        entity.setApiKeyCipher(null);
        entity.setApiKeyUpdatedAt(null);

        return toSecretStatus(modelConfigRepository.save(entity));
    }

    public boolean hasStoredSecret(ModelConfigEntity entity) {
        return entity.getApiKeyCipher() != null && !entity.getApiKeyCipher().isBlank();
    }

    public Map<String, Object> toSecretStatus(ModelConfigEntity entity) {
        boolean envConfigured = entity.getEnvKey() != null && System.getenv(entity.getEnvKey()) != null;
        boolean storedConfigured = hasStoredSecret(entity);
        Map<String, Object> status = new LinkedHashMap<>();
        status.put("provider", entity.getProvider());
        status.put("name", entity.getName());
        status.put("envKey", entity.getEnvKey());
        status.put("configured", envConfigured || storedConfigured);
        status.put("stored", storedConfigured);
        status.put("envConfigured", envConfigured);
        status.put("maskedKey", storedConfigured ? "sk-****" + tailHint(entity.getApiKeyCipher()) : "");
        status.put("updatedAt", entity.getApiKeyUpdatedAt() == null ? "" : entity.getApiKeyUpdatedAt().toString());
        status.put("message", storedConfigured
                ? "密钥已加密保存到 Java 平台层。当前不会通过 GET 接口返回明文。"
                : "未保存平台密钥；可继续使用 .env 环境变量。");

        return status;
    }

    private String encrypt(String plainText) {
        try {
            byte[] iv = new byte[IV_BYTES];
            secureRandom.nextBytes(iv);
            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(Cipher.ENCRYPT_MODE, secretKey(), new GCMParameterSpec(GCM_TAG_BITS, iv));
            byte[] encrypted = cipher.doFinal(plainText.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(iv) + "." + Base64.getEncoder().encodeToString(encrypted);
        } catch (Exception error) {
            throw new IllegalStateException("failed to encrypt api key");
        }
    }

    private SecretKeySpec secretKey() throws Exception {
        String rawKey = firstNonBlank(
                System.getenv("AICHAT_SECRET_KEY"),
                System.getenv("SPRING_APPLICATION_NAME"),
                "aichat-platform-local-secret"
        );
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] key = digest.digest(rawKey.getBytes(StandardCharsets.UTF_8));
        return new SecretKeySpec(key, "AES");
    }

    private String tailHint(String encryptedValue) {
        String normalized = encryptedValue == null ? "" : encryptedValue.replace(".", "");
        if (normalized.length() <= 4) {
            return "local";
        }

        return normalized.substring(normalized.length() - 4);
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
