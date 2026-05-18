package com.aichat.platform.repository;

import com.aichat.platform.entity.RunEventEntity;
import java.util.List;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RunEventRepository extends JpaRepository<RunEventEntity, Long> {

    List<RunEventEntity> findByPlatformRunIdOrderByCreatedAtAsc(String platformRunId);

    List<RunEventEntity> findTop20ByOrderByCreatedAtDesc();

    List<RunEventEntity> findAllByOrderByCreatedAtDesc(Pageable pageable);
}
