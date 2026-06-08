/**
 * 简历优化 Agent API
 */
import apiClient from './client'

const BASE = '/resume-optimization'

export interface ResumeListItem {
  resume_id: string
  filename: string
  name: string | null
  target_position: string | null
  parsed: boolean
  created_at: string
  updated_at: string
}

export interface ResumeContentResponse {
  resume_id: string
  markdown_text: string
  name: string | null
  email: string | null
  phone: string | null
  target_position: string | null
  updated_at: string
}

export interface ResumeChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  modified_section?: string | null
  section_type?: string | null
  explanation?: string | null
}

export interface ResumeChatRequest {
  resume_id: string
  resume_content: string
  message: string
  context: ResumeChatMessage[]
  suggestions?: string[]
}

export interface ResumeChatResponse {
  message: string
  modified_section?: string | null
  section_type?: string | null
  explanation?: string | null
}

export interface Suggestion {
  priority: number
  category: string
  title: string
  description: string
  example?: string | null
}

export interface MatchSuggestionResponse {
  match_id: string
  job_name: string
  company_name: string
  overall_score: number
  suggestions: Suggestion[]
  matched_skills: string[]
  missing_skills: string[]
  strengths: string[]
  weaknesses: string[]
}

export interface BatchSuggestionResponse {
  task_id: string
  keyword: string
  total_jobs: number
  common_missing_skills: string[]
  priority_suggestions: Suggestion[]
  top_skills: [string, number][]
}

export interface MatchAnalysisListItem {
  source?: string
  match_id: string
  resume_id: string
  overall_score: number
  job_label: string
  suggestion_count: number
  created_at: string
}

export interface BatchAnalysisListItem {
  source?: string
  task_id: string
  batch_id: string
  resume_id: string
  keyword: string
  total_jobs: number
  avg_match_score: number | null
  status: string
  suggestion_count: number
  created_at: string
}

export interface VersionResponse {
  version_id: string
  resume_id: string
  content: string
  description?: string | null
  created_at: string
}

export interface VersionListItem {
  version_id: string
  resume_id: string
  description?: string | null
  created_at: string
  content_preview: string
}

export async function getResumes(): Promise<ResumeListItem[]> {
  const { data } = await apiClient.get<ResumeListItem[]>(`${BASE}/resumes`)
  return data
}

export async function getResumeContent(resumeId: string): Promise<ResumeContentResponse> {
  const { data } = await apiClient.get<ResumeContentResponse>(`${BASE}/resumes/${resumeId}`)
  return data
}

export async function updateResumeContent(
  resumeId: string,
  markdownText: string
): Promise<{ message: string }> {
  const { data } = await apiClient.put(`${BASE}/resumes/${resumeId}`, {
    markdown_text: markdownText,
  })
  return data
}

export async function createResumeVersion(
  resumeId: string,
  description?: string
): Promise<VersionResponse> {
  const { data } = await apiClient.post<VersionResponse>(
    `${BASE}/resumes/${resumeId}/versions`,
    { description }
  )
  return data
}

export async function listResumeVersions(resumeId: string): Promise<VersionListItem[]> {
  const { data } = await apiClient.get<VersionListItem[]>(
    `${BASE}/resumes/${resumeId}/versions`
  )
  return data
}

export async function getResumeVersion(
  resumeId: string,
  versionId: string
): Promise<VersionResponse> {
  const { data } = await apiClient.get<VersionResponse>(
    `${BASE}/resumes/${resumeId}/versions/${versionId}`
  )
  return data
}

export async function chatWithAI(request: ResumeChatRequest): Promise<ResumeChatResponse> {
  const { data } = await apiClient.post<ResumeChatResponse>(`${BASE}/chat`, request)
  return data
}

export type StreamChatHandlers = {
  onContent?: (chunk: string) => void
  onMetadata?: (meta: {
    modified_section?: string | null
    section_type?: string | null
    explanation?: string | null
  }) => void
  onError?: (message: string) => void
  onDone?: () => void
}

export async function streamChatWithAI(
  request: ResumeChatRequest,
  handlers: StreamChatHandlers,
  signal?: AbortSignal
): Promise<void> {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`/api${BASE}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(request),
    signal,
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(err.detail || '流式对话请求失败')
  }

  const reader = response.body?.getReader()
  if (!reader) throw new Error('无法读取响应流')

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const raw = line.slice(6).trim()
      if (!raw) continue
      try {
        const payload = JSON.parse(raw)
        if (payload.type === 'content') {
          handlers.onContent?.(payload.data)
        } else if (payload.type === 'metadata') {
          handlers.onMetadata?.(payload.data)
        } else if (payload.type === 'error') {
          handlers.onError?.(payload.data)
        }
      } catch {
        // ignore malformed chunks
      }
    }
  }
  handlers.onDone?.()
}

export async function listResumeMatchAnalyses(
  resumeId: string
): Promise<MatchAnalysisListItem[]> {
  const { data } = await apiClient.get<MatchAnalysisListItem[]>(
    `${BASE}/resumes/${resumeId}/match-analyses`
  )
  return data
}

export async function listResumeBatchAnalyses(
  resumeId: string
): Promise<BatchAnalysisListItem[]> {
  const { data } = await apiClient.get<BatchAnalysisListItem[]>(
    `${BASE}/resumes/${resumeId}/batch-analyses`
  )
  return data
}

export async function getMatchSuggestions(matchId: string): Promise<MatchSuggestionResponse> {
  const { data } = await apiClient.get<MatchSuggestionResponse>(
    `${BASE}/suggestions/match/${matchId}`
  )
  return data
}

export async function getBatchSuggestions(taskId: string): Promise<BatchSuggestionResponse> {
  const { data } = await apiClient.get<BatchSuggestionResponse>(
    `${BASE}/suggestions/batch/${taskId}`
  )
  return data
}

export async function exportResume(
  payload: {
    resume_id: string
    markdown_content: string
    format: 'pdf' | 'docx'
    style?: string
  }
): Promise<Blob> {
  const endpoint = payload.format === 'pdf' ? 'pdf' : 'docx'
  const { data } = await apiClient.post(`${BASE}/export/${endpoint}`, payload, {
    responseType: 'blob',
  })
  return data
}
