"""知识库服务"""
from sqlalchemy.orm import Session
from app.models.knowledge_base import KnowledgeBase, Document, DocumentChunk
from app.models.user import User
from app.core.vector_store import get_vector_store
from app.core.file_storage import get_file_storage
from app.core.document_parser import DocumentParser
from typing import List, Optional
import hashlib
import uuid
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.ollama import OllamaEmbeddings
from app.core.config import settings


class KnowledgeService:
    """知识库业务逻辑"""
    
    def __init__(self, db: Session):
        self.db = db
        self.vector_store = get_vector_store()
        self.file_storage = get_file_storage()
    
    def create_knowledge_base(self, user_id: int, name: str, description: str = None) -> KnowledgeBase:
        """创建知识库"""
        # 创建 Qdrant collection 名称
        collection_name = f"kb_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # 在 Qdrant 中创建 collection
        self.vector_store.create_collection(collection_name)
        
        # 保存到数据库
        kb = KnowledgeBase(
            user_id=user_id,
            name=name,
            description=description,
            vector_collection_name=collection_name
        )
        self.db.add(kb)
        self.db.commit()
        self.db.refresh(kb)
        return kb
    
    def get_knowledge_bases(self, user_id: int, skip: int = 0, limit: int = 10) -> List[KnowledgeBase]:
        """获取用户的知识库列表"""
        return self.db.query(KnowledgeBase).filter(
            KnowledgeBase.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_knowledge_base(self, user_id: int, kb_id: int) -> Optional[KnowledgeBase]:
        """获取知识库详情"""
        return self.db.query(KnowledgeBase).filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == user_id
        ).first()
    
    def update_knowledge_base(self, user_id: int, kb_id: int, name: str = None, description: str = None) -> KnowledgeBase:
        """更新知识库"""
        kb = self.get_knowledge_base(user_id, kb_id)
        if not kb:
            raise ValueError("知识库不存在")
        
        if name:
            kb.name = name
        if description is not None:
            kb.description = description
        
        self.db.commit()
        self.db.refresh(kb)
        return kb
    
    def delete_knowledge_base(self, user_id: int, kb_id: int) -> bool:
        """删除知识库"""
        kb = self.get_knowledge_base(user_id, kb_id)
        if not kb:
            raise ValueError("知识库不存在")
        
        # 删除 Qdrant collection
        self.vector_store.delete_collection(kb.vector_collection_name)
        
        # 删除数据库记录
        self.db.delete(kb)
        self.db.commit()
        return True
    
    async def upload_document(
        self,
        user_id: int,
        kb_id: int,
        file_content: bytes,
        file_name: str
    ) -> Document:
        """上传并处理文档"""
        kb = self.get_knowledge_base(user_id, kb_id)
        if not kb:
            raise ValueError("知识库不存在")
        
        # 计算文件哈希，用于去重
        content_hash = hashlib.sha256(file_content).hexdigest()
        
        # 检查是否已存在相同内容的文档
        existing_doc = self.db.query(Document).filter(
            Document.knowledge_base_id == kb_id,
            Document.content_hash == content_hash
        ).first()
        
        if existing_doc:
            raise ValueError("该文档已存在")
        
        # 保存文件到 MinIO
        file_path = f"{user_id}/{kb_id}/{uuid.uuid4().hex}/{file_name}"
        self.file_storage.upload_file(file_path, file_content)
        
        # 保存文档记录到数据库
        document = Document(
            knowledge_base_id=kb_id,
            file_name=file_name,
            file_path=file_path,
            file_size=len(file_content),
            file_type=file_name.split('.')[-1],
            content_hash=content_hash
        )
        self.db.add(document)
        self.db.flush()  # 获取 document.id
        
        # 解析文档
        try:
            chunks = DocumentParser.parse(file_content, file_name)
        except Exception as e:
            self.db.rollback()
            self.file_storage.delete_file(file_path)
            raise ValueError(f"文档解析失败: {str(e)}")
        
        # 获取 embedding 模型
        embeddings = self._get_embeddings()
        
        # 生成向量并保存
        vectors = []
        payloads = []
        vector_ids = []
        
        for chunk_index, chunk_content in enumerate(chunks):
            # 生成向量
            try:
                vector = embeddings.embed_query(chunk_content)
            except Exception as e:
                print(f"向量生成失败: {str(e)}")
                continue
            
            vectors.append(vector)
            payloads.append({
                "document_id": document.id,
                "chunk_index": chunk_index,
                "content": chunk_content,
                "file_name": file_name
            })
            
            # 保存块记录到数据库
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=chunk_index,
                content=chunk_content
            )
            self.db.add(chunk)
        
        self.db.flush()
        
        # 获取块的 ID
        chunks_in_db = self.db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).all()
        vector_ids = [chunk.id for chunk in chunks_in_db]
        
        # 上传向量到 Qdrant
        if vectors:
            self.vector_store.add_vectors(
                collection_name=kb.vector_collection_name,
                vectors=vectors,
                payloads=payloads,
                ids=vector_ids
            )
            
            # 更新 chunk 的 vector_id
            for chunk, vector_id in zip(chunks_in_db, vector_ids):
                chunk.vector_id = vector_id
        
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def get_documents(self, user_id: int, kb_id: int, skip: int = 0, limit: int = 10) -> List[Document]:
        """获取知识库中的文档"""
        kb = self.get_knowledge_base(user_id, kb_id)
        if not kb:
            raise ValueError("知识库不存在")
        
        return self.db.query(Document).filter(
            Document.knowledge_base_id == kb_id
        ).offset(skip).limit(limit).all()
    
    def delete_document(self, user_id: int, kb_id: int, doc_id: int) -> bool:
        """删除文档"""
        kb = self.get_knowledge_base(user_id, kb_id)
        if not kb:
            raise ValueError("知识库不存在")
        
        doc = self.db.query(Document).filter(
            Document.id == doc_id,
            Document.knowledge_base_id == kb_id
        ).first()
        
        if not doc:
            raise ValueError("文档不存在")
        
        # 删除 MinIO 中的文件
        self.file_storage.delete_file(doc.file_path)
        
        # 删除数据库记录
        self.db.delete(doc)
        self.db.commit()
        return True
    
    def _get_embeddings(self):
        """获取 embedding 模型"""
        if settings.LLM_PROVIDER == "ollama":
            return OllamaEmbeddings(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL
            )
        # 可以添加其他 embedding 模型
        else:
            raise ValueError(f"不支持的 embedding 提供者")
