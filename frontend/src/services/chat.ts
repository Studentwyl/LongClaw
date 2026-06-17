import { apiClient } from './api'

export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  knowledge_base_ids?: number[]
  skill_ids?: number[]
  retrieved_chunks?: any[]
  created_at: string
}

export interface Conversation {
  id: number
  user_id: number
  title: string
  description?: string
  created_at: string
  updated_at: string
}

class ChatService {
  async listConversations(skip = 0, limit = 10) {
    const response = await apiClient.get<Conversation[]>('/conversations', {
      params: { skip, limit },
    })
    return response.data
  }

  async getConversation(id: number) {
    const response = await apiClient.get<Conversation>(`/conversations/${id}`)
    return response.data
  }

  async createConversation(data: { title: string; description?: string }) {
    const response = await apiClient.post<Conversation>('/conversations', data)
    return response.data
  }

  async deleteConversation(id: number) {
    return await apiClient.delete(`/conversations/${id}`)
  }

  async getMessages(convId: number, skip = 0, limit = 50) {
    const response = await apiClient.get<Message[]>(`/conversations/${convId}/messages`, {
      params: { skip, limit },
    })
    return response.data
  }

  async sendMessage(
    convId: number,
    content: string,
    knowledgeBaseIds?: number[],
    skillIds?: number[]
  ) {
    const response = await apiClient.post<Message>(`/conversations/${convId}/messages`, {
      content,
      knowledge_base_ids: knowledgeBaseIds,
      skill_ids: skillIds,
    })
    return response.data
  }
}

export const chatService = new ChatService()
