# 用户操作手册与跨设备部署指南

本文档面向比赛演示、答辩现场和新设备部署。按照本文档操作，可以在另一台电脑上重新安装环境、配置 DeepSeek API，并启动 CLI 或 Web UI 演示。

## 1. 项目简介

本项目是一个基于 DeepSeek API 的多 Agent 自动开发流水线演示系统。

用户输入需求后，系统会按顺序执行：

1. Product Agent：分析需求，拆解产品方案。
2. Coder Agent：根据方案生成 Python 代码。
3. Tester Agent：静态检查生成代码。
4. Code Runner：保存并运行生成代码。
5. Sentry Agent：分析运行错误。
6. Coder Agent：根据错误日志自动修复，最多修复 3 次。

系统提供两种演示入口：

- CLI 演示：适合答辩时展示完整流程和日志。
- Streamlit Web UI：适合比赛现场可视化展示。

## 2. 新设备部署前准备

### 2.1 推荐环境

- 操作系统：Windows 10/11
- Python：3.10 或以上版本
- 网络：在线模式需要访问 DeepSeek API
- 浏览器：Chrome、Edge 或其他现代浏览器

macOS 和 Linux 也可以运行，但 `start_demo.bat` 仅适用于 Windows。

### 2.2 需要准备的内容

- 项目完整代码文件夹
- DeepSeek API Key
- Python 安装包或已安装的 Python 环境
- 比赛现场备用方案：离线演示模式

不要把真实 `.env` 或 API Key 发给无关人员。

## 3. 将项目复制到新设备

### 方式一：U 盘或压缩包复制

1. 在原电脑上找到项目目录，例如：

```text
D:\AIchatProject
```

2. 压缩整个项目文件夹。
3. 将压缩包复制到新电脑。
4. 解压到固定目录，例如：

```text
D:\AIchatProject
```

5. 不建议复制原电脑的 `.venv` 虚拟环境，建议在新电脑重新创建。

### 方式二：Git 仓库拉取

如果项目已经上传到 Git 仓库，可以在新设备执行：

```powershell
git clone 仓库地址
cd AIchatProject
```

拉取后需要重新创建 `.env`，不要把真实 `.env` 提交到 Git。

## 4. 安装 Python

在新设备打开 PowerShell，检查 Python：

```powershell
python --version
```

如果提示找不到 Python，请安装 Python 3.10 或以上版本。

Windows 安装 Python 时建议勾选：

```text
Add python.exe to PATH
```

安装后重新打开 PowerShell，再次执行：

```powershell
python --version
```

## 5. 创建虚拟环境

进入项目目录：

```powershell
cd D:\AIchatProject
```

创建虚拟环境：

```powershell
python -m venv .venv
```

激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 禁止执行脚本，可以临时执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

看到命令行前面出现 `(.venv)`，说明虚拟环境已启用。

## 6. 安装项目依赖

推荐直接运行自动安装脚本：

```powershell
.\install.bat
```

也可以手动安装：

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

如果网络较慢，可以多执行一次安装命令。

安装后检查核心依赖：

```powershell
python -c "import openai, langchain, langgraph, rich, streamlit, dotenv, yaml; print('依赖安装成功')"
```

## 7. 配置环境变量

项目根目录已经提供 `.env.example`，新设备需要复制一份为 `.env`：

```powershell
copy .env.example .env
```

打开 `.env`，填写配置：

```text
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
OFFLINE_MODE=false
```

字段说明：

- `DEEPSEEK_API_KEY`：DeepSeek API Key。
- `DEEPSEEK_BASE_URL`：DeepSeek API 地址，默认 `https://api.deepseek.com`。
- `DEEPSEEK_MODEL`：模型名称，默认 `deepseek-chat`。
- `OFFLINE_MODE`：是否启用离线演示模式。

如需调整代码运行超时时间，可以额外加入：

```text
CODE_RUN_TIMEOUT=10
```

## 8. 在线模式与离线模式

### 在线模式

在线模式会真实调用 DeepSeek API：

```text
OFFLINE_MODE=false
```

适合网络稳定、API Key 可用的环境。

### 离线演示模式

如果比赛现场网络不稳定、API Key 不可用或调用失败，可以改为：

```text
OFFLINE_MODE=true
```

离线模式会使用 `offline_demo.py` 中的预置响应，仍然可以展示：

- Product Agent 分析
- Coder Agent 生成代码
- Tester Agent 静态检查
- Sentry Agent 自动修复
- 最终运行结果

即使没有手动开启离线模式，只要 DeepSeek API 调用失败，系统也会自动切换到预置演示响应。

## 9. 启动 CLI 演示

推荐使用 LangGraph CLI 演示：

```powershell
python graph_demo.py
```

启动后选择案例：

```text
1. 简单成功案例
2. 翻车修复案例
3. 综合案例
4. 自定义输入
```

建议比赛现场演示顺序：

1. 先选择简单成功案例，证明流程可以跑通。
2. 再选择翻车修复案例，展示自动修复闭环。
3. 最后选择综合案例，展示代码生成能力。

## 10. 启动 Web UI

本机访问：

```powershell
python -m streamlit run webui.py
```

浏览器打开：

```text
http://localhost:8501
```

Web UI 支持：

- 输入自定义需求
- 选择演示案例
- 查看 Agent 状态卡片
- 查看运行日志
- 查看 stdout、error_log、retry_count 和 success
- 查看生成的 Markdown 报告

## 11. 让其他设备访问 Web UI

如果希望评委或另一台电脑访问你的 Web UI，可以在演示电脑上启动局域网服务。

### 11.1 启动局域网访问

在演示电脑执行：

```powershell
python -m streamlit run webui.py --server.address 0.0.0.0 --server.port 8501
```

### 11.2 查询演示电脑 IP

在演示电脑执行：

```powershell
ipconfig
```

找到当前网络的 IPv4 地址，例如：

```text
192.168.1.23
```

### 11.3 其他设备访问

确保两台设备连接同一个 Wi-Fi 或局域网，然后在另一台设备浏览器输入：

```text
http://192.168.1.23:8501
```

如果无法访问，请检查：

- 两台设备是否在同一局域网。
- Windows 防火墙是否允许 Python 或 Streamlit 访问网络。
- 端口 `8501` 是否被占用。
- 是否使用了正确的 IPv4 地址。

## 12. Windows 一键启动

项目提供一键启动脚本：

```powershell
.\start_demo.bat
```

菜单选项：

```text
1. Start CLI Demo: python graph_demo.py
2. Start Web UI: python -m streamlit run webui.py
3. Exit
```

如果双击后窗口一闪而过，请在 PowerShell 中进入项目目录后手动运行：

```powershell
.\start_demo.bat
```

## 13. 生成文件说明

运行过程中会生成：

```text
output/generated_code.py
output/web_report.md
```

说明：

- `generated_code.py`：Coder Agent 生成并保存的 Python 代码。
- `web_report.md`：Web UI 生成的 Markdown 报告。

这些文件可以在演示后打开查看。

## 14. 安全限制说明

为了避免生成代码误删文件或执行危险命令，系统在运行代码前会做安全检查。

当前禁止：

- `os.remove`
- `shutil.rmtree`
- `subprocess`
- `eval`
- `exec`

如果生成代码包含这些操作，系统会显示“安全检查失败”，并阻止执行。

## 15. 部署验收清单

在新设备部署完成后，建议按下面顺序检查：

- [ ] `python --version` 可以正常显示 Python 版本。
- [ ] 虚拟环境 `.venv` 已创建并激活。
- [ ] 依赖安装成功。
- [ ] `.env` 已创建。
- [ ] `DEEPSEEK_API_KEY` 已填写，或 `OFFLINE_MODE=true` 已开启。
- [ ] `python graph_demo.py` 可以启动 CLI 菜单。
- [ ] 简单成功案例可以运行完成。
- [ ] 翻车修复案例可以触发自动修复。
- [ ] `python -m streamlit run webui.py` 可以打开 Web UI。
- [ ] 局域网访问地址可以在另一台设备打开。

## 16. 常见问题

### 找不到 Python

重新安装 Python，并确认勾选 `Add python.exe to PATH`。

### 无法激活虚拟环境

执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### No module named streamlit

执行：

```powershell
python -m pip install streamlit
```

或者直接重新安装全部依赖：

```powershell
python -m pip install -r requirements.txt
```

### No module named dotenv

执行：

```powershell
python -m pip install python-dotenv
```

### API Key 不可用

先检查 `.env` 中的 `DEEPSEEK_API_KEY` 是否填写正确。

如果比赛现场急需继续演示，设置：

```text
OFFLINE_MODE=true
```

### 端口 8501 被占用

换一个端口启动：

```powershell
python -m streamlit run webui.py --server.port 8502
```

### 其他设备打不开 Web UI

检查演示电脑 IP、防火墙、Wi-Fi 网络和 Streamlit 启动参数。

推荐启动方式：

```powershell
python -m streamlit run webui.py --server.address 0.0.0.0 --server.port 8501
```

## 17. 比赛现场推荐流程

1. 提前 30 分钟打开电脑，连接网络。
2. 进入项目目录，激活虚拟环境。
3. 检查 `.env` 配置。
4. 先运行 `python graph_demo.py` 测试 CLI。
5. 再运行 `python -m streamlit run webui.py` 测试 Web UI。
6. 如果网络不稳定，立刻开启 `OFFLINE_MODE=true`。
7. 演示时先跑简单案例，再跑翻车修复案例。
8. 最后展示 Web UI、Markdown 报告和答辩材料。
