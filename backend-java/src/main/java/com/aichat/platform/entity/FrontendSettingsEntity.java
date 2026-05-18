package com.aichat.platform.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import java.time.LocalDateTime;

@Entity
@Table(name = "frontend_settings")
public class FrontendSettingsEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 80)
    private String selectedModelProvider;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String enabledPluginsJson;

    private boolean demoMode;

    private int maxRetryCount;

    private boolean requireHumanApproval;

    private boolean offlineMode;

    @Column(length = 40)
    private String apiMode;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    @PrePersist
    void prePersist() {
        LocalDateTime now = LocalDateTime.now();
        createdAt = now;
        updatedAt = now;
    }

    @PreUpdate
    void preUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public Long getId() {
        return id;
    }

    public String getSelectedModelProvider() {
        return selectedModelProvider;
    }

    public void setSelectedModelProvider(String selectedModelProvider) {
        this.selectedModelProvider = selectedModelProvider;
    }

    public String getEnabledPluginsJson() {
        return enabledPluginsJson;
    }

    public void setEnabledPluginsJson(String enabledPluginsJson) {
        this.enabledPluginsJson = enabledPluginsJson;
    }

    public boolean isDemoMode() {
        return demoMode;
    }

    public void setDemoMode(boolean demoMode) {
        this.demoMode = demoMode;
    }

    public int getMaxRetryCount() {
        return maxRetryCount;
    }

    public void setMaxRetryCount(int maxRetryCount) {
        this.maxRetryCount = maxRetryCount;
    }

    public boolean isRequireHumanApproval() {
        return requireHumanApproval;
    }

    public void setRequireHumanApproval(boolean requireHumanApproval) {
        this.requireHumanApproval = requireHumanApproval;
    }

    public boolean isOfflineMode() {
        return offlineMode;
    }

    public void setOfflineMode(boolean offlineMode) {
        this.offlineMode = offlineMode;
    }

    public String getApiMode() {
        return apiMode;
    }

    public void setApiMode(String apiMode) {
        this.apiMode = apiMode;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
}
