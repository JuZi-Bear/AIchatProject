package com.aichat.platform.repository;

import com.aichat.platform.entity.WorkflowTemplateEntity;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowTemplateRepository extends JpaRepository<WorkflowTemplateEntity, Long> {

    List<WorkflowTemplateEntity> findAllByOrderByUpdatedAtDesc();

    Optional<WorkflowTemplateEntity> findByTemplateKey(String templateKey);
}
