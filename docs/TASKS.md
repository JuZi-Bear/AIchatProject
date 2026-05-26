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

- [x] Workflow Editor 小地图。
- [x] Workflow Editor 多选和框选。
- [x] Workflow Editor 手动连线编辑。
- [x] Workflow Editor 连接线选中和删除。
- [x] Workflow Editor 自动顺序连线按钮。
- [x] Workflow Editor 小地图连接预览。
- [x] Workflow Editor 连线视觉增强。
- [x] Workflow Editor Bezier noodle 曲线连线。
- [x] Workflow Editor 端点/箭头视觉分层。
- [x] Workflow Editor Palette 避让路径。
- [x] Workflow Editor Google Material 演示布局。
- [x] Workflow Editor 顶部步骤引导和分组工具栏。
- [x] Workflow Editor 轻量 Agent Palette 和 CodeAgent 高光。
- [x] Workflow Editor 阶段泳道 Canvas。
- [x] Workflow Editor Inspector Tabs 和流程检查。
- [x] CodeAgent 文件夹工作流模板。
- [x] Project Workspace 受控工作区管理。
- [x] CodeAgent 文件夹模式接入默认 Workspace 与安全摘要。
- [x] Workflow Editor Human Approval 节点。
- [x] Workflow Editor 自定义 Agent 节点编辑。
- [x] Java 平台人工确认 API。
- [x] Java 平台模型 API Key 安全状态管理。
- [x] Models 页面 API Key 更新 / 清除入口。
- [x] Java Workflow Runtime Lite 模板执行接口。
- [x] Workflow Editor 执行模板工作流入口。
- [x] Workflow Templates 页面 MySQL 模板执行入口。
- [x] Replay 展示 executed / simulated / waiting 执行模式。
- [x] Replay 事件筛选和搜索。
- [x] Dashboard 最近 CodeAgent 操作卡片增强。
- [x] RunConsole 结构化需求构造器。
- [x] RunConsole 运行结果高光区。
- [x] RunConsole 结果详情紧凑化。
- [ ] 从 Runtime Lite 预研动态 LangGraph 编排。
- [ ] 更强 CodeAgent diff 可视化。
- [ ] C++ Runner 资源限制增强。

## 暂不做

- [ ] 用户系统。
- [ ] 权限系统。
- [ ] 团队协作。
- [ ] 任务队列。
- [ ] 动态改写 LangGraph 主流程。
