# CodeAgent 节点集成说明

本文记录简化版 CodeAgent 节点在当前双轨架构中的调用链路。CodeAgent 不是完整 Codex，只执行用户指定路径的 `read_file`、`write_file`、`list_files` 三类受控文件操作。

## 单人演示闭环

```text
Vue Workflow Editor / RunConsole
  -> 触发 CodeAgent 节点
  -> Java Gateway /api/code-agent/execute
  -> Python /api/code-agent/execute
  -> utils/simple_code_agent.py 执行文件操作
  -> 写入 output/code_agent_audit.jsonl
  -> 返回 AGENT_STARTED / AGENT_FINISHED / AGENT_FAILED
  -> Java 保存 RunRecord + RunEvent
  -> SSE 推送到 Vue
  -> History / Replay 查看执行顺序
```

Python Direct 模式下，Vue 直接调用 Python CodeAgent API 并展示响应事件；Java Gateway 模式下，Java 会额外保存平台运行记录、事件记录，并支持 SSE 与回放。

## Python CodeAgent 节点调用示例

```python
from utils.simple_code_agent import read_file, write_file, list_files, execute_code_agent

content = read_file("src/moduleA.py")["content"]
new_content = content + "\n# 添加新函数 my_func"
write_result = write_file("src/moduleB.py", new_content)
files = list_files("src/")

response = execute_code_agent({
    "operations": [
        {"operation": "read_file", "filePath": "src/moduleA.py"},
        {"operation": "write_file", "filePath": "src/moduleB.py", "content": new_content},
        {"operation": "list_files", "filePath": "src/", "recursive": False},
    ]
})

print(response["results"])
print(response["events"])
```

每次操作都会生成摘要：

```json
{
  "success": true,
  "filePath": "src/moduleB.py",
  "message": "已修改或生成文件内容"
}
```

并追加 JSONL 审计日志，默认路径：

```text
output/code_agent_audit.jsonl
```

## Java SSE 推送事件示例

Vue 在 Java Gateway 模式下可以先订阅 SSE，再触发 CodeAgent：

```text
GET http://127.0.0.1:8088/api/platform/runs/code_agent_demo_001/events/stream
Accept: text/event-stream
```

随后调用：

```http
POST http://127.0.0.1:8088/api/code-agent/execute
Content-Type: application/json
```

```json
{
  "platformRunId": "code_agent_demo_001",
  "operation": "write_file",
  "filePath": "output/code_agent_demo.txt",
  "content": "# 添加新函数 my_func"
}
```

SSE 事件示例：

```text
event: run-event
data: {"platformRunId":"code_agent_demo_001","eventType":"AGENT_STARTED","eventText":"CodeAgent 操作开始","agent":"code_agent","status":"RUNNING","message":"开始执行 write_file: output/code_agent_demo.txt"}

event: final
data: {"platformRunId":"code_agent_demo_001","eventType":"AGENT_FINISHED","eventText":"CodeAgent 操作完成","agent":"code_agent","status":"SUCCESS","message":"已修改或生成文件内容"}
```

Java 会同时写入：

- `run_record`：让 `/replay/{platformRunId}` 可以找到 CodeAgent 操作。
- `run_event`：让 History、RunConsole、Dashboard 和 Replay 可以展示事件顺序。

## Vue 展示示例

前端 API：

```ts
import { executeCodeAgent } from "@/api/codeAgent";
import { subscribeRunEvents } from "@/api/eventStream";

const platformRunId = "code_agent_demo_001";

const subscription = subscribeRunEvents(
  platformRunId,
  (event) => {
    console.log(event.eventText, event.status, event.message);
  },
  (error) => console.warn(error.message),
);

const response = await executeCodeAgent({
  platformRunId,
  operation: "write_file",
  filePath: "output/code_agent_demo.txt",
  content: "# 添加新函数 my_func",
});

subscription.close();
console.log(response.results);
```

当前 Vue 已支持：

- Workflow Editor 中选中 `CodeAgent` 节点后触发操作。
- RunConsole 左侧直接触发 CodeAgent 文件操作。
- 实时展示 CodeAgent 事件时间线。
- 高亮路径阻断、白名单违规和失败事件。
- 点击操作结果中的文件路径查看生成或修改后的内容。
- 快捷填入 Demo 写文件内容，用于现场快速生成文件。
- 一键测试 `.env` 阻断路径，用于展示安全策略和失败事件高亮。
- 预览 `output/code_agent_audit.jsonl` 最近审计记录。
- `write_file` 后展示生成/修改前后的简单行级 diff。
- 支持一键复制审计日志和 diff，便于答辩时粘贴展示。
- Workflow Replay 会用黄色高亮 `code_agent` 文件操作节点。
- Dashboard 在 Java Gateway 模式下展示最近 CodeAgent 操作和事件入口。
- Java 模式下通过 History / Replay 查看 CodeAgent 事件顺序。

## 路径安全策略

配置文件：

```text
config/settings.yaml
```

关键字段：

```yaml
code_agent:
  allowed_paths:
    - src
    - output
    - docs
    - frontend-vue/src
    - backend-java/src
    - utils
  blocked_paths:
    - .git
    - .venv
    - node_modules
    - .env
  audit_log_path: output/code_agent_audit.jsonl
  max_read_chars: 200000
```

若路径不在白名单内，或命中阻断路径，CodeAgent 会返回失败摘要、生成 `AGENT_FAILED` 事件，并写入审计日志。

## 当前限制

- CodeAgent 不会自动决定修改哪些文件，必须由用户或前端节点配置指定路径。
- 当前执行是同步请求，SSE 用于推送 Java 已保存事件，不是 Python 进程内逐 token 日志。
- 文件预览会额外触发一次 `read_file` 操作，也会产生审计记录。
- before/after diff 通过受控 `read_file` 获取写入前后内容，属于演示级行级对比，不是完整 Git diff 引擎。
- 当前不包含多用户权限系统，适合单人演示和本地受控开发场景。
