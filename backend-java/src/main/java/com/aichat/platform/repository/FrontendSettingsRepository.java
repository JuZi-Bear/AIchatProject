package com.aichat.platform.repository;

import com.aichat.platform.entity.FrontendSettingsEntity;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FrontendSettingsRepository extends JpaRepository<FrontendSettingsEntity, Long> {

    Optional<FrontendSettingsEntity> findTopByOrderByIdAsc();
}
