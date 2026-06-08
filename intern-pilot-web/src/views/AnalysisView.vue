<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useResumeStore } from '../stores/resume'
import { useJDStore } from '../stores/jd'
import { useMatchStore } from '../stores/match'
import { analyzeMatch } from '../api/match'
import { getResumeHistory, getJDHistory } from '../api/history'
import type { ResumeHistoryItem, JDHistoryItem } from '../api/history'
import { 
  NCard, 
  NButton, 
  NSpace, 
  NSpin, 
  NAlert,
  NProgress,
  NTag,
  NDivider,
  NCollapse,
  NCollapseItem,
  NSelect,
  useMessage
} from 'naive-ui'
import MarkdownIt from 'markdown-it'

const router = useRouter()
const message = useMessage()
const resumeStore = useResumeStore()
const jdStore = useJDStore()
const matchStore = useMatchStore()

const isLoading = ref(false)
const errorMessage = ref('')
const isAnalyzed = ref(false)

// 历史数据
const resumeHistory = ref<ResumeHistoryItem[]>([])
const jdHistory = ref<JDHistoryItem[]>([])
const selectedResumeId = ref<string | null>(resumeStore.resumeId)
const selectedJdId = ref<string | null>(jdStore.jdId)
const isLoadingHistory = ref(false)

const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true
})

const canAnalyze = computed(() => selectedResumeId.value && selectedJdId.value)

// 简历选项
const resumeOptions = computed(() => 
  resumeHistory.value.map(resume => ({
    label: `${resume.name || '未命名'} (${new Date(resume.created_at).toLocaleDateString()})`,
    value: resume.resume_id
  }))
)

// JD 选项
const jdOptions = computed(() => 
  jdHistory.value.map(jd => ({
    label: `${jd.keywords?.slice(0, 3).join(', ') || 'JD'} (${new Date(jd.created_at).toLocaleDateString()})`,
    value: jd.jd_id
  }))
)

/**
 * 加载历史数据
 */
const loadHistory = async () => {
  try {
    isLoadingHistory.value = true
    
    console.log('开始加载历史数据...')
    
    // 加载简历历史
    const resumes = await getResumeHistory()
    resumeHistory.value = resumes
    console.log('简历历史加载成功:', resumes.length, '条')
    
    // 加载 JD 历史（使用 API 函数）
    const jds = await getJDHistory()
    jdHistory.value = jds
    console.log('JD 历史加载成功:', jds.length, '条')
    console.log('JD 数据:', jds)
    
    if (jds.length === 0) {
      console.warn('⚠️ JD 历史为空，可能的原因：')
      console.warn('1. 数据库中没有 JD 数据')
      console.warn('2. user_id 不匹配')
      console.warn('3. 权限验证失败')
    }
    
    console.log('加载历史数据成功:', {
      resumeCount: resumes.length,
      jdCount: jds.length
    })
    
  } catch (error: any) {
    console.error('加载历史数据失败:', error)
    console.error('错误详情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status
    })
    message.error('加载历史数据失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    isLoadingHistory.value = false
  }
}

/**
 * 匹配度颜色
 */
const getScoreColor = (score: number) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'error'
}

/**
 * 匹配度状态
 */
const getScoreStatus = (score: number) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'error'
}

/**
 * 优先级颜色
 */
const getPriorityColor = (priority: number) => {
  if (priority >= 4) return 'error'
  if (priority >= 3) return 'warning'
  return 'info'
}

/**
 * 渲染 Markdown
 */
const renderMarkdown = (markdown: string) => {
  return md.render(markdown)
}

/**
 * 执行匹配分析
 */
const performAnalysis = async () => {
  if (!canAnalyze.value) {
    message.warning('请选择简历和 JD')
    return
  }
  
  try {
    isLoading.value = true
    errorMessage.value = ''
    
    const response = await analyzeMatch(selectedResumeId.value!, selectedJdId.value!)
    
    matchStore.setMatchId(response.match_id)
    matchStore.setAnalysis(response.analysis)
    matchStore.setEnhancements(response.enhancements)
    matchStore.setReport(response.report_markdown)
    
    // 更新 store 中的 ID
    resumeStore.setResumeId(selectedResumeId.value!)
    jdStore.setJDId(selectedJdId.value!)
    
    isAnalyzed.value = true
    message.success('分析完成！')
    
    // 自动跳转到报告页面
    router.push('/analysis-reports')
    
  } catch (error: any) {
    console.error('分析失败:', error)
    
    // 检查是否是超时错误
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      message.warning('分析时间较长，正在后台处理，请稍后查看历史记录')
      errorMessage.value = '分析超时，但后台可能仍在处理中。请稍后在历史记录中查看结果。'
    } else {
      errorMessage.value = error.response?.data?.detail || error.message || '分析失败'
      message.error(errorMessage.value)
    }
  } finally {
    isLoading.value = false
  }
}

/**
 * 重新开始
 */
const restart = () => {
  router.push('/resume')
}

/**
 * 页面加载时自动分析
 */
onMounted(async () => {
  // 加载历史数据
  await loadHistory()
  
  // 如果有选中的简历和 JD，且没有分析结果，自动分析
  if (canAnalyze.value && !matchStore.analysis) {
    performAnalysis()
  } else if (matchStore.analysis) {
    isAnalyzed.value = true
  }
})
</script>

<template>
  <div style="max-width: 1200px; margin: 0 auto">
    <n-card title="📊 AI 匹配分析">
      <template #header-extra>
        <n-tag type="info">步骤 3/3</n-tag>
      </template>
      
      <!-- 选择简历和 JD -->
      <n-card title="选择数据" style="margin-bottom: 24px" :bordered="false">
        <n-space vertical :size="16">
          <div>
            <div style="margin-bottom: 8px; font-weight: 600">📄 选择简历：</div>
            <n-select
              v-model:value="selectedResumeId"
              :options="resumeOptions"
              placeholder="请选择历史简历"
              :loading="isLoadingHistory"
              clearable
              filterable
            />
          </div>
          
          <div>
            <div style="margin-bottom: 8px; font-weight: 600">📋 选择 JD：</div>
            <n-select
              v-model:value="selectedJdId"
              :options="jdOptions"
              placeholder="请选择历史 JD"
              :loading="isLoadingHistory"
              clearable
              filterable
            />
          </div>
          
          <n-space>
            <n-button 
              type="primary" 
              :disabled="!canAnalyze" 
              :loading="isLoading"
              @click="performAnalysis"
            >
              开始分析
            </n-button>
            <n-button @click="restart">上传新简历/JD</n-button>
          </n-space>
        </n-space>
      </n-card>
      
      <!-- 前置检查 -->
      <n-alert v-if="!canAnalyze && !isLoadingHistory" type="info" style="margin-bottom: 16px">
        请选择简历和 JD，或者上传新的简历和 JD
        <template #action>
          <n-button size="small" @click="restart">上传新数据</n-button>
        </template>
      </n-alert>
      
      <!-- 加载中 -->
      <div v-if="isLoading" style="text-align: center; padding: 48px 0">
        <n-spin size="large">
          <template #description>
            <div style="margin-top: 16px; font-size: 16px">
              AI 正在分析简历与岗位的匹配度...
            </div>
          </template>
        </n-spin>
      </div>
      
      <!-- 错误提示 -->
      <n-alert v-if="errorMessage" type="error" style="margin-bottom: 16px">
        {{ errorMessage }}
        <template #action>
          <n-button size="small" @click="performAnalysis">重试</n-button>
        </template>
      </n-alert>
      
      <!-- 分析结果 -->
      <div v-if="isAnalyzed && matchStore.analysis">
        <!-- 匹配度评分 -->
        <n-card title="🎯 匹配度评分" style="margin-bottom: 24px">
          <div style="text-align: center; padding: 24px 0">
            <div style="font-size: 64px; font-weight: bold; margin-bottom: 16px">
              {{ matchStore.analysis.overall_score?.toFixed(1) ?? '0.0' }}
            </div>
            <n-progress
              type="line"
              :percentage="matchStore.analysis.overall_score ?? 0"
              :status="getScoreStatus(matchStore.analysis.overall_score ?? 0)"
              :show-indicator="false"
              style="max-width: 400px; margin: 0 auto"
            />
            <div style="margin-top: 16px; font-size: 16px; color: #666">
              {{ (matchStore.analysis.overall_score ?? 0) >= 80 ? '非常匹配' : 
                 (matchStore.analysis.overall_score ?? 0) >= 60 ? '基本匹配' : '匹配度较低' }}
            </div>
          </div>
        </n-card>
        
        <!-- 技能匹配情况 -->
        <n-card title="💡 技能匹配情况" style="margin-bottom: 24px">
          <div style="margin-bottom: 16px">
            <div style="margin-bottom: 8px; font-weight: 600">✅ 已命中技能：</div>
            <n-space v-if="matchStore.analysis.matched_skills?.length">
              <n-tag v-for="(skill, idx) in matchStore.analysis.matched_skills" :key="idx" type="success">
                {{ skill }}
              </n-tag>
            </n-space>
            <div v-else style="color: #999">暂无</div>
          </div>
          
          <n-divider style="margin: 16px 0" />
          
          <div>
            <div style="margin-bottom: 8px; font-weight: 600">❌ 缺失技能：</div>
            <n-space v-if="matchStore.analysis.missing_skills?.length">
              <n-tag v-for="(skill, idx) in matchStore.analysis.missing_skills" :key="idx" type="error">
                {{ skill }}
              </n-tag>
            </n-space>
            <div v-else style="color: #999">暂无</div>
          </div>
        </n-card>
        
        <!-- 优劣势分析 -->
        <n-card title="📈 优劣势分析" style="margin-bottom: 24px">
          <div style="margin-bottom: 16px">
            <div style="margin-bottom: 8px; font-weight: 600; color: #18a058">💪 优势：</div>
            <ul v-if="matchStore.analysis.strengths?.length" style="margin: 0; padding-left: 20px">
              <li v-for="(item, idx) in matchStore.analysis.strengths" :key="idx" style="margin-bottom: 8px">
                {{ item }}
              </li>
            </ul>
            <div v-else style="color: #999">暂无</div>
          </div>
          
          <n-divider style="margin: 16px 0" />
          
          <div>
            <div style="margin-bottom: 8px; font-weight: 600; color: #d03050">⚠️ 劣势：</div>
            <ul v-if="matchStore.analysis.weaknesses?.length" style="margin: 0; padding-left: 20px">
              <li v-for="(item, idx) in matchStore.analysis.weaknesses" :key="idx" style="margin-bottom: 8px">
                {{ item }}
              </li>
            </ul>
            <div v-else style="color: #999">暂无</div>
          </div>
        </n-card>
        
        <!-- 改进建议 -->
        <n-card title="🚀 改进建议" style="margin-bottom: 24px">
          <ul v-if="matchStore.analysis.suggestions?.length" style="margin: 0; padding-left: 20px">
            <li v-for="(item, idx) in matchStore.analysis.suggestions" :key="idx" style="margin-bottom: 8px">
              {{ item }}
            </li>
          </ul>
          <div v-else style="color: #999">暂无</div>
        </n-card>
        
        <!-- 增强建议 -->
        <n-card title="✨ 简历增强建议" style="margin-bottom: 24px">
          <n-collapse v-if="matchStore.enhancements?.length">
            <n-collapse-item 
              v-for="(enhancement, idx) in matchStore.enhancements" 
              :key="idx"
              :title="`${enhancement.title}`"
            >
              <template #header-extra>
                <n-tag :type="getPriorityColor(enhancement.priority)" size="small">
                  优先级 {{ enhancement.priority }}
                </n-tag>
                <n-tag type="info" size="small" style="margin-left: 8px">
                  {{ enhancement.category }}
                </n-tag>
              </template>
              
              <div style="margin-bottom: 12px">
                {{ enhancement.description }}
              </div>
              
              <div v-if="enhancement.example" style="background: #f5f5f5; padding: 12px; border-radius: 4px">
                <div style="font-weight: 600; margin-bottom: 8px">示例：</div>
                <div style="white-space: pre-wrap">{{ enhancement.example }}</div>
              </div>
            </n-collapse-item>
          </n-collapse>
          <div v-else style="color: #999">暂无</div>
        </n-card>
        
        <!-- 完整报告 -->
        <n-card title="📝 完整分析报告" style="margin-bottom: 24px">
          <div 
            v-if="matchStore.report" 
            class="markdown-body"
            v-html="renderMarkdown(matchStore.report)"
          />
          <div v-else style="color: #999">暂无</div>
        </n-card>
        
        <!-- 操作按钮 -->
        <n-space justify="center">
          <n-button @click="restart">重新开始</n-button>
          <n-button type="primary" @click="performAnalysis">重新分析</n-button>
        </n-space>
      </div>
    </n-card>
  </div>
</template>

<style scoped>
ul {
  list-style-type: disc;
}

/* Markdown 样式 */
.markdown-body {
  line-height: 1.6;
  color: #333;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body h1 {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body h2 {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body h3 {
  font-size: 1.25em;
}

.markdown-body p {
  margin-bottom: 16px;
}

.markdown-body ul,
.markdown-body ol {
  margin-bottom: 16px;
  padding-left: 2em;
}

.markdown-body li {
  margin-bottom: 4px;
}

.markdown-body code {
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 85%;
}

.markdown-body pre {
  background-color: #f6f8fa;
  padding: 16px;
  border-radius: 6px;
  overflow: auto;
  margin-bottom: 16px;
}

.markdown-body pre code {
  background-color: transparent;
  padding: 0;
}

.markdown-body blockquote {
  border-left: 4px solid #dfe2e5;
  padding-left: 16px;
  margin-left: 0;
  color: #6a737d;
}

.markdown-body strong {
  font-weight: 600;
}

.markdown-body em {
  font-style: italic;
}
</style>
