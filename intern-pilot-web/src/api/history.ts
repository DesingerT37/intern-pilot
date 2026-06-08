/**
 * 历史记录 API 客户端
 */
import { apiClient } from './client'

/**
 * 简历历史记录
 */
export interface ResumeHistory {
  resume_id: string
  filename: string
  name?: string
  email?: string
  target_position?: string
  parsed: boolean
  created_at: string
}

/**
 * 简历详情
 */
export interface ResumeDetail {
  resume_id: string
  filename: string
  name?: string
  email?: string
  phone?: string
  target_position?: string
  markdown_text?: string
  education: Array<{
    school?: string
    major?: string
    degree?: string
    start_date?: string
    end_date?: string
    description?: string
  }>
  skills: string[]
  projects: Array<{
    name?: string
    role?: string
    start_date?: string
    end_date?: string
    description?: string
    technologies?: string[]
  }>
  work_experience: Array<{
    company?: string
    position?: string
    start_date?: string
    end_date?: string
    description?: string
    responsibilities?: string[]
  }>
  certifications: string[]
  awards: string[]
  created_at: string
}

/**
 * JD 历史记录
 */
export interface JDHistory {
  jd_id: string
  keywords?: string[]  // 关键词列表，用于标识 JD
  parsed: boolean
  created_at: string
}

// 为了向后兼容，添加别名
export type JDHistoryItem = JDHistory
export type ResumeHistoryItem = ResumeHistory

/**
 * JD 详情
 */
export interface JDDetail {
  jd_id: string
  raw_text: string
  required_skills: string[]
  preferred_skills: string[]
  responsibilities: string[]
  requirements: string[]
  keywords: string[]
  created_at: string
}

/**
 * 匹配分析历史记录
 */
export interface MatchHistory {
  match_id: string
  resume_id: string
  jd_id: string
  overall_score: number  // 改为 overall_score 与后端一致
  resume_name?: string
  company?: string
  position?: string
  created_at: string
}

/**
 * 匹配分析详情
 */
export interface MatchDetail {
  match_id: string
  resume_id: string
  jd_id: string
  overall_score: number
  skill_match_score?: number
  experience_match_score?: number
  education_match_score?: number
  matched_skills: string[]
  missing_skills: string[]
  strengths: string[]
  weaknesses: string[]
  suggestions: string[]
  enhancements: Array<{
    priority: number
    category: string
    title: string
    description: string
    example?: string
  }>
  report_markdown: string
  created_at: string
  resume_name?: string
  jd_keywords?: string[]
}

/**
 * 获取简历历史记录
 */
export async function getResumeHistory(): Promise<ResumeHistory[]> {
  const response = await apiClient.get('/history/resumes')
  return response.data
}

/**
 * 获取简历详情
 */
export async function getResumeDetail(resumeId: string): Promise<ResumeDetail> {
  const response = await apiClient.get(`/history/resumes/${resumeId}`)
  return response.data
}

/**
 * 获取 JD 历史记录
 */
export async function getJDHistory(): Promise<JDHistory[]> {
  const response = await apiClient.get('/history/jds')
  return response.data
}

/**
 * 获取 JD 详情
 */
export async function getJDDetail(jdId: string): Promise<JDDetail> {
  const response = await apiClient.get(`/history/jds/${jdId}`)
  return response.data
}

/**
 * 获取匹配分析历史记录
 */
export async function getMatchHistory(): Promise<MatchHistory[]> {
  const response = await apiClient.get('/history/matches')
  return response.data
}

/**
 * 获取匹配分析详情
 */
export async function getMatchDetail(matchId: string): Promise<MatchDetail> {
  const response = await apiClient.get(`/history/matches/${matchId}`)
  return response.data
}
