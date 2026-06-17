"""对话 API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.services.chat_service import ChatService
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse
)
from typing import List

router = APIRouter(prefix="/api/conversations", tags=["chat"])


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conv_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建对话"""
    service = ChatService(db)
    conv = service.create_conversation(
        current_user.id,
        conv_data.title,
        conv_data.description
    )
    return conv


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取对话列表"""
    service = ChatService(db)
    return service.get_conversations(current_user.id, skip, limit)


@router.get("/{conv_id}", response_model=ConversationResponse)
async def get_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取对话详情"""
    service = ChatService(db)
    conv = service.get_conversation(current_user.id, conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")
    return conv


@router.delete("/{conv_id}")
async def delete_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除对话"""
    service = ChatService(db)
    try:
        service.delete_conversation(current_user.id, conv_id)
        return {"message": "对话已删除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{conv_id}/messages", response_model=List[MessageResponse])
async def list_messages(
    conv_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取消息历史"""
    service = ChatService(db)
    try:
        return service.get_messages(current_user.id, conv_id, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{conv_id}/messages", response_model=MessageResponse)
async def send_message(
    conv_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送消息"""
    service = ChatService(db)
    try:
        response = await service.send_message(
            current_user.id,
            conv_id,
            message_data.content,
            message_data.knowledge_base_ids,
            message_data.skill_ids
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")
