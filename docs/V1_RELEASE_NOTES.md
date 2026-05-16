# v1.0 Release Notes

## 版本名称

AI Multi-Agent Pipeline 比赛演示版

## 版本定位

v1.0 面向比赛现场演示，目标是稳定展示“自然语言需求 → 多 Agent 协作 → 自动测试 → 自动修复 → 插件扩展 → 质量评分 → Markdown 报告”的完整闭环。

本版本冻结核心运行逻辑，后续只做 Bug 修复、文档优化和小范围 UI 调整。

## 核心功能清单

- 用户输入自然语言需求，系统生成 Python 代码。
- Product Agent 负责需求拆解。
- Coder Agent 负责代码生成和自动修复。
- Tester Agent 负责生成 pytest 测试并运行测试。
- Approval Node 提供 Human-in-the-loop 人工审批。
- Runner 保存并运行 `output/generated_code.py`。
- Sentry Agent 分析 stderr、pytest 输出和测试代码，触发修复。
- 最多自动修复 N 次，默认 3 次。
- pytest + coverage 判断代码正确性和覆盖率。
- Quality Evaluator 生成 100 分制质量评分。
- 插件系统支持 Doc、Security、Refactor、UI Agent。
- 支持 DeepSeek、Qwen、GLM 多模型切换。
- 支持多模型效果对比。
- 支持离线演示模式，API 不可用时仍可演示。
- 支持 Markdown 报告生成。
- 支持 runs 历史记录保存和回放。
- 支持 CLI 和 Web UI 两种演示入口。
- 支持 Docker 部署。

## 已完成技术模块

- Python 3.11 项目基础结构。
- LangGraph 多 Agent 状态机。
- DeepSeek / Qwen / GLM 多模型配置。
- OpenAI SDK 兼容接口调用。
- `config/settings.yaml` 默认配置。
- `services/run_service.py` Application Service 层。
- `utils/summary_builder.py` 统一 `run_summary`。
- `utils/ui_state_builder.py` 统一 `ui_view_model`。
- `utils/error_utils.py` 统一错误摘要。
- `utils/run_store.py` 运行历史保存。
- `utils/test_runner.py` pytest + coverage 执行。
- `utils/code_runner.py` 代码保存、运行和安全检查。
- 插件系统统一返回 `plugin_results`。
- Markdown 报告生成与报告聚合。
- Dockerfile 和 docker-compose.yml。

## 已完成 UI/UX 优化

- Web UI 调整为左侧控制栏 + 右侧主展示区。
- Header 展示当前模型、运行状态和 run_id。
- Summary Cards 横向展示 success、retry_count、test_success、coverage、quality_score、security_status。
- AI 工作流时间轴展示节点图标、中文状态、摘要和整体进度。
- 自动修复高光时刻突出失败、Sentry 分析、Coder 修复和最终测试结果。
- 最终结果总览一屏展示核心结论。
- 结果索引提供最终代码、pytest、错误摘要、自动修复、插件结果、报告和历史入口。
- Agent 输出统一放入 Product、Coder、Tester、Sentry、Plugins、Report、Raw State Tabs。
- 长内容默认折叠，减少页面空白。
- 演示模式隐藏冗长日志，开发模式保留完整调试信息。

## 已完成架构重构

- 抽离 `core/`：AgentState、workflow、quality evaluator。
- 保留 `graph.py` 兼容入口。
- 抽离 `run_summary`，避免多处重复解析 state。
- 抽离 `ui_view_model`，作为 UI 展示稳定数据结构。
- 抽离 `run_service`，作为 Streamlit 和未来 API 复用的服务边界。
- 新增 `docs/API_CONTRACT.md`，预留 FastAPI / Vue / Java 接口结构。
- 新增 `docs/V2_ARCHITECTURE_PLAN.md`，规划 v2.0 多技术栈升级路线。

## 已知限制

- 当前主要面向单文件 Python 示例，暂不适合大型多文件工程。
- Runner 仍以 Python subprocess 为主，安全隔离能力有限。
- 自动测试由模型生成，复杂需求下测试质量仍需人工复核。
- 自动修复不保证 100% 成功，达到最大修复次数后会停止并生成报告。
- Streamlit 适合 v1.0 演示，复杂前端交互将在 v2.0 规划中升级。
- 多模型对比依赖对应 API Key 和网络环境。
- 离线模式适合演示兜底，不代表真实模型效果。

## 后续 v2.0 扩展方向

- 使用 FastAPI 包装 Python Agent Engine。
- 使用 Vue3 + TypeScript 替换 Streamlit，构建正式 Dashboard。
- 使用 Java Spring Boot 提供平台服务层、用户权限、任务管理和审计。
- 使用 C++ Runner Sandbox 增强代码执行隔离。
- 使用 Docker Compose 编排多服务。
- 支持更复杂的多文件项目生成、测试、修复和部署。
