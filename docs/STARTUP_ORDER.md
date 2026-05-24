# v2-only 启动顺序

当前项目默认只维护 v2 平台化演示链路。

## 推荐方式一：Docker Compose

1. 确认 Docker Desktop 已启动。
2. 如果本机 `3306` 被占用，设置：

```powershell
$env:MYSQL_HOST_PORT="3307"
```

3. 启动：

```powershell
docker compose up --build
```

4. 访问：

- Vue: http://127.0.0.1:5174
- Java: http://127.0.0.1:8088/api/health
- FastAPI: http://127.0.0.1:8001/docs

## 推荐方式二：本地一键联调

```powershell
.\scripts\start_v2_local.ps1
```

默认启动：

- Python FastAPI: `127.0.0.1:8001`
- 临时 MySQL: `127.0.0.1:3307`
- Java Gateway: `127.0.0.1:8088`
- Vue: `127.0.0.1:5174`

停止：

```powershell
.\scripts\stop_v2_local.ps1
```

## 手动开发启动

1. 启动 MySQL。
2. 启动 Python FastAPI：

```powershell
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
```

3. 启动 Java Gateway：

```powershell
cd backend-java
mvn spring-boot:run
```

4. 启动 Vue：

```powershell
cd frontend-vue
npm install
npm run dev
```

## 验收顺序

1. Health：

```powershell
Invoke-RestMethod http://127.0.0.1:8001/health
Invoke-RestMethod http://127.0.0.1:8088/api/health
Invoke-RestMethod http://127.0.0.1:8088/api/agent/health
```

2. Smoke：

```powershell
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
.\scripts\smoke_workflow_template.ps1
```

3. 最终验收：

```powershell
.\scripts\final_v2_acceptance.ps1
```
