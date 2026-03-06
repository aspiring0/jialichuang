"""
简单的测试运行脚本 - 诊断pytest问题
"""
import sys
import subprocess

print("=" * 50)
print("测试诊断脚本")
print("=" * 50)

# 测试1: 检查pytest是否可用
print("\n1. 检查pytest...")
try:
    result = subprocess.run(
        ["pytest", "--version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"   ✅ pytest版本: {result.stdout.strip()}")
except Exception as e:
    print(f"   ❌ pytest不可用: {e}")
    sys.exit(1)

# 测试2: 列出测试文件
print("\n2. 收集测试...")
try:
    result = subprocess.run(
        ["pytest", "backend/tests/", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd="d:/Code/嘉立创"
    )
    print(f"   输出:\n{result.stdout}")
    if result.stderr:
        print(f"   错误:\n{result.stderr}")
except subprocess.TimeoutExpired:
    print("   ❌ 收集测试超时")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 测试3: 运行单个简单测试
print("\n3. 运行单个测试...")
try:
    result = subprocess.run(
        ["pytest", "backend/tests/test_api.py::TestHealthEndpoints::test_liveness", "-v"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd="d:/Code/嘉立创"
    )
    print(f"   输出:\n{result.stdout}")
    if result.stderr:
        print(f"   错误:\n{result.stderr}")
    print(f"   返回码: {result.returncode}")
except subprocess.TimeoutExpired:
    print("   ❌ 测试超时 - 可能卡在某个地方")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("\n" + "=" * 50)
print("诊断完成")
print("=" * 50)