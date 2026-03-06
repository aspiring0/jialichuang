# Multi-Agent Data Analysis System

## 架构概述

本系统采用 LangGraph 构建多智能体数据分析流水线，包含以下核心组件：

```
┌─────────────────────────────────────────────────────────────┐
│                     Supervisor Agent                         │
│              (总调度器 - 意图理解与任务分解)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        ▼             ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│ DataParser│  │ Analysis  │  │Visualization│ │ Debugger  │
│   Agent   │─▶│   Agent   │─▶│   Agent    │─▶│  Agent    │
│ 数据解析   │  │  分析执行  │  │  可视化    │  │  调试修复  │
└───────────┘  └───────────┘  └───────────┘  └───────────┘
```

## Agent 说明

### 1. Supervisor Agent (总调度器)

**职责：**
- 理解用户自然语言查询意图
- 将复杂任务分解为子任务
- 确定调用哪些专业 Agent
- 聚合各 Agent 结果

**文件：**
- 实现：`backend/app/agents/supervisor.py`
- 提示词：`backend/app/prompts/supervisor.py`

### 2. DataParser Agent (数据解析器)

**职责：**
- 解析 CSV、Excel、JSON 等数据文件
- 推断列的数据类型
- 生成数据统计摘要
- 检测数据质量问题

**状态更新：**
- `parsed_schema`: 数据结构信息
- `data_summary`: 统计摘要

### 3. Analysis Agent (分析执行器)

**职责：**
- 根据用户需求生成分析策略
- 编写安全的 Python 分析代码
- 在沙箱环境执行代码
- 返回分析结果

**状态更新：**
- `analysis_results`: 分析结果
- `generated_code`: 生成的代码

### 4. Visualization Agent (可视化生成器)

**职责：**
- 推荐合适的图表类型
- 生成 ECharts 配置 JSON
- 支持多种图表：折线图、柱状图、饼图等

**状态更新：**
- `echarts_configs`: ECharts 配置列表

### 5. Debugger Agent (调试修复器)

**职责：**
- 分析代码执行错误
- 定位错误原因
- 生成修复后的代码
- 决定是否重试

**状态更新：**
- `retry_count`: 重试次数
- `errors`: 错误列表

## 状态管理 (AgentState)

```python
class AgentState(TypedDict):
    # 用户输入
    user_query: str           # 用户自然语言查询
    file_path: Optional[str]  # 上传的文件路径
    session_id: Optional[str] # 会话ID
    
    # 中间状态
    intent: Optional[str]           # 识别的意图
    parsed_schema: Optional[Dict]   # 数据Schema
    data_summary: Optional[Dict]    # 数据摘要
    analysis_results: Optional[Dict] # 分析结果
    generated_code: Optional[List[str]] # 生成的代码
    echarts_configs: Optional[List[Dict]] # 图表配置
    
    # 执行控制
    current_agent: str         # 当前执行的Agent
    agent_sequence: List[str]  # Agent执行序列
    retry_count: int           # 重试次数
    max_retries: int           # 最大重试次数
    errors: List[str]          # 错误列表
    success: bool              # 是否成功完成
    
    # 输出
    final_output: Optional[Dict]  # 最终输出
    execution_logs: List[str]     # 执行日志
```

## 工作流程

1. **用户提交查询** → 创建初始 State
2. **Supervisor 分析意图** → 确定 Agent 执行序列
3. **DataParser 解析数据** → 生成 Schema 和摘要
4. **Analysis 执行分析** → 生成代码并执行
5. **Visualization 生成图表** → 创建 ECharts 配置
6. **如有错误** → Debugger 修复并重试
7. **Supervisor 聚合结果** → 返回最终输出

## 测试覆盖

| 模块 | 测试文件 | 测试数量 | 状态 |
|------|---------|---------|------|
| State | test_state.py | 15 | ✅ |
| Graph | test_graph.py | 22 | ✅ |
| Supervisor | test_supervisor.py | 15 | ✅ |

运行测试：
```bash
cd backend
python -m pytest tests/test_state.py tests/test_graph.py tests/test_supervisor.py -v