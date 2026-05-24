# v2-only Risk And Solution

## Docker 失败

解决：先检查端口占用，再使用本地脚本启动。

```powershell
docker compose ps
docker compose logs backend-java
```

## Java 连接 MySQL 失败

解决：等待 MySQL 初始化完成，确认 `SPRING_DATASOURCE_URL` 指向 `mysql:3306`。

## Vue 调 API 失败

解决：检查 API 模式和地址：

```text
VITE_API_MODE=java
VITE_JAVA_API_BASE_URL=http://localhost:8088/api
```

## Python Agent Engine 失败

解决：检查 `.env`、依赖、8001 端口和 FastAPI `/health`。

## CodeAgent 阻断路径

解决：确认路径在 allowed paths 内。阻断本身是安全能力，演示时可以作为亮点说明。

## SSE 失败

解决：使用历史事件查询和 Replay 展示完整事件。
