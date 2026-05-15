# AI Multi-Agent Pipeline

## 项目简介

一个面向比赛演示的多智能体自动开发流水线项目。用户输入自然语言需求后，系统会完成需求拆解、代码生成、pytest 自动测试、代码运行、错误分析、自动修复、插件扩展、质量评分和 Markdown 报告生成。

项目默认支持 DeepSeek，也支持通义千问 Qwen 和智谱 GLM。Web UI 适合比赛现场展示，CLI 适合快速验证和调试。

## 项目亮点

- 国产大模型驱动：支持 DeepSeek、Qwen、GLM。
- 多 Agent 协作：Product、Coder、Tester、Sentry、Quality 分工明确。
- LangGraph 状态机：支持条件分支、自动修复循环和人工审批。
- 测试驱动修复：自动生成 pytest 测试，用测试失败结果驱动修复。
- Human-in-the-loop：运行 AI 生成代码前需要人工确认。
- 插件式 AI 模块：Doc、Security、Refactor、UI Agent 可配置启用。
- 多模型对比：同一需求下对比多个模型的成功率、修复次数、覆盖率和质量评分。
- 质量评分：从运行、测试、覆盖率、安全和修复次数给出 100 分评价。
- Web UI 可视化：展示 Agent 工作流、修复过程、插件结果、历史记录和报告。
- Docker 部署：降低新设备环境差异导致的演示风险。

## 技术架构

```text
用户需求
  ↓
Product Agent：需求拆解
  ↓
Coder Agent：代码生成 / 修复
  ↓
Tester Agent：生成 pytest 并运行测试
  ↓
Approval Node：人工审批
  ↓
Runner：保存并运行代码
  ↓
条件判断
  ├─ 成功：Plugins → Quality → Report
  └─ 失败：Sentry Agent → Coder Agent，最多自动修复 N 次
```

核心状态由 LangGraph 管理，最终写入 `runs/{run_id}.json`，同时生成 Markdown 报告到 `reports/`。

## 核心功能

- 根据自然语言需求生成 Python 代码。
- 自动保存代码到 `output/generated_code.py`。
- 自动生成测试文件 `tests/test_generated_code.py`。
- 使用 pytest + coverage 验证代码正确性和覆盖率。
- 捕获 stdout、stderr、returncode。
- 失败后由 Sentry Agent 分析错误并触发 Coder Agent 修复。
- 支持最大修复次数配置，默认 3 次。
- 支持危险代码检查，拦截 `os.remove`、`shutil.rmtree`、`subprocess`、`eval`、`exec`。
- 支持插件系统、运行历史、报告生成和模型对比。

## 快速启动

Windows 推荐使用一键安装脚本：

```powershell
cd D:\AIchatProject
.\install.bat
```

复制环境变量模板：

```powershell
copy .env.example .env
```

填写至少一个模型 API Key，例如：

```text
DEEPSEEK_API_KEY=your_deepseek_api_key
DEFAULT_MODEL_PROVIDER=deepseek
OFFLINE_MODE=false
```

启动 Web UI：

```powershell
python -m streamlit run webui.py
```

浏览器访问：

```text
http://localhost:8501
```

如果比赛现场网络不稳定，可以设置：

```text
OFFLINE_MODE=true
```

系统会使用预置响应继续演示流程。

## 本地运行方式

手动安装依赖：

```powershell
cd D:\AIchatProject
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

一键启动菜单：

```powershell
.\start_demo.bat
```

可选择：

```text
1. CLI 演示
2. Web UI
3. 退出
```

## Docker 运行方式

先准备 `.env`：

```powershell
copy .env.example .env
```

启动容器：

```powershell
docker compose up --build
```

访问：

```text
http://localhost:8501
```

停止：

```powershell
docker compose down
```

Docker 服务名为 `ai-agent-pipeline`，并挂载：

- `reports/`
- `runs/`
- `output/`

## Web UI 使用方式

启动：

```powershell
python -m streamlit run webui.py
```

左侧控制栏包含：

- 演示案例选择
- 自定义需求输入
- 最大修复次数设置
- 演示模式 / 开发模式切换
- DeepSeek / Qwen / GLM 模型选择
- 多模型对比模式
- 插件开关
- 人工审批 checkbox
- 开始运行和清空结果按钮

右侧展示区包含：

- 当前模型、运行状态、success、retry_count、enabled_plugins 状态卡片
- Requirement、Product、Coder、Tester、Approval、Runner、Sentry、Plugins、Quality、Report 工作流节点
- Product / Coder / Tester / Sentry / Plugins / 模型对比 / Final State Tabs
- pytest 测试结果和 coverage 覆盖率
- 质量评分
- stdout / stderr 折叠日志
- 运行报告和历史记录

演示模式会隐藏完整 prompt、完整 state 和过长错误栈，只保留关键摘要；开发模式显示完整调试信息。

## CLI 使用方式

LangGraph CLI：

```powershell
python graph_demo.py
```

可选择：

- 单模型运行
- 多模型对比运行
- 简单成功案例
- 翻车修复案例
- 综合案例
- 自定义输入

早期兼容入口仍保留：

```powershell
python main.py
```

## 插件系统说明

插件配置文件：

```text
config/agents.yaml
```

默认插件：

- Doc Agent：生成 README 风格说明，写入 `doc_result`。
- Security Agent：检查危险操作，写入 `security_result`。
- Refactor Agent：分析代码结构和可读性，写入 `refactor_result`。
- UI Agent：生成页面布局和交互建议，写入 `ui_result`。

插件统一结果写入：

```text
state["plugin_results"]
```

统一结构：

```text
plugin_name
status: success / warning / failed / disabled
summary
detail
```

开发新插件可参考：

```text
plugins/plugin_template.py
docs/PLUGIN_GUIDE.md
```

## 多模型切换说明

模型配置文件：

```text
config/models.yaml
```

支持模型：

- DeepSeek：`deepseek-chat`
- Qwen：`qwen-plus`
- GLM：`glm-4-flash`

环境变量：

```text
DEEPSEEK_API_KEY=your_deepseek_api_key
QWEN_API_KEY=your_qwen_api_key
GLM_API_KEY=your_glm_api_key
DEFAULT_MODEL_PROVIDER=deepseek
```

Web UI 可以在侧边栏选择模型。多模型对比会为每个模型独立运行完整流程，并生成对比报告：

```text
reports/report_compare_{run_id}.md
```

## 自动测试与质量评分说明

Tester Agent 会根据需求和代码生成 pytest 测试，并运行：

```powershell
python -m coverage run -m pytest tests/test_generated_code.py -q
python -m coverage report
```

最终成功需要同时满足：

- Runner 运行成功。
- pytest 测试通过。

Quality Node 使用 100 分制评分：

- pytest 通过：30 分
- 程序运行成功：20 分
- 覆盖率：最高 20 分
- 安全检查通过：15 分
- 自动修复次数：最高 15 分

评分结果保存为：

- `coverage_percent`
- `quality_score`
- `quality_summary`

## 自动修复闭环说明

当 Runner 或 pytest 失败时：

1. Sentry Agent 读取代码、stderr、pytest 输出和测试代码。
2. Sentry Agent 输出错误原因和修复建议。
3. Coder Agent 根据需求、原始代码、错误日志和 Sentry 建议修复代码。
4. 系统重新保存、测试并运行。
5. 达到最大修复次数后仍失败，则停止并生成最终报告。

最大修复次数配置在：

```text
config/settings.yaml
```

## 目录结构

```text
core/                 LangGraph 核心状态和工作流
agents.py             Product / Coder / Tester / Sentry Agent
plugins/              自定义 AI 插件模块
utils/                代码运行、测试、报告、摘要和历史工具
config/               模型、插件和默认运行配置
docs/                 操作手册、答辩材料、设计文档
reports/              Markdown 运行报告
runs/                 每次运行的完整 state JSON
output/               生成代码和兼容输出
tests/                自动生成的 pytest 测试
graph_demo.py         CLI 演示入口
webui.py              Streamlit Web UI
Dockerfile            Docker 镜像配置
docker-compose.yml    Docker Compose 启动配置
requirements.txt      Python 依赖
.env.example          环境变量模板
```

完整提交结构见：

```text
docs/DELIVERY_STRUCTURE.md
```

## 答辩与交付材料

- `docs/PRESENTATION_OUTLINE.md`：答辩大纲。
- `docs/DEFENSE_QA.md`：评委问答。
- `docs/DEMO_FLOW.md`：比赛现场演示流程。
- `docs/FINAL_CHECKLIST.md`：交付前检查清单。
- `docs/INNOVATION_POINTS.md`：创新点总结。
- `docs/RISK_AND_SOLUTION.md`：风险与解决方案。
- `docs/TECH_STACK.md`：技术栈说明。
- `docs/OPERATION_GUIDE.md`：部署和操作指南。
- `docs/USER_MANUAL.md`：跨设备部署手册。

## 常见问题

### 1. 没有 API Key 能演示吗？

可以。设置 `OFFLINE_MODE=true` 后，系统会使用预置响应完成演示流程。

### 2. Web UI 打不开怎么办？

确认命令是否正在运行：

```powershell
python -m streamlit run webui.py
```

再访问 `http://localhost:8501`。如果端口被占用，可以关闭占用进程或修改启动端口。

### 3. 为什么必须勾选人工审批？

因为系统会运行 AI 生成的 Python 代码。人工审批用于防止未经确认就执行潜在危险代码。

### 4. 自动修复一定成功吗？

不保证。系统默认最多修复 3 次，仍失败会停止并生成报告，方便人工接管。

### 5. 生成代码安全吗？

系统在运行前会拦截危险关键词，并通过 Security Agent 再做一次安全检查。但比赛项目仍建议只运行单文件、低风险 Python 示例。

### 6. Docker 和本地启动选哪个？

比赛现场推荐优先使用本地已验证环境；新设备部署或环境不稳定时使用 Docker 更稳。

### 7. 报告和历史记录在哪里？

- 报告：`reports/`
- 运行状态：`runs/`
- 生成代码：`output/generated_code.py`

### 8. 如何新增插件？

复制 `plugins/plugin_template.py`，实现 `run(state)`，在 `plugin_loader.py` 注册，并在 `config/agents.yaml` 启用。
