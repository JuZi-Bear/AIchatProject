# AI Multi-Agent Pipeline

基于 DeepSeek API 的多智能体自动开发流水线演示项目。

## 当前流程

用户输入需求后，程序会依次执行：

1. Product Agent：拆解需求
2. Coder Agent：生成 Python 代码
3. Tester Agent：静态检查代码
4. Code Runner：保存并运行代码
5. Sentry Agent：分析运行错误
6. Coder Agent：根据错误自动修复，最多 3 次

## 安装依赖

如果还没有安装 `rich`、`streamlit` 或 `python-dotenv`，请执行：

```powershell
.\.venv\Scripts\python.exe -m pip install rich streamlit python-dotenv
```

如果 OpenAI SDK 也没有安装，请执行：

```powershell
.\.venv\Scripts\python.exe -m pip install openai langgraph rich streamlit python-dotenv
```

## 配置 DeepSeek

项目使用 `python-dotenv` 读取项目根目录的 `.env` 文件，也支持直接读取系统环境变量。可以参考 `.env.example` 创建自己的 `.env`：

```text
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
OFFLINE_MODE=false
CODE_RUN_TIMEOUT=10
```

`.env` 已加入 `.gitignore`，不要把真实 key 提交到 Git。

如果比赛现场网络不稳定，或者 API Key 临时不可用，可以开启离线演示模式：

```text
OFFLINE_MODE=true
```

开启后系统会使用 `offline_demo.py` 中的预置响应，CLI 和 Web UI 仍然可以继续展示 Product、Coder、Tester、Sentry 和自动修复流程。

即使没有手动开启离线模式，只要 DeepSeek API 调用失败，系统也会自动切换到预置演示响应，保证比赛现场不中断。

## 安全兜底

`Code Runner` 在执行生成代码前会做轻量安全检查，发现以下危险操作会直接拦截：

- `os.remove`
- `shutil.rmtree`
- `subprocess`
- `eval`
- `exec`

代码运行超时时间由 `CODE_RUN_TIMEOUT` 控制，默认 10 秒。

## 运行

一键启动入口（Windows）：

```powershell
cd D:\AIchatProject
.\start_demo.bat
```

启动后可选择：

```text
1. Start CLI Demo: python graph_demo.py
2. Start Web UI: streamlit run webui.py
3. Exit
```

原有 CLI 演示入口：

```powershell
cd D:\AIchatProject
.\.venv\Scripts\python.exe main.py
```

启动后会出现演示菜单：

```text
1. 简单案例
2. 翻车修复案例
3. 综合案例
4. 自定义输入
```

LangGraph 演示入口：

```powershell
cd D:\AIchatProject
.\.venv\Scripts\python.exe graph_demo.py
```

`graph_demo.py` 也会显示演示菜单：

```text
1. 简单成功案例
2. 翻车修复案例
3. 综合案例
4. 自定义输入
```

LangGraph 演示会优先展示最终状态摘要：

- 是否成功
- 修复次数
- 最终 stdout
- 最终 error_log

Streamlit Web UI：

```powershell
cd D:\AIchatProject
streamlit run webui.py
```

Web UI 包含需求输入、演示案例选择、Agent 执行过程、最终运行结果和 Markdown 报告查看。

Web UI 截图占位：

```text
docs/assets/webui-dashboard.png
```

建议比赛前截取 Streamlit 首页、Agent 工作流和最终结果面板，放到上面的路径。

## 演示案例

普通成功案例：

```text
做一个简单 Python 程序，运行后直接打印 hello world，不需要用户输入
```

自动修复案例：

```text
写一个简单 Python 程序，必须调用 input 读取用户姓名，然后打印 hello 加姓名
```

这个案例在自动运行时容易触发 `EOFError`，适合展示：

- 第一次运行失败
- Sentry Agent 分析错误
- Coder Agent 自动修复
- 再次运行成功

综合案例：

```text
写一个学生成绩统计程序。程序内置 5 个学生的姓名和分数，不需要用户输入。运行后输出平均分、最高分学生、最低分学生、及格人数，并用函数组织代码。
```

完整比赛讲稿见：

```text
docs/DEMO_SCRIPT.md
```

## 输出效果

CLI 使用 `rich` 展示不同 Agent 的状态：

- Product Agent：蓝色
- Coder Agent：绿色
- Tester Agent：黄色
- Sentry Agent：红色

最终运行结果会显示：

- 成功：绿色 ✅
- 失败：红色 ❌

## Figma 协作

本项目已准备 Figma 协作说明和 UI 设计规格：

```text
figma/design_link.md
docs/UI_SPEC.md
```

当前只完成设计文档，不包含前端代码。

建议在 Figma 中设计 4 个核心页面：

- 首页：项目介绍与开始按钮
- Agent 工作流页：展示 Product、Coder、Tester、Sentry 节点
- 运行日志页：展示 stdout、stderr、修复次数
- 报告页：展示 Markdown 报告列表

## 答辩材料

比赛答辩材料已整理在：

```text
docs/PRESENTATION_OUTLINE.md
docs/SCORE_POINTS.md
docs/DEFENSE_QA.md
```

建议答辩时按以下顺序准备：

1. 先讲 `PRESENTATION_OUTLINE.md` 中的项目背景、架构和演示流程。
2. 再用 `SCORE_POINTS.md` 对齐评分点。
3. 最后用 `DEFENSE_QA.md` 准备评委追问。

## 操作指南

比赛现场操作说明见：

```text
docs/OPERATION_GUIDE.md
```

完整用户操作手册和跨设备部署步骤见：

```text
docs/USER_MANUAL.md
```
