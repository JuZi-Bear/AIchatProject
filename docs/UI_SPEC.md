# v2-only UI Spec

当前 UI 以 Vue 前端为准，风格方向是 Google Material + Figma 风编辑器。

## 页面

- Dashboard：平台总览。
- RunConsole：任务执行与 CodeAgent 结果。
- Workflow Editor：无限画布、浮动 Palette、右侧属性浮层。
- Workflow Templates：模板中心。
- Replay：事件回放。
- History：平台运行记录。
- Reports：报告中心。
- Agents：Agent 注册中心。
- Models / Plugins：配置查看与前端配置。

## Workflow Editor

- 主体是无限画布。
- 左侧浮动 Palette 提供 Agent 和分支节点。
- 点击节点才显示属性面板。
- 连接线与画布同层缩放和平移。
- 后续可加小地图、多选、框选和快捷键提示。

## 状态颜色

- 成功：绿色。
- 失败：红色。
- 运行中：蓝色。
- 修复或警告：黄色。
- 等待：灰色。
