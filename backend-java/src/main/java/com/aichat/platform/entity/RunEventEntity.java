package com.aichat.platform.entity;

import com.aichat.platform.model.RunEventType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import java.time.LocalDateTime;

@Entity
@Table(name = "run_event")
public class RunEventEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 80, nullable = false)
    private String platformRunId;

    @Column(length = 80)
    private String pythonRunId;

    @Enumerated(EnumType.STRING)
    @Column(length = 60, nullable = false)
    private RunEventType eventType;

    @Column(length = 120)
    private String eventText;

    @Column(length = 60)
    private String agent;

    @Column(length = 40)
    private String status;

    @Column(length = 512)
    private String message;

    @Lob
    @Column(columnDefinition = "LONGTEXT")
    private String detailJson;

    private LocalDateTime createdAt;

    @PrePersist
    void prePersist() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
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

    public RunEventType getEventType() {
        return eventType;
    }

    public void setEventType(RunEventType eventType) {
        this.eventType = eventType;
    }

    public String getEventText() {
        return eventText;
    }

    public void setEventText(String eventText) {
        this.eventText = eventText;
    }

    public String getAgent() {
        return agent;
    }

    public void setAgent(String agent) {
        this.agent = agent;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getDetailJson() {
        return detailJson;
    }

    public void setDetailJson(String detailJson) {
        this.detailJson = detailJson;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
