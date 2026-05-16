# v1.0 最终验收清单

本文用于 v1.0 比赛演示版最终验收。验收结论以比赛现场稳定演示为优先级。

## 启动验收

- [ ] `install.bat` 是否可用。
- [ ] `start_demo.bat` 是否可用。
- [ ] `python graph_demo.py` 是否可用。
- [ ] `python -m streamlit run webui.py` 是否可用。
- [ ] `docker compose up --build` 是否可用。

## 核心流程验收

- [ ] 简单成功案例是否能完成运行。
- [ ] 翻车自动修复案例是否能触发 Sentry Agent 和 Coder Agent 修复。
- [ ] 综合案例是否能生成代码、测试、评分和报告。
- [ ] 自定义需求案例是否能正常输入并运行。

## Agent 验收

- [ ] Product Agent 是否能输出需求拆解。
- [ ] Coder Agent 是否能生成代码。
- [ ] Coder Agent 是否能在失败后根据错误日志修复代码。
- [ ] Tester Agent 是否能生成 pytest 测试。
- [ ] Tester Agent 是否能运行 pytest + coverage。
- [ ] Sentry Agent 是否能分析错误摘要和修复建议。
- [ ] Plugins 是否能按配置执行。
- [ ] Quality Evaluator 是否能生成质量评分。
- [ ] Report Generator 是否能生成 Markdown 报告。

## UI 验收

- [ ] 页面展示顺序是否清晰。
- [ ] 首屏是否可见核心结果。
- [ ] 工作流视觉引导是否正常。
- [ ] AI 工作流时间轴是否显示节点图标、状态和摘要。
- [ ] 高光时刻是否显示正常。
- [ ] 结果快速导航是否正常。
- [ ] 空白 box 是否明显减少。
- [ ] 演示模式是否正常。
- [ ] 开发模式是否正常。
- [ ] 长内容是否默认折叠。
- [ ] Raw State 是否只在开发模式查看。

## 工程验收

- [ ] `run_summary` 是否正常生成。
- [ ] `ui_view_model` 是否正常生成。
- [ ] `run_service` 是否正常调用。
- [ ] `reports/` 是否正常生成 Markdown 报告。
- [ ] `runs/` 是否正常保存历史记录。
- [ ] 插件配置是否正常读取和写回。
- [ ] 多模型配置是否正常读取。
- [ ] `.env.example` 是否包含必要环境变量。
- [ ] Docker 配置是否正常。
- [ ] 离线模式是否可用于兜底演示。

## 文档验收

- [ ] README 是否覆盖项目简介、亮点、架构、启动方式、Web UI、CLI、插件、多模型、测试修复、UI/UX、v2.0 和常见问题。
- [ ] `docs/DEMO_FLOW.md` 是否能指导比赛现场演示。
- [ ] `docs/DEFENSE_QA.md` 是否至少包含 25 个问答。
- [ ] `docs/V1_RELEASE_NOTES.md` 是否完成。
- [ ] `docs/V1_FREEZE_RULES.md` 是否完成。
- [ ] `docs/V2_ARCHITECTURE_PLAN.md` 是否完成。

## 最终验收结论

- [ ] v1.0 可以进入比赛演示冻结状态。
- [ ] 后续只允许 Bug 修复、文案调整、文档优化、启动脚本修复和 UI 小问题修复。
