# MySQL Setup

本文说明 v2.0 Java 平台服务层使用 MySQL 的本地和 Docker 配置方式。

## 创建数据库

```sql
CREATE DATABASE aichat_platform DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 本地配置

`backend-java/src/main/resources/application.yml` 默认配置：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/aichat_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true
    username: root
    password: your_password
    driver-class-name: com.mysql.cj.jdbc.Driver

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
```

本地启动前需要把 `your_password` 改成实际 MySQL root 密码，或用环境变量覆盖：

```powershell
$env:SPRING_DATASOURCE_USERNAME="root"
$env:SPRING_DATASOURCE_PASSWORD="your_real_password"
cd backend-java
mvn spring-boot:run
```

## Docker Compose

`docker-compose.yml` 已新增 MySQL 8.0 服务：

```yaml
mysql:
  image: mysql:8.0
  container_name: aichat-mysql
  environment:
    MYSQL_ROOT_PASSWORD: root
    MYSQL_DATABASE: aichat_platform
  ports:
    - "3306:3306"
  volumes:
    - mysql_data:/var/lib/mysql
```

Docker 中 `backend-java` 使用容器名访问数据库：

```text
SPRING_DATASOURCE_URL=jdbc:mysql://mysql:3306/aichat_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true
SPRING_DATASOURCE_USERNAME=root
SPRING_DATASOURCE_PASSWORD=root
```

## 持久化范围

MySQL 当前保存：

- Java 平台运行记录：`run_record`
- Java 报告索引：`report_index`
- 前端配置：`frontend_settings`
- 模型配置雏形：`model_config`
- 插件配置雏形：`plugin_config`

Python Agent Engine 仍负责 AI 工作流、LangGraph、插件执行和报告生成。`reports/` 与 `runs/` 文件目录仍保留，用于存储 Markdown 报告和大文本运行状态。

## 常见问题

### Access denied for user

检查 `spring.datasource.username` 和 `spring.datasource.password` 是否与本地 MySQL 一致。

### Unknown database aichat_platform

先执行创建数据库 SQL，或使用 Docker Compose 自动创建数据库。

### Communications link failure

检查 MySQL 是否启动、端口 `3306` 是否被占用，以及 Docker 环境中是否使用 `mysql` 作为数据库主机名。

### Public Key Retrieval is not allowed

如果本地 MySQL 认证策略导致连接失败，确认 JDBC URL 中包含：

```text
allowPublicKeyRetrieval=true
```

### 表没有自动创建

确认 `spring.jpa.hibernate.ddl-auto=update` 生效，并检查 Java 服务启动日志中的 Hibernate 输出。
