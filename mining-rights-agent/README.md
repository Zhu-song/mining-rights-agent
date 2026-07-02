# 矿权日报 Agent - 运行指南

## 📋 项目概述

本项目实现了一个基于 MCP (Model Context Protocol) 协议的矿权日报 Agent，包含 3 个 MCP Server 和 1 个 Agent Client，能够自动生成矿业公司的今日简报。

### 核心功能

- **NewsServer**: 新闻摘要服务（端口 8001）
- **ReservesServer**: 储量数据服务（端口 8002）
- **PriceServer**: 价格走势服务（端口 8003）
- **Agent Client**: 使用 LangGraph 编排的智能客户端

## 🚀 快速启动（5分钟内运行）

### 方法一：直接运行（推荐用于开发）

```bash
# 1. 克隆项目后进入目录
cd mining-rights-agent

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 设置环境变量（如需调用真实LLM）
cp .env.example .env
# 编辑 .env 文件，填入你的 Anthropic API Key

# 4. 启动三个 MCP Server（分别在三个终端窗口运行）
python servers/news_server.py
python servers/reserves_server.py
python servers/price_server.py

# 5. 运行 Agent Client
python -m agent.main "给我生成一份关于 Pilbara 锂矿的今日简报"
```

### 方法二：Docker Compose 运行

```bash
# 1. 克隆项目后进入目录
cd mining-rights-agent

# 2. 设置环境变量（如需调用真实LLM）
echo "ANTHROPIC_API_KEY=your-api-key" > .env

# 3. 使用 Docker Compose 启动所有服务
docker-compose up --build
```

## 📡 MCP Server 端口

| Server | 端口 | 描述 |
|--------|------|------|
| NewsServer | 8081 | 新闻摘要和政策更新 |
| ReservesServer | 8082 | 储量数据和资源报告 |
| PriceServer | 8083 | 价格走势和对比分析 |

## 🔧 API 接口

### NewsServer 工具

1. **fetch_mining_news**: 获取矿业公司新闻
   - 参数: `company` (公司名称), `days` (天数，默认7)
   
2. **search_policy_updates**: 搜索政策更新
   - 参数: `country` (国家), `mineral` (矿种)

### ReservesServer 工具

1. **get_reserves_data**: 获取储量数据
   - 参数: `company` (公司名称), `mineral` (矿种，默认lithium)
   
2. **get_resource_report**: 获取资源报告
   - 参数: `company` (公司名称)

### PriceServer 工具

1. **get_price_trend**: 获取价格走势
   - 参数: `mineral` (矿种), `days` (天数，默认30)
   
2. **get_price_comparison**: 对比多种矿产品价格
   - 参数: `minerals` (矿种列表)

## 📝 使用示例

```bash
# 启动单个 Server 测试
python servers/news_server.py

# 使用 MCP Inspector 测试（需安装）
npx -y @modelcontextprotocol/inspector
# 在 Inspector 中连接: http://localhost:8001/mcp
```

## 📁 项目结构

```
mining-rights-agent/
├── agent/
│   ├── __init__.py
│   ├── state.py        # LangGraph 状态定义
│   ├── workflow.py     # LangGraph 工作流
│   └── main.py         # Agent 入口
├── servers/
│   ├── news_server.py      # 新闻摘要服务
│   ├── reserves_server.py  # 储量数据服务
│   └── price_server.py     # 价格走势服务
├── mcp-config.json      # MCP 配置文件
├── docker-compose.yml   # Docker Compose 配置
├── Dockerfile.server    # Server Dockerfile
├── Dockerfile.agent     # Agent Dockerfile
├── pyproject.toml       # Python 项目配置
├── requirements.txt     # 依赖列表
└── RUN.md               # 运行指南
```

## ⚠️ 注意事项

1. **API Key**: 运行 Agent 需要配置 Anthropic API Key
2. **端口占用**: 请确保 8001, 8002, 8003 端口未被占用
3. **网络访问**: 部分数据服务需要外网访问权限
4. **开发模式**: 默认使用内置模拟数据，可替换为真实数据源

## 🛠️ 调试

```bash
# 查看 Server 日志
python servers/news_server.py --verbose

# 测试单个工具调用
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/list","params":{}}'
```
