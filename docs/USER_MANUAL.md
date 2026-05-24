# v2-only 用户手册

本文面向比赛演示和本地试用用户，说明如何启动和使用当前 v2 平台。

## 快速启动

推荐使用 Docker Compose：

```powershell
cd D:\AIchatProject
docker compose up -d --build
```

访问：

- Vue 前端：`http://127.0.0.1:5174`
- Java Gateway：`http://127.0.0.1:8088/api/health`
- FastAPI Docs：`http://127.0.0.1:8001/docs`

## 本地脚本启动

```powershell
.\scripts\start_v2_local.ps1
```

## 手动启动

```powershell
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
cd backend-java
mvn spring-boot:run
cd ..\frontend-vue
npm run dev
```

## 常用页面

- Dashboard：平台总览。
- RunConsole：执行任务和 CodeAgent。
- History：查看平台运行记录。
- Reports：查看报告索引和内容。
- Agents：查看 Agent 注册中心。
- Workflow Templates：查看和管理模板。
- Workflow Editor：拖拽式工作流编辑。
- Replay：回放某次运行事件。

## CodeAgent 演示

1. 打开 Workflow Editor。
2. 拖入 CodeAgent 节点。
3. 设置允许路径内的读写或列目录操作。
4. 执行任务。
5. 在 RunConsole 查看实时事件。
6. 查看审计日志和文件 diff。
7. 打开 Replay 回放事件顺序。

## 验证命令

```powershell
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
.\scripts\smoke_workflow_template.ps1
.\scripts\final_v2_acceptance.ps1
```

## 常见问题

### Java 连接 MySQL 失败

先确认 MySQL 容器已启动并等待初始化完成，再重启 Java 服务。

### Vue 调 API 失败

检查 `frontend-vue/.env.development` 或生产构建中的 API 模式。v2 演示推荐 Java Gateway。

### SSE 不显示

先查看历史事件接口和 Replay。SSE 是实时增强能力，历史事件仍保存在 MySQL。

### CodeAgent 写文件被阻断

检查路径是否在 `allowed_paths` 内，是否命中 `blocked_paths`。被阻断会写入事件和审计日志。
