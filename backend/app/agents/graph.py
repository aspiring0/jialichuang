"""
LangGraph Main Graph Definition
Defines the multi-agent workflow for data analysis
"""

from typing import Literal

from langgraph.graph import END, StateGraph

from app.agents.state import AgentState


def supervisor_node(state: AgentState) -> AgentState:
    """
    Supervisor agent node - placeholder for now.
    Will be implemented in supervisor.py
    """
    state["current_agent"] = "supervisor"
    state["execution_logs"] = state.get("execution_logs", []) + ["Supervisor: Processing request"]
    return state


def data_parser_node(state: AgentState) -> AgentState:
    """
    Data parser agent node - placeholder for now.
    Will be implemented in data_parser.py
    """
    state["current_agent"] = "data_parser"
    state["execution_logs"] = state.get("execution_logs", []) + ["DataParser: Parsing data"]
    return state


def analysis_node(state: AgentState) -> AgentState:
    """
    Analysis agent node - placeholder for now.
    Will be implemented in analysis.py
    """
    state["current_agent"] = "analysis"
    state["execution_logs"] = state.get("execution_logs", []) + ["Analysis: Running analysis"]
    return state


def visualization_node(state: AgentState) -> AgentState:
    """
    Visualization agent node - placeholder for now.
    Will be implemented in visualization.py
    """
    state["current_agent"] = "visualization"
    state["execution_logs"] = state.get("execution_logs", []) + ["Visualization: Creating charts"]
    return state


def debugger_node(state: AgentState) -> AgentState:
    """
    Debugger agent node - placeholder for now.
    Will be implemented in debugger.py
    """
    state["current_agent"] = "debugger"
    state["execution_logs"] = state.get("execution_logs", []) + ["Debugger: Analyzing errors"]
    return state


def route_from_supervisor(state: AgentState) -> Literal["data_parser", "analysis", "visualization", "end"]:
    """
    Route from supervisor to the next agent based on state.
    """
    # Check if we have errors that need debugging
    if state.get("errors") and len(state["errors"]) > 0:
        if state.get("retry_count", 0) < state.get("max_retries", 3):
            return "debugger"
    
    # Simple routing logic based on what's needed
    if state.get("file_path") and not state.get("parsed_schema"):
        return "data_parser"
    
    if state.get("parsed_schema") and not state.get("analysis_results"):
        return "analysis"
    
    if state.get("analysis_results") and not state.get("echarts_configs"):
        return "visualization"
    
    return "end"


def route_from_debugger(state: AgentState) -> Literal["analysis", "end"]:
    """
    Route from debugger - either retry or give up.
    """
    if state.get("retry_count", 0) >= state.get("max_retries", 3):
        return "end"
    return "analysis"


def create_analysis_graph() -> StateGraph:
    """
    Create the main analysis graph with all agents.
    
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
    
    # Add edges for linear flow
    workflow.add_edge("data_parser", "supervisor")
    workflow.add_edge("analysis", "supervisor")
    workflow.add_edge("visualization", "supervisor")
    
    # Debugger can retry or end
    workflow.add_conditional_edges(
        "debugger",
        route_from_debugger,
        {
            "analysis": "analysis",
            "end": END,
        },
    )
    
    return workflow.compile()


# Graph instance for easy import
analysis_graph = create_analysis_graph()