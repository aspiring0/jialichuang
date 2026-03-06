"""
运行数据库测试
"""
import subprocess
import sys

print("运行数据库测试 (10秒超时)...")

result = subprocess.run(
    [sys.executable, "-m", "pytest", 
     "backend/tests/test_db_simple.py",
     "-v", "--tb=short"],
    capture_output=True,
    text=True,
    timeout=10,
    cwd="d:/Code/嘉立创"
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\n返回码: {result.returncode}")