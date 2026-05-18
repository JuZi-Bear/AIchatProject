package com.aichat.platform.repository;

import com.aichat.platform.entity.PluginConfigEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PluginConfigRepository extends JpaRepository<PluginConfigEntity, Long> {
}
