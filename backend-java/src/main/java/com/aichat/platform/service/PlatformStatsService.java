package com.aichat.platform.service;

import com.aichat.platform.repository.ReportIndexRepository;
import com.aichat.platform.repository.RunRecordRepository;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class PlatformStatsService {

    private final RunRecordRepository runRecordRepository;
    private final ReportIndexRepository reportIndexRepository;

    public PlatformStatsService(RunRecordRepository runRecordRepository, ReportIndexRepository reportIndexRepository) {
        this.runRecordRepository = runRecordRepository;
        this.reportIndexRepository = reportIndexRepository;
    }

    public Map<String, Object> getStats() {
        long totalRuns = runRecordRepository.count();
        long successRuns = runRecordRepository.countBySuccessTrue();
        long failedRuns = totalRuns - successRuns;
        Double averageScore = runRecordRepository.averageQualityScore();
        double averageQualityScore = averageScore == null
                ? 0
                : Math.round(averageScore * 10.0) / 10.0;

        Map<String, Object> stats = new LinkedHashMap<>();
        stats.put("totalRuns", totalRuns);
        stats.put("successRuns", successRuns);
        stats.put("failedRuns", failedRuns);
        stats.put("averageQualityScore", averageQualityScore);
        stats.put("totalReports", reportIndexRepository.count());
        stats.put("testSuccessRuns", runRecordRepository.countByTestSuccessTrue());
        stats.put("repairedRuns", runRecordRepository.countByRetryCountGreaterThan(0));

        return stats;
    }
}
