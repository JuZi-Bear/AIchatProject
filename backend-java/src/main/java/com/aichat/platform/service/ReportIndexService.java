package com.aichat.platform.service;

import com.aichat.platform.entity.ReportIndexEntity;
import com.aichat.platform.entity.RunRecordEntity;
import com.aichat.platform.repository.ReportIndexRepository;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Service;

@Service
public class ReportIndexService {

    private final ReportIndexRepository reportIndexRepository;

    public ReportIndexService(ReportIndexRepository reportIndexRepository) {
        this.reportIndexRepository = reportIndexRepository;
    }

    public Optional<ReportIndexEntity> saveReportIndexFromRunRecord(RunRecordEntity record) {
        if (record.getReportPath() == null || record.getReportPath().isBlank()) {
            return Optional.empty();
        }

        String reportName = reportNameFromPath(record.getReportPath());
        if (reportName.isBlank()) {
            return Optional.empty();
        }

        ReportIndexEntity entity = reportIndexRepository
                .findByReportNameAndPlatformRunId(reportName, record.getPlatformRunId())
                .orElseGet(ReportIndexEntity::new);

        entity.setReportName(reportName);
        entity.setReportPath(record.getReportPath());
        entity.setPlatformRunId(record.getPlatformRunId());
        entity.setPythonRunId(record.getPythonRunId());
        entity.setRequirement(record.getRequirement());
        entity.setSuccess(record.isSuccess());
        entity.setQualityScore(record.getQualityScore());

        return Optional.of(reportIndexRepository.save(entity));
    }

    public List<ReportIndexEntity> listReports() {
        return reportIndexRepository.findAllByOrderByCreatedAtDesc();
    }

    public Optional<ReportIndexEntity> getReportByName(String reportName) {
        return reportIndexRepository.findByReportName(reportName);
    }

    public List<ReportIndexEntity> getReportsByPlatformRunId(String platformRunId) {
        return reportIndexRepository.findByPlatformRunIdOrderByCreatedAtDesc(platformRunId);
    }

    private String reportNameFromPath(String reportPath) {
        String normalized = reportPath.replace("\\", "/");
        int index = normalized.lastIndexOf("/");
        return index >= 0 ? normalized.substring(index + 1) : normalized;
    }
}
