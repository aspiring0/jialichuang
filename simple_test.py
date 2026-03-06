"""
最简单的导入测试 - 不运行pytest
"""
import sys
sys.path.insert(0, "d:/Code/嘉立创/backend")

print("=" * 50)
print("简单导入测试")
print("=" * 50)

# 测试1: 导入app
print("\n1. 导入FastAPI app...")
try:
    from app.main import app
    print(f"   ✅ 成功: {app.title}")
except Exception as e:
    print(f"   ❌ 失败: {e}")

# 测试2: 导入配置
print("\n2. 导入配置...")
try:
    from app.config import settings
    print(f"   ✅ 成功: {settings.APP_NAME}")
    print(f"   Provider: {settings.DEFAULT_LLM_PROVIDER}")
except Exception as e:
    print(f"   ❌ 失败: {e}")

# 测试3: 导入数据库
print("\n3. 导入数据库...")
try:
    from app.database import Base, get_db
    print(f"   ✅ 成功")
except Exception as e:
    print(f"   ❌ 失败: {e}")

# 测试4: 导入模型
print("\n4. 导入模型...")
try:
    from app.models.session import Session
    from app.models.task import Task
    print(f"   ✅ 成功")
except Exception as e:
    print(f"   ❌ 失败: {e}")

# 测试5: 导入LLM服务
print("\n5. 导入LLM服务...")
try:
    from app.services.llm_service import get_llm_service
    print(f"   ✅ 成功")
except Exception as e:
    print(f"   ❌ 失败: {e}")

print("\n" + "=" * 50)
print("所有导入测试完成")
print("=" * 50)