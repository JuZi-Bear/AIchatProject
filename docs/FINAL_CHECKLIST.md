# 最终交付检查清单

用于比赛提交前逐项确认项目是否可以稳定演示。

## v2-demo-rc1 验收结论

- [x] 已执行 `.\scripts\final_v2_acceptance.ps1`。
- [x] Python API `http://127.0.0.1:8001/health` 通过。
- [x] Java Gateway `http://127.0.0.1:8088/api/health` 通过。
- [x] 临时 MySQL `127.0.0.1:3307` 监听，Java 平台记录可查询。
- [x] Vue Dashboard、RunConsole、History、Reports、Models、Plugins、Agents、Workflow Templates、Workflow Editor 均返回 HTTP 200。
- [x] CodeAgent smoke 通过，包括文件写入、阻断路径、SSE、RunEvent、Replay 和 JSONL 审计日志。
- [x] Workflow 模板 smoke 通过，包括保存、版本递增、实例化、回放和删除。
- [x] 演示数据脚本通过，生成 Agent 运行、CodeAgent 文件操作和 Workflow 模板回放三类平台记录。
- [x] seed 脚本中的真实 Agent 示例已替换为稳定 hello world 成功样例，当前记录 `success=true`、`qualityScore=100`。
- [x] v2 演示脚本入口、三分钟演示脚本和本地联调文档已更新。

备注：2026-05-21 已将 `scripts/seed_v2_demo_data.ps1` 的 Agent 示例需求替换为 ASCII hello world 成功样例，并让 `start_v2_local.ps1` 优先使用 `.venv\Scripts\python.exe`，避免系统 Python 缺少 `coverage` 导致 pytest 阶段失败。

## 环境检查

- [ ] 确认 Python 版本为 3.11 或兼容版本。
- [ ] 确认当前目录为项目根目录。
- [ ] 确认 `.venv` 虚拟环境已创建。
- [ ] 确认 PowerShell 可以执行本项目脚本。
- [ ] 确认 `reports/`、`runs/`、`output/`、`tests/` 目录存在或可自动创建。

## API Key 检查

- [ ] 确认已根据 `.env.example` 创建 `.env`。
- [ ] 确认 `DEEPSEEK_API_KEY` 已填写，或已启用 `OFFLINE_MODE=true`。
- [ ] 如需演示 Qwen，确认 `QWEN_API_KEY` 已填写。
- [ ] 如需演示 GLM，确认 `GLM_API_KEY` 已填写。
- [ ] 确认 `DEFAULT_MODEL_PROVIDER` 与演示模型一致。

## 依赖安装检查

- [ ] 确认已运行 `install.bat`。
- [ ] 确认 `requirements.txt` 安装成功。
- [ ] 确认 `streamlit`、`langgraph`、`openai`、`pytest`、`coverage` 可导入。
- [ ] 确认 `python -m pytest -q` 不因环境缺失直接失败。

## Docker 检查

- [ ] 确认 Docker Desktop 已启动。
- [ ] 确认 `docker compose up --build` 可以构建镜像。
- [ ] 确认 Web UI 可通过 `http://localhost:8501` 访问。
- [ ] 确认 `reports/`、`runs/`、`output/` 已挂载到宿主机。
- [ ] 确认容器可以读取 `.env` 中的模型配置。

## CLI 演示检查

- [ ] 运行 `python graph_demo.py`。
- [ ] 可以选择简单成功案例。
- [ ] 可以选择翻车修复案例。
- [ ] 可以选择综合案例。
- [ ] 可以选择自定义输入。
- [ ] CLI 结束后打印 `run_id`、状态文件路径和报告路径。

## Web UI 演示检查

- [ ] 运行 `python -m streamlit run webui.py`。
- [ ] 左侧控制栏显示案例、模型、插件、模式和运行按钮。
- [ ] 未勾选人工审批时不会运行生成代码。
- [ ] 勾选人工审批后可以正常执行流程。
- [ ] 工作流节点状态颜色正常显示。
- [ ] Agent 输出 Tabs 可以展开查看。
- [ ] 演示模式只展示关键摘要。
- [ ] 开发模式可以查看完整 state、stdout、stderr。

## 插件系统检查

- [ ] `config/agents.yaml` 可控制插件开关。
- [ ] Web UI 侧边栏 checkbox 可写回插件配置。
- [ ] Doc Agent 输出 `doc_result`。
- [ ] Security Agent 输出 `security_result`。
- [ ] Refactor Agent 输出 `refactor_result`。
- [ ] UI Agent 输出 `ui_result`。
- [ ] `plugin_results` 使用统一结构展示插件结果。

## 模型切换检查

- [ ] Web UI 可以选择 DeepSeek。
- [ ] Web UI 可以选择 Qwen。
- [ ] Web UI 可以选择 GLM。
- [ ] 缺少 API Key 时页面有清晰 warning。
- [ ] 模型信息写入报告和运行历史。
- [ ] 多模型对比模式可以选择 2-3 个模型。

## 自动测试检查

- [ ] Tester Agent 可以生成 pytest 测试代码。
- [ ] 测试代码保存到 `tests/test_generated_code.py`。
- [ ] pytest 运行结果写入 `test_stdout` 和 `test_stderr`。
- [ ] coverage 输出写入 `coverage_stdout`。
- [ ] 覆盖率写入 `coverage_percent`。

## 自动修复检查

- [ ] Runner 失败时进入 Sentry Agent。
- [ ] pytest 失败时也进入 Sentry Agent。
- [ ] Sentry Agent 输出错误摘要和修复建议。
- [ ] Coder Agent 根据错误日志修复代码。
- [ ] 最大修复次数从 `config/settings.yaml` 读取。
- [ ] 修复 3 次后仍失败会停止并输出最终错误。

## 报告生成检查

- [ ] 每次运行生成 Markdown 报告。
- [ ] 报告包含需求、模型、Agent 输出、测试、覆盖率、质量评分和插件结果。
- [ ] 报告包含 `run_id`、运行时间和状态文件路径。
- [ ] Web UI 可以预览最新报告。
- [ ] 模型对比运行生成 `report_compare_{run_id}.md`。

## 运行历史检查

- [ ] 每次运行生成 `runs/{run_id}.json`。
- [ ] 历史状态包含模型信息、审批信息、测试结果、插件结果和报告路径。
- [ ] Web UI 可以选择历史 run_id。
- [ ] Web UI 可以加载历史结果到当前展示区。
- [ ] 历史生成代码和错误日志可以查看。

## 常见问题检查

- [ ] API Key 缺失时可以切换离线模式。
- [ ] 网络不可用时可以使用预置演示响应。
- [ ] 依赖安装失败时有操作指南可参考。
- [ ] Docker 启动失败时有排查步骤。
- [ ] 端口 8501 被占用时知道如何更换或释放端口。
- [ ] 生成代码包含危险操作时会被安全检查拦截。
