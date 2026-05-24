# v2-only Plugin Guide

插件系统由 Python Agent Engine 负责执行，Vue 和 Java 负责展示与配置。

## 当前插件

- Doc Agent
- Security Agent
- Refactor Agent
- UI Agent

## 配置

```yaml
# config/agents.yaml
plugins:
  doc_agent:
    enabled: true
  security_agent:
    enabled: true
  refactor_agent:
    enabled: true
  ui_agent:
    enabled: true
```

## v2 展示

- Vue Plugins 页面展示插件配置。
- RunConsole 显示插件输出。
- Java + MySQL 可保存平台配置。
- Reports 页面展示插件结果摘要。

## 修改原则

- 不改变插件统一输出字段。
- 不在插件中写真实 API Key。
- 插件输出应能被 `ui_view_model` 消费。
