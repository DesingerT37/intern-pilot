<template>
  <div class="register-container">
    <div class="register-wrapper">
      <div class="register-header">
        <div class="logo">
          <span class="logo-icon">🚀</span>
          <span class="logo-text">InternPilot</span>
        </div>
        <p class="subtitle">AI 实习求职助手</p>
      </div>

      <n-card class="register-card" :bordered="false">
        <h2 style="text-align: center; margin-bottom: 32px; font-size: 24px">创建账号</h2>
        
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
            >
              <template #prefix>
                <span style="font-size: 18px">👤</span>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="email">
            <n-input
              v-model:value="formData.email"
              placeholder="邮箱地址"
            >
              <template #prefix>
                <span style="font-size: 18px">📧</span>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="password">
            <n-input
              v-model:value="formData.password"
              type="password"
              show-password-on="click"
              placeholder="密码（至少 6 位）"
            >
              <template #prefix>
                <span style="font-size: 18px">🔒</span>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="confirmPassword">
            <n-input
              v-model:value="formData.confirmPassword"
              type="password"
              show-password-on="click"
              placeholder="确认密码"
              @keydown.enter="handleRegister"
            >
              <template #prefix>
                <span style="font-size: 18px">🔑</span>
              </template>
            </n-input>
          </n-form-item>

          <n-button
            type="primary"
            block
            size="large"
            :loading="authStore.loading"
            @click="handleRegister"
            style="margin-top: 8px"
          >
            注册
          </n-button>
        </n-form>

        <div class="footer-text">
          已有账号？
          <n-button text type="primary" @click="goToLogin" style="font-size: 14px">
            立即登录
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
  type FormRules, 
  type FormItemRule 
} from 'naive-ui'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const formRef = ref<FormInst | null>(null)
const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validatePasswordSame = (rule: FormItemRule, value: string): boolean => {
  return value === formData.password
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度 3-20 位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePasswordSame, message: '两次密码输入不一致', trigger: 'blur' }
  ]
}

async function handleRegister() {
  try {
    await formRef.value?.validate()
    
    await authStore.register({
      username: formData.username,
      email: formData.email,
      password: formData.password
    })
    
    message.success('注册成功！请登录', { duration: 3000 })
    
    // 延迟跳转，让用户看到成功提示
    setTimeout(() => {
      router.push('/login')
    }, 1500)
    
  } catch (err: any) {
    if (err.response) {
      message.error(authStore.error || '注册失败')
    }
  }
}

function goToLogin() {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-wrapper {
  width: 100%;
  max-width: 420px;
}

.register-header {
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

.register-card {
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
