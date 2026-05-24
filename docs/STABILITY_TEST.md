# v2-only Stability Test

## 基础环境

- [ ] Python 可启动 FastAPI。
- [ ] Node 可构建 Vue。
- [ ] Java 17 可打包后端。
- [ ] Docker 可启动 Compose。

## 命令

```powershell
cd frontend-vue
npm run build

cd ..\backend-java
mvn -DskipTests package

cd ..
docker compose up -d --build
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
.\scripts\smoke_workflow_template.ps1
.\scripts\final_v2_acceptance.ps1
```

## 页面

- [ ] `/`
- [ ] `/agents`
- [ ] `/workflows/templates`
- [ ] `/workflows/editor`
- [ ] `/history`
- [ ] `/reports`

## 通过标准

- 健康接口可访问。
- 页面 HTTP 200。
- CodeAgent 安全阻断正常。
- Workflow 模板保存、实例化、删除正常。
- Replay 可以展示事件。
