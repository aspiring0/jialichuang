"""
Supervisor Agent - Central Orchestrator for Multi-Agent Data Analysis System
"""

import json
from typing import Any, Dict, List, Optional

from app.agents.state import AgentState
from app.prompts.supervisor import (
    SUPERVISOR_SYSTEM_PROMPT,
    SUPERVISOR_INTENT_PROMPT,
    SUPERVISOR_AGGREGATION_PROMPT,
)
from app.services.llm_service import get_llm_service


class SupervisorAgent:
    """
    Supervisor Agent - Central orchestrator that coordinates all other agents.
    
    Responsibilities:
    - Understand user intent from natural language queries
    - Decompose complex tasks into subtasks
    - Determine which agents to call and in what sequence
    - Aggregate results from all agents
    - Manage overall workflow execution
    """
    
    def __init__(self, llm_provider: Optional[str] = None):
        """
        Initialize Supervisor Agent.
        
        Args:
            llm_provider: LLM provider to use (openai, anthropic, zhipu)
        """
        self.llm = get_llm_service(llm_provider)
        self.name = "supervisor"
    
    async def analyze_intent(self, state: AgentState) -> Dict[str, Any]:
        """
        Analyze user query and determine intent.
        
        Args:
            state: Current agent state
        
        Returns:
            Dictionary containing intent analysis results
        """
        prompt = SUPERVISOR_INTENT_PROMPT.format(
            user_query=state.get("user_query", ""),
            has_file=state.get("file_path") is not None,
            has_schema=state.get("parsed_schema") is not None,
            has_analysis=state.get("analysis_results") is not None,
            has_charts=len(state.get("echarts_configs", [])) > 0,
        )
        
        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=SUPERVISOR_SYSTEM_PROMPT,
            temperature=0.3,  # Lower temperature for more deterministic intent classification
        )
        
        # Parse JSON response
        try:
            # Try to extract JSON from response
            json_str = self._extract_json(response)
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError:
            # Return default intent if parsing fails
            return self._get_default_intent(state)
    
    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from text that may contain markdown code blocks.
        
        Args:
            text: Text that may contain JSON
        
        Returns:
            Extracted JSON string
        """
        # Try to find JSON in markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        else:
            # Try to find JSON object directly
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                return text[start:end]
        return text
    
    def _get_default_intent(self, state: AgentState) -> Dict[str, Any]:
        """
        Get default intent based on current state.
        
        Args:
            state: Current agent state
        
        Returns:
            Default intent dictionary
        """
        agent_sequence = []
        
        if state.get("file_path") and not state.get("parsed_schema"):
            agent_sequence.append("data_parser")
        
        if not state.get("analysis_results"):
            agent_sequence.append("analysis")
        
        if not state.get("echarts_configs"):
            agent_sequence.append("visualization")
        
        return {
            "intent": "data_explore",
            "confidence": 0.5,
            "agent_sequence": agent_sequence,
            "task_plan": [
                {"agent": agent, "task": f"Execute {agent} tasks", "priority": i + 1}
                for i, agent in enumerate(agent_sequence)
            ],
            "reasoning": "Default intent based on state analysis",
        }
    
    async def aggregate_results(self, state: AgentState) -> Dict[str, Any]:
        """
        Aggregate results from all agents into final output.
        
        Args:
            state: Current agent state with all agent outputs
        
        Returns:
            Aggregated final output
        """
        prompt = SUPERVISOR_AGGREGATION_PROMPT.format(
            user_query=state.get("user_query", ""),
            schema=json.dumps(state.get("parsed_schema", {}), ensure_ascii=False, indent=2),
            analysis_results=json.dumps(state.get("analysis_results", {}), ensure_ascii=False, indent=2),
            charts=json.dumps(state.get("echarts_configs", []), ensure_ascii=False, indent=2),
        )
        
        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=SUPERVISOR_SYSTEM_PROMPT,
            temperature=0.5,
        )
        
        try:
            json_str = self._extract_json(response)
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError:
            return {
                "summary": "分析完成，请查看详细结果。",
                "key_findings": [],
                "insights": [],
                "recommendations": [],
                "raw_response": response,
            }
    
    def determine_next_agent(self, state: AgentState) -> Optional[str]:
        """
        Determine the next agent to call based on current state.
        
        Args:
            state: Current agent state
        
        Returns:
            Name of next agent to call, or None if done
        """
        # Check for errors that need debugging
        if state.get("errors") and len(state["errors"]) > 0:
            if state.get("retry_count", 0) < state.get("max_retries", 3):
                return "debugger"
        
        # Determine based on what's missing
        if state.get("file_path") and not state.get("parsed_schema"):
            return "data_parser"
        
        if state.get("parsed_schema") and not state.get("analysis_results"):
            return "analysis"
        
        if state.get("analysis_results") and not state.get("echarts_configs"):
            return "visualization"
        
        return None  # All done


async def supervisor_node(state: AgentState) -> AgentState:
    """
    LangGraph node function for Supervisor Agent.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated agent state
    """
    state["current_agent"] = "supervisor"
    state["execution_logs"] = state.get("execution_logs", []) + [
        "Supervisor: Starting orchestration"
    ]
    
    # Create supervisor instance
    supervisor = SupervisorAgent()
    
    # If this is the first call, analyze intent
    if not state.get("intent"):
        intent_result = await supervisor.analyze_intent(state)
        state["intent"] = intent_result.get("intent")
        state["agent_sequence"] = intent_result.get("agent_sequence", [])
        state["task_plan"] = intent_result.get("task_plan", [])
        
        state["execution_logs"] = state.get("execution_logs", []) + [
            f"Supervisor: Intent classified as '{state['intent']}'",
            f"Supervisor: Agent sequence: {state['agent_sequence']}"
        ]
    
    # Determine next agent
    next_agent = supervisor.determine_next_agent(state)
    state["next_agent"] = next_agent
    
    # If no next agent, aggregate results
    if next_agent is None:
        state["execution_logs"] = state.get("execution_logs", []) + [
            "Supervisor: All agents completed, aggregating results"
        ]
        
        final_output = await supervisor.aggregate_results(state)
        state["final_output"] = final_output
        state["success"] = True
        
        state["execution_logs"] = state.get("execution_logs", []) + [
            "Supervisor: Final output generated"
        ]
    else:
        state["execution_logs"] = state.get("execution_logs", []) + [
            f"Supervisor: Routing to {next_agent}"
        ]
    
    return state