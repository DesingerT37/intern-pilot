/**
 * JD 状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useJDStore = defineStore('jd', () => {
  const jdId = ref<string | null>(null)
  const jdData = ref<any>(null)
  const jdText = ref<string>('')
  const keywords = ref<string[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const setJDId = (id: string) => {
    jdId.value = id
  }

  const setJDData = (data: any) => {
    jdData.value = data
  }

  const setJDText = (text: string) => {
    jdText.value = text
  }

  const setKeywords = (kws: string[]) => {
    keywords.value = kws
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const setError = (err: string | null) => {
    error.value = err
  }

  const clearJD = () => {
    jdId.value = null
    jdData.value = null
    jdText.value = ''
    keywords.value = []
    error.value = null
  }

  return {
    jdId,
    jdData,
    jdText,
    keywords,
    isLoading,
    error,
    setJDId,
    setJDData,
    setJDText,
    setKeywords,
    setLoading,
    setError,
    clearJD
  }
})
