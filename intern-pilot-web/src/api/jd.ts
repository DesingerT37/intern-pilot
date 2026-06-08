/**
 * JD 相关 API
 */
import apiClient from './client'

export interface JDParseRequest {
  jd_text: string
}

export interface JDParseResponse {
  jd_id: string
  jd_data: any
  keywords: string[]
  message: string
}

/**
 * 解析 JD
 */
export const parseJD = async (jdText: string): Promise<JDParseResponse> => {
  const response = await apiClient.post('/jd/parse', {
    jd_text: jdText
  })
  return response.data
}
