# 比赛答辩大纲

## 1. 项目背景

AI 编程助手已经能根据自然语言生成代码，但真实开发不是“生成一次代码”就结束。一个可交付的软件过程还需要需求拆解、测试验证、错误定位、修复迭代、安全控制和结果归档。

本项目希望把 AI 写代码升级为一条可观察、可测试、可修复、可扩展的自动开发流水线。

## 2. 痛点分析

- 自然语言需求不够结构化，直接生成代码容易漏功能。
- 单模型一次性生成代码，稳定性和可解释性不足。
- 代码不运行、不测试，就无法判断是否真正可用。
- 运行失败后，错误日志需要人工阅读和定位。
- 传统演示只展示“成功生成”，缺少“失败后如何恢复”的能力。
- 比赛现场需要稳定可演示，不能被网络、环境或依赖问题轻易打断。

## 3. 解决方案

系统将软件开发过程拆成多个 Agent：

- Product Agent：拆解需求。
- Coder Agent：生成和修复代码。
- Tester Agent：生成 pytest 测试并执行。
- Approval Node：人工审批是否运行代码。
- Runner：保存和运行代码。
- Sentry Agent：分析错误并给出修复建议。
- Plugins：执行文档、安全、重构和 UI 建议等扩展模块。
- Quality Node：给出代码质量评分。
- Report Node：生成 Markdown 报告和历史记录。

## 4. 系统架构

```text
Web UI / CLI
  ↓
LangGraph Workflow
  ↓
Agents + Plugins
  ↓
Code Runner + pytest + coverage
  ↓
Reports + Runs History
```

核心目录：

- `core/`：状态机和质量评分。
- `agents.py`：核心 Agent。
- `plugins/`：自定义 AI 模块。
- `utils/`：运行、测试、报告、历史、摘要工具。
- `config/`：模型、插件、默认参数配置。
- `webui.py` / `graph_demo.py`：演示入口。

## 5. 技术路线

- Python 3.11 作为主开发语言。
- 使用 OpenAI SDK 兼容接口接入 DeepSeek、Qwen、GLM。
- 使用 LangGraph 管理 Agent 状态机。
- 使用 Streamlit 构建比赛展示 Web UI。
- 使用 pytest + coverage 验证代码正确性和覆盖率。
- 使用 Docker 固定运行环境。
- 使用 Markdown 保存报告，使用 JSON 保存运行历史。

## 6. 多 Agent 协作流程

```text
Requirement
→ Product Agent
→ Coder Agent
→ Tester Agent
→ Approval Node
→ Runner
→ Sentry Agent
→ Coder Agent 修复
→ Plugins
→ Quality
→ Report
```

每个 Agent 的职责单一，降低一次性提示词复杂度，也方便 Web UI 展示中解释每个节点的价值。

## 7. LangGraph 状态机

LangGraph 负责保存并传递完整 state，包括：

- 用户需求
- Product 分析结果
- 生成代码
- pytest 测试代码和测试结果
- stdout / stderr
- Sentry 分析结果
- 修复次数
- 审批状态
- 插件结果
- 质量评分
- 报告路径

条件分支：

- Runner 和 pytest 都成功：进入插件、质量评分和报告。
- Runner 或 pytest 失败，且未超过最大修复次数：进入 Sentry，再回到 Coder。
- 达到最大修复次数：停止修复，生成最终报告。
- 人工审批拒绝：不运行代码，直接进入插件、质量评分和报告。

## 8. 自动测试与自愈修复

Tester Agent 会根据需求和代码生成 pytest 测试，并覆盖：

- 正常输入
- 边界情况
- 异常输入
- 核心功能

失败后，Sentry Agent 会综合分析：

- 原始代码
- 测试代码
- pytest stdout
- pytest stderr
- Runner stderr

Coder Agent 修复业务代码后，系统重新运行测试和代码，形成自动修复闭环。

## 9. 插件化 AI 模块

插件系统让主流程之外的能力可以按配置启用：

- Doc Agent：生成说明文档。
- Security Agent：检查危险操作。
- Refactor Agent：给出重构建议。
- UI Agent：给出界面设计建议。

插件统一写入 `plugin_results`，便于 Web UI 和报告展示。未来可以扩展 Deploy Agent、Database Agent、Architect Agent 等。

## 10. 多模型对比

系统支持 DeepSeek、Qwen、GLM 多模型切换和对比。

对比指标：

- success
- 自动修复次数
- pytest 是否通过
- 覆盖率
- 质量评分
- 插件结果摘要

对比报告可直接复制到答辩 PPT，用于说明不同模型在同一任务下的表现差异。

## 11. Web UI 演示

Web UI 采用“左侧控制栏 + 右侧展示区”：

- 左侧选择案例、模型、插件、最大修复次数、演示模式和人工审批。
- 右侧展示 Agent 工作流、输出 Tabs、pytest 测试、质量评分、插件结果、历史记录和报告。

演示模式只显示关键摘要，开发模式保留完整日志和 state。

## 12. Docker 部署

项目提供：

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

默认启动：

```powershell
python -m streamlit run webui.py --server.address=0.0.0.0 --server.port=8501
```

Docker 用于减少新设备 Python 环境不一致的问题。

## 13. 创新点

- 国产大模型多模型接入。
- 多 Agent 自动开发流水线。
- LangGraph 状态机控制复杂流程。
- pytest 驱动自动修复。
- Human-in-the-loop 安全审批。
- 插件式 AI 进程模块。
- 多模型效果对比。
- 代码质量量化评分。
- Web UI 可视化演示和历史复盘。
- Docker 工程化部署。

## 14. 总结与展望

本项目证明了 AI 编程可以从“单次代码生成”升级为“可测试、可修复、可审计、可扩展”的自动开发流水线。

后续可扩展方向：

- 支持多文件项目生成。
- 增加数据库、部署、前端和架构 Agent。
- 接入真实 Figma 设计稿。
- 支持企业私有模型和本地模型。
- 增加更严格的沙箱执行和权限控制。
