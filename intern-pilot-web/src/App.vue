<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NConfigProvider, NMessageProvider, darkTheme, NLayout, NLayoutHeader, NLayoutContent, NLayoutFooter, NMenu, NButton, NDropdown, NAvatar } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isDark = ref(false)

const menuOptions: MenuOption[] = [
  {
    label: '首页',
    key: 'home',
    path: '/'
  },
  {
    label: '简历上传',
    key: 'resume',
    path: '/resume'
  },
  {
    label: '岗位需求',
    key: 'jd',
    path: '/jd'
  },
  {
    label: '匹配分析',
    key: 'analysis',
    path: '/analysis'
  },
  {
    label: '简历优化 ✨',
    key: 'resume-optimization',
    path: '/resume-optimization'
  },
  {
    label: '批量分析 ⭐',
    key: 'batch-analysis',
    path: '/batch-analysis'
  },
  {
    label: '历史记录',
    key: 'history',
    path: '/history'
  }
]

const userDropdownOptions = [
  {
    label: '退出登录',
    key: 'logout'
  }
]

const handleMenuSelect = (key: string, item: MenuOption) => {
  if (item.path) {
    router.push(item.path as string)
  }
}

const handleUserDropdown = (key: string) => {
  if (key === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}

// 初始化认证状态
onMounted(async () => {
  await authStore.init()
})
</script>

<template>
  <n-config-provider :theme="isDark ? darkTheme : null">
    <n-message-provider>
      <n-layout style="min-height: 100vh">
        <n-layout-header bordered style="height: 64px; padding: 0 24px; display: flex; align-items: center; justify-content: space-between">
          <div style="display: flex; align-items: center; gap: 48px">
            <div style="display: flex; align-items: center; gap: 12px">
              <span style="font-size: 28px">🚀</span>
              <span style="font-size: 20px; font-weight: bold">InternPilot</span>
            </div>
            <n-menu
              mode="horizontal"
              :value="route.name as string"
              :options="menuOptions"
              @update:value="handleMenuSelect"
            />
          </div>
          
          <!-- 用户信息 / 登录注册按钮 -->
          <div v-if="authStore.isAuthenticated" style="display: flex; align-items: center; gap: 12px">
            <n-dropdown :options="userDropdownOptions" @select="handleUserDropdown">
              <div style="display: flex; align-items: center; gap: 8px; cursor: pointer">
                <n-avatar round size="small">
                  {{ authStore.username.charAt(0).toUpperCase() }}
                </n-avatar>
                <span>{{ authStore.username }}</span>
              </div>
            </n-dropdown>
          </div>
          <div v-else style="display: flex; gap: 12px">
            <n-button @click="goToLogin">登录</n-button>
            <n-button type="primary" @click="goToRegister">注册</n-button>
          </div>
        </n-layout-header>
        
        <n-layout-content style="padding: 24px; min-height: calc(100vh - 64px - 64px)">
          <router-view />
        </n-layout-content>
        
        <n-layout-footer bordered style="padding: 24px; text-align: center">
          <p style="color: #999">© 2026 InternPilot - AI求职领航员 | 助力每一位同学拿到理想 Offer</p>
        </n-layout-footer>
      </n-layout>
    </n-message-provider>
  </n-config-provider>
</template>

<style scoped>
</style>
