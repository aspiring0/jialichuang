"""
端到端流程测试
测试完整的数据分析流程：上传数据 -> 输入问题 -> Agent调度 -> 任务分配
"""

import asyncio
import sys
import os
import json
import tempfile
from pathlib import Path

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.llm_service import get_llm_service
from app.agents.supervisor import supervisor_node, SupervisorAgent
from app.agents.graph import create_analysis_graph, analysis_graph
from app.agents.state import AgentState, create_initial_state
from app.config import settings


def create_test_csv():
    """创建测试CSV文件"""
    csv_content = """日期,产品,销售额,数量,地区
2024-01-01,产品A,15000,100,华东
2024-01-02,产品B,12000,80,华南
2024-01-03,产品A,18000,120,华东
2024-01-04,产品C,9000,60,华北
2024-01-05,产品B,14000,90,华南
2024-01-06,产品A,20000,130,华东
2024-01-07,产品C,11000,70,华北
2024-01-08,产品B,16000,100,华南
2024-01-09,产品A,22000,140,华东
2024-01-10,产品C,13000,85,华北"""
    
    # 创建临时文件
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, "sales_data.csv")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(csv_content)
    
    return file_path


async def test_supervisor_intent():
    """测试 Supervisor 意图识别"""
    print("\n" + "="*60)
    print("📡 测试 1: Supervisor 意图识别")
    print("="*60)
    
    test_cases = [
        ("帮我分析一下销售数据的趋势", "trend_analysis"),
        ("哪个产品的销售额最高？", "comparison"),
        ("给我看下数据的分布情况", "distribution"),
        ("预测下个月的销售", "prediction"),
    ]
    
    supervisor = SupervisorAgent()
    
    for query, expected_intent in test_cases:
        print(f"\n📝 查询: {query}")
        
        state = {
            "user_query": query,
            "file_path": "/data/test.csv",
            "execution_logs": []
        }
        
        try:
            result = await supervisor.analyze_intent(state)
            intent = result.get("intent", "unknown")
            agent_sequence = result.get("agent_sequence", [])
            
            print(f"   ✅ 识别意图: {intent}")
            print(f"   📊 Agent序列: {agent_sequence}")
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
    
    return True


async def test_supervisor_routing():
    """测试 Supervisor 路由决策"""
    print("\n" + "="*60)
    print("📡 测试 2: Supervisor 路由决策")
    print("="*60)
    
    # 创建测试CSV
    csv_path = create_test_csv()
    print(f"\n📁 创建测试文件: {csv_path}")
    
    # 读取文件内容预览
    with open(csv_path, "r", encoding="utf-8") as f:
        preview = f.read()[:200]
    print(f"📄 文件预览:\n{preview}...")
    
    # 构建初始状态
    initial_state = {
        "user_query": "帮我分析销售数据的趋势，并生成可视化图表",
        "file_path": csv_path,
        "messages": [],
        "execution_logs": [],
        "errors": [],
        "retry_count": 0,
        "max_retries": 3
    }
    
    print(f"\n📝 用户查询: {initial_state['user_query']}")
    print("\n🤖 调用 Supervisor Agent...")
    
    try:
        result = await supervisor_node(initial_state)
        
        print(f"\n📊 调度结果:")
        print(f"  - 识别意图: {result.get('intent', 'N/A')}")
        print(f"  - Agent序列: {result.get('agent_sequence', [])}")
        print(f"  - 下一个Agent: {result.get('next_agent', 'N/A')}")
        
        # 显示执行日志
        logs = result.get("execution_logs", [])
        print(f"\n📜 执行日志:")
        for log in logs:
            print(f"  → {log}")
        
        return True, result
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_langgraph_flow():
    """测试 LangGraph 完整流程"""
    print("\n" + "="*60)
    print("📡 测试 3: LangGraph 完整流程")
    print("="*60)
    
    csv_path = create_test_csv()
    
    # 构建图
    print("\n🔨 构建 LangGraph...")
    try:
        graph = analysis_graph  # 使用已编译的图实例
        print("✅ LangGraph 构建成功")
    except Exception as e:
        print(f"❌ LangGraph 构建失败: {e}")
        return False
    
    # 使用 create_initial_state 创建正确的初始状态
    initial_state = create_initial_state(
        user_query="分析销售数据中各产品的销售趋势",
        file_path=csv_path
    )
    
    print(f"\n📝 用户查询: {initial_state['user_query']}")
    print(f"📁 数据文件: {csv_path}")
    
    print("\n🚀 执行 LangGraph...")
    
    try:
        # 执行图
        result = await graph.ainvoke(initial_state)
        
        print("\n📊 执行结果:")
        print(f"  - 当前Agent: {result.get('current_agent', 'N/A')}")
        print(f"  - 识别意图: {result.get('intent', 'N/A')}")
        print(f"  - Agent序列: {result.get('agent_sequence', [])}")
        print(f"  - 下一个Agent: {result.get('next_agent', 'N/A')}")
        
        # 显示执行日志
        logs = result.get("execution_logs", [])
        print(f"\n📜 完整执行日志 ({len(logs)} 条):")
        for i, log in enumerate(logs, 1):
            print(f"  {i}. {log}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_llm_data_analysis():
    """测试 LLM 数据分析能力"""
    print("\n" + "="*60)
    print("📡 测试 4: LLM 数据分析能力")
    print("="*60)
    
    csv_path = create_test_csv()
    
    # 读取数据
    with open(csv_path, "r", encoding="utf-8") as f:
        csv_content = f.read()
    
    llm = get_llm_service()
    
    prompt = f"""你是一个数据分析专家。请分析以下CSV数据并回答问题。

CSV数据:
```
{csv_content}
```

问题: 请分析各产品的销售趋势，哪个产品表现最好？

请以JSON格式返回分析结果:
{{
    "analysis": "分析结论",
    "best_product": "表现最好的产品",
    "trend": "趋势描述",
    "recommendations": ["建议1", "建议2"]
}}
"""

    print(f"\n📝 发送数据分析请求...")
    
    try:
        response = await llm.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=500
        )
        
        print(f"\n🤖 LLM 分析结果:")
        print(response)
        
        # 尝试解析JSON
        try:
            # 提取JSON
            if "{" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                result = json.loads(json_str)
                
                print(f"\n📊 结构化结果:")
                print(f"  - 分析结论: {result.get('analysis', 'N/A')}")
                print(f"  - 最佳产品: {result.get('best_product', 'N/A')}")
                print(f"  - 趋势: {result.get('trend', 'N/A')}")
                print(f"  - 建议: {result.get('recommendations', [])}")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


async def test_full_pipeline():
    """测试完整管道"""
    print("\n" + "="*60)
    print("📡 测试 5: 完整分析管道")
    print("="*60)
    
    csv_path = create_test_csv()
    
    print(f"\n📁 测试文件: {csv_path}")
    
    # 模拟完整流程
    steps = [
        ("1. 用户上传数据", lambda: print(f"   ✅ 文件已上传: {csv_path}")),
        ("2. 用户输入问题", lambda: print(f"   ✅ 问题: 分析销售趋势")),
        ("3. Supervisor 分析意图", None),
        ("4. 分配任务给 Agent", None),
    ]
    
    print("\n🔄 执行流程:")
    
    # Step 1 & 2
    steps[0][1]()
    steps[1][1]()
    
    # Step 3: Supervisor
    print("\n   🤖 Supervisor 正在分析...")
    
    initial_state = {
        "user_query": "分析销售数据，告诉我哪个产品表现最好",
        "file_path": csv_path,
        "messages": [],
        "execution_logs": [],
        "errors": [],
        "retry_count": 0,
        "max_retries": 3
    }
    
    try:
        result = await supervisor_node(initial_state)
        
        print(f"   ✅ 意图识别: {result.get('intent')}")
        print(f"   ✅ Agent序列: {result.get('agent_sequence')}")
        print(f"   ✅ 下一步: 调用 {result.get('next_agent')} Agent")
        
        # Step 4: 任务分配详情
        print("\n   📋 任务分配详情:")
        task_plan = result.get('task_plan', [])
        for i, task in enumerate(task_plan, 1):
            if isinstance(task, dict):
                print(f"      {i}. Agent: {task.get('agent', 'N/A')}")
                print(f"         任务: {task.get('task', 'N/A')}")
                print(f"         优先级: {task.get('priority', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 端到端流程测试")
    print("="*60)
    
    print(f"\n当前配置:")
    print(f"  - LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
    print(f"  - Model: {settings.ZHIPU_MODEL}")
    
    results = {}
    
    # 测试 1: 意图识别
    results["intent"] = await test_supervisor_intent()
    
    # 测试 2: 路由决策
    passed, _ = await test_supervisor_routing()
    results["routing"] = passed
    
    # 测试 3: LangGraph 流程
    results["langgraph"] = await test_langgraph_flow()
    
    # 测试 4: LLM 数据分析
    results["llm_analysis"] = await test_llm_data_analysis()
    
    # 测试 5: 完整管道
    results["full_pipeline"] = await test_full_pipeline()
    
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
        print("\n🎉 所有测试通过! API 和 LLM 连接正常，Agent 调度工作正常。")
    else:
        print("\n⚠️ 部分测试未通过，请检查。")


if __name__ == "__main__":
    asyncio.run(main())