# 操作指南

如果需要在另一台设备上重新部署项目，请优先参考完整手册：

```text
docs/USER_MANUAL.md
```

## 1. 环境安装

建议使用 Windows + Python 3.10 及以上版本。

进入项目目录：

```powershell
cd D:\AIchatProject
```

安装依赖：

```powershell
python -m pip install openai langgraph rich streamlit python-dotenv
```

如果使用项目虚拟环境：

```powershell
.\.venv\Scripts\python.exe -m pip install openai langgraph rich streamlit python-dotenv
```

## 2. API 与运行配置

项目支持两种方式读取 DeepSeek API Key。

### 方式一：环境变量

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

### 方式二：`.env` 文件

在项目根目录创建 `.env`：

```text
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
OFFLINE_MODE=false
CODE_RUN_TIMEOUT=10
```

也可以直接复制 `.env.example` 后修改：

```powershell
copy .env.example .env
```

注意：`.env` 不要提交到 Git。

### 离线演示模式

如果现场网络不稳定、API Key 额度不足或 DeepSeek API 暂时不可用，可以在 `.env` 中开启：

```text
OFFLINE_MODE=true
```

开启后系统会使用 `offline_demo.py` 中的预置演示响应，仍然可以展示完整的 Agent 流程和自动修复闭环。

如果没有开启离线模式，但 DeepSeek API 临时调用失败，系统也会自动使用预置演示响应，避免比赛现场流程中断。

### 代码运行超时

`CODE_RUN_TIMEOUT` 控制生成代码最多运行多少秒，默认 10 秒：

```text
CODE_RUN_TIMEOUT=10
```

## 3. 一键启动

Windows 下可直接双击：

```text
start_demo.bat
```

菜单选项：

```text
1. Start CLI Demo: python graph_demo.py
2. Start Web UI: streamlit run webui.py
3. Exit
```

## 4. CLI 启动方式

```powershell
python graph_demo.py
```

如果使用虚拟环境：

```powershell
.\.venv\Scripts\python.exe graph_demo.py
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
streamlit run webui.py
```

浏览器打开：

```text
http://localhost:8501
```

Web UI 支持：

- 需求输入
- 演示案例选择
- Agent 状态卡片
- 工作流展示
- stdout / error_log
- Markdown 报告

## 6. 演示案例选择

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

## 7. 常见报错处理

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
streamlit run webui.py --server.port 8502
```

### Web UI 没有自动打开浏览器

手动访问：

```text
http://localhost:8501
```

### input 案例运行失败

这是正常演示点。系统会将 `EOFError` 交给 Sentry Agent 分析，并让 Coder Agent 自动修复。

## 8. 比赛推荐启动顺序

1. 双击 `start_demo.bat`。
2. 选择 `2` 启动 Web UI。
3. 打开浏览器展示 Dashboard。
4. 先跑简单成功案例。
5. 再跑翻车修复案例。
6. 展示 Markdown 报告。
