"""
Agent Base - Base class and protocol for all agents

Defines the standard interface that all agents must follow.
"""

from typing import Dict, List, Protocol, Any, Optional
from app.agents.state import AgentState


class BaseAgent(Protocol):
    """
    Agent 基础接口协议
    
    所有 Agent 必须实现此接口。
    
    ## 状态更新规范
    
    Agent 必须返回 **新的状态字典**，而不是直接修改输入的 state。
    
    正确示例：
    ```python
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        return {
            **state,  # 保留原有状态
            "current_agent": self.name,
            "parsed_schema": result,  # 新增/更新字段
        }
    ```
    
    错误示例：
    ```python
    def __call__(self, state: AgentState) -> AgentState:
        state["parsed_schema"] = result  # 直接修改！这会导致问题
        return state
    ```
    """
    
    @property
    def name(self) -> str:
        """Agent 名称"""
        ...
    
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """
        执行 Agent 逻辑，返回更新后的状态字典
        
        Args:
            state: 当前全局状态
        
        Returns:
            包含更新的状态字典（会被 LangGraph 合并）
        """
        ...
    
    def get_required_inputs(self) -> List[str]:
        """返回此 Agent 需要的输入状态字段"""
        ...
    
    def get_outputs(self) -> List[str]:
        """返回此 Agent 产出的输出状态字段"""
        ...


class AgentResult:
    """
    Agent 执行结果封装
    
    提供标准化的结果格式，便于调试和追踪
    """
    
    def __init__(
        self,
        agent_name: str,
        success: bool,
        outputs: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
        logs: Optional[List[str]] = None,
    ):
        self.agent_name = agent_name
        self.success = success
        self.outputs = outputs or {}
        self.errors = errors or []
        self.logs = logs or []
    
    def to_state_update(self, state: AgentState) -> Dict[str, Any]:
        """
        转换为 LangGraph 状态更新格式
        
        Args:
            state: 当前状态
        
        Returns:
            状态更新字典
        """
        update = {
            # 保留原有状态
            **state,
            # 更新当前 agent
            "current_agent": self.agent_name,
            # 添加执行日志
            "execution_logs": state.get("execution_logs", []) + [
                f"[{self.agent_name}] {'Success' if self.success else 'Failed'}"
            ] + self.logs,
        }
        
        # 合并输出
        update.update(self.outputs)
        
        # 如果有错误，添加到错误列表
        if self.errors:
            update["errors"] = state.get("errors", []) + self.errors
        
        return update


def create_completed_agents_update(state: AgentState, agent_name: str) -> List[str]:
    """
    创建 completed_agents 的更新值
    
    ## 关键：防止重复添加
    
    这个函数确保每个 agent 只被添加一次到 completed_agents 列表。
    
    Args:
        state: 当前状态
        agent_name: 要添加的 agent 名称
    
    Returns:
        更新后的 completed_agents 列表
    """
    completed = state.get("completed_agents", [])
    if agent_name not in completed:
        return completed + [agent_name]
    return completed