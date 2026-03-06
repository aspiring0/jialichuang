"""
快速pytest测试 - 带超时
"""
import subprocess
import sys

print("运行单个测试 (15秒超时)...")

result = subprocess.run(
    [sys.executable, "-m", "pytest", 
     "backend/tests/test_api.py::TestHealthEndpoints::test_liveness",
     "-v", "--tb=short"],
    capture_output=True,
    text=True,
    timeout=15,
    cwd="d:/Code/嘉立创"
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\n返回码: {result.returncode}")