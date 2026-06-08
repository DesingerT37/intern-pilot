<template>
  <div class="reports-container">
    <n-card title="📊 历史分析报告" :bordered="false">
      <template #header-extra>
        <n-button type="primary" @click="$router.push('/batch-analysis')">
          <template #icon>
            <span>➕</span>
          </template>
          新建分析
        </n-button>
      </template>

      <!-- 加载中 -->
      <n-spin v-if="loading" :size="60" style="width: 100%; padding: 60px 0">
        <template #description>
          <n-text depth="3">加载报告列表中...</n-text>
        </template>
      </n-spin>

      <!-- 报告列表 -->
      <n-space v-else-if="reports.length > 0" vertical :size="16">
        <n-card
          v-for="report in reports"
          :key="report.batch_id"
          :bordered="false"
          embedded
          hoverable
          class="report-card"
          @click="handleViewReport(report)"
        >
          <div class="report-header">
            <div class="report-title">
              <n-text strong style="font-size: 16px">{{ report.keyword }}</n-text>
              <n-tag v-if="report.city" size="small" type="info">{{ report.city }}</n-tag>
            </div>
            <n-tag :type="getStatusType(report.status)" size="small">
              {{ getStatusLabel(report.status) }}
            </n-tag>
          </div>

          <n-divider style="margin: 12px 0" />

          <n-descriptions :column="3" size="small">
            <n-descriptions-item label="分析职位">
              {{ report.analyzed_jobs }} / {{ report.total_jobs }} 个
            </n-descriptions-item>
            <n-descriptions-item label="匹配度">
              <n-progress
                type="line"
                :percentage="report.match_score"
                :height="8"
                :show-indicator="false"
                :color="getMatchScoreColor(report.match_score)"
                style="width: 100px"
              />
              <n-text style="margin-left: 8px">{{ report.match_score.toFixed(1) }}%</n-text>
            </n-descriptions-item>
            <n-descriptions-item label="分析时间">
              {{ formatDate(report.created_at) }}
            </n-descriptions-item>
          </n-descriptions>

          <n-space style="margin-top: 12px">
            <n-button size="small" type="primary" @click.stop="handleViewReport(report)">
              查看报告
            </n-button>
            <n-button size="small" @click.stop="handleDownloadReport(report)">
              下载报告
            </n-button>
          </n-space>
        </n-card>
      </n-space>

      <!-- 空状态 -->
      <n-empty
        v-else
        description="暂无分析报告"
        style="padding: 60px 0"
      >
        <template #extra>
          <n-button type="primary" @click="$router.push('/batch-analysis')">
            立即创建分析
          </n-button>
        </template>
      </n-empty>
    </n-card>

    <!-- 报告查看模态框 -->
    <n-modal
      v-model:show="showReportModal"
      preset="card"
      title="📝 分析报告"
      style="width: 90%; max-width: 1400px"
      :bordered="false"
    >
      <template #header-extra>
        <n-space>
          <n-button size="small" @click="handleDownloadCurrentReport">
            下载 Markdown
          </n-button>
          <n-button size="small" type="primary" @click="showReportModal = false">
            关闭
          </n-button>
        </n-space>
      </template>

      <n-spin v-if="loadingReport" :size="60" style="width: 100%; padding: 60px 0">
        <template #description>
          <n-text depth="3">加载报告详情中...</n-text>
        </template>
      </n-spin>

      <div v-else-if="currentReport" class="report-content">
        <!-- 分析概览 -->
        <n-card title="📈 分析概览" :bordered="false" embedded style="margin-bottom: 16px">
          <n-descriptions :column="2" bordered>
            <n-descriptions-item label="关键词">
              {{ selectedReportInfo?.keyword }}
            </n-descriptions-item>
            <n-descriptions-item label="城市">
              {{ selectedReportInfo?.city || '全国' }}
            </n-descriptions-item>
            <n-descriptions-item label="分析职位数">
              {{ currentReport.aggregated_analysis.total_jobs }} 个
            </n-descriptions-item>
            <n-descriptions-item label="简历匹配度">
              <n-progress
                type="line"
                :percentage="currentReport.resume_match_score"
                :height="12"
                :color="getMatchScoreColor(currentReport.resume_match_score)"
                style="width: 200px"
              />
              <n-text style="margin-left: 8px">
                {{ currentReport.resume_match_score.toFixed(1) }}%
              </n-text>
            </n-descriptions-item>
          </n-descriptions>
        </n-card>

        <!-- 优化建议 -->
        <n-card title="🚀 优化建议" :bordered="false" embedded style="margin-bottom: 16px">
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
        </n-card>

        <!-- Markdown 报告 -->
        <n-card title="📝 完整报告" :bordered="false" embedded>
          <div class="markdown-content" v-html="renderedMarkdown"></div>
        </n-card>
      </div>
    </n-modal>
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
  NDescriptions,
  NDescriptionsItem,
  NProgress,
  NDivider,
  NModal,
  NSpin,
  NEmpty,
  NCollapse,
  NCollapseItem,
  NAlert
} from 'naive-ui'
import {
  getAnalysisReports,
  getBatchResult,
  type AnalysisReportItem,
  type BatchAnalysisResult
} from '@/api/batchAnalysis'
import { marked } from 'marked'

const router = useRouter()
const message = useMessage()

// 报告列表
const reports = ref<AnalysisReportItem[]>([])
const loading = ref(false)

// 当前查看的报告
const showReportModal = ref(false)
const loadingReport = ref(false)
const currentReport = ref<BatchAnalysisResult>()
const selectedReportInfo = ref<AnalysisReportItem>()

// 计算属性
const sortedSuggestions = computed(() => {
  if (!currentReport.value) return []
  return [...currentReport.value.priority_suggestions].sort((a, b) => b.priority - a.priority)
})

const renderedMarkdown = computed(() => {
  if (!currentReport.value) return ''
  return marked(currentReport.value.report_markdown)
})

// 方法
async function loadReports() {
  loading.value = true
  try {
    reports.value = await getAnalysisReports(50)
  } catch (error: any) {
    console.error('加载报告列表失败:', error)
    message.error('加载报告列表失败')
  } finally {
    loading.value = false
  }
}

async function handleViewReport(report: AnalysisReportItem) {
  selectedReportInfo.value = report
  showReportModal.value = true
  loadingReport.value = true
  
  try {
    currentReport.value = await getBatchResult(report.task_id)
  } catch (error: any) {
    console.error('加载报告详情失败:', error)
    message.error('加载报告详情失败')
    showReportModal.value = false
  } finally {
    loadingReport.value = false
  }
}

function handleDownloadReport(report: AnalysisReportItem) {
  // 先加载报告详情，然后下载
  handleViewReport(report).then(() => {
    if (currentReport.value) {
      downloadMarkdown(currentReport.value.report_markdown, `分析报告_${report.keyword}_${formatDate(report.created_at)}.md`)
    }
  })
}

function handleDownloadCurrentReport() {
  if (currentReport.value && selectedReportInfo.value) {
    downloadMarkdown(
      currentReport.value.report_markdown,
      `分析报告_${selectedReportInfo.value.keyword}_${formatDate(selectedReportInfo.value.created_at)}.md`
    )
  }
}

function downloadMarkdown(content: string, filename: string) {
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  message.success('报告已下载')
}

function getStatusType(status: string): 'default' | 'success' | 'warning' | 'error' | 'info' {
  if (status === 'completed') return 'success'
  if (status === 'running') return 'info'
  if (status === 'failed') return 'error'
  return 'default'
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    completed: '已完成',
    running: '进行中',
    failed: '失败',
    pending: '等待中'
  }
  return labels[status] || status
}

function getMatchScoreColor(score: number): string {
  if (score >= 80) return '#18a058'
  if (score >= 60) return '#f0a020'
  return '#d03050'
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
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

// 生命周期
onMounted(() => {
  loadReports()
})
</script>

<style scoped>
.reports-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.report-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.report-content {
  max-height: 70vh;
  overflow-y: auto;
}

.markdown-content {
  line-height: 1.8;
}

.markdown-content :deep(h1) {
  font-size: 24px;
  margin-top: 24px;
  margin-bottom: 16px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 8px;
}

.markdown-content :deep(h2) {
  font-size: 20px;
  margin-top: 20px;
  margin-bottom: 12px;
}

.markdown-content :deep(h3) {
  font-size: 18px;
  margin-top: 16px;
  margin-bottom: 10px;
}

.markdown-content :deep(p) {
  margin-bottom: 12px;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin-left: 24px;
  margin-bottom: 12px;
}

.markdown-content :deep(code) {
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.markdown-content :deep(pre) {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 12px;
}
</style>
