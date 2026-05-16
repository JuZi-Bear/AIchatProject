# 开发任务清单

## 当前版本状态

- [x] v1.0 比赛交付版功能冻结
- [x] 暂停新增 Vue、Java、C++ 等新架构模块
- [x] 不再改变现有核心运行逻辑
- [x] 当前阶段只做交付检查、答辩材料、演示流程和风险预案收口
- [x] 当前阶段只允许 Bug 修复、提示优化、文档完善和启动稳定性改善

## v1.0 稳定性测试

- [x] 新建 docs/STABILITY_TEST.md
- [x] 新建 docs/BUG_FIX_LOG.md
- [x] 环境测试：Python 3.11、虚拟环境、依赖、.env 和 API Key 提示
- [x] CLI 测试：graph_demo 菜单、简单案例、翻车修复、报告生成和人工审批
- [x] Web UI 测试：Streamlit 启动、案例、插件、模型、结果、报告、历史和模式切换
- [x] Docker 测试：docker compose 配置、端口、env_file 和目录挂载
- [x] 核心功能测试：Product、Coder、Tester、Runner、Sentry、Quality、run_summary 和插件报告
- [x] 文档检查：README、FINAL_CHECKLIST、DEMO_FLOW、BUG_FIX_LOG 和 STABILITY_TEST
- [x] 演示流程检查：Web UI 翻车修复案例、人工审批、自动修复、质量评分和报告展示
- [x] 使用 DeepSeek `deepseek-v4-pro` 做在线 smoke test
- [x] 修复 start_demo.bat 依赖缺失提示
- [x] 修复 install.bat Python 3.11 推荐提示
- [x] 修复自动生成测试/报告/运行历史误入 Git 的风险
- [x] 修复 DEEPSEEK_MODEL / DEEPSEEK_BASE_URL 环境变量覆盖模型配置的问题

## UI/UX 优化与架构重构同步计划

- [x] 第一阶段：新增 docs/ui_workflow/ UI 优化工作流文档
- [x] 第二阶段：统一 UI 状态数据层
- [x] 新增 build_ui_view_model(state, run_summary=None)
- [x] 新增列表结构 build_workflow_status(state)
- [x] 新增 build_result_index(state, run_summary=None)
- [x] 保留 build_workflow_status_map(state) 兼容当前 Streamlit 页面
- [x] webui.py 开始优先读取 UI ViewModel 展示摘要、工作流、插件和报告数据
- [x] 更新 UI_COMPONENTS_SPEC.md 说明 ViewModel、workflow_steps 和 summary_cards
- [x] 新增 docs/CODEX_UI_WORKFLOW.md 标记第二阶段进度
- [x] 第三阶段：基于 UI ViewModel 重排 Web UI 页面结构
- [x] Header 展示项目名称、当前模型、运行状态和 run_id
- [x] 主区域顶部使用紧凑 summary_cards 展示 success、retry_count、test_success、coverage_percent、quality_score、security_status
- [x] AI 工作流进度区按 workflow_steps 的 order 展示节点状态和摘要
- [x] 最终结果总览区集中展示成功状态、修复次数、测试、覆盖率、质量评分、报告路径和错误摘要
- [x] Agent 输出详情 Tabs 调整为 Product、Coder、Tester、Sentry、Plugins、Report、Raw State
- [x] 新增结果索引区，固定提供最终代码、测试结果、错误摘要、插件结果和报告入口
- [x] 演示模式隐藏完整日志和 Raw State，只保留摘要、工作流、高光、最终结果和报告入口
- [x] 开发模式保留完整代码、stdout、stderr、plugin_results 和 state
- [x] 更新 UI_LAYOUT_SPEC 和 UI_ACCEPTANCE_CHECKLIST
- [x] 第四阶段：抽离接口适配层
- [x] 新建 services/ 目录
- [x] 新建 services/run_service.py
- [x] 实现 create_run(request)，统一返回 state、run_summary、ui_view_model
- [x] 实现 get_run(run_id)、list_run_history()、get_latest_report()
- [x] 实现 get_available_models()、get_available_plugins()
- [x] webui.py 通过 create_run(request) 执行工作流，不再直接调用 LangGraph 核心入口
- [x] webui.py 历史记录、模型列表、插件信息开始使用服务层数据
- [x] 新建 docs/API_CONTRACT.md 记录未来 FastAPI / Vue / Java 接口结构
- [x] 更新 TECH_STACK 和 CODEX_UI_WORKFLOW
- [x] 第五阶段：增强 AI 工作流视觉引导和轻量动画感
- [x] 新增 render_workflow_timeline(ui_view_model)
- [x] Timeline 只接收 ui_view_model，不直接解析原始 state
- [x] Timeline 展示 Requirement、Product、Coder、Tester、Approval、Runner、Sentry、Plugins、Quality、Report
- [x] 每个节点展示中文状态、简短摘要和状态图标
- [x] 使用 st.progress 展示整体进度
- [x] 使用 st.status / st.info 展示当前执行步骤
- [x] 自动修复高光时刻改为读取 ui_view_model
- [x] 更新 UI_ANIMATION_SPEC
- [x] 第六阶段：增加结果快速导航与报告聚合
- [x] 新增 render_result_overview(ui_view_model)
- [x] 最终结果总览展示成功状态、run_id、修复次数、测试结果、覆盖率、质量评分、安全状态和报告路径
- [x] 新增 render_result_index(ui_view_model)
- [x] 结果索引提供最终代码、pytest、错误摘要、自动修复、插件结果、运行报告和历史记录入口
- [x] 结果索引用 Tabs + expander 实现快速查看
- [x] Agent 输出详情继续统一放入 Product、Coder、Tester、Sentry、Plugins、Report、Raw State Tabs
- [x] 完整代码、stdout、stderr、full state 和 report markdown 默认折叠
- [x] 更新 UI_INTERACTION_SPEC 和 UI_ACCEPTANCE_CHECKLIST
- [x] 第七阶段：减少空白 box 并规范 UI 组件渲染
- [x] 新增 render_header(ui_view_model)
- [x] 规范 render_summary_cards(ui_view_model)
- [x] 保留 render_workflow_timeline(ui_view_model) 作为主工作流展示
- [x] 规范 render_result_overview(ui_view_model)
- [x] 规范 render_agent_tabs(ui_view_model)
- [x] 新增 render_plugin_results(ui_view_model)
- [x] 新增 render_report_section(ui_view_model)
- [x] 新增 render_history_section(ui_view_model)
- [x] 短字段使用 columns 横向排列
- [x] 长内容统一放入 expander
- [x] 统一卡片 padding、margin 和高度，减少大面积空白
- [x] 更新 UI_COMPONENTS_SPEC 和 UI_ACCEPTANCE_CHECKLIST
- [x] 第八阶段：生成 v2.0 多技术栈架构预留文档
- [x] 新建 docs/V2_ARCHITECTURE_PLAN.md
- [x] 记录 v1.0 当前架构和 v2.0 目标架构
- [x] 规划 frontend-vue、backend-java、agent-engine-python、runner-sandbox-cpp 服务拆分
- [x] 记录 Vue → Java API → Python Agent Engine → LangGraph → Runner Sandbox → ui_view_model 数据流
- [x] 引用 docs/API_CONTRACT.md 作为接口契约
- [x] 说明当前保留 Streamlit 的原因
- [x] 规划 FastAPI、Vue3 + TS、Java Spring Boot、C++ Runner Sandbox、Docker Compose 升级路线
- [x] 更新 TECH_STACK、README 和 DEFENSE_QA
- [x] v1.0 最终验收
- [x] 新建 docs/V1_RELEASE_NOTES.md
- [x] 新建 docs/V1_FINAL_ACCEPTANCE.md
- [x] 新建 docs/V1_FREEZE_RULES.md
- [x] README 检查并补充 UI/UX 优化说明和 v2.0 架构规划
- [x] DEMO_FLOW 检查并同步当前 Web UI 展示流程
- [x] DEFENSE_QA 检查，确认包含 25+ 个评委问答
- [x] v1.0 版本冻结
- [x] 比赛演示准备
- [x] 答辩材料确认

## 第一阶段：基础 Agent

- [x] 接入 DeepSeek API
- [x] 实现 Product Agent
- [x] 实现 Coder Agent
- [x] 实现 main.py 串联调用

## 第二阶段：自动测试

- [x] 实现 Tester Agent 静态检查
- [x] 检查语法问题、逻辑问题和入口调用
- [x] 自动保存 Coder Agent 生成的代码
- [x] 使用 subprocess 运行代码
- [x] 捕获 stdout 和 stderr
- [x] 判断运行是否成功

## 第三阶段：自动修复

- [x] 实现 Sentry Agent
- [x] 将错误日志反馈给 Coder Agent
- [x] 最多自动修复 3 次
- [x] 测试通过后输出成功结果

## 第四阶段：演示优化

- [x] 使用 rich 增加彩色输出
- [x] 增加 Agent 状态展示
- [x] 准备翻车案例
- [x] 生成 README

## 第六阶段：比赛演示案例

- [x] 生成 docs/DEMO_SCRIPT.md
- [x] 准备 3 个演示需求
- [x] 新增 demo_cases.py
- [x] main.py 支持选择演示案例
- [x] 更新 README

## LangGraph 重构

- [x] 搭建基础 graph.py
- [x] 定义 AgentState
- [x] 创建 Product/Coder/Tester/Sentry 空节点
- [x] 连接 START → product_node → coder_node → tester_node → END
- [x] 接入真实 Agent 调用
- [x] 接入代码保存与运行节点
- [x] 接入自动修复循环
- [x] 新增 graph_demo.py 演示入口
- [x] graph_demo.py 支持演示案例菜单
- [x] 更新 LangGraph 演示文档
- [ ] 替换 main.py 现有流程

## 第八阶段：Figma 协同文档

- [x] 整理 figma/design_link.md
- [x] 新增 docs/UI_SPEC.md
- [x] 设计首页说明
- [x] 设计 Agent 工作流页说明
- [x] 设计运行日志页说明
- [x] 设计报告页说明
- [x] 更新 README Figma 协作说明

## 第九阶段：Streamlit Web UI

- [x] 新建 webui.py
- [x] 实现项目标题、需求输入框、演示案例选择和开始运行按钮
- [x] 调用 run_graph_demo(requirement)
- [x] 展示 Product/Coder/Tester/Sentry 分区
- [x] 展示 retry_count、success、stdout、error_log
- [x] 支持查看生成的 Markdown 报告
- [x] 更新 README 运行方式

## 第十阶段：Web UI 视觉优化与 Figma 对齐

- [x] 根据 docs/UI_SPEC.md 优化 webui.py
- [x] 增加侧边栏项目简介、技术栈、演示案例和运行入口
- [x] 增加 Agent 状态卡片
- [x] 增加 Agent Workflow 流程图区域
- [x] 增加 success、retry_count、stdout、error_log 结果面板
- [x] 使用自定义 CSS 优化页面
- [x] README 增加 Web UI 截图占位说明

## Web UI 展示布局与交互优化

- [x] 页面调整为左侧控制栏 + 右侧主展示区
- [x] 左侧栏支持演示案例、自定义需求和最大修复次数设置
- [x] 左侧栏显示在线 / 离线模式
- [x] 左侧栏支持自定义 AI 插件开关
- [x] 增加运行前确认 checkbox
- [x] 增加清空结果按钮
- [x] 右侧顶部增加当前模型、运行状态、success、retry_count、enabled_plugins 摘要卡片
- [x] 增加 Requirement、Product、Coder、Tester、Runner、Sentry、Plugins、Report 工作流状态
- [x] 工作流状态支持 Waiting、Running、Done、Failed、Repairing
- [x] Agent 输出改为 Tabs 展示
- [x] 代码内容使用 st.code 展示
- [x] stdout 和 stderr 使用折叠面板展示
- [x] 插件结果单独展示 doc_result、security_result、refactor_result、ui_result
- [x] 增加演示模式 / 开发模式切换
- [x] 使用 session_state 保存 requirement、selected_case、result_state、run_status、enabled_plugins、latest_report
- [x] 未确认运行权限时点击开始运行只显示 warning，不执行代码
- [x] 清空结果按钮重置 result_state、run_status、latest_report、stdout、stderr
- [x] 增加最新 Markdown 报告查看区域
- [x] docs/UI_SPEC.md 更新 Figma 布局关键词
- [x] README 和操作指南更新 Web UI 使用说明

## Web UI 演示模式专项优化

- [x] 演示模式隐藏完整 prompt、完整 state、过长 stderr 和冗长分析
- [x] 演示模式只展示用户需求、当前 Agent、错误状态、修复摘要和最终结果
- [x] 新增自动修复高光时刻区域
- [x] 自动修复高光展示第一次失败、错误摘要、Sentry 分析、Coder 修复和再次运行结果
- [x] 未触发修复时提示一次运行成功
- [x] 新增比赛讲解提示 expander
- [x] 新增结果总结卡片
- [x] 结果总结展示成功/失败、修复次数、生成代码文件、安全检查、文档生成和报告文件名
- [x] summarize_error 优先提取 Error、Exception、Traceback、SyntaxError、IndexError、ValueError
- [x] 工作流状态文案转换为等待中、运行中、已完成、失败、修复中
- [x] 开发模式继续保留完整 state、stdout、stderr、插件结果和代码
- [x] 更新 docs/UI_SPEC.md、docs/DEMO_SCRIPT.md、docs/OPERATION_GUIDE.md、README.md

## LangGraph 状态持久化与运行历史

- [x] 新建 runs/ 目录保存运行状态
- [x] 新建 utils/run_store.py
- [x] 实现 create_run_id()
- [x] 实现 save_run_state(run_id, state)
- [x] 实现 load_run_state(run_id)
- [x] 实现 list_runs()
- [x] 实现 get_latest_run()
- [x] graph_demo.py 运行结束后保存 runs/{run_id}.json
- [x] webui.py 运行结束后保存 runs/{run_id}.json
- [x] state 写入 run_id、run_time、enabled_plugins、state_path 和 report_path
- [x] 报告中加入 run_id、运行时间和状态文件路径
- [x] Web UI 增加历史运行记录区域
- [x] Web UI 支持查看历史需求、Agent 输出、修复次数、成功状态和报告路径
- [x] Web UI 支持查看历史生成代码和历史错误日志
- [x] graph_demo.py 运行结束后打印 run_id、状态保存路径和报告路径
- [x] README 增加运行历史记录说明
- [x] 操作指南增加历史运行记录查看步骤
- [x] docker-compose.yml 挂载 runs/ 目录

## Human-in-the-loop 人工审批节点

- [x] AgentState 新增 approved、approval_message、require_human_approval
- [x] LangGraph 在 Tester Agent 和 Runner 之间增加 approval_node
- [x] approval_node 支持未启用审批时自动通过
- [x] approval_node 支持 CLI input() 人工确认
- [x] approval_node 支持 Web UI checkbox 审批结果
- [x] 审批拒绝时不运行 generated_code.py
- [x] 审批拒绝时写入 error_log 并进入 Plugins / Report
- [x] graph_demo.py 增加是否启用人工审批选项
- [x] Web UI 将运行确认 checkbox 与 approved 字段打通
- [x] Web UI 增加 Approval Node 工作流状态
- [x] 报告增加人工审批字段
- [x] runs/{run_id}.json 保存人工审批字段
- [x] README、操作指南、UI_SPEC、DEFENSE_QA 更新人工审批说明

## 第十一阶段：答辩材料与评分点包装

- [x] 新增 docs/PRESENTATION_OUTLINE.md
- [x] 新增 docs/SCORE_POINTS.md
- [x] 新增 docs/DEFENSE_QA.md
- [x] 准备 20+ 个评委问答
- [x] README 增加答辩材料说明

## 第十二阶段：一键启动与演示脚本精修

- [x] 新建 start_demo.bat
- [x] start_demo.bat 支持 CLI 和 Web UI 启动
- [x] 新增 docs/OPERATION_GUIDE.md
- [x] 优化 docs/DEMO_SCRIPT.md
- [x] 增加 5 分钟比赛演示台词
- [x] README 增加一键启动说明

## 稳定性兜底与安全配置

- [x] 新增 .env.example
- [x] 使用 python-dotenv 读取 DEEPSEEK_API_KEY 和 DEEPSEEK_BASE_URL
- [x] agents.py 移除 API Key 硬编码
- [x] 新增 offline_demo.py 离线演示响应
- [x] API 调用失败时自动使用预置演示响应
- [x] 增加代码执行安全检查
- [x] 禁止 os.remove、shutil.rmtree、subprocess、eval、exec
- [x] run_code 支持 timeout 配置
- [x] README 和操作指南更新配置说明

## 操作手册与跨设备部署

- [x] 新增 docs/USER_MANUAL.md
- [x] 说明新设备部署流程
- [x] 说明虚拟环境和依赖安装
- [x] 说明 .env 和离线模式配置
- [x] 说明 CLI 与 Web UI 启动方式
- [x] 说明局域网访问 Web UI
- [x] 增加部署验收清单和常见问题
- [x] README 增加操作手册入口

## 工程化交付基础包

- [x] 新增 requirements.txt
- [x] requirements.txt 写入 openai、langchain、langgraph、rich、streamlit、python-dotenv、pytest、pyyaml
- [x] 更新 .env.example 标准配置模板
- [x] agents.py 使用 python-dotenv 读取 .env
- [x] agents.py 缺少 API Key 时给出清晰提示
- [x] 新增 install.bat 自动升级 pip 并安装依赖
- [x] 修复 start_demo.bat 使用 python graph_demo.py
- [x] 修复 start_demo.bat 使用 python -m streamlit run webui.py
- [x] 更新 README 安装、配置和启动说明
- [x] 更新 docs/OPERATION_GUIDE.md 新电脑部署和常见错误处理

## 自定义 AI 进程模块 / 插件系统

- [x] 新建 plugins/ 目录和 plugins/__init__.py
- [x] 新建 plugins/base_plugin.py 并定义 BasePluginAgent
- [x] 新建 Doc Agent 插件并写入 doc_result
- [x] 新建 Security Agent 插件并写入 security_result
- [x] 新建 config/agents.yaml 控制插件启用状态
- [x] 新建 plugin_loader.py 读取配置并顺序执行插件
- [x] graph.py 增加 plugins_node
- [x] graph_demo.py 输出 doc_result 和 security_result
- [x] webui.py 增加自定义 AI 模块展示区域
- [x] README 和操作指南更新插件系统说明

## Web UI 插件配置能力

- [x] 侧边栏增加自定义 AI 模块配置区域
- [x] Web UI 自动读取 config/agents.yaml
- [x] 展示 Doc Agent 和 Security Agent 的名称、说明和启用状态
- [x] 使用 checkbox 控制插件启用状态
- [x] checkbox 修改后自动写回 config/agents.yaml
- [x] 运行时按最新配置执行插件
- [x] 运行结果区域增加插件执行结果面板
- [x] 展示 doc_result 和 security_result
- [x] 插件未启用时显示“该插件未启用”
- [x] README 增加 Web UI 插件配置说明
- [x] 操作指南增加插件配置操作步骤

## Refactor Agent 代码重构插件

- [x] 新建 plugins/refactor_agent.py
- [x] 插件名设置为 Refactor Agent
- [x] 分析最终代码结构、重复代码、函数命名和可读性
- [x] 输出重构建议和可选优化代码片段
- [x] 将结果写入 state["refactor_result"]
- [x] config/agents.yaml 增加 refactor_agent 开关
- [x] plugin_loader.py 支持加载 refactor_agent
- [x] graph_demo.py 输出 refactor_result
- [x] webui.py 插件配置区增加 Refactor Agent
- [x] Web UI 和 Markdown 报告展示 Refactor Agent 结果
- [x] README 和操作指南增加 Refactor Agent 说明

## 自定义插件开发模板

- [x] 新建 plugins/plugin_template.py
- [x] 模板类继承 BasePluginAgent
- [x] 模板包含 name、description、enabled 和 run(state)
- [x] 模板注释说明如何读取 requirement 和 code
- [x] 模板注释说明如何调用大模型和写回 state
- [x] 新建 docs/PLUGIN_GUIDE.md
- [x] PLUGIN_GUIDE.md 说明插件系统、目录结构和开发流程
- [x] 新增 plugins/ui_agent.py
- [x] UI Agent 输出页面布局建议、核心组件和交互说明
- [x] UI Agent 将结果写入 state["ui_result"]
- [x] config/agents.yaml 增加 ui_agent 开关
- [x] plugin_loader.py 支持加载 ui_agent
- [x] graph_demo.py 输出 ui_result
- [x] webui.py 插件配置区和结果区增加 UI Agent
- [x] Markdown 报告增加 UI Agent 结果
- [x] README 和操作指南更新插件模板说明

## Docker 部署与环境固定

- [x] 新建 Dockerfile
- [x] 新建 docker-compose.yml
- [x] Docker 镜像基于 python:3.11-slim
- [x] Docker 构建时安装 requirements.txt 依赖
- [x] 默认启动 Web UI
- [x] Web UI 绑定 0.0.0.0:8501
- [x] 支持通过 .env 传入 DeepSeek 配置
- [x] docker-compose.yml 服务名设置为 ai-agent-pipeline
- [x] docker-compose.yml 挂载 reports/ 和 output/
- [x] 新增 .dockerignore 避免打包本地敏感文件
- [x] README 增加 Docker 启动方式
- [x] 操作指南增加 Docker 部署说明
- [x] 保持 Windows 本地启动方式不变

## pytest 自动测试与测试驱动修复

- [x] Tester Agent 支持 `tester_agent(requirement, code)` 生成 pytest 测试代码
- [x] 保留 `tester_agent(code)` 兼容旧版 main.py 静态检查流程
- [x] 新增 utils/test_runner.py
- [x] 实现 save_test_code(test_code)
- [x] 实现 run_tests() 并捕获 stdout、stderr、returncode
- [x] AgentState 新增 test_code、test_stdout、test_stderr、test_success
- [x] tester_node 自动保存测试代码并运行 pytest
- [x] 成功判断同时检查 Runner success 和 pytest test_success
- [x] pytest 失败时将测试代码和测试日志传给 Sentry Agent
- [x] Coder Agent 修复模式接收 pytest 失败信息并要求修复业务代码
- [x] Markdown 报告增加 pytest 测试代码和测试结果
- [x] Web UI 增加 pytest 测试结果展示区域
- [x] graph_demo.py 输出 test_success、test_stdout 和 test_stderr
- [x] DEMO_SCRIPT 增加测试驱动修复案例
- [x] README、操作指南、UI_SPEC、DEFENSE_QA 更新自动测试说明

## 测试覆盖率与代码质量评分

- [x] requirements.txt 增加 coverage
- [x] utils/test_runner.py 新增 run_tests_with_coverage()
- [x] 使用 coverage run -m pytest 执行测试
- [x] 使用 coverage report 输出覆盖率报告
- [x] 从 TOTAL 行解析 coverage_percent
- [x] AgentState 新增 coverage_stdout、coverage_percent、quality_score、quality_summary
- [x] 新增 quality_evaluator.py
- [x] 实现 evaluate_quality(state)
- [x] 评分规则覆盖 pytest、运行成功、覆盖率、安全检查和自动修复次数
- [x] LangGraph 增加 quality_node
- [x] 流程调整为 Plugins → Quality → Report
- [x] Markdown 报告增加 coverage_percent、quality_score、quality_summary 和安全检查结果
- [x] Web UI 增加质量评分区域
- [x] 演示模式展示大号分数卡片、覆盖率、测试状态和安全状态
- [x] 开发模式展示 coverage_stdout、完整评分依据和完整 state
- [x] graph_demo.py 输出 coverage_percent、quality_score、quality_summary
- [x] README、UI_SPEC、操作指南、DEFENSE_QA 更新质量评分说明

## 多模型切换模块

- [x] 新建 config/models.yaml
- [x] 配置 DeepSeek、Qwen 和 GLM 模型信息
- [x] .env.example 增加 QWEN_API_KEY、GLM_API_KEY 和 DEFAULT_MODEL_PROVIDER
- [x] 新建 model_manager.py
- [x] 实现 load_models_config()
- [x] 实现 get_available_models()
- [x] 实现 get_default_model()
- [x] 实现 get_llm_client(provider)
- [x] 实现 get_current_model_info(provider)
- [x] agents.py 改为通过 model_manager 获取 OpenAI 兼容 client
- [x] Agent 函数支持 provider 参数
- [x] graph.py 在 AgentState 中保存 model_provider、model_name、model_base_url
- [x] LangGraph 节点按 state["model_provider"] 调用模型
- [x] graph_demo.py 增加模型选择菜单
- [x] Web UI 侧边栏增加模型选择区域
- [x] Web UI 显示所选模型名称和 API Key 缺失 warning
- [x] 报告增加模型服务商、模型名称和 base_url
- [x] 运行历史状态保存模型信息
- [x] docker-compose.yml 支持多模型环境变量
- [x] README、操作指南、UI_SPEC、DEFENSE_QA 更新多模型说明

## 模型效果对比模块

- [x] 新增 utils/model_comparator.py
- [x] 支持接收多份 state 数据生成对比行
- [x] 支持生成 Markdown 对比表格
- [x] 支持写入 reports/report_compare_{run_id}.md
- [x] graph_demo.py 增加单模型运行 / 多模型对比运行选项
- [x] graph_demo.py 支持选择 2-3 个模型运行
- [x] 每个模型独立执行完整 Agent 流程
- [x] 每个模型独立保存 runs/{run_id}_modelN.json
- [x] 每个模型独立生成 Markdown 报告
- [x] Web UI 侧边栏增加模型对比模式
- [x] Web UI 支持选择 2-3 个模型
- [x] Web UI 增加“模型对比”Tab
- [x] 对比表格展示成功状态、失败次数、修复次数、pytest、覆盖率、质量评分和插件摘要
- [x] 支持折叠查看每个模型 stdout、stderr 和插件详细输出
- [x] README、UI_SPEC、操作指南、DEFENSE_QA 更新模型对比说明

## Web UI 美化与高亮展示

- [x] Agent 工作流节点按 Waiting、Running、Done、Failed、Repairing 使用不同颜色
- [x] 每个工作流节点显示 retry_count
- [x] 自动修复相关节点在 retry_count > 0 时使用黄色边框高亮
- [x] 最终成功的 Report 节点使用绿色加粗样式
- [x] 模型对比表高亮成功模型、最少修复次数、最高覆盖率和最高质量评分
- [x] 插件执行结果按通过、警告、风险、未启用使用绿色、黄色、红色、灰色展示
- [x] 报告区域使用成功 / 失败大卡片、Markdown 渲染、代码高亮和折叠日志
- [x] 演示模式继续只显示关键信息，开发模式保留完整 state、stdout、stderr
- [x] README、UI_SPEC、操作指南更新高亮说明

## 功能优化和框架优化第一阶段

- [x] 新建 core/ 目录
- [x] 新建 core/state.py 并独立 AgentState
- [x] 新建 core/workflow.py 承载 LangGraph 构建和运行逻辑
- [x] 保留 graph.py 作为兼容入口
- [x] 新建 core/quality_evaluator.py
- [x] 保留 quality_evaluator.py 作为兼容入口
- [x] 新建 config/settings.yaml
- [x] 新建 config/config_loader.py
- [x] 最大修复次数从 config/settings.yaml 读取
- [x] Web UI 默认最大修复次数、默认模型、人工审批和演示模式从配置读取
- [x] graph_demo.py 默认最大修复次数、默认模型和人工审批从配置读取
- [x] README 和操作指南补充模块化结构说明

## 统一错误处理与错误摘要

- [x] 新建 utils/error_utils.py
- [x] 实现 summarize_error(error_log)
- [x] 实现 format_error_for_display(error_log, demo_mode=True)
- [x] 实现 is_retryable_error(error_log)
- [x] Web UI 错误展示统一调用 error_utils
- [x] graph_demo.py 错误摘要统一调用 error_utils
- [x] report_generator.py 错误摘要统一调用 error_utils
- [x] 演示模式只显示错误摘要
- [x] 开发模式显示完整错误
- [x] README 和操作指南更新错误处理说明

## 统一运行结果摘要 run_summary

- [x] 新增 utils/summary_builder.py
- [x] 实现 build_run_summary(state)
- [x] 输出 success、retry_count、test_success、coverage_percent、quality_score
- [x] 输出 security_status、enabled_plugins、model_provider、report_path
- [x] graph_demo.py 使用 run_summary 展示核心结果
- [x] webui.py 使用 run_summary 展示核心结果
- [x] report_generator.py 使用 run_summary 生成 Markdown 摘要
- [x] 避免核心结果字段在多个文件中重复解析 state
- [x] README 和操作指南更新 run_summary 说明

## 插件系统返回结构规范化

- [x] 修改 BasePluginAgent，提供统一 build_result() 和 normalize_result()
- [x] 插件 run(state) 返回 plugin_name、status、summary、detail
- [x] status 统一为 success / warning / failed / disabled
- [x] plugin_loader.py 统一写入 state["plugin_results"]
- [x] 插件关闭时写入 disabled 结果
- [x] 插件异常时写入 failed 结果
- [x] 保留 doc_result、security_result、refactor_result、ui_result 兼容旧逻辑
- [x] Web UI 插件展示优先读取 plugin_results
- [x] Markdown 报告统一展示 plugin_results
- [x] docs/PLUGIN_GUIDE.md 更新插件开发规范

## 最终交付检查

- [x] 新建 docs/FINAL_CHECKLIST.md
- [x] FINAL_CHECKLIST 覆盖环境、API Key、依赖、Docker、CLI、Web UI、插件、模型、测试、修复、报告、历史和常见问题检查
- [x] 新建 docs/DELIVERY_STRUCTURE.md
- [x] DELIVERY_STRUCTURE 说明 core、agents、plugins、utils、config、docs、reports、runs、output、tests 和部署文件作用
- [x] 优化 README.md 为比赛提交版结构
- [x] README 覆盖项目简介、亮点、架构、功能、快速启动、本地运行、Docker、Web UI、CLI、插件、多模型、测试评分、自动修复、目录结构和常见问题
- [x] 优化 docs/PRESENTATION_OUTLINE.md
- [x] PRESENTATION_OUTLINE 按比赛答辩顺序组织背景、痛点、方案、架构、技术路线、Agent 流程、LangGraph、测试修复、插件、多模型、Web UI、Docker、创新点和展望
- [x] 优化 docs/DEFENSE_QA.md
- [x] DEFENSE_QA 准备 20+ 个评委可能提问和简洁回答
- [x] 新建 docs/DEMO_FLOW.md
- [x] DEMO_FLOW 写清楚比赛现场从打开 Web UI 到展示质量评分和报告的完整流程
- [x] 新建 docs/INNOVATION_POINTS.md
- [x] INNOVATION_POINTS 总结国产大模型、多 Agent、LangGraph、测试驱动修复、插件、多模型对比、质量评分、人工审批、Docker 和 Web UI 创新点
- [x] 新建 docs/RISK_AND_SOLUTION.md
- [x] RISK_AND_SOLUTION 说明 API Key、网络、模型、代码安全、测试、Docker、依赖和 Python 版本风险处理
- [x] 新建 docs/TECH_STACK.md
- [x] TECH_STACK 整理 Python 3.11、DeepSeek/Qwen/GLM、OpenAI SDK、LangGraph、Streamlit、Rich、pytest、coverage、Docker、PyYAML、python-dotenv 和 Markdown 报告作用
