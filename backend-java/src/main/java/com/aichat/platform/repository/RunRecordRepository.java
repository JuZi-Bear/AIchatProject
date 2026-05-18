package com.aichat.platform.repository;

import com.aichat.platform.entity.RunRecordEntity;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface RunRecordRepository extends JpaRepository<RunRecordEntity, Long> {

    List<RunRecordEntity> findAllByOrderByCreatedAtDesc();

    Optional<RunRecordEntity> findByPlatformRunId(String platformRunId);

    long countBySuccessTrue();

    long countBySuccessFalse();

    long countByTestSuccessTrue();

    long countByRetryCountGreaterThan(int retryCount);

    @Query("select avg(r.qualityScore) from RunRecordEntity r")
    Double averageQualityScore();
}
