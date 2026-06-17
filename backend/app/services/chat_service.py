"""对话服务"""
from sqlalchemy.orm import Session
from app.models.conversation import Conversation, Message
from app.models.knowledge_base import KnowledgeBase
from app.core.llm import get_llm_provider
from app.core.vector_store import get_vector_store
from app.core.config import settings
from typing import List, Optional, Dict, Any
from langchain.embeddings.ollama import OllamaEmbeddings
import json


class ChatService:
    """对话业务逻辑"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_provider = get_llm_provider()
        self.vector_store = get_vector_store()
    
    def create_conversation(self, user_id: int, title: str, description: str = None) -> Conversation:
        """创建对话"""
        conversation = Conversation(
            user_id=user_id,
            title=title,
            description=description
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def get_conversations(self, user_id: int, skip: int = 0, limit: int = 10) -> List[Conversation]:
        """获取用户的对话列表"""
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    
    def get_conversation(self, user_id: int, conv_id: int) -> Optional[Conversation]:
        """获取对话详情"""
        return self.db.query(Conversation).filter(
            Conversation.id == conv_id,
            Conversation.user_id == user_id
        ).first()
    
    def get_messages(self, user_id: int, conv_id: int, skip: int = 0, limit: int = 50) -> List[Message]:
        """获取对话消息历史"""
        conversation = self.get_conversation(user_id, conv_id)
        if not conversation:
            raise ValueError("对话不存在")
        
        return self.db.query(Message).filter(
            Message.conversation_id == conv_id
        ).order_by(Message.created_at).offset(skip).limit(limit).all()
    
    async def send_message(
        self,
        user_id: int,
        conv_id: int,
        content: str,
        knowledge_base_ids: Optional[List[int]] = None,
        skill_ids: Optional[List[int]] = None
    ) -> Message:
        """发送消息并获取 AI 回复"""
        conversation = self.get_conversation(user_id, conv_id)
        if not conversation:
            raise ValueError("对话不存在")
        
        # 保存用户消息
        user_message = Message(
            conversation_id=conv_id,
            role="user",
            content=content,
            knowledge_base_ids=knowledge_base_ids,
            skill_ids=skill_ids
        )
        self.db.add(user_message)
        self.db.flush()
        
        # 构建对话历史
        messages_history = self._build_chat_history(conv_id)
        
        # 检索相关知识库内容
        retrieved_chunks = []
        if knowledge_base_ids:
            retrieved_chunks = await self._search_knowledge_bases(
                user_id, knowledge_base_ids, content
            )
        
        # 构建提示词
        system_prompt = self._build_system_prompt(retrieved_chunks, skill_ids)
        
        # 调用 LLM
        try:
            messages_to_send = [
                {"role": "system", "content": system_prompt},
                *messages_history,
                {"role": "user", "content": content}
            ]
            
            ai_response = await self.llm_provider.chat(messages_to_send)
        except Exception as e:
            raise ValueError(f"LLM 调用失败: {str(e)}")
        
        # 保存 AI 回复
        ai_message = Message(
            conversation_id=conv_id,
            role="assistant",
            content=ai_response,
            knowledge_base_ids=knowledge_base_ids,
            skill_ids=skill_ids,
            retrieved_chunks=retrieved_chunks
        )
        self.db.add(ai_message)
        self.db.commit()
        self.db.refresh(ai_message)
        
        return ai_message
    
    async def _search_knowledge_bases(
        self,
        user_id: int,
        kb_ids: List[int],
        query: str
    ) -> List[Dict[str, Any]]:
        """在知识库中搜索相关内容"""
        embeddings = OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL
        )
        
        # 生成查询向量
        try:
            query_vector = embeddings.embed_query(query)
        except Exception as e:
            print(f"生成查询向量失败: {str(e)}")
            return []
        
        retrieved_chunks = []
        
        for kb_id in kb_ids:
            # 获取知识库的 collection 名称
            kb = self.db.query(KnowledgeBase).filter(
                KnowledgeBase.id == kb_id,
                KnowledgeBase.user_id == user_id
            ).first()
            
            if not kb:
                continue
            
            # 在 Qdrant 中搜索
            try:
                results = self.vector_store.search(
                    collection_name=kb.vector_collection_name,
                    query_vector=query_vector,
                    limit=3,
                    threshold=0.5
                )
                
                for result in results:
                    retrieved_chunks.append({
                        "kb_id": kb_id,
                        "kb_name": kb.name,
                        "content": result["payload"].get("content", ""),
                        "file_name": result["payload"].get("file_name", ""),
                        "score": result["score"]
                    })
            except Exception as e:
                print(f"向量搜索失败: {str(e)}")
                continue
        
        return retrieved_chunks
    
    def _build_chat_history(self, conv_id: int, limit: int = 10) -> List[Dict[str, str]]:
        """构建对话历史"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conv_id
        ).order_by(Message.created_at).limit(limit).all()
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    def _build_system_prompt(self, retrieved_chunks: List[Dict[str, Any]], skill_ids: Optional[List[int]] = None) -> str:
        """构建系统提示词"""
        prompt = """你是一个有帮助的 AI 助手。你可以基于提供的知识库内容回答问题。

相关知识库内容：
"""
        
        if retrieved_chunks:
            for chunk in retrieved_chunks:
                prompt += f"\n【{chunk['kb_name']} - {chunk['file_name']}】\n{chunk['content']}\n"
        else:
            prompt += "\n(没有相关的知识库内容)\n"
        
        if skill_ids:
            prompt += f"\n可用的技能: {skill_ids}\n"
        
        prompt += "\n请根据上述信息回答用户的问题。如果知识库中没有相关内容，请明确说明。"
        
        return prompt
    
    def delete_conversation(self, user_id: int, conv_id: int) -> bool:
        """删除对话"""
        conversation = self.get_conversation(user_id, conv_id)
        if not conversation:
            raise ValueError("对话不存在")
        
        self.db.delete(conversation)
        self.db.commit()
        return True
