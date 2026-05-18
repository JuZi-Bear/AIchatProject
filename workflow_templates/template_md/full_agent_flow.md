# 完整多 Agent 流程

## 适用场景

用于展示平台化多 Agent 协作能力，覆盖需求分析、代码生成、测试、运行、错误分析、插件增强、质量评分和报告生成。

## Agent 执行顺序

1. Product Agent：需求拆解。
2. Coder Agent：代码生成。
3. Tester Agent：测试生成与测试执行。
4. Runner：运行验证。
5. Sentry Agent：错误分析与修复建议。
6. Coder Agent：根据错误分析修复代码。
7. Plugin Executor：执行文档、安全、重构和 UI 插件。
8. Quality Evaluator：质量评分。
9. Report Generator：报告生成。

## 阶段顺序

分析 -> 生成 -> 测试 -> 执行 -> 修复 -> 插件 -> 评分 -> 报告

## 说明

该模板适合展示 v2.0 平台轨的完整能力边界，但当前仍复用现有固定 LangGraph 流程。
