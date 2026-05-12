# 比赛演示脚本

## 演示开场

本项目演示一个 AI 多智能体自动开发流水线：

用户需求 → Product Agent → Coder Agent → Tester Agent → Code Runner → Sentry Agent → 自动修复

运行命令：

```powershell
cd D:\AIchatProject
.\.venv\Scripts\python.exe main.py
```

也可以运行 LangGraph 演示入口：

```powershell
cd D:\AIchatProject
.\.venv\Scripts\python.exe graph_demo.py
```

两个入口启动后都可以选择 3 个预设案例，也可以选择自定义输入。

LangGraph 演示会在最终结果里重点展示：

- 是否成功
- 修复次数
- 最终 stdout
- 最终 error_log

## 案例 1：简单成功案例

### 用户输入需求

```text
做一个简单 Python 程序，运行后直接打印 hello world，不需要用户输入
```

### 预期系统流程

1. Product Agent 将需求拆成一个最小任务：打印 `hello world`。
2. Coder Agent 生成一行 Python 代码。
3. Tester Agent 静态检查代码，确认没有明显语法和逻辑问题。
4. Code Runner 保存代码到 `output/generated_code.py`。
5. Code Runner 运行代码并输出 `hello world`。

### 可能出现的错误

这个案例通常不会出错，适合作为开场展示系统的最短成功路径。

### Sentry Agent 如何修复

一般不会触发 Sentry Agent。如果模型意外生成错误代码，Sentry Agent 会读取 `stderr`，给出错误原因和修复建议。

### 最终展示亮点

- 蓝色 Product Agent 面板展示需求拆解。
- 绿色 Coder Agent 面板展示生成代码。
- 黄色 Tester Agent 面板展示静态检查。
- 最终显示绿色 `✅ 运行成功`。

## 案例 2：第一次失败但可自动修复案例

### 用户输入需求

```text
写一个简单 Python 程序，必须调用 input 读取用户姓名，然后打印 hello 加姓名
```

### 预期系统流程

1. Product Agent 拆解为“读取姓名”和“打印问候语”。
2. Coder Agent 可能生成包含 `input()` 的代码。
3. Tester Agent 静态检查通常认为代码语法没问题。
4. Code Runner 自动运行时没有人工输入，容易触发 `EOFError`。
5. Sentry Agent 分析 `stderr`，指出 `input()` 在非交互环境中读取失败。
6. Coder Agent 根据错误日志修复代码，例如用 `try-except EOFError` 设置默认姓名。
7. Code Runner 保存修复后的代码并重新运行。

### 可能出现的错误

```text
EOFError: EOF when reading a line
```

### Sentry Agent 如何修复

Sentry Agent 会建议：

- 捕获 `EOFError`
- 在没有输入时使用默认值
- 保证代码在非交互运行环境中也能正常结束

### 最终展示亮点

- 第一次运行显示红色 `❌ 运行失败`。
- 自动修复状态面板显示“当前第 1 轮修复”和错误摘要。
- 红色 Sentry Agent 面板展示错误分析。
- 修复后重新运行，显示绿色 `✅ 运行成功`。

## 案例 3：复杂一点的综合案例

### 用户输入需求

```text
写一个学生成绩统计程序。程序内置 5 个学生的姓名和分数，不需要用户输入。运行后输出平均分、最高分学生、最低分学生、及格人数，并用函数组织代码。
```

### 预期系统流程

1. Product Agent 将需求拆成数据准备、统计计算、结果输出几个部分。
2. Coder Agent 生成包含函数的 Python 程序。
3. Tester Agent 检查函数、变量、入口调用和基础逻辑。
4. Code Runner 保存并运行代码。
5. 程序输出平均分、最高分学生、最低分学生和及格人数。

### 可能出现的错误

可能出现：

- 字典键名写错导致 `KeyError`
- 变量名不一致导致 `NameError`
- 除法计算时列表为空导致 `ZeroDivisionError`
- 忘记调用主函数，导致没有输出

### Sentry Agent 如何修复

如果运行失败，Sentry Agent 会根据 `stderr` 判断具体问题：

- `NameError`：提示统一变量名。
- `KeyError`：提示检查字典字段。
- `ZeroDivisionError`：提示添加空列表保护。
- 没有输出：提示补充入口函数调用。

然后 Coder Agent 会基于原始代码、错误日志和修复建议重新生成完整代码。

### 最终展示亮点

- 展示系统不只会写一行代码，也能生成结构化函数代码。
- 展示 Tester Agent 对入口函数和逻辑的检查。
- 展示 Code Runner 自动保存和运行真实 Python 文件。
- 如果触发错误，可以继续展示 Sentry Agent 自动修复闭环。

## 现场演示建议

推荐顺序：

1. 先演示简单案例，快速证明系统能跑通。
2. 再演示翻车修复案例，展示自动修复闭环。
3. 最后演示综合案例，展示更完整的代码生成能力。

如果时间有限，只演示案例 1 和案例 2。

## 5 分钟比赛演示台词

### 0:00 - 0:40 开场介绍

各位评委老师好，我们的项目叫 **AI Multi-Agent Pipeline**。

它解决的问题是：现在大模型可以生成代码，但真实开发中只生成代码还不够。开发者还需要拆解需求、检查代码、运行验证、分析报错、再修复。

所以我们做了一个多智能体自动开发流水线，让 AI 不只是写代码，而是完成一条更接近真实开发流程的闭环。

一句话概括：

```text
用户输入需求后，系统自动完成需求分析、代码生成、静态检查、运行测试、错误分析和自动修复。
```

### 0:40 - 1:30 技术架构说明

系统主要由四类 Agent 组成：

- Product Agent：负责把自然语言需求拆成产品方案。
- Coder Agent：负责生成 Python 代码，也负责修复失败代码。
- Tester Agent：负责做静态检查，判断语法、逻辑和入口调用问题。
- Sentry Agent：负责分析 stderr 错误日志，并给出修复建议。

底层我们使用 **DeepSeek API** 作为国产大模型能力，使用 **LangGraph** 管理整个工作流状态。

LangGraph 中的流程是：

```text
Product Node → Coder Node → Tester Node → Runner Node
```

如果 Runner 执行成功，流程结束；如果失败，就进入：

```text
Sentry Node → Coder Node → Tester Node → Runner Node
```

最多自动修复 3 次，避免无限循环。

### 1:30 - 2:40 翻车案例演示

现在我们演示一个故意容易翻车的案例。

需求是：

```text
写一个简单 Python 程序，必须调用 input 读取用户姓名，然后打印 hello 加姓名
```

这个需求在普通终端里没有问题，但我们的系统会自动运行生成的代码，不会人工输入内容，所以第一次运行很可能出现：

```text
EOFError: EOF when reading a line
```

这就是一个真实开发中常见的问题：代码看起来没错，但自动化环境里会失败。

### 2:40 - 3:50 自动修复亮点

当第一次运行失败后，系统会做三件事：

第一，把 stderr 错误日志交给 Sentry Agent。

第二，Sentry Agent 分析出错误原因：代码调用了 input，但自动运行环境没有人工输入。

第三，Coder Agent 根据 Sentry 的建议重新生成代码，比如增加：

```python
try:
    name = input("请输入你的姓名: ")
except EOFError:
    name = "默认用户"
print("hello", name)
```

修复后的代码会再次保存并运行。

如果运行成功，Web UI 会显示：

```text
success: 成功
retry_count: 1
stdout: hello 默认用户
```

这就是我们项目最核心的亮点：不是只展示 AI 写代码，而是展示 AI 如何在失败后自我修复。

### 3:50 - 4:40 Web UI 与报告展示

除了 CLI，我们还做了 Streamlit Web UI。

Web UI 中可以看到：

- 左侧项目简介和技术栈
- 中间 Agent Workflow 流程图
- Product、Coder、Tester、Sentry 状态卡片
- stdout 和 error_log 运行结果
- 自动生成的 Markdown 报告

这部分是为了让比赛现场的评委更直观地看到每个 Agent 做了什么，而不是只看终端输出。

### 4:40 - 5:00 总结收尾

最后总结一下，我们项目的创新点有三个：

第一，基于国产大模型 DeepSeek 实现多智能体协作。

第二，使用 LangGraph 把开发流程做成可扩展状态机。

第三，实现了从需求到代码、从失败到修复、从运行到报告的完整闭环。

未来我们还可以继续扩展 pytest 测试生成、多文件项目生成、Figma 到前端页面生成，让它变成一个更完整的 AI 软件工厂原型。

谢谢各位老师。
