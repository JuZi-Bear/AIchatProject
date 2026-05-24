# v2-only Bug Fix Log

本文只记录当前 v2 平台链路的修复记录。旧运行入口相关问题已随 v2-only 收敛移除，不再作为当前维护对象。

## 2026-05-24

- 收敛 Docker 默认入口为 FastAPI。
- 移除旧 Python UI / CLI 依赖。
- 统一文档启动命令为 Vue -> Java -> FastAPI -> MySQL。

## 后续记录格式

| 日期 | 问题 | 影响范围 | 修复 | 验证 |
| --- | --- | --- | --- | --- |
