# 开发任务清单

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

## 第十一阶段：答辩材料与评分点包装

- [x] 新增 docs/PRESENTATION_OUTLINE.md
- [x] 新增 docs/SCORE_POINTS.md
- [x] 新增 docs/DEFENSE_QA.md
- [x] 准备 15 个评委问答
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
