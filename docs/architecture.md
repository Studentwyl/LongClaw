# LongClaw 架构设计

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     前端 (React + TypeScript)                │
│              负责 UI、用户交互、状态管理                      │
└─────────────────────────────────────────────────────────────┘
                           ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI 应用服务层                         │
│  ┌─────────────┬──────────────┬──────────────┬─────────────┐
│  │ Auth        │ Knowledge    │  Skills      │  Chat       │
│  │ 认证        │  知识库      │  技能        │  对话       │
│  └─────────────┴──────────────┴──────────────┴─────────────┘
└─────────────────────────────────────────────────────────────┘
          ↓              ↓              ↓              ↓
    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
    │PostgreSQL│  │  Qdrant  │  │  MinIO   │  │ Ollama   │
    │  关系DB  │  │ 向量DB   │  │ 对象存储 │  │ 本地LLM  │
    └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

## 组件详解

### 1. 前端架构
```
React App
├── Pages (页面)
│   ├── LoginPage (登录)
│   ├── DashboardPage (仪表板)
│   ├── KnowledgeBasePage (知识库)
│   ├── SkillsPage (技能)
│   └── ChatPage (对话)
├── Components (组件)
│   ├── Header (头部)
│   ├── Sidebar (侧边栏)
│   ├── DocumentUpload (文档上传)
│   ├── ChatInterface (聊天界面)
│   └── ...
├── Services (服务)
│   ├── api.ts (API 调用)
│   ├── auth.ts (认证)
│   └── storage.ts (本地存储)
└── Store (状态管理 - Zustand)
    ├── authStore (认证状态)
    ├── knowledgeStore (知识库状态)
    └── chatStore (聊天状态)
```

### 2. 后端架构
```
FastAPI App
├── API 路由
│   ├── auth.py (认证)
│   ├── knowledge.py (知识库)
│   ├── skills.py (技能)
│   └── chat.py (对话)
├── 业务逻辑层 (Services)
│   ├── user_service.py
│   ├── knowledge_service.py
│   ├── skill_service.py
│   └── chat_service.py
├── 核心模块 (Core)
│   ├── config.py (配置)
│   ├── database.py (数据库连接)
│   ├── llm.py (LLM 抽象层)
│   ├── vector_store.py (Qdrant 集成)
│   ├── file_storage.py (MinIO 集成)
│   └── document_parser.py (文档解析)
├── 数据模型 (Models)
│   ├── user.py
│   ├── knowledge_base.py
│   ├── skills.py
│   ├── conversation.py
│   └── usage.py
├── 数据模式 (Schemas)
│   └── 各种 Pydantic 模型
└── 中间件 (Middleware)
    ├── 认证中间件
    ├── 错误处理
    └── 日志记录
```

### 3. 数据流

#### 上传知识库文档流程
```
1. 用户上传文件
   ↓
2. FastAPI 接收并校验
   ↓
3. 文件保存到 MinIO
   ↓
4. 调用 DocumentParser 解析
   ↓
5. 分块处理 (LangChain TextSplitter)
   ↓
6. 生成向量 (使用 LLM 的 embedding)
   ↓
7. 向量和元数据存储到 Qdrant
   ↓
8. 文档信息存储到 PostgreSQL
   ↓
9. 返回成功响应
```

#### 对话流程
```
1. 用户发送消息
   ↓
2. FastAPI 接收并保存消息
   ↓
3. 提取用户查询的向量
   ↓
4. 在 Qdrant 中搜索相关知识库内容
   ↓
5. 检查是否需要调用 Skills
   ↓
6. 构建 LLM 提示词 (prompt)
   ↓
7. 调用 LLM (Ollama / 国内厂商)
   ↓
8. 获取 LLM 回复
   ↓
9. 保存消息和使用记录到 PostgreSQL
   ↓
10. 返回回复（包含溯源信息）
```

### 4. 存储设计

#### PostgreSQL 存储
- 用户和认证信息
- 知识库和文档元数据
- 对话和消息历史
- Skills 配置

#### Qdrant 存储
- 文档块的向量表示
- 向量的元数据 (文档ID, 块索引等)
- 用户隔离: 每个用户一个独立的 collection

#### MinIO 存储
- 原始上传的文档文件
- 用户隔离: 每个用户一个独立的 bucket 或前缀

### 5. LLM 抽象层设计

支持多个 LLM 提供者:
```python
# 使用工厂模式
class LLMProvider:
    async def chat(messages, **kwargs) -> str

class OllamaProvider(LLMProvider):  # 本地部署
class DashscopeProvider(LLMProvider):  # 阿里通义千问
class OpenAIProvider(LLMProvider):  # OpenAI

# 根据配置选择合适的提供者
provider = get_llm_provider()
response = await provider.chat(messages)
```

## 用户数据隔离方案

### 1. 数据库级别
- 所有表都有 `user_id` 字段
- 所有查询都过滤 `user_id`
- ORM 级别的自动隔离

### 2. 向量存储级别
- 每个用户的知识库使用独立的 Qdrant collection
- Collection 命名: `kb_{user_id}_{kb_id}`

### 3. 文件存储级别
- 每个用户的文件使用独立的前缀
- 路径: `{user_id}/{kb_id}/{document_id}/{file_name}`

### 4. API 级别
- 认证中间件提取 user_id
- 所有 API 自动注入 user_id
- 防止跨用户数据访问

## 安全性设计

### 认证
- JWT Token 方案
- Token 过期和刷新
- 密码哈希 (bcrypt)

### 授权
- 基于 user_id 的数据隔离
- 角色控制 (可扩展)

### 验证
- 输入数据验证 (Pydantic)
- 文件上传验证 (类型、大小等)
- SQL 注入防护 (ORM)

## 可扩展性设计

### 1. 水平扩展
- 无状态 API 服务
- 支持多实例部署
- 数据库连接池

### 2. 性能优化
- Redis 缓存 (可选)
- Qdrant 向量缓存
- 异步任务队列 (可选)
- 向量索引优化

### 3. 功能扩展
- 插件系统 (Skills)
- 自定义 LLM 提供者
- 自定义文档解析器
- Webhook 支持 (可选)

## 部署拓扑

```
┌──────────────────────────────────────────────┐
│           Docker Compose / K8s                │
├──────────────────────────────────────────────┤
│                                               │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │ Nginx    │→ │ Backend  │  │ Frontend  │  │
│  │ 反向代理 │  │ FastAPI  │  │ React     │  │
│  │ 80/443   │  │ 8000     │  │ 5173      │  │
│  └──────────┘  └──────────┘  └───────────┘  │
│                      ↓                        │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │PostgreSQL│  │ Qdrant   │  │  MinIO    │  │
│  │ 5432     │  │ 6333     │  │ 9000/9001 │  │
│  └──────────┘  └──────────┘  └───────────┘  │
│                      ↓                        │
│  ┌──────────────────────────────────────┐   │
│  │ Ollama (可选本地 LLM)                │   │
│  │ 11434                                │   │
│  └──────────────────────────────────────┘   │
│                                               │
└──────────────────────────────────────────────┘
```
