#!/bin/bash
# MaxKB MCP Server 快速部署脚本
# 支持 Ubuntu/Debian/CentOS/RHEL 系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量
INSTALL_DIR="/opt/maxkb-mcp-server"
SERVICE_NAME="maxkb-mcp-server"
PYTHON_VERSION="3.10"

# 打印信息函数
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否以 root 运行
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "请使用 root 权限运行此脚本"
        exit 1
    fi
}

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
    else
        print_error "无法检测操作系统类型"
        exit 1
    fi
    print_info "检测到操作系统: $OS $VERSION"
}

# 安装 Python 和依赖
install_dependencies() {
    print_info "正在安装依赖..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        apt-get update
        apt-get install -y python3 python3-pip python3-venv git
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Fedora"* ]]; then
        yum update -y
        yum install -y python3 python3-pip git
    else
        print_error "不支持的操作系统: $OS"
        exit 1
    fi
    
    print_info "依赖安装完成"
}

# 克隆项目代码
clone_project() {
    print_info "正在克隆项目..."
    
    if [ -d "$INSTALL_DIR" ]; then
        print_warn "目录 $INSTALL_DIR 已存在，正在更新..."
        cd "$INSTALL_DIR"
        git pull
    else
        git clone https://github.com/zevin-cloud/maxkb_mcpserver.git "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi
    
    print_info "项目克隆完成"
}

# 创建虚拟环境并安装依赖
setup_venv() {
    print_info "正在创建虚拟环境..."
    
    python3 -m venv venv
    source venv/bin/activate
    
    print_info "正在安装 Python 依赖..."
    pip install --upgrade pip
    pip install fastmcp>=0.4.0 httpx>=0.27.0 pydantic>=2.0.0 pydantic-settings>=2.0.0 uvicorn starlette
    
    print_info "虚拟环境设置完成"
}

# 创建环境配置文件
create_env_file() {
    print_info "正在创建环境配置文件..."
    
    cat > "$INSTALL_DIR/.env" << 'EOF'
# MaxKB API 配置
MAXKB_BASE_URL=https://your-maxkb-server.com
MAXKB_API_KEY=your-api-key-here
MAXKB_WORKSPACE_ID=default

# MCP Server 配置
MCP_SERVER_NAME=maxkb-knowledge-base
MCP_SERVER_VERSION=0.1.0

# 传输模式配置
# 可选值: stdio, sse
# stdio: 适用于 Claude Desktop 等本地应用
# sse: 适用于 Dify 等远程调用
MCP_TRANSPORT=sse
MCP_HOST=0.0.0.0
MCP_PORT=3000
EOF

    print_info "环境配置文件已创建: $INSTALL_DIR/.env"
    print_warn "请编辑 .env 文件，配置你的 MaxKB 服务器地址和 API Key"
}

# 创建 systemd 服务文件
create_systemd_service() {
    print_info "正在创建 systemd 服务..."
    
    cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOF
[Unit]
Description=MaxKB MCP Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}
Environment=PATH=${INSTALL_DIR}/venv/bin
ExecStart=${INSTALL_DIR}/venv/bin/python -m src
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    print_info "systemd 服务已创建"
}

# 创建启动脚本
create_start_script() {
    print_info "正在创建启动脚本..."
    
    cat > "$INSTALL_DIR/start.sh" << 'EOF'
#!/bin/bash
# MaxKB MCP Server 启动脚本

cd "$(dirname "$0")"
source venv/bin/activate

# 检查环境变量
if [ ! -f .env ]; then
    echo "错误: 未找到 .env 配置文件"
    echo "请复制 .env.example 为 .env 并配置相关参数"
    exit 1
fi

# 启动服务
python -m src
EOF

    chmod +x "$INSTALL_DIR/start.sh"
    print_info "启动脚本已创建: $INSTALL_DIR/start.sh"
}

# 创建 Docker 部署文件
create_docker_files() {
    print_info "正在创建 Docker 部署文件..."
    
    # Dockerfile
    cat > "$INSTALL_DIR/Dockerfile" << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir fastmcp>=0.4.0 httpx>=0.27.0 pydantic>=2.0.0 pydantic-settings>=2.0.0 uvicorn starlette

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["python", "-m", "src"]
EOF

    # docker-compose.yml
    cat > "$INSTALL_DIR/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  maxkb-mcp-server:
    build: .
    container_name: maxkb-mcp-server
    ports:
      - "3000:3000"
    environment:
      - MAXKB_BASE_URL=${MAXKB_BASE_URL}
      - MAXKB_API_KEY=${MAXKB_API_KEY}
      - MAXKB_WORKSPACE_ID=${MAXKB_WORKSPACE_ID:-default}
      - MCP_TRANSPORT=${MCP_TRANSPORT:-sse}
      - MCP_HOST=0.0.0.0
      - MCP_PORT=3000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/sse"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
EOF

    print_info "Docker 部署文件已创建"
}

# 显示使用说明
show_usage() {
    echo ""
    echo "=========================================="
    echo "  MaxKB MCP Server 部署完成！"
    echo "=========================================="
    echo ""
    echo "安装目录: $INSTALL_DIR"
    echo ""
    echo "【后续步骤】"
    echo ""
    echo "1. 编辑配置文件:"
    echo "   nano $INSTALL_DIR/.env"
    echo ""
    echo "2. 启动方式（选择一种）:"
    echo ""
    echo "   方式 A - 直接启动:"
    echo "   cd $INSTALL_DIR && ./start.sh"
    echo ""
    echo "   方式 B - Systemd 服务:"
    echo "   systemctl start $SERVICE_NAME"
    echo "   systemctl enable $SERVICE_NAME  # 开机自启"
    echo ""
    echo "   方式 C - Docker 部署:"
    echo "   cd $INSTALL_DIR"
    echo "   docker-compose up -d"
    echo ""
    echo "3. 验证服务:"
    echo "   curl http://localhost:3000/sse"
    echo ""
    echo "【服务管理命令】"
    echo "   查看状态: systemctl status $SERVICE_NAME"
    echo "   启动服务: systemctl start $SERVICE_NAME"
    echo "   停止服务: systemctl stop $SERVICE_NAME"
    echo "   重启服务: systemctl restart $SERVICE_NAME"
    echo "   查看日志: journalctl -u $SERVICE_NAME -f"
    echo ""
    echo "【Dify 集成配置】"
    echo '   {"mcpServers": {"maxkb": {"url": "http://your-server-ip:3000/sse"}}}'
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    echo "=========================================="
    echo "  MaxKB MCP Server 快速部署脚本"
    echo "=========================================="
    echo ""
    
    check_root
    detect_os
    install_dependencies
    clone_project
    setup_venv
    create_env_file
    create_systemd_service
    create_start_script
    create_docker_files
    show_usage
}

# 运行主函数
main
