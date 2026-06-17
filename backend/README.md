# 后端 README

## 项目结构

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py       # 认证相关
│   │   ├── knowledge.py  # 知识库管理
│   │   ├── chat.py       # 对话接口
│   │   └── skills.py     # 技能管理
│   ├── core/             # 核心模块
│   │   ├── config.py     # 配置管理
│   │   ├── database.py   # 数据库连接
│   │   ├── llm.py        # LLM 抽象层
│   │   ├── vector_store.py  # Qdrant 集成
│   │   ├── file_storage.py  # MinIO 集成
│   │   └── document_parser.py # 文档解析
│   ├── models/           # SQLAlchemy 模型
│   │   ├── user.py
│   │   ├── knowledge_base.py
│   │   ├── skills.py
│   │   ├── conversation.py
│   │   └── usage.py
│   ├── schemas/          # Pydantic 数据模式
│   │   ├── user.py
│   │   ├── knowledge_base.py
│   │   ├── conversation.py
│   │   └── skill.py
│   ├── services/         # 业务逻辑服务
│   │   ├── knowledge_service.py
│   │   ├── chat_service.py
│   │   └── skill_service.py
│   ├── middleware/       # 中间件
│   ├── utils/            # 工具函数
│   │   ├── security.py   # JWT 和密码处理
│   │   └── dependencies.py # 依赖注入
│   └── main.py           # 应用入口
├── requirements.txt      # Python 依赖
├── .env.example          # 环境变量示例
├── Dockerfile            # Docker 镜像配置
└── docker-compose.yml    # Docker Compose 配置
```

## 环境设置

### 1. 创建虚拟环境

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件
```

## 运行

### 开发模式

```bash
python -m uvicorn app.main:app --reload
```

应用将在 `http://localhost:8000` 启动

### 生产模式

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API 文档

访问 http://localhost:8000/docs 查看 Swagger UI 文档

## 数据库迁移

第一次运行时，应用会自动创建所有数据库表。

如需手动创建或更新表：

```bash
alembic upgrade head
```

## 测试

### 用户注册

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 用户登录

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

获得 token 后，在后续请求中使用：

```bash
curl -X GET http://localhost:8000/api/knowledge-bases \
  -H "Authorization: Bearer <token>"
```

## 故障排查

### 数据库连接失败

检查 `.env` 文件中的 `DATABASE_URL` 是否正确

### Qdrant 连接失败

确保 Qdrant 服务正在运行

### MinIO 连接失败

检查 MinIO 的端点和凭证

## 性能优化

1. 启用数据库连接池
2. 使用异步操作
3. 缓存常用数据
4. 批量操作优化
