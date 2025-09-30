#!/bin/bash

# Rapidapp One-Click Setup Script
# This script sets up the entire development environment from scratch

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Rapidapp One-Click Setup${NC}"
echo -e "${BLUE}==============================${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install dependencies based on OS
install_dependencies() {
    echo -e "${YELLOW}📦 Installing system dependencies...${NC}"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        sudo apt update
        sudo apt install -y curl wget git build-essential pkg-config libssl-dev
        
        # Install Docker if not present
        if ! command_exists docker; then
            echo -e "${YELLOW}🐳 Installing Docker...${NC}"
            sudo apt install -y docker.io docker-compose
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker $USER
        fi
        
        # Install Node.js 20
        if ! command_exists node || [[ $(node -v | cut -d'.' -f1 | cut -d'v' -f2) -lt 20 ]]; then
            echo -e "${YELLOW}📱 Installing Node.js 20...${NC}"
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt-get install -y nodejs
        fi
        
        # Install pnpm
        if ! command_exists pnpm; then
            echo -e "${YELLOW}📦 Installing pnpm...${NC}"
            sudo npm install -g pnpm
        fi
        
        # Install Rust
        if ! command_exists cargo; then
            echo -e "${YELLOW}🦀 Installing Rust...${NC}"
            curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
            source "$HOME/.cargo/env"
        fi
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! command_exists brew; then
            echo -e "${RED}❌ Homebrew required on macOS. Please install: https://brew.sh${NC}"
            exit 1
        fi
        
        brew install docker docker-compose node@20 pnpm rust pkg-config openssl
    else
        echo -e "${RED}❌ Unsupported operating system${NC}"
        exit 1
    fi
}

# Check and install dependencies
install_dependencies

# Verify Node.js version
NODE_VERSION=$(node -v | cut -d'.' -f1 | cut -d'v' -f2)
if [[ $NODE_VERSION -lt 20 ]]; then
    echo -e "${RED}❌ Node.js 20+ required, found version $(node -v)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ System dependencies installed${NC}"

# Install project dependencies
echo -e "${YELLOW}📦 Installing project dependencies...${NC}"
pnpm install

# Create missing directories and files
echo -e "${YELLOW}📁 Creating missing project structure...${NC}"

# Ensure all required directories exist
mkdir -p packages/eslint-config-custom
mkdir -p packages/templates/src
mkdir -p services/feature-flags
mkdir -p services/validation-pipeline

echo -e "${GREEN}✅ Project dependencies installed${NC}"

# Fix configuration files
echo -e "${YELLOW}⚙️ Fixing configuration issues...${NC}"

# Create environment files for services
create_env_files() {
    echo -e "${YELLOW}📝 Creating environment configuration files...${NC}"
    
    # Event store .env
    if [[ ! -f "services/event-store/.env" ]]; then
        cat > services/event-store/.env << 'EOF'
DATABASE_URL=postgresql://event_store_user:password@localhost:5432/event_store
REDIS_URL=redis://localhost:6379
PORT=3001
RUST_LOG=info
JAEGER_ENDPOINT=http://localhost:14268/api/traces
EOF
        echo -e "${GREEN}✅ Created event-store .env file${NC}"
    fi
    
    # Collab engine .env
    if [[ ! -f "services/collab-engine/.env" ]]; then
        cat > services/collab-engine/.env << 'EOF'
PORT=3002
REDIS_URL=redis://localhost:6379
EVENT_STORE_URL=http://localhost:3001
JAEGER_ENDPOINT=http://localhost:14268/api/traces
NODE_ENV=development
EOF
        echo -e "${GREEN}✅ Created collab-engine .env file${NC}"
    fi
    
    # Orchestrator .env
    if [[ ! -f "services/orchestrator/.env" ]]; then
        cat > services/orchestrator/.env << 'EOF'
DATABASE_URL=postgresql://orchestrator_user:password@localhost:5432/orchestrator
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017/orchestrator
JAEGER_ENDPOINT=http://localhost:14268/api/traces
PYTHON_ENV=development
EOF
        echo -e "${GREEN}✅ Created orchestrator .env file${NC}"
    fi
}

# Create the environment files
create_env_files

# Fix configuration files

# Start infrastructure
echo -e "${YELLOW}🐳 Starting infrastructure services...${NC}"
if groups $USER | grep -q docker; then
    docker-compose up -d postgres redis mongodb jaeger prometheus grafana
else
    sudo docker-compose up -d postgres redis mongodb jaeger prometheus grafana
fi

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 15

# Verify services
echo -e "${YELLOW}🔍 Verifying services...${NC}"
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo -e "${GREEN}✅ Grafana running${NC}"
else
    echo -e "${YELLOW}⚠️ Grafana starting up...${NC}"
fi

if curl -s http://localhost:16686/api/services > /dev/null; then
    echo -e "${GREEN}✅ Jaeger running${NC}"
else
    echo -e "${YELLOW}⚠️ Jaeger starting up...${NC}"
fi

if curl -s http://localhost:9090/-/healthy > /dev/null; then
    echo -e "${GREEN}✅ Prometheus running${NC}"
else
    echo -e "${YELLOW}⚠️ Prometheus starting up...${NC}"
fi

echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🌐 Access your services:${NC}"
echo -e "  📊 Grafana:    http://localhost:3000 (admin/admin)"
echo -e "  🔍 Jaeger:     http://localhost:16686"
echo -e "  📈 Prometheus: http://localhost:9090"
echo -e "  🐘 PostgreSQL: localhost:5432"
echo -e "  🔴 Redis:      localhost:6379"
echo -e "  🍃 MongoDB:    localhost:27017"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}📚 Next steps:${NC}"
echo -e "  • Run 'make dev' to start development servers"
echo -e "  • Run 'pnpm cli new my-app' to create a new app"
echo -e "  • Check 'make help' for more commands"

if ! groups $USER | grep -q docker; then
    echo -e "${YELLOW}⚠️ You may need to log out and log back in for Docker permissions to take effect${NC}"
fi