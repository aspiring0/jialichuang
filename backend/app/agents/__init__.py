"""
Multi-Agent System for Data Analysis
Using LangGraph for agent orchestration
"""

from app.agents.state import AgentState

# 延迟导入 graph 以避免循环导入
def get_analysis_graph():
    """延迟加载分析图"""
    from app.agents.graph import create_analysis_graph
    return create_analysis_graph()

__all__ = ["AgentState", "get_analysis_graph"]
