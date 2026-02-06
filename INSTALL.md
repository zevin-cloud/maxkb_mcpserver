# MaxKB MCP Server - Linux 快速部署指南

## 方式一：一键脚本部署（推荐）

### 1. 快速安装

```bash
# 下载并运行部署脚本
curl -fsSL https://raw.githubusercontent.com/zevin-cloud/maxkb_mcpserver/main/deploy.sh | sudo bash

# 或者使用 wget
wget -qO- https://raw.githubusercontent.com/zevin-cloud/maxkb_mcpserver/main/deploy.sh | sudo bash
```

### 2. 配置环境变量

```bash
# 编辑配置文件
nano /opt/maxkb-mcp-server/.env
```

填写你的 MaxKB 配置：
```env
MAXKB_BASE_URL=https://your-maxkb-server.com
MAXKB_API_KEY=your-api-key-here
```

### 3. 启动服务

```bash
# 方式 A：使用 systemd（推荐，支持开机自启）
systemctl start maxkb-mcp-server
systemctl enable maxkb-mcp-server  # 开机自启

# 方式 B：直接启动
cd /opt/maxkb-mcp-server && ./start.sh
```

### 4. 验证安装

```bash
# 检查服务状态
systemctl status maxkb-mcp-server

# 测试接口
curl http://localhost:3000/sse

# 查看日志
journalctl -u maxkb-mcp-server -f
```

---

## 方式二：Docker 部署

### 1. 快速启动

```bash
# 克隆项目
git clone https://github.com/zevin-cloud/maxkb_mcpserver.git
cd maxkb_mcpserver

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 启动服务
docker-compose up -d
```

### 2. 常用命令

```bash
# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新到最新版本
git pull
docker-compose up -d --build
```

---

## 方式三：手动部署

### 1. 安装依赖

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git
```

**CentOS/RHEL:**
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip git
```

### 2. 部署项目

```bash
# 创建目录
sudo mkdir -p /opt/maxkb-mcp-server
cd /opt/maxkb-mcp-server

# 克隆代码
sudo git clone https://github.com/zevin-cloud/maxkb_mcpserver.git .

# 创建虚拟环境
sudo python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install fastmcp>=0.4.0 httpx>=0.27.0 pydantic>=2.0.0 pydantic-settings>=2.0.0 uvicorn starlette

# 配置环境变量
sudo cp .env.example .env
sudo nano .env  # 编辑配置
```

### 3. 创建 Systemd 服务

```bash
sudo tee /etc/systemd/system/maxkb-mcp-server.service > /dev/null <<EOF
[Unit]
Description=MaxKB MCP Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/maxkb-mcp-server
Environment=PATH=/opt/maxkb-mcp-server/venv/bin
ExecStart=/opt/maxkb-mcp-server/venv/bin/python -m src
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 重载配置并启动
sudo systemctl daemon-reload
sudo systemctl start maxkb-mcp-server
sudo systemctl enable maxkb-mcp-server
```

---

## 配置说明

### 环境变量

| 变量名 | 必填 | 默认值 | 说明 |
|-------|------|-------|------|
| `MAXKB_BASE_URL` | 是 | - | MaxKB 服务器地址 |
| `MAXKB_API_KEY` | 是 | - | MaxKB API 密钥 |
| `MAXKB_WORKSPACE_ID` | 否 | default | 工作空间 ID |
| `MCP_TRANSPORT` | 否 | sse | 传输模式: stdio/sse |
| `MCP_HOST` | 否 | 0.0.0.0 | 监听地址 |
| `MCP_PORT` | 否 | 3000 | 监听端口 |

### 传输模式选择

| 模式 | 适用场景 | 配置方式 |
|-----|---------|---------|
| `sse` | Dify、远程调用 | `MCP_TRANSPORT=sse` |
| `stdio` | Claude Desktop、Cursor | `MCP_TRANSPORT=stdio` |

---

## 集成配置

### Dify 配置

在 Dify 的 **Settings > MCP** 中添加：

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

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) 或 `%APPDATA%\Claude\claude_desktop_config.json` (Windows)：

```json
{
  "mcpServers": {
    "maxkb": {
      "command": "python",
      "args": ["-m", "src"],
      "cwd": "/opt/maxkb-mcp-server",
      "env": {
        "MAXKB_BASE_URL": "https://your-maxkb.com",
        "MAXKB_API_KEY": "your-api-key",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

---

## 故障排查

### 服务无法启动

```bash
# 检查日志
journalctl -u maxkb-mcp-server -n 50

# 检查端口占用
netstat -tlnp | grep 3000

# 测试 MaxKB 连接
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-maxkb-server.com/admin/api/workspace/default/knowledge
```

### 权限问题

```bash
# 修复目录权限
sudo chown -R $USER:$USER /opt/maxkb-mcp-server

# 重新加载服务
sudo systemctl daemon-reload
sudo systemctl restart maxkb-mcp-server
```

### Docker 问题

```bash
# 查看容器日志
docker-compose logs -f maxkb-mcp-server

# 进入容器调试
docker-compose exec maxkb-mcp-server /bin/bash

# 检查环境变量
docker-compose exec maxkb-mcp-server env | grep MAXKB
```

---

## 更新升级

### 脚本部署升级

```bash
cd /opt/maxkb-mcp-server
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart maxkb-mcp-server
```

### Docker 升级

```bash
git pull
docker-compose down
docker-compose up -d --build
```

---

## 卸载

```bash
# 停止并删除服务
sudo systemctl stop maxkb-mcp-server
sudo systemctl disable maxkb-mcp-server
sudo rm /etc/systemd/system/maxkb-mcp-server.service
sudo systemctl daemon-reload

# 删除安装目录
sudo rm -rf /opt/maxkb-mcp-server

# Docker 卸载
docker-compose down -v
docker rmi maxkb-mcp-server:latest
```
