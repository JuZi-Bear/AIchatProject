# 答辩问答准备

## 1. 你们项目解决的核心问题是什么？

答：核心问题是把“AI 生成代码”升级为“AI 自动开发流水线”。系统不仅生成代码，还会拆解需求、检查代码、保存运行、分析错误并自动修复，形成从需求到可运行结果的闭环。

## 2. 为什么要使用多 Agent，而不是一个大模型一次完成？

答：单个大模型一次性完成需求分析、写代码、测试和修复，结果不稳定且难解释。多 Agent 把任务拆成 Product、Coder、Tester、Sentry 四个角色，每个 Agent 目标更清晰，流程更容易控制，也更适合展示和扩展。

## 3. Product Agent 的作用是什么？

答：Product Agent 负责把用户的自然语言需求拆成结构化产品方案，包括功能列表、技术需求和开发步骤。这样可以给后续 Coder Agent 提供更明确的输入。

## 4. Tester Agent 是真的运行测试吗？

答：当前 Tester Agent 负责静态检查，判断代码是否有明显语法问题、逻辑问题和入口调用问题。真正的运行验证由 Code Runner 完成，它会用 subprocess 运行生成的 Python 文件并捕获 stdout、stderr 和 returncode。

## 5. Sentry Agent 为什么叫 Sentry？

答：这里借用了错误监控系统的概念。Sentry Agent 的职责是分析运行失败后的 stderr 错误日志，提取错误原因和修复建议，再反馈给 Coder Agent 进行修复。

## 6. 自动修复是怎么实现的？

答：系统运行生成代码后，如果 returncode 不为 0，就把 stderr、原始代码和产品方案交给 Sentry Agent 分析。之后 Coder Agent 根据错误日志和修复建议重新生成完整代码。这个过程最多重复 3 次。

## 7. 为什么限制最多修复 3 次？

答：限制次数是为了避免无限循环。大模型修复不是百分百可靠，如果连续 3 次仍失败，系统会停止并输出最终错误，方便人工接管。

## 8. LangGraph 在项目中起什么作用？

答：LangGraph 把整个流程抽象成状态机。每个节点负责一个 Agent 或运行步骤，状态在节点之间传递。runner_node 会根据 success 和 retry_count 决定结束还是进入修复分支。

## 9. 你们的 LangGraph 状态里包含哪些内容？

答：主要包含 requirement、product_result、code、tester_result、stdout、error_log、sentry_result、retry_count 和 success。这些字段记录了从用户需求到最终运行结果的完整过程。

## 10. 项目为什么选择 DeepSeek？

答：DeepSeek 是国产大模型，适合体现国产 AI 能力。同时它提供 OpenAI 兼容 API，接入成本低，便于快速构建多 Agent 应用。

## 11. 如果模型生成了 Markdown 代码块怎么办？

答：我们在 `utils/code_runner.py` 中增加了代码清理逻辑，会在保存前移除 ```python 这类 Markdown 代码块围栏，避免写入 Python 文件后产生语法错误。

## 12. 如果生成的代码需要用户 input，会不会卡住？

答：Code Runner 使用 subprocess 运行代码时不会提供人工输入。如果代码调用 input，通常会触发 EOFError。这个错误会被 Sentry Agent 捕获并分析，Coder Agent 会尝试增加 try-except 和默认值，确保代码在非交互环境也能运行结束。

## 13. Web UI 的作用是什么？

答：Web UI 让非技术评委更容易理解系统流程。它展示需求输入、Agent 状态卡片、工作流、stdout、error_log、修复次数和 Markdown 报告，比单纯命令行更适合比赛现场演示。

## 14. 当前项目还有哪些不足？

答：目前主要面向单文件 Python 示例，复杂项目、多文件生成、真实 pytest 测试和前端代码生成还没有完全实现。当前重点是证明多 Agent 自动开发闭环的可行性。

## 15. 未来如何扩展？

答：未来可以增加 Architect Agent 负责项目结构设计，增加 pytest 测试生成，支持多文件项目，接入 Figma 设计稿生成前端页面，并保存历史运行报告，形成更完整的 AI 软件工厂原型。
