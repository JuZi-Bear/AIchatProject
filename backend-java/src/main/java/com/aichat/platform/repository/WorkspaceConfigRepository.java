package com.aichat.platform.repository;

import com.aichat.platform.entity.WorkspaceConfigEntity;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkspaceConfigRepository extends JpaRepository<WorkspaceConfigEntity, Long> {

    List<WorkspaceConfigEntity> findAllByOrderByDefaultWorkspaceDescNameAsc();

    Optional<WorkspaceConfigEntity> findFirstByDefaultWorkspaceTrueOrderByIdAsc();
}
