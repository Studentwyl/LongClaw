"""技能服务"""
from sqlalchemy.orm import Session
from app.models.skills import Skill, SkillParameter
from typing import List, Optional, Dict, Any


class SkillService:
    """技能业务逻辑"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_skill(
        self,
        user_id: int,
        name: str,
        description: str = None,
        skill_type: str = "custom",
        config: Dict[str, Any] = None,
        parameters: List[Dict[str, Any]] = None
    ) -> Skill:
        """创建技能"""
        skill = Skill(
            user_id=user_id,
            name=name,
            description=description,
            type=skill_type,
            config=config or {}
        )
        self.db.add(skill)
        self.db.flush()
        
        # 添加参数
        if parameters:
            for param in parameters:
                skill_param = SkillParameter(
                    skill_id=skill.id,
                    param_name=param.get("param_name"),
                    param_type=param.get("param_type", "string"),
                    required=param.get("required", False),
                    description=param.get("description")
                )
                self.db.add(skill_param)
        
        self.db.commit()
        self.db.refresh(skill)
        return skill
    
    def get_skills(self, user_id: int, skip: int = 0, limit: int = 10) -> List[Skill]:
        """获取用户的技能列表"""
        return self.db.query(Skill).filter(
            Skill.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_skill(self, user_id: int, skill_id: int) -> Optional[Skill]:
        """获取技能详情"""
        return self.db.query(Skill).filter(
            Skill.id == skill_id,
            Skill.user_id == user_id
        ).first()
    
    def update_skill(
        self,
        user_id: int,
        skill_id: int,
        name: str = None,
        description: str = None,
        config: Dict[str, Any] = None
    ) -> Skill:
        """更新技能"""
        skill = self.get_skill(user_id, skill_id)
        if not skill:
            raise ValueError("技能不存在")
        
        if name:
            skill.name = name
        if description is not None:
            skill.description = description
        if config is not None:
            skill.config = config
        
        self.db.commit()
        self.db.refresh(skill)
        return skill
    
    def delete_skill(self, user_id: int, skill_id: int) -> bool:
        """删除技能"""
        skill = self.get_skill(user_id, skill_id)
        if not skill:
            raise ValueError("技能不存在")
        
        self.db.delete(skill)
        self.db.commit()
        return True
