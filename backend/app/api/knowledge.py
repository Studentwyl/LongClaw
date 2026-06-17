"""知识库 API"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.services.knowledge_service import KnowledgeService
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    DocumentResponse
)
from typing import List

router = APIRouter(prefix="/api/knowledge-bases", tags=["knowledge"])


@router.post("", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建知识库"""
    service = KnowledgeService(db)
    kb = service.create_knowledge_base(
        user_id=current_user.id,
        name=kb_data.name,
        description=kb_data.description
    )
    return kb


@router.get("", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识库列表"""
    service = KnowledgeService(db)
    return service.get_knowledge_bases(current_user.id, skip, limit)


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识库详情"""
    service = KnowledgeService(db)
    kb = service.get_knowledge_base(current_user.id, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return kb


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: int,
    kb_data: KnowledgeBaseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新知识库"""
    service = KnowledgeService(db)
    try:
        kb = service.update_knowledge_base(
            current_user.id,
            kb_id,
            kb_data.name,
            kb_data.description
        )
        return kb
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{kb_id}")
async def delete_knowledge_base(
    kb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除知识库"""
    service = KnowledgeService(db)
    try:
        service.delete_knowledge_base(current_user.id, kb_id)
        return {"message": "知识库已删除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{kb_id}/documents", response_model=DocumentResponse)
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文档"""
    service = KnowledgeService(db)
    
    # 检查文件格式
    allowed_extensions = {".txt", ".md", ".pdf", ".doc", ".docx", ".ppt", ".pptx"}
    file_ext = "." + file.filename.split(".")[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。支持的格式: {', '.join(allowed_extensions)}"
        )
    
    try:
        file_content = await file.read()
        doc = await service.upload_document(
            current_user.id,
            kb_id,
            file_content,
            file.filename
        )
        return doc
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/{kb_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    kb_id: int,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识库中的文档"""
    service = KnowledgeService(db)
    try:
        return service.get_documents(current_user.id, kb_id, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{kb_id}/documents/{doc_id}")
async def delete_document(
    kb_id: int,
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除文档"""
    service = KnowledgeService(db)
    try:
        service.delete_document(current_user.id, kb_id, doc_id)
        return {"message": "文档已删除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
