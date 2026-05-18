# 操作指南

> 维护指南：本文面向维护者和排障场景。面向演示用户的新设备部署说明见 `docs/USER_MANUAL.md`，双轨启动顺序见 `docs/STARTUP_ORDER.md`，Docker 多服务主文档见 `docs/DOCKER_COMPOSE_GUIDE.md`。

如果需要在另一台设备上重新部署项目，请优先参考完整手册：

```text
docs/USER_MANUAL.md
```

## 1. 环境安装

建议使用 Windows + Python 3.10 及以上版本。

### 新电脑部署流程

1. 将项目复制到新电脑，例如放在 `D:\AIchatProject`。
2. 安装 Python 3.10 或以上版本，并确认安装时勾选 `Add python.exe to PATH`。
3. 打开 PowerShell，进入项目目录。
4. 运行 `install.bat` 自动创建虚拟环境并安装依赖。
5. 复制 `.env.example` 为 `.env`，填写 DeepSeek API Key。
6. 运行 `start_demo.bat` 启动 CLI 或 Web UI。

进入项目目录：

```powershell
cd D:\AIchatProject
```

推荐使用自动安装脚本：

```powershell
.\install.bat
```

手动安装方式：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2. API 与运行配置

项目支持 DeepSeek、通义千问 Qwen 和智谱 GLM。模型列表在 `config/models.yaml` 中维护，默认使用 `DEFAULT_MODEL_PROVIDER=deepseek`。

### 项目模块结构

当前工程按职责拆分为：

- `core/`：核心 LangGraph 工作流、AgentState、质量评分。
- `agents.py` / `agents/`：Product、Coder、Tester、Sentry 等智能体能力。
- `plugins/`：可配置扩展模块，例如 Doc、Security、Refactor、UI Agent。
- `utils/`：代码保存运行、pytest、coverage、历史记录、模型对比等工具。
- `config/`：默认设置、模型配置和插件配置。

`graph.py` 仍然保留为兼容入口，内部导出 `core.workflow` 中的 `build_graph()` 和 `run_graph_demo()`，所以原有启动方式不变。

### 默认运行参数

项目默认参数保存在：

```text
config/settings.yaml
```

默认内容：

```yaml
max_retry_count: 3
offline_mode: false
require_human_approval: true
default_model_provider: deepseek
demo_mode: true
save_reports: true
save_runs: true
```

这些配置会影响：

- CLI 和 Web UI 的默认最大修复次数。
- 默认模型服务商。
- 是否默认启用人工审批。
- Web UI 是否默认进入演示模式。
- 是否默认开启离线演示模式。

### 方式一：环境变量

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:QWEN_API_KEY="你的通义千问 API Key"
$env:GLM_API_KEY="你的智谱 GLM API Key"
$env:DEFAULT_MODEL_PROVIDER="deepseek"
```

### 方式二：`.env` 文件

在项目根目录创建 `.env`：

```text
DEEPSEEK_API_KEY=your_deepseek_api_key
QWEN_API_KEY=your_qwen_api_key
GLM_API_KEY=your_glm_api_key
DEFAULT_MODEL_PROVIDER=deepseek
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
OFFLINE_MODE=false
```

也可以直接复制 `.env.example` 后修改：

```powershell
copy .env.example .env
```

注意：`.env` 不要提交到 Git。

### 多模型切换

当前支持的模型配置如下：

```text
DeepSeek: deepseek-chat
Qwen: qwen-plus
GLM: glm-4-flash
```

Web UI 左侧栏有“模型选择”区域，可以直接选择 DeepSeek、Qwen 或 GLM。所选模型会写入本次运行状态：

- `model_provider`
- `model_name`
- `model_base_url`

如果选择的模型缺少对应 API Key，Web UI 会显示 warning，并在运行时自动使用离线演示响应，不影响 DeepSeek 已配置场景继续运行。

### 离线演示模式

如果现场网络不稳定、API Key 额度不足或模型 API 暂时不可用，可以在 `.env` 中开启：

```text
OFFLINE_MODE=true
```

开启后系统会使用 `offline_demo.py` 中的预置演示响应，仍然可以展示完整的 Agent 流程和自动修复闭环。

如果没有配置当前模型对应的 API Key，系统也会自动进入离线演示模式，避免比赛现场因为 API Key 缺失而中断。

如果没有开启离线模式，但当前模型 API 临时调用失败，系统也会自动使用预置演示响应，避免比赛现场流程中断。

### 代码运行超时

`CODE_RUN_TIMEOUT` 控制生成代码最多运行多少秒，默认 10 秒：

```text
CODE_RUN_TIMEOUT=10
```

如果不配置该项，系统会自动使用默认 10 秒。

### 统一错误处理

错误摘要能力集中在：

```text
utils/error_utils.py
```

核心函数：

- `summarize_error(error_log)`：从 stderr、pytest 输出或 Traceback 中提取关键错误行。
- `format_error_for_display(error_log, demo_mode=True)`：演示模式返回摘要，开发模式返回完整错误。
- `is_retryable_error(error_log)`：判断错误是否适合继续自动修复。

使用规则：

- 比赛演示模式只显示错误摘要，避免投屏时出现过长错误栈。
- 开发模式显示完整 stderr、pytest stderr 和 error_log。
- Markdown 报告会额外包含“错误摘要”区域，便于答辩时快速说明失败原因。

### 统一运行摘要

核心运行结果统一由下面的工具生成：

```text
utils/summary_builder.py
```

核心函数：

```text
build_run_summary(state)
```

统一摘要字段：

- `success`
- `retry_count`
- `test_success`
- `coverage_percent`
- `quality_score`
- `security_status`
- `enabled_plugins`
- `model_provider`
- `report_path`

CLI、Web UI 和 Markdown 报告都使用同一份 `run_summary` 展示核心结果。这样后续如果要调整“安全状态”或“插件启用状态”的展示文案，只需要改 `summary_builder.py`。

### 自定义 AI 模块配置

项目会读取 `config/agents.yaml`，并在 LangGraph 流程结束前运行 `enabled=true` 的插件。

默认配置：

```yaml
plugins:
  - name: doc_agent
    enabled: true
  - name: security_agent
    enabled: true
  - name: refactor_agent
    enabled: true
  - name: ui_agent
    enabled: true
```

- `Doc Agent`：根据最终代码生成说明内容，写入 `state["doc_result"]`。
- `Security Agent`：检查危险操作，写入 `state["security_result"]`。
- `Refactor Agent`：分析代码结构、命名和可读性，写入 `state["refactor_result"]`。
- `UI Agent`：根据用户需求和最终代码生成 UI 设计建议，写入 `state["ui_result"]`。

关闭插件时，将对应插件的 `enabled` 改成 `false`。

新增插件时，在 `plugins/` 目录新建文件，继承 `BasePluginAgent` 并实现 `run(state)` 方法。然后在 `plugin_loader.py` 的 `PLUGIN_CLASSES` 中登记插件名和类，再把插件名加入 `config/agents.yaml`。

插件开发模板和完整说明见：

```text
plugins/plugin_template.py
docs/PLUGIN_GUIDE.md
```

### Web UI 中配置插件

比赛现场推荐直接在 Web UI 中开关插件：

1. 启动 Web UI：

```powershell
python -m streamlit run webui.py
```

2. 在左侧栏找到“自定义 AI 模块配置”。
3. 查看当前支持的插件：
   - `Doc Agent`
   - `Security Agent`
   - `Refactor Agent`
   - `UI Agent`
4. 勾选或取消勾选插件旁边的 checkbox。
5. 页面会自动写回 `config/agents.yaml`。
6. 点击“开始运行”，系统会按照最新配置执行插件。

运行完成后，结果区域会显示“插件执行结果”面板：

- `doc_result`
- `security_result`
- `refactor_result`
- `ui_result`

如果某个插件没有启用，面板中会显示“该插件未启用”。

## 3. 一键启动

Windows 下可直接双击：

```text
start_demo.bat
```

菜单选项：

```text
1. Start CLI Demo: python graph_demo.py
2. Start Web UI: python -m streamlit run webui.py
3. Exit
```

`start_demo.bat` 会在项目根目录下优先激活 `.venv` 虚拟环境，然后统一使用 `python` 启动命令，避免直接调用全局 `streamlit` 命令。

如果 `.venv` 是从其他电脑复制过来的，可能会因为 Python 安装路径不同而失效。此时请重新创建虚拟环境并安装依赖。

## 4. CLI 启动方式

```powershell
python graph_demo.py
```

如果使用虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
python graph_demo.py
```

启动后选择演示案例：

```text
1. 简单成功案例
2. 翻车修复案例
3. 综合案例
4. 自定义输入
```

## 5. Web UI 启动方式

```powershell
python -m streamlit run webui.py
```

浏览器打开：

```text
http://localhost:8501
```

Web UI 支持：

- 左侧控制栏选择演示案例或输入自定义需求
- 设置最大自动修复次数
- 选择当前模型：DeepSeek、Qwen 或 GLM
- 显示在线 / 离线模式
- 在 Web UI 中启用或关闭自定义 AI 插件
- 勾选“我确认允许运行 AI 生成的代码”后开始运行
- 清空本次页面运行结果
- 右侧展示当前模型、运行状态、success、retry_count、enabled_plugins
- 展示 Requirement、Product、Coder、Tester、Approval、Runner、Sentry、Plugins、Quality、Report 的 Waiting / Running / Done / Failed / Repairing 状态
- 使用 Tabs 查看 Product、Coder、Tester、Sentry、Plugins 和 Final State
- 查看 Tester Agent 自动生成的 pytest 测试代码、test_success、pytest stdout 和 pytest stderr
- 查看 coverage 覆盖率、quality_score 和完整评分依据
- 使用折叠面板查看 stdout 和 stderr
- 查看最新 Markdown 报告

### 5.1 演示模式与开发模式

Web UI 左侧提供两种显示模式：

- 演示模式：隐藏完整错误栈，只展示错误摘要，适合比赛现场投屏。
- 开发模式：展示完整 state、stdout、stderr，适合调试问题。

演示模式会重点展示：

- 用户输入需求
- 当前执行到哪个 Agent
- Agent 工作流进度
- 是否发生错误
- pytest 自动测试是否通过
- 覆盖率和质量评分
- Sentry Agent 如何分析错误
- Coder Agent 如何修复
- 最终是否成功
- 修复次数
- 报告是否生成

演示模式新增区域：

- `演示模式总览`：用摘要卡片展示本次运行重点。
- `自动修复高光时刻`：触发修复时展示第一次失败、错误摘要、Sentry 分析、Coder 修复和再次运行结果。
- `讲解提示`：根据本次结果自动生成比赛讲解要点。
- `结果总结卡片`：展示成功/失败、修复次数、生成代码文件、安全检查、文档生成和报告文件名。

状态会自动转换成中文：

```text
Waiting   → 等待中
Running   → 运行中
Done      → 已完成
Failed    → 失败
Repairing → 修复中
```

颜色高亮规则：

- 等待中：灰色。
- 运行中：蓝色。
- 已完成：绿色。
- 失败：红色。
- 修复中：黄色。

当发生自动修复时，修复相关节点会显示 `retry_count`，并使用黄色边框突出。最终成功后，Report 节点会用绿色加粗样式显示，方便比赛现场快速讲清“失败 → 分析 → 修复 → 成功”的过程。

插件结果也会高亮：

- 通过：绿色。
- 建议或警告：黄色。
- 风险或失败：红色。
- 未启用：灰色。

### 5.2 人工审批节点

因为系统会保存并运行 AI 生成的 Python 代码，开始运行前必须勾选：

```text
我确认允许运行 AI 生成的代码
```

未勾选时点击“开始运行”，Web UI 会继续执行需求分析、代码生成和 Tester Agent 检查，但 `Approval Node` 会拒绝执行 Runner：

```text
approved = False
approval_message = 等待人工确认：用户未勾选运行确认框，已停止执行 Runner。
error_log = 用户拒绝执行 AI 生成代码
```

此时系统不会运行 `output/generated_code.py`，也不会进入自动修复，而是直接进入插件和报告阶段。

勾选后再点击“开始运行”，审批通过：

```text
approved = True
approval_message = Web UI 人工审批通过，允许运行 AI 生成代码。
```

CLI 运行 `graph_demo.py` 时，可以选择是否启用人工审批。如果启用，终端会询问：

```text
是否允许运行 AI 生成的代码？y/n
```

### 5.3 pytest 自动测试

LangGraph 中的 Tester Agent 不再只是静态检查。它会根据用户需求和生成代码自动生成 pytest 文件：

```text
tests/test_generated_code.py
```

系统随后执行 pytest + coverage：

```powershell
python -m coverage run -m pytest tests/test_generated_code.py -q
python -m coverage report
```

测试状态会写入：

- `test_code`
- `test_stdout`
- `test_stderr`
- `test_success`
- `coverage_stdout`
- `coverage_percent`

最终成功条件是：

```text
Runner success == True
pytest test_success == True
```

如果 pytest 失败，Sentry Agent 会同时收到原始代码、测试代码、pytest stdout、pytest stderr 和 Runner error_log，再判断是代码逻辑问题、测试问题、边界条件问题还是运行环境问题。Coder Agent 修复时会被明确要求修复业务代码，而不是修改测试用例。

### 5.4 质量评分与覆盖率

系统在插件执行后、报告生成前执行 `Quality Node`，输出：

- `quality_score`
- `quality_summary`
- `coverage_percent`
- `coverage_stdout`

评分规则为 100 分：

- pytest 通过：30 分
- 程序运行成功：20 分
- 覆盖率 >= 90%：20 分；>= 70%：15 分；>= 50%：10 分；< 50%：5 分
- 安全检查通过：15 分
- 自动修复次数 0 次：15 分；1 次：10 分；2 次：5 分；3 次：0 分

演示模式会显示大号质量分数卡片、覆盖率、测试状态和安全状态。开发模式会显示完整 `coverage_stdout`、完整评分依据和完整 state。

### 5.5 多模型效果对比

Web UI 支持在同一需求下对比 2-3 个模型：

1. 在左侧栏勾选“启用模型对比模式”。
2. 在“选择 2-3 个模型”中选择 DeepSeek、Qwen、GLM。
3. 输入同一个用户需求。
4. 勾选“我确认允许运行 AI 生成的代码”。
5. 点击“开始运行”。

系统会让每个模型独立执行完整 LangGraph 流程，并保存：

```text
runs/{run_id}_model1.json
runs/{run_id}_model2.json
runs/{run_id}_model3.json
reports/report_compare_{run_id}.md
```

“模型对比”Tab 会展示：

- 成功状态
- 失败次数
- 自动修复次数
- pytest 是否通过
- 覆盖率
- 质量评分
- 插件摘要

对比表会自动突出关键指标：成功模型行使用绿色背景，修复次数最少的模型行使用浅绿色提示，覆盖率最高值使用绿色文字，质量评分最高值使用绿色加粗，便于直接投屏讲解。

也可以展开每个模型查看完整 stdout、stderr 和插件详细输出。CLI 中运行 `python graph_demo.py` 后，可选择“多模型对比运行”，并输出同样的 Markdown 对比报告。

Web UI 会使用 `st.session_state` 保存：

- `requirement`
- `selected_case`
- `result_state`
- `run_status`
- `enabled_plugins`
- `latest_report`
- `stdout`
- `stderr`

### 5.3 报告文件

每次 Web UI 运行结束后会生成 Markdown 报告：

```text
reports/report_时间戳.md
reports/latest_report.md
```

页面底部会显示最新报告文件名，并支持直接查看和下载报告内容。

### 5.4 历史运行记录

每次 Web UI 或 `graph_demo.py` 完成运行后，系统都会生成一个 `run_id`：

```text
run_年月日_时分秒
```

例如：

```text
run_20260427_153000
```

最终状态会保存到：

```text
runs/{run_id}.json
```

状态文件至少包含：

- requirement
- product_result
- code
- tester_result
- sentry_result
- stdout
- error_log
- test_code
- test_stdout
- test_stderr
- test_success
- coverage_stdout
- coverage_percent
- quality_score
- quality_summary
- retry_count
- success
- enabled_plugins
- approved
- approval_message
- require_human_approval
- doc_result
- security_result
- refactor_result
- ui_result
- report_path

在 Web UI 底部找到“历史运行记录”区域后，可以：

1. 选择历史 `run_id`。
2. 查看该次运行的需求、成功状态、修复次数和报告路径。
3. 展开“过程回放”查看各 Agent 摘要。
4. 展开“查看历史生成代码”查看该次 Coder Agent 代码。
5. 展开“查看历史错误日志”查看该次 stderr / error_log。
6. 展开“查看历史 pytest 测试”查看测试摘要、测试代码和测试日志。
7. 展开“查看历史质量评分”查看覆盖率、质量评分和评分依据。
8. 点击“加载为当前结果”，把历史记录加载到主展示区。

`graph_demo.py` 运行结束后会在终端打印：

- run_id
- 状态保存路径
- 报告路径

## 6. Docker 与 v2 前端部署方式

如果新电脑已经安装 Docker Desktop，可以使用 Docker 固定 Python 版本和依赖环境。

### 6.0 Vue 开发模式启动

Vue3 + TypeScript 前端位于：

```text
frontend-vue/
```

开发模式默认使用 Python Direct，需要两个终端。

终端 1：启动 Python Agent Engine API：

```powershell
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
```

终端 2：启动 Vue 开发服务器：

```powershell
cd D:\AIchatProject\frontend-vue
npm install
npm run dev
```

开发模式访问：

```text
Vue 前端: http://localhost:5173
FastAPI Docs: http://localhost:8001/docs
```

`frontend-vue/.env.development` 默认指向 Python Direct：

```text
VITE_API_MODE=python
VITE_PYTHON_API_BASE_URL=http://127.0.0.1:8001
VITE_JAVA_API_BASE_URL=http://127.0.0.1:8088/api
```

如果要通过 Java Gateway 调用，请先启动 MySQL 和 `backend-java`，再将 `VITE_API_MODE` 改为 `java`。MySQL 配置见 `docs/MYSQL_SETUP.md`。

### 6.0.1 Vue 生产构建

生产构建命令：

```powershell
cd D:\AIchatProject\frontend-vue
npm run build
```

构建产物位于：

```text
frontend-vue/dist/
```

`frontend-vue/.env.production` 默认指向 Java Gateway：

```text
VITE_API_MODE=java
VITE_PYTHON_API_BASE_URL=http://localhost:8001
VITE_JAVA_API_BASE_URL=http://localhost:8088/api
```

生产容器中使用 Nginx 托管静态资源，并通过 `nginx.conf` 支持 Vue Router history 路由回退到 `index.html`。

### 6.1 准备配置

进入项目目录：

```powershell
cd D:\AIchatProject
```

复制环境变量模板：

```powershell
copy .env.example .env
```

编辑 `.env`：

```text
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
OFFLINE_MODE=false
```

### 6.2 Docker Compose 多服务启动

```powershell
docker compose up --build
```

启动后浏览器访问：

```text
Vue 前端: http://localhost:5174
FastAPI Docs: http://localhost:8001/docs
Java Gateway: http://localhost:8088/api/health
MySQL: localhost:3306
Streamlit v1: http://localhost:8501
```

### 6.3 停止容器

```powershell
docker compose down
```

### 6.4 Docker 说明

- 镜像基于 `python:3.11-slim`。
- 依赖来自 `requirements.txt`。
- 根目录 `Dockerfile` 默认启动 Streamlit Web UI，也可以通过 Compose command 覆盖为 FastAPI API 服务。
- `frontend-vue/Dockerfile` 使用 `node:20-alpine` 构建 Vue，并使用 `nginx:alpine` 运行生产静态资源。
- `.env` 会通过 `docker-compose.yml` 传入容器。
- Compose 会读取 `DEEPSEEK_API_KEY`、`QWEN_API_KEY`、`GLM_API_KEY` 和 `DEFAULT_MODEL_PROVIDER`。
- Compose 服务包括 `mysql`、`ai-agent-api`、`backend-java`、`frontend-vue` 和 `streamlit-web`。
- `mysql_data` volume 会保存 Java 平台层数据库数据。
- `reports/`、`runs/`、`output/`、`config/` 会挂载到 Python 容器中，方便保留报告、历史、生成产物和配置。
- `runner-cpp/` 会挂载到 Python 容器中，作为可选 C++ Runner Sandbox 增强模块。
- Windows 本地启动方式不受影响，仍然可以使用 `start_demo.bat`。

### 6.5 CORS 说明

FastAPI API 当前允许以下前端来源：

```text
http://localhost:5173
http://localhost:5174
http://127.0.0.1:5173
http://127.0.0.1:5174
```

开发阶段可以扩展来源；生产部署时应收紧到实际域名。

## 7. 演示案例选择

### 简单成功案例

适合开场，证明系统可以完整跑通。

```text
做一个简单 Python 程序，运行后直接打印 hello world，不需要用户输入
```

### 翻车修复案例

适合展示自动修复闭环。

```text
写一个简单 Python 程序，必须调用 input 读取用户姓名，然后打印 hello 加姓名
```

### 综合案例

适合展示稍复杂代码生成。

```text
写一个学生成绩统计程序。程序内置 5 个学生的姓名和分数，不需要用户输入。运行后输出平均分、最高分学生、最低分学生、及格人数，并用函数组织代码。
```

## 8. 常见报错处理

### 报错：Python was not found

说明新电脑没有安装 Python，或 Python 没有加入 PATH。

处理：

1. 安装 Python 3.10 或以上版本。
2. 安装时勾选 `Add python.exe to PATH`。
3. 重新打开 PowerShell 后再运行 `install.bat`。

### 报错：install.bat 安装依赖失败

通常是网络问题或 pip 源访问慢。

处理：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

如果仍然失败，检查当前网络是否能访问 Python 包下载源。

### 报错：No module named streamlit

说明 Streamlit 没有安装。

处理：

```powershell
python -m pip install streamlit
```

### 报错：No module named rich

处理：

```powershell
python -m pip install rich
```

### 报错：No module named dotenv

处理：

```powershell
python -m pip install python-dotenv
```

### 报错：No module named langgraph 或 langchain

处理：

```powershell
python -m pip install -r requirements.txt
```

### 报错：No module named coverage

说明覆盖率依赖没有安装。项目使用 `coverage` 统计 pytest 覆盖率。

处理：

```powershell
python -m pip install -r requirements.txt
```

### 报错：请先设置环境变量 DEEPSEEK_API_KEY

说明没有配置 DeepSeek API Key。

处理：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

或者创建 `.env` 文件。

如果比赛现场只是要保证演示继续，可以在 `.env` 中设置：

```text
OFFLINE_MODE=true
```

### 报错：安全检查失败

说明生成代码包含危险操作，运行器已经在执行前拦截。

当前禁止：

- `os.remove`
- `shutil.rmtree`
- `subprocess`
- `eval`
- `exec`

处理方式：让 Sentry Agent 和 Coder Agent 修复代码，或修改需求，避免生成危险调用。

### 报错：代码运行超时

说明生成代码可能在等待输入或进入死循环。

处理方式：优先展示自动修复流程；如需临时放宽超时，可调整 `.env`：

```text
CODE_RUN_TIMEOUT=15
```

### 报错：端口 8501 被占用

说明已有 Streamlit 或其他服务占用端口。

处理：

```powershell
python -m streamlit run webui.py --server.port 8502
```

如果使用 Docker，可以临时修改 `docker-compose.yml` 的端口映射，例如：

```yaml
ports:
  - "8502:8501"
```

然后访问：

```text
http://localhost:8502
```

### 报错：Vue 前端提示 API 连接失败

说明当前 `VITE_API_MODE` 对应的 API 服务未启动或端口不一致。

处理：

```powershell
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
```

然后访问：

```text
http://localhost:8001/health
```

如果使用 Docker Compose，请确认 `ai-agent-api` 正常启动，并访问：

```text
http://localhost:8001/docs
```

如果 `VITE_API_MODE=java`，还需要确认 Java Gateway 正常启动：

```text
http://localhost:8088/api/health
http://localhost:8088/api/agent/health
```

同时确认 MySQL 正常：

```text
localhost:3306
```

### 报错：浏览器出现 CORS 错误

说明当前前端地址不在 FastAPI 允许来源中。默认已允许：

```text
http://localhost:5173
http://localhost:5174
http://127.0.0.1:5173
http://127.0.0.1:5174
```

处理方式：

1. 优先使用上述端口访问 Vue。
2. 如果必须换端口，在 `api_server.py` 的 CORS `allow_origins` 中增加对应来源。
3. 生产环境不要长期使用过宽的 CORS 配置，应收紧到实际域名。

### 报错：端口 8001、5173 或 5174 被占用

说明 FastAPI、Vue dev server 或 Nginx 前端端口已被占用。

处理：

- FastAPI 可改端口启动，并同步修改 `frontend-vue/.env.development`。
- Vue dev server 可使用 Vite 自动分配的新端口，或关闭占用进程。
- Docker Compose 可调整 `docker-compose.yml` 中的端口映射，例如 `"5175:80"`。

### 报错：npm run build 失败

常见原因是 Node 版本过低、依赖未安装或 TypeScript 类型错误。

处理：

```powershell
cd frontend-vue
npm install
npm run build
```

推荐 Node.js 20。不要为了通过构建删除核心页面或组件；应根据 TypeScript 报错修正类型定义、组件 props 或 API 返回类型。

### 报错：docker 不是内部或外部命令

说明没有安装 Docker Desktop，或 Docker 没有加入 PATH。

处理：

1. 安装 Docker Desktop。
2. 重启 PowerShell。
3. 执行 `docker --version` 检查是否安装成功。

### 报错：docker compose up 失败

常见原因是网络问题、Docker Desktop 没有启动、`.env` 文件不存在，或本机 `3306` 已被其他 MySQL 服务占用。

处理：

```powershell
copy .env.example .env
docker compose up --build
```

### Web UI 没有自动打开浏览器

手动访问：

```text
http://localhost:8501
```

### input 案例运行失败

这是正常演示点。系统会将 `EOFError` 交给 Sentry Agent 分析，并让 Coder Agent 自动修复。

## 9. 比赛推荐启动顺序

1. 双击 `start_demo.bat`。
2. 选择 `2` 启动 Web UI。
3. 打开浏览器展示 Dashboard。
4. 先跑简单成功案例。
5. 再跑翻车修复案例。
6. 展示 Markdown 报告。
