# v1.0 / v2.0 双轨启动测试清单

本文用于确认 v1.0 比赛演示轨和 v2.0 平台化升级轨都能独立启动、独立测试、互不破坏。每次较大修改后，至少按影响范围执行对应轨道测试。

## v1.0 比赛演示轨测试

### 测试项

- [ ] 虚拟环境能否激活。
- [ ] `requirements.txt` 能否安装。
- [ ] `graph_demo.py` 能否运行。
- [ ] `webui.py` 能否运行。
- [ ] `start_demo.bat` 能否运行。
- [ ] 简单成功案例是否通过。
- [ ] 翻车修复案例是否触发自动修复。
- [ ] 报告是否生成。
- [ ] `runs/` 是否保存运行历史。
- [ ] 离线或 API 异常时是否有提示。

### 测试命令

```powershell
cd D:\AIchatProject
.\.venv\Scripts\Activate.ps1
python graph_demo.py
python -m streamlit run webui.py
.\start_demo.bat
```

### 验收标准

- CLI 或 Streamlit 至少有一个入口能完成完整演示。
- Web UI 页面不白屏、不崩溃。
- 运行完成后能看到结果摘要、Agent 输出和报告入口。
- `reports/` 中有 Markdown 报告。
- `runs/` 中有运行历史 JSON。
- API Key 缺失、离线模式或模型异常时有可理解提示。

## v2.0 平台化升级轨测试

### 测试项

- [ ] FastAPI 是否启动。
- [ ] Vue 是否启动。
- [ ] Java 是否启动。
- [ ] MySQL 是否连接。
- [ ] Docker Compose 是否启动。
- [ ] Vue Python Direct 模式是否可用。
- [ ] Vue Java Gateway 模式是否可用。
- [ ] Java 是否能代理 Python API。
- [ ] Java 是否能写入 MySQL。
- [ ] Reports / Runs / Models / Plugins 页面是否可用。
- [ ] C++ Runner 是否可选执行。

### 测试命令

FastAPI：

```powershell
cd D:\AIchatProject
.\.venv\Scripts\Activate.ps1
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
```

Vue：

```powershell
cd D:\AIchatProject\frontend-vue
npm run dev
```

Java：

```powershell
cd D:\AIchatProject\backend-java
mvn spring-boot:run
```

Docker Compose：

```powershell
cd D:\AIchatProject
docker compose up --build
```

C++ Runner 可选编译：

```powershell
cd D:\AIchatProject\runner-cpp
cmake -S . -B build
cmake --build build --config Release
```

### 验收标准

- FastAPI Docs 可访问：`http://localhost:8001/docs`。
- Java Health 可访问：`http://localhost:8088/api/health`。
- Vue Dashboard 可访问：开发模式通常为 `http://localhost:5173`，Docker 模式为 `http://localhost:5174`。
- Docker 模式下 Streamlit 可访问：`http://localhost:8501`。
- Java Gateway 模式下 Dashboard 能显示平台统计或清晰的连接失败提示。
- Reports / Runs / Models / Plugins 页面不白屏。
- C++ Runner 不存在时能自动回退 Python Runner。

## 测试记录

测试结果记录到 `docs/TEST_RESULT_LOG.md`。如果失败，先记录问题、复现命令、影响轨道和是否已修复，不要直接删除或重写核心模块。
