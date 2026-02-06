# MaxKB MCP Server 技术方案

> 基于 MCP (Model Context Protocol) 协议的 MaxKB 知识库检索服务
> 
> 作者：售前工程师
> 日期：2025年2月

---

## 一、方案概述

### 1.1 什么是 MCP？

MCP (Model Context Protocol) 是由 Anthropic 推出的开放协议，旨在标准化 AI 模型与外部数据源、工具之间的集成方式。它解决了传统 AI 集成中的以下痛点：

| 传统集成方式 | MCP 协议方式 |
|------------|-------------|
| 每个工具需要单独开发适配器 | 一次开发，多处复用 |
| 缺乏统一的数据交换标准 | 标准化的 JSON-RPC 通信 |
| 配置分散，难以管理 | 统一的 Server 配置中心 |
| 安全性难以保障 | 内置的权限和认证机制 |

### 1.2 MaxKB MCP Server 定位

本项目实现了 **MaxKB 知识库与 MCP 生态的桥梁**，使任何支持 MCP 的 AI 应用（如 Claude Desktop、Dify、Cursor 等）都能无缝访问 MaxKB 的知识库能力。

```
┌─────────────────────────────────────────────────────────────┐
│                      AI 应用层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │Claude Desktop│  │    Dify     │  │      Cursor         │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────────┼────────────┘
          │                │                    │
          └────────────────┴────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  MCP 协议层  │
                    │  (JSON-RPC) │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │ MaxKB MCP │   │ 其他 MCP  │   │ 其他 MCP  │
    │  Server   │   │  Server   │   │  Server   │
    └─────┬─────┘   └───────────┘   └───────────┘
          │
    ┌─────▼─────────────────────────────────────┐
    │              MaxKB 知识库                  │
    │  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
    │  │知识库 A │  │知识库 B │  │知识库 C │   │
    │  └─────────┘  └─────────┘  └─────────┘   │
    └───────────────────────────────────────────┘
```

---

## 二、核心功能

### 2.1 提供的 MCP Tools

| Tool 名称 | 功能描述 | 适用场景 |
|----------|---------|---------|
| `list_knowledge_bases` | 列出所有可用的知识库 | 让用户选择要查询的知识库 |
| `get_knowledge_base_info` | 获取知识库详细信息 | 展示知识库元数据、文档数量等 |
| `search_knowledge_base` | 在知识库中搜索内容 | 核心检索功能，支持向量/关键词检索 |

### 2.2 搜索功能特性

```python
search_knowledge_base(
    query: str,              # 搜索查询文本
    knowledge_base_id: str,  # 目标知识库 ID
    top_k: int = 5,          # 返回结果数量 (1-50)
    similarity: float = 0.6, # 相似度阈值 (0.0-1.0)
    search_mode: str = "embedding"  # 检索模式：embedding/keywords
)
```

**检索模式对比：**

| 模式 | 原理 | 优势 | 适用场景 |
|-----|------|-----|---------|
| `embedding` | 向量语义检索 | 理解语义，召回率高 | 自然语言问答 |
| `keywords` | 关键词匹配 | 精确匹配，速度快 | 特定术语查询 |

---

## 三、技术架构

### 3.1 项目结构

```
maxkb_mcpserver/
├── src/
│   ├── __init__.py          # 包初始化
│   ├── __main__.py          # 程序入口
│   ├── server.py            # MCP Server 核心实现
│   ├── client.py            # MaxKB API 客户端
│   ├── config.py            # 配置管理 (Pydantic Settings)
│   └── models.py            # 数据模型定义
├── .env                     # 环境变量配置 (不提交到 Git)
├── .gitignore               # Git 忽略规则
├── pyproject.toml           # 项目依赖配置
└── README.md                # 使用说明
```

### 3.2 核心模块说明

#### 3.2.1 Config 模块 - 配置管理

使用 Pydantic Settings 实现类型安全的配置管理：

```python
class Settings(BaseSettings):
    """Server configuration settings."""
    model_config = SettingsConfigDict(
        env_file=".env",           # 从 .env 文件加载
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    maxkb_base_url: str = "http://localhost:8080"
    maxkb_api_key: str = ""
    maxkb_workspace_id: str = "default"
    mcp_transport: str = "stdio"   # stdio 或 sse
```

**优势：**
- 类型安全：所有配置项都有类型注解
- 环境隔离：开发/生产环境使用不同配置
- 敏感信息保护：API Key 等敏感信息存储在 `.env`，不进入版本控制

#### 3.2.2 Client 模块 - MaxKB API 封装

```python
class MaxKBClient:
    """Client for MaxKB API."""
    
    async def list_knowledge_bases(self) -> list[KnowledgeBase]:
        """获取知识库列表"""
        
    async def get_knowledge_base(self, kb_id: str) -> KnowledgeBase | None:
        """获取知识库详情"""
        
    async def search(self, request: SearchRequest) -> SearchResponse:
        """执行知识库搜索"""
```

**技术亮点：**
- 异步 HTTP 客户端 (httpx.AsyncClient)
- 自动认证处理 (Bearer Token)
- 完善的错误处理和重定向检测

#### 3.2.3 Server 模块 - MCP 协议实现

```python
# 初始化 MCP Server
mcp = FastMCP(settings.mcp_server_name)

@mcp.tool()
async def search_knowledge_base(...) -> str:
    """搜索知识库 - 暴露给 AI 使用的工具"""
    
# 支持两种传输模式
if settings.mcp_transport == "sse":
    # SSE 模式：适合远程调用
    starlette_app = Starlette(...)
else:
    # stdio 模式：适合本地集成
    mcp.run(transport="stdio")
```

### 3.3 传输模式对比

| 特性 | SSE 模式 | stdio 模式 |
|-----|---------|-----------|
| 通信方式 | HTTP Server-Sent Events | 标准输入输出 |
| 适用场景 | 远程服务、多客户端 | 本地桌面应用 |
| 配置复杂度 | 需要配置 IP/端口 | 零配置 |
| 代表应用 | Dify、自建服务 | Claude Desktop、Cursor |

---

## 四、部署方案

### 4.1 环境要求

- Python >= 3.10
- MaxKB API 访问权限
- 网络可达 MaxKB 服务

### 4.2 快速部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd maxkb_mcpserver

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写 MaxKB 配置

# 4. 启动服务
python -m src
```

### 4.3 配置说明

```env
# MaxKB API 配置
MAXKB_BASE_URL=https://your-maxkb-server.com
MAXKB_API_KEY=your-api-key
MAXKB_WORKSPACE_ID=default

# MCP Server 配置
MCP_SERVER_NAME=maxkb-knowledge-base
MCP_TRANSPORT=sse          # stdio 或 sse
MCP_HOST=0.0.0.0
MCP_PORT=3000
```

---

## 五、集成案例

### 5.1 与 Dify 集成

Dify 从 0.6.0 版本开始支持 MCP 协议，配置步骤：

1. 在 Dify 的 **Settings > MCP** 中添加配置：

```json
{
  "mcpServers": {
    "maxkb": {
      "url": "http://your-server-ip:3000/sse"
    }
  }
}
```

2. 在 Agent 应用中选择 MaxKB 工具

3. 即可在对话中使用知识库检索能力

### 5.2 与 Claude Desktop 集成

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "maxkb": {
      "command": "python",
      "args": ["-m", "src"],
      "cwd": "/path/to/maxkb_mcpserver",
      "env": {
        "MAXKB_BASE_URL": "https://your-maxkb.com",
        "MAXKB_API_KEY": "your-api-key",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### 5.3 与 Cursor 集成

在 Cursor 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "maxkb": {
      "command": "python",
      "args": ["-m", "src"],
      "cwd": "/path/to/maxkb_mcpserver",
      "env": {
        "MAXKB_BASE_URL": "...",
        "MAXKB_API_KEY": "...",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

---

## 六、技术优势

### 6.1 对客户的价值

| 价值点 | 说明 |
|-------|-----|
| **一次建设，多处复用** | 知识库维护一次，所有 AI 应用共享 |
| **降低集成成本** | 无需为每个 AI 应用单独开发接口 |
| **标准化接入** | 符合 MCP 标准，生态兼容性好 |
| **安全可控** | API Key 分级管理，访问权限可控 |

### 6.2 技术亮点

1. **异步高性能**：基于 asyncio 和 httpx，支持高并发
2. **类型安全**：全代码类型注解，Pydantic 数据校验
3. **灵活部署**：支持 SSE 和 stdio 两种模式
4. **易于扩展**：模块化设计，新增工具简单

### 6.3 与竞品的对比

| 特性 | MaxKB MCP | 传统 API 集成 | 其他知识库 MCP |
|-----|-----------|-------------|---------------|
| 标准化程度 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| 部署复杂度 | ⭐⭐ (简单) | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 生态兼容性 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| 中文支持 | ⭐⭐⭐⭐⭐ | - | ⭐⭐⭐ |
| 私有化部署 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 七、常见问题

### Q1: 支持哪些检索模式？
支持向量检索（embedding）和关键词检索（keywords）两种模式，可在调用时通过 `search_mode` 参数指定。

### Q2: 如何保护 API Key 安全？
- API Key 存储在 `.env` 文件，不提交到 Git
- 服务端到 MaxKB 使用 HTTPS 加密传输
- 支持通过环境变量注入配置

### Q3: 支持多工作空间吗？
支持，通过 `MAXKB_WORKSPACE_ID` 环境变量配置，可在不同工作空间间切换。

### Q4: 如何调试 MCP Server？
```bash
# 查看 MCP 工具列表
python -c "from src.server import mcp; print([t.name for t in mcp._tools])"

# 测试搜索功能
python test_search.py
```

---

## 八、总结

MaxKB MCP Server 是连接 MaxKB 知识库与 MCP 生态的关键组件，它：

1. **标准化**了知识库的访问接口
2. **简化**了 AI 应用的集成流程
3. **保护**了企业的知识资产安全
4. **扩展**了 MaxKB 的应用场景

通过本项目，客户可以轻松将 MaxKB 知识库能力注入到各种 AI 应用中，实现知识的高效复用。

---

## 附录

### 相关链接

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MaxKB 官方文档](https://maxkb.cn/)
- [FastMCP 框架](https://github.com/jlowin/fastmcp)

### 版本历史

| 版本 | 日期 | 更新内容 |
|-----|------|---------|
| 0.1.0 | 2025-02 | 初始版本，支持基础检索功能 |
