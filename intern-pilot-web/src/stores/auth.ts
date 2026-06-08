/**
 * 用户认证 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'
import { apiClient } from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<authApi.UserResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const username = computed(() => user.value?.username || '')

  // Actions
  
  /**
   * 用户注册
   */
  async function register(data: authApi.RegisterRequest) {
    loading.value = true
    error.value = null
    
    try {
      const userData = await authApi.register(data)
      
      // 注册成功，返回用户数据
      // 不自动登录，让用户手动登录
      return userData
    } catch (err: any) {
      error.value = err.response?.data?.detail || '注册失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登录
   */
  async function login(data: authApi.LoginRequest) {
    loading.value = true
    error.value = null
    
    try {
      console.log('Auth Store: 开始登录请求', data.username)
      
      const response = await authApi.login(data)
      
      console.log('Auth Store: 登录响应', response)
      
      // 保存 token
      token.value = response.access_token
      localStorage.setItem('access_token', response.access_token)
      
      // 保存用户信息
      user.value = response.user
      
      // 设置 axios 默认 header
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${response.access_token}`
      
      console.log('Auth Store: 登录成功', user.value)
      
      return response
    } catch (err: any) {
      console.error('Auth Store: 登录失败', err)
      error.value = err.response?.data?.detail || '登录失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登出
   */
  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    delete apiClient.defaults.headers.common['Authorization']
  }

  /**
   * 获取当前用户信息
   */
  async function fetchCurrentUser() {
    if (!token.value) return
    
    loading.value = true
    error.value = null
    
    try {
      user.value = await authApi.getCurrentUser()
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取用户信息失败'
      // 如果 token 无效，清除登录状态
      if (err.response?.status === 401) {
        logout()
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 初始化认证状态
   */
  async function init() {
    if (token.value) {
      // 设置 axios 默认 header
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      
      // 尝试获取用户信息
      try {
        await fetchCurrentUser()
      } catch (err) {
        // 如果失败，清除登录状态
        logout()
      }
    }
  }

  return {
    // State
    token,
    user,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    username,
    
    // Actions
    register,
    login,
    logout,
    fetchCurrentUser,
    init
  }
})
