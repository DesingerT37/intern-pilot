<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    title="💼 岗位详情"
    :style="{ width: '80%', maxWidth: '1200px' }"
    :segmented="{ content: 'soft' }"
    @after-leave="handleClose"
  >
    <n-spin :show="loading">
      <div v-if="jd" class="jd-detail">
        <!-- 基本信息卡片 -->
        <n-card title="🏢 基本信息" :bordered="false" class="info-card">
          <n-descriptions :column="2" label-placement="left">
            <n-descriptions-item label="公司">
              <n-text strong>{{ jd.company || '未填写' }}</n-text>
            </n-descriptions-item>
            <n-descriptions-item label="职位">
              <n-text strong>{{ jd.position || '未填写' }}</n-text>
            </n-descriptions-item>
            <n-descriptions-item label="工作地点">
              <n-text>{{ jd.location || '未填写' }}</n-text>
            </n-descriptions-item>
            <n-descriptions-item label="薪资范围">
              <n-tag v-if="jd.salary_range" type="success">
                {{ jd.salary_range }}
              </n-tag>
              <n-text v-else depth="3">未填写</n-text>
            </n-descriptions-item>
            <n-descriptions-item label="添加时间" :span="2">
              <n-text>{{ formatDate(jd.created_at) }}</n-text>
            </n-descriptions-item>
          </n-descriptions>
        </n-card>

        <!-- 详细信息 Tabs -->
        <n-card title="📋 详细信息" :bordered="false" class="detail-card">
          <n-tabs type="line" animated>
            <!-- 岗位职责 -->
            <n-tab-pane name="responsibilities" tab="📝 岗位职责">
              <n-empty
                v-if="!jd.responsibilities || jd.responsibilities.length === 0"
                description="暂无岗位职责"
              />
              <n-list v-else bordered>
                <n-list-item v-for="(item, index) in jd.responsibilities" :key="index">
                  <template #prefix>
                    <n-text strong>{{ index + 1 }}.</n-text>
                  </template>
                  {{ item }}
                </n-list-item>
              </n-list>
            </n-tab-pane>

            <!-- 任职要求 -->
            <n-tab-pane name="requirements" tab="✅ 任职要求">
              <n-empty
                v-if="!jd.requirements || jd.requirements.length === 0"
                description="暂无任职要求"
              />
              <n-list v-else bordered>
                <n-list-item v-for="(item, index) in jd.requirements" :key="index">
                  <template #prefix>
                    <n-text strong>{{ index + 1 }}.</n-text>
                  </template>
                  {{ item }}
                </n-list-item>
              </n-list>
            </n-tab-pane>

            <!-- 技能要求 -->
            <n-tab-pane name="skills" tab="⚡ 技能要求">
              <n-space vertical :size="16">
                <!-- 必备技能 -->
                <div v-if="jd.required_skills && jd.required_skills.length > 0">
                  <n-text strong style="font-size: 16px">🔴 必备技能</n-text>
                  <n-space :size="12" style="margin-top: 12px">
                    <n-tag
                      v-for="(skill, index) in jd.required_skills"
                      :key="index"
                      type="error"
                      size="large"
                    >
                      {{ skill }}
                    </n-tag>
                  </n-space>
                </div>

                <!-- 优先技能 -->
                <div v-if="jd.preferred_skills && jd.preferred_skills.length > 0">
                  <n-text strong style="font-size: 16px">🟡 优先技能</n-text>
                  <n-space :size="12" style="margin-top: 12px">
                    <n-tag
                      v-for="(skill, index) in jd.preferred_skills"
                      :key="index"
                      type="warning"
                      size="large"
                    >
                      {{ skill }}
                    </n-tag>
                  </n-space>
                </div>

                <n-empty
                  v-if="
                    (!jd.required_skills || jd.required_skills.length === 0) &&
                    (!jd.preferred_skills || jd.preferred_skills.length === 0)
                  "
                  description="暂无技能要求"
                />
              </n-space>
            </n-tab-pane>

            <!-- 福利待遇 -->
            <n-tab-pane name="benefits" tab="🎁 福利待遇">
              <n-empty
                v-if="!jd.benefits || jd.benefits.length === 0"
                description="暂无福利待遇"
              />
              <n-space v-else :size="12">
                <n-tag
                  v-for="(benefit, index) in jd.benefits"
                  :key="index"
                  type="success"
                  size="large"
                >
                  {{ benefit }}
                </n-tag>
              </n-space>
            </n-tab-pane>
          </n-tabs>
        </n-card>

        <!-- 关键词 -->
        <n-card v-if="jd.keywords && jd.keywords.length > 0" title="🔑 关键词" :bordered="false">
          <n-space :size="12">
            <n-tag
              v-for="(keyword, index) in jd.keywords"
              :key="index"
              type="info"
              size="medium"
            >
              {{ keyword }}
            </n-tag>
          </n-space>
        </n-card>

        <!-- 原始文本 -->
        <n-card v-if="jd.raw_text" title="📝 原始文本" :bordered="false">
          <n-collapse>
            <n-collapse-item title="点击展开/收起原始JD文本" name="raw">
              <n-code 
                :code="jd.raw_text" 
                language="text" 
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
        <n-button type="primary" @click="handleStartAnalysis">
          开始匹配分析
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
import { getJDDetail, type JDDetail } from '@/api/history'

const props = defineProps<{
  jdId: string | null
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
}>()

const router = useRouter()
const message = useMessage()

const visible = ref(false)
const loading = ref(false)
const jd = ref<JDDetail | null>(null)

// 监听 show 变化
watch(
  () => props.show,
  (newVal) => {
    visible.value = newVal
    if (newVal && props.jdId) {
      loadJDDetail()
    }
  }
)

// 监听 visible 变化
watch(visible, (newVal) => {
  emit('update:show', newVal)
})

// 加载JD详情
async function loadJDDetail() {
  if (!props.jdId) return

  loading.value = true
  try {
    jd.value = await getJDDetail(props.jdId)
  } catch (error) {
    console.error('加载JD详情失败:', error)
    message.error('加载JD详情失败')
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

// 开始匹配分析
function handleStartAnalysis() {
  if (!props.jdId) return
  router.push({
    path: '/analysis',
    query: { jd_id: props.jdId }
  })
  handleClose()
}

// 关闭弹窗
function handleClose() {
  visible.value = false
  jd.value = null
}
</script>

<style scoped>
.jd-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card,
.detail-card {
  background: var(--n-color);
}
</style>
