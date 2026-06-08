<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    title="📄 简历详情"
    :style="{ width: '80%', maxWidth: '1200px' }"
    :segmented="{ content: 'soft' }"
    @after-leave="handleClose"
  >
    <n-spin :show="loading">
      <div v-if="resume" class="resume-detail">
        <!-- 基本信息卡片 -->
        <n-card title="👤 基本信息" :bordered="false" class="info-card">
          <n-descriptions :column="2" label-placement="left">
            <n-descriptions-item label="姓名">
              <n-text strong>{{ resume.name || '未填写' }}</n-text>
            </n-descriptions-item>
            <n-descriptions-item label="邮箱">
              <n-text>{{ resume.email || '未填写' }}</n-text>
            </n-descriptions-item>
            <n-descriptions-item label="电话">
              <n-text>{{ resume.phone || '未填写' }}</n-text>
            </n-descriptions-item>
            <n-descriptions-item label="目标岗位">
              <n-tag v-if="resume.target_position" type="success">
                {{ resume.target_position }}
              </n-tag>
              <n-text v-else depth="3">未填写</n-text>
            </n-descriptions-item>
            <n-descriptions-item label="文件名">
              <n-text>{{ resume.filename }}</n-text>
            </n-descriptions-item>
            <n-descriptions-item label="上传时间">
              <n-text>{{ formatDate(resume.created_at) }}</n-text>
            </n-descriptions-item>
          </n-descriptions>
        </n-card>

        <!-- 详细信息 Tabs -->
        <n-card title="📋 详细信息" :bordered="false" class="detail-card">
          <n-tabs type="line" animated>
            <!-- 教育经历 -->
            <n-tab-pane name="education" tab="🎓 教育经历">
              <n-empty
                v-if="!resume.education || resume.education.length === 0"
                description="暂无教育经历"
              />
              <n-space v-else vertical :size="16">
                <n-card
                  v-for="(edu, index) in resume.education"
                  :key="index"
                  :bordered="false"
                  size="small"
                  class="item-card"
                >
                  <n-space vertical :size="8">
                    <n-text strong style="font-size: 16px">
                      {{ edu.school || '未知学校' }}
                    </n-text>
                    <n-space :size="8">
                      <n-tag v-if="edu.major" type="info">{{ edu.major }}</n-tag>
                      <n-tag v-if="edu.degree" type="success">{{ edu.degree }}</n-tag>
                    </n-space>
                    <n-text v-if="edu.start_date || edu.end_date" depth="3">
                      {{ edu.start_date || '?' }} - {{ edu.end_date || '至今' }}
                    </n-text>
                    <n-text v-if="edu.description">{{ edu.description }}</n-text>
                  </n-space>
                </n-card>
              </n-space>
            </n-tab-pane>

            <!-- 工作经验 -->
            <n-tab-pane name="work" tab="💼 工作经验">
              <n-empty
                v-if="!resume.work_experience || resume.work_experience.length === 0"
                description="暂无工作经验"
              />
              <n-space v-else vertical :size="16">
                <n-card
                  v-for="(work, index) in resume.work_experience"
                  :key="index"
                  :bordered="false"
                  size="small"
                  class="item-card"
                >
                  <n-space vertical :size="8">
                    <n-text strong style="font-size: 16px">
                      {{ work.company || '未知公司' }}
                    </n-text>
                    <n-tag v-if="work.position" type="info">{{ work.position }}</n-tag>
                    <n-text v-if="work.start_date || work.end_date" depth="3">
                      {{ work.start_date || '?' }} - {{ work.end_date || '至今' }}
                    </n-text>
                    <n-text v-if="work.description">{{ work.description }}</n-text>
                    <div v-if="work.responsibilities && work.responsibilities.length > 0">
                      <n-text strong>工作职责:</n-text>
                      <ul style="margin: 8px 0; padding-left: 20px">
                        <li v-for="(resp, i) in work.responsibilities" :key="i">
                          {{ resp }}
                        </li>
                      </ul>
                    </div>
                  </n-space>
                </n-card>
              </n-space>
            </n-tab-pane>

            <!-- 项目经历 -->
            <n-tab-pane name="projects" tab="🚀 项目经历">
              <n-empty
                v-if="!resume.projects || resume.projects.length === 0"
                description="暂无项目经历"
              />
              <n-space v-else vertical :size="16">
                <n-card
                  v-for="(project, index) in resume.projects"
                  :key="index"
                  :bordered="false"
                  size="small"
                  class="item-card"
                >
                  <n-space vertical :size="8">
                    <n-text strong style="font-size: 16px">
                      {{ project.name || '未命名项目' }}
                    </n-text>
                    <n-space :size="8">
                      <n-tag v-if="project.role" type="info">{{ project.role }}</n-tag>
                    </n-space>
                    <n-text v-if="project.start_date || project.end_date" depth="3">
                      {{ project.start_date || '?' }} - {{ project.end_date || '至今' }}
                    </n-text>
                    <n-text v-if="project.description">{{ project.description }}</n-text>
                    <div v-if="project.technologies && project.technologies.length > 0">
                      <n-text strong>技术栈:</n-text>
                      <n-space :size="8" style="margin-top: 8px">
                        <n-tag
                          v-for="(tech, i) in project.technologies"
                          :key="i"
                          size="small"
                          type="success"
                        >
                          {{ tech }}
                        </n-tag>
                      </n-space>
                    </div>
                  </n-space>
                </n-card>
              </n-space>
            </n-tab-pane>

            <!-- 技能清单 -->
            <n-tab-pane name="skills" tab="⚡ 技能清单">
              <n-empty
                v-if="!resume.skills || resume.skills.length === 0"
                description="暂无技能信息"
              />
              <n-space v-else :size="12">
                <n-tag
                  v-for="(skill, index) in resume.skills"
                  :key="index"
                  type="info"
                  size="large"
                >
                  {{ skill }}
                </n-tag>
              </n-space>
            </n-tab-pane>

            <!-- 证书与奖项 -->
            <n-tab-pane name="extra" tab="🏆 证书与奖项">
              <n-space vertical :size="16">
                <!-- 证书 -->
                <div v-if="resume.certifications && resume.certifications.length > 0">
                  <n-text strong style="font-size: 16px">📜 证书</n-text>
                  <n-list bordered style="margin-top: 12px">
                    <n-list-item v-for="(cert, index) in resume.certifications" :key="index">
                      {{ cert }}
                    </n-list-item>
                  </n-list>
                </div>

                <!-- 奖项 -->
                <div v-if="resume.awards && resume.awards.length > 0">
                  <n-text strong style="font-size: 16px">🏅 奖项</n-text>
                  <n-list bordered style="margin-top: 12px">
                    <n-list-item v-for="(award, index) in resume.awards" :key="index">
                      {{ award }}
                    </n-list-item>
                  </n-list>
                </div>

                <n-empty
                  v-if="
                    (!resume.certifications || resume.certifications.length === 0) &&
                    (!resume.awards || resume.awards.length === 0)
                  "
                  description="暂无证书与奖项"
                />
              </n-space>
            </n-tab-pane>
          </n-tabs>
        </n-card>

        <!-- 原始文本 -->
        <n-card v-if="resume.markdown_text" title="📝 原始文本" :bordered="false">
          <n-collapse>
            <n-collapse-item title="点击展开/收起 Markdown 原文" name="markdown">
              <n-code 
                :code="resume.markdown_text" 
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
        <n-button type="primary" @click="handleBatchAnalysis">
          批量分析
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
  NButton
} from 'naive-ui'
import { getResumeDetail, type ResumeDetail } from '@/api/history'

const props = defineProps<{
  resumeId: string | null
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
}>()

const router = useRouter()
const message = useMessage()

const visible = ref(false)
const loading = ref(false)
const resume = ref<ResumeDetail | null>(null)

// 监听 show 变化
watch(
  () => props.show,
  (newVal) => {
    visible.value = newVal
    if (newVal && props.resumeId) {
      loadResumeDetail()
    }
  }
)

// 监听 visible 变化
watch(visible, (newVal) => {
  emit('update:show', newVal)
})

// 加载简历详情
async function loadResumeDetail() {
  if (!props.resumeId) return

  loading.value = true
  try {
    resume.value = await getResumeDetail(props.resumeId)
  } catch (error) {
    console.error('加载简历详情失败:', error)
    message.error('加载简历详情失败')
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

// 批量分析
function handleBatchAnalysis() {
  if (!props.resumeId) return
  router.push({
    path: '/batch-analysis',
    query: { resume_id: props.resumeId }
  })
  handleClose()
}

// 关闭弹窗
function handleClose() {
  visible.value = false
  resume.value = null
}
</script>

<style scoped>
.resume-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card,
.detail-card {
  background: var(--n-color);
}

.item-card {
  background: var(--n-color-target);
  border: 1px solid var(--n-border-color);
}
</style>
