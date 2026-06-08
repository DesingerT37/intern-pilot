/**
 * 简历相关 API
 */
import apiClient from './client'

export interface ResumeUploadResponse {
  resume_id: string
  filename: string
  file_size: number
  message: string
}

export interface ResumeParseResponse {
  resume_id: string
  resume_data: any
  raw_text: string
  message: string
}

/**
 * 上传简历
 */
export const uploadResume = async (file: File): Promise<ResumeUploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await apiClient.post('/resume/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return response.data
}

/**
 * 解析简历
 */
export const parseResume = async (resumeId: string): Promise<ResumeParseResponse> => {
  const response = await apiClient.post(`/resume/parse/${resumeId}`)
  return response.data
}
