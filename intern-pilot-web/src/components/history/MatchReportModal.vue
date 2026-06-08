<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    title="🎯 匹配分析报告"
    :style="{ width: '90%', maxWidth: '1400px' }"
    :segmented="{ content: 'soft' }"
    @after-leave="handleClose"
  >
    <n-spin :show="loading">
      <div v-if="match" class="match-report">
        <!-- 概览卡片 -->
        <n-card :bordered="false" class="overview-card">
          <n-space vertical :size="16">
            <!-- 匹配分数 -->
            <div class="score-section">
              <n-space align="center" :size="16">
                <n-avatar
                  :size="80"
                  :color="getScoreColor(match.overall_score)"
                  style="font-size: 32px; font-weight: bold"
                >
                  {{ match.overall_score?.toFixed(0) ?? '0' }}
                </n-avatar>
                <div>
                  <n-text strong style="font-size: 24px">匹配分数</n-text>
                  <br />
                  <n-tag :type="getScoreType(match.overall_score)" size="large" style="margin-top: 8px">
                    {{ getScoreLabel(match.overall_score) }}
                  </n-tag>
                </div>
              </n-space>
            </div>

            <!-- 基本信息 -->
            <n-descriptions :column="2" label-placement="left">
              <n-descriptions-item label="简历">
                <n-text>{{ match.resume_name || '未知' }}</n-text>
              </n-descriptions-item>
              <n-descriptions-item label="岗位">
                <n-text>{{ match.company || '未知' }} - {{ match.position || '未知' }}</n-text>
              </n-descriptions-item>
              <n-descriptions-item label="分析时间" :span="2">
                <n-text>{{ formatDate(match.created_at) }}</n-text>
              </n-descriptions-item>
            </n-descriptions>
          </n-space>
        </n-card>

        <!-- 详细分析 Tabs -->
        <n-card title="📊 详细分析" :bordered="false" class="detail-card">
          <n-tabs type="line" animated>
            <!-- 技能匹配 -->
            <n-tab-pane name="skills" tab="⚡ 技能匹配">
              <n-space vertical :size="24">
                <!-- 已匹配技能 -->
                <div v-if="match.matched_skills && match.matched_skills.length > 0">
                  <n-space align="center" :size="8" style="margin-bottom: 12px">
                    <n-text strong style="font-size: 18px">✅ 已匹配技能</n-text>
                    <n-tag type="success" size="small">
                      {{ match.matched_skills.length }} 项
                    </n-tag>
                  </n-space>
                  <n-space :size="12">
                    <n-tag
                      v-for="(skill, index) in match.matched_skills"
                      :key="index"
                      type="success"
                      size="large"
                    >
                      {{ skill }}
                    </n-tag>
                  </n-space>
                </div>

                <!-- 缺失技能 -->
                <div v-if="match.missing_skills && match.missing_skills.length > 0">
                  <n-space align="center" :size="8" style="margin-bottom: 12px">
                    <n-text strong style="font-size: 18px">❌ 缺失技能</n-text>
                    <n-tag type="error" size="small">
                      {{ match.missing_skills.length }} 项
                    </n-tag>
                  </n-space>
                  <n-space :size="12">
                    <n-tag
                      v-for="(skill, index) in match.missing_skills"
                      :key="index"
                      type="error"
                      size="large"
                    >
                      {{ skill }}
                    </n-tag>
                  </n-space>
                </div>

                <n-empty
                  v-if="
                    (!match.matched_skills || match.matched_skills.length === 0) &&
                    (!match.missing_skills || match.missing_skills.length === 0)
                  "
                  description="暂无技能匹配信息"
                />
              </n-space>
            </n-tab-pane>

            <!-- 优势分析 -->
            <n-tab-pane name="strengths" tab="💪 优势分析">
              <n-empty
                v-if="!match.strengths || match.strengths.length === 0"
                description="暂无优势分析"
              />
              <n-list v-else bordered>
                <n-list-item v-for="(item, index) in match.strengths" :key="index">
                  <template #prefix>
                    <n-icon color="#18a058" size="20">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path
                          fill="currentColor"
                          d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"
                        />
                      </svg>
                    </n-icon>
                  </template>
                  {{ item }}
                </n-list-item>
              </n-list>
            </n-tab-pane>

            <!-- 劣势分析 -->
            <n-tab-pane name="weaknesses" tab="⚠️ 劣势分析">
              <n-empty
                v-if="!match.weaknesses || match.weaknesses.length === 0"
                description="暂无劣势分析"
              />
              <n-list v-else bordered>
                <n-list-item v-for="(item, index) in match.weaknesses" :key="index">
                  <template #prefix>
                    <n-icon color="#d03050" size="20">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path
                          fill="currentColor"
                          d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"
                        />
                      </svg>
                    </n-icon>
                  </template>
                  {{ item }}
                </n-list-item>
              </n-list>
            </n-tab-pane>

            <!-- 改进建议 -->
            <n-tab-pane name="suggestions" tab="💡 改进建议">
              <n-empty
                v-if="!match.suggestions || match.suggestions.length === 0"
                description="暂无改进建议"
              />
              <n-list v-else bordered>
                <n-list-item v-for="(item, index) in match.suggestions" :key="index">
                  <template #prefix>
                    <n-icon color="#2080f0" size="20">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path
                          fill="currentColor"
                          d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z"
                        />
                      </svg>
                    </n-icon>
                  </template>
                  {{ item }}
                </n-list-item>
              </n-list>
            </n-tab-pane>
          </n-tabs>
        </n-card>

        <!-- 简历优化建议 -->
        <n-card
          v-if="match.enhancements && match.enhancements.length > 0"
          title="✨ 简历优化建议"
          :bordered="false"
        >
          <n-collapse>
            <n-collapse-item title="点击展开/收起优化建议" name="enhancements">
              <n-space vertical :size="16">
                <n-card
                  v-for="(enhancement, index) in match.enhancements"
                  :key="index"
                  :bordered="false"
                  size="small"
                  class="enhancement-card"
                >
                  <n-space vertical :size="12">
                    <n-space align="center" :size="8">
                      <n-tag :type="getPriorityType(enhancement.priority)">
                        优先级 {{ enhancement.priority }}
                      </n-tag>
                      <n-tag type="info">{{ enhancement.category }}</n-tag>
                    </n-space>

                    <div>
                      <n-text strong style="font-size: 16px">{{ enhancement.title }}</n-text>
                    </div>

                    <div>
                      <n-text depth="3">{{ enhancement.description }}</n-text>
                    </div>

                    <div v-if="enhancement.example">
                      <n-text strong style="color: #18a058">示例:</n-text>
                      <n-blockquote style="margin-top: 8px; border-left-color: #18a058">
                        {{ enhancement.example }}
                      </n-blockquote>
                    </div>
                  </n-space>
                </n-card>
              </n-space>
            </n-collapse-item>
          </n-collapse>
        </n-card>

        <!-- 完整报告 -->
        <n-card v-if="match.report_markdown" title="📄 完整报告" :bordered="false">
          <n-collapse>
            <n-collapse-item title="点击展开/收起完整报告 (Markdown)" name="report">
              <n-code 
                :code="match.report_markdown" 
                language="markdown" 
                show-line-numbers 
                word-wrap
              />
            </n-collapse-item>
          </n-collapse>
        </n-card>
      </div>
    </n-spin>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleClose">关闭</n-button>
        <n-button type="primary" @click="handleOptimizeResume">
          优化简历
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  useMessage,
  NModal,
  NSpin,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NText,
  NTag,
  NTabs,
  NTabPane,
  NEmpty,
  NSpace,
  NList,
  NListItem,
  NCollapse,
  NCollapseItem,
  NCode,
  NButton,
  NAvatar,
  NIcon,
  NBlockquote
} from 'naive-ui'
import { getMatchDetail, type MatchDetail } from '@/api/history'

const props = defineProps<{
  matchId: string | null
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
}>()

const router = useRouter()
const message = useMessage()

const visible = ref(false)
const loading = ref(false)
const match = ref<MatchDetail | null>(null)

// 监听 show 变化
watch(
  () => props.show,
  (newVal) => {
    visible.value = newVal
    if (newVal && props.matchId) {
      loadMatchDetail()
    }
  }
)

// 监听 visible 变化
watch(visible, (newVal) => {
  emit('update:show', newVal)
})

// 加载匹配详情
async function loadMatchDetail() {
  if (!props.matchId) return

  loading.value = true
  try {
    match.value = await getMatchDetail(props.matchId)
  } catch (error) {
    console.error('加载匹配详情失败:', error)
    message.error('加载匹配详情失败')
    handleClose()
  } finally {
    loading.value = false
  }
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

// 获取优先级类型
function getPriorityType(priority: number): 'error' | 'warning' | 'info' {
  if (priority <= 2) return 'error'  // 高优先级
  if (priority <= 4) return 'warning'  // 中优先级
  return 'info'  // 低优先级
}

// 优化简历
function handleOptimizeResume() {
  if (!match.value) return
  router.push({
    path: '/analysis',
    query: {
      resume_id: match.value.resume_id,
      jd_id: match.value.jd_id
    }
  })
  handleClose()
}

// 关闭弹窗
function handleClose() {
  visible.value = false
  match.value = null
}
</script>

<style scoped>
.match-report {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.overview-card,
.detail-card {
  background: var(--n-color);
}

.score-section {
  padding: 16px;
  background: var(--n-color-target);
  border-radius: 8px;
}

.enhancement-card {
  background: var(--n-color-target);
  border: 1px solid var(--n-border-color);
}
</style>
