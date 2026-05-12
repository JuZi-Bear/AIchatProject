# 竞赛评分点包装

## 1. 国产大模型应用

项目基于 DeepSeek API 构建核心 Agent，体现国产大模型在软件工程自动化场景中的应用能力。

可强调点：

- 使用 DeepSeek 完成需求分析、代码生成、测试检查和错误分析。
- 不是简单问答，而是接入真实代码运行流程。
- 具备工程化封装，后续可切换其他国产模型。

## 2. 多智能体协作

项目将复杂开发流程拆分为多个 Agent：

- Product Agent：需求拆解
- Coder Agent：代码生成与修复
- Tester Agent：静态检查
- Sentry Agent：错误日志分析

可强调点：

- 每个 Agent 角色清晰。
- 输出结果逐步传递。
- 比单 Agent 生成更容易解释和演示。

## 3. 自动开发流水线

项目实现从需求到代码的完整自动化路径：

```text
需求 → 产品方案 → 代码 → 检查 → 保存 → 运行 → 修复
```

可强调点：

- 不停留在“生成代码”。
- 生成后会保存成真实 Python 文件。
- 系统会实际运行代码，验证结果。

## 4. 自动测试

当前项目包含两层测试能力：

- Tester Agent 静态检查代码。
- Code Runner 使用 subprocess 真实运行代码。

可强调点：

- 静态检查关注语法、逻辑和入口调用。
- 动态运行捕获 stdout、stderr、returncode。
- 运行结果可在 CLI 和 Web UI 中展示。

## 5. 错误反馈闭环

当代码运行失败时，系统会自动进入错误反馈流程：

```text
stderr → Sentry Agent → 修复建议 → Coder Agent → 新代码 → 再运行
```

可强调点：

- 支持最多自动修复 3 次。
- 修复过程可视化展示。
- 能展示“第一次失败，之后修复成功”的比赛亮点。

## 6. LangGraph 状态机

项目使用 LangGraph 管理工作流状态和条件分支。

状态字段包括：

- requirement
- product_result
- code
- tester_result
- stdout
- error_log
- sentry_result
- retry_count
- success

可强调点：

- 工作流不是硬编码顺序脚本，而是可扩展状态机。
- runner_node 根据 success 和 retry_count 决定是否进入修复。
- 未来可以增加更多节点，例如 Architect Agent、Report Agent、UI Agent。

## 7. Figma + Web UI 展示

项目不仅有 CLI，也准备了设计协作和 Web 演示：

- `figma/design_link.md`
- `docs/UI_SPEC.md`
- `webui.py`

可强调点：

- Figma 文档说明了页面目标和交互。
- Web UI 对齐 AI Dashboard / Developer Console / Agent Workflow 风格。
- 适合现场演示和非技术评委理解。

## 8. 自动生成报告

Streamlit Web UI 支持生成 Markdown 报告，包含：

- 用户需求
- 运行结果
- Product Agent 输出
- Coder Agent 代码
- Tester Agent 检查结果
- stdout / error_log

可强调点：

- 演示结果可以沉淀为文档。
- 便于赛后复盘。
- 未来可扩展为报告中心或历史记录。

## 9. 工程完整度

项目从文档、代码、演示到 UI 都有闭环：

- PRD / TASKS / 架构文档
- Agent 实现
- LangGraph 工作流
- CLI 演示
- Streamlit Web UI
- Figma 协作文档
- 答辩材料

可强调点：

- 不只是原型脚本，而是一个可持续迭代的工程项目。
- 每个阶段都有任务清单记录。

## 10. 现场演示建议

推荐演示路径：

1. 打开 Web UI，展示整体 Dashboard。
2. 选择简单成功案例，快速跑通。
3. 选择翻车修复案例，展示错误反馈闭环。
4. 展示 Markdown 报告。
5. 简短说明 LangGraph 状态机。

核心一句话：

```text
我们不是只让大模型写代码，而是让多个 Agent 组成一条能运行、能发现错误、能自动修复的开发流水线。
```
