# LongClaw 🦞

## 项目介绍

**LongClaw** 是一个开源的 AI Agent 智能体平台。用户可以上传自己的知识库文档，为 Agent 添加自定义技能 (Skills)，然后通过多轮对话与 Agent 互动。所有用户的数据完全隔离，支持本地部署。

### 核心特性

- 🧠 **知识库问答** - 基于用户上传的文档进行智能问答
- 🛠️ **自定义 Skills** - 用户可添加自定义技能增强 Agent 能力
- 💬 **多轮对话** - 支持完整的上下文记忆
- 🔍 **溯源追踪** - 清晰显示 Agent 使用了哪些知识库和技能
- 👤 **用户隔离** - 每个用户的数据完全独立
- 🐳 **容器部署** - Docker Compose 一键启动
- 🌍 **多源 LLM** - 支持本地 Ollama 和国内厂商 API

### 支持的文件格式

- 📄 文本: txt, md
- 📕 文档: doc, docx
- 📊 演示: ppt, pptx
- 📑 PDF

## 技术栈

| 层级 | 技术 |
|-----|------|
| **前端** | React 18 + TypeScript + Vite |
| **后端** | Python 3.11 + FastAPI |
| **数据库** | PostgreSQL 15 |
| **向量库** | Qdrant |
| **文件存储** | MinIO |
| **LLM** | Ollama (本地) + 国内厂商支持 |
| **部署** | Docker + Docker Compose |

## 快速开始

### 使用 Docker Compose (推荐)

```bash
# 1. 克隆项目
git clone https://github.com/Studentwyl/LongClaw.git
cd LongClaw

# 2. 配置环境
cd backend
cp .env.example .env
# 根据需要编辑 .env

# 3. 启动所有服务
docker-compose up -d

# 4. 等待服务启动完成 (约 30-60 秒)
docker-compose ps

# 5. 访问应用
# 前端: http://localhost:5173
# 后端 API: http://localhost:8000/docs
# Qdrant UI: http://localhost:6333/dashboard
# MinIO: http://localhost:9001 (minioadmin/minioadmin)
```

### 本地开发

#### 后端开发

```bash
cd backend

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 启动后端 (需要 PostgreSQL、Qdrant、MinIO 运行)
python -m uvicorn app.main:app --reload
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 项目结构

```
LongClaw/
├── backend/                # Python 后端
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心模块
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # 数据模式
│   │   ├── services/      # 业务逻辑
│   │   ├── middleware/    # 中间件
│   │   └── main.py        # 应用入口
│   ├── requirements.txt   # 依赖清单
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/              # React 前端
│   ├── src/
│   │   ├── components/   # 组件
│   │   ├── pages/        # 页面
│   │   ├── services/     # 服务
│   │   └── App.tsx
│   ├── package.json
│   ├── Dockerfile
│   └── vite.config.ts
├── docs/                  # 文档
│   ├── requirements.md   # 需求文档
│   ├── architecture.md   # 架构设计
│   └── deployment.md     # 部署指南
└── README.md
```

## 使用示例

### 1. 用户注册/登录

```bash
# 注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "password123"
  }'

# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "password123"
  }'
```

### 2. 创建知识库

```bash
curl -X POST http://localhost:8000/api/knowledge-bases \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的第一个知识库",
    "description": "存储个人学习资料"
  }'
```

### 3. 上传文档

```bash
curl -X POST http://localhost:8000/api/knowledge-bases/{kb_id}/documents \
  -H "Authorization: Bearer {token}" \
  -F "file=@document.pdf"
```

### 4. 创建对话

```bash
curl -X POST http://localhost:8000/api/conversations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "我的第一个对话"
  }'
```

### 5. 发送消息

```bash
curl -X POST http://localhost:8000/api/conversations/{conv_id}/messages \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "你好，能帮我解释一下这个文档吗？",
    "knowledge_base_ids": [1],
    "skill_ids": []
  }'
```

详细 API 文档见 http://localhost:8000/docs

## 配置指南

### 支持的 LLM 提供者

#### 1. Ollama (本地部署)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

可用模型: mistral, llama2, neural-chat, etc.

```bash
# 拉取模型
docker-compose exec ollama ollama pull mistral
```

#### 2. 阿里云通义千问 (DashScope)
```env
LLM_PROVIDER=dashscope
DASHSCOPE_API_KEY=your_api_key
DASHSCOPE_MODEL=qwen-turbo
```

获取 API Key: https://dashscope.aliyuncs.com

#### 3. OpenAI
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-3.5-turbo
```

### 数据库配置

```env
DATABASE_URL=postgresql://longclaw:longclaw_password@localhost:5432/longclaw
```

### 文件存储配置

```env
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

## 文档

- [需求文档](./docs/requirements.md) - 功能需求和 API 设计
- [架构设计](./docs/architecture.md) - 系统架构和数据流
- [部署指南](./docs/deployment.md) - 部署步骤和配置

## 开发

### 后端开发指南

1. 环境设置
2. 数据库迁移
3. 测试

详见 [后端 README](./backend/README.md)

### 前端开发指南

1. 环境设置
2. 项目结构
3. 组件开发

详见 [前端 README](./frontend/README.md)

## 常见问题

### Q: 如何修改默认密码？
A: 编辑 `.env` 文件中的 `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` 等配置。

### Q: 如何使用国内的 LLM API？
A: 在 `.env` 中设置 `LLM_PROVIDER=dashscope`，并提供对应的 API Key。

### Q: 如何备份数据？
A: 参考 [部署指南 - 备份和恢复](./docs/deployment.md#备份和恢复)

### Q: 支持什么操作系统？
A: 任何支持 Docker 的操作系统 (Linux, macOS, Windows)

## 性能指标

- 支持用户数: 无限制 (取决于硬件)
- 文档上限: 无限制
- 向量搜索响应: <500ms
- LLM 响应: 取决于模型

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License - 详见 [LICENSE](./LICENSE)

## 联系方式

- GitHub: [@Studentwyl](https://github.com/Studentwyl)
- 问题反馈: GitHub Issues

## 鸣谢

感谢以下开源项目的支持：
- FastAPI
- React
- PostgreSQL
- Qdrant
- MinIO
- Ollama

---

**⭐ 如果这个项目对你有帮助，请给个 Star 吧！**
