import { apiClient } from './api'

export interface SkillParameter {
  param_name: string
  param_type: string
  required?: boolean
  description?: string
}

export interface Skill {
  id: number
  user_id: number
  name: string
  description?: string
  type: string
  config?: Record<string, any>
  created_at: string
  updated_at: string
}

class SkillService {
  async list(skip = 0, limit = 10) {
    const response = await apiClient.get<Skill[]>('/skills', {
      params: { skip, limit },
    })
    return response.data
  }

  async get(id: number) {
    const response = await apiClient.get<Skill>(`/skills/${id}`)
    return response.data
  }

  async create(data: {
    name: string
    description?: string
    type: string
    config?: Record<string, any>
    parameters?: SkillParameter[]
  }) {
    const response = await apiClient.post<Skill>('/skills', data)
    return response.data
  }

  async update(
    id: number,
    data: {
      name?: string
      description?: string
      config?: Record<string, any>
    }
  ) {
    const response = await apiClient.put<Skill>(`/skills/${id}`, data)
    return response.data
  }

  async delete(id: number) {
    return await apiClient.delete(`/skills/${id}`)
  }
}

export const skillService = new SkillService()
