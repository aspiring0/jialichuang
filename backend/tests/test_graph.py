"""
Tests for LangGraph Main Graph Definition
"""

import pytest

from app.agents.state import AgentState, create_initial_state
from app.agents.graph import (
    create_analysis_graph,
    route_from_supervisor,
    route_from_debugger,
    supervisor_node,
    data_parser_node,
    analysis_node,
    visualization_node,
    debugger_node,
)


class TestSupervisorNode:
    """Tests for supervisor_node function"""

    def test_supervisor_sets_current_agent(self):
        """Test that supervisor sets current_agent"""
        state = create_initial_state(user_query="test")
        result = supervisor_node(state)
        
        assert result["current_agent"] == "supervisor"

    def test_supervisor_adds_execution_log(self):
        """Test that supervisor adds execution log"""
        state = create_initial_state(user_query="test")
        result = supervisor_node(state)
        
        assert len(result["execution_logs"]) == 1
        assert "Supervisor" in result["execution_logs"][0]


class TestDataParserNode:
    """Tests for data_parser_node function"""

    def test_data_parser_sets_current_agent(self):
        """Test that data parser sets current_agent"""
        state = create_initial_state(user_query="test")
        result = data_parser_node(state)
        
        assert result["current_agent"] == "data_parser"

    def test_data_parser_adds_execution_log(self):
        """Test that data parser adds execution log"""
        state = create_initial_state(user_query="test")
        result = data_parser_node(state)
        
        assert len(result["execution_logs"]) == 1
        assert "DataParser" in result["execution_logs"][0]


class TestAnalysisNode:
    """Tests for analysis_node function"""

    def test_analysis_sets_current_agent(self):
        """Test that analysis sets current_agent"""
        state = create_initial_state(user_query="test")
        result = analysis_node(state)
        
        assert result["current_agent"] == "analysis"

    def test_analysis_adds_execution_log(self):
        """Test that analysis adds execution log"""
        state = create_initial_state(user_query="test")
        result = analysis_node(state)
        
        assert len(result["execution_logs"]) == 1
        assert "Analysis" in result["execution_logs"][0]


class TestVisualizationNode:
    """Tests for visualization_node function"""

    def test_visualization_sets_current_agent(self):
        """Test that visualization sets current_agent"""
        state = create_initial_state(user_query="test")
        result = visualization_node(state)
        
        assert result["current_agent"] == "visualization"

    def test_visualization_adds_execution_log(self):
        """Test that visualization adds execution log"""
        state = create_initial_state(user_query="test")
        result = visualization_node(state)
        
        assert len(result["execution_logs"]) == 1
        assert "Visualization" in result["execution_logs"][0]


class TestDebuggerNode:
    """Tests for debugger_node function"""

    def test_debugger_sets_current_agent(self):
        """Test that debugger sets current_agent"""
        state = create_initial_state(user_query="test")
        result = debugger_node(state)
        
        assert result["current_agent"] == "debugger"

    def test_debugger_adds_execution_log(self):
        """Test that debugger adds execution log"""
        state = create_initial_state(user_query="test")
        result = debugger_node(state)
        
        assert len(result["execution_logs"]) == 1
        assert "Debugger" in result["execution_logs"][0]


class TestRouteFromSupervisor:
    """Tests for route_from_supervisor function"""

    def test_routes_to_data_parser_when_file_no_schema(self):
        """Test routing to data_parser when file exists but no schema"""
        state = create_initial_state(user_query="test", file_path="/data/test.csv")
        result = route_from_supervisor(state)
        
        assert result == "data_parser"

    def test_routes_to_analysis_when_schema_no_results(self):
        """Test routing to analysis when schema exists but no results"""
        state = create_initial_state(user_query="test")
        state["parsed_schema"] = {"file_type": "csv", "columns": ["a"]}
        result = route_from_supervisor(state)
        
        assert result == "analysis"

    def test_routes_to_visualization_when_results_no_charts(self):
        """Test routing to visualization when results exist but no charts"""
        state = create_initial_state(user_query="test")
        state["parsed_schema"] = {"file_type": "csv", "columns": ["a"]}
        state["analysis_results"] = {"summary": "test"}
        result = route_from_supervisor(state)
        
        assert result == "visualization"

    def test_routes_to_end_when_complete(self):
        """Test routing to end when all processing is complete"""
        state = create_initial_state(user_query="test")
        state["parsed_schema"] = {"file_type": "csv", "columns": ["a"]}
        state["analysis_results"] = {"summary": "test"}
        state["echarts_configs"] = [{"type": "bar"}]
        result = route_from_supervisor(state)
        
        assert result == "end"

    def test_routes_to_debugger_when_errors_and_retries_left(self):
        """Test routing to debugger when errors exist and retries left"""
        state = create_initial_state(user_query="test")
        state["errors"] = ["some error"]
        state["retry_count"] = 0
        state["max_retries"] = 3
        result = route_from_supervisor(state)
        
        assert result == "debugger"


class TestRouteFromDebugger:
    """Tests for route_from_debugger function"""

    def test_routes_to_analysis_when_retries_left(self):
        """Test routing back to analysis when retries remaining"""
        state = create_initial_state(user_query="test")
        state["retry_count"] = 1
        state["max_retries"] = 3
        result = route_from_debugger(state)
        
        assert result == "analysis"

    def test_routes_to_end_when_max_retries_reached(self):
        """Test routing to end when max retries reached"""
        state = create_initial_state(user_query="test")
        state["retry_count"] = 3
        state["max_retries"] = 3
        result = route_from_debugger(state)
        
        assert result == "end"


class TestCreateAnalysisGraph:
    """Tests for create_analysis_graph function"""

    def test_creates_graph_successfully(self):
        """Test that graph is created without errors"""
        graph = create_analysis_graph()
        
        assert graph is not None

    def test_graph_can_invoke_with_initial_state(self):
        """Test that graph can be invoked with initial state"""
        graph = create_analysis_graph()
        state = create_initial_state(user_query="test query")
        
        # The graph should be executable
        result = graph.invoke(state)
        
        assert result is not None
        assert "execution_logs" in result

    def test_graph_execution_with_file_path(self):
        """Test graph execution with file path - simulates full flow"""
        graph = create_analysis_graph()
        state = create_initial_state(
            user_query="分析这个文件",
            file_path="/data/test.csv",
        )
        
        # Pre-populate state to avoid infinite loop with placeholder nodes
        # In real implementation, nodes would set these values
        state["parsed_schema"] = {"file_type": "csv", "columns": ["a", "b"]}
        state["analysis_results"] = {"summary": "test analysis"}
        state["echarts_configs"] = [{"type": "bar"}]
        
        result = graph.invoke(state)
        
        # Should have processed and completed
        assert result is not None
        assert "execution_logs" in result


class TestGraphNodes:
    """Tests for graph node execution"""

    def test_all_nodes_preserve_user_query(self):
        """Test that all nodes preserve the original user query"""
        original_query = "原始查询内容"
        
        for node_func in [supervisor_node, data_parser_node, analysis_node, 
                          visualization_node, debugger_node]:
            state = create_initial_state(user_query=original_query)
            result = node_func(state)
            assert result["user_query"] == original_query

    def test_nodes_accumulate_logs(self):
        """Test that multiple node calls accumulate logs"""
        state = create_initial_state(user_query="test")
        
        state = supervisor_node(state)
        state = data_parser_node(state)
        state = analysis_node(state)
        
        assert len(state["execution_logs"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])