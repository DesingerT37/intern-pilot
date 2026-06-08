<template>
  <n-modal
    v-model:show="showModal"
    preset="card"
    title="📋 历史爬取任务"
    style="width: 800px; max-width: 90vw"
    :bordered="false"
    :segmented="{
      content: true,
      footer: 'soft'
    }"
  >
    <n-space vertical :size="16">
      <!-- 筛选器 -->
      <n-space align="center">
        <n-text>状态筛选：</n-text>
        <n-select
          v-model:value="statusFilter"
          :options="statusOptions"
          style="width: 150px"
          @update:value="loadHistory"
        />
        <n-button @click="loadHistory" :loading="loading">
          <template #icon>
            <span>🔄</span>
          </template>
          刷新
        </n-button>
      </n-space>

      <!-- 任务列表 -->
      <n-spin :show="loading">
        <n-empty
          v-if="!loading && tasks.length === 0"
          description="暂无历史任务"
          style="padding: 40px 0"
        >
          <template #icon>
            <span style="font-size: 48px">📭</span>
          </template>
        </n-empty>

        <n-list v-else bordered>
          <n-list-item v-for="task in tasks" :key="task.task_id">
            <n-thing>
              <template #avatar>
                <n-avatar>
                  <span v-if="task.status === 'completed'">✅</span>
                  <span v-else-if="task.status === 'running'">⏳</span>
                  <span v-else-if="task.status === 'failed'">❌</span>
                  <span v-else>📋</span>
                </n-avatar>
              </template>

              <template #header>
                <n-space align="center">
                  <n-text strong>{{ task.keyword }}</n-text>
                  <n-tag
                    :type="getStatusType(task.status)"
                    size="small"
                  >
                    {{ getStatusText(task.status) }}
                  </n-tag>
                </n-space>
              </template>

              <template #description>
                <n-space vertical :size="4">
                  <n-text depth="3" style="font-size: 12px">
                    📍 {{ task.city || '全国' }} | 
                    📊 找到 {{ task.crawled_jobs }} 个职位 | 
                    🕐 {{ formatDate(task.created_at) }}
                  </n-text>
                </n-space>
              </template>

              <template #action>
                <n-space>
                  <n-button
                    v-if="task.status === 'completed' && task.crawled_jobs > 0"
                    type="primary"
                    size="small"
                    @click="handleSelectTask(task)"
                  >
                    选择此任务
                  </n-button>
                  <n-button
                    v-else
                    size="small"
                    disabled
                  >
                    不可用
                  </n-button>
                </n-space>
              </template>
            </n-thing>
          </n-list-item>
        </n-list>
      </n-spin>
    </n-space>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleClose">关闭</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NSpace, NText, NSelect, NButton, NSpin, NEmpty, NList, NListItem, NThing, NAvatar, NTag, useMessage } from 'naive-ui'
import { getTaskHistory, type TaskHistoryItem } from '@/api/batchAnalysis'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  'select': [task: TaskHistoryItem]
}>()

const message = useMessage()

const showModal = ref(props.show)
const loading = ref(false)
const tasks = ref<TaskHistoryItem[]>([])
const statusFilter = ref<string | null>(null)

const statusOptions = [
  { label: '全部', value: null },
  { label: '已完成', value: 'completed' },
  { label: '进行中', value: 'running' },
  { label: '失败', value: 'failed' }
]

watch(() => props.show, (val) => {
  showModal.value = val
  if (val) {
    loadHistory()
  }
})

watch(showModal, (val) => {
  emit('update:show', val)
})

async function loadHistory() {
  loading.value = true
  try {
    tasks.value = await getTaskHistory(statusFilter.value || undefined, 20)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载历史任务失败')
  } finally {
    loading.value = false
  }
}

function getStatusType(status: string) {
  switch (status) {
    case 'completed':
      return 'success'
    case 'running':
      return 'warning'
    case 'failed':
      return 'error'
    default:
      return 'default'
  }
}

function getStatusText(status: string) {
  switch (status) {
    case 'completed':
      return '已完成'
    case 'running':
      return '进行中'
    case 'failed':
      return '失败'
    case 'pending':
      return '等待中'
    default:
      return status
  }
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function handleSelectTask(task: TaskHistoryItem) {
  emit('select', task)
  handleClose()
}

function handleClose() {
  showModal.value = false
}
</script>

<style scoped>
.n-list-item {
  padding: 16px;
}
</style>
