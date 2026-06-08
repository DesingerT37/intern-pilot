/**
 * 统一 API 错误信息解析
 */
import type { AxiosError } from 'axios'

export function getApiErrorMessage(err: unknown, fallback = '操作失败'): string {
  if (!err) return fallback

  const axiosErr = err as AxiosError<{ detail?: string | { msg?: string }[] }>
  const status = axiosErr.response?.status
  const detail = axiosErr.response?.data?.detail

  if (typeof detail === 'string') {
    return mapStatusMessage(status, detail)
  }
  if (Array.isArray(detail)) {
    const msg = detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
    return mapStatusMessage(status, msg)
  }

  if (axiosErr.message) {
    return mapStatusMessage(status, axiosErr.message)
  }

  if (err instanceof Error) {
    return mapStatusMessage(status, err.message)
  }

  return fallback
}

function mapStatusMessage(status: number | undefined, detail: string): string {
  if (status === 401) return '登录已过期，请重新登录'
  if (status === 403) return detail || '无权访问该资源'
  if (status === 404) return detail || '请求的资源不存在'
  if (status === 429) return detail || '请求过于频繁，请稍后再试'
  if (status === 503) return detail || 'AI 服务暂时不可用，请稍后重试'
  if (status && status >= 500) return detail || '服务器错误，请稍后重试'
  return detail
}

export function isAuthError(err: unknown): boolean {
  const axiosErr = err as AxiosError
  return axiosErr.response?.status === 401
}

export function isAiUnavailable(err: unknown): boolean {
  const axiosErr = err as AxiosError
  const status = axiosErr.response?.status
  return status === 503 || (axiosErr.message || '').includes('AI service')
}
