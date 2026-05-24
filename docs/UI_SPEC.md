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
- 右下角小地图显示节点分布和当前视口，可点击或拖动快速移动视角。
- 支持 `Ctrl/Cmd + 点击` 多选节点，支持空白区域拖拽框选。
- 多选后显示批量操作浮层，可整理选中、删除选中或取消选择。
- 后续可加手动连线编辑、小地图缩放细节和快捷键提示。

## Replay

- 支持按 Agent、状态和关键字筛选事件。
- 提供“只看 CodeAgent”快捷按钮。
- CodeAgent 事件使用黄色高亮，安全阻断或失败事件使用红色强调。
- 自动播放基于筛选后的事件列表运行。

## Dashboard

- Java Gateway 模式展示“最近 CodeAgent 操作”卡片。
- 卡片显示最近运行、最近事件、阻断/异常状态、事件时间，并提供 History / Replay 跳转。
- Python Direct 模式显示轻提示，不展示 Java 平台事件卡片。

## 状态颜色

- 成功：绿色。
- 失败：红色。
- 运行中：蓝色。
- 修复或警告：黄色。
- 等待：灰色。
