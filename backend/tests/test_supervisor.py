"""
Tests for Supervisor Agent
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.state import create_initial_state
from app.agents.supervisor import SupervisorAgent, supervisor_node


class TestSupervisorAgent:
    """Tests for SupervisorAgent class"""

    def test_extract_json_from_markdown_block(self):
        """Test extracting JSON from markdown code block"""
        supervisor = SupervisorAgent.__new__(SupervisorAgent)
        
        text = '''```json
{"intent": "test", "confidence": 0.9}
```'''
        result = supervisor._extract_json(text)
        assert result == '{"intent": "test", "confidence": 0.9}'

    def test_extract_json_from_plain_block(self):
        """Test extracting JSON from plain code block"""
        supervisor = SupervisorAgent.__new__(SupervisorAgent)
        
        text = '''```
{"intent": "analysis"}
```'''
        result = supervisor._extract_json(text)
        assert result == '{"intent": "analysis"}'

    def test_extract_json_from_raw_text(self):
        """Test extracting JSON from raw text"""
        supervisor = SupervisorAgent.__new__(SupervisorAgent)
        
        text = 'Here is the result: {"key": "value"} and more text'
        result = supervisor._extract_json(text)
        assert result == '{"key": "value"}'

    def test_get_default_intent_with_file(self):
        """Test default intent when file is present"""
        supervisor = SupervisorAgent.__new__(SupervisorAgent)
        
        state = create_initial_state(
            user_query="分析这个文件",
            file_path="/data/test.csv",
        )
        
        result = supervisor._get_default_intent(state)
        
        assert result["intent"] == "data_explore"
        assert "data_parser" in result["agent_sequence"]
        assert "analysis" in result["agent_sequence"]
        assert "visualization" in result["agent_sequence"]

    def test_get_default_intent_with_schema(self):
        """Test default intent when schema is already parsed"""
        supervisor = SupervisorAgent.__new__(SupervisorAgent)
        
        state = create_initial_state(user_query="继续分析")
        state["parsed_schema"] = {"file_type": "csv", "columns": ["a"]}
        
        result = supervisor._get_default_intent(state)
        
        assert "data_parser" not in result["agent_sequence"]
        assert "analysis" in result["agent_sequence"]

    def test_determine_next_agent_needs_parsing(self):
        """Test routing to data_parser when file needs parsing"""
        supervisor = SupervisorAgent.__new__(SupervisorAgent)
        
        state = create_initial_state(
            user_query="分析数据",
            file_path="/data/test.csv",
        )
        
        result = supervisor.determine_next_agent(state)
        assert result == "data_parser"

    def test_determine_next_agent_needs_analysis(self):
        """Test routing to analysis when schema exists but no results"""
        supervisor = SupervisorAgent.__new__(SupervisorAgent)
        
        state = create_initial_state(user_query="分析数据")
        state["parsed_schema"] = {"file_type": "csv", "columns": ["a"]}
        
        result = supervisor.determine_next_agent(state)
        assert result == "analysis"

    def test_determine_next_agent_needs_visualization(self):
        """Test routing to visualization when analysis is done"""
        supervisor = SupervisorAgent.__new__(SupervisorAgent)
        
        state = create_initial_state(user_query="分析数据")
        state["parsed_schema"] = {"file_type": "csv", "columns": ["a"]}
        state["analysis_results"] = {"summary": "test"}
        
        result = supervisor.determine_next_agent(state)
        assert result == "visualization"

    def test_determine_next_agent_needs_debugger(self):
        """Test routing to debugger when errors exist"""
        supervisor = SupervisorAgent.__new__(SupervisorAgent)
        
        state = create_initial_state(user_query="分析数据")
        state["errors"] = ["some error"]
        state["retry_count"] = 0
        state["max_retries"] = 3
        
        result = supervisor.determine_next_agent(state)
        assert result == "debugger"

    def test_determine_next_agent_complete(self):
        """Test returning None when all processing is complete"""
        supervisor = SupervisorAgent.__new__(SupervisorAgent)
        
        state = create_initial_state(user_query="分析数据")
        state["parsed_schema"] = {"file_type": "csv", "columns": ["a"]}
        state["analysis_results"] = {"summary": "test"}
        state["echarts_configs"] = [{"type": "bar"}]
        
        result = supervisor.determine_next_agent(state)
        assert result is None


class TestSupervisorNode:
    """Tests for supervisor_node function"""

    @pytest.mark.asyncio
    async def test_supervisor_node_sets_current_agent(self):
        """Test that supervisor node sets current_agent"""
        state = create_initial_state(
            user_query="测试查询",
            file_path="/data/test.csv",
        )
        # Pre-populate to complete immediately
        state["parsed_schema"] = {"file_type": "csv"}
        state["analysis_results"] = {"summary": "test"}
        state["echarts_configs"] = [{"type": "bar"}]
        
        mock_llm = AsyncMock()
        mock_llm.generate.return_value = json.dumps({
            "summary": "测试摘要",
            "key_findings": [],
            "insights": [],
            "recommendations": []
        })
        
        with patch('app.agents.supervisor.get_llm_service', return_value=mock_llm):
            result = await supervisor_node(state)
        
        assert result["current_agent"] == "supervisor"

    @pytest.mark.asyncio
    async def test_supervisor_node_adds_execution_logs(self):
        """Test that supervisor node adds execution logs"""
        state = create_initial_state(user_query="测试查询")
        state["parsed_schema"] = {"file_type": "csv"}
        state["analysis_results"] = {"summary": "test"}
        state["echarts_configs"] = [{"type": "bar"}]
        
        mock_llm = AsyncMock()
        mock_llm.generate.return_value = json.dumps({
            "summary": "测试摘要",
            "key_findings": [],
            "insights": [],
            "recommendations": []
        })
        
        with patch('app.agents.supervisor.get_llm_service', return_value=mock_llm):
            result = await supervisor_node(state)
        
        assert len(result["execution_logs"]) > 0
        assert any("Supervisor" in log for log in result["execution_logs"])

    def test_supervisor_node_is_coroutine(self):
        """Test that supervisor_node is an async function"""
        import inspect
        assert inspect.iscoroutinefunction(supervisor_node)


class TestSupervisorAgentIntegration:
    """Integration tests for SupervisorAgent with mocked LLM"""

    @pytest.mark.asyncio
    async def test_analyze_intent_with_mock_llm(self):
        """Test intent analysis with mocked LLM response"""
        mock_llm = AsyncMock()
        mock_llm.generate.return_value = json.dumps({
            "intent": "trend_analysis",
            "confidence": 0.95,
            "agent_sequence": ["data_parser", "analysis", "visualization"],
            "task_plan": [
                {"agent": "data_parser", "task": "Parse data", "priority": 1}
            ],
            "reasoning": "User wants trend analysis"
        })
        
        with patch('app.agents.supervisor.get_llm_service', return_value=mock_llm):
            supervisor = SupervisorAgent()
            state = create_initial_state(user_query="分析销售趋势")
            
            result = await supervisor.analyze_intent(state)
            
            assert result["intent"] == "trend_analysis"
            assert result["confidence"] == 0.95
            assert "data_parser" in result["agent_sequence"]

    @pytest.mark.asyncio
    async def test_aggregate_results_with_mock_llm(self):
        """Test result aggregation with mocked LLM"""
        mock_llm = AsyncMock()
        mock_llm.generate.return_value = json.dumps({
            "summary": "销售数据呈现上升趋势",
            "key_findings": ["Q4销售额最高", "同比增长15%"],
            "insights": ["节假日效应明显"],
            "recommendations": ["增加Q4库存"]
        })
        
        with patch('app.agents.supervisor.get_llm_service', return_value=mock_llm):
            supervisor = SupervisorAgent()
            state = create_initial_state(user_query="分析销售")
            state["parsed_schema"] = {"columns": ["date", "sales"]}
            state["analysis_results"] = {"summary": "趋势向上"}
            state["echarts_configs"] = [{"type": "line"}]
            
            result = await supervisor.aggregate_results(state)
            
            assert "summary" in result
            assert len(result["key_findings"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])