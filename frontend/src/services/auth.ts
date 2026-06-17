import { apiClient } from './api'

export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

class AuthService {
  async register(username: string, email: string, password: string) {
    const response = await apiClient.post<User>('/auth/register', {
      username,
      email,
      password,
    })
    return response.data
  }

  async login(username: string, password: string) {
    const response = await apiClient.post<AuthResponse>('/auth/login', {
      username,
      password,
    })
    const { access_token, user } = response.data
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(user))
    return response.data
  }

  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  getToken() {
    return localStorage.getItem('token')
  }

  getUser() {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  }
}

export const authService = new AuthService()
