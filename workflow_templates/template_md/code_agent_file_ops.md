# CodeAgent 文件操作流程

## 适用场景

用于在 Vue Workflow Editor 中演示简化版 Code Agent 节点，执行项目文件读取、写入和目录文件列表操作。

## 支持操作

1. read_file：读取项目内指定文件内容。
2. write_file：写入或生成项目内指定文件，自动创建父目录。
3. list_files：列出项目目录中的文件，目录不存在时自动创建。

## 事件输出

每次操作会生成：

1. AGENT_STARTED：操作开始。
2. AGENT_FINISHED：操作完成。
3. AGENT_FAILED：操作失败。

Java Gateway 模式下，这些事件会写入 MySQL `run_event` 表，并通过 SSE 推送给 Vue。

## 说明

该模板不替代完整 Codex，也不改写 LangGraph 主流程，只作为受控文件操作节点和可视化回放基础能力。
