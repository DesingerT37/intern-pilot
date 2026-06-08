/**
 * 匹配分析状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMatchStore = defineStore('match', () => {
  const matchId = ref<string | null>(null)
  const analysis = ref<any>(null)
  const enhancements = ref<any[]>([])
  const report = ref<string>('')
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const setMatchId = (id: string) => {
    matchId.value = id
  }

  const setAnalysis = (data: any) => {
    analysis.value = data
  }

  const setEnhancements = (data: any[]) => {
    enhancements.value = data
  }

  const setReport = (markdown: string) => {
    report.value = markdown
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const setError = (err: string | null) => {
    error.value = err
  }

  const clearMatch = () => {
    matchId.value = null
    analysis.value = null
    enhancements.value = []
    report.value = ''
    error.value = null
  }

  return {
    matchId,
    analysis,
    enhancements,
    report,
    isLoading,
    error,
    setMatchId,
    setAnalysis,
    setEnhancements,
    setReport,
    setLoading,
    setError,
    clearMatch
  }
})
