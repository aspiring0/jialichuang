"""
LLM Service Test - 仅测试智谱AI连接
无需启动Docker服务
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.services.llm_service import get_llm_service
from app.config import settings


async def main():
    print("=" * 50)
    print("🤖 智谱AI GLM-4 连接测试")
    print("=" * 50)
    
    print(f"\n配置: Provider={settings.DEFAULT_LLM_PROVIDER}, Model={settings.ZHIPU_MODEL}")
    
    if not settings.ZHIPU_API_KEY:
        print("❌ ZHIPU_API_KEY 未配置")
        return
    
    try:
        llm = get_llm_service("zhipu")
        
        print("\n发送测试请求...")
        response = await llm.generate(
            prompt="你好，请用一句话介绍你自己。",
            system_prompt="你是AI助手",
            max_tokens=50,
        )
        
        print(f"\n✅ 成功!\n回答: {response}")
        
    except Exception as e:
        print(f"\n❌ 失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())