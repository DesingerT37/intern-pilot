/**
 * BOSS 直聘登录 API 客户端
 */
import { apiClient } from './client'

/**
 * 登录状态响应
 */
export interface LoginStatusResponse {
  is_logged_in: boolean
  message: string
  checked_at: string
}

/**
 * 登录操作响应
 */
export interface LoginActionResponse {
  success: boolean
  message: string
}

/**
 * 检查 BOSS 直聘登录状态
 */
export async function checkLoginStatus(): Promise<LoginStatusResponse> {
  const response = await apiClient.get('/boss/login/status')
  return response.data
}

/**
 * 打开 BOSS 直聘登录页
 */
export async function openLoginPage(): Promise<LoginActionResponse> {
  const response = await apiClient.post('/boss/login/open')
  return response.data
}

/**
 * 清除登录会话
 */
export async function clearSession(): Promise<LoginActionResponse> {
  const response = await apiClient.post('/boss/login/clear')
  return response.data
}
