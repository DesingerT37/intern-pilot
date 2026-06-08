<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-header">
        <div class="logo">
          <span class="logo-icon">🚀</span>
          <span class="logo-text">InternPilot</span>
        </div>
        <p class="subtitle">AI 实习求职助手</p>
      </div>

      <n-card class="login-card" :bordered="false">
        <h2 style="text-align: center; margin-bottom: 32px; font-size: 24px">欢迎回来</h2>
        
        <n-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          size="large"
        >
          <n-form-item path="username">
            <n-input
              v-model:value="formData.username"
              placeholder="用户名"
              @keydown.enter="handleLogin"
            >
              <template #prefix>
                <span style="font-size: 18px">👤</span>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="password">
            <n-input
              v-model:value="formData.password"
              type="password"
              show-password-on="click"
              placeholder="密码"
              @keydown.enter="handleLogin"
            >
              <template #prefix>
                <span style="font-size: 18px">🔒</span>
              </template>
            </n-input>
          </n-form-item>

          <n-button
            type="primary"
            block
            size="large"
            :loading="authStore.loading"
            @click="handleLogin"
            style="margin-top: 8px"
          >
            登录
          </n-button>
        </n-form>

        <div class="footer-text">
          还没有账号？
          <n-button text type="primary" @click="goToRegister" style="font-size: 14px">
            立即注册
          </n-button>
        </div>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { 
  useMessage, 
  NCard, 
  NForm, 
  NFormItem, 
  NInput, 
  NButton, 
  NSpace, 
  NText,
  type FormInst, 
  type FormRules 
} from 'naive-ui'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const formRef = ref<FormInst | null>(null)
const formData = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ]
}

async function handleLogin() {
  try {
    // 验证表单
    await formRef.value?.validate()
    
    console.log('开始登录...', formData)
    
    // 调用登录
    await authStore.login(formData)
    
    console.log('登录成功，准备跳转')
    
    message.success('登录成功！', { duration: 2000 })
    
    // 延迟跳转
    setTimeout(() => {
      router.push('/')
    }, 500)
    
  } catch (err: any) {
    console.error('登录失败:', err)
    
    // 显示错误信息
    const errorMsg = authStore.error || err.response?.data?.detail || err.message || '登录失败'
    message.error(errorMsg)
  }
}

function goToRegister() {
  router.push('/register')
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-wrapper {
  width: 100%;
  max-width: 420px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.logo-icon {
  font-size: 48px;
  animation: float 3s ease-in-out infinite;
}

.logo-text {
  font-size: 36px;
  font-weight: bold;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

.login-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 40px 32px;
}

.footer-text {
  text-align: center;
  margin-top: 24px;
  color: #666;
  font-size: 14px;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
</style>
