<template>
  <div class="history-container">
    <!-- 首页: 统计卡片 -->
    <div v-if="currentView === 'home'" class="home-view">
      <n-card title="📚 历史记录" :bordered="false">
        <n-space vertical :size="24">
          <n-text depth="3">点击卡片查看详细列表</n-text>

          <n-grid :cols="3" :x-gap="16" :y-gap="16" responsive="screen">
            <!-- 简历卡片 -->
            <n-grid-item>
              <n-card
                hoverable
                class="stat-card resume-card"
                @click="showList('resumes')"
              >
                <n-space vertical align="center" :size="16">
                  <n-avatar :size="64" color="#18a058">
                    <n-icon :size="32">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path
                          fill="currentColor"
                          d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6m4 18H6V4h7v5h5v11m-3-7v1H8v-1h7m0 2v1H8v-1h7m0 2v1H8v-1h7Z"
                        />
                      </svg>
                    </n-icon>
                  </n-avatar>
                  <div style="text-align: center">
                    <n-text strong style="font-size: 32px; display: block">
                      {{ resumeCount }}
                    </n-text>
                    <n-text depth="3" style="font-size: 16px">份简历</n-text>
                  </div>
                </n-space>
              </n-card>
            </n-grid-item>

            <!-- 岗位卡片 -->
            <n-grid-item>
              <n-card
                hoverable
                class="stat-card jd-card"
                @click="showList('jds')"
              >
                <n-space vertical align="center" :size="16">
                  <n-avatar :size="64" color="#2080f0">
                    <n-icon :size="32">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path
                          fill="currentColor"
                          d="M20 6h-4V4c0-1.11-.89-2-2-2h-4c-1.11 0-2 .89-2 2v2H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-6 0h-4V4h4v2z"
                        />
                      </svg>
                    </n-icon>
                  </n-avatar>
                  <div style="text-align: center">
                    <n-text strong style="font-size: 32px; display: block">
                      {{ jdCount }}
                    </n-text>
                    <n-text depth="3" style="font-size: 16px">个岗位</n-text>
                  </div>
                </n-space>
              </n-card>
            </n-grid-item>

            <!-- 分析卡片 -->
            <n-grid-item>
              <n-card
                hoverable
                class="stat-card match-card"
                @click="showList('matches')"
              >
                <n-space vertical align="center" :size="16">
                  <n-avatar :size="64" color="#f0a020">
                    <n-icon :size="32">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path
                          fill="currentColor"
                          d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
                        />
                      </svg>
                    </n-icon>
                  </n-avatar>
                  <div style="text-align: center">
                    <n-text strong style="font-size: 32px; display: block">
                      {{ matchCount }}
                    </n-text>
                    <n-text depth="3" style="font-size: 16px">次分析</n-text>
                  </div>
                </n-space>
              </n-card>
            </n-grid-item>
          </n-grid>
        </n-space>
      </n-card>
    </div>

    <!-- 列表页: 简历列表 -->
    <div v-else-if="currentView === 'resumes'" class="list-view">
      <n-card :bordered="false">
        <template #header>
          <n-space align="center">
            <n-button text @click="backToHome">
              <template #icon>
                <n-icon>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
                  </svg>
                </n-icon>
              </template>
              返回
            </n-button>
            <n-text strong style="font-size: 18px">📄 简历列表</n-text>
            <n-tag type="info">共 {{ resumeHistory.length }} 份</n-tag>
          </n-space>
        </template>

        <n-spin :show="loadingResumes">
          <n-empty
            v-if="!loadingResumes && resumeHistory.length === 0"
            description="暂无简历记录"
          >
            <template #extra>
              <n-button type="primary" @click="$router.push('/resume')">
                上传简历
              </n-button>
            </template>
          </n-empty>

          <n-list v-else bordered>
            <n-list-item v-for="resume in resumeHistory" :key="resume.resume_id">
              <template #prefix>
                <n-avatar color="#18a058">
                  <n-icon size="20">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6m4 18H6V4h7v5h5v11m-3-7v1H8v-1h7m0 2v1H8v-1h7m0 2v1H8v-1h7Z"
                      />
                    </svg>
                  </n-icon>
                </n-avatar>
              </template>

              <n-thing>
                <template #header>
                  <n-text strong>{{ resume.filename }}</n-text>
                </template>
                <template #description>
                  <n-space :size="8">
                    <n-tag v-if="resume.name" size="small" type="info">
                      {{ resume.name }}
                    </n-tag>
                    <n-tag v-if="resume.target_position" size="small" type="success">
                      {{ resume.target_position }}
                    </n-tag>
                    <n-tag :type="resume.parsed ? 'success' : 'warning'" size="small">
                      {{ resume.parsed ? '已解析' : '未解析' }}
                    </n-tag>
                    <n-text depth="3" style="font-size: 12px">
                      上传于 {{ formatDate(resume.created_at) }}
                    </n-text>
                  </n-space>
                </template>
              </n-thing>

              <template #suffix>
                <n-space>
                  <n-button size="small" @click="useResumeForBatchAnalysis(resume.resume_id)">
                    批量分析
                  </n-button>
                  <n-button size="small" type="primary" @click="viewResumeDetail(resume.resume_id)">
                    查看详情
                  </n-button>
                </n-space>
              </template>
            </n-list-item>
          </n-list>
        </n-spin>
      </n-card>
    </div>

    <!-- 列表页: 岗位列表 -->
    <div v-else-if="currentView === 'jds'" class="list-view">
      <n-card :bordered="false">
        <template #header>
          <n-space align="center">
            <n-button text @click="backToHome">
              <template #icon>
                <n-icon>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
                  </svg>
                </n-icon>
              </template>
              返回
            </n-button>
            <n-text strong style="font-size: 18px">💼 岗位列表</n-text>
            <n-tag type="info">共 {{ jdHistory.length }} 个</n-tag>
          </n-space>
        </template>

        <n-spin :show="loadingJDs">
          <n-empty v-if="!loadingJDs && jdHistory.length === 0" description="暂无岗位记录">
            <template #extra>
              <n-button type="primary" @click="$router.push('/jd')">
                添加岗位
              </n-button>
            </template>
          </n-empty>

          <n-list v-else bordered>
            <n-list-item v-for="jd in jdHistory" :key="jd.jd_id">
              <template #prefix>
                <n-avatar color="#2080f0">
                  <n-icon size="20">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M20 6h-4V4c0-1.11-.89-2-2-2h-4c-1.11 0-2 .89-2 2v2H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-6 0h-4V4h4v2z"
                      />
                    </svg>
                  </n-icon>
                </n-avatar>
              </template>

              <n-thing>
                <template #header>
                  <n-text strong>{{ jd.position || '未知职位' }}</n-text>
                </template>
                <template #description>
                  <n-space :size="8">
                    <n-tag v-if="jd.company" size="small" type="info">
                      {{ jd.company }}
                    </n-tag>
                    <n-tag v-if="jd.location" size="small">
                      {{ jd.location }}
                    </n-tag>
                    <n-tag :type="jd.parsed ? 'success' : 'warning'" size="small">
                      {{ jd.parsed ? '已解析' : '未解析' }}
                    </n-tag>
                    <n-text depth="3" style="font-size: 12px">
                      添加于 {{ formatDate(jd.created_at) }}
                    </n-text>
                  </n-space>
                </template>
              </n-thing>

              <template #suffix>
                <n-button size="small" type="primary" @click="viewJDDetail(jd.jd_id)">
                  查看详情
                </n-button>
              </template>
            </n-list-item>
          </n-list>
        </n-spin>
      </n-card>
    </div>

    <!-- 列表页: 分析列表 -->
    <div v-else-if="currentView === 'matches'" class="list-view">
      <n-card :bordered="false">
        <template #header>
          <n-space align="center">
            <n-button text @click="backToHome">
              <template #icon>
                <n-icon>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
                  </svg>
                </n-icon>
              </template>
              返回
            </n-button>
            <n-text strong style="font-size: 18px">🎯 分析列表</n-text>
            <n-tag type="info">共 {{ matchHistory.length }} 次</n-tag>
          </n-space>
        </template>

        <n-spin :show="loadingMatches">
          <n-empty v-if="!loadingMatches && matchHistory.length === 0" description="暂无分析记录">
            <template #extra>
              <n-button type="primary" @click="$router.push('/analysis')">
                开始分析
              </n-button>
            </template>
          </n-empty>

          <n-list v-else bordered>
            <n-list-item v-for="match in matchHistory" :key="match.match_id">
              <template #prefix>
                <n-avatar :color="getScoreColor(match.overall_score)">
                  <n-text style="color: white; font-weight: bold">
                    {{ match.overall_score?.toFixed(0) ?? '0' }}
                  </n-text>
                </n-avatar>
              </template>

              <n-thing>
                <template #header>
                  <n-space :size="8" align="center">
                    <n-text strong>匹配分析</n-text>
                    <n-tag :type="getScoreType(match.overall_score)" size="small">
                      {{ getScoreLabel(match.overall_score) }}
                    </n-tag>
                  </n-space>
                </template>
                <template #description>
                  <n-space :size="8" vertical>
                    <n-text v-if="match.resume_name" depth="3" style="font-size: 12px">
                      简历: {{ match.resume_name }}
                    </n-text>
                    <n-text v-if="match.company || match.position" depth="3" style="font-size: 12px">
                      岗位: {{ match.company || '未知' }} - {{ match.position || '未知' }}
                    </n-text>
                    <n-text depth="3" style="font-size: 12px">
                      分析于 {{ formatDate(match.created_at) }}
                    </n-text>
                  </n-space>
                </template>
              </n-thing>

              <template #suffix>
                <n-button size="small" type="primary" @click="viewMatchDetail(match.match_id)">
                  查看报告
                </n-button>
              </template>
            </n-list-item>
          </n-list>
        </n-spin>
      </n-card>
    </div>

    <!-- 简历详情弹窗 -->
    <ResumeDetailModal v-model:show="showResumeDetail" :resume-id="selectedResumeId" />

    <!-- JD详情弹窗 -->
    <JDDetailModal v-model:show="showJDDetail" :jd-id="selectedJDId" />

    <!-- 匹配分析报告弹窗 -->
    <MatchReportModal v-model:show="showMatchReport" :match-id="selectedMatchId" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  useMessage,
  NCard,
  NSpace,
  NText,
  NGrid,
  NGridItem,
  NAvatar,
  NIcon,
  NButton,
  NSpin,
  NEmpty,
  NList,
  NListItem,
  NThing,
  NTag
} from 'naive-ui'
import {
  getResumeHistory,
  getJDHistory,
  getMatchHistory,
  type ResumeHistory,
  type JDHistory,
  type MatchHistory
} from '@/api/history'
import ResumeDetailModal from '@/components/history/ResumeDetailModal.vue'
import JDDetailModal from '@/components/history/JDDetailModal.vue'
import MatchReportModal from '@/components/history/MatchReportModal.vue'

const router = useRouter()
const message = useMessage()

// 当前视图: 'home' | 'resumes' | 'jds' | 'matches'
const currentView = ref<'home' | 'resumes' | 'jds' | 'matches'>('home')

// 数据
const resumeHistory = ref<ResumeHistory[]>([])
const jdHistory = ref<JDHistory[]>([])
const matchHistory = ref<MatchHistory[]>([])

// 加载状态
const loadingResumes = ref(false)
const loadingJDs = ref(false)
const loadingMatches = ref(false)

// 弹窗状态
const showResumeDetail = ref(false)
const showJDDetail = ref(false)
const showMatchReport = ref(false)

// 选中的ID
const selectedResumeId = ref<string | null>(null)
const selectedJDId = ref<string | null>(null)
const selectedMatchId = ref<string | null>(null)

// 统计数量
const resumeCount = computed(() => resumeHistory.value.length)
const jdCount = computed(() => jdHistory.value.length)
const matchCount = computed(() => matchHistory.value.length)

// 加载简历历史
async function loadResumeHistory() {
  loadingResumes.value = true
  try {
    resumeHistory.value = await getResumeHistory()
  } catch (error) {
    console.error('加载简历历史失败:', error)
    message.error('加载简历历史失败')
  } finally {
    loadingResumes.value = false
  }
}

// 加载 JD 历史
async function loadJDHistory() {
  loadingJDs.value = true
  try {
    jdHistory.value = await getJDHistory()
  } catch (error) {
    console.error('加载岗位历史失败:', error)
    message.error('加载岗位历史失败')
  } finally {
    loadingJDs.value = false
  }
}

// 加载匹配历史
async function loadMatchHistory() {
  loadingMatches.value = true
  try {
    matchHistory.value = await getMatchHistory()
  } catch (error) {
    console.error('加载分析历史失败:', error)
    message.error('加载分析历史失败')
  } finally {
    loadingMatches.value = false
  }
}

// 显示列表
function showList(type: 'resumes' | 'jds' | 'matches') {
  currentView.value = type
  
  // 如果数据还没加载,则加载
  if (type === 'resumes' && resumeHistory.value.length === 0) {
    loadResumeHistory()
  } else if (type === 'jds' && jdHistory.value.length === 0) {
    loadJDHistory()
  } else if (type === 'matches' && matchHistory.value.length === 0) {
    loadMatchHistory()
  }
}

// 返回首页
function backToHome() {
  currentView.value = 'home'
}

// 格式化日期
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 使用简历进行批量分析
function useResumeForBatchAnalysis(resumeId: string) {
  router.push({
    path: '/batch-analysis',
    query: { resume_id: resumeId }
  })
}

// 查看简历详情
function viewResumeDetail(resumeId: string) {
  selectedResumeId.value = resumeId
  showResumeDetail.value = true
}

// 查看 JD 详情
function viewJDDetail(jdId: string) {
  selectedJDId.value = jdId
  showJDDetail.value = true
}

// 查看匹配详情
function viewMatchDetail(matchId: string) {
  selectedMatchId.value = matchId
  showMatchReport.value = true
}

// 获取分数颜色
function getScoreColor(score: number): string {
  if (score >= 80) return '#18a058'
  if (score >= 60) return '#f0a020'
  return '#d03050'
}

// 获取分数类型
function getScoreType(score: number): 'success' | 'warning' | 'error' {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'error'
}

// 获取分数标签
function getScoreLabel(score: number): string {
  if (score >= 80) return '高度匹配'
  if (score >= 60) return '基本匹配'
  return '匹配度低'
}

// 初始化时只加载统计数据
onMounted(() => {
  // 加载所有数据用于统计
  loadResumeHistory()
  loadJDHistory()
  loadMatchHistory()
})
</script>

<style scoped>
.history-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.home-view {
  width: 100%;
}

.list-view {
  width: 100%;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.resume-card:hover {
  border-color: #18a058;
}

.jd-card:hover {
  border-color: #2080f0;
}

.match-card:hover {
  border-color: #f0a020;
}
</style>
