# 技术框架扩展边界

本文定义技术框架扩展时哪些模块可以优先扩展，哪些模块需要谨慎，哪些模块暂时不要大改。

## 可以扩展的模块

| 模块 | 可扩展方向 |
| --- | --- |
| `backend-java/` | 任务生命周期、配置中心、平台统计、报告索引、统一错误响应 |
| `frontend-vue/` | 工作台、报告中心、模型配置、插件配置、运行统计展示 |
| `api_server.py` | 轻量 API 适配、兼容新增只读接口 |
| `services/` | API 服务层业务适配、运行记录读取、配置读取封装 |
| `config/` | yaml 配置模板、Prompt 模板、模型 Provider 配置 |
| `docs/` | 架构规划、接口契约、测试清单、维护规范 |
| `docker-compose.yml` | 服务编排增强、环境变量和 volume 配置，服务结构变更需谨慎 |

## 需要谨慎扩展的模块

| 模块 | 谨慎原因 |
| --- | --- |
| `core/` | 承载 LangGraph 状态和工作流，影响 v1/v2 主流程 |
| `agents/` / `agents.py` | Agent 行为和输出直接影响演示效果 |
| `plugins/` | 插件执行协议影响报告和前端展示 |
| `utils/code_runner.py` | 代码执行路径高风险，必须保留 fallback |
| `graph_demo.py` | v1 CLI 演示入口 |
| `webui.py` | v1 Streamlit 稳定演示入口 |

## 暂时不要大改的模块和协议

- LangGraph 主流程。
- Agent 核心 prompt。
- 插件执行协议。
- 报告生成核心逻辑。
- `run_summary` 数据结构。
- `ui_view_model` 数据结构。

这些内容可以兼容扩展字段，但不应删除字段或改变现有语义。

## 扩展规则

- v1.0 不因 v2.0 扩展而失效。
- Python Direct 不因 Java Gateway 而失效。
- MySQL 不替代 yaml，除非用户确认。
- C++ Runner 不替代 Python Runner，除非用户确认。
- Vue 不删除 Streamlit，除非用户确认。
- Java 不直接承载 LangGraph 主流程。
- Docker Compose 服务结构变更需要先更新文档和测试清单。
- 涉及核心协议的变更必须先更新 `API_CONTRACT.md` 和 `CODEX_PROJECT_CONTEXT.md`。
