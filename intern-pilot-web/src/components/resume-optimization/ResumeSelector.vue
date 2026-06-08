<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import {
  NCard,
  NInput,
  NList,
  NListItem,
  NThing,
  NTag,
  NEmpty,
  NSpin,
  NText,
  useMessage,
} from 'naive-ui'
import { getResumes, type ResumeListItem } from '@/api/resumeOptimization'
import { getApiErrorMessage } from '@/utils/apiError'

const props = defineProps<{
  selectedId?: string | null
  /** 嵌入弹窗时使用，去掉外层卡片 */
  embedded?: boolean
}>()

const emit = defineEmits<{
  select: [resume: ResumeListItem]
}>()

const message = useMessage()
const loading = ref(false)
const resumes = ref<ResumeListItem[]>([])
const search = ref('')
const filterParsed = ref<'all' | 'parsed' | 'unparsed'>('all')

const filteredResumes = computed(() => {
  let list = resumes.value
  if (filterParsed.value === 'parsed') list = list.filter((r) => r.parsed)
  if (filterParsed.value === 'unparsed') list = list.filter((r) => !r.parsed)
  const q = search.value.trim().toLowerCase()
  if (!q) return list
  return list.filter(
    (r) =>
      (r.name || '').toLowerCase().includes(q) ||
      (r.target_position || '').toLowerCase().includes(q) ||
      r.filename.toLowerCase().includes(q)
  )
})

const loadResumes = async () => {
  loading.value = true
  try {
    resumes.value = await getResumes()
  } catch (err) {
    message.error(getApiErrorMessage(err, '加载简历列表失败'))
  } finally {
    loading.value = false
  }
}

const formatDate = (s: string) => new Date(s).toLocaleString('zh-CN')

const handleSelect = (resume: ResumeListItem) => {
  emit('select', resume)
}

onMounted(loadResumes)

watch(
  () => props.selectedId,
  (id) => {
    if (id && resumes.value.length && !resumes.value.find((r) => r.resume_id === id)) {
      loadResumes()
    }
  }
)

defineExpose({ reload: loadResumes })
</script>

<template>
  <n-card
    v-if="!embedded"
    title="简历列表"
    size="small"
    :bordered="false"
    class="selector-card"
  >
    <n-input
      v-model:value="search"
      placeholder="搜索姓名、职位、文件名..."
      clearable
      size="small"
      style="margin-bottom: 8px"
    />
    <div class="filter-row">
      <n-tag
        :type="filterParsed === 'all' ? 'primary' : 'default'"
        size="small"
        style="cursor: pointer"
        @click="filterParsed = 'all'"
      >
        全部
      </n-tag>
      <n-tag
        :type="filterParsed === 'parsed' ? 'success' : 'default'"
        size="small"
        style="cursor: pointer"
        @click="filterParsed = 'parsed'"
      >
        已解析
      </n-tag>
      <n-tag
        :type="filterParsed === 'unparsed' ? 'warning' : 'default'"
        size="small"
        style="cursor: pointer"
        @click="filterParsed = 'unparsed'"
      >
        未解析
      </n-tag>
    </div>

    <n-spin :show="loading">
      <n-list v-if="filteredResumes.length" hoverable clickable class="resume-list">
        <n-list-item
          v-for="item in filteredResumes"
          :key="item.resume_id"
          :class="{ active: item.resume_id === selectedId }"
          @click="handleSelect(item)"
        >
          <n-thing>
            <template #header>
              <span class="resume-name">{{ item.name || item.filename }}</span>
            </template>
            <template #description>
              <n-text depth="3" style="font-size: 12px">
                {{ item.target_position || '未设置目标职位' }}
              </n-text>
            </template>
            <template #header-extra>
              <n-tag :type="item.parsed ? 'success' : 'warning'" size="small">
                {{ item.parsed ? '已解析' : '未解析' }}
              </n-tag>
            </template>
            <n-text depth="3" style="font-size: 11px">
              更新于 {{ formatDate(item.updated_at) }}
            </n-text>
          </n-thing>
        </n-list-item>
      </n-list>
      <n-empty v-else description="暂无简历" size="small" style="margin-top: 24px" />
    </n-spin>
  </n-card>

  <div v-else class="selector-embedded">
    <n-input
      v-model:value="search"
      placeholder="搜索姓名、职位、文件名..."
      clearable
      size="small"
      style="margin-bottom: 8px"
    />
    <div class="filter-row">
      <n-tag
        :type="filterParsed === 'all' ? 'primary' : 'default'"
        size="small"
        style="cursor: pointer"
        @click="filterParsed = 'all'"
      >
        全部
      </n-tag>
      <n-tag
        :type="filterParsed === 'parsed' ? 'success' : 'default'"
        size="small"
        style="cursor: pointer"
        @click="filterParsed = 'parsed'"
      >
        已解析
      </n-tag>
      <n-tag
        :type="filterParsed === 'unparsed' ? 'warning' : 'default'"
        size="small"
        style="cursor: pointer"
        @click="filterParsed = 'unparsed'"
      >
        未解析
      </n-tag>
    </div>

    <n-spin :show="loading">
      <n-list v-if="filteredResumes.length" hoverable clickable class="resume-list resume-list--modal">
        <n-list-item
          v-for="item in filteredResumes"
          :key="item.resume_id"
          :class="{ active: item.resume_id === selectedId }"
          @click="handleSelect(item)"
        >
          <n-thing>
            <template #header>
              <span class="resume-name">{{ item.name || item.filename }}</span>
            </template>
            <template #description>
              <n-text depth="3" style="font-size: 12px">
                {{ item.target_position || '未设置目标职位' }}
              </n-text>
            </template>
            <template #header-extra>
              <n-tag :type="item.parsed ? 'success' : 'warning'" size="small">
                {{ item.parsed ? '已解析' : '未解析' }}
              </n-tag>
            </template>
            <n-text depth="3" style="font-size: 11px">
              更新于 {{ formatDate(item.updated_at) }}
            </n-text>
          </n-thing>
        </n-list-item>
      </n-list>
      <n-empty v-else description="暂无简历" size="small" style="margin-top: 24px" />
    </n-spin>
  </div>
</template>

<style scoped>
.selector-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: none !important;
  box-shadow: none !important;
}
.selector-card :deep(.n-card__content) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.selector-embedded {
  display: flex;
  flex-direction: column;
}
.filter-row {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.resume-list {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}
.resume-list--modal {
  max-height: 420px;
}
.n-list-item.active {
  background: rgba(24, 160, 88, 0.08);
  border-radius: 6px;
}
.resume-name {
  font-weight: 600;
}
</style>
