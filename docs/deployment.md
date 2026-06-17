# LongClaw 部署指南

## 前置要求

- Docker & Docker Compose
- Git
- Python 3.11+ (本地开发)
- Node.js 18+ (前端开发)

## 快速开始 (Docker Compose)

### 1. 克隆项目
```bash
git clone https://github.com/Studentwyl/LongClaw.git
cd LongClaw
```

### 2. 配置环境变量
```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，配置必要的参数
```

### 3. 启动所有服务
```bash
cd backend
docker-compose up -d
```

### 4. 检查服务状态
```bash
docker-compose ps

# 或查看日志
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f qdrant
docker-compose logs -f minio
docker-compose logs -f ollama
```

### 5. 初始化数据库 (首次)
```bash
docker-compose exec backend python -m alembic upgrade head
```

### 6. 访问应用

- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- Qdrant UI: http://localhost:6333/dashboard
- MinIO 控制台: http://localhost:9001 (用户名/密码: minioadmin/minioadmin)

## 服务说明

### PostgreSQL (5432)
关系数据库，存储用户、知识库、对话等数据。

**初始化**:
```sql
CREATE DATABASE longclaw;
CREATE USER longclaw WITH PASSWORD 'longclaw_password';
ALTER ROLE longclaw SET client_encoding TO 'utf8';
```

### Qdrant (6333)
向量数据库，存储文档向量用于相似度搜索。

**访问**:
- HTTP: http://localhost:6333
- 管理 UI: http://localhost:6333/dashboard

### MinIO (9000/9001)
S3 兼容的对象存储，用于存储上传的文档。

**访问**:
- API: http://localhost:9000
- 控制台: http://localhost:9001

**创建 bucket**:
```bash
docker-compose exec minio mc mb minio/longclaw
```

### Ollama (11434)
本地 LLM 服务 (可选)。

**拉取模型**:
```bash
docker-compose exec ollama ollama pull mistral
# 或
docker-compose exec ollama ollama pull llama2
```

### FastAPI Backend (8000)
Python 后端应用。

**API 文档**: http://localhost:8000/docs (Swagger UI)

### React Frontend (5173)
React 前端应用。

## 本地开发

### 后端开发

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 复制环境变量
cp .env.example .env

# 5. 启动开发服务器
python -m uvicorn app.main:app --reload

# 后端将在 http://localhost:8000 启动
```

### 前端开发

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 前端将在 http://localhost:5173 启动
```

## 生产部署

### 方案 1: 单服务器 Docker Compose

```bash
# 在服务器上执行
git clone https://github.com/Studentwyl/LongClaw.git
cd LongClaw/backend

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 启动
docker-compose -f docker-compose.yml up -d

# 查看状态
docker-compose ps
```

### 方案 2: 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 方案 3: 使用 Kubernetes

```yaml
# 待补充 - K8s manifests
```

## 配置参数详解

### 后端环境变量 (.env)

| 变量 | 说明 | 示例 |
|-----|------|------|
| DATABASE_URL | PostgreSQL 连接字符串 | postgresql://user:pass@host:5432/db |
| QDRANT_HOST | Qdrant 主机 | localhost |
| QDRANT_PORT | Qdrant 端口 | 6333 |
| MINIO_ENDPOINT | MinIO 端点 | localhost:9000 |
| MINIO_ACCESS_KEY | MinIO 访问密钥 | minioadmin |
| MINIO_SECRET_KEY | MinIO 密钥 | minioadmin |
| LLM_PROVIDER | LLM 提供者 | ollama 或 dashscope 或 openai |
| OLLAMA_BASE_URL | Ollama 地址 | http://localhost:11434 |
| OLLAMA_MODEL | Ollama 模型 | mistral |
| SECRET_KEY | JWT 密钥 | 生成随机值 |

## 日志和监控

### 查看服务日志

```bash
# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f qdrant
```

### 常见问题排查

#### 1. 数据库连接失败
```bash
# 检查 PostgreSQL 服务
docker-compose ps postgres

# 测试连接
docker-compose exec postgres psql -U longclaw -d longclaw
```

#### 2. Qdrant 连接失败
```bash
# 检查 Qdrant 服务
docker-compose ps qdrant

# 测试连接
curl http://localhost:6333/health
```

#### 3. MinIO 连接失败
```bash
# 检查 MinIO 服务
docker-compose ps minio

# 测试连接
curl http://localhost:9000/minio/health/live
```

#### 4. LLM 调用失败
```bash
# 检查 Ollama 服务
docker-compose ps ollama

# 测试调用
curl http://localhost:11434/api/tags

# 拉取模型 (如未拉取)
docker-compose exec ollama ollama pull mistral
```

## 备份和恢复

### 备份 PostgreSQL
```bash
docker-compose exec postgres pg_dump -U longclaw longclaw > backup.sql
```

### 恢复 PostgreSQL
```bash
docker-compose exec -T postgres psql -U longclaw longclaw < backup.sql
```

### 备份 Qdrant
```bash
docker-compose exec qdrant mkdir -p /qdrant/snapshots
docker-compose exec qdrant curl -X POST http://localhost:6333/snapshots
```

### 备份 MinIO
```bash
docker-compose exec minio mc mirror minio/longclaw ./backups/minio
```

## 更新和升级

### 更新代码
```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

### 数据库迁移
```bash
docker-compose exec backend alembic upgrade head
```

## 安全建议

1. 修改默认密钥和密码
   - MinIO: minioadmin
   - PostgreSQL: longclaw_password
   - JWT SECRET_KEY

2. 启用 HTTPS
   - 使用 Let's Encrypt 获取证书
   - 配置 Nginx 反向代理

3. 防火墙配置
   - 只允许必要的端口外出
   - 限制数据库访问

4. 定期备份
   - 数据库备份
   - 文件存储备份

## 性能优化

1. 调整 PostgreSQL 配置
2. 增加 Qdrant 向量索引大小
3. 启用 Redis 缓存 (可选)
4. 使用 CDN 加速前端资源

## 监控和告警

1. 设置数据库监控
2. 设置应用性能监控 (APM)
3. 配置错误告警
4. 设置健康检查告警
