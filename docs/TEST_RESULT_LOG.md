# 双轨测试结果记录

本文用于手动记录 v1.0 / v2.0 双轨启动和回归测试结果。

| 测试项 | 轨道 | 命令/页面 | 结果 | 问题 | 是否修复 |
|---|---|---|---|---|---|
| 虚拟环境激活 | v1-demo | `.\.venv\Scripts\Activate.ps1` | 未测试 |  |  |
| requirements 安装 | v1-demo | `pip install -r requirements.txt` | 未测试 |  |  |
| CLI 演示 | v1-demo | `python graph_demo.py` | 未测试 |  |  |
| Streamlit Web UI | v1-demo | `python -m streamlit run webui.py` | 未测试 |  |  |
| Windows 启动脚本 | v1-demo | `.\start_demo.bat` | 未测试 |  |  |
| FastAPI 启动 | v2-platform | `python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001` | 未测试 |  |  |
| Vue 开发模式 | v2-platform | `npm run dev` | 未测试 |  |  |
| Java Gateway | v2-platform | `mvn spring-boot:run` | 未测试 |  |  |
| Docker Compose | v2-platform | `docker compose up --build` | 未测试 |  |  |
| Vue Dashboard | v2-platform | `http://localhost:5173` 或 `http://localhost:5174` | 未测试 |  |  |
| FastAPI Docs | v2-platform | `http://localhost:8001/docs` | 未测试 |  |  |
| Java Health | v2-platform | `http://localhost:8088/api/health` | 未测试 |  |  |
| Streamlit Docker | v1-demo / docker | `http://localhost:8501` | 未测试 |  |  |
| C++ Runner 可选编译 | experimental | `cmake -S . -B build` | 未测试 |  |  |

## 记录规则

- 结果建议填写：通过 / 失败 / 跳过 / 未测试。
- 问题栏记录错误摘要、端口、日志位置或截图说明。
- 是否修复建议填写：是 / 否 / 待确认。
- 不确定是否影响双轨时，同时标记 v1-demo 和 v2-platform。
