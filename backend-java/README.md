# backend-java

## 目录作用

`backend-java/` 是 v2.0 平台化升级轨的 Java Spring Boot 服务层。当前职责是 API Gateway、MySQL 任务记录、报告索引、平台统计、前端配置、模型配置和插件配置管理。

## 核心文件

- `pom.xml`：Maven 依赖和构建配置。
- `src/main/java/com/aichat/platform/controller/`：HTTP Controller。
- `src/main/java/com/aichat/platform/service/`：平台服务、Python Agent Client、记录和配置管理。
- `src/main/java/com/aichat/platform/entity/`：JPA 实体。
- `src/main/java/com/aichat/platform/repository/`：JPA Repository。
- `src/main/resources/application.yml`：端口、Python Agent Engine 和 MySQL 配置。
- `Dockerfile`：Java 服务容器构建。

## 不能随便修改

- 不要让 Java 替代 Python Agent Engine。
- 不要删除原有代理接口。
- 不要改变 Python API 的返回结构。
- 不要把数据库密码或 API Key 写死到源码中。
- 不要在 Java 层直接解析 LangGraph 内部 state。

## 轨道归属

v2-platform。

## 当前开发状态

active。
