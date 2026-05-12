# AI 多智能体自主开发流水线 PRD

## 项目目标

基于国产大模型 DeepSeek，构建一个多智能体协同开发系统，实现从自然语言需求到代码生成、测试、报错分析、自动修复的闭环流程。

## 核心功能

1. Product Agent：拆解用户需求
2. Architect Agent：设计项目结构
3. Coder Agent：生成 Python 代码
4. Tester Agent：生成并运行测试
5. Sentry Agent：分析错误日志
6. 自动修复：将错误反馈给 Coder Agent 重新生成代码
7. CLI 可视化：用不同颜色展示 Agent 协作过程

## 技术栈

- Python
- DeepSeek API
- OpenAI SDK
- pytest
- rich
- typer
- markdown 文档管理

## 演示目标

输入一个需求，系统自动完成：

需求分析 → 代码生成 → 测试失败 → 错误分析 → 自动修复 → 测试通过