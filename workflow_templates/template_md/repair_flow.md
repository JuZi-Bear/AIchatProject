# 自动修复重点流程

## 适用场景

用于突出自动测试失败、Sentry Agent 错误分析、Coder Agent 修复和再次验证的闭环能力。

## Agent 执行顺序

1. Product Agent：分析需求和验收目标。
2. Coder Agent：生成初版代码。
3. Tester Agent：生成测试并触发失败。
4. Runner：执行验证。
5. Sentry Agent：分析错误摘要。
6. Coder Agent：执行自动修复。
7. Tester Agent：重新运行测试。
8. Runner：再次验证。
9. Quality Evaluator：评分。
10. Report Generator：生成报告。

## 阶段顺序

分析 -> 生成 -> 测试 -> 执行 -> 修复 -> 再测试 -> 再执行 -> 评分 -> 报告

## 说明

该模板适合比赛答辩中的高光片段，用来解释“从失败到自愈”的工作流价值。
