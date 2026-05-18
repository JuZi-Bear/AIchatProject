# utils

## 目录作用

`utils/` 是共享工具目录，包含代码执行、C++ Runner 适配、错误处理、模型对比、运行历史、摘要构建、测试运行和 UI ViewModel 构建等能力。

## 核心文件

- `code_runner.py`：Python Runner 和 C++ Runner 选择逻辑。
- `cpp_runner_adapter.py`：C++ Runner 调用适配层。
- `run_store.py`：运行历史读写。
- `summary_builder.py`：`run_summary` 构建。
- `ui_state_builder.py`：`ui_view_model` 构建。
- `test_runner.py`：测试运行辅助。
- `error_utils.py`：错误摘要工具。

## 不能随便修改

- 不要删除 Python Runner fallback。
- 不要破坏 `run_summary` 和 `ui_view_model` 的兼容字段。
- 不要把生成输出目录改成前端或 Java 私有路径。
- 不要让工具层依赖 Vue 或 Java 运行环境。

## 轨道归属

shared-core。

## 当前开发状态

stable。
