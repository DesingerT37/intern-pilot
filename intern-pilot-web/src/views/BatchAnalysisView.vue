<template>
  <div class="batch-analysis-container">
    <n-card title="📊 批量职位分析" :bordered="false">
      <template #header-extra>
        <n-tag v-if="currentStep === 1" type="info">步骤 1/6: 选择简历</n-tag>
        <n-tag v-else-if="currentStep === 2" type="info">步骤 2/6: 检查登录</n-tag>
        <n-tag v-else-if="currentStep === 3" type="info">步骤 3/6: 配置参数</n-tag>
        <n-tag v-else-if="currentStep === 4" type="warning">步骤 4/6: 爬取进度</n-tag>
        <n-tag v-else-if="currentStep === 5" type="warning">步骤 5/6: AI 分析</n-tag>
        <n-tag v-else type="success">步骤 6/6: 查看结果 ✓</n-tag>
      </template>

      <!-- 步骤 1: 选择简历 -->
      <div v-if="currentStep === 1" class="form-section">
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
              
              <!-- 无简历时的引导 -->
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
              
              <!-- 有简历时的提示 -->
              <n-text v-else depth="3" style="display: block">
                💡 提示：已找到 {{ resumeOptions.length }} 份简历，请选择要分析的简历
              </n-text>
            </n-space>
          </n-card>

          <!-- 历史任务选择 -->
          <n-card title="📋 或使用历史任务" :bordered="false" embedded>
            <n-space vertical :size="12">
              <n-text depth="3">
                如果您之前已经爬取过职位数据，可以直接选择历史任务进行 AI 分析，无需重新爬取
              </n-text>
              <n-space>
                <n-button
                  @click="showHistoryModal = true"
                  :disabled="!formData.resume_id"
                >
                  <template #icon>
                    <span>📋</span>
                  </template>
                  选择历史任务
                </n-button>
                <n-button
                  type="primary"
                  @click="$router.push('/analysis-reports')"
                >
                  <template #icon>
                    <span>📊</span>
                  </template>
                  查看历史报告
                </n-button>
              </n-space>
              <n-text v-if="!formData.resume_id" depth="3" type="warning" style="font-size: 12px">
                请先选择简历
              </n-text>
            </n-space>
          </n-card>

          <!-- 操作按钮 -->
          <n-space justify="end">
            <n-button @click="handleCancel">取消</n-button>
            <n-button
              type="primary"
              :disabled="!canProceedToConfig"
              @click="handleProceedToLogin"
            >
              下一步：检查登录 →
            </n-button>
          </n-space>
        </n-space>
      </div>

      <!-- 步骤 2: 检查 BOSS 登录 -->
      <div v-else-if="currentStep === 2" class="login-check-section">
        <n-space vertical :size="24">
          <n-card title="🔐 BOSS 直聘登录检查" :bordered="false" embedded>
            <n-space vertical :size="16">
              <n-alert
                v-if="checkingLogin"
                type="info"
                :bordered="false"
              >
                <template #icon>
                  <span style="font-size: 20px">⏳</span>
                </template>
                正在检查登录状态...
              </n-alert>

              <n-alert
                v-else-if="bossLoginStatus?.is_logged_in"
                type="success"
                :bordered="false"
              >
                <template #icon>
                  <span style="font-size: 20px">✅</span>
                </template>
                <div style="display: flex; flex-direction: column; gap: 8px">
                  <n-text strong>已登录 BOSS 直聘</n-text>
                  <n-text depth="3">{{ bossLoginStatus.message }}</n-text>
                  <n-text depth="3" style="font-size: 12px">
                    检查时间：{{ new Date(bossLoginStatus.checked_at).toLocaleString('zh-CN') }}
                  </n-text>
                </div>
              </n-alert>

              <n-alert
                v-else-if="bossLoginStatus && !bossLoginStatus.is_logged_in"
                type="warning"
                :bordered="false"
              >
                <template #icon>
                  <span style="font-size: 20px">⚠️</span>
                </template>
                <div style="display: flex; flex-direction: column; gap: 12px">
                  <n-text strong>未登录 BOSS 直聘</n-text>
                  <n-text depth="3">{{ bossLoginStatus.message }}</n-text>
                  <n-text depth="3">
                    爬取职位数据需要先登录 BOSS 直聘。点击下方按钮打开登录页面，在浏览器中完成登录后，点击"重新检查"按钮。
                  </n-text>
                  <n-space>
                    <n-button
                      type="primary"
                      :loading="openingLogin"
                      @click="handleOpenLogin"
                    >
                      打开登录页面
                    </n-button>
                    <n-button
                      :loading="checkingLogin"
                      @click="checkBossLogin"
                    >
                      重新检查
                    </n-button>
                  </n-space>
                </div>
              </n-alert>

              <n-text v-if="!checkingLogin && !bossLoginStatus" depth="3">
                点击"检查登录状态"按钮开始检查
              </n-text>
            </n-space>
          </n-card>

          <!-- 操作按钮 -->
          <n-space justify="space-between">
            <n-button @click="currentStep = 1">← 上一步</n-button>
            <n-space>
              <n-button
                v-if="!bossLoginStatus"
                type="primary"
                :loading="checkingLogin"
                @click="checkBossLogin"
              >
                检查登录状态
              </n-button>
              <n-button
                v-else
                type="primary"
                :disabled="!bossLoginStatus?.is_logged_in"
                @click="handleProceedToConfig"
              >
                下一步：配置参数 →
              </n-button>
            </n-space>
          </n-space>
        </n-space>
      </div>

      <!-- 步骤 3: 配置爬取参数 -->
      <div v-else-if="currentStep === 3" class="config-section">
        <n-space vertical :size="24">
          <!-- 搜索设置 -->
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

          <!-- 高级选项 -->
          <n-card title="⚙️ 高级选项" :bordered="false" embedded>
            <n-checkbox v-model:checked="formData.fetch_details">
              包含职位详情（推荐，但会增加时间）
            </n-checkbox>
          </n-card>

          <!-- 操作按钮 -->
          <n-space justify="space-between">
            <n-button @click="currentStep = 2">← 上一步</n-button>
            <n-button
              type="primary"
              :disabled="!canProceedToCrawl"
              :loading="starting"
              @click="handleStart"
            >
              开始爬取 →
            </n-button>
          </n-space>
        </n-space>
      </div>

      <!-- 步骤 4: 爬取进度 -->
      <div v-else-if="currentStep === 4" class="progress-section">
        <n-space vertical :size="24">
          <n-card title="🔄 正在爬取职位数据..." :bordered="false" embedded>
            <n-space vertical :size="16">
              <n-descriptions :column="2" bordered>
                <n-descriptions-item label="关键词">
                  {{ formData.keyword }}
                </n-descriptions-item>
                <n-descriptions-item label="城市">
                  {{ formData.city }}
                </n-descriptions-item>
                <n-descriptions-item label="目标页数">
                  {{ formData.pages }} 页
                </n-descriptions-item>
                <n-descriptions-item label="已找到">
                  {{ progress.unique_jobs }} 个职位
                </n-descriptions-item>
              </n-descriptions>

              <n-progress
                type="line"
                :percentage="progress.progress_percentage"
                :status="progressStatus"
                :indicator-placement="'inside'"
              />

              <n-text>{{ progress.message }}</n-text>

              <!-- 实时日志 -->
              <n-card title="📝 实时日志" size="small" embedded>
                <div class="log-container">
                  <div v-for="(log, index) in logs" :key="index" class="log-item">
                    <n-text depth="3">{{ log }}</n-text>
                  </div>
                </div>
              </n-card>
            </n-space>
          </n-card>

          <n-space justify="end">
            <n-button @click="handleStop" :loading="stopping">
              停止分析
            </n-button>
          </n-space>
        </n-space>
      </div>

      <!-- 步骤 5: AI 分析进度 -->
      <div v-else-if="currentStep === 5" class="analysis-section">
        <n-space vertical :size="24">
          <n-card title="🤖 AI 正在分析..." :bordered="false" embedded>
            <n-space vertical :size="16">
              <n-alert type="success" :bordered="false">
                ✅ 职位爬取完成：{{ progress.unique_jobs }} 个职位
              </n-alert>

              <n-progress
                type="line"
                :percentage="analysisProgress"
                status="info"
                :indicator-placement="'inside'"
              />

              <n-steps :current="analysisStep" :status="analysisStepStatus">
                <n-step title="解析职位描述" />
                <n-step title="提取技能要求" />
                <n-step title="统计分布" />
                <n-step title="生成建议" />
              </n-steps>

              <n-text depth="3">预计剩余时间：约 {{ estimatedAnalysisTime }} 秒</n-text>
            </n-space>
          </n-card>
        </n-space>
      </div>

      <!-- 步骤 6: 分析结果 -->
      <div v-else-if="currentStep === 6 && analysisResult" class="result-section">
        <n-space vertical :size="24">
          <!-- 分析概览 -->
          <n-card title="📈 分析概览" :bordered="false" embedded>
            <n-descriptions :column="2" bordered>
              <n-descriptions-item label="关键词">
                {{ formData.keyword }}
              </n-descriptions-item>
              <n-descriptions-item label="分析职位数">
                {{ analysisResult.aggregated_analysis.total_jobs }} 个
              </n-descriptions-item>
              <n-descriptions-item label="分析时间">
                {{ analysisTime }}
              </n-descriptions-item>
              <n-descriptions-item label="耗时">
                {{ duration }}
              </n-descriptions-item>
            </n-descriptions>
          </n-card>

          <!-- 简历匹配度 -->
          <n-card title="🎯 简历匹配度" :bordered="false" embedded>
            <div class="match-score-container">
              <n-progress
                type="circle"
                :percentage="analysisResult.resume_match_score"
                :stroke-width="12"
                :color="getMatchScoreColor(analysisResult.resume_match_score)"
              >
                <div class="score-text">
                  <div class="score-value">{{ analysisResult.resume_match_score.toFixed(1) }}</div>
                  <div class="score-label">匹配度</div>
                </div>
              </n-progress>
              <n-text style="margin-top: 16px">
                {{ getMatchScoreLabel(analysisResult.resume_match_score) }}
              </n-text>
            </div>
          </n-card>

          <!-- 高频技能 -->
          <n-card title="💡 高频技能要求 Top 10" :bordered="false" embedded>
            <n-space vertical :size="8">
              <div
                v-for="([skill, count], index) in analysisResult.aggregated_analysis.top_skills"
                :key="skill"
                class="skill-item"
              >
                <div class="skill-header">
                  <n-text>{{ index + 1 }}. {{ skill }}</n-text>
                  <n-text depth="3">{{ count }}/{{ analysisResult.aggregated_analysis.total_jobs }}</n-text>
                </div>
                <n-progress
                  type="line"
                  :percentage="(count / analysisResult.aggregated_analysis.total_jobs) * 100"
                  :show-indicator="false"
                  :height="8"
                />
              </div>
            </n-space>
          </n-card>

          <!-- 学历和经验分布 -->
          <n-grid :cols="2" :x-gap="16">
            <n-gi>
              <n-card title="📚 学历要求分布" :bordered="false" embedded>
                <div class="distribution-chart">
                  <div
                    v-for="(count, edu) in analysisResult.aggregated_analysis.education_distribution"
                    :key="edu"
                    class="distribution-item"
                  >
                    <n-text>{{ edu }}</n-text>
                    <n-text depth="3">
                      {{ ((count / analysisResult.aggregated_analysis.total_jobs) * 100).toFixed(1) }}%
                    </n-text>
                  </div>
                </div>
              </n-card>
            </n-gi>
            <n-gi>
              <n-card title="💼 经验要求分布" :bordered="false" embedded>
                <div class="distribution-chart">
                  <div
                    v-for="(count, exp) in analysisResult.aggregated_analysis.experience_distribution"
                    :key="exp"
                    class="distribution-item"
                  >
                    <n-text>{{ exp }}</n-text>
                    <n-text depth="3">
                      {{ ((count / analysisResult.aggregated_analysis.total_jobs) * 100).toFixed(1) }}%
                    </n-text>
                  </div>
                </div>
              </n-card>
            </n-gi>
          </n-grid>

          <!-- 薪资统计 -->
          <n-card title="💰 薪资范围统计" :bordered="false" embedded>
            <n-descriptions :column="2" bordered>
              <n-descriptions-item label="最低薪资">
                {{ analysisResult.aggregated_analysis.salary_stats.min }}K/月
              </n-descriptions-item>
              <n-descriptions-item label="最高薪资">
                {{ analysisResult.aggregated_analysis.salary_stats.max }}K/月
              </n-descriptions-item>
              <n-descriptions-item label="平均薪资">
                {{ analysisResult.aggregated_analysis.salary_stats.avg }}K/月
              </n-descriptions-item>
              <n-descriptions-item label="中位数薪资">
                {{ analysisResult.aggregated_analysis.salary_stats.median }}K/月
              </n-descriptions-item>
            </n-descriptions>
          </n-card>

          <!-- 优化建议 -->
          <n-card title="🚀 针对性优化建议" :bordered="false" embedded>
            <n-space vertical :size="16">
              <n-collapse>
                <n-collapse-item
                  v-for="(suggestion, index) in sortedSuggestions"
                  :key="index"
                  :title="`${getPriorityIcon(suggestion.priority)} ${suggestion.title}`"
                >
                  <template #header-extra>
                    <n-tag :type="getPriorityType(suggestion.priority)" size="small">
                      {{ getCategoryLabel(suggestion.category) }}
                    </n-tag>
                  </template>
                  <n-text>{{ suggestion.description }}</n-text>
                  <n-divider v-if="suggestion.example" />
                  <n-alert v-if="suggestion.example" type="info" :bordered="false">
                    <template #header>示例</template>
                    {{ suggestion.example }}
                  </n-alert>
                </n-collapse-item>
              </n-collapse>
            </n-space>
          </n-card>

          <!-- 完整报告 -->
          <n-card title="📝 完整分析报告" :bordered="false" embedded>
            <n-space>
              <n-button type="primary" @click="showReportModal = true">
                查看报告
              </n-button>
              <n-button @click="downloadReport">
                下载 Markdown
              </n-button>
            </n-space>
          </n-card>

          <!-- 操作按钮 -->
          <n-space justify="end">
            <n-button @click="handleReset">重新分析</n-button>
            <n-button type="primary" @click="$router.push('/')">
              返回首页
            </n-button>
          </n-space>
        </n-space>
      </div>
    </n-card>

    <!-- 报告查看模态框 -->
    <n-modal
      v-model:show="showReportModal"
      preset="card"
      title="📝 完整分析报告"
      style="width: 80%; max-width: 1200px"
      :bordered="false"
    >
      <div v-if="analysisResult" class="markdown-content" v-html="renderedMarkdown"></div>
    </n-modal>

    <!-- 历史任务选择模态框 -->
    <TaskHistoryModal
      v-model:show="showHistoryModal"
      @select="handleSelectHistoryTask"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
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
  NFormItem,
  NInput,
  NSlider,
  NCheckbox,
  NDescriptions,
  NDescriptionsItem,
  NProgress,
  NSteps,
  NStep,
  NGrid,
  NGi,
  NCollapse,
  NCollapseItem,
  NDivider,
  NModal,
  NThing,
  NEmpty
} from 'naive-ui'
import {
  startBatchAnalysis,
  streamBatchProgress,
  stopTask,
  analyzeBatch,
  getBatchResult,
  type CrawlTaskRequest,
  type CrawlProgress,
  type BatchAnalysisResult,
  type TaskHistoryItem
} from '@/api/batchAnalysis'
import { getResumeHistory } from '@/api/history'
import { checkLoginStatus, openLoginPage } from '@/api/bossLogin'
import { marked } from 'marked'
import TaskHistoryModal from '@/components/batch/TaskHistoryModal.vue'

const router = useRouter()
const message = useMessage()

// 表单数据
const formData = ref<CrawlTaskRequest>({
  resume_id: undefined,
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

// 当前步骤
const currentStep = ref(1) // 1: 选择简历, 2: 检查登录, 3: 配置参数, 4: 爬取进度, 5: AI分析, 6: 结果展示

// BOSS 登录状态
const bossLoginStatus = ref<{
  is_logged_in: boolean
  message: string
  checked_at: string
} | null>(null)
const checkingLogin = ref(false)
const openingLogin = ref(false)

// 任务 ID
const taskId = ref<string>()

// 进度数据
const progress = ref<CrawlProgress>({
  task_id: '',
  status: 'pending',
  current_page: 0,
  total_pages: 0,
  jobs_found: 0,
  unique_jobs: 0,
  message: '',
  progress_percentage: 0
})

// 日志
const logs = ref<string[]>([])

// SSE 连接
let eventSource: EventSource | null = null

// 状态
const starting = ref(false)
const stopping = ref(false)

// 分析进度
const analysisProgress = ref(0)
const analysisStep = ref(1)
const analysisStepStatus = ref<'process' | 'finish' | 'error' | 'wait'>('process')

// 分析结果
const analysisResult = ref<BatchAnalysisResult>()

// 时间记录
const startTime = ref<Date>()
const endTime = ref<Date>()

// 报告模态框
const showReportModal = ref(false)

// 历史任务模态框
const showHistoryModal = ref(false)

// 计算属性
const canStart = computed(() => {
  return formData.value.resume_id && formData.value.keyword.trim().length > 0
})

const canProceedToConfig = computed(() => {
  return formData.value.resume_id !== undefined
})

const canProceedToCrawl = computed(() => {
  return bossLoginStatus.value?.is_logged_in === true && formData.value.keyword.trim().length > 0
})

const estimatedTime = computed(() => {
  return Math.ceil(formData.value.pages * 0.5)
})

const estimatedAnalysisTime = computed(() => {
  return Math.max(60 - analysisProgress.value, 10)
})

const progressStatus = computed(() => {
  if (progress.value.status === 'completed') return 'success'
  if (progress.value.status === 'failed') return 'error'
  return 'info'
})

const analysisTime = computed(() => {
  if (!endTime.value) return '-'
  return endTime.value.toLocaleString('zh-CN')
})

const duration = computed(() => {
  if (!startTime.value || !endTime.value) return '-'
  const diff = endTime.value.getTime() - startTime.value.getTime()
  const minutes = Math.floor(diff / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  return `${minutes} 分 ${seconds} 秒`
})

const sortedSuggestions = computed(() => {
  if (!analysisResult.value) return []
  return [...analysisResult.value.priority_suggestions].sort((a, b) => b.priority - a.priority)
})

const renderedMarkdown = computed(() => {
  if (!analysisResult.value) return ''
  return marked(analysisResult.value.report_markdown)
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

async function checkBossLogin() {
  checkingLogin.value = true
  try {
    const status = await checkLoginStatus()
    bossLoginStatus.value = status
    
    if (status.is_logged_in) {
      message.success('BOSS 直聘已登录')
    } else {
      message.warning('BOSS 直聘未登录，请先登录')
    }
  } catch (error: any) {
    console.error('检查登录状态失败:', error)
    message.error('检查登录状态失败，请稍后重试')
  } finally {
    checkingLogin.value = false
  }
}

async function handleOpenLogin() {
  openingLogin.value = true
  try {
    const result = await openLoginPage()
    message.success(result.message || '登录页面已打开，请在浏览器中完成登录')
    
    // 等待 3 秒后自动重新检查登录状态
    setTimeout(async () => {
      await checkBossLogin()
    }, 3000)
  } catch (error: any) {
    console.error('打开登录页面失败:', error)
    message.error(error.response?.data?.detail || '打开登录页面失败')
  } finally {
    openingLogin.value = false
  }
}

function handleProceedToLogin() {
  if (!formData.value.resume_id) {
    message.warning('请先选择简历')
    return
  }
  currentStep.value = 2
  // 自动检查登录状态
  checkBossLogin()
}

function handleProceedToConfig() {
  if (!bossLoginStatus.value?.is_logged_in) {
    message.warning('请先登录 BOSS 直聘')
    return
  }
  currentStep.value = 3
}

async function handleStart() {
  // 验证表单
  if (!formData.value.resume_id) {
    message.warning('请先选择简历')
    return
  }
  
  if (!formData.value.keyword.trim()) {
    message.warning('请输入职位关键词')
    return
  }
  
  if (!bossLoginStatus.value?.is_logged_in) {
    message.warning('请先登录 BOSS 直聘')
    return
  }
  
  starting.value = true
  startTime.value = new Date()
  
  try {
    const response = await startBatchAnalysis(formData.value)
    taskId.value = response.task_id
    currentStep.value = 4 // 爬取进度
    
    // 开始 SSE 监听
    startSSE()
    
    message.success('任务已启动，正在爬取职位数据...')
  } catch (error: any) {
    console.error('启动任务失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '启动任务失败'
    message.error(errorMsg)
  } finally {
    starting.value = false
  }
}

function startSSE() {
  if (!taskId.value) return
  
  eventSource = streamBatchProgress(
    taskId.value,
    (data) => {
      progress.value = data
      
      // 添加日志
      const timestamp = new Date().toLocaleTimeString('zh-CN')
      logs.value.push(`[${timestamp}] ${data.message}`)
      
      // 限制日志数量
      if (logs.value.length > 20) {
        logs.value.shift()
      }
      
      // 爬取完成，开始 AI 分析
      if (data.status === 'completed') {
        currentStep.value = 5 // AI 分析
        startAnalysis()
      } else if (data.status === 'failed') {
        message.error('爬取失败：' + data.message)
        currentStep.value = 3 // 返回配置参数
      }
    },
    (error) => {
      console.error('SSE 连接失败:', error)
      message.error('实时进度连接失败，请刷新页面重试')
    }
  )
}

async function startAnalysis() {
  if (!taskId.value || !formData.value.resume_id) return
  
  // 模拟分析进度
  const interval = setInterval(() => {
    if (analysisProgress.value < 90) {
      analysisProgress.value += 10
      analysisStep.value = Math.min(Math.floor(analysisProgress.value / 25) + 1, 4)
    }
  }, 3000)
  
  try {
    const result = await analyzeBatch(taskId.value, formData.value.resume_id)
    analysisResult.value = result
    analysisProgress.value = 100
    analysisStep.value = 4
    analysisStepStatus.value = 'finish'
    currentStep.value = 6 // 结果展示
    endTime.value = new Date()
    
    clearInterval(interval)
    message.success('分析完成！')
  } catch (error: any) {
    clearInterval(interval)
    
    // 检查是否是超时错误
    const isTimeout = error.code === 'ECONNABORTED' || error.message?.includes('timeout')
    
    if (isTimeout) {
      // 超时后，尝试获取结果（后端可能已经完成分析）
      message.warning('请求超时，正在检查分析结果...')
      
      try {
        // 等待 2 秒，给后端一点时间完成
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        const result = await getBatchResult(taskId.value)
        
        // 如果成功获取到结果，说明分析已完成
        analysisResult.value = result
        analysisProgress.value = 100
        analysisStep.value = 4
        analysisStepStatus.value = 'finish'
        currentStep.value = 6 // 结果展示
        endTime.value = new Date()
        
        message.success('分析完成！')
      } catch (resultError: any) {
        // 获取结果也失败，说明分析确实没完成
        analysisStepStatus.value = 'error'
        message.error('分析超时，请稍后在历史记录中查看结果')
        console.error('获取结果失败:', resultError)
      }
    } else {
      // 其他错误
      analysisStepStatus.value = 'error'
      message.error(error.response?.data?.detail || '分析失败')
      console.error(error)
    }
  }
}

async function handleStop() {
  if (!taskId.value) return
  
  stopping.value = true
  try {
    await stopTask(taskId.value)
    message.success('任务已停止')
    handleReset()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '停止任务失败')
  } finally {
    stopping.value = false
  }
}

function handleCancel() {
  router.push('/')
}

function handleReset() {
  currentStep.value = 1
  taskId.value = undefined
  progress.value = {
    task_id: '',
    status: 'pending',
    current_page: 0,
    total_pages: 0,
    jobs_found: 0,
    unique_jobs: 0,
    message: '',
    progress_percentage: 0
  }
  logs.value = []
  analysisProgress.value = 0
  analysisStep.value = 1
  analysisStepStatus.value = 'process'
  analysisResult.value = undefined
  startTime.value = undefined
  endTime.value = undefined
  
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
}

// 处理历史任务选择
async function handleSelectHistoryTask(task: TaskHistoryItem) {
  if (!formData.value.resume_id) {
    message.error('请先选择简历')
    return
  }
  
  // 设置任务 ID
  taskId.value = task.task_id
  
  // 跳过爬取步骤，直接进入 AI 分析
  currentStep.value = 5
  startTime.value = new Date()
  
  message.info(`已选择历史任务：${task.keyword}（${task.crawled_jobs} 个职位）`)
  
  // 开始 AI 分析
  await startAnalysis()
}

function getMatchScoreColor(score: number): string {
  if (score >= 80) return '#18a058'
  if (score >= 60) return '#f0a020'
  return '#d03050'
}

function getMatchScoreLabel(score: number): string {
  if (score >= 80) return '高度匹配 - 简历优秀'
  if (score >= 60) return '基本匹配 - 有提升空间'
  return '匹配度较低 - 需要优化'
}

function getPriorityIcon(priority: number): string {
  const icons = ['🔵', '🟢', '🟡', '🟠', '🔴']
  return icons[priority - 1] || '📌'
}

function getPriorityType(priority: number): 'default' | 'success' | 'warning' | 'error' | 'info' {
  if (priority >= 4) return 'error'
  if (priority === 3) return 'warning'
  if (priority === 2) return 'info'
  return 'success'
}

function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    skill: '技能补充',
    project: '项目优化',
    experience: '经验强化',
    keyword: '关键词优化',
    format: '格式调整'
  }
  return labels[category] || category
}

function downloadReport() {
  if (!analysisResult.value) return
  
  const blob = new Blob([analysisResult.value.report_markdown], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `批量分析报告_${formData.value.keyword}_${new Date().toLocaleDateString()}.md`
  a.click()
  URL.revokeObjectURL(url)
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

onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
})
</script>

<style scoped>
.batch-analysis-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.log-container {
  max-height: 200px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-item {
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
}

.log-item:last-child {
  border-bottom: none;
}

.match-score-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
}

.score-text {
  text-align: center;
}

.score-value {
  font-size: 32px;
  font-weight: bold;
}

.score-label {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}

.skill-item {
  margin-bottom: 12px;
}

.skill-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.distribution-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.distribution-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.markdown-content {
  line-height: 1.8;
}

.markdown-content h1 {
  font-size: 24px;
  margin-top: 24px;
  margin-bottom: 16px;
}

.markdown-content h2 {
  font-size: 20px;
  margin-top: 20px;
  margin-bottom: 12px;
}

.markdown-content h3 {
  font-size: 18px;
  margin-top: 16px;
  margin-bottom: 8px;
}

.markdown-content ul,
.markdown-content ol {
  margin-left: 24px;
  margin-bottom: 12px;
}

.markdown-content code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.markdown-content pre {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
