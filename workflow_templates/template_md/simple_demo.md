# 简单演示流程

## 适用场景

用于快速展示从自然语言需求到代码生成、测试、质量评分和报告生成的主线能力。

## Agent 执行顺序

1. Product Agent：拆解用户需求。
2. Coder Agent：生成业务代码。
3. Tester Agent：生成并运行测试。
4. Runner：执行代码验证。
5. Quality Evaluator：汇总覆盖率和质量评分。
6. Report Generator：生成 Markdown 报告。

## 阶段顺序

分析 -> 生成 -> 测试 -> 执行 -> 评分 -> 报告

## 说明

该模板适合比赛现场的快速成功案例，不强调自动修复链路。
