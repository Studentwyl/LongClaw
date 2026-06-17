import { create } from 'zustand'
import { KnowledgeBase, Document } from '../services/knowledge'
import { knowledgeService } from '../services/knowledge'

interface KnowledgeStore {
  knowledgeBases: KnowledgeBase[]
  selectedKnowledgeBase: KnowledgeBase | null
  documents: Document[]
  isLoading: boolean
  error: string | null
  fetchKnowledgeBases: () => Promise<void>
  selectKnowledgeBase: (kb: KnowledgeBase) => Promise<void>
  createKnowledgeBase: (name: string, description?: string) => Promise<void>
  updateKnowledgeBase: (id: number, name?: string, description?: string) => Promise<void>
  deleteKnowledgeBase: (id: number) => Promise<void>
  fetchDocuments: (kbId: number) => Promise<void>
  uploadDocument: (kbId: number, file: File) => Promise<void>
  deleteDocument: (kbId: number, docId: number) => Promise<void>
}

export const useKnowledgeStore = create<KnowledgeStore>((set) => ({
  knowledgeBases: [],
  selectedKnowledgeBase: null,
  documents: [],
  isLoading: false,
  error: null,

  async fetchKnowledgeBases() {
    set({ isLoading: true, error: null })
    try {
      const data = await knowledgeService.list()
      set({ knowledgeBases: data, isLoading: false })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '获取知识库失败',
        isLoading: false,
      })
    }
  },

  async selectKnowledgeBase(kb: KnowledgeBase) {
    set({ selectedKnowledgeBase: kb })
    await set()(({ fetchDocuments }) => fetchDocuments(kb.id))
  },

  async createKnowledgeBase(name: string, description?: string) {
    set({ isLoading: true, error: null })
    try {
      await knowledgeService.create({ name, description })
      await set()(({ fetchKnowledgeBases }) => fetchKnowledgeBases())
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '创建知识库失败',
        isLoading: false,
      })
    }
  },

  async updateKnowledgeBase(id: number, name?: string, description?: string) {
    set({ isLoading: true, error: null })
    try {
      await knowledgeService.update(id, { name, description })
      await set()(({ fetchKnowledgeBases }) => fetchKnowledgeBases())
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '更新知识库失败',
        isLoading: false,
      })
    }
  },

  async deleteKnowledgeBase(id: number) {
    set({ isLoading: true, error: null })
    try {
      await knowledgeService.delete(id)
      await set()(({ fetchKnowledgeBases }) => fetchKnowledgeBases())
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '删除知识库失败',
        isLoading: false,
      })
    }
  },

  async fetchDocuments(kbId: number) {
    set({ isLoading: true, error: null })
    try {
      const data = await knowledgeService.listDocuments(kbId)
      set({ documents: data, isLoading: false })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '获取文档失败',
        isLoading: false,
      })
    }
  },

  async uploadDocument(kbId: number, file: File) {
    set({ isLoading: true, error: null })
    try {
      await knowledgeService.uploadDocument(kbId, file)
      await set()(({ fetchDocuments }) => fetchDocuments(kbId))
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '上传文档失败',
        isLoading: false,
      })
    }
  },

  async deleteDocument(kbId: number, docId: number) {
    set({ isLoading: true, error: null })
    try {
      await knowledgeService.deleteDocument(kbId, docId)
      await set()(({ fetchDocuments }) => fetchDocuments(kbId))
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '删除文档失败',
        isLoading: false,
      })
    }
  },
}))
