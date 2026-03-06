"""
后端与AI交互测试脚本
测试 LLM Service 与 Supervisor Agent 的集成
"""

import asyncio
import sys
import os

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.llm_service import get_llm_service, LLMServiceFactory
from app.agents.supervisor import SupervisorAgent
from app.prompts import get_system_prompt, get_prompt_template
from app.config import settings


async def test_llm_service():
    """测试 LLM 服务基础功能"""
    print("\n" + "="*60)
    print("📡 测试 1: LLM Service 基础连接")
    print("="*60)
    
    print(f"\n当前配置:")
    print(f"  - LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
    print(f"  - Zhipu API Key: {'已配置' if settings.ZHIPU_API_KEY else '未配置'}")
    print(f"  - Zhipu Model: {settings.ZHIPU_MODEL}")
    print(f"  - OpenAI API Key: {'已配置' if settings.OPENAI_API_KEY else '未配置'}")
    print(f"  - OpenAI Model: {settings.OPENAI_MODEL}")
    print(f"  - Anthropic API Key: {'已配置' if settings.ANTHROPIC_API_KEY else '未配置'}")
    print(f"  - Anthropic Model: {settings.ANTHROPIC_MODEL}")
    
    if not settings.ZHIPU_API_KEY and not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
        print("\n❌ 错误: 没有配置任何 LLM API Key!")
        print("请在 .env 文件中配置 ZHIPU_API_KEY, OPENAI_API_KEY 或 ANTHROPIC_API_KEY")
        return False
    
    try:
        # 获取 LLM 服务
        llm = get_llm_service()
        print(f"\n✅ LLM 服务初始化成功: {type(llm).__name__}")
        
        # 测试简单对话
        print("\n🤖 发送测试消息...")
        test_prompt = "你好，请用一句话介绍你自己。"
        
        response = await llm.generate(
            prompt=test_prompt,
            temperature=0.7,
            max_tokens=100
        )
        
        print(f"\n📝 用户: {test_prompt}")
        print(f"🤖 AI 回复: {response}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LLM 服务测试失败: {e}")
        return False


async def test_supervisor_agent():
    """测试 Supervisor Agent"""
    print("\n" + "="*60)
    print("📡 测试 2: Supervisor Agent 集成")
    print("="*60)
    
    try:
        from app.agents.supervisor import supervisor_node
        
        # 测试简单意图理解
        test_query = "帮我分析一下销售数据的趋势"
        
        print(f"\n📝 用户查询: {test_query}")
        print("\n🤖 正在分析意图...")
        
        # 构建测试状态
        test_state = {
            "user_query": test_query,
            "file_path": "/data/sales.csv",  # 模拟文件路径
            "messages": [],
            "execution_logs": []
        }
        
        # 调用 supervisor_node（LangGraph 节点函数）
        result = await supervisor_node(test_state)
        
        print(f"\n📊 分析结果:")
        print(f"  - 意图: {result.get('intent', 'N/A')}")
        print(f"  - Agent 序列: {result.get('agent_sequence', [])}")
        print(f"  - 下一个 Agent: {result.get('next_agent', 'N/A')}")
        print(f"  - 执行日志: {result.get('execution_logs', [])[-3:]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Supervisor Agent 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_prompts_loading():
    """测试 Prompts 加载"""
    print("\n" + "="*60)
    print("📡 测试 3: Prompts 加载")
    print("="*60)
    
    try:
        # 测试 supervisor prompt
        supervisor_prompt = get_system_prompt("supervisor")
        print(f"\n✅ Supervisor Prompt 加载成功:")
        print(f"   前100字符: {supervisor_prompt[:100]}...")
        
        # 测试 data_parser prompt
        data_parser_prompt = get_system_prompt("data_parser")
        print(f"\n✅ DataParser Prompt 加载成功:")
        print(f"   前100字符: {data_parser_prompt[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Prompts 加载测试失败: {e}")
        return False


async def test_llm_stream():
    """测试 LLM 流式输出"""
    print("\n" + "="*60)
    print("📡 测试 4: LLM 流式输出")
    print("="*60)
    
    try:
        llm = get_llm_service()
        
        test_prompt = "请用三句话描述数据分析的流程。"
        print(f"\n📝 用户: {test_prompt}")
        print(f"\n🤖 AI 流式回复: ")
        print("-" * 40)
        
        async for chunk in llm.generate_stream(
            prompt=test_prompt,
            temperature=0.7,
            max_tokens=200
        ):
            print(chunk, end="", flush=True)
        
        print("\n" + "-" * 40)
        
        return True
        
    except Exception as e:
        print(f"\n❌ LLM 流式输出测试失败: {e}")
        return False


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 后端与 AI 交互测试")
    print("="*60)
    
    results = {}
    
    # 测试 1: Prompts 加载
    results["prompts"] = await test_prompts_loading()
    
    # 测试 2: LLM Service 基础连接
    results["llm_service"] = await test_llm_service()
    
    # 测试 3: LLM 流式输出 (仅当基础测试通过)
    if results["llm_service"]:
        results["llm_stream"] = await test_llm_stream()
    else:
        results["llm_stream"] = False
        print("\n⏭️ 跳过流式输出测试 (基础测试未通过)")
    
    # 测试 4: Supervisor Agent (仅当 LLM 测试通过)
    if results["llm_service"]:
        results["supervisor"] = await test_supervisor_agent()
    else:
        results["supervisor"] = False
        print("\n⏭️ 跳过 Supervisor 测试 (LLM 测试未通过)")
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过! 后端与 AI 交互正常。")
    else:
        print("\n⚠️ 部分测试未通过，请检查配置。")


if __name__ == "__main__":
    asyncio.run(main())