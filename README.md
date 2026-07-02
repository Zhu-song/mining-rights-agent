# 矿权日报 Agent

基于 MCP (Model Context Protocol) 协议的智能矿业简报生成系统，利用 LangGraph 编排多个 MCP Server，自动整合新闻、储量、价格等多维度数据，为矿业公司生成专业的今日简报。

## ✨ 核心特性

- **多源数据整合**：新闻摘要、储量数据、价格走势三位一体
- **双模式运行**：无需 API Key 即可运行的本地模式 / 基于 Claude 的增强模式
- **LangGraph 工作流**：6 节点流水线自动化生成简报
- **MCP 标准化接口**：支持 MCP Inspector 调试和扩展

## 🛠️ 技术栈

- **框架**: LangGraph, LangChain
- **协议**: MCP (Model Context Protocol)
- **语言**: Python >= 3.10
- **依赖管理**: uv / pip

## 📐 工作流架构

```
┌─────────────┐    ┌─────────────┐    ┌───────────────┐
│ parse_query │───▶│ fetch_news  │───▶│ fetch_reserves │
└─────────────┘    └─────────────┘    └───────────────┘
                                               │
                                               ▼
┌───────────────┐    ┌─────────────┐    ┌─────────────┐
│ generate_report │◀──│ analyze_risk│◀──│ fetch_price │
└───────────────┘    └─────────────┘    └─────────────┘
         │
         ▼
      [END]
```

| 节点 | 功能 |
|------|------|
| parse_query | 解析用户查询，提取公司、矿种、国家信息 |
| fetch_news | 获取公司新闻和政策更新 |
| fetch_reserves | 获取储量数据和资源报告 |
| fetch_price | 获取价格走势数据 |
| analyze_risk | 分析投资风险因素 |
| generate_report | 整合所有数据生成最终简报 |

## 🚀 快速启动

### 1. 环境准备

```bash
cd mining-rights-agent

source .venv/bin/activate
```

如果虚拟环境尚未配置，使用以下命令安装依赖：

```bash
uv sync
# 或使用 pip
pip install -e .
```

### 2. 运行 Agent（本地模式，无需 API Key）

```bash
python -m agent.main "给我生成一份关于 Pilbara 锂矿的今日简报"
```

### 3. 使用增强模式（需要 Anthropic API Key）

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 Anthropic API Key：

```env
ANTHROPIC_API_KEY=your-api-key-here
```

然后重新运行 Agent：

```bash
python -m agent.main "给我生成一份关于 Newmont 金矿的今日简报"
```

### 4. 测试单个 MCP Server

使用测试脚本测试所有 Server：

```bash
python test_mcp.py
```

使用 MCP Inspector 调试（stdio 模式）：

```bash
npx -y @modelcontextprotocol/inspector python servers/news_server.py
npx -y @modelcontextprotocol/inspector python servers/reserves_server.py
npx -y @modelcontextprotocol/inspector python servers/price_server.py
```

## 📡 MCP Server 工具

### NewsServer

| 工具 | 参数 | 说明 |
|------|------|------|
| `fetch_mining_news` | `company` (公司名称), `days` (天数，默认7) | 获取矿业公司新闻 |
| `search_policy_updates` | `country` (国家), `mineral` (矿种) | 搜索政策更新 |

### ReservesServer

| 工具 | 参数 | 说明 |
|------|------|------|
| `get_reserves_data` | `company` (公司名称), `mineral` (矿种，默认lithium) | 获取储量数据 |
| `get_resource_report` | `company` (公司名称) | 获取资源报告 |

### PriceServer

| 工具 | 参数 | 说明 |
|------|------|------|
| `get_price_trend` | `mineral` (矿种), `days` (天数，默认30) | 获取价格走势 |
| `get_price_comparison` | `minerals` (矿种列表) | 对比多种矿产品价格 |

## 📁 项目结构

```
mining-rights-agent/
├── agent/
│   ├── __init__.py
│   ├── state.py        # LangGraph 状态定义
│   ├── workflow.py     # LangGraph 工作流编排
│   └── main.py         # Agent 入口
├── servers/
│   ├── news_server.py      # 新闻摘要服务
│   ├── reserves_server.py  # 储量数据服务
│   └── price_server.py     # 价格走势服务
├── test_mcp.py         # MCP Server 测试脚本
├── docker-compose.yml  # Docker Compose 配置
├── Dockerfile          # Docker 镜像构建文件
├── .dockerignore       # Docker 构建忽略文件
├── pyproject.toml      # Python 项目配置
├── .env.example        # 环境变量模板
└── .venv/              # Python 虚拟环境
```

## 🔧 配置说明

### 支持的公司

- Pilbara Minerals（锂矿）
- Newmont（金矿、铜矿）
- Barrick Gold（金矿）

### 支持的矿种

- lithium（锂）
- gold（金）
- copper（铜）
- iron_ore（铁矿石）

### 支持的国家

- Australia（澳大利亚）
- Canada（加拿大）
- China（中国）

## 🧪 运行测试

```bash
python test_mcp.py
```

## ⚠️ 注意事项

1. **本地模式**：默认使用内置模拟数据，无需 API Key
2. **增强模式**：配置 Anthropic API Key 后可使用 LLM 进行智能查询解析和风险分析
3. **MCP 传输**：所有 Server 使用 stdio 传输，无需端口配置
4. **数据来源**：当前使用模拟数据，可替换为真实数据源

## 📝 使用示例

```bash
# 查询 Pilbara 锂矿
python -m agent.main "给我生成一份关于 Pilbara 锂矿的今日简报"

# 查询 Newmont 金矿
python -m agent.main "给我生成一份关于 Newmont 金矿的今日简报"

# 查询 Barrick 金矿
python -m agent.main "给我生成一份关于 Barrick Gold 的今日简报"
```

## 🐳 Docker 部署

### 使用默认查询启动

```bash
cd mining-rights-agent
docker-compose up --build
```

### 使用自定义查询

```bash
docker-compose run --rm mining-agent "给我生成一份关于 Newmont 金矿的今日简报"
```

### 使用增强模式（配置 API Key）

```bash
cp .env.example .env
# 编辑 .env 文件，填入 Anthropic API Key
docker-compose up --build
```

### 直接使用 Docker 命令

```bash
docker build -t mining-rights-agent .
docker run --rm mining-rights-agent "给我生成一份关于 Barrick Gold 的今日简报"
```

### Dockerfile 说明

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY agent/ ./agent/
COPY servers/ ./servers/

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["python", "-m", "agent.main"]
```

### docker-compose.yml 说明

- 使用 `env_file` 加载环境变量
- 默认执行 Pilbara 锂矿简报查询
- 通过 `docker-compose run` 可传入自定义查询参数