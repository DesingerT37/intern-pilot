/**
 * Vue Router 配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: { title: 'InternPilot - AI实习求职助手' }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { title: '登录 - InternPilot' }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { title: '注册 - InternPilot' }
    },
    {
      path: '/resume',
      name: 'resume',
      component: () => import('../views/ResumeView.vue'),
      meta: { title: '简历上传 - InternPilot' }
    },
    {
      path: '/jd',
      name: 'jd',
      component: () => import('../views/JDView.vue'),
      meta: { title: '岗位需求 - InternPilot' }
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: () => import('../views/AnalysisView.vue'),
      meta: { title: '匹配分析 - InternPilot' }
    },
    {
      path: '/batch-analysis',
      name: 'batch-analysis',
      component: () => import('../views/BatchAnalysisView.vue'),
      meta: { title: '批量分析 - InternPilot', requiresAuth: true }
    },
    {
      path: '/analysis-reports',
      name: 'analysis-reports',
      component: () => import('../views/AnalysisReportsView.vue'),
      meta: { title: '分析报告 - InternPilot', requiresAuth: true }
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('../views/HistoryView.vue'),
      meta: { title: '历史记录 - InternPilot', requiresAuth: true }
    },
    {
      path: '/resume-optimization',
      name: 'resume-optimization',
      component: () => import('../views/ResumeOptimizationView.vue'),
      meta: { title: '简历优化 - InternPilot', requiresAuth: true }
    }
  ]
})

// 路由守卫：更新页面标题 & 登录校验
router.beforeEach((to, from, next) => {
  document.title = (to.meta.title as string) || 'InternPilot'
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('access_token')
    if (!token) {
      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }
  }
  next()
})

export default router
