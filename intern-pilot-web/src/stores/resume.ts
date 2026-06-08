/**
 * 简历状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useResumeStore = defineStore('resume', () => {
  const resumeId = ref<string | null>(null)
  const resumeData = ref<any>(null)
  const resumeFile = ref<File | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const setResumeId = (id: string) => {
    resumeId.value = id
  }

  const setResumeData = (data: any) => {
    resumeData.value = data
  }

  const setResumeFile = (file: File) => {
    resumeFile.value = file
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const setError = (err: string | null) => {
    error.value = err
  }

  const clearResume = () => {
    resumeId.value = null
    resumeData.value = null
    resumeFile.value = null
    error.value = null
  }

  return {
    resumeId,
    resumeData,
    resumeFile,
    isLoading,
    error,
    setResumeId,
    setResumeData,
    setResumeFile,
    setLoading,
    setError,
    clearResume
  }
})
