# MaxKB MCP Server

MaxKB 知识库的 MCP (Model Context Protocol) 服务，支持通过 SSE 或 stdio 方式访问 MaxKB 知识库。

## 功能

- **list_knowledge_bases** - 列出所有知识库
- **get_knowledge_base_info** - 获取知识库详情
- **search_knowledge_base** - 搜索知识库内容（支持向量检索和关键词检索）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

编辑 `.env` 文件：

```env
# MaxKB API Configuration
MAXKB_BASE_URL=https://mk2.lovekd.top:20000
MAXKB_API_KEY=your-api-key

# MaxKB Workspace Configuration
MAXKB_WORKSPACE_ID=default

# MCP Server Configuration
MCP_SERVER_NAME=maxkb-knowledge-base
MCP_SERVER_VERSION=0.1.0

# Transport Configuration
# Options: stdio, sse
MCP_TRANSPORT=sse
MCP_HOST=0.0.0.0
MCP_PORT=3000
```

## 运行方式

### 方式 1：SSE 模式（推荐）

```bash
python -m src
```

服务启动后：
- SSE 端点：`http://0.0.0.0:3000/sse`
- 消息端点：`http://0.0.0.0:3000/messages/`

### 方式 2：stdio 模式

```bash
python -m src
```

（需要设置 `MCP_TRANSPORT=stdio`）

## 外部系统配置

### Dify 配置

```json
{
  "mcpServers": {
    "maxkb": {
      "url": "http://your-server-ip:3000/sse"
    }
  }
}
```

### Claude Desktop 配置

```json
{
  "mcpServers": {
    "maxkb": {
      "command": "python",
      "args": ["-m", "src"],
      "cwd": "/path/to/maxkb_mcpserver",
      "env": {
        "MAXKB_BASE_URL": "https://mk2.lovekd.top:20000",
        "MAXKB_API_KEY": "your-api-key",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

## 项目结构

```
maxkb_mcpserver/
├── src/
│   ├── __init__.py
│   ├── __main__.py      # 入口文件
│   ├── server.py        # MCP Server 实现
│   ├── client.py        # MaxKB API 客户端
│   ├── config.py        # 配置管理
│   └── models.py        # 数据模型
├── .env                 # 环境变量配置
├── requirements.txt     # 依赖列表
└── README.md           # 本文件
```

## 测试

```bash
# 测试知识库列表
python -c "import asyncio; from src.client import MaxKBClient; c = MaxKBClient(); print(asyncio.run(c.list_knowledge_bases()))"

# 测试搜索
python test_search2.py
```

## 提示词模板

见 `prompt_external.md` 文件，包含完整的 MCP 调用提示词。

## 注意事项

1. 确保 MaxKB API Key 有效
2. 确保防火墙允许访问 3000 端口（SSE 模式）
3. 首次使用建议先调用 `list_knowledge_bases` 获取知识库列表
