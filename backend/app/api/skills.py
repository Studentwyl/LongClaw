"""技能 API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.services.skill_service import SkillService
from app.schemas.skill import SkillCreate, SkillUpdate, SkillResponse
from typing import List

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.post("", response_model=SkillResponse)
async def create_skill(
    skill_data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建技能"""
    service = SkillService(db)
    skill = service.create_skill(
        current_user.id,
        skill_data.name,
        skill_data.description,
        skill_data.type,
        skill_data.config,
        [p.dict() for p in skill_data.parameters] if skill_data.parameters else None
    )
    return skill


@router.get("", response_model=List[SkillResponse])
async def list_skills(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取技能列表"""
    service = SkillService(db)
    return service.get_skills(current_user.id, skip, limit)


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取技能详情"""
    service = SkillService(db)
    skill = service.get_skill(current_user.id, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")
    return skill


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新技能"""
    service = SkillService(db)
    try:
        skill = service.update_skill(
            current_user.id,
            skill_id,
            skill_data.name,
            skill_data.description,
            skill_data.config
        )
        return skill
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{skill_id}")
async def delete_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除技能"""
    service = SkillService(db)
    try:
        service.delete_skill(current_user.id, skill_id)
        return {"message": "技能已删除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
