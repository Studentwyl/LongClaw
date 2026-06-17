# LongClaw 需求文档

## 项目概述

LongClaw 是一个 AI Agent 智能体平台，允许用户基于自己的知识库构建智能对话机器人。用户可以上传多种格式的文档作为知识库，添加自定义的 Skills (技能)，然后通过多轮对话与 Agent 交互。

## 核心功能

### 1. 用户管理
- 用户注册/登录
- 用户认证 (JWT)
- 用户信息管理
- 用户数据隔离

### 2. 知识库管理
- 创建/编辑/删除知识库
- 上传支持的文档格式: txt, md, doc, docx, pdf, ppt, pptx
- 文档自动解析和分块
- 向量化存储到 Qdrant
- 知识库版本管理 (可选)

### 3. Skills (技能) 系统
- 创建/编辑/删除 Skills
- Skill 参数配置
- Skill 调用和执行
- 内置 Skills (如网络搜索、计算等)

### 4. 对话功能
- 创建/管理对话会话
- 多轮对话记忆
- 基于知识库的问答
- 使用 Skills 增强对话
- 显示对话溯源 (使用了哪些知识库/Skills)

### 5. 文件存储
- 文档上传到 MinIO
- 文档管理和删除
- 文档预览 (可选)

## 技术栈

| 组件 | 技术 |
|-----|------|
| 前端 | React + TypeScript + Vite |
| 后端 | Python + FastAPI |
| 数据库 | PostgreSQL |
| 向量存储 | Qdrant |
| 文件存储 | MinIO |
| 文件解析 | LangChain + 补充库 |
| LLM | Ollama (本地) + 国内厂商 |
| 部署 | Docker + Docker Compose |

## API 端点设计

### 认证模块
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/profile` - 获取用户信息

### 知识库模块
- `GET /api/knowledge-bases` - 列出知识库
- `POST /api/knowledge-bases` - 创建知识库
- `GET /api/knowledge-bases/{id}` - 获取知识库详情
- `PUT /api/knowledge-bases/{id}` - 更新知识库
- `DELETE /api/knowledge-bases/{id}` - 删除知识库
- `POST /api/knowledge-bases/{id}/documents` - 上传文档
- `DELETE /api/knowledge-bases/{id}/documents/{doc_id}` - 删除文档

### Skills 模块
- `GET /api/skills` - 列出 Skills
- `POST /api/skills` - 创建 Skill
- `GET /api/skills/{id}` - 获取 Skill 详情
- `PUT /api/skills/{id}` - 更新 Skill
- `DELETE /api/skills/{id}` - 删除 Skill

### 对话模块
- `GET /api/conversations` - 列出对话
- `POST /api/conversations` - 创建对话
- `GET /api/conversations/{id}` - 获取对话详情
- `POST /api/conversations/{id}/messages` - 发送消息
- `GET /api/conversations/{id}/messages` - 获取消息历史
- `DELETE /api/conversations/{id}` - 删除对话

## 数据模型

### 用户表 (users)
- id, username, email, hashed_password, is_active, created_at, updated_at

### 知识库表 (knowledge_bases)
- id, user_id, name, description, vector_collection_name, created_at, updated_at

### 文档表 (documents)
- id, knowledge_base_id, file_name, file_path, file_size, file_type, content_hash, created_at, updated_at

### 文档块表 (document_chunks)
- id, document_id, chunk_index, content, vector_id, created_at

### Skills 表 (skills)
- id, user_id, name, description, type, config, created_at, updated_at

### 对话表 (conversations)
- id, user_id, title, description, created_at, updated_at

### 消息表 (messages)
- id, conversation_id, role, content, knowledge_base_ids, skill_ids, retrieved_chunks, created_at

## 部署方案

使用 Docker Compose 一键部署：
- PostgreSQL
- Qdrant
- MinIO
- Ollama (可选)
- FastAPI 后端
- React 前端

## 安全性

- 用户认证 (JWT)
- 密码加密 (bcrypt)
- 用户数据隔离
- API 速率限制 (可选)
- 输入验证和清理

## 扩展方向

1. 知识库搜索优化
2. 对话推荐
3. 成本统计和配额管理
4. 多模态支持 (图片、音频等)
5. 工作流自动化
6. 数据导出和备份
