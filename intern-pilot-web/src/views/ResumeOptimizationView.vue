<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage, NIcon, NButton, NText } from 'naive-ui'
import { getApiErrorMessage } from '@/utils/apiError'
import {
  ChevronBackOutline,
  ChevronForwardOutline,
  DocumentTextOutline,
} from '@vicons/ionicons5'
import ResumeSelectModal from '@/components/resume-optimization/ResumeSelectModal.vue'
import ResumeEditor from '@/components/resume-optimization/ResumeEditor.vue'
import SuggestionPanel from '@/components/resume-optimization/SuggestionPanel.vue'
import AIChatPanel from '@/components/resume-optimization/AIChatPanel.vue'
import { getResumeContent, type ResumeListItem } from '@/api/resumeOptimization'
import { useMatchStore } from '@/stores/match'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()
const matchStore = useMatchStore()

const selectedResumeId = ref<string | null>(null)
const selectedResumeLabel = ref('')
const resumeContent = ref('')
const loadingContent = ref(false)
const pendingChatMessage = ref('')
const showResumeModal = ref(false)

const suggestionsCollapsed = ref(false)
const chatCollapsed = ref(false)

const suggestionsWidth = ref(300)
const chatWidth = ref(360)

const resizing = ref<'suggestions' | 'chat' | null>(null)
const editorRef = ref<InstanceType<typeof ResumeEditor> | null>(null)
const suggestionPanelRef = ref<InstanceType<typeof SuggestionPanel> | null>(null)

const matchId = ref<string | null>((route.query.match_id as string) || matchStore.matchId || null)
const taskId = ref<string | null>((route.query.task_id as string) || null)

const suggestionsShellStyle = computed(() => ({
  width: suggestionsCollapsed.value ? '0px' : `${suggestionsWidth.value}px`,
}))

const chatShellStyle = computed(() => ({
  width: chatCollapsed.value ? '0px' : `${chatWidth.value}px`,
}))

const handleSelectResume = async (resume: ResumeListItem) => {
  selectedResumeId.value = resume.resume_id
  selectedResumeLabel.value = resume.name || resume.filename
  loadingContent.value = true
  try {
    const data = await getResumeContent(resume.resume_id)
    resumeContent.value = data.markdown_text || ''
  } catch (err) {
    message.error(getApiErrorMessage(err, '加载简历内容失败'))
  } finally {
    loadingContent.value = false
    await nextTick()
    suggestionPanelRef.value?.reload?.()
  }
}

const handleSendToAi = (text: string) => {
  pendingChatMessage.value = text
  chatCollapsed.value = false
}

const handleInsertTemplate = (text: string) => {
  editorRef.value?.insertAtCursor(text)
  message.success('模板已插入')
}

const handleApplySection = (text: string) => {
  editorRef.value?.insertAtCursor(text)
  message.success('内容已插入编辑器')
}

const handleFormatContent = (text: string) => {
  editorRef.value?.setContent(text)
}

const onMouseMove = (e: MouseEvent) => {
  if (!resizing.value) return
  if (resizing.value === 'suggestions' && !suggestionsCollapsed.value) {
    suggestionsWidth.value = Math.min(480, Math.max(220, e.clientX - 56))
  } else if (resizing.value === 'chat' && !chatCollapsed.value) {
    chatWidth.value = Math.min(560, Math.max(280, window.innerWidth - e.clientX - 56))
  }
}

const onMouseUp = () => {
  resizing.value = null
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    message.warning('请先登录')
    router.push('/login')
    return
  }
  if (route.query.match_id) matchId.value = route.query.match_id as string
  if (route.query.task_id) taskId.value = route.query.task_id as string
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
})

watch(
  () => route.query.match_id,
  (id) => {
    if (id) matchId.value = id as string
  }
)
</script>

<template>
  <div class="ro-page">
    <header class="ro-toolbar">
      <div class="ro-toolbar-spacer" aria-hidden="true" />
      <h2 class="ro-title">简历优化 Agent</h2>
      <div class="ro-toolbar-actions">
        <n-text v-if="selectedResumeLabel" depth="3" class="ro-current-resume">
          当前：{{ selectedResumeLabel }}
        </n-text>
        <n-button size="small" @click="showResumeModal = true">
          <template #icon>
            <n-icon><DocumentTextOutline /></n-icon>
          </template>
          选择简历
        </n-button>
      </div>
    </header>

    <ResumeSelectModal
      v-model:show="showResumeModal"
      :selected-id="selectedResumeId"
      @select="handleSelectResume"
    />

    <div class="ro-workspace">
      <!-- 左侧：优化建议 -->
      <div class="ro-side ro-side--left">
        <button
          type="button"
          class="ro-panel-toggle ro-panel-toggle--left"
          :title="suggestionsCollapsed ? '展开优化建议' : '收起优化建议'"
          @click="suggestionsCollapsed = !suggestionsCollapsed"
        >
          <n-icon size="18">
            <ChevronBackOutline v-if="!suggestionsCollapsed" />
            <ChevronForwardOutline v-else />
          </n-icon>
          <span class="ro-toggle-text">{{ suggestionsCollapsed ? '建议' : '收起' }}</span>
        </button>

        <div
          class="ro-panel-shell ro-panel-shell--left"
          :class="{ 'is-collapsed': suggestionsCollapsed }"
          :style="suggestionsShellStyle"
        >
          <aside class="ro-panel ro-left">
            <SuggestionPanel
              ref="suggestionPanelRef"
              :resume-id="selectedResumeId"
              :match-id="matchId"
              :task-id="taskId"
              :editor-content="resumeContent"
              @send-to-ai="handleSendToAi"
              @insert-template="handleInsertTemplate"
              @format-content="handleFormatContent"
            />
          </aside>
          <div
            class="ro-resizer ro-resizer-v"
            :class="{ 'is-hidden': suggestionsCollapsed }"
            @mousedown="resizing = 'suggestions'"
          />
        </div>
      </div>

      <!-- 中间：编辑器（全高） -->
      <div class="ro-center-column">
        <div class="ro-center-editor">
          <ResumeEditor
            ref="editorRef"
            v-model="resumeContent"
            :resume-id="selectedResumeId"
            :loading="loadingContent"
          />
        </div>
      </div>

      <!-- 右侧：AI 对话（类似 Cursor） -->
      <div class="ro-side ro-side--right">
        <div
          class="ro-panel-shell ro-panel-shell--right"
          :class="{ 'is-collapsed': chatCollapsed }"
          :style="chatShellStyle"
        >
          <div
            class="ro-resizer ro-resizer-v"
            :class="{ 'is-hidden': chatCollapsed }"
            @mousedown="resizing = 'chat'"
          />
          <aside class="ro-panel ro-right">
            <AIChatPanel
              :resume-id="selectedResumeId"
              :resume-content="resumeContent"
              v-model:pending-message="pendingChatMessage"
              @apply-section="handleApplySection"
            />
          </aside>
        </div>

        <button
          type="button"
          class="ro-panel-toggle ro-panel-toggle--right"
          :title="chatCollapsed ? '展开 AI 对话' : '收起 AI 对话'"
          @click="chatCollapsed = !chatCollapsed"
        >
          <span class="ro-toggle-text">{{ chatCollapsed ? 'AI' : '收起' }}</span>
          <n-icon size="18">
            <ChevronForwardOutline v-if="!chatCollapsed" />
            <ChevronBackOutline v-else />
          </n-icon>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ro-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px - 64px - 48px);
  max-height: calc(100vh - 64px - 64px - 48px);
  box-sizing: border-box;
  overflow: hidden;
}

.ro-toolbar {
  flex-shrink: 0;
  margin: 0 0 12px;
  padding: 0;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
}

.ro-toolbar-spacer {
  grid-column: 1;
}

.ro-title {
  grid-column: 2;
  margin: 0;
  padding: 0;
  line-height: 1.4;
  font-size: 20px;
  font-weight: 600;
  color: var(--n-text-color);
  text-align: center;
  justify-self: center;
}

.ro-toolbar-actions {
  grid-column: 3;
  justify-self: end;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.ro-current-resume {
  font-size: 13px;
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ro-workspace {
  display: flex;
  flex: 1;
  min-height: 0;
  gap: 0;
  align-items: stretch;
}

.ro-side {
  display: flex;
  flex-shrink: 0;
  align-items: stretch;
  min-height: 0;
  height: 100%;
  align-self: stretch;
}

.ro-side--left {
  flex-direction: row;
}

.ro-side--right {
  flex-direction: row;
}

.ro-panel-toggle {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 36px;
  flex-shrink: 0;
  border: 1px solid var(--n-border-color);
  background: var(--n-color);
  color: var(--n-text-color-2);
  cursor: pointer;
  transition:
    background 0.2s ease,
    color 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
  padding: 8px 4px;
  z-index: 2;
}

.ro-panel-toggle:hover {
  background: rgba(24, 160, 88, 0.08);
  color: #18a058;
  border-color: rgba(24, 160, 88, 0.35);
}

.ro-panel-toggle--left {
  border-radius: 8px 0 0 8px;
  border-right: none;
}

.ro-panel-toggle--right {
  border-radius: 0 8px 8px 0;
  border-left: none;
  flex-direction: column;
}

.ro-toggle-text {
  font-size: 11px;
  writing-mode: vertical-rl;
  letter-spacing: 2px;
  user-select: none;
}

.ro-panel-shell {
  display: flex;
  overflow: hidden;
  flex-shrink: 0;
  min-width: 0;
  min-height: 0;
  align-self: stretch;
  opacity: 1;
  transition:
    width 0.32s cubic-bezier(0.4, 0, 0.2, 1),
    opacity 0.26s ease,
    margin 0.32s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: width, opacity;
}

.ro-panel-shell.is-collapsed {
  opacity: 0;
  pointer-events: none;
  margin: 0 !important;
}

.ro-panel-shell--left {
  flex-direction: row;
  margin-right: 0;
}

.ro-panel-shell--right {
  flex-direction: row;
  margin-left: 0;
}

.ro-panel {
  flex: 1;
  min-width: 0;
  min-height: 0;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--n-border-color);
  background: var(--n-color);
  transition: border-color 0.32s ease;
}

.ro-panel.ro-left > *,
.ro-panel.ro-right > * {
  flex: 1;
  min-height: 0;
  height: 100%;
  overflow: hidden;
}

.ro-panel-shell--left .ro-panel {
  border-radius: 0 8px 8px 0;
  border-left: none;
}

.ro-panel-shell--right .ro-panel {
  border-radius: 8px 0 0 8px;
  border-right: none;
}

.ro-panel-shell.is-collapsed .ro-panel {
  border-color: transparent;
}

.ro-center-column {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  min-height: 0;
  margin: 0 6px;
}

.ro-center-editor {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 12px;
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  background: var(--n-color-modal);
}

.ro-center-editor .editor-shell {
  height: 100%;
  min-height: 0;
}

.ro-resizer {
  flex-shrink: 0;
  transition:
    width 0.32s cubic-bezier(0.4, 0, 0.2, 1),
    opacity 0.2s ease,
    background 0.15s ease;
}

.ro-resizer-v {
  width: 6px;
  cursor: col-resize;
}

.ro-resizer:hover:not(.is-hidden) {
  background: rgba(24, 160, 88, 0.22);
}

.ro-resizer.is-hidden {
  width: 0 !important;
  opacity: 0;
  pointer-events: none;
  overflow: hidden;
}

.ro-page:has(.ro-resizer:active) .ro-panel-shell {
  transition: none !important;
}
</style>
