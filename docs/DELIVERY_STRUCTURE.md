# v2-only Delivery Structure

当前交付结构围绕 v2 平台主链路组织。

```text
frontend-vue/     Vue3 + TypeScript 前端
backend-java/     Java Spring Boot 平台服务
api_server.py     FastAPI Python Agent Engine
services/         Python API 业务服务
core/             LangGraph 工作流核心
agent_registry/   Agent 元信息注册
workflow_templates/ Workflow 模板
plugins/          插件 Agent
utils/            共享工具与 CodeAgent
runner-cpp/       可选 C++ Runner
config/           模型、插件、运行配置
docs/             文档中心
docker-compose.yml v2 多服务编排
```

生成产物：

- `reports/`
- `runs/`
- `output/`

启动与验收见 `README.md`、`docs/STARTUP_ORDER.md`、`docs/FINAL_CHECKLIST.md`。
