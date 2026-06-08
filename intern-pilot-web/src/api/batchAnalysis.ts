/**
 * 批量分析 API 客户端
 */
import { apiClient } from './client'

/**
 * 爬取任务请求
 */
export interface CrawlTaskRequest {
  resume_id?: string
  keyword: string
  city?: string
  pages?: number
  fetch_details?: boolean
}

/**
 * 爬取任务响应
 */
export interface CrawlTaskResponse {
  task_id: string
  message: string
  status: string
}

/**
 * 爬取进度
 */
export interface CrawlProgress {
  task_id: string
  status: string  // pending/running/completed/failed/stopped
  current_page: number
  total_pages: number
  jobs_found: number
  unique_jobs: number
  message: string
  progress_percentage: number
}

/**
 * BOSS 职位信息
 */
export interface BossJobInfo {
  job_id?: string
  job_name: string
  company_name: string
  location?: string
  salary_range?: string
  education?: string
  experience?: string
  job_description?: string
  job_tags: string[]
}

/**
 * 聚合 JD 分析
 */
export interface AggregatedJDAnalysis {
  total_jobs: number
  top_skills: [string, number][]
  education_distribution: Record<string, number>
  experience_distribution: Record<string, number>
  salary_stats: {
    min: number
    max: number
    avg: number
    median: number
    count: number
  }
  common_requirements: string[]
  common_responsibilities: string[]
}

/**
 * 优化建议
 */
export interface EnhancementSuggestion {
  priority: number
  category: string
  title: string
  description: string
  example?: string
}

/**
 * 批量分析结果
 */
export interface BatchAnalysisResult {
  task_id: string
  aggregated_analysis: AggregatedJDAnalysis
  resume_match_score: number
  priority_suggestions: EnhancementSuggestion[]
  report_markdown: string
}

/**
 * 启动批量分析任务
 */
export async function startBatchAnalysis(request: CrawlTaskRequest): Promise<CrawlTaskResponse> {
  const response = await apiClient.post('/batch-analysis/start', request)
  return response.data
}

/**
 * 获取任务进度（单次查询）
 */
export async function getTaskProgress(taskId: string): Promise<CrawlProgress> {
  const response = await apiClient.get(`/batch-analysis/${taskId}/progress`)
  return response.data
}

/**
 * 获取任务爬取的职位列表
 */
export async function getTaskJobs(taskId: string): Promise<BossJobInfo[]> {
  const response = await apiClient.get(`/batch-analysis/${taskId}/jobs`)
  return response.data
}

/**
 * 停止任务
 */
export async function stopTask(taskId: string): Promise<{ message: string; task_id: string }> {
  const response = await apiClient.post(`/batch-analysis/${taskId}/stop`)
  return response.data
}

/**
 * 触发 AI 分析
 */
export async function analyzeBatch(taskId: string, resumeId: string): Promise<BatchAnalysisResult> {
  const response = await apiClient.post(`/batch-analysis/${taskId}/analyze`, null, {
    params: { resume_id: resumeId },
    timeout: 180000  // 3 分钟超时（AI 分析耗时较长）
  })
  return response.data
}

/**
 * 获取分析结果
 */
export async function getBatchResult(taskId: string): Promise<BatchAnalysisResult> {
  const response = await apiClient.get(`/batch-analysis/${taskId}/result`)
  return response.data
}

/**
 * SSE 流式接收进度
 */
export function streamBatchProgress(
  taskId: string,
  onProgress: (data: CrawlProgress) => void,
  onError?: (error: Error) => void,
  onComplete?: () => void
): EventSource {
  // 从 localStorage 获取 token
  const token = localStorage.getItem('token')
  
  // 构建 URL,将 token 作为查询参数
  const baseUrl = import.meta.env.VITE_API_BASE_URL || ''
  const url = `${baseUrl}/api/batch-analysis/${taskId}/stream${token ? `?token=${token}` : ''}`
  
  const eventSource = new EventSource(url)
  
  eventSource.onmessage = (event) => {
    try {
      const data: CrawlProgress = JSON.parse(event.data)
      onProgress(data)
      
      // 任务完成，关闭连接
      if (data.status === 'completed' || data.status === 'failed' || data.status === 'stopped') {
        eventSource.close()
        onComplete?.()
      }
    } catch (error) {
      console.error('解析 SSE 数据失败:', error)
      onError?.(error as Error)
    }
  }
  
  eventSource.onerror = (error) => {
    console.error('SSE 连接错误:', error)
    eventSource.close()
    onError?.(new Error('SSE 连接失败'))
  }
  
  return eventSource
}

/**
 * 历史任务信息
 */
export interface TaskHistoryItem {
  task_id: string
  keyword: string
  city?: string
  status: string
  progress: number
  total_jobs: number
  crawled_jobs: number
  created_at: string
  started_at?: string
  completed_at?: string
}

/**
 * 获取历史任务列表
 */
export async function getTaskHistory(
  status?: string,
  limit: number = 20
): Promise<TaskHistoryItem[]> {
  const params: Record<string, any> = { limit }
  if (status) {
    params.status = status
  }
  
  const response = await apiClient.get('/batch-analysis/history', { params })
  return response.data
}

/**
 * 分析报告信息
 */
export interface AnalysisReportItem {
  batch_id: string
  task_id: string
  keyword: string
  city?: string
  total_jobs: number
  analyzed_jobs: number
  match_score: number
  status: string
  created_at: string
  completed_at?: string
}

/**
 * 获取历史分析报告列表
 */
export async function getAnalysisReports(limit: number = 20): Promise<AnalysisReportItem[]> {
  const response = await apiClient.get('/batch-analysis/reports', {
    params: { limit }
  })
  return response.data
}
