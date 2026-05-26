package com.aichat.platform.repository;

import com.aichat.platform.entity.ModelConfigEntity;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ModelConfigRepository extends JpaRepository<ModelConfigEntity, Long> {
    Optional<ModelConfigEntity> findByProvider(String provider);
}
