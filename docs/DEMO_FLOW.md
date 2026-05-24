# v2-only Demo Flow

## 推荐流程

1. 启动 v2 服务。
2. 打开 Vue Dashboard。
3. 进入 Workflow Editor，拖入 Agent / CodeAgent / 分支节点。
4. 执行 CodeAgent 文件操作。
5. 查看 SSE 实时事件。
6. 查看 JSONL 审计日志和 diff。
7. 进入 Replay 回放。
8. 展示 Java + MySQL 平台记录。

## 命令

```powershell
docker compose up -d --build
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
.\scripts\smoke_workflow_template.ps1
```
