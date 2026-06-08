/**
 * 用户认证 API
 */
import { apiClient } from './client'

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface UserResponse {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserResponse
}

export interface UserStats {
  total_resumes: number
  total_jds: number
  total_matches: number
  last_login_at: string | null
  last_activity_at: string | null
}

/**
 * 用户注册
 */
export async function register(data: RegisterRequest): Promise<UserResponse> {
  const response = await apiClient.post('/auth/register', data)
  return response.data
}

/**
 * 用户登录
 */
export async function login(data: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post('/auth/login', data)
  return response.data
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser(): Promise<UserResponse> {
  const response = await apiClient.get('/auth/me')
  return response.data
}

/**
 * 获取用户统计
 */
export async function getUserStats(): Promise<UserStats> {
  const response = await apiClient.get('/auth/stats')
  return response.data
}
