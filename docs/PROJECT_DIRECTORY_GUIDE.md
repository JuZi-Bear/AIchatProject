# 项目目录指南

本文用于说明当前 v2-only 项目目录结构和目录职责。目录树省略了 `.venv/`、`node_modules/`、`target/`、`build/`、`dist/`、缓存目录等大型或生成目录。

## 目录树

```text
AIchatProject/
├─ agents/                  shared-core，Agent 模块说明与后续拆分预留目录
├─ backend-java/            v2-platform，Spring Boot 平台服务层
│  ├─ src/main/java/        Java 控制器、服务、实体、仓库和配置
│  ├─ src/main/resources/   application.yml 等配置
│  ├─ Dockerfile
│  └─ pom.xml
├─ config/                  shared-core，模型、插件和运行配置
├─ core/                    shared-core，LangGraph 状态和工作流
├─ docs/                    documentation，架构、API、Docker、演示和协作文档
├─ figma/                   experimental，设计链接和设计协作资料
├─ frontend-vue/            v2-platform，Vue3 + TypeScript 前端
│  ├─ src/api/              API 客户端封装
│  ├─ src/components/       Vue 展示组件
│  ├─ src/stores/           Pinia 状态
│  ├─ src/types/            TypeScript 类型
│  ├─ src/views/            页面视图
│  ├─ Dockerfile
│  └─ nginx.conf
├─ output/                  generated-output，生成代码和临时输出
├─ plugins/                 shared-core，Doc/Security/Refactor/UI 等插件
├─ reports/                 generated-output，Markdown 报告
├─ runner-cpp/              experimental，C++ Runner Sandbox 最小版本
├─ runs/                    generated-output，运行历史 JSON
├─ schemas/                 v2-platform，FastAPI 请求响应模型
├─ services/                v2-platform，API 服务层业务适配
├─ tests/                   shared-core，Python 测试
├─ utils/                   shared-core，Runner、摘要、历史、UI 状态等工具
├─ api_server.py            v2-platform，Python FastAPI Agent Engine
├─ docker-compose.yml       v2-platform，多服务编排
└─ README.md                documentation，项目入口说明
```

## 分类说明

| 分类 | 含义 |
| --- | --- |
| `v2-platform` | 平台化升级链路，包含 API、Vue、Java、MySQL、Docker 等 |
| `shared-core` | v2 Agent 核心、插件、配置和工具 |
| `experimental` | 预研或增强模块，不能默认替代稳定链路 |
| `generated-output` | 运行产物、报告和历史数据，不应作为核心源码编辑 |
| `documentation` | 项目说明、答辩、操作和协作文档 |

## 重点目录说明

### frontend-vue/：v2-platform

Vue3 + TypeScript 前端，用于展示 Dashboard、运行控制台、历史记录、报告、模型和插件配置。开发模式读取 `.env.development`，生产构建读取 `.env.production` 或 Docker build args。

### backend-java/：v2-platform

Spring Boot 平台服务层，当前承担 Java Gateway、MySQL 任务记录、报告索引、平台统计、前端配置、模型配置和插件配置管理。它不替代 Python Agent Engine。

### runner-cpp/：experimental

C++ Runner Sandbox 最小版本。当前作为可选增强模块存在，默认不替代 Python Runner。只有在 `config/settings.yaml` 设置 `runner_mode: cpp` 且可执行文件存在时才尝试使用。

### agents/：shared-core

当前作为 Agent 模块拆分预留和说明目录。现有主实现仍在顶层 `agents.py` 与 `core/workflow.py` 中，整理阶段不移动它们。

### plugins/：shared-core

插件系统实现目录，包含 Doc Agent、Security Agent、Refactor Agent、UI Agent 等插件。v2 运行摘要、报告和 Vue 页面依赖插件结果展示。

### utils/：shared-core

工具函数目录，包含代码执行、C++ Runner 适配、历史存储、摘要构建、UI ViewModel 构建等。修改时要同时考虑 FastAPI、Java、Vue、Replay 和报告展示链路。

### reports/：generated-output

Markdown 报告输出目录。Java MySQL 会保存报告索引，但报告正文仍可能来自该目录。

### runs/：generated-output

Python 运行历史 JSON 目录。Python Direct 调试和部分报告查询仍可依赖该目录读取历史。

### output/：generated-output

生成代码、测试结果和临时输出目录。不要把这里的产物当作核心源码维护。

### docs/：documentation

文档总目录。优先从 `docs/DOCUMENT_INDEX.md` 进入，避免 README 继续膨胀。
