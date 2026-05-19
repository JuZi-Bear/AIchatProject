# v2.0 三分钟平台演示脚本

本文用于比赛现场或录屏时快速展示 v2.0 平台化能力。目标不是完整讲完所有技术细节，而是在 3 分钟内证明：

- Vue 前端可以作为平台控制台。
- Java Gateway + MySQL 可以记录平台运行数据。
- Python Agent Engine 仍负责 AI 工作流执行。
- CodeAgent 文件操作、SSE 事件、审计日志和 Replay 能形成闭环。
- Workflow 模板可以生成可回放任务视图。

## 演示前准备

进入项目目录：

```powershell
cd D:\AIchatProject
```

启动 v2 本地联调链路：

```powershell
.\scripts\start_v2_local.ps1
```

生成演示数据：

```powershell
.\scripts\seed_v2_demo_data.ps1
```

打开页面：

```text
http://127.0.0.1:5174/
```

如果已经有足够数据，也可以跳过生成脚本，直接从 Dashboard 开始讲。

## 三分钟演示流程

### 0:00 - 0:25 项目定位

打开 Vue Dashboard。

讲解：

```text
这是一个 AI 多智能体自主开发流水线。v1.0 保留 Streamlit 做稳定比赛演示，v2.0 则升级为 Vue、Java、MySQL、FastAPI 的平台化架构。
```

指向页面：

- API 模式：Java Gateway + MySQL
- 运行统计
- 最近运行
- 最近事件
- 模型和插件状态

### 0:25 - 0:55 一键生成平台数据

展示刚才执行的命令输出，或说明脚本做了三件事：

```text
这个脚本自动生成三类记录：真实 Agent 工作流运行、CodeAgent 文件操作、Workflow 模板回放任务。
```

重点讲：

- Agent 运行证明 Python Agent Engine 仍可执行真实工作流。
- CodeAgent 运行证明平台可以执行受控文件操作。
- 模板回放证明 Workflow Editor 的模板可以进入平台记录和 Replay。

### 0:55 - 1:30 History 查看三类任务

打开：

```text
http://127.0.0.1:5174/history
```

讲解：

```text
History 里会把任务区分为普通 Agent 运行、CodeAgent 文件操作和模板回放。它们都进入 Java 平台记录，并保存到 MySQL。
```

现场操作：

1. 点击一条 Agent 运行，展示 Summary、Workflow、Agent 输出。
2. 点击一条 CodeAgent 运行，展示文件操作事件和审计信息。
3. 点击一条模板回放任务，准备进入 Replay。

### 1:30 - 2:05 CodeAgent 闭环

在 History 或 RunConsole 中展示 CodeAgent 记录。

讲解：

```text
CodeAgent 不是完整 Codex，它只执行 read_file、write_file、list_files 三类受控操作。路径由白名单和阻断路径限制，每次操作都会生成事件，并写入 JSONL 审计日志。
```

强调闭环：

```text
拖拽或触发节点之后，文件会被生成或修改，Java 会保存 RunEvent，SSE 可以实时推送给 Vue，之后还能在 Replay 中回放。
```

如果需要现场触发，可打开：

```text
http://127.0.0.1:5174/runs/new
```

使用 CodeAgent 面板执行一次 `write_file`。

### 2:05 - 2:40 Workflow Replay

打开一条模板回放链接：

```text
http://127.0.0.1:5174/replay/{platformRunId}
```

讲解：

```text
Replay 不是简单日志列表，而是按事件顺序展示 Product、Coder、CodeAgent、Quality、Report 等节点的执行轨迹。它可以用于比赛展示、问题复盘和后续平台审计。
```

现场操作：

- 点击自动播放。
- 暂停在 CodeAgent 节点。
- 展示当前事件高亮。
- 展示 detailJson 折叠信息。

### 2:40 - 3:00 收尾

讲解：

```text
这个项目目前采用双轨并行：v1.0 保证比赛现场稳定，v2.0 展示平台化升级能力。AI 工作流不直接耦合前端和 Java，平台层通过 API、事件、MySQL 和 Replay 把执行过程变成可观察、可追溯、可演示的工程系统。
```

## 推荐展示顺序

1. Dashboard：看平台总览和数据状态。
2. History：看三类任务记录。
3. CodeAgent：看文件操作、审计和事件。
4. Replay：看工作流回放。
5. Workflow Editor：补充说明可视化编排和模板保存。

## 现场兜底

如果 Vue 页面打不开：

```powershell
.\scripts\start_v2_local.ps1
```

如果 Java 服务异常：

```powershell
cd backend-java
mvn spring-boot:run -Dspring-boot.run.profiles=local
```

如果只想展示稳定演示：

```powershell
python -m streamlit run webui.py
```

如果演示数据不足：

```powershell
.\scripts\seed_v2_demo_data.ps1
```

如果只生成 CodeAgent 数据：

```powershell
.\scripts\seed_v2_demo_data.ps1 -SkipAgentRun -SkipWorkflowTemplate
```

## 讲解关键词

- 双轨并行：v1 稳定演示，v2 平台升级。
- 解耦：Vue / Java / Python 通过 API 和事件连接。
- 可观察：RunEvent、SSE、Replay。
- 可追溯：MySQL 任务记录和 JSONL 审计日志。
- 可扩展：Agent Registry、Prompt 模板、Workflow 模板、CodeAgent 节点。

## 不建议现场做的事

- 不现场改 LangGraph 主流程。
- 不现场改数据库表结构。
- 不现场配置复杂用户系统或权限系统。
- 不把 C++ Runner 替代 Python Runner。
- 不删除 Streamlit v1 演示轨。
