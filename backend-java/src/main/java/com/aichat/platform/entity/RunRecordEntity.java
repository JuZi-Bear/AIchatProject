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
@Table(name = "run_record")
public class RunRecordEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 80)
    private String platformRunId;

    @Column(length = 80)
    private String pythonRunId;

    @Column(length = 40)
    private String status;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String requirement;

    @Column(length = 80)
    private String modelProvider;

    @Column(length = 160)
    private String modelName;

    @Column(length = 512)
    private String modelBaseUrl;

    private boolean success;

    private int retryCount;

    private boolean testSuccess;

    private double coveragePercent;

    private double qualityScore;

    @Column(length = 80)
    private String securityStatus;

    @Column(length = 512)
    private String reportPath;

    @Column(length = 512)
    private String statePath;

    @Column(length = 40)
    private String runnerMode;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String runnerWarning;

    @Lob
    @Column(columnDefinition = "LONGTEXT")
    private String runSummaryJson;

    @Lob
    @Column(columnDefinition = "LONGTEXT")
    private String uiViewModelJson;

    @Lob
    @Column(columnDefinition = "LONGTEXT")
    private String pluginResultsJson;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String errorSummary;

    private boolean approved;

    private boolean requireHumanApproval;

    @Lob
    @Column(columnDefinition = "LONGTEXT")
    private String rawResponse;

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

    public String getPlatformRunId() {
        return platformRunId;
    }

    public void setPlatformRunId(String platformRunId) {
        this.platformRunId = platformRunId;
    }

    public String getPythonRunId() {
        return pythonRunId;
    }

    public void setPythonRunId(String pythonRunId) {
        this.pythonRunId = pythonRunId;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getRequirement() {
        return requirement;
    }

    public void setRequirement(String requirement) {
        this.requirement = requirement;
    }

    public String getModelProvider() {
        return modelProvider;
    }

    public void setModelProvider(String modelProvider) {
        this.modelProvider = modelProvider;
    }

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
    }

    public String getModelBaseUrl() {
        return modelBaseUrl;
    }

    public void setModelBaseUrl(String modelBaseUrl) {
        this.modelBaseUrl = modelBaseUrl;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public int getRetryCount() {
        return retryCount;
    }

    public void setRetryCount(int retryCount) {
        this.retryCount = retryCount;
    }

    public boolean isTestSuccess() {
        return testSuccess;
    }

    public void setTestSuccess(boolean testSuccess) {
        this.testSuccess = testSuccess;
    }

    public double getCoveragePercent() {
        return coveragePercent;
    }

    public void setCoveragePercent(double coveragePercent) {
        this.coveragePercent = coveragePercent;
    }

    public double getQualityScore() {
        return qualityScore;
    }

    public void setQualityScore(double qualityScore) {
        this.qualityScore = qualityScore;
    }

    public String getSecurityStatus() {
        return securityStatus;
    }

    public void setSecurityStatus(String securityStatus) {
        this.securityStatus = securityStatus;
    }

    public String getReportPath() {
        return reportPath;
    }

    public void setReportPath(String reportPath) {
        this.reportPath = reportPath;
    }

    public String getStatePath() {
        return statePath;
    }

    public void setStatePath(String statePath) {
        this.statePath = statePath;
    }

    public String getRunnerMode() {
        return runnerMode;
    }

    public void setRunnerMode(String runnerMode) {
        this.runnerMode = runnerMode;
    }

    public String getRunnerWarning() {
        return runnerWarning;
    }

    public void setRunnerWarning(String runnerWarning) {
        this.runnerWarning = runnerWarning;
    }

    public String getRunSummaryJson() {
        return runSummaryJson;
    }

    public void setRunSummaryJson(String runSummaryJson) {
        this.runSummaryJson = runSummaryJson;
    }

    public String getUiViewModelJson() {
        return uiViewModelJson;
    }

    public void setUiViewModelJson(String uiViewModelJson) {
        this.uiViewModelJson = uiViewModelJson;
    }

    public String getPluginResultsJson() {
        return pluginResultsJson;
    }

    public void setPluginResultsJson(String pluginResultsJson) {
        this.pluginResultsJson = pluginResultsJson;
    }

    public String getErrorSummary() {
        return errorSummary;
    }

    public void setErrorSummary(String errorSummary) {
        this.errorSummary = errorSummary;
    }

    public boolean isApproved() {
        return approved;
    }

    public void setApproved(boolean approved) {
        this.approved = approved;
    }

    public boolean isRequireHumanApproval() {
        return requireHumanApproval;
    }

    public void setRequireHumanApproval(boolean requireHumanApproval) {
        this.requireHumanApproval = requireHumanApproval;
    }

    public String getRawResponse() {
        return rawResponse;
    }

    public void setRawResponse(String rawResponse) {
        this.rawResponse = rawResponse;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
}
