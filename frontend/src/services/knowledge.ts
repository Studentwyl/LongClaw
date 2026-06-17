import { apiClient } from './api'

export interface KnowledgeBase {
  id: number
  user_id: number
  name: string
  description?: string
  vector_collection_name?: string
  created_at: string
  updated_at: string
}

export interface Document {
  id: number
  knowledge_base_id: number
  file_name: string
  file_size: number
  file_type: string
  created_at: string
  updated_at: string
}

class KnowledgeService {
  async list(skip = 0, limit = 10) {
    const response = await apiClient.get<KnowledgeBase[]>('/knowledge-bases', {
      params: { skip, limit },
    })
    return response.data
  }

  async get(id: number) {
    const response = await apiClient.get<KnowledgeBase>(`/knowledge-bases/${id}`)
    return response.data
  }

  async create(data: { name: string; description?: string }) {
    const response = await apiClient.post<KnowledgeBase>('/knowledge-bases', data)
    return response.data
  }

  async update(id: number, data: { name?: string; description?: string }) {
    const response = await apiClient.put<KnowledgeBase>(`/knowledge-bases/${id}`, data)
    return response.data
  }

  async delete(id: number) {
    return await apiClient.delete(`/knowledge-bases/${id}`)
  }

  async listDocuments(kbId: number, skip = 0, limit = 10) {
    const response = await apiClient.get<Document[]>(`/knowledge-bases/${kbId}/documents`, {
      params: { skip, limit },
    })
    return response.data
  }

  async uploadDocument(kbId: number, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.postForm<Document>(`/knowledge-bases/${kbId}/documents`, formData)
    return response.data
  }

  async deleteDocument(kbId: number, docId: number) {
    return await apiClient.delete(`/knowledge-bases/${kbId}/documents/${docId}`)
  }
}

export const knowledgeService = new KnowledgeService()
