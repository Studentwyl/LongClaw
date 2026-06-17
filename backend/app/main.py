"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, knowledge, chat, skills
from app.core.database import Base, engine

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建应用
app = FastAPI(
    title="LongClaw",
    description="AI Agent 智能体平台 - 基于知识库和技能的对话系统",
    version="0.1.0"
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(auth.router)
app.include_router(knowledge.router)
app.include_router(chat.router)
app.include_router(skills.router)


@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "欢迎使用 LongClaw AI Agent 平台",
        "version": "0.1.0",
        "docs": "http://localhost:8000/docs"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
