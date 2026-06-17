import axios, { AxiosInstance } from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000')

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: API_TIMEOUT,
    })

    // 请求拦截器 - 添加认证令牌
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截器 - 处理错误
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // 清除令牌并重定向到登录页
          localStorage.removeItem('token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  public get<T>(url: string, config = {}) {
    return this.client.get<T>(url, config)
  }

  public post<T>(url: string, data?: unknown, config = {}) {
    return this.client.post<T>(url, data, config)
  }

  public put<T>(url: string, data?: unknown, config = {}) {
    return this.client.put<T>(url, data, config)
  }

  public delete<T>(url: string, config = {}) {
    return this.client.delete<T>(url, config)
  }

  public postForm<T>(url: string, data: FormData) {
    return this.client.post<T>(url, data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  }
}

export const apiClient = new APIClient()
