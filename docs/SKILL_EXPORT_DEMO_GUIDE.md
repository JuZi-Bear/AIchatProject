# Workflow Skill Export 演示指南

本文用于比赛演示和本地验收，说明如何把 Workflow Editor / Workflow Templates 中保存到 Java + MySQL 的模板导出为 Codex Skill 包。

## 演示目标

展示闭环：

```text
保存 Workflow 模板
  -> 导出 Codex Skill
  -> 查看 SKILL.md / workflow-template.json / run_workflow.py
  -> 通过 Java Gateway 执行导出脚本
  -> Replay 查看执行事件
```

当前阶段只导出 Skill，不自动安装到 Codex，也不绕过 Java Gateway、Dynamic LangGraph Runtime 或 CodeAgent 安全策略。

## 前置条件

1. v2 主链路已启动：

```powershell
.\scripts\start_v2_local.ps1
```

或：

```powershell
docker compose up -d --build
```

2. Java Gateway 可访问：

```powershell
Invoke-RestMethod http://127.0.0.1:8088/api/health
```

3. Workflow 模板已保存到 Java + MySQL。

## 自动验收

推荐先执行 smoke 脚本：

```powershell
.\scripts\smoke_skill_export.ps1 -RunExportedScript
```

该脚本会：

- 创建一个临时 MySQL Workflow 模板。
- 调用 `POST /api/platform/workflows/templates/{templateKey}/export-skill`。
- 校验导出目录包含：
  - `SKILL.md`
  - `references/workflow-template.json`
  - `scripts/run_workflow.py`
- 校验 `SKILL.md` frontmatter 只包含 `name` 和 `description`。
- 校验 `run_workflow.py` 调用 Java Gateway 的 `execute-langgraph` 接口。
- 可选执行导出的 `run_workflow.py`。
- 删除临时模板，但保留导出的 Skill 目录作为演示产物。

如果只想校验文件结构，不执行导出脚本：

```powershell
.\scripts\smoke_skill_export.ps1
```

如果希望保留临时模板，方便后续重复运行导出脚本：

```powershell
.\scripts\smoke_skill_export.ps1 -RunExportedScript -KeepTemplate
```

## 页面演示

1. 打开 Workflow Templates：

```text
http://127.0.0.1:5174/workflows/templates
```

2. 选择 Java MySQL 模板，点击“导出 Skill”。

3. 查看导出结果：

```text
generated-skills/<skill-name>/
  SKILL.md
  references/workflow-template.json
  scripts/run_workflow.py
```

本地 `mvn spring-boot:run` 场景下，Java 进程工作目录可能是 `backend-java/`，导出物也可能出现在：

```text
backend-java/generated-skills/<skill-name>/
```

Docker Compose 场景下会挂载到项目根目录：

```text
generated-skills/<skill-name>/
```

4. 运行导出脚本：

```powershell
cd generated-skills\<skill-name>
python scripts\run_workflow.py --api-base http://127.0.0.1:8088/api --requirement "Run exported skill demo"
```

5. 根据输出中的 `platformRunId` 打开 Replay：

```text
http://127.0.0.1:5174/replay/<platformRunId>
```

## 安全边界

- 导出的 Skill 不包含 API Key。
- 导出的脚本只调用 Java Gateway。
- 导出的脚本不直接调用 Python Agent Engine、CodeAgent 文件系统接口或模型 API。
- CodeAgent 文件操作仍由平台安全策略、白名单、阻断路径和审计日志控制。
- `generated-skills/` 是运行产物目录，默认不提交具体导出物。

## 常见问题

### 导出成功但找不到目录

检查两个位置：

```powershell
Get-ChildItem generated-skills
Get-ChildItem backend-java\generated-skills
```

### `run_workflow.py` 连接失败

确认 Java Gateway 已启动：

```powershell
Invoke-RestMethod http://127.0.0.1:8088/api/health
```

### 导出脚本返回模板不存在

如果 smoke 脚本没有使用 `-KeepTemplate`，临时模板会被删除。请在页面中使用真实模板导出，或重新运行：

```powershell
.\scripts\smoke_skill_export.ps1 -RunExportedScript -KeepTemplate
```
