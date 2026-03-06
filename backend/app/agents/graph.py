"""
LangGraph Main Graph Definition
Defines the multi-agent workflow for data analysis

## 防止无限重入的机制

1. **completed_agents 追踪**: 每个 agent 完成后添加到列表（使用去重函数）
2. **step_count 计数器**: 每次路由递增，超过 max_steps 强制结束
3. **双重检查**: 结果状态 + 完成状态综合判断
4. **错误恢复**: 错误时设置标记而不是保持 None，防止重复路由
5. **返回新字典**: 所有节点返回新字典，不直接修改 state
"""

from typing import Literal

from langgraph.graph import END, StateGraph

from app.agents.state import AgentState
from app.agents.base import create_completed_agents_update
from app.agents.supervisor import supervisor_node
from app.agents.data_parser import data_parser_node


def analysis_node(state: AgentState) -> AgentState:
    """
    Analysis agent node - placeholder for now.
    Will be implemented in analysis.py
    
    ## 状态更新规范
    - 返回**新字典**，不直接修改 state
    - 使用 create_completed_agents_update 防止重复
    - 设置 analysis_results（即使失败也要设置标记）
    """
    # 获取当前值（不修改原 state）
    current_step = state.get("step_count", 0) + 1
    completed = create_completed_agents_update(state, "analysis")
    logs = state.get("execution_logs", []) + ["Analysis: Running analysis"]
    
    # 返回新的状态字典
    return {
        **state,
        "current_agent": "analysis",
        "step_count": current_step,
        "completed_agents": completed,
        "execution_logs": logs,
        # 设置占位结果 - 即使是占位也要设置，防止无限循环
        "analysis_results": {
            "status": "completed",
            "summary": "Analysis placeholder - will be implemented",
            "insights": ["Analysis placeholder - will be implemented"],
            "statistics": {},
        },
    }


def visualization_node(state: AgentState) -> AgentState:
    """
    Visualization agent node - placeholder for now.
    Will be implemented in visualization.py
    
    ## 状态更新规范
    - 返回**新字典**，不直接修改 state
    - 使用 create_completed_agents_update 防止重复
    - 设置 echarts_configs（必须是 List 类型）
    """
    # 获取当前值（不修改原 state）
    current_step = state.get("step_count", 0) + 1
    completed = create_completed_agents_update(state, "visualization")
    logs = state.get("execution_logs", []) + ["Visualization: Creating charts"]
    
    # 返回新的状态字典
    return {
        **state,
        "current_agent": "visualization",
        "step_count": current_step,
        "completed_agents": completed,
        "execution_logs": logs,
        # 设置占位结果 - 使用 List 类型
        "echarts_configs": [
            {
                "status": "completed",
                "title": {"text": "Visualization placeholder"},
                "placeholder": True,
            }
        ],
    }


def debugger_node(state: AgentState) -> AgentState:
    """
    Debugger agent node - placeholder for now.
    Will be implemented in debugger.py
    
    ## 状态更新规范
    - 返回**新字典**，不直接修改 state
    - 使用 create_completed_agents_update 防止重复
    - 增加 retry_count
    - 清除 errors（可选，取决于调试结果）
    """
    # 获取当前值（不修改原 state）
    current_step = state.get("step_count", 0) + 1
    current_retry = state.get("retry_count", 0) + 1
    completed = create_completed_agents_update(state, "debugger")
    logs = state.get("execution_logs", []) + ["Debugger: Analyzing errors"]
    
    # 新状态字典
    new_state = {
        **state,
        "current_agent": "debugger",
        "step_count": current_step,
        "completed_agents": completed,
        "retry_count": current_retry,
        "execution_logs": logs,
    }
    
    # 如果达到最大重试次数，清除错误以允许流程继续
    max_retries = state.get("max_retries", 3)
    if current_retry >= max_retries:
        new_state["execution_logs"] = logs + [
            "Debugger: Max retries reached, clearing errors to proceed"
        ]
        new_state["errors"] = []
    
    return new_state


def _is_agent_completed(state: AgentState, agent_name: str) -> bool:
    """
    检查 agent 是否已完成（防止重复执行）
    
    Args:
        state: 当前状态
        agent_name: agent 名称
    
    Returns:
        是否已完成
    """
    completed = state.get("completed_agents", [])
    return agent_name in completed


def _should_terminate(state: AgentState) -> bool:
    """
    检查是否应该终止执行（循环防护）
    
    Args:
        state: 当前状态
    
    Returns:
        是否应该终止
    """
    step_count = state.get("step_count", 0)
    max_steps = state.get("max_steps", 20)
    
    if step_count >= max_steps:
        return True
    
    # 检查是否所有必要 agent 都已完成
    has_file = state.get("file_path") is not None
    has_schema = state.get("parsed_schema") is not None
    has_analysis = state.get("analysis_results") is not None
    has_charts = len(state.get("echarts_configs", [])) > 0
    
    # 如果没有文件，只需要分析结果
    if not has_file:
        return has_analysis
    
    # 如果有文件，需要 schema、分析和图表
    return has_schema and has_analysis and has_charts


def route_from_supervisor(state: AgentState) -> Literal["data_parser", "analysis", "visualization", "debugger", "end"]:
    """
    从 supervisor 路由到下一个 agent
    
    ## 路由逻辑（防止无限循环）
    
    1. 首先检查 step_count 是否超限
    2. 检查 retry_count 是否超限
    3. 如果有错误且未超重试限制，路由到 debugger
    4. 按顺序检查各 agent 是否需要执行（且未执行过）
    5. 所有任务完成则结束
    """
    # 获取当前步骤（路由不增加 step_count，节点才增加）
    current_step = state.get("step_count", 0)
    
    # 调试日志
    print(f"[ROUTER] Step {current_step}: "
          f"completed={state.get('completed_agents', [])}, "
          f"has_schema={bool(state.get('parsed_schema'))}, "
          f"has_analysis={bool(state.get('analysis_results'))}, "
          f"charts={len(state.get('echarts_configs', []))}, "
          f"errors={len(state.get('errors', []))}, "
          f"retry={state.get('retry_count', 0)}/{state.get('max_retries', 3)}")
    
    # 硬限制 1：最大步骤数检查
    max_steps = state.get("max_steps", 20)
    if current_step >= max_steps:
        print(f"[ROUTER] Max steps ({max_steps}) reached, ending")
        return "end"
    
    # 硬限制 2：最大重试次数检查
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)
    if retry_count >= max_retries:
        print(f"[ROUTER] Max retries ({max_retries}) reached")
        # 清除错误以允许流程继续
        if state.get("errors"):
            print("[ROUTER] Clearing errors after max retries")
    
    # 检查是否需要调试（有错误且 debugger 未执行过）
    if state.get("errors") and len(state["errors"]) > 0:
        if retry_count < max_retries and not _is_agent_completed(state, "debugger"):
            print("[ROUTER] Errors detected, routing to debugger")
            return "debugger"
    
    # 按顺序检查各 agent
    
    # 1. DataParser: 有文件且未解析，且 data_parser 未执行过
    if state.get("file_path") and not state.get("parsed_schema"):
        if not _is_agent_completed(state, "data_parser"):
            print("[ROUTER] Routing to data_parser")
            return "data_parser"
        else:
            print("[ROUTER] data_parser already completed, skipping")
    
    # 2. Analysis: schema 已解析或无文件，且 analysis 未执行过
    has_schema_or_no_file = state.get("parsed_schema") or not state.get("file_path")
    if has_schema_or_no_file and not state.get("analysis_results"):
        if not _is_agent_completed(state, "analysis"):
            print("[ROUTER] Routing to analysis")
            return "analysis"
        else:
            print("[ROUTER] analysis already completed, skipping")
    
    # 3. Visualization: analysis 已完成，且 visualization 未执行过
    if state.get("analysis_results") and len(state.get("echarts_configs", [])) == 0:
        if not _is_agent_completed(state, "visualization"):
            print("[ROUTER] Routing to visualization")
            return "visualization"
        else:
            print("[ROUTER] visualization already completed, skipping")
    
    # 所有任务完成
    print("[ROUTER] All tasks completed or agents exhausted, ending")
    return "end"


def create_analysis_graph() -> StateGraph:
    """
    Create the main analysis graph with all agents.
    
    ## 图结构说明
    
    ```
    START -> supervisor -> [data_parser | analysis | visualization | debugger | END]
                  ^                    |
                  |____________________|
                  (循环直到完成)
    ```
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph with AgentState
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("data_parser", data_parser_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("visualization", visualization_node)
    workflow.add_node("debugger", debugger_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add conditional edges from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "data_parser": "data_parser",
            "analysis": "analysis",
            "visualization": "visualization",
            "debugger": "debugger",
            "end": END,
        },
    )
    
    # All agents return to supervisor for routing decision
    workflow.add_edge("data_parser", "supervisor")
    workflow.add_edge("analysis", "supervisor")
    workflow.add_edge("visualization", "supervisor")
    workflow.add_edge("debugger", "supervisor")
    
    return workflow.compile()


# Graph instance for easy import
analysis_graph = create_analysis_graph()