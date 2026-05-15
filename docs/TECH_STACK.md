# 技术栈说明

## Python 3.11

项目主语言，用于实现 Agent 调用、LangGraph 工作流、代码运行、测试执行、报告生成和 Web UI。

## DeepSeek / Qwen / GLM

国产大模型服务商。系统支持 DeepSeek、通义千问 Qwen 和智谱 GLM，方便比赛中展示国产模型能力和多模型对比。

## OpenAI SDK 兼容接口

不同模型通过 OpenAI SDK 的兼容接口调用，统一 client 创建方式，降低切换模型的复杂度。

## LangGraph

用于构建多 Agent 状态机。负责节点流转、条件分支、自动修复循环、人工审批和插件执行顺序。

## Streamlit

用于构建 Web UI。展示演示案例、模型选择、Agent 工作流、pytest 结果、质量评分、插件结果、运行历史和 Markdown 报告。

## Rich

用于 CLI 彩色输出，让命令行演示更清晰地区分 Product、Coder、Tester、Sentry 等 Agent 输出。

## pytest

Tester Agent 自动生成 pytest 测试文件，系统使用 pytest 验证生成代码是否满足需求。

## coverage

配合 pytest 统计测试覆盖率，并将覆盖率写入质量评分和运行报告。

## Docker

用于固定运行环境。Dockerfile 基于 `python:3.11-slim`，docker-compose 默认启动 Web UI，并挂载报告、运行历史和输出目录。

## PyYAML

用于读取 `config/settings.yaml`、`config/models.yaml` 和 `config/agents.yaml`，实现配置化管理。

## python-dotenv

用于读取 `.env` 中的 API Key、base_url、默认模型和离线模式配置，避免硬编码敏感信息。

## Markdown 报告

每次运行后自动生成 Markdown 报告，记录需求、模型、Agent 输出、测试结果、覆盖率、质量评分、插件结果、运行历史路径和错误摘要。
