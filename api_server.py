import os
import subprocess
import mimetypes
import re
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from schemas.run_request import RunRequest
from schemas.run_response import RunResponse
from services.run_service import (
    create_run,
    get_available_agents,
    get_available_models,
    get_available_plugins,
    get_report,
    get_run,
    get_workflow_templates,
    instantiate_workflow_template,
    list_reports,
    list_run_history,
)
import re
from utils.simple_code_agent import execute_code_agent, _normalize_project_path, write_file
from agents import ask_llm, should_use_offline_demo
from dynamic_workflow import execute_dynamic_workflow, resume_dynamic_workflow, validate_dynamic_workflow


app = FastAPI(
    title="Python Agent Engine API",
    description="FastAPI wrapper for the v2.0 Python Agent Engine preview.",
    version="v2-api-preview",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()

    return model.dict()


def _build_run_response(result: dict, include_state: bool) -> dict:
    response = {
        "run_id": result.get("run_id", ""),
        "run_summary": result.get("run_summary", {}),
        "ui_view_model": result.get("ui_view_model", {}),
    }

    if include_state:
        response["state"] = result.get("state", {})

    return response


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "python-agent-engine",
        "version": "v2-api-preview",
    }


@app.get("/models")
def list_models():
    return get_available_models()


@app.get("/plugins")
def list_plugins():
    return get_available_plugins()


@app.get("/agents")
def list_agents():
    return get_available_agents()


@app.get("/api/workflows/templates")
def list_workflow_templates():
    return get_workflow_templates()


@app.post("/api/workflows/instantiate")
def instantiate_workflow(request: dict):
    try:
        return instantiate_workflow_template(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/workflows/dynamic/validate")
def validate_dynamic_workflow_template(request: dict):
    return validate_dynamic_workflow(request or {})


@app.post("/api/workflows/dynamic/execute")
def execute_dynamic_workflow_template(request: dict):
    return execute_dynamic_workflow(request or {})


@app.post("/api/workflows/dynamic/runs/{run_id}/resume")
def resume_dynamic_workflow_run(run_id: str, request: dict):
    try:
        return resume_dynamic_workflow(run_id, request or {})
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/api/code-agent/execute")
def execute_code_agent_operation(request: dict):
    return execute_code_agent(request or {})


@app.post("/api/code-agent/open-folder")
def open_code_agent_folder(request: dict):
    folder_path = str(request.get("filePath", "")).strip()
    try:
        target_path, relative_path = _normalize_project_path(folder_path)
        if not target_path.exists():
            return {"success": False, "message": f"目录不存在：{relative_path}"}
        if not target_path.is_dir():
            target_path = target_path.parent

        if os.name == "nt":
            os.startfile(target_path)
        else:
            subprocess.Popen(["xdg-open", str(target_path)])

        return {"success": True, "message": f"已在系统文件管理器中打开：{relative_path}"}
    except Exception as e:
        return {"success": False, "message": f"打开文件夹失败：{str(e)}"}


OFFLINE_DEMO_PROJECT = [
    {
        "filePath": "index.html",
        "content": """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>极客黑客计算器</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="matrix-bg" id="matrix"></div>
    <div class="calculator-card">
        <div class="header">
            <span class="dot red"></span>
            <span class="dot yellow"></span>
            <span class="dot green"></span>
            <span class="title">Hacker Terminal Calculator v1.0</span>
        </div>
        <div class="screen" id="display">0</div>
        <div class="buttons">
            <button class="btn fn" onclick="clearScreen()">AC</button>
            <button class="btn fn" onclick="deleteChar()">DEL</button>
            <button class="btn fn" onclick="press('/')">/</button>
            <button class="btn fn" onclick="press('*')">*</button>
            
            <button class="btn num" onclick="press('7')">7</button>
            <button class="btn num" onclick="press('8')">8</button>
            <button class="btn num" onclick="press('9')">9</button>
            <button class="btn fn" onclick="press('-')">-</button>
            
            <button class="btn num" onclick="press('4')">4</button>
            <button class="btn num" onclick="press('5')">5</button>
            <button class="btn num" onclick="press('6')">6</button>
            <button class="btn fn" onclick="press('+')">+</button>
            
            <button class="btn num" onclick="press('1')">1</button>
            <button class="btn num" onclick="press('2')">2</button>
            <button class="btn num" onclick="press('3')">3</button>
            <button class="btn num" onclick="press('.')">.</button>
            
            <button class="btn num wide" onclick="press('0')">0</button>
            <button class="btn enter" onclick="calculate()">=</button>
        </div>
    </div>
    <script src="app.js"></script>
</body>
</html>"""
    },
    {
        "filePath": "style.css",
        "content": """body {
    margin: 0;
    padding: 0;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #050505;
    font-family: 'Courier New', Courier, monospace;
    overflow: hidden;
}
.matrix-bg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    opacity: 0.15;
}
.calculator-card {
    position: relative;
    z-index: 10;
    width: 320px;
    background: rgba(17, 24, 39, 0.95);
    border: 2px solid #00ff66;
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0, 255, 102, 0.3);
    padding: 16px;
    box-sizing: border-box;
}
.header {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    border-bottom: 1px solid #374151;
    padding-bottom: 8px;
}
.dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 6px;
}
.red { background: #ff5f56; }
.yellow { background: #ffbd2e; }
.green { background: #27c93f; }
.title {
    color: #00ff66;
    font-size: 11px;
    margin-left: 8px;
}
.screen {
    background: #0d1117;
    border: 1px solid #374151;
    border-radius: 6px;
    color: #00ff66;
    font-size: 32px;
    text-align: right;
    padding: 16px;
    margin-bottom: 16px;
    min-height: 48px;
    overflow: hidden;
    text-shadow: 0 0 5px rgba(0, 255, 102, 0.5);
    word-break: break-all;
}
.buttons {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
}
.btn {
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 12px;
    font-size: 18px;
    font-family: inherit;
    cursor: pointer;
    background: #1f2937;
    color: #e5e7eb;
    transition: all 0.2s ease;
}
.btn:hover {
    background: #374151;
    border-color: #9ca3af;
}
.btn.fn {
    color: #38bdf8;
}
.btn.num {
    color: #e5e7eb;
}
.btn.enter {
    grid-column: span 2;
    background: #059669;
    color: #ffffff;
    border-color: #00ff66;
}
.btn.enter:hover {
    background: #10b981;
    box-shadow: 0 0 10px rgba(0, 255, 102, 0.5);
}
.btn.wide {
    grid-column: span 2;
}"""
    },
    {
        "filePath": "app.js",
        "content": """const display = document.getElementById('display');
let currentInput = '';

function press(val) {
    if (currentInput === '0' && val !== '.') {
        currentInput = val;
    } else {
        currentInput += val;
    }
    updateDisplay();
}

function clearScreen() {
    currentInput = '0';
    updateDisplay();
}

function deleteChar() {
    if (currentInput.length > 1) {
        currentInput = currentInput.slice(0, -1);
    } else {
        currentInput = '0';
    }
    updateDisplay();
}

function calculate() {
    try {
        let sanitized = currentInput.replace(/[^0-9+\\-*/.]/g, '');
        let result = Function('"use strict";return (' + sanitized + ')')();
        currentInput = String(result);
    } catch (e) {
        currentInput = 'ERROR';
    }
    updateDisplay();
}

function updateDisplay() {
    display.innerText = currentInput || '0';
}

// Matrix Background Effect
const canvas = document.createElement('canvas');
const matrixContainer = document.getElementById('matrix');
if (matrixContainer) {
    matrixContainer.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    const cols = Math.floor(width / 20) + 1;
    const ypos = Array(cols).fill(0);

    function matrix() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, width, height);
        
        ctx.fillStyle = '#00ff66';
        ctx.font = '15pt monospace';
        
        ypos.forEach((y, ind) => {
            const text = String.fromCharCode(Math.floor(Math.random() * 128));
            const x = ind * 20;
            ctx.fillText(text, x, y);
            
            if (y > 100 + Math.random() * 10000) {
                ypos[ind] = 0;
            } else {
                ypos[ind] = y + 20;
            }
        });
    }

    setInterval(matrix, 50);

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });
}"""
    }
]


@app.post("/api/code-agent/ai-generate")
def ai_generate_code_agent_project(request: dict):
    requirement = str(request.get("requirement", "")).strip()
    base_dir = str(request.get("baseDir", "output/code_agent_workspace")).strip()
    model_provider = request.get("modelProvider")

    if not requirement:
        raise HTTPException(status_code=400, detail="需求不能为空")

    try:
        target_dir_path, relative_base_dir = _normalize_project_path(base_dir)
        target_dir_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"目标目录不合法: {str(e)}")

    generated_files = []

    if should_use_offline_demo(model_provider):
        project_files = OFFLINE_DEMO_PROJECT
    else:
        system_prompt = (
            "You are an expert AI software developer. "
            "Generate all files needed for the user's project requirement. "
            "Output ONLY a raw JSON array of objects representing the files to be created. "
            "Do not include markdown code block syntax (like ```json ... ```). Output the raw JSON text directly. "
            "Each object in the array must have two keys:\\n"
            '- "filePath": the relative path of the file from the project directory (e.g. "index.html", "style.css", "app.js").\\n'
            '- "content": the complete text content of the file.\\n\\n'
            "Example format:\\n"
            '[\\n  {\\n    "filePath": "index.html",\\n    "content": "<!DOCTYPE html>..."\\n  }\\n]'
        )
        user_prompt = f"项目需求：{requirement}\\n目标文件夹：{relative_base_dir}\\n\\n请直接输出对应的 JSON 数组。"

        try:
            llm_response = ask_llm(system_prompt, user_prompt, provider=model_provider)
            text = llm_response.strip()
            match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
            if match:
                text = match.group(0)

            project_files = json.loads(text)
            if not isinstance(project_files, list):
                raise ValueError("LLM did not return a list of files")
        except Exception as err:
            print(f"AI一键生成调用大模型失败，降级使用本地经典计算器Demo: {err}")
            project_files = OFFLINE_DEMO_PROJECT

    written_files = []
    results = []

    for file_item in project_files:
        rel_path = file_item.get("filePath", "").strip()
        rel_path = rel_path.replace("\\\\", "/").replace("\\", "/").strip("/")
        if not rel_path:
            continue

        full_rel_file_path = f"{relative_base_dir}/{rel_path}"
        content = file_item.get("content", "")

        try:
            res = write_file(full_rel_file_path, content)
            written_files.append(full_rel_file_path)
            results.append({
                "success": True,
                "filePath": full_rel_file_path,
                "operation": "write_file",
                "message": "已生成文件"
            })
        except Exception as e:
            results.append({
                "success": False,
                "filePath": full_rel_file_path,
                "operation": "write_file",
                "message": f"安全阻断或写入失败：{str(e)}"
            })

    success = any(r["success"] for r in results)

    return {
        "success": success,
        "agent": "code_agent",
        "operation": "ai_generate",
        "filePath": relative_base_dir,
        "message": "AI 项目一键生成完毕" if success else "AI 项目生成失败或被安全阻断",
        "results": results,
        "files": written_files,
        "events": [
            {
                "id": 0,
                "platformRunId": "",
                "eventType": "AGENT_FINISHED",
                "eventText": "AI一键项目生成完成",
                "agent": "code_agent",
                "status": "SUCCESS" if success else "FAILED",
                "message": f"成功在目录 {relative_base_dir} 下生成了 {len(written_files)} 个文件！",
                "createdAt": datetime.now().isoformat()
            }
        ]
    }


@app.get("/api/code-agent/preview/serve/{file_path:path}")
def serve_preview_file(file_path: str):
    try:
        target_path, relative_path = _normalize_project_path(file_path)
        if not target_path.exists():
            raise HTTPException(status_code=404, detail=f"文件不存在：{relative_path}")
        if not target_path.is_file():
            raise HTTPException(status_code=400, detail=f"目标不是文件：{relative_path}")

        mime_type, _ = mimetypes.guess_type(str(target_path))
        headers = {}
        if mime_type == "text/html":
            headers["Content-Security-Policy"] = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval' *; "
                "img-src * data:; "
                "style-src * 'unsafe-inline';"
            )

        return FileResponse(
            target_path,
            media_type=mime_type or "application/octet-stream",
            headers=headers,
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@app.post("/runs", response_model=RunResponse, response_model_exclude_none=True)
def create_workflow_run(request: RunRequest):
    try:
        result = create_run(_model_to_dict(request))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return _build_run_response(result, include_state=True)


@app.get("/runs", response_model=list[dict])
def list_workflow_runs():
    return list_run_history()


@app.get("/runs/{run_id}", response_model=RunResponse)
def get_workflow_run(run_id: str):
    result = get_run(run_id)

    if not result.get("found", False):
        raise HTTPException(status_code=404, detail=f"run not found: {run_id}")

    return _build_run_response(result, include_state=True)


@app.get("/reports")
def list_markdown_reports():
    return list_reports()


@app.get("/reports/{report_name}")
def get_markdown_report(report_name: str):
    try:
        return get_report(report_name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
