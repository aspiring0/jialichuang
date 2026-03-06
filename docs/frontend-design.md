# 前端设计文档

## Multi-Agent Data Analysis Assistant - Frontend Design Document

---

## 目录

1. [概述](#概述)
2. [技术栈](#技术栈)
3. [目录结构](#目录结构)
4. [核心界面设计](#核心界面设计)
5. [API接口对接](#api接口对接)
6. [状态管理](#状态管理)
7. [WebSocket通信](#websocket通信)
8. [组件设计](#组件设计)
9. [类型定义](#类型定义)
10. [开发计划](#开发计划)

---

## 概述

### 设计目标

基于项目计划书要求，前端需要实现：

- **双栏响应式布局**：参考 Gemini AI Studio / Claude Artifacts 设计风格
- **自然语言交互**：用户用自然语言描述数据分析需求
- **实时进度展示**：通过 WebSocket 实时推送 Agent 思考链
- **多 Tab 工作区**：数据快照、代码、日志、图表、报告
- **会话管理**：支持多会话并行，完全隔离

### 核心原则

1. **零硬编码**：前端只负责展示，所有分析逻辑由后端 LLM 生成
2. **沉浸式体验**：对话 + 结果一体化展示
3. **实时反馈**：Agent 执行过程可视化
4. **会话隔离**：不同对话之间数据环境完全隔离

---

## 技术栈

| 类别 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| **框架** | React | 18.x | 前端框架 |
| **语言** | TypeScript | 5.x | 类型安全 |
| **构建工具** | Vite | 5.x | 快速构建 |
| **状态管理** | Zustand | 4.x | 轻量级状态管理 |
| **样式方案** | Tailwind CSS | 3.x | 原子化 CSS |
| **UI 组件库** | Ant Design | 5.x | 企业级组件 |
| **图表可视化** | ECharts | 5.x | 交互式图表 |
| **代码高亮** | Prism.js | 1.x | 语法高亮 |
| **Markdown 渲染** | react-markdown | 9.x | 报告渲染 |
| **HTTP 客户端** | Axios | 1.x | API 请求 |
| **实时通信** | Socket.IO Client | 4.x | WebSocket |
| **文件上传** | react-dropzone | 14.x | 拖拽上传 |
| **测试** | Vitest + Playwright | - | 单元测试 + E2E |

---

## 目录结构

```
frontend/
├── public/
│   ├── favicon.ico
│   └── assets/
│       └── images/
│
├── src/
│   ├── main.tsx                    # 入口文件
│   ├── App.tsx                     # 根组件
│   ├── index.css                   # 全局样式
│   ├── vite-env.d.ts               # Vite 类型声明
│   │
│   ├── api/                        # API 层
│   │   ├── client.ts               # Axios 实例配置
│   │   ├── sessions.ts             # 会话管理 API
│   │   ├── tasks.ts                # 任务管理 API
│   │   ├── analyze.ts              # 分析相关 API
│   │   └── websocket.ts            # WebSocket 封装
│   │
│   ├── components/                 # 组件
│   │   ├── ui/                     # 基础 UI 组件
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Progress.tsx
│   │   │   ├── Tabs.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── layout/                 # 布局组件
│   │   │   ├── Header.tsx          # 顶部导航
│   │   │   ├── Sidebar.tsx         # 侧边栏（会话列表）
│   │   │   ├── MainLayout.tsx      # 主布局
│   │   │   ├── DualPanelLayout.tsx # 双栏布局
│   │   │   └── index.ts
│   │   │
│   │   ├── features/               # 功能组件
│   │   │   │
│   │   │   ├── FileUpload/         # 文件上传模块
│   │   │   │   ├── DropZone.tsx    # 拖拽上传区域
│   │   │   │   ├── FilePreview.tsx # 文件预览
│   │   │   │   ├── FileList.tsx    # 文件列表
│   │   │   │   └── index.tsx
│   │   │   │
│   │   │   ├── ChatPanel/          # 左侧对话面板
│   │   │   │   ├── ChatInput.tsx   # 输入框
│   │   │   │   ├── MessageList.tsx # 消息列表
│   │   │   │   ├── MessageItem.tsx # 单条消息
│   │   │   │   ├── ThinkingChain.tsx  # 思考链展示
│   │   │   │   └── index.tsx
│   │   │   │
│   │   │   ├── Workspace/          # 右侧工作区
│   │   │   │   ├── TabPanel.tsx    # Tab 容器
│   │   │   │   ├── DataSnapshot.tsx   # 原始数据快照
│   │   │   │   ├── CodeViewer.tsx     # 代码查看器
│   │   │   │   ├── ExecutionLog.tsx   # 执行日志
│   │   │   │   ├── ChartViewer.tsx    # 图表查看器
│   │   │   │   ├── ChartGallery.tsx   # 图表画廊
│   │   │   │   ├── AnalysisReport.tsx # 分析报告
│   │   │   │   └── index.tsx
│   │   │   │
│   │   │   ├── AnalysisProgress/   # 分析进度
│   │   │   │   ├── AgentStatus.tsx     # Agent 状态
│   │   │   │   ├── ProgressTimeline.tsx # 进度时间线
│   │   │   │   ├── ProgressBar.tsx     # 进度条
│   │   │   │   └── index.tsx
│   │   │   │
│   │   │   └── SessionList/        # 会话列表
│   │   │       ├── SessionItem.tsx
│   │   │       ├── NewSessionButton.tsx
│   │   │       └── index.tsx
│   │   │
│   │   └── common/                 # 通用组件
│   │       ├── Loading.tsx
│   │       ├── ErrorBoundary.tsx
│   │       ├── EmptyState.tsx
│   │       └── index.ts
│   │
│   ├── hooks/                      # 自定义 Hooks
│   │   ├── useWebSocket.ts         # WebSocket 连接
│   │   ├── useAnalysis.ts          # 分析逻辑
│   │   ├── useFileUpload.ts        # 文件上传
│   │   ├── useSession.ts           # 会话管理
│   │   └── useLocalStorage.ts      # 本地存储
│   │
│   ├── stores/                     # Zustand 状态管理
│   │   ├── analysisStore.ts        # 分析状态
│   │   ├── sessionStore.ts         # 会话状态
│   │   ├── uiStore.ts              # UI 状态
│   │   └── index.ts
│   │
│   ├── types/                      # TypeScript 类型
│   │   ├── api.ts                  # API 响应类型
│   │   ├── session.ts              # 会话类型
│   │   ├── task.ts                 # 任务类型
│   │   ├── analysis.ts             # 分析类型
│   │   ├── chart.ts                # 图表类型
│   │   ├── websocket.ts            # WebSocket 类型
│   │   └── index.ts
│   │
│   ├── utils/                      # 工具函数
│   │   ├── format.ts               # 格式化
│   │   ├── validation.ts           # 验证
│   │   ├── constants.ts            # 常量
│   │   └── helpers.ts              # 辅助函数
│   │
│   └── pages/                      # 页面
│       ├── Home.tsx                # 首页
│       ├── Analysis.tsx            # 主分析页面
│       ├── History.tsx             # 历史记录
│       └── NotFound.tsx            # 404 页面
│
├── tests/                          # 测试
│   ├── unit/                       # 单元测试
│   └── e2e/                        # E2E 测试
│
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── .eslintrc.cjs
├── .prettierrc
└── index.html
```

---

## 核心界面设计

### 整体布局

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Header (Logo + 新建对话)                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  🤖 Multi-Agent Data Analyst    [新建对话]    [历史]    [设置]          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
├────────────────────────────────┬────────────────────────────────────────────┤
│                                │                                             │
│    左侧交互区 (Chat Pane)       │          右侧工作区 (Workspace)              │
│         宽度: 40%               │               宽度: 60%                     │
│                                │                                             │
│  ┌──────────────────────────┐ │  ┌──────────────────────────────────────┐  │
│  │   📎 文件上传区域          │ │  │  [数据] [代码] [日志] [图表] [报告]   │  │
│  │   (拖拽或点击上传)         │ │  ├──────────────────────────────────────┤  │
│  │   支持 CSV/Excel/JSON     │ │  │                                       │  │
│  │   最大 10MB               │ │  │                                       │  │
│  └──────────────────────────┘ │  │                                       │  │
│                                │  │         Tab 内容区域                   │  │
│  ┌──────────────────────────┐ │  │                                       │  │
│  │   📊 数据预览 (前100行)    │ │  │   - 数据快照：表格展示                 │  │
│  │   ┌──────┬──────┬──────┐ │ │  │   - 代码：语法高亮 + 复制              │  │
│  │   │ 列名 │ 类型  │ 示例  │ │ │  │   - 日志：实时流式输出                 │  │
│  │   ├──────┼──────┼──────┤ │ │  │   - 图表：ECharts交互                  │  │
│  │   │ id   │ int  │ 1,2  │ │ │  │   - 报告：Markdown渲染                 │  │
│  │   │ name │ str  │ A,B  │ │ │  │                                       │  │
│  │   └──────┴──────┴──────┘ │ │  │                                       │  │
│  └──────────────────────────┘ │  └──────────────────────────────────────┘  │
│                                │                                            │
│  ┌──────────────────────────┐ │                                            │
│  │   🤔 思考链 (Thinking)    │ │                                            │
│  │   ┌────────────────────┐ │ │                                            │
│  │   │ ✓ Supervisor       │ │ │                                            │
│  │   │   任务分解完成      │ │ │                                            │
│  │   │ ◐ DataParser       │ │ │                                            │
│  │   │   正在解析数据...   │ │ │                                            │
│  │   │ ○ Analysis         │ │ │                                            │
│  │   │   等待中           │ │ │                                            │
│  │   │ ○ Visualization    │ │ │                                            │
│  │   │   等待中           │ │ │                                            │
│  │   └────────────────────┘ │ │                                            │
│  └──────────────────────────┘ │                                            │
│                                │                                            │
├────────────────────────────────┴────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  💬 输入自然语言查询...                              [发送] 📎      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 响应式设计

| 屏幕尺寸 | 布局方式 | 说明 |
|---------|---------|------|
| `>= 1280px` | 双栏并排 | 左侧 40%，右侧 60% |
| `768px - 1279px` | 双栏并排 | 左侧 45%，右侧 55% |
| `< 768px` | 单栏切换 | Tab 切换对话/工作区 |

---

## API接口对接

### 已有接口

#### 1. 会话管理 `/api/v1/sessions`

```typescript
// GET /api/v1/sessions - 列出会话
interface SessionListResponse {
  sessions: Session[];
  total: number;
}

// POST /api/v1/sessions - 创建会话
interface SessionCreate {
  title?: string;
}

// GET /api/v1/sessions/{id} - 获取会话
// PATCH /api/v1/sessions/{id} - 更新会话
// DELETE /api/v1/sessions/{id} - 删除会话
```

#### 2. 任务管理 `/api/v1/tasks`

```typescript
// GET /api/v1/tasks - 列出任务
interface TaskListResponse {
  tasks: Task[];
  total: number;
}

// POST /api/v1/tasks - 创建任务
interface TaskCreate {
  session_id: string;
  type: 'data_parsing' | 'analysis' | 'visualization' | 'debugging';
  priority?: number;
  tags?: string[];
  dependencies?: string[];
  input_data?: Record<string, any>;
  timeout_seconds?: number;
}

// GET /api/v1/tasks/{id} - 获取任务
// PATCH /api/v1/tasks/{id} - 更新任务
// POST /api/v1/tasks/{id}/retry - 重试任务
```

#### 3. 健康检查 `/api/v1/health`

```typescript
// GET /api/v1/health - 完整健康检查
interface HealthResponse {
  status: 'healthy' | 'degraded';
  timestamp: string;
  version: string;
  services: {
    postgresql: string;
    redis: string;
    rabbitmq: string;
    minio: string;
  };
}

// GET /api/v1/health/live - 存活探针
// GET /api/v1/health/ready - 就绪探针
```

### 待开发接口

#### 4. 分析接口 `/api/v1/analyze` (规划中)

```typescript
// POST /api/v1/analyze/upload - 上传并分析
interface AnalyzeUploadRequest {
  file: File;
  query: string;
  session_id?: string;
}

interface AnalyzeUploadResponse {
  session_id: string;
  task_id: string;
  status: 'pending';
}

// GET /api/v1/analyze/result/{session_id} - 获取结果
interface AnalysisResultResponse {
  session_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  data_summary?: DataSummary;
  analysis_results?: Record<string, any>;
  echarts_configs?: EChartsConfig[];
  generated_code?: string[];
  execution_logs?: string[];
  errors?: string[];
}

// WebSocket /api/v1/analyze/ws/{session_id} - 实时进度
```

---

## 状态管理

### Zustand Stores

#### sessionStore.ts

```typescript
import { create } from 'zustand';

interface SessionState {
  sessions: Session[];
  currentSession: Session | null;
  isLoading: boolean;
  
  // Actions
  fetchSessions: () => Promise<void>;
  createSession: (title?: string) => Promise<Session>;
  selectSession: (id: string) => void;
  deleteSession: (id: string) => Promise<void>;
}

export const useSessionStore = create<SessionState>((set, get) => ({
  sessions: [],
  currentSession: null,
  isLoading: false,
  
  fetchSessions: async () => {
    set({ isLoading: true });
    const response = await api.get('/sessions');
    set({ sessions: response.data.sessions, isLoading: false });
  },
  
  createSession: async (title) => {
    const response = await api.post('/sessions', { title });
    const newSession = response.data;
    set((state) => ({
      sessions: [newSession, ...state.sessions],
      currentSession: newSession,
    }));
    return newSession;
  },
  
  selectSession: (id) => {
    const session = get().sessions.find(s => s.id === id);
    set({ currentSession: session || null });
  },
  
  deleteSession: async (id) => {
    await api.delete(`/sessions/${id}`);
    set((state) => ({
      sessions: state.sessions.filter(s => s.id !== id),
      currentSession: state.currentSession?.id === id ? null : state.currentSession,
    }));
  },
}));
```

#### analysisStore.ts

```typescript
import { create } from 'zustand';

interface AnalysisState {
  // 文件
  uploadedFile: File | null;
  filePreview: DataSnapshot | null;
  
  // 分析状态
  status: 'idle' | 'uploading' | 'analyzing' | 'completed' | 'error';
  progress: number;
  
  // 思考链
  thinkingChain: ThinkingStep[];
  
  // 结果
  generatedCode: string[];
  executionLogs: string[];
  echartsConfigs: EChartsConfig[];
  analysisReport: string;
  
  // 错误
  errors: string[];
  
  // Actions
  setUploadedFile: (file: File) => void;
  clearFile: () => void;
  updateStatus: (status: string, progress: number) => void;
  addThinkingStep: (step: ThinkingStep) => void;
  setResults: (results: AnalysisResults) => void;
  addError: (error: string) => void;
  reset: () => void;
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  uploadedFile: null,
  filePreview: null,
  status: 'idle',
  progress: 0,
  thinkingChain: [],
  generatedCode: [],
  executionLogs: [],
  echartsConfigs: [],
  analysisReport: '',
  errors: [],
  
  setUploadedFile: (file) => set({ uploadedFile: file }),
  clearFile: () => set({ uploadedFile: null, filePreview: null }),
  updateStatus: (status, progress) => set({ status, progress }),
  addThinkingStep: (step) => set((state) => ({
    thinkingChain: [...state.thinkingChain, step],
  })),
  setResults: (results) => set(results),
  addError: (error) => set((state) => ({
    errors: [...state.errors, error],
  })),
  reset: () => set({
    uploadedFile: null,
    filePreview: null,
    status: 'idle',
    progress: 0,
    thinkingChain: [],
    generatedCode: [],
    executionLogs: [],
    echartsConfigs: [],
    analysisReport: '',
    errors: [],
  }),
}));
```

---

## WebSocket通信

### 消息格式

```typescript
// WebSocket 消息类型
interface WSMessage {
  type: 'progress' | 'result' | 'error' | 'agent_update' | 'thinking' | 'log';
  agent?: AgentType;
  message: string;
  progress: number;
  timestamp: string;
  data?: any;
}

type AgentType = 'supervisor' | 'data_parser' | 'analysis' | 'visualization' | 'debugger';
```

### 消息示例

```json
// 进度更新
{
  "type": "progress",
  "agent": "data_parser",
  "message": "正在解析数据文件...",
  "progress": 0.3,
  "timestamp": "2026-03-06T01:00:00Z"
}

// Agent 切换
{
  "type": "agent_update",
  "agent": "analysis",
  "message": "Supervisor → Analysis Agent",
  "progress": 0.5,
  "timestamp": "2026-03-06T01:00:05Z"
}

// 思考链
{
  "type": "thinking",
  "agent": "analysis",
  "message": "正在生成统计分析代码...",
  "progress": 0.6,
  "timestamp": "2026-03-06T01:00:10Z",
  "data": {
    "thought": "检测到数值型列，将生成描述性统计..."
  }
}

// 执行日志
{
  "type": "log",
  "message": "stdout: 正在执行 pandas 代码...",
  "timestamp": "2026-03-06T01:00:15Z"
}

// 完成
{
  "type": "result",
  "message": "分析完成",
  "progress": 1.0,
  "timestamp": "2026-03-06T01:00:30Z",
  "data": {
    "echarts_configs": [...],
    "analysis_results": {...}
  }
}

// 错误
{
  "type": "error",
  "message": "代码执行超时",
  "timestamp": "2026-03-06T01:00:30Z",
  "data": {
    "error_type": "TimeoutError",
    "retry_count": 1
  }
}
```

### WebSocket Hook

```typescript
// hooks/useWebSocket.ts
import { useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAnalysisStore } from '@/stores/analysisStore';

export function useWebSocket(sessionId: string | null) {
  const socketRef = useRef<Socket | null>(null);
  const { updateStatus, addThinkingStep, setResults, addError } = useAnalysisStore();
  
  const connect = useCallback(() => {
    if (!sessionId) return;
    
    socketRef.current = io(`${API_BASE_URL}/analyze/ws/${sessionId}`, {
      transports: ['websocket'],
    });
    
    socketRef.current.on('connect', () => {
      console.log('WebSocket connected');
    });
    
    socketRef.current.on('message', (msg: WSMessage) => {
      switch (msg.type) {
        case 'progress':
        case 'agent_update':
          updateStatus('analyzing', msg.progress);
          addThinkingStep({
            agent: msg.agent,
            status: 'running',
            message: msg.message,
            timestamp: msg.timestamp,
          });
          break;
          
        case 'thinking':
          addThinkingStep({
            agent: msg.agent,
            status: 'thinking',
            message: msg.message,
            thought: msg.data?.thought,
            timestamp: msg.timestamp,
          });
          break;
          
        case 'log':
          // 追加到执行日志
          break;
          
        case 'result':
          updateStatus('completed', 1.0);
          setResults(msg.data);
          break;
          
        case 'error':
          updateStatus('error', msg.progress);
          addError(msg.message);
          break;
      }
    });
    
    socketRef.current.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });
  }, [sessionId]);
  
  const disconnect = useCallback(() => {
    socketRef.current?.disconnect();
    socketRef.current = null;
  }, []);
  
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);
  
  return { connect, disconnect };
}
```

---

## 组件设计

### 核心组件

#### 1. DualPanelLayout.tsx

```tsx
import { ReactNode } from 'react';

interface DualPanelLayoutProps {
  leftPanel: ReactNode;
  rightPanel: ReactNode;
  leftWidth?: string;
}

export function DualPanelLayout({ 
  leftPanel, 
  rightPanel, 
  leftWidth = '40%' 
}: DualPanelLayoutProps) {
  return (
    <div className="flex h-full">
      <div 
        className="border-r border-gray-200 overflow-auto"
        style={{ width: leftWidth }}
      >
        {leftPanel}
      </div>
      <div className="flex-1 overflow-auto">
        {rightPanel}
      </div>
    </div>
  );
}
```

#### 2. ThinkingChain.tsx

```tsx
import { CheckCircle, Circle, Loader2 } from 'lucide-react';

interface ThinkingStep {
  agent: AgentType;
  status: 'pending' | 'running' | 'completed' | 'error';
  message: string;
  timestamp: string;
  thought?: string;
}

interface ThinkingChainProps {
  steps: ThinkingStep[];
}

const agentNames: Record<AgentType, string> = {
  supervisor: '总调度器',
  data_parser: '数据解析',
  analysis: '分析执行',
  visualization: '可视化',
  debugger: '纠错修复',
};

export function ThinkingChain({ steps }: ThinkingChainProps) {
  return (
    <div className="thinking-chain">
      <h3 className="text-sm font-medium text-gray-700 mb-3">
        🤔 思考链
      </h3>
      <div className="space-y-2">
        {steps.map((step, index) => (
          <div 
            key={index}
            className={`flex items-start gap-2 p-2 rounded ${
              step.status === 'running' ? 'bg-blue-50' : ''
            }`}
          >
            <StatusIcon status={step.status} />
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm">
                  {agentNames[step.agent]}
                </span>
                <span className="text-xs text-gray-500">
                  {formatTime(step.timestamp)}
                </span>
              </div>
              <p className="text-sm text-gray-600">{step.message}</p>
              {step.thought && (
                <p className="text-xs text-gray-400 mt-1 italic">
                  {step.thought}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    case 'running':
      return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
    case 'error':
      return <Circle className="w-4 h-4 text-red-500" />;
    default:
      return <Circle className="w-4 h-4 text-gray-300" />;
  }
}
```

#### 3. ChartViewer.tsx

```tsx
import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface ChartViewerProps {
  config: EChartsConfig;
}

export function ChartViewer({ config }: ChartViewerProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  
  useEffect(() => {
    if (!chartRef.current) return;
    
    chartInstance.current = echarts.init(chartRef.current);
    chartInstance.current.setOption(config.option);
    
    const handleResize = () => {
      chartInstance.current?.resize();
    };
    
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
      chartInstance.current?.dispose();
    };
  }, [config]);
  
  return (
    <div className="chart-viewer">
      <h4 className="text-sm font-medium mb-2">{config.title}</h4>
      <div 
        ref={chartRef} 
        className="w-full h-80"
      />
    </div>
  );
}
```

---

## 类型定义

```typescript
// types/index.ts

// 会话状态
export enum SessionStatus {
  ACTIVE = 'active',
  ARCHIVED = 'archived',
  DELETED = 'deleted',
}

export interface Session {
  id: string;
  title: string | null;
  status: SessionStatus;
  created_at: string;
  updated_at: string;
}

// 任务类型
export enum TaskType {
  DATA_PARSING = 'data_parsing',
  ANALYSIS = 'analysis',
  VISUALIZATION = 'visualization',
  DEBUGGING = 'debugging',
}

export enum TaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface Task {
  id: string;
  session_id: string;
  type: TaskType;
  status: TaskStatus;
  priority: number;
  tags: string[] | null;
  input_data: Record<string, any> | null;
  output_data: Record<string, any> | null;
  error_message: string | null;
  retry_count: number;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
}

// Agent 类型
export type AgentType = 
  | 'supervisor' 
  | 'data_parser' 
  | 'analysis' 
  | 'visualization' 
  | 'debugger';

// 数据摘要
export interface DataSummary {
  row_count: number;
  column_count: number;
  columns: ColumnSchema[];
}

export interface ColumnSchema {
  name: string;
  type: string;
  nullable: boolean;
  sample_values: any[];
}

// 图表配置
export interface EChartsConfig {
  title: string;
  chart_type: string;
  option: Record<string, any>;
}

// 分析结果
export interface AnalysisResults {
  session_id: string;
  status: TaskStatus;
  data_summary?: DataSummary;
  analysis_results?: Record<string, any>;
  echarts_configs?: EChartsConfig[];
  generated_code?: string[];
  execution_logs?: string[];
  analysis_report?: string;
  errors?: string[];
}
```

---

## 开发计划

### Phase 4: 前端完善 (3 周)

| 阶段 | 时间 | 任务 | 交付物 |
|------|------|------|--------|
| **4-1** | Week 1 | 基础框架搭建 | Vite 项目 + 路由 + 状态管理 |
| **4-2** | Week 2 | 双栏布局 + 文件上传 | 完整 UI 框架 |
| **4-3** | Week 3 | WebSocket + 工作区 | 完整功能实现 |

### 详细任务

#### Phase 4-1: 基础框架（Week 1）

- [ ] 初始化 Vite + React + TypeScript 项目
- [ ] 配置 Tailwind CSS
- [ ] 配置路径别名 (`@/`)
- [ ] 配置 Zustand 状态管理
- [ ] 配置 Axios API 客户端
- [ ] 创建基础 UI 组件库
- [ ] 配置 ESLint + Prettier

#### Phase 4-2: 布局与上传（Week 2）

- [ ] 实现 Header 组件
- [ ] 实现 DualPanelLayout 双栏布局
- [ ] 实现 FileUpload 拖拽上传组件
- [ ] 实现数据预览表格组件
- [ ] 对接会话管理 API
- [ ] 实现会话列表

#### Phase 4-3: 实时与工作区（Week 3）

- [ ] 实现 WebSocket 连接管理
- [ ] 实现 ThinkingChain 思考链组件
- [ ] 实现多 Tab 工作区
- [ ] 实现 CodeViewer 代码高亮
- [ ] 实现 ExecutionLog 日志展示
- [ ] 实现 ChartViewer 图表渲染
- [ ] 实现 AnalysisReport Markdown 渲染

### 测试计划

| 测试类型 | 工具 | 覆盖率目标 |
|---------|------|-----------|
| 单元测试 | Vitest | > 80% |
| E2E 测试 | Playwright | 核心流程 100% |
| 可访问性 | axe DevTools | WCAG 2.1 AA |

---

## 附录

### 环境变量

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000
```

### 启动命令

```bash
# 开发模式
npm run dev

# 构建
npm run build

# 预览
npm run preview

# 测试
npm run test

# E2E 测试
npm run test:e2e
```

---

*文档版本: 1.0*
*最后更新: 2026-03-06*