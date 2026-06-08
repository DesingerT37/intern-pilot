/**
 * API 客户端配置
 */
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: '/api',
  timeout: 180000,  // 增加到 3 分钟，因为 LLM 调用可能需要较长时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：自动附加 Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 直接返回 response，不要提前解包 data
    return response
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default apiClient
