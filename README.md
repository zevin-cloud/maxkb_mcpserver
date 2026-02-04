# MaxKB MCP Server

基于 MCP (Model Context Protocol) 的 MaxKB 知识库检索服务器，让 AI 助手可以通过标准协议访问 MaxKB 知识库。

## 功能特性

- **知识库列表**: 列出所有可用的知识库
- **知识库搜索**: 在指定知识库中搜索相关内容
- **智能问答**: 向知识库提问，获取 AI 生成的答案
- **MCP 协议**: 基于标准 MCP 协议，兼容 Claude Desktop 等客户端

## 安装

### 环境要求

- Python 3.10+
- MaxKB 服务已部署并运行

### 安装步骤

1. 克隆或下载本项目

2. 安装依赖
```bash
pip install -e .
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填写你的 MaxKB 配置
```

## 配置

创建 `.env` 文件并配置以下参数：

```env
# MaxKB API Configuration
MAXKB_BASE_URL=http://localhost:8080    # MaxKB 服务地址
MAXKB_API_KEY=your-api-key-here         # MaxKB API 密钥

# MCP Server Configuration
MCP_SERVER_NAME=maxkb-knowledge-base
MCP_SERVER_VERSION=0.1.0
```

### 获取 MaxKB API Key

1. 登录 MaxKB 管理后台
2. 进入「系统管理」->「API 密钥」
3. 创建新的 API 密钥并复制

## 使用

### 启动服务器

```bash
python -m src
```

### 在 Claude Desktop 中使用

1. 安装 Claude Desktop
2. 编辑配置文件：
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`

3. 添加 MCP Server 配置：

```json
{
  "mcpServers": {
    "maxkb": {
      "command": "python",
      "args": ["-m", "src"],
      "env": {
        "MAXKB_BASE_URL": "http://localhost:8080",
        "MAXKB_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

4. 重启 Claude Desktop，即可使用 MaxKB 工具

## 可用工具

### 1. list_knowledge_bases

列出所有可用的知识库。

**返回值**: 知识库列表（ID、名称、描述、文档数量）

### 2. get_knowledge_base_info

获取指定知识库的详细信息。

**参数**:
- `knowledge_base_id`: 知识库 ID

### 3. search_knowledge_base

在知识库中搜索相关内容。

**参数**:
- `query`: 搜索关键词
- `knowledge_base_id`: 知识库 ID
- `top_k`: 返回结果数量（1-20，默认 5）

**返回值**: 搜索结果列表（内容、标题、来源、相似度）

### 4. ask_question

向知识库提问，获取 AI 生成的答案。

**参数**:
- `question`: 问题内容
- `knowledge_base_id`: 知识库 ID

**返回值**: 答案和引用的参考资料

## 开发

### 代码格式化

```bash
ruff format src
ruff check --fix src
```

### 类型检查

```bash
mypy src
```

## 项目结构

```
maxkb-mcp-server/
├── src/
│   ├── __init__.py          # 包初始化
│   ├── __main__.py          # 入口文件
│   ├── server.py            # MCP Server 主逻辑
│   ├── client.py            # MaxKB API 客户端
│   ├── models.py            # 数据模型
│   └── config.py            # 配置管理
├── pyproject.toml           # 项目配置
├── .env.example             # 环境变量示例
└── README.md                # 本文档
```

## 技术栈

- **FastMCP**: MCP Python 框架
- **httpx**: 异步 HTTP 客户端
- **pydantic**: 数据模型验证

## 许可证

MIT License

## 相关链接

- [MaxKB 官网](https://maxkb.cn/)
- [MaxKB GitHub](https://github.com/1Panel-dev/MaxKB)
- [MCP 协议文档](https://modelcontextprotocol.io/)
