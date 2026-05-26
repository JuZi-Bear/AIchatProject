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
@Table(name = "workspace_config")
public class WorkspaceConfigEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 120)
    private String name;

    @Column(nullable = false, length = 500)
    private String rootPath;

    private boolean enabled;

    private boolean defaultWorkspace;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String description;

    private int maxFiles;

    private int maxReadChars;

    private boolean dryRunDefault;

    private boolean backupBeforeWrite;

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

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getRootPath() {
        return rootPath;
    }

    public void setRootPath(String rootPath) {
        this.rootPath = rootPath;
    }

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public boolean isDefaultWorkspace() {
        return defaultWorkspace;
    }

    public void setDefaultWorkspace(boolean defaultWorkspace) {
        this.defaultWorkspace = defaultWorkspace;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public int getMaxFiles() {
        return maxFiles;
    }

    public void setMaxFiles(int maxFiles) {
        this.maxFiles = maxFiles;
    }

    public int getMaxReadChars() {
        return maxReadChars;
    }

    public void setMaxReadChars(int maxReadChars) {
        this.maxReadChars = maxReadChars;
    }

    public boolean isDryRunDefault() {
        return dryRunDefault;
    }

    public void setDryRunDefault(boolean dryRunDefault) {
        this.dryRunDefault = dryRunDefault;
    }

    public boolean isBackupBeforeWrite() {
        return backupBeforeWrite;
    }

    public void setBackupBeforeWrite(boolean backupBeforeWrite) {
        this.backupBeforeWrite = backupBeforeWrite;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
}
