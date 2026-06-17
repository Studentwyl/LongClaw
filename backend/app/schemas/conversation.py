"""对话数据模式"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ConversationCreate(BaseModel):
    """创建对话"""
    title: str
    description: Optional[str] = None


class MessageCreate(BaseModel):
    """创建消息"""
    content: str
    knowledge_base_ids: Optional[List[int]] = None
    skill_ids: Optional[List[int]] = None


class MessageResponse(BaseModel):
    """消息响应"""
    id: int
    conversation_id: int
    role: str
    content: str
    knowledge_base_ids: Optional[List[int]]
    skill_ids: Optional[List[int]]
    retrieved_chunks: Optional[List[dict]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """对话响应"""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
