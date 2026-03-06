"""
Agent State Definition for LangGraph
Defines the global state shared across all agents in the analysis workflow
"""

from typing import Annotated, Any, Dict, List, Optional, TypedDict

import operator


class DataSchema(TypedDict, total=False):
    """Data schema information extracted from uploaded file"""
    
    file_type: str  # csv, excel, json
    columns: List[str]  # column names
    column_types: Dict[str, str]  # column name -> data type
    row_count: int  # number of rows
    column_count: int  # number of columns
    primary_keys: Optional[List[str]]  # potential primary key columns
    datetime_columns: Optional[List[str]]  # datetime columns detected


class DataSummary(TypedDict, total=False):
    """Statistical summary of the data"""
    
    numeric_stats: Dict[str, Dict[str, float]]  # column -> {mean, std, min, max, etc.}
    categorical_stats: Dict[str, Dict[str, int]]  # column -> {value -> count}
    missing_values: Dict[str, int]  # column -> missing count
    sample_data: List[Dict[str, Any]]  # first N rows as sample


class DataQualityReport(TypedDict, total=False):
    """Data quality assessment report"""
    
    overall_score: float  # 0-100 quality score
    issues: List[Dict[str, Any]]  # list of quality issues found
    recommendations: List[str]  # recommendations for data cleaning


class ChartRecommendation(TypedDict, total=False):
    """Chart recommendation from Visualization Agent"""
    
    chart_type: str  # line, bar, pie, scatter, heatmap, etc.
    title: str  # chart title
    x_field: Optional[str]  # x-axis field
    y_fields: Optional[List[str]]  # y-axis fields
    reason: str  # why this chart is recommended


class AnalysisResult(TypedDict, total=False):
    """Analysis result from Analysis Agent"""
    
    summary: str  # text summary of analysis
    statistics: Dict[str, Any]  # statistical results
    insights: List[str]  # key insights discovered
    correlations: Optional[Dict[str, Any]]  # correlation analysis results


class AgentState(TypedDict):
    """
    Global state for the Multi-Agent Data Analysis system.
    
    This state is passed between agents in the LangGraph workflow.
    All agents can read from and write to this shared state.
    
    Using Annotated with operator.add for lists allows LangGraph to
    automatically merge list updates from parallel branches.
    """
    
    # ============================================
    # User Input
    # ============================================
    user_query: str  # User's natural language query
    file_path: Optional[str]  # Path to uploaded data file
    session_id: Optional[str]  # Session identifier for tracking
    
    # ============================================
    # Supervisor Agent State
    # ============================================
    task_plan: List[Dict[str, Any]]  # Decomposed task list
    current_task_index: int  # Index of current executing task
    agent_sequence: List[str]  # Ordered list of agents to execute
    intent: Optional[str]  # Classified user intent
    
    # ============================================
    # DataParser Agent Output
    # ============================================
    parsed_schema: Optional[DataSchema]  # Extracted data schema
    data_summary: Optional[DataSummary]  # Statistical summary
    data_quality_report: Optional[DataQualityReport]  # Quality assessment
    
    # ============================================
    # Analysis Agent Output
    # ============================================
    analysis_strategy: Optional[str]  # Generated analysis strategy
    generated_code: Optional[str]  # Generated Python code
    analysis_results: Optional[AnalysisResult]  # Analysis results
    code_execution_output: Optional[str]  # Raw output from code execution
    
    # ============================================
    # Visualization Agent Output
    # ============================================
    chart_recommendations: List[ChartRecommendation]  # Recommended charts
    echarts_configs: List[Dict[str, Any]]  # ECharts configuration objects
    
    # ============================================
    # Error Handling & Debugging
    # ============================================
    errors: Annotated[List[str], operator.add]  # Accumulated error messages
    retry_count: int  # Current retry count
    max_retries: int  # Maximum allowed retries (default: 3)
    debug_logs: Annotated[List[str], operator.add]  # Debug information
    
    # ============================================
    # Execution Control
    # ============================================
    execution_logs: Annotated[List[str], operator.add]  # Execution trace
    current_agent: Optional[str]  # Currently executing agent name
    next_agent: Optional[str]  # Next agent to execute
    
    # ============================================
    # Final Output
    # ============================================
    final_output: Optional[Dict[str, Any]]  # Final aggregated result
    success: bool  # Whether the workflow completed successfully


def create_initial_state(
    user_query: str,
    file_path: Optional[str] = None,
    session_id: Optional[str] = None,
) -> AgentState:
    """
    Create an initial AgentState with default values.
    
    Args:
        user_query: The user's natural language query
        file_path: Optional path to the data file
        session_id: Optional session identifier
    
    Returns:
        AgentState with initialized default values
    """
    return AgentState(
        # User Input
        user_query=user_query,
        file_path=file_path,
        session_id=session_id,
        
        # Supervisor
        task_plan=[],
        current_task_index=0,
        agent_sequence=[],
        intent=None,
        
        # DataParser
        parsed_schema=None,
        data_summary=None,
        data_quality_report=None,
        
        # Analysis
        analysis_strategy=None,
        generated_code=None,
        analysis_results=None,
        code_execution_output=None,
        
        # Visualization
        chart_recommendations=[],
        echarts_configs=[],
        
        # Error Handling
        errors=[],
        retry_count=0,
        max_retries=3,
        debug_logs=[],
        
        # Execution Control
        execution_logs=[],
        current_agent=None,
        next_agent=None,
        
        # Final Output
        final_output=None,
        success=False,
    )


def get_state_summary(state: AgentState) -> Dict[str, Any]:
    """
    Get a summary of the current state for logging/debugging.
    
    Args:
        state: Current AgentState
    
    Returns:
        Dictionary with key state information
    """
    return {
        "user_query": state.get("user_query", "")[:100],  # Truncate for readability
        "session_id": state.get("session_id"),
        "intent": state.get("intent"),
        "current_agent": state.get("current_agent"),
        "next_agent": state.get("next_agent"),
        "has_schema": state.get("parsed_schema") is not None,
        "has_analysis": state.get("analysis_results") is not None,
        "chart_count": len(state.get("echarts_configs", [])),
        "error_count": len(state.get("errors", [])),
        "retry_count": state.get("retry_count", 0),
        "success": state.get("success", False),
    }