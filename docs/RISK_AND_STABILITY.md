# v2-only 风险与稳定性说明

当前版本已经收敛为 v2-only 演示链路：Vue -> Java -> FastAPI -> MySQL。本文记录现场演示风险和兜底策略。

## 主要风险

| 风险 | 影响 | 兜底 |
| --- | --- | --- |
| Docker 启动失败 | 多服务无法一次启动 | 改用本地脚本或手动启动 |
| MySQL 启动慢 | Java 初次连接失败 | 等待容器 healthy 后重试 Java |
| Java 不可用 | Vue Gateway 模式失败 | 临时切换 Vue Python Direct 调试 |
| Python API 不可用 | Agent Engine 无法运行 | 先检查 `.env`、依赖和端口 8001 |
| API Key 不可用 | 模型调用失败 | 使用 demo/offline 模式 |
| CodeAgent 路径阻断 | 文件操作被拒绝 | 展示阻断是安全能力，并改用 allowed path |
| SSE 连接失败 | 实时日志不显示 | 使用历史事件查询与 Replay |

## 现场推荐顺序

1. 优先使用 Docker Compose：

```powershell
docker compose up -d --build
```

2. 检查健康接口：

```powershell
Invoke-RestMethod http://127.0.0.1:8001/health
Invoke-RestMethod http://127.0.0.1:8088/api/health
Invoke-RestMethod http://127.0.0.1:8088/api/agent/health
```

3. 运行 smoke：

```powershell
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
.\scripts\smoke_workflow_template.ps1
```

## 为什么 v2-only

项目已经进入平台化演示阶段，现场重点从“单脚本演示”升级为“可观察、可审计、可回放的平台闭环”。保留 Python Direct 作为开发调试模式，但默认演示入口统一为 Vue + Java + FastAPI + MySQL。
