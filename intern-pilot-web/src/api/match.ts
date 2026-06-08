/**
 * 匹配分析相关 API
 */
import apiClient from './client'

export interface MatchRequest {
  resume_id: string
  jd_id: string
}

export interface MatchResponse {
  match_id: string
  analysis: {
    overall_score: number  // 改为 overall_score 与后端一致
    skill_match_score?: number
    experience_match_score?: number
    education_match_score?: number
    matched_skills: string[]
    missing_skills: string[]
    strengths: string[]
    weaknesses: string[]
    suggestions: string[]
  }
  enhancements: Array<{
    priority: number
    category: string
    title: string
    description: string
    example?: string
  }>
  report_markdown: string
  message: string
}

/**
 * 匹配分析
 */
export const analyzeMatch = async (resumeId: string, jdId: string): Promise<MatchResponse> => {
  const response = await apiClient.post('/match/analyze', {
    resume_id: resumeId,
    jd_id: jdId
  })
  return response.data
}

/**
 * 简历增强
 */
export const enhanceResume = async (resumeId: string, jdId: string): Promise<MatchResponse> => {
  const response = await apiClient.post('/match/enhance', {
    resume_id: resumeId,
    jd_id: jdId
  })
  return response.data
}
