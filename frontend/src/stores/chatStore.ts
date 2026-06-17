import { create } from 'zustand'
import { Conversation, Message } from '../services/chat'
import { chatService } from '../services/chat'

interface ChatStore {
  conversations: Conversation[]
  selectedConversation: Conversation | null
  messages: Message[]
  isLoading: boolean
  isSending: boolean
  error: string | null
  fetchConversations: () => Promise<void>
  selectConversation: (conv: Conversation) => Promise<void>
  createConversation: (title: string, description?: string) => Promise<void>
  deleteConversation: (id: number) => Promise<void>
  fetchMessages: (convId: number) => Promise<void>
  sendMessage: (convId: number, content: string, kbIds?: number[], skillIds?: number[]) => Promise<void>
}

export const useChatStore = create<ChatStore>((set) => ({
  conversations: [],
  selectedConversation: null,
  messages: [],
  isLoading: false,
  isSending: false,
  error: null,

  async fetchConversations() {
    set({ isLoading: true, error: null })
    try {
      const data = await chatService.listConversations()
      set({ conversations: data, isLoading: false })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '获取对话失败',
        isLoading: false,
      })
    }
  },

  async selectConversation(conv: Conversation) {
    set({ selectedConversation: conv })
    try {
      const messages = await chatService.getMessages(conv.id)
      set({ messages })
    } catch (error: any) {
      set({ error: error.response?.data?.detail || '获取消息失败' })
    }
  },

  async createConversation(title: string, description?: string) {
    set({ isLoading: true, error: null })
    try {
      const conv = await chatService.createConversation({ title, description })
      set(({ conversations }) => ({
        conversations: [conv, ...conversations],
        isLoading: false,
      }))
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '创建对话失败',
        isLoading: false,
      })
    }
  },

  async deleteConversation(id: number) {
    set({ isLoading: true, error: null })
    try {
      await chatService.deleteConversation(id)
      set(({ conversations }) => ({
        conversations: conversations.filter((c) => c.id !== id),
        isLoading: false,
      }))
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '删除对话失败',
        isLoading: false,
      })
    }
  },

  async fetchMessages(convId: number) {
    set({ isLoading: true, error: null })
    try {
      const messages = await chatService.getMessages(convId)
      set({ messages, isLoading: false })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '获取消息失败',
        isLoading: false,
      })
    }
  },

  async sendMessage(convId: number, content: string, kbIds?: number[], skillIds?: number[]) {
    set({ isSending: true, error: null })
    try {
      const message = await chatService.sendMessage(convId, content, kbIds, skillIds)
      set(({ messages }) => ({
        messages: [...messages, message],
        isSending: false,
      }))
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '发送消息失败',
        isSending: false,
      })
    }
  },
}))
