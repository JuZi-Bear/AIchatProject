# AI Multi-Agent Pipeline

AI Multi-Agent Pipeline 是一个 v2-only 的 AI 多智能体开发平台演示版。当前主链路为：

```text
Vue3 + TypeScript
  -> Java Spring Boot Platform API
  -> Python FastAPI Agent Engine
  -> LangGraph / Agent / CodeAgent
  -> MySQL / RunEvent / SSE / Replay
```

本版本已经移除旧 Python UI / CLI 入口，项目默认只维护 v2 平台化演示链路。

## 核心能力

- 多 Agent 工作流：Product、Coder、Tester、Runner、Sentry、Quality、Report 等节点协作。
- Java 平台层：任务记录、配置管理、报告索引、平台统计、RunEvent 事件记录。
- MySQL 持久化：保存运行记录、事件、配置、Workflow 模板和报告索引。
- SSE 实时事件：Java Gateway 向 Vue 推送任务事件，支持实时日志体验。
- Workflow Replay：基于 MySQL RunEvent 逐步回放一次历史运行。
- Agent 注册中心：Python 管理 Agent 元信息，Vue `/agents` 展示注册表。
- Prompt 模板：主要 Agent Prompt 存放在 `prompts/`。
- Workflow 模板：内置模板 + Java/MySQL 自定义模板保存、版本、删除和实例化。
- Workflow Editor：Google Material 风演示编辑器，支持模板保存、手动连线、自定义 Agent 节点和 Human Approval 节点。
- Dynamic LangGraph Runtime v1：Workflow Editor 模板可经 Python 校验后编译为受控 LangGraph 执行图，支持安全条件分支、有上限循环、暂停和恢复。
- Workflow Skill Export：Java MySQL 模板可导出为本地 Codex Skill 包，包含 `SKILL.md`、模板 JSON 和平台 API 调用脚本。
- CodeAgent：受控执行单文件和文件夹工作区操作，支持模板填充、dry-run diff、备份、JSONL 审计日志和 RunEvent。
- Project Workspace：Java Gateway + MySQL 保存受控工作区，CodeAgent 文件夹模式可选择默认工作区并展示安全摘要。
- 平台人工确认：Java Gateway 可记录 `WAITING_FOR_HUMAN`、批准/拒绝事件，并在 Replay 中展示。
- 模型密钥管理：Java Gateway 模式下 Models 页面可更新平台层 API Key 状态，GET 接口只返回 masked 信息，不返回明文。
- C++ Runner Sandbox：可选安全执行增强，默认仍保留 Python Runner fallback。
- Figma-first UI：`figma/` 保存设计 token、页面映射和组件清单。

## 技术栈

- Frontend：Vue3、TypeScript、Vite、Element Plus、Pinia、Axios、Vue Router。
- Platform：Java 17、Spring Boot 3、Maven、Spring Data JPA。
- Agent Engine：Python 3.11、FastAPI、LangGraph。
- Persistence：MySQL 8.0。
- Runtime：Docker Compose、Nginx、Uvicorn。
- Experimental：C++17、CMake Runner Sandbox。

## 快速启动

### Docker Compose

```powershell
docker compose up --build
```

默认服务：

| 服务 | 地址 |
| --- | --- |
| Vue 前端 | http://127.0.0.1:5174 |
| Java Gateway | http://127.0.0.1:8088/api/health |
| FastAPI Docs | http://127.0.0.1:8001/docs |
| MySQL | `127.0.0.1:${MYSQL_HOST_PORT:-3306}` |

如果本机 `3306` 被占用：

```powershell
$env:MYSQL_HOST_PORT="3307"
docker compose up --build
```

### 本地联调

```powershell
.\scripts\start_v2_local.ps1
```

停止：

```powershell
.\scripts\stop_v2_local.ps1
```

### 手动启动

终端 1：Python Agent Engine

```powershell
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
```

终端 2：Java Gateway

```powershell
cd backend-java
mvn spring-boot:run
```

终端 3：Vue

```powershell
cd frontend-vue
npm install
npm run dev
```

## 常用页面

- Dashboard: http://127.0.0.1:5174/
- Run Console: http://127.0.0.1:5174/runs/new
- History: http://127.0.0.1:5174/history
- Reports: http://127.0.0.1:5174/reports
- Agents: http://127.0.0.1:5174/agents
- Workflow Templates: http://127.0.0.1:5174/workflows/templates
- Workflow Editor: http://127.0.0.1:5174/workflows/editor

## 验收命令

```powershell
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
.\scripts\smoke_workflow_template.ps1
.\scripts\smoke_workflow_runtime_lite.ps1
.\scripts\smoke_skill_export.ps1 -RunExportedScript
.\scripts\smoke_dynamic_runtime_context.ps1
.\scripts\final_v2_acceptance.ps1
```

前端构建：

```powershell
cd frontend-vue
npm run build
```

Java 构建：

```powershell
cd backend-java
mvn -DskipTests package
```

Skill Export 验收：

```powershell
.\scripts\smoke_skill_export.ps1 -RunExportedScript
```

该命令会创建临时 Workflow 模板、导出 Skill 包、校验 `SKILL.md` / `workflow-template.json` / `run_workflow.py`，并通过导出的脚本调用 Java Gateway 的 Dynamic LangGraph 执行接口。导出的 Skill 目录会保留在 `generated-skills/` 或本地 Java 工作目录下的 `backend-java/generated-skills/`，临时模板默认会清理。

## 项目结构

```text
frontend-vue/       Vue3 + TypeScript 平台前端
backend-java/       Java Spring Boot 平台服务层
api_server.py       Python FastAPI Agent Engine 入口
services/           Python API 服务层
core/               LangGraph 工作流核心
agents.py           Agent 实现
agent_registry/     Agent 元信息注册中心
prompts/            Prompt Markdown 模板
workflow_templates/ Workflow 模板
plugins/            插件系统
utils/              Runner、事件、报告、CodeAgent 工具
config/             Python yaml 配置
runner-cpp/         C++ Runner Sandbox
scripts/            v2 启动、smoke 和验收脚本
generated-skills/   Workflow 模板导出的 Codex Skill 运行产物
docs/               架构、运维、API、验收和答辩文档
figma/              Figma-first UI 设计源规范
```

## 关键文档

- `docs/V2_ONLY_RUNTIME_SIMPLIFICATION.md`：v2-only 主链路说明。
- `docs/API_CONTRACT.md`：Python / Java / Platform API 契约。
- `docs/DOCKER_COMPOSE_GUIDE.md`：Docker Compose 启动指南。
- `docs/OPERATION_GUIDE.md`：v2 运维与演示操作手册。
- `docs/V2_DEMO_RELEASE_NOTES.md`：v2 演示版发布说明。
- `docs/FIGMA_UI_WORKFLOW.md`：Figma-first UI 工作流。
- `docs/CODEX_PROJECT_CONTEXT.md`：Codex 协作上下文。
- `docs/SKILL_EXPORT_DEMO_GUIDE.md`：Workflow Template 导出 Codex Skill 演示和验收指南。

## 最新扩展

- CodeAgent 文件夹模式新增工作流模板选择，可一键填充工作区、include/exclude、输出文件、dry-run 和备份策略。
- Workspace 页面新增受控工作区管理，可保存默认文件夹、读取限制、dry-run 和备份策略；Python CodeAgent 仍做最终白名单裁判。
- Workflow Editor 新增 `Human Approval` 和 `Custom Agent` 节点；第一阶段用于模板、回放和人工确认事件，不动态改写 LangGraph。
- Java 新增 `POST /api/platform/runs/{platformRunId}/approval`，用于批准或拒绝等待人工确认的任务。
- Java 新增 `GET/POST/DELETE /api/platform/secrets/models`，用于平台层模型 API Key 状态管理和加密保存。
- Java 新增 Workflow Runtime Lite：`POST /api/platform/workflows/templates/{templateKey}/execute` 可按 MySQL 模板节点顺序执行平台演示链路，CodeAgent 节点真实执行，Report 节点生成 Markdown 演示报告，其它 Agent 节点写入可回放事件。
- Python 新增 Dynamic LangGraph Runtime v1：`POST /api/workflows/dynamic/validate`、`POST /api/workflows/dynamic/execute` 和 `POST /api/workflows/dynamic/runs/{run_id}/resume` 可校验、执行和恢复受控模板图。
- Java Gateway 新增 Dynamic LangGraph 代理：`POST /api/platform/workflows/templates/{templateKey}/validate-langgraph`、`POST /api/platform/workflows/templates/{templateKey}/execute-langgraph` 和 `POST /api/platform/workflows/runs/{platformRunId}/resume`。
- Java Gateway 新增 Workflow Skill Export：`POST /api/platform/workflows/templates/{templateKey}/export-skill` 将 MySQL 模板导出到 `generated-skills/<skill-name>/`，但不会自动安装。

## 当前限制

- Workflow Runtime Lite 是平台层演示执行器，不等于动态 LangGraph Runtime；Product / Coder / Tester 等节点第一版作为 `simulated` 事件，CodeAgent 和 Report 节点为 `executed`，Human Approval 节点为 `waiting`。
- Dynamic LangGraph Runtime v1 是受控执行路径，不替换固定 `/runs` 主流程；条件表达式必须走白名单解析，循环必须有 `maxIterations`，暂停/恢复使用平台保存的动态 state。
- Workflow Editor 当前可生成平台模板、Runtime Lite 演示链路、Dynamic LangGraph 执行图和可回放任务视图；前端字段级连线会进入模板和回放展示，但真实字段值传递仍是后续 `Dynamic Workflow Runtime` 深化方向。
- Workflow Skill Export 只导出本地 Skill 目录，不自动安装到 `~/.codex/skills`；导出的脚本只调用 Java Gateway，不直接绕过平台安全边界。
- 自定义 Agent 节点当前保存到模板 JSON，不会自动注册到 Python Agent Registry。
- 前端 API Key 管理仅 Java Gateway 模式可用；Python Direct 模式仍建议使用 `.env`。
- CodeAgent 是简化文件操作模块，不是完整 Codex。
- C++ Runner Sandbox 是可选增强，不默认替代 Python Runner。
- 用户系统、权限系统、团队协作和任务队列暂未启用。

## 推荐下一步

优先推进 Skill 自动安装 / 启用流程：

1. 让导出的 `generated-skills/<skill-name>/` 可一键复制到 Codex skills 目录。
2. 只安装用户确认的 Skill，不自动覆盖同名目录。
3. 在 Vue 中展示安装状态、目标路径和安全提示。
4. 保持 Skill 脚本只调用 Java Gateway，不绕过平台安全边界。
5. 暂缓用户系统、权限和团队协作。
