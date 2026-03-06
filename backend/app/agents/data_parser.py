"""
DataParser Agent - Data Parsing and Schema Inference
Parses uploaded data files and extracts schema information

## 状态更新规范

遵循 Week 3-4 接口设计：
- 返回**新字典**，不直接修改 state
- 使用 create_completed_agents_update 防止重复
- 设置 parsed_schema（失败时设置空对象而非 None）
"""

import json
import os
from typing import Any, Dict, List, Optional

from app.agents.state import AgentState
from app.agents.base import create_completed_agents_update
from app.prompts.loader import get_system_prompt, get_prompt_template
from app.services.llm_service import get_llm_service


class DataParserAgent:
    """
    DataParser Agent - Responsible for parsing data files and inferring schema.
    
    职责：
    - 调用 LLM 生成解析代码
    - 通过 Sandbox 执行代码（未来实现）
    - 当前：直接调用 LLM 分析数据
    
    禁止：
    - 直接操作 pandas/numpy 或读取文件
    - 所有数据处理应在 sandbox 中执行
    
    ## 接口规范 (Week 3-4)
    """
    
    # 输入字段（必须存在于 state 中）
    REQUIRED_INPUTS: List[str] = ["file_path"]
    
    # 输出字段（Agent 会产出这些字段）
    OUTPUTS: List[str] = ["parsed_schema", "data_summary", "data_quality_report"]
    
    def __init__(self, llm_provider: Optional[str] = None):
        """
        Initialize DataParser Agent.
        
        Args:
            llm_provider: LLM provider to use (openai, anthropic, zhipu)
        """
        self.llm = get_llm_service(llm_provider)
        self.name = "data_parser"
    
    def _read_file_preview(self, file_path: str, max_lines: int = 20) -> str:
        """
        Read first N lines of file for preview.
        
        Args:
            file_path: Path to the file
            max_lines: Maximum number of lines to read
        
        Returns:
            File content preview as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.strip())
                return '\n'.join(lines)
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            break
                        lines.append(line.strip())
                    return '\n'.join(lines)
            except:
                return "[Unable to read file content]"
        except FileNotFoundError:
            return f"[File not found: {file_path}]"
        except Exception as e:
            return f"[Error reading file: {str(e)}]"
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic file information.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Dictionary with file information
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        return {
            "file_path": file_path,
            "file_extension": file_ext,
            "file_type": self._detect_file_type(file_ext),
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
        }
    
    def _detect_file_type(self, extension: str) -> str:
        """Detect file type from extension."""
        type_map = {
            '.csv': 'csv',
            '.xlsx': 'excel',
            '.xls': 'excel',
            '.json': 'json',
            '.txt': 'text',
            '.parquet': 'parquet',
        }
        return type_map.get(extension, 'unknown')
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response.
        
        Args:
            response: Raw LLM response
        
        Returns:
            Parsed JSON dictionary
        """
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                else:
                    json_str = response
            
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {}
    
    async def parse_file(self, state: AgentState) -> Dict[str, Any]:
        """
        Parse the data file and extract schema information.
        
        Args:
            state: Current agent state
        
        Returns:
            Dictionary containing parsed schema, summary, and quality report
        """
        file_path = state.get("file_path")
        if not file_path:
            return {
                "parsed_schema": None,
                "data_summary": None,
                "data_quality_report": None,
                "errors": ["No file path provided"],
            }
        
        file_info = self._get_file_info(file_path)
        file_preview = self._read_file_preview(file_path)
        
        # Load prompts from .md files
        system_prompt = get_system_prompt("data_parser")
        prompt_template = get_prompt_template("data_parser", "Data Parsing Prompt")
        
        # Build prompt for LLM
        prompt = prompt_template.format(
            file_path=file_path,
            file_type=file_info["file_type"],
            file_size_mb=file_info["file_size_mb"],
            file_preview=file_preview,
        )
        
        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
            )
            
            result = self._extract_json_from_response(response)
            
            parsed_schema = {
                "file_type": file_info["file_type"],
                "columns": result.get("columns", []),
                "column_types": result.get("column_types", {}),
                "row_count": result.get("row_count", 0),
                "column_count": len(result.get("columns", [])),
                "primary_keys": result.get("primary_keys", []),
                "datetime_columns": result.get("datetime_columns", []),
            }
            
            data_summary = {
                "numeric_stats": result.get("numeric_stats", {}),
                "categorical_stats": result.get("categorical_stats", {}),
                "missing_values": result.get("missing_values", {}),
                "sample_data": result.get("sample_data", []),
            }
            
            data_quality_report = {
                "overall_score": result.get("quality_score", 0),
                "issues": result.get("quality_issues", []),
                "recommendations": result.get("recommendations", []),
            }
            
            return {
                "parsed_schema": parsed_schema,
                "data_summary": data_summary,
                "data_quality_report": data_quality_report,
                "errors": [],
            }
            
        except Exception as e:
            return {
                "parsed_schema": None,
                "data_summary": None,
                "data_quality_report": None,
                "errors": [f"Error parsing file: {str(e)}"],
            }


async def data_parser_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node function for DataParser Agent.
    
    ## 状态更新规范（遵循 Week 3-4 接口）
    - 返回**新字典**，不直接修改 state
    - 使用 create_completed_agents_update 防止重复
    - 设置 parsed_schema（失败时设置空对象而非 None）
    - 有错误时添加到 errors
    
    Args:
        state: Current agent state
    
    Returns:
        更新后的状态字典
    """
    # 获取当前值（不修改原 state）
    current_step = state.get("step_count", 0) + 1
    completed = create_completed_agents_update(state, "data_parser")
    logs = state.get("execution_logs", []) + [
        "DataParser: Starting file parsing"
    ]
    
    # Create DataParser instance
    parser = DataParserAgent()
    
    # Parse the file
    result = await parser.parse_file(state)
    
    # 构建新状态字典
    new_state = {
        **state,
        "current_agent": "data_parser",
        "step_count": current_step,
        "completed_agents": completed,
        "execution_logs": logs,
    }
    
    # 更新结果 - 即使失败也要设置值，防止无限循环
    parsed_schema = result.get("parsed_schema")
    if parsed_schema:
        new_state["parsed_schema"] = parsed_schema
        new_state["data_summary"] = result.get("data_summary")
        new_state["data_quality_report"] = result.get("data_quality_report")
        new_state["execution_logs"] = new_state["execution_logs"] + [
            f"DataParser: Parsed {parsed_schema.get('column_count', 0)} columns",
            f"DataParser: Detected {parsed_schema.get('row_count', 0)} rows",
            f"DataParser: File type: {parsed_schema.get('file_type', 'unknown')}",
        ]
    else:
        # 失败时设置空对象，而不是保持 None
        new_state["parsed_schema"] = {
            "file_type": "unknown",
            "columns": [],
            "column_types": {},
            "row_count": 0,
            "column_count": 0,
            "parse_error": True,
        }
        new_state["data_summary"] = {}
        new_state["data_quality_report"] = {
            "overall_score": 0, 
            "issues": [], 
            "recommendations": []
        }
    
    # 处理错误
    if result.get("errors"):
        new_state["errors"] = state.get("errors", []) + result["errors"]
        new_state["execution_logs"] = new_state["execution_logs"] + [
            f"DataParser: Errors occurred: {result['errors']}"
        ]
    
    return new_state