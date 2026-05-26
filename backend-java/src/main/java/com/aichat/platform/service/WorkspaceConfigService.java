package com.aichat.platform.service;

import com.aichat.platform.entity.WorkspaceConfigEntity;
import com.aichat.platform.model.WorkspaceConfig;
import com.aichat.platform.repository.WorkspaceConfigRepository;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class WorkspaceConfigService {

    private final WorkspaceConfigRepository workspaceConfigRepository;

    public WorkspaceConfigService(WorkspaceConfigRepository workspaceConfigRepository) {
        this.workspaceConfigRepository = workspaceConfigRepository;
    }

    @Transactional
    public List<WorkspaceConfig> listWorkspaces() {
        if (workspaceConfigRepository.count() == 0) {
            workspaceConfigRepository.save(toEntity(new WorkspaceConfigEntity(), WorkspaceConfig.defaults()));
        }

        return workspaceConfigRepository.findAllByOrderByDefaultWorkspaceDescNameAsc()
                .stream()
                .map(this::toModel)
                .toList();
    }

    @Transactional
    public WorkspaceConfig createWorkspace(WorkspaceConfig request) {
        WorkspaceConfig normalized = request == null ? WorkspaceConfig.defaults() : request.normalized();
        WorkspaceConfigEntity entity = toEntity(new WorkspaceConfigEntity(), normalized);

        if (workspaceConfigRepository.count() == 0 || normalized.isDefault()) {
            clearDefaultWorkspace(null);
            entity.setDefaultWorkspace(true);
        }

        return toModel(workspaceConfigRepository.save(entity));
    }

    @Transactional
    public Optional<WorkspaceConfig> updateWorkspace(Long id, WorkspaceConfig request) {
        return workspaceConfigRepository.findById(id).map(entity -> {
            boolean wasDefault = entity.isDefaultWorkspace();
            WorkspaceConfig normalized = request == null ? toModel(entity) : request.normalized();
            toEntity(entity, normalized);

            if (normalized.isDefault()) {
                clearDefaultWorkspace(id);
                entity.setDefaultWorkspace(true);
                entity.setEnabled(true);
            } else if (wasDefault) {
                entity.setDefaultWorkspace(true);
                entity.setEnabled(true);
            }

            return toModel(workspaceConfigRepository.save(entity));
        });
    }

    @Transactional
    public Optional<WorkspaceConfig> deleteWorkspace(Long id) {
        return workspaceConfigRepository.findById(id).map(entity -> {
            WorkspaceConfig deleted = toModel(entity);
            boolean wasDefault = entity.isDefaultWorkspace();
            workspaceConfigRepository.delete(entity);

            if (wasDefault) {
                workspaceConfigRepository.findAllByOrderByDefaultWorkspaceDescNameAsc()
                        .stream()
                        .findFirst()
                        .ifPresent(next -> {
                            next.setDefaultWorkspace(true);
                            next.setEnabled(true);
                            workspaceConfigRepository.save(next);
                        });
            }

            return deleted;
        });
    }

    private void clearDefaultWorkspace(Long exceptId) {
        workspaceConfigRepository.findAll().forEach(current -> {
            if (current.isDefaultWorkspace() && (exceptId == null || !current.getId().equals(exceptId))) {
                current.setDefaultWorkspace(false);
                workspaceConfigRepository.save(current);
            }
        });
    }

    private WorkspaceConfigEntity toEntity(WorkspaceConfigEntity entity, WorkspaceConfig model) {
        WorkspaceConfig normalized = model.normalized();
        entity.setName(normalized.name());
        entity.setRootPath(normalized.rootPath());
        entity.setEnabled(normalized.enabled());
        entity.setDefaultWorkspace(normalized.isDefault());
        entity.setDescription(normalized.description());
        entity.setMaxFiles(normalized.maxFiles());
        entity.setMaxReadChars(normalized.maxReadChars());
        entity.setDryRunDefault(normalized.dryRunDefault());
        entity.setBackupBeforeWrite(normalized.backupBeforeWrite());
        return entity;
    }

    private WorkspaceConfig toModel(WorkspaceConfigEntity entity) {
        return new WorkspaceConfig(
                entity.getId(),
                entity.getName(),
                entity.getRootPath(),
                entity.isEnabled(),
                entity.isDefaultWorkspace(),
                entity.getDescription(),
                entity.getMaxFiles(),
                entity.getMaxReadChars(),
                entity.isDryRunDefault(),
                entity.isBackupBeforeWrite(),
                entity.getCreatedAt() == null ? null : entity.getCreatedAt().toString(),
                entity.getUpdatedAt() == null ? null : entity.getUpdatedAt().toString()
        ).normalized();
    }
}
