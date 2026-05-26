# 技术框架扩展总规划

当前项目已进入 v2-only 平台化演示阶段。本规划用于约束后续扩展方向，避免在演示稳定前引入过重业务。

## 当前技术架构现状

- Vue3 + TypeScript：平台前端和工作流可视化。
- Java Spring Boot：平台 API Gateway、任务记录、配置、RunEvent、SSE、Replay。
- MySQL：平台持久化。
- Python FastAPI Agent Engine：AI 工作流 API。
- LangGraph：多 Agent 工作流编排。
- Agent Registry / Prompt Templates：Agent 元信息和 Prompt 管理。
- Workflow Templates：模板管理和可视化编辑入口。
- CodeAgent：受控项目文件操作。
- C++ Runner Sandbox：可选执行安全增强。
- Docker Compose：v2 多服务部署。
- Figma：前端 UI 设计源。

## 当前架构优势

- 前端、平台服务、Agent Engine、持久化、Runner 分层清晰。
- Java 不直接承载 LangGraph，Python 专注 AI 工作流。
- Vue 通过 `ui_view_model`、`run_summary`、RunEvent 和 Replay 展示结果。
- CodeAgent 文件操作可审计、可推送、可回放。
- Docker Compose 可一键启动完整平台链路。
- Figma-first 让 UI 修改可以回到个人可编辑设计源。

## 当前架构不足

- Java 任务生命周期还可以更细。
- Workflow Editor 尚未驱动真实动态 LangGraph 分支。
- C++ Runner 仍是最小安全执行雏形。
- 缺少多任务队列。
- 缺少用户、权限和团队协作。
- 本地模型适配层尚未完整建立。

## 第一阶段：平台服务层增强

目标：增强 Java 平台任务生命周期、配置中心、错误响应和审计能力。

已完成：

- RunRecord / RunEvent / ReportIndex。
- MySQL 持久化。
- SSE 实时事件。
- Replay API。
- Settings / Model / Plugin config。
- Workflow 模板保存、版本、删除和实例化。
- Human Approval 平台层审批事件和批准 / 拒绝 API。
- Java Gateway 模型 API Key 状态管理和加密保存接口。

后续建议：

- 任务状态机显式化，尤其是 `WAITING_FOR_HUMAN -> APPROVED / REJECTED` 后的自动继续策略。
- 事件查询筛选。
- 平台审计日志增强。
- 统一错误码。

## 第二阶段：前端平台化增强

目标：让 Vue 成为稳定平台工作台。

已完成：

- Dashboard。
- History / Reports / Agents。
- Workflow Templates。
- Google Material 风 Workflow Editor：步骤引导、轻量 Agent Palette、阶段泳道 Canvas、Inspector Tabs。
- CodeAgentPanel。
- Replay。
- CodeAgent 文件夹工作流模板选择。
- Workflow Editor 自定义 Agent 节点和 Human Approval 节点。
- Models 页面平台层 API Key 更新 / 清除入口。
- Workflow Runtime Lite：Java 平台层读取 MySQL 模板并按节点顺序写入事件，CodeAgent 节点真实执行，其它 Agent 节点作为可回放模拟事件。

后续建议：

- 小地图。
- 多选和框选。
- 手动连线编辑。
- Replay 过滤和搜索。
- Figma Component Variants 同步。
- 将自定义 Agent 从“模板节点”升级为可注册 Agent 前，需要先从 Workflow Runtime Lite 演进到 Dynamic Workflow Runtime。

## 第三阶段：AI Agent Engine 增强

目标：提升 Python Agent Engine 可扩展性。

已完成：

- Agent Registry。
- Prompt 模板目录。
- Workflow Templates。
- workflow_events。

后续建议：

- 多模型 Provider 抽象层。
- Prompt 版本管理。
- 本地模型接口预留。
- Workflow 模板协议稳定后，再考虑动态编排。

## 第四阶段：执行安全增强

目标：提升代码执行安全性和可观测性。

已完成：

- CodeAgent 路径策略、阻断路径、审计日志。
- C++ Runner 最小版本。

后续建议：

- Runner 资源限制。
- Docker Sandbox 预留。
- 更强危险行为扫描。
- 执行结果结构化。

## 第五阶段：平台化能力

目标：从单人演示进入多人平台。

当前不建议马上做：

- 用户系统。
- 权限系统。
- 团队协作。
- 项目空间。
- 多任务队列。

原因：

- 当前优先稳定演示闭环。
- 过早引入权限和协作会显著增加复杂度。

## 当前推荐路线

1. 稳定 v2-only 演示版。
2. 继续验证 Workflow Runtime Lite 的节点执行边界。
3. 增强 Replay 和事件分析。
4. 提升 CodeAgent diff / 审计展示。
5. 再进入 Dynamic Workflow Runtime、任务生命周期和配置中心深水区。
