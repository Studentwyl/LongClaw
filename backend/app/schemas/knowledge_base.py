"""知识库数据模式"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class KnowledgeBaseCreate(BaseModel):
    """创建知识库"""
    name: str
    description: Optional[str] = None


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库"""
    name: Optional[str] = None
    description: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    vector_collection_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """文档响应"""
    id: int
    knowledge_base_id: int
    file_name: str
    file_size: int
    file_type: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
