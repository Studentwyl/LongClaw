# 前端 README

## 项目结构

```
frontend/
├── src/
│   ├── components/       # 可复用组件
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── ChatInterface.tsx
│   │   ├── DocumentUpload.tsx
│   │   └── SkillsPanel.tsx
│   ├── pages/           # 页面
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── KnowledgeBasePage.tsx
│   │   ├── SkillsPage.tsx
│   │   └── ChatPage.tsx
│   ├── services/        # API 调用服务
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── knowledge.ts
│   │   ├── chat.ts
│   │   └── skills.ts
│   ├── stores/          # Zustand 状态管理
│   │   ├── authStore.ts
│   │   ├── knowledgeStore.ts
│   │   └── chatStore.ts
│   ├── utils/           # 工具函数
│   │   ├── request.ts   # HTTP 客户端
│   │   └── format.ts    # 格式化工具
│   ├── types/           # TypeScript 类型定义
│   ├── App.tsx          # 应用主组件
│   ├── main.tsx         # 入口文件
│   └── index.css        # 全局样式
├── public/              # 静态资源
├── package.json
├── tsconfig.json
├── vite.config.ts
├── Dockerfile
└── README.md
```

## 环境设置

### 1. 安装依赖

```bash
npm install
```

### 2. 环境变量

创建 `.env` 文件：

```
VITE_API_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000
```

## 开发

### 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动

### 构建

```bash
npm run build
```

### 预览构建结果

```bash
npm run preview
```

### 代码检查

```bash
npm run lint
```

## 页面说明

### 登录页面 (LoginPage.tsx)

- 用户注册
- 用户登录
- Token 存储

### 仪表板页面 (DashboardPage.tsx)

- 概览统计
- 快速操作
- 最近对话

### 知识库页面 (KnowledgeBasePage.tsx)

- 创建知识库
- 编辑知识库
- 删除知识库
- 管理文档
- 上传文档

### 对话页面 (ChatPage.tsx)

- 选择知识库
- 选择技能
- 发送消息
- 显示对话历史
- 显示溯源信息

### 技能页面 (SkillsPage.tsx)

- 创建技能
- 编辑技能
- 删除技能
- 配置参数

## 主要依赖

- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Zustand** - 状态管理
- **Axios** - HTTP 客户端
- **React Router** - 路由

## API 集成

所有 API 调用都通过 `services` 模块进行，例如：

```typescript
import { knowledgeService } from '@/services/knowledge'

// 创建知识库
const kb = await knowledgeService.create({
  name: '我的知识库',
  description: '描述'
})

// 获取知识库列表
const kbs = await knowledgeService.list()

// 上传文档
const doc = await knowledgeService.uploadDocument(kbId, file)
```

## 状态管理

使用 Zustand 进行全局状态管理：

```typescript
import { useAuthStore } from '@/stores/authStore'

const { user, token, login, logout } = useAuthStore()
```

## 样式

- 使用 CSS 模块
- 响应式设计
- 支持浅色/深色主题 (可选)

## 部署

### Docker

```bash
docker build -t longclaw-frontend .
docker run -p 5173:5173 longclaw-frontend
```

### 生产构建

```bash
npm run build
npm run preview
```

## 浏览器支持

- Chrome (最新版)
- Firefox (最新版)
- Safari (最新版)
- Edge (最新版)
