import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User } from '../services/auth'
import { authService } from '../services/auth'

interface AuthStore {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthStore>(
  persist(
    (set) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,

      async login(username: string, password: string) {
        set({ isLoading: true, error: null })
        try {
          const { access_token, user } = await authService.login(username, password)
          set({
            token: access_token,
            user,
            isLoading: false,
          })
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || '登录失败',
            isLoading: false,
          })
          throw error
        }
      },

      async register(username: string, email: string, password: string) {
        set({ isLoading: true, error: null })
        try {
          await authService.register(username, email, password)
          set({ isLoading: false })
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || '注册失败',
            isLoading: false,
          })
          throw error
        }
      },

      logout() {
        authService.logout()
        set({ user: null, token: null })
      },

      setUser(user: User) {
        set({ user })
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)
