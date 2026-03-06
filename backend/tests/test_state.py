"""
Tests for Agent State Definition
"""

import pytest

from app.agents.state import (
    AgentState,
    ChartRecommendation,
    DataQualityReport,
    DataSchema,
    DataSummary,
    AnalysisResult,
    create_initial_state,
    get_state_summary,
)


class TestDataSchema:
    """Tests for DataSchema TypedDict"""

    def test_data_schema_creation(self):
        """Test creating a valid DataSchema"""
        schema: DataSchema = {
            "file_type": "csv",
            "columns": ["id", "name", "value"],
            "column_types": {"id": "int", "name": "str", "value": "float"},
            "row_count": 100,
            "column_count": 3,
            "primary_keys": ["id"],
            "datetime_columns": [],
        }
        
        assert schema["file_type"] == "csv"
        assert len(schema["columns"]) == 3
        assert schema["row_count"] == 100


class TestDataSummary:
    """Tests for DataSummary TypedDict"""

    def test_data_summary_creation(self):
        """Test creating a valid DataSummary"""
        summary: DataSummary = {
            "numeric_stats": {
                "value": {"mean": 50.5, "std": 10.2, "min": 1.0, "max": 100.0}
            },
            "categorical_stats": {
                "category": {"A": 30, "B": 40, "C": 30}
            },
            "missing_values": {"id": 0, "name": 5, "value": 2},
            "sample_data": [{"id": 1, "name": "test", "value": 1.5}],
        }
        
        assert summary["numeric_stats"]["value"]["mean"] == 50.5
        assert summary["missing_values"]["name"] == 5


class TestDataQualityReport:
    """Tests for DataQualityReport TypedDict"""

    def test_quality_report_creation(self):
        """Test creating a valid DataQualityReport"""
        report: DataQualityReport = {
            "overall_score": 85.5,
            "issues": [
                {"column": "name", "type": "missing_values", "count": 5}
            ],
            "recommendations": ["Consider filling missing values in 'name' column"],
        }
        
        assert report["overall_score"] == 85.5
        assert len(report["issues"]) == 1


class TestChartRecommendation:
    """Tests for ChartRecommendation TypedDict"""

    def test_chart_recommendation_creation(self):
        """Test creating a valid ChartRecommendation"""
        rec: ChartRecommendation = {
            "chart_type": "bar",
            "title": "Sales by Category",
            "x_field": "category",
            "y_fields": ["sales"],
            "reason": "Bar chart is ideal for comparing categorical data",
        }
        
        assert rec["chart_type"] == "bar"
        assert rec["x_field"] == "category"


class TestAnalysisResult:
    """Tests for AnalysisResult TypedDict"""

    def test_analysis_result_creation(self):
        """Test creating a valid AnalysisResult"""
        result: AnalysisResult = {
            "summary": "The data shows increasing trend in sales",
            "statistics": {"mean": 100, "median": 95},
            "insights": ["Sales peaked in Q4", "Category A leads in revenue"],
            "correlations": {"price": {"sales": -0.3}},
        }
        
        assert result["summary"] == "The data shows increasing trend in sales"
        assert len(result["insights"]) == 2


class TestCreateInitialState:
    """Tests for create_initial_state function"""

    def test_create_minimal_state(self):
        """Test creating state with minimal required fields"""
        state = create_initial_state(user_query="分析这份数据")
        
        assert state["user_query"] == "分析这份数据"
        assert state["file_path"] is None
        assert state["session_id"] is None
        assert state["task_plan"] == []
        assert state["current_task_index"] == 0
        assert state["agent_sequence"] == []
        assert state["intent"] is None
        assert state["parsed_schema"] is None
        assert state["data_summary"] is None
        assert state["data_quality_report"] is None
        assert state["analysis_strategy"] is None
        assert state["generated_code"] is None
        assert state["analysis_results"] is None
        assert state["code_execution_output"] is None
        assert state["chart_recommendations"] == []
        assert state["echarts_configs"] == []
        assert state["errors"] == []
        assert state["retry_count"] == 0
        assert state["max_retries"] == 3
        assert state["debug_logs"] == []
        assert state["execution_logs"] == []
        assert state["current_agent"] is None
        assert state["next_agent"] is None
        assert state["final_output"] is None
        assert state["success"] is False

    def test_create_state_with_file(self):
        """Test creating state with file path"""
        state = create_initial_state(
            user_query="分析这个CSV文件",
            file_path="/data/sales.csv",
        )
        
        assert state["user_query"] == "分析这个CSV文件"
        assert state["file_path"] == "/data/sales.csv"

    def test_create_state_with_session(self):
        """Test creating state with session ID"""
        state = create_initial_state(
            user_query="帮我看看数据",
            session_id="test-session-123",
        )
        
        assert state["session_id"] == "test-session-123"

    def test_create_state_full(self):
        """Test creating state with all parameters"""
        state = create_initial_state(
            user_query="分析销售数据趋势",
            file_path="/data/sales_2024.csv",
            session_id="session-456",
        )
        
        assert state["user_query"] == "分析销售数据趋势"
        assert state["file_path"] == "/data/sales_2024.csv"
        assert state["session_id"] == "session-456"


class TestGetStateSummary:
    """Tests for get_state_summary function"""

    def test_summary_minimal_state(self):
        """Test summary of minimal state"""
        state = create_initial_state(user_query="测试查询")
        summary = get_state_summary(state)
        
        assert summary["user_query"] == "测试查询"
        assert summary["session_id"] is None
        assert summary["intent"] is None
        assert summary["current_agent"] is None
        assert summary["next_agent"] is None
        assert summary["has_schema"] is False
        assert summary["has_analysis"] is False
        assert summary["chart_count"] == 0
        assert summary["error_count"] == 0
        assert summary["retry_count"] == 0
        assert summary["success"] is False

    def test_summary_truncates_long_query(self):
        """Test that long queries are truncated"""
        long_query = "这是一个非常非常长的查询" * 20  # 180+ chars
        state = create_initial_state(user_query=long_query)
        summary = get_state_summary(state)
        
        assert len(summary["user_query"]) == 100

    def test_summary_with_data(self):
        """Test summary with populated state"""
        state = create_initial_state(
            user_query="分析数据",
            session_id="test-789",
        )
        state["intent"] = "trend_analysis"
        state["current_agent"] = "analysis"
        state["next_agent"] = "visualization"
        state["parsed_schema"] = {"file_type": "csv", "columns": ["a", "b"]}
        state["analysis_results"] = {"summary": "test"}
        state["echarts_configs"] = [{"type": "bar"}, {"type": "line"}]
        state["errors"] = ["minor error"]
        state["retry_count"] = 1
        state["success"] = True
        
        summary = get_state_summary(state)
        
        assert summary["session_id"] == "test-789"
        assert summary["intent"] == "trend_analysis"
        assert summary["current_agent"] == "analysis"
        assert summary["next_agent"] == "visualization"
        assert summary["has_schema"] is True
        assert summary["has_analysis"] is True
        assert summary["chart_count"] == 2
        assert summary["error_count"] == 1
        assert summary["retry_count"] == 1
        assert summary["success"] is True


class TestAgentStateMutation:
    """Tests for AgentState mutation behavior"""

    def test_list_accumulation(self):
        """Test that list fields can be accumulated"""
        state = create_initial_state(user_query="test")
        
        # Simulate adding errors
        state["errors"] = state.get("errors", []) + ["error1"]
        state["errors"] = state.get("errors", []) + ["error2"]
        
        assert len(state["errors"]) == 2
        assert state["errors"][0] == "error1"
        assert state["errors"][1] == "error2"

    def test_execution_log_accumulation(self):
        """Test that execution logs can be accumulated"""
        state = create_initial_state(user_query="test")
        
        state["execution_logs"] = state.get("execution_logs", []) + ["Starting analysis"]
        state["execution_logs"] = state.get("execution_logs", []) + ["Parsing data"]
        
        assert len(state["execution_logs"]) == 2

    def test_state_update_preserves_other_fields(self):
        """Test that updating one field doesn't affect others"""
        state = create_initial_state(
            user_query="original query",
            session_id="original-session",
        )
        
        # Update one field
        state["intent"] = "new_intent"
        state["retry_count"] = 5
        
        # Other fields should remain
        assert state["user_query"] == "original query"
        assert state["session_id"] == "original-session"
        assert state["max_retries"] == 3  # Default value preserved


if __name__ == "__main__":
    pytest.main([__file__, "-v"])