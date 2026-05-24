# v2-only 开发任务清单

## 当前版本状态

- [x] 删除旧 Python UI / CLI 入口文件。
- [x] Docker Compose 收敛为 v2-only 服务。
- [x] Vue -> Java -> FastAPI -> MySQL 主链路可启动。
- [x] Workflow Editor 升级为 Figma 风无限画布。
- [x] Figma-first UI 源规范已加入 `figma/`。
- [x] CodeAgent 文件操作、SSE、审计日志和 Replay 闭环已可演示。

## v2 主链路

- [x] Python FastAPI Agent Engine。
- [x] Java Spring Boot Gateway。
- [x] MySQL 持久化。
- [x] Vue3 + TypeScript 前端。
- [x] Docker Compose 多服务启动。
- [x] RunEvent 事件记录。
- [x] SSE 实时事件。
- [x] Workflow Replay。
- [x] Agent 注册中心。
- [x] Prompt 模板管理。
- [x] Workflow 模板管理。
- [x] Workflow Editor。
- [x] CodeAgent 文件操作。
- [x] C++ Runner Sandbox 可选增强。

## v2-only 收敛任务

- [x] 移除旧 Python 页面 Compose 服务。
- [x] 删除旧 Python 页面入口。
- [x] 删除旧 Python CLI 入口。
- [x] 删除 `main.py`。
- [x] 删除旧 Windows 启动脚本。
- [x] 删除旧 Windows 安装脚本。
- [x] 删除 v1-only 发布、冻结和验收文档。
- [x] 删除过时并行架构主文档。
- [x] 从 `requirements.txt` 移除 v1-only 依赖。
- [x] 根 `Dockerfile` 默认启动 FastAPI。
- [x] README 收敛为 v2-only 入口。
- [x] 文档导航收敛为 v2-only 口径。

## 验收任务

- [ ] `git diff --check`。
- [ ] `npm run build`。
- [ ] `mvn -DskipTests package`。
- [ ] `docker compose up -d --build`。
- [ ] Python / Java / Java proxy health 检查。
- [ ] Vue 关键页面 HTTP 200。
- [ ] CodeAgent smoke。
- [ ] Workflow Template smoke。
- [ ] final v2 acceptance。
- [ ] 更新 `TEST_RESULT_LOG.md` 记录 2026-05-24 v2-only 验收。

## 后续可选优化

- [ ] Workflow Editor 小地图。
- [ ] Workflow Editor 多选和框选。
- [ ] Workflow Editor 手动连线编辑。
- [ ] Replay 事件筛选和搜索。
- [ ] 更强 CodeAgent diff 可视化。
- [ ] C++ Runner 资源限制增强。

## 暂不做

- [ ] 用户系统。
- [ ] 权限系统。
- [ ] 团队协作。
- [ ] 任务队列。
- [ ] 动态改写 LangGraph 主流程。
