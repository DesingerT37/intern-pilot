<template>
  <div class="batch-analysis-container">
    <n-card title="📊 批量职位分析" :bordered="false">
      <template #header-extra>
        <n-tag v-if="currentStep === 1" type="info">步骤 1/6</n-tag>
        <n-tag v-else-if="currentStep === 2" type="info">步骤 2/6</n-tag>
        <n-tag v-else-if="currentStep === 3" type="info">步骤 3/6</n-tag>
        <n-tag v-else-if="currentStep === 4" type="warning">步骤 4/6</n-tag>
        <n-tag v-else-if="currentStep === 5" type="warning">步骤 5/6</n-tag>
        <n-tag v-else type="success">已完成 ✓</n-tag>
      </template>

      <!-- 步骤 1: 选择简历 -->
      <div v-if="currentStep === 1" class="step-section">
        <n-space vertical :size="24">
          <n-card title="📄 选择简历" :bordered="false" embedded>
            <n-space vertical :size="12">
              <n-select
                v-model:value="formData.resume_id"
                :options="resumeOptions"
                placeholder="选择已上传的简历"
                :loading="loadingResumes"
                clearable
              />
              
              <n-alert
                v-if="!loadingResumes && resumeOptions.length === 0"
                type="warning"
                :bordered="false"
              >
                <template #icon>
                  <span style="font-size: 20px">📝</span>
                </template>
                <div style="display: flex; flex-direction: column; gap: 8px">
                  <n-text strong>还没有上传简历？</n-text>
                  <n-text depth="3">
                    批量分析需要先上传简历，以便 AI 根据市场需求为您生成针对性的优化建议
                  </n-text>
                  <n-button
                    type="primary"
                    size="small"
                    @click="$router.push('/resume')"
                    style="width: fit-content; margin-top: 4px"
                  >
                    立即上传简历 →
                  </n-button>
                </div>
              </n-alert>
              
              <n-text v-else depth="3" style="display: block">
                💡 提示：已找到 {{ resumeOptions.length }} 份简历，请选择要分析的简历
              </n-text>
            </n-space>
          </n-card>

          <n-space justify="end">
            <n-button @click="handleCancel">取消</n-button>
            <n-button
              type="primary"
              :disabled="!formData.resume_id"
              @click="goToStep(2)"
            >
              下一步 →
            </n-button>
          </n-space>
        </n-space>
      </div>

      <!-- 步骤 2: 检查登录状态 -->
      <div v-else-if="currentStep === 2" class="step-section">
        <n-space vertical :size="24">
          <n-card title="🔐 检查 BOSS 直聘登录状态" :bordered="false" embedded>
            <n-spin :show="checkingLogin">
              <n-space vertical :size="16">
                <!-- 检查中 -->
                <div v-if="checkingLogin" style="text-align: center; padding: 24px">
                  <n-text>正在检查登录状态...</n-text>
                </div>

                <!-- 已登录 -->
                <n-alert v-else-if="loginStatus.is_logged_in" type="success" :bordered="false">
                  <template #icon>
                    <span style="font-size: 24px">✅</span>
                  </template>
                  <n-space vertical :size="8">
                    <n-text strong>{{ loginStatus.message }}</n-text>
                    <n-text depth="3" style="font-size: 12px">
                      检查时间: {{ formatDate(loginStatus.checked_at) }}
                    </n-text>
                    <n-text depth="3">
                      可以开始爬取职位数据
                    </n-text>
                  </n-space>
                </n-alert>

                <!-- 未登录 -->
                <n-alert v-else type="warning" :bordered="false">
                  <template #icon>
                    <span style="font-size: 24px">⚠️</span>
                  </template>
                  <n-space vertical :size="12">
                    <n-text strong>{{ loginStatus.message }}</n-text>
                    <n-text depth="3">
                      需要先登录 BOSS 直聘才能爬取数据
                    </n-text>
                    <n-space>
                      <n-button
                        type="primary"
                        :loading="openingLogin"
                        @click="handleOpenLogin"
                      >
                        <template #icon>
                          <span>🔓</span>
                        </template>
                        打开登录页
                      </n-button>
                      <n-button @click="handleCheckLogin">
                        重新检查
                      </n-button>
                    </n-space>
                    <n-divider style="margin: 8px 0" />
                    <n-text depth="3" style="font-size: 12px">
                      💡 提示：点击"打开登录页"后，会在浏览器中打开 BOSS 直聘登录页面，
                      请在浏览器中完成扫码或验证码登录，登录成功后点击"重新检查"
                    </n-text>
                  </n-space>
                </n-alert>
              </n-space>
            </n-spin>
          </n-card>

          <n-space justify="space-between">
            <n-button @click="goToStep(1)">
              ← 上一步
            </n-button>
            <n-button
              type="primary"
              :disabled="!loginStatus.is_logged_in"
              @click="goToStep(3)"
            >
              下一步 →
            </n-button>
          </n-space>
        </n-space>
      </div>

      <!-- 步骤 3: 配置爬取参数 -->
      <div v-else-if="currentStep === 3" class="step-section">
        <n-space vertical :size="24">
          <n-card title="🔍 搜索设置" :bordered="false" embedded>
            <n-space vertical :size="16">
              <n-form-item label="目标职位关键词" required>
                <n-input
                  v-model:value="formData.keyword"
                  placeholder="例如：Python后端工程师"
                  :maxlength="50"
                  show-count
                />
                <template #feedback>
                  💡 示例：Python后端、前端工程师、Java开发
                </template>
              </n-form-item>

              <n-form-item label="工作城市">
                <n-select
                  v-model:value="formData.city"
                  :options="cityOptions"
                  placeholder="选择城市"
                />
              </n-form-item>

              <n-form-item label="抓取页数">
                <n-slider
                  v-model:value="formData.pages"
                  :min="1"
                  :max="10"
                  :step="1"
                  :marks="{ 1: '1', 5: '5', 10: '10' }"
                />
                <n-text depth="3" style="margin-top: 8px">
                  当前：{{ formData.pages }} 页（预计 {{ formData.pages * 10 }}-{{ formData.pages * 15 }} 个职位）
                </n-text>
              </n-form-item>

              <n-alert type="warning" :bordered="false">
                ⚠️ 提示：页数越多，分析越全面，但耗时也越长（约 {{ estimatedTime }} 分钟）
              </n-alert>
            </n-space>
          </n-card>

          <n-card title="⚙️ 高级选项" :bordered="false" embedded>
            <n-checkbox v-model:checked="formData.fetch_details">
              包含职位详情（推荐，但会增加时间）
            </n-checkbox>
          </n-card>

          <n-space justify="space-between">
            <n-button @click="goToStep(2)">
              ← 上一步
            </n-button>
            <n-button
              type="primary"
              :disabled="!canStart"
              :loading="starting"
              @click="handleStart"
            >
              开始分析 →
            </n-button>
          </n-space>
        </n-space>
      </div>

      <!-- 步骤 4-6: 保持原有的爬取进度、AI分析、结果展示 -->
      <!-- 这里省略,使用原有代码 -->
      <div v-else>
        <n-result status="info" title="功能开发中" description="爬取和分析功能正在完善中..." />
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  useMessage,
  NCard,
  NSpace,
  NText,
  NButton,
  NTag,
  NSelect,
  NAlert,
  NSpin,
  NFormItem,
  NInput,
  NSlider,
  NCheckbox,
  NDivider,
  NResult
} from 'naive-ui'
import { getResumeHistory } from '@/api/history'
import { checkLoginStatus, openLoginPage, type LoginStatusResponse } from '@/api/bossLogin'

const router = useRouter()
const message = useMessage()

// 当前步骤
const currentStep = ref(1)

// 表单数据
const formData = ref({
  resume_id: undefined as string | undefined,
  keyword: '',
  city: '全国',
  pages: 3,
  fetch_details: true
})

// 简历选项
const resumeOptions = ref<Array<{ label: string; value: string }>>([])
const loadingResumes = ref(false)

// 城市选项
const cityOptions = [
  { label: '全国', value: '全国' },
  { label: '北京', value: '北京' },
  { label: '上海', value: '上海' },
  { label: '深圳', value: '深圳' },
  { label: '杭州', value: '杭州' },
  { label: '广州', value: '广州' },
  { label: '成都', value: '成都' },
  { label: '南京', value: '南京' },
  { label: '武汉', value: '武汉' },
  { label: '西安', value: '西安' }
]

// 登录状态
const loginStatus = ref<LoginStatusResponse>({
  is_logged_in: false,
  message: '',
  checked_at: ''
})
const checkingLogin = ref(false)
const openingLogin = ref(false)

// 状态
const starting = ref(false)

// 计算属性
const canStart = computed(() => {
  return formData.value.resume_id && formData.value.keyword.trim().length > 0
})

const estimatedTime = computed(() => {
  return Math.ceil(formData.value.pages * 0.5)
})

// 方法
async function loadResumes() {
  loadingResumes.value = true
  try {
    const resumes = await getResumeHistory()
    resumeOptions.value = resumes.map(r => ({
      label: `${r.filename} (${r.name || '未命名'})`,
      value: r.resume_id
    }))
    
    if (resumeOptions.value.length === 0) {
      message.warning('暂无简历记录，请先在"简历分析"页面上传简历')
    }
  } catch (error: any) {
    console.error('加载简历列表失败:', error)
    message.error('加载简历列表失败，请稍后重试')
  } finally {
    loadingResumes.value = false
  }
}

async function handleCheckLogin() {
  checkingLogin.value = true
  try {
    loginStatus.value = await checkLoginStatus()
    
    if (loginStatus.value.is_logged_in) {
      message.success('登录状态正常')
    } else {
      message.warning('未检测到登录状态')
    }
  } catch (error: any) {
    console.error('检查登录状态失败:', error)
    message.error('检查登录状态失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    checkingLogin.value = false
  }
}

async function handleOpenLogin() {
  openingLogin.value = true
  try {
    const result = await openLoginPage()
    message.success(result.message)
    message.info('请在浏览器中完成登录，登录成功后点击"重新检查"', {
      duration: 5000
    })
  } catch (error: any) {
    console.error('打开登录页失败:', error)
    message.error('打开登录页失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    openingLogin.value = false
  }
}

function goToStep(step: number) {
  // 步骤 2 需要自动检查登录状态
  if (step === 2) {
    currentStep.value = step
    handleCheckLogin()
  } else {
    currentStep.value = step
  }
}

async function handleStart() {
  // TODO: 实现爬取逻辑
  message.info('爬取功能正在开发中...')
}

function handleCancel() {
  router.push('/')
}

function formatDate(dateString: string): string {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  loadResumes()
  
  // 从 URL 查询参数获取 resume_id
  const resumeIdFromQuery = router.currentRoute.value.query.resume_id as string
  if (resumeIdFromQuery) {
    formData.value.resume_id = resumeIdFromQuery
    message.success('已自动选择简历')
  }
})
</script>

<style scoped>
.batch-analysis-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.step-section {
  min-height: 400px;
}
</style>
