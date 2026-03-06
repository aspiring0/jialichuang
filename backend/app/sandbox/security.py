"""
Security Checker - Code Safety Validation

Validates Python code before execution to prevent malicious operations.
"""

import ast
from typing import List, Set


class SecurityChecker:
    """
    代码安全检查器
    
    禁止以下操作：
    - 文件系统操作（os, shutil）
    - 网络操作（requests, socket）
    - 系统调用（subprocess）
    - 危险内置函数（eval, exec, compile）
    """
    
    # 完全禁止的模块
    FORBIDDEN_MODULES: Set[str] = {
        'os', 'sys', 'subprocess', 'socket', 
        'requests', 'urllib', 'shutil', 'threading',
        'multiprocessing', 'ctypes', 'pickle',
        'importlib', 'builtins', '__builtins__',
        'code', 'codeop', 'compile', 'exec',
    }
    
    # 禁止的内置函数
    FORBIDDEN_BUILTINS: Set[str] = {
        'eval', 'exec', 'compile', 'open', 
        '__import__', 'globals', 'locals', 'vars',
        'getattr', 'setattr', 'delattr', 'hasattr',
        'input', 'breakpoint',
    }
    
    # 允许使用的模块（数据分析相关）
    ALLOWED_MODULES: Set[str] = {
        'pandas', 'numpy', 'scipy', 'sklearn',
        'statistics', 'math', 'json', 're',
        'datetime', 'collections', 'itertools',
        'functools', 'typing', 'decimal', 'fractions',
    }
    
    def __init__(self):
        self.errors: List[str] = []
    
    def is_safe(self, code: str) -> bool:
        """
        检查代码是否安全
        
        Args:
            code: 要检查的 Python 代码
        
        Returns:
            True 如果代码安全，False 否则
        """
        self.errors = []
        
        # 1. 检查是否能解析为有效的 Python 代码
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.errors.append(f"语法错误: {e}")
            return False
        
        # 2. 遍历 AST 检查危险操作
        for node in ast.walk(tree):
            # 检查 import 语句
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module in self.FORBIDDEN_MODULES:
                        self.errors.append(f"禁止导入模块: {module}")
            
            # 检查 from ... import 语句
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    if module in self.FORBIDDEN_MODULES:
                        self.errors.append(f"禁止导入模块: {module}")
            
            # 检查函数调用
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in self.FORBIDDEN_BUILTINS:
                        self.errors.append(f"禁止使用函数: {func_name}")
                
                # 检查属性调用 (如 os.system)
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        module = node.func.value.id
                        if module in self.FORBIDDEN_MODULES:
                            self.errors.append(f"禁止调用 {module}.{node.func.attr}")
        
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """获取所有安全检查错误"""
        return self.errors
    
    def get_allowed_modules(self) -> Set[str]:
        """获取允许的模块列表"""
        return self.ALLOWED_MODULES.copy()