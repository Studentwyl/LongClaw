"""技能数据模式"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class SkillParameterSchema(BaseModel):
    """技能参数"""
    param_name: str
    param_type: str
    required: bool = False
    description: Optional[str] = None


class SkillCreate(BaseModel):
    """创建技能"""
    name: str
    description: Optional[str] = None
    type: str
    config: Optional[Dict[str, Any]] = None
    parameters: Optional[List[SkillParameterSchema]] = None


class SkillUpdate(BaseModel):
    """更新技能"""
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class SkillResponse(BaseModel):
    """技能响应"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    type: str
    config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
