# v2-only 架构规划

当前项目已收敛为 v2-only 平台化演示版。默认运行链路为：

```text
Vue3 + TypeScript
  -> Java Spring Boot Platform API
  -> Python FastAPI Agent Engine
  -> LangGraph / Agent / CodeAgent
  -> MySQL / RunEvent / SSE / Replay
```

## 当前架构

### frontend-vue

- Vue3 + TypeScript 平台前端。
- 负责 Dashboard、RunConsole、History、Reports、Agents、Workflow Templates、Workflow Editor、Replay。
- 通过 Java Gateway 访问平台能力。
- Workflow Editor 已采用 Figma 风无限画布。

### backend-java

- Java Spring Boot 平台服务层。
- 提供 API Gateway、MySQL 持久化、RunEvent、SSE、Replay、Settings、Model/Plugin config、Workflow 模板管理。
- 负责调用 Python Agent Engine，不承载 Agent 逻辑。

### Python FastAPI Agent Engine

- `api_server.py` 暴露 Agent Engine API。
- `services/run_service.py` 封装工作流运行、历史、报告、模型、插件。
- `core/` 和 LangGraph 负责 Agent 工作流。
- 输出 `run_summary`、`ui_view_model`、`workflow_events`。

### MySQL

- 保存平台运行记录、事件、报告索引、配置、Workflow 模板和 Workspace 配置。

### CodeAgent

- 提供 `read_file`、`write_file`、`list_files`。
- 支持受控文件夹工作区模式：扫描、读取、生成计划、dry-run diff、应用变更。
- 遵守路径白名单、阻断路径和读取长度限制。
- 写入 JSONL 审计日志。
- 事件进入 Java RunEvent、SSE 和 Replay。

### C++ Runner Sandbox

- 保留为可选执行安全增强。
- 默认不替代 Python Runner。

## 已完成阶段

- [x] FastAPI Agent Engine API。
- [x] Vue3 + TypeScript 前端。
- [x] Java Spring Boot Gateway。
- [x] MySQL 持久化。
- [x] Java 平台记录、报告索引和统计。
- [x] Vue 接入 Java + MySQL 数据视图。
- [x] RunEvent 事件记录。
- [x] SSE 实时事件推送。
- [x] Python `workflow_events` 细粒度事件。
- [x] Workflow Replay。
- [x] Agent 注册中心。
- [x] Prompt 模板管理。
- [x] Workflow 模板管理。
- [x] Workflow Editor。
- [x] CodeAgent 文件操作。
- [x] C++ Runner Sandbox 最小版本。
- [x] Docker Compose v2-only 总集成。
- [x] Figma-first UI 设计源规范。
- [x] v2 Demo Polish：Workflow Editor 小地图/多选、Replay 筛选、Dashboard CodeAgent 操作卡片。
- [x] Workflow Editor 可视化编排体验增强：手动连线、连接删除、快捷键提示、小地图连接预览。
- [x] v2 Demo Polish：连线视觉增强、RunConsole 结构化输入、运行结果高光区。
- [x] Workflow Editor 连线视觉二次打磨：Bezier noodle 曲线、端点/箭头分层、Palette 避让。
- [x] CodeAgent 文件夹工作流模板和 Project Workspace 受控工作区管理。
- [x] Human Approval 平台层审批节点、事件和 Replay 确认入口。
- [x] Workflow Editor 自定义 Agent 模板节点。
- [x] Java Gateway 模型 API Key masked 状态和加密保存接口。

## v2-only 收敛结果

- 旧 Python UI / CLI 入口已删除。
- Docker Compose 仅保留 `mysql`、`ai-agent-api`、`backend-java`、`frontend-vue`。
- 根 `Dockerfile` 默认启动 FastAPI。
- README 和核心文档默认只说明 v2 主链路。

## 当前限制

- Workflow Editor 当前编辑平台模板和可回放任务视图；手动连线和强化连接线用于前端编排表达和模板保存，不直接驱动动态 LangGraph 分支。
- Custom Agent 当前是模板可视化节点，不会自动注册到 Python Agent Registry。
- Human Approval 第一阶段是 Java 平台层审批事件，不会中断真实 LangGraph 运行。
- Java Gateway 可保存平台层模型密钥状态，但 Python Direct 仍通过 `.env` 配置模型 Key。
- Java Gateway Workspace 是平台体验层配置；Python CodeAgent 仍依据 `config/settings.yaml` 做最终路径安全裁判。
- RunConsole 结构化需求构造器只在前端拼接 `requirement`，不改变 POST `/runs` 请求结构。
- CodeAgent 是简化文件操作模块，不是完整 Codex。
- C++ Runner 当前不是完整安全沙箱。
- 用户系统、权限系统、团队协作和任务队列暂未启用。

## 推荐下一步

1. 继续稳定 v2-only 演示版和验收脚本。
2. 预研动态 Workflow Runtime，让模板连接未来可以安全映射到后端执行拓扑。
3. 增强 Replay 事件对比和导出。
4. 继续同步 Figma 设计源与 Vue 实现。
5. 暂缓用户/权限/团队协作等复杂平台功能。
