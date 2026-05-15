# 项目创新点

## 1. 基于国产大模型

项目支持 DeepSeek、通义千问 Qwen 和智谱 GLM，默认使用 DeepSeek。不同模型通过 OpenAI SDK 兼容接口接入，既体现国产大模型能力，也方便比赛现场切换和对比。

## 2. 多智能体协作

系统将自动开发拆分为 Product、Coder、Tester、Sentry、Quality 和多个插件 Agent。每个 Agent 专注一个任务，流程更清晰，也便于解释、调试和扩展。

## 3. LangGraph 状态机工作流

项目使用 LangGraph 管理节点和状态流转，避免把复杂逻辑写成线性脚本。状态机可以表达条件分支、失败重试、人工审批和插件扩展，适合展示“可控的 AI 工作流”。

## 4. 测试驱动自动修复

Tester Agent 会根据需求和代码自动生成 pytest 测试。系统不只依赖程序是否运行成功，还会根据测试失败结果触发 Sentry 分析和 Coder 修复，形成测试驱动的自愈闭环。

## 5. 插件式 AI 进程模块

项目内置 Doc Agent、Security Agent、Refactor Agent 和 UI Agent，并支持通过配置启用或关闭。后续可以快速扩展 Deploy Agent、Database Agent、Architect Agent 等模块。

## 6. 多模型对比

Web UI 和 CLI 支持选择 2-3 个模型对同一需求独立运行完整流程，并对比成功状态、修复次数、pytest、覆盖率、质量评分和插件结果。

## 7. 代码质量评分

Quality Node 将测试通过、运行成功、覆盖率、安全检查和自动修复次数转换成 100 分制评分，让结果从“能运行”升级为“可量化评价”。

## 8. Human-in-the-loop 安全审批

系统在执行 AI 生成代码前加入人工审批节点。用户未确认时不会运行代码，降低比赛现场和真实使用中的安全风险。

## 9. Docker 工程化部署

项目提供 Dockerfile 和 docker-compose.yml，可以在新设备上快速启动 Web UI，减少 Python 环境差异带来的问题。

## 10. Web UI 可视化演示

Streamlit Web UI 将多 Agent 状态、自动修复过程、pytest 结果、质量评分、插件结果和 Markdown 报告集中展示，适合比赛现场投屏讲解。
