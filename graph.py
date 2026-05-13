from typing import TypedDict
import warnings

from langchain_core._api.deprecation import LangChainPendingDeprecationWarning

warnings.filterwarnings("ignore", category=LangChainPendingDeprecationWarning)

from langgraph.graph import END, START, StateGraph

from agents import coder_agent, product_agent, sentry_agent, tester_agent
from utils.code_runner import run_code, save_code


class AgentState(TypedDict):
    requirement: str
    product_result: str
    code: str
    tester_result: str
    stdout: str
    error_log: str
    sentry_result: str
    retry_count: int
    success: bool


def product_node(state):
    state["product_result"] = product_agent(state["requirement"])
    return state


def coder_node(state):
    if state["error_log"] and not state["success"]:
        state["code"] = coder_agent(
            state["product_result"],
            code=state["code"],
            error_log=state["error_log"],
            sentry_result=state["sentry_result"],
        )
    else:
        state["code"] = coder_agent(state["product_result"])

    return state


def tester_node(state):
    state["tester_result"] = tester_agent(state["code"])
    return state


def sentry_node(state):
    state["sentry_result"] = sentry_agent(state["code"], state["error_log"])
    state["retry_count"] = state["retry_count"] + 1
    return state


def runner_node(state):
    save_code(state["code"])
    run_result = run_code()
    state["stdout"] = run_result["stdout"]
    state["error_log"] = run_result["stderr"]
    state["success"] = run_result["returncode"] == 0
    return state


def should_continue(state):
    if state["success"]:
        return "end"

    if state["retry_count"] >= 3:
        return "end"

    return "repair"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("product_node", product_node)
    graph.add_node("coder_node", coder_node)
    graph.add_node("tester_node", tester_node)
    graph.add_node("sentry_node", sentry_node)
    graph.add_node("runner_node", runner_node)

    graph.add_edge(START, "product_node")
    graph.add_edge("product_node", "coder_node")
    graph.add_edge("coder_node", "tester_node")
    graph.add_edge("tester_node", "runner_node")
    graph.add_conditional_edges(
        "runner_node",
        should_continue,
        {
            "end": END,
            "repair": "sentry_node",
        },
    )
    graph.add_edge("sentry_node", "coder_node")

    return graph.compile()


def run_graph_demo(requirement, progress_callback=None):
    app = build_graph()
    state = {
        "requirement": requirement,
        "product_result": "",
        "code": "",
        "tester_result": "",
        "stdout": "",
        "error_log": "",
        "sentry_result": "",
        "retry_count": 0,
        "success": False,
    }

    if progress_callback:
        result = state
        for event in app.stream(state):
            for node_name, node_state in event.items():
                result = node_state
                progress_callback(node_name, result)
    else:
        result = app.invoke(state)

    return result
