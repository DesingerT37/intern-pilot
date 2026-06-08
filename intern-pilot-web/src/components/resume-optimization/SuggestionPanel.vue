<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  NTabs,
  NTabPane,
  NButton,
  NTag,
  NEmpty,
  NSpin,
  NSelect,
  NText,
  NSpace,
  NDivider,
  NAlert,
  useMessage,
} from 'naive-ui'
import SuggestionItemCard from './SuggestionItemCard.vue'
import {
  getMatchSuggestions,
  getBatchSuggestions,
  listResumeMatchAnalyses,
  listResumeBatchAnalyses,
  type Suggestion,
  type MatchSuggestionResponse,
  type BatchSuggestionResponse,
} from '@/api/resumeOptimization'
import { getApiErrorMessage } from '@/utils/apiError'
import { applyFormatAction, type FormatAction } from '@/utils/markdownFormat'

const props = defineProps<{
  resumeId?: string | null
  matchId?: string | null
  taskId?: string | null
  editorContent?: string
}>()

const emit = defineEmits<{
  sendToAi: [text: string]
  insertTemplate: [text: string]
  formatContent: [content: string]
}>()

const message = useMessage()
const activeTab = ref<'match' | 'batch' | 'quick'>('match')
const categoryFilter = ref<string | null>(null)
const loadingMatch = ref(false)
const loadingBatch = ref(false)
const loadingLists = ref(false)
const matchData = ref<MatchSuggestionResponse | null>(null)
const batchData = ref<BatchSuggestionResponse | null>(null)
const matchRecords = ref<Awaited<ReturnType<typeof listResumeMatchAnalyses>>>([])
const batchRecords = ref<Awaited<ReturnType<typeof listResumeBatchAnalyses>>>([])
const selectedMatchId = ref<string | null>(null)
const selectedTaskId = ref<string | null>(null)
const listError = ref('')

const categoryOptions = [
  { label: '全部分类', value: '' },
  { label: '技能', value: 'skill' },
  { label: '项目', value: 'project' },
  { label: '描述', value: 'description' },
  { label: '格式', value: 'format' },
]

const templates = [
  { title: '教育经历', content: '## 教育经历\n\n### 学校 - 专业 (年份)\n- 主修课程...\n' },
  { title: '工作经验', content: '## 工作经验\n\n### 公司 - 职位 (年份)\n- 职责与成果...\n' },
  { title: '项目经历', content: '## 项目经历\n\n### 项目名 (年份)\n- 技术栈 / 成果...\n' },
  { title: '技能', content: '## 技能\n\n- **语言**: ...\n- **框架**: ...\n' },
]

const formatDate = (iso: string) => {
  try {
    return new Date(iso).toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

const matchSelectOptions = computed(() =>
  matchRecords.value.map((m) => ({
    label: `${m.job_label} · ${m.overall_score.toFixed(0)}分 · ${m.suggestion_count}条 · ${formatDate(m.created_at)}`,
    value: m.match_id,
  }))
)

const batchSelectOptions = computed(() =>
  batchRecords.value.map((b) => {
    const st =
      b.status === 'completed' ? '已完成' : b.status === 'running' ? '进行中' : b.status
    return {
      label: `${b.keyword} · ${st} · ${b.total_jobs}职位 · ${b.suggestion_count}条 · ${formatDate(b.created_at)}`,
      value: b.task_id,
    }
  })
)

const filterSuggestions = (list: Suggestion[]) => {
  const sorted = [...list].sort((a, b) => a.priority - b.priority)
  if (!categoryFilter.value) return sorted
  return sorted.filter((s) => s.category === categoryFilter.value)
}

const matchSuggestions = computed(() =>
  matchData.value ? filterSuggestions(matchData.value.suggestions) : []
)

const batchSuggestions = computed(() =>
  batchData.value ? filterSuggestions(batchData.value.priority_suggestions) : []
)

const loadMatchSuggestions = async (matchId?: string | null) => {
  const id = matchId ?? selectedMatchId.value
  if (!id) return
  loadingMatch.value = true
  matchData.value = null
  try {
    matchData.value = await getMatchSuggestions(id)
    selectedMatchId.value = id
  } catch (err) {
    message.error(getApiErrorMessage(err, '加载 JD 匹配建议失败'))
  } finally {
    loadingMatch.value = false
  }
}

const loadBatchSuggestions = async (taskId?: string | null) => {
  const id = taskId ?? selectedTaskId.value
  if (!id) return
  loadingBatch.value = true
  batchData.value = null
  try {
    batchData.value = await getBatchSuggestions(id)
    selectedTaskId.value = id
  } catch (err) {
    message.error(getApiErrorMessage(err, '加载批量分析建议失败'))
  } finally {
    loadingBatch.value = false
  }
}

const onMatchSelect = (id: string | null) => {
  selectedMatchId.value = id
  if (id) loadMatchSuggestions(id)
  else matchData.value = null
}

const onBatchSelect = (id: string | null) => {
  selectedTaskId.value = id
  if (id) loadBatchSuggestions(id)
  else batchData.value = null
}

const fetchAnalysisLists = async () => {
  listError.value = ''
  if (!props.resumeId) {
    matchRecords.value = []
    batchRecords.value = []
    selectedMatchId.value = null
    selectedTaskId.value = null
    matchData.value = null
    batchData.value = null
    return
  }

  loadingLists.value = true
  try {
    const [matches, batches] = await Promise.all([
      listResumeMatchAnalyses(props.resumeId),
      listResumeBatchAnalyses(props.resumeId),
    ])
    matchRecords.value = matches
    batchRecords.value = batches

    const matchPick =
      (props.matchId && matches.some((m) => m.match_id === props.matchId)
        ? props.matchId
        : matches[0]?.match_id) ?? null

    const batchPick =
      (props.taskId && batches.some((b) => b.task_id === props.taskId)
        ? props.taskId
        : batches.find((b) => b.status === 'completed')?.task_id ??
          batches[0]?.task_id) ??
      null

    selectedMatchId.value = matchPick
    selectedTaskId.value = batchPick

    if (matchPick) await loadMatchSuggestions(matchPick)
    else matchData.value = null

    if (batchPick) await loadBatchSuggestions(batchPick)
    else batchData.value = null
  } catch (err) {
    listError.value = getApiErrorMessage(err, '加载分析记录失败')
    message.error(listError.value)
  } finally {
    loadingLists.value = false
  }
}

watch(() => props.resumeId, fetchAnalysisLists, { immediate: true })

watch(activeTab, (tab) => {
  if (tab === 'batch' && selectedTaskId.value && !batchData.value && !loadingBatch.value) {
    loadBatchSuggestions(selectedTaskId.value)
  }
  if (tab === 'match' && selectedMatchId.value && !matchData.value && !loadingMatch.value) {
    loadMatchSuggestions(selectedMatchId.value)
  }
})

const formatOneSuggestion = (s: Suggestion) => {
  let text = `【${s.title}】\n${s.description}`
  if (s.example) text += `\n\n示例：\n${s.example}`
  return text
}

const copyOne = async (s: Suggestion) => {
  try {
    await navigator.clipboard.writeText(formatOneSuggestion(s))
    message.success(`已复制：${s.title}`)
  } catch {
    message.error('复制失败')
  }
}

const sendOneToAi = (s: Suggestion, source: string) => {
  emit(
    'sendToAi',
    `【${source}】请仅根据下面这一条建议优化简历（不要一次处理多条）：\n\n${formatOneSuggestion(s)}`
  )
  message.success('已发送本条给 AI')
}

const runFormat = (action: FormatAction) => {
  const source = props.editorContent ?? ''
  if (!source.trim()) {
    message.warning('编辑器内容为空')
    return
  }
  emit('formatContent', applyFormatAction(source, action))
  message.success('格式化完成')
}

defineExpose({ reload: fetchAnalysisLists })
</script>

<template>
  <div class="suggestion-root">
    <n-alert v-if="!resumeId" type="info" :show-icon="false" class="top-alert">
      请先在右上角选择简历
    </n-alert>
    <n-alert v-else-if="listError" type="error" :show-icon="false" class="top-alert">
      {{ listError }}
    </n-alert>

    <n-tabs v-model:value="activeTab" type="line" size="small" class="suggestion-tabs">
      <n-tab-pane name="match" tab="JD匹配建议">
        <div class="tab-layout">
          <div class="tab-toolbar">
            <n-select
              v-model:value="selectedMatchId"
              :options="matchSelectOptions"
              :placeholder="resumeId ? '选择 JD 匹配记录' : '请先选择简历'"
              size="small"
              clearable
              :disabled="!resumeId || !matchRecords.length"
              :loading="loadingLists"
              @update:value="onMatchSelect"
            />
            <n-select
              v-model:value="categoryFilter"
              :options="categoryOptions"
              placeholder="分类筛选"
              size="small"
              clearable
              style="margin-top: 8px"
            />
          </div>

          <n-spin :show="loadingMatch" class="list-spin">
            <div class="suggestion-list-scroll">
              <n-empty
                v-if="resumeId && !matchRecords.length && !loadingLists"
                size="small"
                description="暂无 JD 匹配记录"
              />
              <template v-else>
                <div v-if="matchData" class="summary-row">
                  <n-text strong>{{ matchData.job_name }}</n-text>
                  <n-tag size="small" type="info">{{ matchData.overall_score.toFixed(0) }} 分</n-tag>
                  <n-text depth="3" style="font-size: 12px">共 {{ matchSuggestions.length }} 条</n-text>
                </div>
                <SuggestionItemCard
                  v-for="(s, i) in matchSuggestions"
                  :key="'m-' + i + '-' + s.title"
                  :suggestion="s"
                  source-label="JD匹配"
                  source-type="info"
                  @send-to-ai="(item) => sendOneToAi(item, 'JD匹配分析')"
                  @copy="copyOne"
                />
                <n-empty
                  v-if="matchData && !matchSuggestions.length && !loadingMatch"
                  size="small"
                  description="该记录暂无结构化建议"
                />
              </template>
            </div>
          </n-spin>
        </div>
      </n-tab-pane>

      <n-tab-pane name="batch" tab="批量分析建议">
        <div class="tab-layout">
          <div class="tab-toolbar">
            <n-select
              v-model:value="selectedTaskId"
              :options="batchSelectOptions"
              :placeholder="resumeId ? '选择批量分析记录' : '请先选择简历'"
              size="small"
              clearable
              :disabled="!resumeId || !batchRecords.length"
              :loading="loadingLists"
              @update:value="onBatchSelect"
            />
            <n-select
              v-model:value="categoryFilter"
              :options="categoryOptions"
              placeholder="分类筛选"
              size="small"
              clearable
              style="margin-top: 8px"
            />
          </div>

          <n-spin :show="loadingBatch" class="list-spin">
            <div class="suggestion-list-scroll">
              <n-empty
                v-if="resumeId && !batchRecords.length && !loadingLists"
                size="small"
                description="暂无批量分析记录"
              />
              <template v-else>
                <div v-if="batchData" class="summary-row">
                  <n-text strong>{{ batchData.keyword }}</n-text>
                  <n-tag size="small" type="warning">{{ batchData.total_jobs }} 职位</n-tag>
                  <n-text depth="3" style="font-size: 12px">共 {{ batchSuggestions.length }} 条</n-text>
                </div>
                <SuggestionItemCard
                  v-for="(s, i) in batchSuggestions"
                  :key="'b-' + i + '-' + s.title"
                  :suggestion="s"
                  source-label="批量分析"
                  source-type="warning"
                  @send-to-ai="(item) => sendOneToAi(item, '批量分析')"
                  @copy="copyOne"
                />
                <n-empty
                  v-if="batchData && !batchSuggestions.length && !loadingBatch"
                  size="small"
                  description="该记录暂无结构化建议"
                />
              </template>
            </div>
          </n-spin>
        </div>
      </n-tab-pane>

      <n-tab-pane name="quick" tab="快速操作">
        <div class="tab-layout">
          <div class="suggestion-list-scroll">
            <n-text depth="3" style="font-size: 12px; display: block; margin-bottom: 8px">段落模板</n-text>
            <n-space vertical :size="8">
              <div v-for="tpl in templates" :key="tpl.title" class="quick-row">
                <n-text>{{ tpl.title }}</n-text>
                <n-button size="tiny" type="primary" @click="emit('insertTemplate', tpl.content)">
                  插入
                </n-button>
              </div>
            </n-space>
            <n-divider />
            <n-space vertical :size="6">
              <n-button size="small" block @click="runFormat('lists')">统一列表符号</n-button>
              <n-button size="small" block @click="runFormat('headings')">规范标题层级</n-button>
              <n-button size="small" block @click="runFormat('whitespace')">清理空行</n-button>
              <n-button size="small" block type="primary" @click="runFormat('all')">一键全部格式化</n-button>
            </n-space>
          </div>
        </div>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<style scoped>
.suggestion-root {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 8px 10px 10px;
  box-sizing: border-box;
}

.top-alert {
  flex-shrink: 0;
  margin-bottom: 8px;
}

.suggestion-tabs {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Naive Tabs 内部 flex 链 */
.suggestion-tabs :deep(.n-tabs-nav) {
  flex-shrink: 0;
}

.suggestion-tabs :deep(.n-tabs-pane-wrapper) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.suggestion-tabs :deep(.n-tab-pane) {
  height: 100%;
  overflow: hidden;
}

.tab-layout {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-top: 8px;
  box-sizing: border-box;
}

.tab-toolbar {
  flex-shrink: 0;
  margin-bottom: 8px;
}

.list-spin {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.list-spin :deep(.n-spin-container),
.list-spin :deep(.n-spin-content) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 可滚动的建议列表 */
.suggestion-list-scroll {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 4px 4px 12px 0;
  box-sizing: border-box;
}

.summary-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--n-border-color);
}

.quick-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border: 1px solid var(--n-border-color);
  border-radius: 6px;
  background: #fff;
}
</style>

<!-- 让 Naive Tabs 根节点参与 flex（非 scoped） -->
<style>
.ro-panel.ro-right .suggestion-tabs.n-tabs {
  height: 100%;
  min-height: 0;
}

.ro-panel.ro-right .suggestion-tabs > .n-tabs-pane-wrapper {
  flex: 1 1 auto !important;
  min-height: 0 !important;
  height: auto !important;
  overflow: hidden !important;
}
</style>
