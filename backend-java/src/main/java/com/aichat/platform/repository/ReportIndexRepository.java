package com.aichat.platform.repository;

import com.aichat.platform.entity.ReportIndexEntity;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReportIndexRepository extends JpaRepository<ReportIndexEntity, Long> {

    List<ReportIndexEntity> findAllByOrderByCreatedAtDesc();

    Optional<ReportIndexEntity> findByReportName(String reportName);

    Optional<ReportIndexEntity> findByReportNameAndPlatformRunId(String reportName, String platformRunId);

    List<ReportIndexEntity> findByPlatformRunIdOrderByCreatedAtDesc(String platformRunId);
}
