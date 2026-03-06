# 环境搭建指南

## Multi-Agent Data Analysis Assistant - Phase 0 基础设施配置

本文档详细说明如何搭建开发环境，包括所有依赖服务的配置和验证。

---

## 目录

1. [前置要求](#前置要求)
2. [Conda环境配置](#conda环境配置)
3. [Docker服务配置](#docker服务配置)
4. [项目依赖安装](#项目依赖安装)
5. [环境变量配置](#环境变量配置)
6. [启动服务](#启动服务)
7. [健康检查验证](#健康检查验证)
8. [常见问题](#常见问题)

---

## 前置要求

请确保您的系统已安装以下软件：

| 软件 | 版本要求 | 用途 |
|------|---------|------|
| **Conda/Miniconda** | 最新版 | Python环境管理 |
| **Docker Desktop** | 最新版 | 容器化服务 |
| **Git** | 2.x+ | 版本控制 |

### 验证安装

```bash
# 检查 Conda
conda --version

# 检查 Docker
docker --version
docker-compose --version

# 检查 Git
git --version
```

---

## Conda环境配置

### 1. 激活现有环境

本项目使用名为 `jiali` 的 conda 环境（Python 3.10.19）。

```bash
# 激活环境
conda activate jiali

# 验证 Python 版本
python --version
# 输出: Python 3.10.19
```

### 2. 如需创建新环境（可选）

如果 `jiali` 环境不存在，可以创建：

```bash
# 使用 environment.yml 创建环境
conda env create -f environment.yml

# 或手动创建
conda create -n jiali python=3.10
conda activate jiali
```

---

## Docker服务配置

项目需要以下 Docker 服务：

| 服务 | 端口 | 用途 |
|------|------|------|
| PostgreSQL | 5432 | 关系型数据库 |
| Redis | 6379 | 缓存/消息队列 |
| RabbitMQ | 5672, 15672 | 异步任务队列 |
| MinIO | 9000, 9001 | S3兼容对象存储 |
| Prometheus | 9090 | 监控指标采集 |
| Grafana | 3000 | 监控仪表盘 |

### 1. 创建数据目录

```bash
# 在项目根目录执行
mkdir -p data/postgres data/redis data/rabbitmq data/minio data/prometheus data/grafana data/logs
```

### 2. 启动 Docker 服务

```bash
# 进入 docker 目录
cd infrastructure/docker

# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 验证 Docker 服务

```bash
# PostgreSQL
docker exec -it multi-agent-postgres psql -U postgres -c "SELECT version();"

# Redis
docker exec -it multi-agent-redis redis-cli ping

# RabbitMQ 管理界面
# 浏览器访问: http://localhost:15672 (guest/guest)

# MinIO 控制台
# 浏览器访问: http://localhost:9001 (minioadmin/minioadmin)

# Prometheus
# 浏览器访问: http://localhost:9090

# Grafana
# 浏览器访问: http://localhost:3000 (admin/admin)
```

---

## 项目依赖安装

### 1. 安装 Python 依赖

```bash
# 确保在项目根目录且已激活 conda 环境
conda activate jiali

# 安装依赖
pip install -r requirements.txt
```

### 2. 验证关键依赖

```bash
# FastAPI
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"

# SQLAlchemy
python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"

# LangChain
python -c "import langchain; print(f'LangChain: {langchain.__version__}')"
```

---

## 环境变量配置

### 1. 创建 .env 文件

```bash
# 复制模板文件
cp .env.example .env
```

### 2. 配置 LLM API Key

编辑 `.env` 文件，填入您的 API Key：

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-api-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Default LLM Provider (openai or anthropic)
DEFAULT_LLM_PROVIDER=openai
```

### 3. 重要配置项说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | 应用密钥，生产环境必须修改 | - |
| `DATABASE_URL` | PostgreSQL 连接字符串 | 自动生成 |
| `REDIS_URL` | Redis 连接字符串 | 自动生成 |
| `CORS_ORIGINS` | 允许的前端域名 | localhost:5173 |

---

## 启动服务

### 1. 启动后端 API 服务

```bash
# 方式1: 使用 uvicorn 直接启动
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式2: 使用 Makefile
make dev
```

### 2. 访问 API 文档

服务启动后，访问以下地址：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 3. 服务访问地址汇总

| 服务 | 地址 | 凭据 |
|------|------|------|
| FastAPI | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| RabbitMQ | http://localhost:15672 | guest/guest |
| MinIO | http://localhost:9001 | minioadmin/minioadmin |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |

---

## 健康检查验证

### 1. 使用健康检查脚本

```bash
# 运行健康检查
python infrastructure/scripts/health_check.py
```

预期输出：
```
============================================================
  Multi-Agent Data Analysis Assistant - Health Check
============================================================

  ✓ PostgreSQL       Connected (PostgreSQL 15.x)
  ✓ Redis            Connected (Redis 7.x.x)
  ✓ RabbitMQ         Connected (RabbitMQ Ready)
  ✓ MinIO            Connected (0 buckets)
  ✓ FastAPI          Connected (FastAPI Running)
  ✓ Prometheus       Connected (Prometheus Healthy)
  ✓ Grafana          Connected (Grafana Healthy)

============================================================
  All services are healthy!
============================================================
```

### 2. 使用 API 端点检查

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 存活探针
curl http://localhost:8000/api/v1/health/live

# 就绪探针
curl http://localhost:8000/api/v1/health/ready
```

### 3. 运行单元测试

```bash
# 运行所有测试
cd backend
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## 常见问题

### Q1: Docker 服务启动失败

**问题**: 端口被占用

**解决方案**:
```bash
# 检查端口占用
netstat -ano | findstr :5432
netstat -ano | findstr :6379
netstat -ano | findstr :5672

# 修改 docker-compose.yml 中的端口映射
```

### Q2: 数据库连接失败

**问题**: PostgreSQL 未就绪

**解决方案**:
```bash
# 等待 PostgreSQL 完全启动
docker-compose logs postgres

# 手动检查连接
docker exec -it multi-agent-postgres psql -U postgres
```

### Q3: 依赖安装失败

**问题**: pip 安装超时

**解决方案**:
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q4: MinIO 连接失败

**问题**: MinIO 启动较慢

**解决方案**:
```bash
# 等待 MinIO 就绪
docker-compose logs minio

# 重启 MinIO
docker-compose restart minio
```

---

## 下一步

Phase 0 基础设施搭建完成后，请继续：

1. **Phase 1**: MVP 核心链路开发
   - 前端基础界面
   - 文件上传功能
   - 单 Agent 代码生成
   - 沙箱执行引擎

2. **配置 API Key**: 在 `.env` 文件中填入您的 LLM API Key

3. **验证环境**: 确保所有健康检查通过

---

## 附录：项目目录结构

```
d:\Code\嘉立创\
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── api/               # API路由
│   │   │   ├── __init__.py
│   │   │   └── endpoints/
│   │   │       ├── health.py
│   │   │       ├── sessions.py
│   │   │       └── tasks.py
│   │   └── models/            # 数据模型
│   │       ├── __init__.py
│   │       ├── session.py
│   │       └── task.py
│   └── tests/                 # 测试文件
│       ├── conftest.py
│       └── test_api.py
├── frontend/                   # 前端应用（待开发）
├── infrastructure/             # 基础设施
│   ├── docker/
│   │   └── docker-compose.yml
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── grafana/
│   │   └── provisioning/
│   └── scripts/
│       └── health_check.py
├── docs/                       # 文档
├── data/                       # 数据目录（Docker挂载）
├── .env.example               # 环境变量模板
├── environment.yml            # Conda环境配置
├── requirements.txt           # Python依赖
├── Makefile                   # 常用命令
└── README.md                  # 项目说明
```

---

*文档版本: 1.0*
*最后更新: 2026-03-05*