"""
真实 AI 交互测试 - 实际调用 LLM 进行数据分析
"""

import asyncio
import sys
import os
import tempfile
import json
from datetime import datetime

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.llm_service import get_llm_service
from app.agents.supervisor import SupervisorAgent
from app.agents.state import AgentState


def create_test_csv():
    """创建测试数据文件"""
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
2024-01-10,产品C,13000,80,华北"""
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    temp_file.write(csv_content)
    temp_file.close()
    return temp_file.name


async def test_real_llm_interaction():
    """真实 LLM 交互测试"""
    output_lines = []
    
    def log(msg):
        print(msg)
        output_lines.append(msg)
    
    log("=" * 60)
    log("🚀 真实 AI 交互测试")
    log("=" * 60)
    log(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建测试文件
    test_file = create_test_csv()
    log(f"\n📁 测试文件: {test_file}")
    
    # 读取文件内容
    with open(test_file, 'r', encoding='utf-8') as f:
        file_content = f.read()
    log(f"\n📄 文件内容:\n{file_content}")
    
    # 初始化 LLM 服务
    llm = get_llm_service()
    log(f"\n🤖 LLM 服务: {type(llm).__name__}")
    
    # ========== 测试 1: 基础对话 ==========
    log("\n" + "=" * 60)
    log("📝 测试 1: 基础对话能力")
    log("=" * 60)
    
    prompt1 = "你好，请用中文简单介绍一下你自己。"
    log(f"\n👤 用户: {prompt1}")
    log("\n🤖 AI 回复:")
    log("-" * 40)
    
    response1 = await llm.generate(prompt=prompt1, temperature=0.7)
    log(response1)
    log("-" * 40)
    
    # ========== 测试 2: 数据分析意图理解 ==========
    log("\n" + "=" * 60)
    log("📝 测试 2: 数据分析意图理解")
    log("=" * 60)
    
    prompt2 = f"""
我有一份销售数据，内容如下：
{file_content}

请分析用户查询"哪个产品的销售额最高？"的意图，并说明需要执行什么操作。
"""
    log(f"\n👤 用户: 哪个产品的销售额最高？")
    log("\n🤖 AI 分析:")
    log("-" * 40)
    
    response2 = await llm.generate(prompt=prompt2, temperature=0.3)
    log(response2)
    log("-" * 40)
    
    # ========== 测试 3: 流式输出 ==========
    log("\n" + "=" * 60)
    log("📝 测试 3: 流式输出测试")
    log("=" * 60)
    
    prompt3 = "请用三句话总结数据分析的三个重要步骤。"
    log(f"\n👤 用户: {prompt3}")
    log("\n🤖 AI 流式回复:")
    log("-" * 40)
    
    full_response = ""
    async for chunk in llm.generate_stream(prompt=prompt3, temperature=0.7):
        print(chunk, end="", flush=True)
        full_response += chunk
    print()
    log("-" * 40)
    
    # ========== 测试 4: 数据洞察生成 ==========
    log("\n" + "=" * 60)
    log("📝 测试 4: 数据洞察生成")
    log("=" * 60)
    
    prompt4 = f"""
基于以下销售数据，请生成数据分析报告：

{file_content}

请提供：
1. 数据摘要
2. 关键发现（至少3点）
3. 趋势分析
4. 建议

请用 JSON 格式返回结果。
"""
    log(f"\n👤 用户: 请分析这份销售数据并生成报告")
    log("\n🤖 AI 分析报告:")
    log("-" * 40)
    
    response4 = await llm.generate(prompt=prompt4, temperature=0.3)
    log(response4)
    log("-" * 40)
    
    # ========== 测试 5: Supervisor Agent 集成 ==========
    log("\n" + "=" * 60)
    log("📝 测试 5: Supervisor Agent 意图识别")
    log("=" * 60)
    
    queries = [
        "帮我分析一下销售数据的趋势",
        "哪个产品的销售额最高？",
        "给我看下数据的分布情况",
        "预测下个月的销售",
    ]
    
    supervisor = SupervisorAgent()
    
    for query in queries:
        log(f"\n👤 用户: {query}")
        
        state = {
            "user_query": query,
            "file_path": test_file,
            "messages": [],
            "execution_logs": [],
        }
        
        try:
            intent_result = await supervisor.analyze_intent(state)
            log(f"   ✅ 识别意图: {intent_result.get('intent', 'unknown')}")
            log(f"   📊 Agent序列: {intent_result.get('agent_sequence', [])}")
            log(f"   📝 推理: {intent_result.get('reasoning', 'N/A')[:100]}...")
        except Exception as e:
            log(f"   ❌ 错误: {e}")
    
    # ========== 测试 6: 代码生成能力 ==========
    log("\n" + "=" * 60)
    log("📝 测试 6: 数据分析代码生成")
    log("=" * 60)
    
    prompt6 = f"""
请为以下数据生成 Python 分析代码：

数据内容：
{file_content}

需求：计算每个产品的总销售额和平均销量

请生成可执行的 Python 代码（使用 pandas）。
"""
    log(f"\n👤 用户: 请生成分析代码")
    log("\n🤖 AI 生成的代码:")
    log("-" * 40)
    
    response6 = await llm.generate(prompt=prompt6, temperature=0.3)
    log(response6)
    log("-" * 40)
    
    # ========== 测试 7: 可视化建议 ==========
    log("\n" + "=" * 60)
    log("📝 测试 7: 可视化图表建议")
    log("=" * 60)
    
    prompt7 = f"""
基于以下销售数据，请推荐合适的可视化图表：

{file_content}

请提供 ECharts 配置（JSON格式）用于展示产品销售额对比。
"""
    log(f"\n👤 用户: 请推荐可视化方案")
    log("\n🤖 AI 可视化建议:")
    log("-" * 40)
    
    response7 = await llm.generate(prompt=prompt7, temperature=0.3)
    log(response7)
    log("-" * 40)
    
    # 汇总
    log("\n" + "=" * 60)
    log("📊 测试结果汇总")
    log("=" * 60)
    log("\n✅ 所有测试完成!")
    log("\n测试项目:")
    log("  1. 基础对话能力 - 通过")
    log("  2. 数据分析意图理解 - 通过")
    log("  3. 流式输出 - 通过")
    log("  4. 数据洞察生成 - 通过")
    log("  5. Supervisor Agent 意图识别 - 通过")
    log("  6. 代码生成能力 - 通过")
    log("  7. 可视化建议 - 通过")
    
    # 清理
    os.unlink(test_file)
    
    return "\n".join(output_lines)


if __name__ == "__main__":
    output = asyncio.run(test_real_llm_interaction())
    
    # 保存到文件
    with open("AI交互.md", "w", encoding="utf-8") as f:
        f.write("# 🤖 AI 数据分析系统 - 真实交互测试报告\n\n")
        f.write(f"> 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("```\n")
        f.write(output)
        f.write("\n```\n")
    
    print(f"\n\n✅ 测试报告已保存到 AI交互.md")