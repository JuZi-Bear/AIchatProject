# 代码健康检查与最小清理报告

本文记录“双轨并行架构收敛整理阶段”的代码健康检查结果。本轮只做低风险文档和忽略规则整理，不删除核心功能，不改变业务逻辑。

## 检查范围

- 核心入口：CLI、Streamlit、FastAPI、Vue、Java、C++ Runner、Docker、Windows 脚本。
- 配置文件：环境变量示例、Python yaml、Vue env、Java application.yml、Docker Compose。
- 文档一致性：README 与 docs 中的启动命令、服务名、端口和访问地址。
- 冗余和临时文件：`test_*.py`、`demo_*.py`、`*_old.py`、`*_backup.py`、temp/draft/backup 命名。
- 前后端接口一致性：FastAPI、Java Controller、Vue API client。
- `.gitignore`：运行产物、构建产物、缓存和敏感文件忽略规则。

## 核心入口检查

| 入口 | 当前状态 | 判断 |
| --- | --- | --- |
| `graph_demo.py` | 存在 | v1 CLI 演示入口，保留 |
| `webui.py` | 存在 | v1 Streamlit 演示入口，保留 |
| `api_server.py` | 存在 | v2 Python FastAPI Agent Engine，保留 |
| `frontend-vue/` | 存在 | v2 Vue 前端，保留 |
| `backend-java/` | 存在 | v2 Java 平台服务层，保留 |
| `runner-cpp/` | 存在 | C++ Runner Sandbox 预研模块，保留 |
| `docker-compose.yml` | 存在 | v2 多服务编排，保留 |
| `start_demo.bat` | 存在 | Windows v1 快速启动脚本，保留 |
| `install.bat` | 存在 | Windows 依赖安装脚本，保留 |

## 重复文件检查

扫描到的可能被误判为临时文件的文件：

| 文件 | 判断 | 建议 |
| --- | --- | --- |
| `demo_cases.py` | 正常演示案例文件 | 保留 |
| `plugins/plugin_template.py` | 正常插件模板文件，包含 template 命名 | 保留 |
| `utils/test_runner.py` | 正常测试运行工具 | 保留 |
| `tests/test_generated_code.py` | 生成测试/测试样例文件，已在 `.gitignore` 中忽略后续变化 | 是否继续跟踪需用户确认 |
| `docs/PROMPTS.md` | 0 字节空文档 | 建议后续确认是否作为提示词归档入口保留 |

未发现明显的 `*_old.py`、`*_backup.py`、`.bak`、`draft` 草稿代码文件。

## 废弃代码检查

本轮未发现可以直接删除的废弃核心代码。存在一些早期文档或可合并文档：

- `docs/ARCHITECTURE.md`：内容很短，建议后续并入 `DUAL_TRACK_ARCHITECTURE.md`。
- `docs/DELIVERY_STRUCTURE.md`：与 `PROJECT_DIRECTORY_GUIDE.md` 有重叠，建议后续标记为交付历史文档。
- `docs/RISK_AND_SOLUTION.md`：与 `RISK_AND_STABILITY.md` 有重叠，建议后续合并。
- `docs/USER_MANUAL.md` 与 `docs/OPERATION_GUIDE.md`：启动和部署说明有重复，建议后续一个面向用户、一个面向维护者。

本阶段不删除这些文件，只在 `DOCUMENT_INDEX.md` 中标记主文档和建议合并项。

## 命名一致性检查

- 当前 Docker Compose 服务名统一为：`mysql`、`ai-agent-api`、`backend-java`、`frontend-vue`、`streamlit-web`。
- 历史文档中的旧服务名 `ai-agent-pipeline` 已修正为当前多服务口径；`DOCKER_COMPOSE_GUIDE.md` 中只作为旧容器残留示例提及。
- Vue API 模式命名统一为 `Python Direct` 和 `Java Gateway`。
- 目录分类统一使用：`v1-demo`、`v2-platform`、`shared-core`、`experimental`、`generated-output`、`documentation`。

## 配置文件检查

| 文件 | 结论 |
| --- | --- |
| `.env.example` | Python 本地环境示例，包含模型 Key、默认模型、离线模式 |
| `.env.docker.example` | Docker 环境示例，额外包含 `MYSQL_ROOT_PASSWORD` 和 `MYSQL_DATABASE` |
| `config/settings.yaml` | 默认 `runner_mode: python`，符合 C++ Runner 可选增强定位 |
| `config/models.yaml` | DeepSeek 默认启用，Qwen/GLM 默认关闭，模型 env_key 与环境变量示例一致 |
| `config/agents.yaml` | Doc/Security/Refactor/UI 插件均启用 |
| `frontend-vue/.env.development` | 默认 `VITE_API_MODE=python`，Python API 为 `127.0.0.1:8001`，Java 为 `127.0.0.1:8088/api` |
| `frontend-vue/.env.production` | 默认 `VITE_API_MODE=java`，Java API 为 `localhost:8088/api`，Python API 为 `localhost:8001` |
| `backend-java/src/main/resources/application.yml` | 本地 Java 端口 `8088`，默认 Python Agent 为 `127.0.0.1:8001`，MySQL 为 `localhost:3306/aichat_platform` |
| `docker-compose.yml` | Docker 中 Java 调 Python 使用 `http://ai-agent-api:8001`，MySQL 使用 `mysql:3306`，端口映射一致 |

未发现端口冲突类配置错误。需要注意：本地 MySQL 默认密码仍是占位值 `your_password`，Docker 模式默认使用 `root`，这是本地和容器环境差异，不属于冲突。

## 启动脚本检查

- `install.bat`：创建 `.venv`，安装 `requirements.txt`，仍适合 v1 Python 环境安装。
- `start_demo.bat`：提供 CLI Demo 和 Streamlit Web UI 两个入口，仍适合 v1 比赛演示。
- 当前没有重复 Windows 启动脚本。
- v2 Vue/Java/Docker 启动命令集中在 README 和 docs 中，不建议再新增批处理脚本，避免入口过多。

## Docker 文件检查

- 根 `Dockerfile` 同时支持 Streamlit 和 FastAPI，通过 Compose command 区分启动命令。
- `frontend-vue/Dockerfile` 使用 Node 构建、Nginx 运行，支持生产构建参数。
- `backend-java/Dockerfile` 使用 Maven + Java 17 构建运行。
- `docker-compose.yml` 已包含 `mysql`、`ai-agent-api`、`backend-java`、`frontend-vue`、`streamlit-web`。
- C++ Runner 当前按方案 A 作为挂载目录，不作为独立 Compose 服务。

## 前后端接口一致性检查

- FastAPI 路径：`/health`、`/models`、`/plugins`、`/runs`、`/runs/{run_id}`、`/reports`、`/reports/{report_name}`。
- Java Gateway base URL：`/api`。
- Java health 代理：`/api/agent/health`。
- Java 代理接口：`/api/models`、`/api/plugins`、`/api/runs`、`/api/reports`。
- Java 平台接口：`/api/platform/runs`、`/api/platform/reports`、`/api/platform/stats`、`/api/settings`。
- Vue `src/api/client.ts` 已集中处理 health 路径差异：Python 用 `/health`，Java 用 `/agent/health`。
- Vue reports/history/settings 在 Java 模式下使用平台接口，在 Python 模式下保持 Python Direct。

未发现需要修改 API 返回结构的问题。

## 风险项列表

- `tests/test_generated_code.py` 看起来像生成文件，但当前已存在于项目中。是否继续跟踪需要用户确认。
- `docs/PROMPTS.md` 是空文档，后续可作为提示词归档入口，也可确认后删除。
- 文档体系中仍有重复说明，尤其是启动、Docker、风险和目录结构说明。
- `webui.py` 文件较大，后续如果继续优化，应只做展示层小步拆分，不应重写。
- C++ Runner 当前不是完整安全沙箱，不能默认启用为生产 Runner。
- Docker Compose 启动依赖端口 `3306`、`8001`、`8088`、`5174`、`8501`，比赛现场需要提前检查端口。

## 建议清理项

低风险、可后续执行：

- 将 `docs/ARCHITECTURE.md` 合并到 `DUAL_TRACK_ARCHITECTURE.md` 后标记归档。
- 将 `docs/DELIVERY_STRUCTURE.md` 的目录说明收敛到 `PROJECT_DIRECTORY_GUIDE.md`。
- 将 `docs/RISK_AND_SOLUTION.md` 合并到 `RISK_AND_STABILITY.md`。
- 明确 `docs/PROMPTS.md` 是否用于提示词归档。
- 确认 `tests/test_generated_code.py` 是否应作为生成产物从 Git 跟踪中移除。

本阶段已完成的低风险清理：

- 补充健康检查、维护指南和安全变更清单。
- 统一旧 Docker 服务名文档口径。
- 补齐 `.gitignore` 中运行产物、构建产物、日志和缓存规则。
