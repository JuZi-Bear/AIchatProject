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
- 支持手动连线：从节点右侧输出点拖到另一个节点左侧输入点创建连接。
- 连接线起终点停在节点外侧，避免被节点卡片遮挡。
- 连接线采用类似 React Flow / Blueprint / Node-RED 的 Bezier noodle 曲线，并使用白色托底描边提升网格背景上的可读性。
- 连接线从输出端口外侧起笔，终点停在输入端口前方，避免箭头、端口和端点圆点堆叠。
- 箭头使用小型独立 marker，默认深蓝灰色，选中连接使用 Google Blue 加粗和发光效果。
- 连线中状态使用蓝色动态虚线，强化拖拽方向。
- 左侧 Agent Palette 展开时，连接线按当前 viewport 反算安全区并优先绕开 Palette 覆盖区域。
- 连接点由节点自身输入/输出端口表达，平时低显著度，hover 或选中节点时高亮。
- 支持选中连接线并通过 `Delete / Backspace` 删除。
- 保留“自动顺序连线”按钮，可按当前节点顺序重建连接。
- 右下角小地图显示节点分布和当前视口，可点击或拖动快速移动视角。
- 小地图显示浅灰连接线，选中节点高亮。
- 支持 `Ctrl/Cmd + 点击` 多选节点，支持空白区域拖拽框选。
- 多选后显示批量操作浮层，可整理选中、删除选中或取消选择。
- 快捷键：`Space` 平移、滚轮缩放、`Delete / Backspace` 删除选中节点或连接、`Esc` 取消选择或连线中状态。
- 当前手动连线用于模板编辑和演示编排，不直接改写 LangGraph 真实运行拓扑。

## Replay

- 支持按 Agent、状态和关键字筛选事件。
- 提供“只看 CodeAgent”快捷按钮。
- CodeAgent 事件使用黄色高亮，安全阻断或失败事件使用红色强调。
- 自动播放基于筛选后的事件列表运行。

## Dashboard

- Java Gateway 模式展示“最近 CodeAgent 操作”卡片。
- 卡片显示最近运行、最近事件、阻断/异常状态、事件时间，并提供 History / Replay 跳转。
- Python Direct 模式显示轻提示，不展示 Java 平台事件卡片。

## RunConsole

- 左侧提供结构化需求构造器，可将任务目标、约束、验收标准、目标文件、输出格式和 CodeAgent 文件操作拼接成最终 `requirement`。
- 保留原始需求输入框，允许用户继续手动编辑最终自然语言需求。
- 右侧顶部显示运行结果高光区，集中展示成功状态、质量评分、测试状态、覆盖率、修复次数、事件数量、CodeAgent 状态和报告状态。
- Java 模式下结果高光区提供 History / Replay / Reports 快捷入口。
- 详细调试信息继续放在 SummaryCards、WorkflowTimeline、ResultOverview、AgentOutputTabs 和 ReportPreview 中。

## 状态颜色

- 成功：绿色。
- 失败：红色。
- 运行中：蓝色。
- 修复或警告：黄色。
- 等待：灰色。
