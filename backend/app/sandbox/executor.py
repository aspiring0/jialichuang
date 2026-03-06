"""
Code Executor - Secure Python Code Execution

Executes Python code in a controlled environment for data analysis.
"""

import asyncio
import json
import traceback
from typing import Any, Dict, Optional

from app.sandbox.security import SecurityChecker


class CodeExecutor:
    """
    代码执行器
    
    职责：安全执行 Python 代码（本地模式）
    注意：生产环境应使用 Docker 容器隔离
    
    这是唯一可以执行 pandas/numpy 的地方
    """
    
    def __init__(
        self,
        timeout: int = 30,
        memory_limit_mb: int = 512,
    ):
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.security_checker = SecurityChecker()
    
    async def execute(
        self,
        code: str,
        file_path: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        在安全环境中执行代码
        
        Args:
            code: 要执行的 Python 代码
            file_path: 数据文件路径（可选）
            input_data: 输入数据（可选）
        
        Returns:
            {
                "success": bool,      # 执行是否成功
                "output": Any,        # 执行结果
                "error": str,         # 错误信息（如果失败）
                "logs": list[str],    # 执行日志
                "variables": dict,    # 执行后的变量
            }
        """
        result = {
            "success": False,
            "output": None,
            "error": None,
            "logs": [],
            "variables": {},
        }
        
        # 1. 安全检查
        if not self.security_checker.is_safe(code):
            result["error"] = f"代码安全检查失败: {self.security_checker.get_errors()}"
            result["logs"].append("Security check failed")
            return result
        
        result["logs"].append("Security check passed")
        
        # 2. 准备执行环境
        exec_globals = {
            "__builtins__": {
                "print": lambda *args, **kwargs: result["logs"].append(" ".join(str(a) for a in args)),
                "len": len,
                "range": range,
                "list": list,
                "dict": dict,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "None": None,
                "True": True,
                "False": False,
                "json": json,
            },
            "json": json,
        }
        
        # 导入允许的模块
        try:
            import pandas as pd
            import numpy as np
            exec_globals["pd"] = pd
            exec_globals["pandas"] = pd
            exec_globals["np"] = np
            exec_globals["numpy"] = np
            result["logs"].append("Imported pandas, numpy")
        except ImportError as e:
            result["error"] = f"导入依赖失败: {e}"
            return result
        
        # 如果有文件路径，注入 df 变量
        if file_path:
            try:
                exec_globals["df"] = exec_globals["pd"].read_csv(file_path)
                exec_globals["file_path"] = file_path
                result["logs"].append(f"Loaded file: {file_path}")
            except Exception as e:
                result["error"] = f"加载文件失败: {e}"
                return result
        
        # 如果有输入数据，注入
        if input_data:
            exec_globals.update(input_data)
            result["logs"].append(f"Injected {len(input_data)} input variables")
        
        # 3. 执行代码
        try:
            # 在事件循环中执行，带超时
            exec_result = await asyncio.wait_for(
                self._run_code(code, exec_globals),
                timeout=self.timeout
            )
            
            result["success"] = True
            result["output"] = exec_result
            result["logs"].append("Execution completed successfully")
            
            # 收集变量
            for key in ["schema", "summary", "results", "stats", "data", "analysis", "config"]:
                if key in exec_globals:
                    result["variables"][key] = self._serialize(exec_globals[key])
            
            # 收集 DataFrame 信息
            if "df" in exec_globals:
                df = exec_globals["df"]
                result["variables"]["df_info"] = {
                    "shape": list(df.shape),
                    "columns": list(df.columns),
                    "dtypes": {k: str(v) for k, v in df.dtypes.items()},
                }
            
        except asyncio.TimeoutError:
            result["error"] = f"执行超时（{self.timeout}秒）"
            result["logs"].append("Execution timed out")
        
        except Exception as e:
            result["error"] = f"执行错误: {str(e)}\n{traceback.format_exc()}"
            result["logs"].append(f"Execution failed: {e}")
        
        return result
    
    async def _run_code(self, code: str, exec_globals: Dict[str, Any]) -> Any:
        """在独立线程中执行代码"""
        loop = asyncio.get_event_loop()
        
        def run():
            local_vars = {}
            exec(code, exec_globals, local_vars)
            # 检查是否有返回值变量
            return exec_globals.get("result") or local_vars.get("result") or local_vars
        
        return await loop.run_in_executor(None, run)
    
    def _serialize(self, obj: Any) -> Any:
        """序列化对象为 JSON 兼容格式"""
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._serialize(item) for item in obj]
        
        # 处理 pandas DataFrame
        try:
            import pandas as pd
            if isinstance(obj, pd.DataFrame):
                return obj.to_dict(orient="records")[:100]  # 限制100行
            if isinstance(obj, pd.Series):
                return obj.tolist()
        except:
            pass
        
        # 处理 numpy 数组
        try:
            import numpy as np
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.integer, np.floating)):
                return obj.item()
        except:
            pass
        
        # 其他类型转为字符串
        return str(obj)


# 创建全局实例
_executor: Optional[CodeExecutor] = None


def get_executor() -> CodeExecutor:
    """获取全局代码执行器实例"""
    global _executor
    if _executor is None:
        _executor = CodeExecutor()
    return _executor