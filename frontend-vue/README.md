# frontend-vue

## 目录作用

`frontend-vue/` 是 v2.0 平台化升级轨的 Vue3 + TypeScript 前端项目，用于逐步替代 Streamlit 的平台展示能力。它支持 Dashboard、运行控制台、历史记录、报告、模型配置、插件配置和演示模式。

## 核心文件

- `src/api/`：Axios API 封装，负责 Python Direct / Java Gateway 模式差异。
- `src/views/`：页面视图，例如 Dashboard、RunConsole、RunHistory、Reports、Models、Plugins。
- `src/components/`：工作流、结果、报告、Dashboard 和演示组件。
- `src/stores/settings.ts`：Pinia 设置存储，支持 localStorage 和 Java settings。
- `src/types/`：TypeScript 类型定义。
- `.env.development`、`.env.production`：API 模式和地址配置。
- `Dockerfile`、`nginx.conf`：生产构建和 Nginx 部署配置。

## 不能随便修改

- 不要在页面组件中硬编码 Python / Java 路径判断，路径差异应集中在 `src/api/`。
- 不要删除 Python Direct 模式。
- 不要删除 Java Gateway 模式。
- 不要改变 `run_summary` 和 `ui_view_model` 的前端兼容展示。
- 不要把 API Key 写入前端代码。

## 轨道归属

v2-platform。

## 当前开发状态

active。
