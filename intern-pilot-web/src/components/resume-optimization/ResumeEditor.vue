<script setup lang="ts">
import { ref, watch, computed, defineAsyncComponent } from 'vue'
import { MdEditor, MdPreview } from 'md-editor-v3'
import {
  NButton,
  NSpace,
  NRadioGroup,
  NRadioButton,
  useMessage,
} from 'naive-ui'
import { updateResumeContent } from '@/api/resumeOptimization'
import { getApiErrorMessage } from '@/utils/apiError'

const VersionHistoryModal = defineAsyncComponent(
  () => import('./VersionHistoryModal.vue')
)
const ExportDialog = defineAsyncComponent(() => import('./ExportDialog.vue'))

const props = defineProps<{
  resumeId: string | null
  modelValue: string
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  saved: []
}>()

const message = useMessage()
const content = ref(props.modelValue)
const displayMode = ref<'edit' | 'preview' | 'split'>('edit')
const saving = ref(false)
const showVersionModal = ref(false)
const showExportModal = ref(false)
const editorRef = ref<InstanceType<typeof MdEditor> | null>(null)

const canEdit = computed(() => !!props.resumeId)

watch(
  () => props.modelValue,
  (v) => {
    if (v !== content.value) content.value = v
  }
)

watch(content, (v) => {
  emit('update:modelValue', v)
})

const handleSave = async () => {
  if (!props.resumeId) {
    message.warning('请先选择简历')
    return
  }
  saving.value = true
  try {
    await updateResumeContent(props.resumeId, content.value)
    message.success('简历已保存')
    emit('saved')
  } catch (err) {
    message.error(getApiErrorMessage(err, '保存失败'))
  } finally {
    saving.value = false
  }
}

const setContent = (text: string) => {
  content.value = text
}

const insertText = (text: string) => {
  const sep = content.value.endsWith('\n') || !content.value ? '' : '\n\n'
  content.value = content.value + sep + text
}

const insertAtCursor = (text: string) => {
  insertText(text)
}

const handleRestored = (text: string) => {
  setContent(text)
}

defineExpose({ insertText, insertAtCursor, setContent, content })
</script>

<template>
  <div class="editor-shell">
    <div class="editor-toolbar">
      <span class="editor-title">Markdown 编辑器</span>
      <n-space align="center" :size="8" wrap>
        <n-radio-group v-model:value="displayMode" size="small">
          <n-radio-button value="edit">编辑</n-radio-button>
          <n-radio-button value="split">分屏</n-radio-button>
          <n-radio-button value="preview">预览</n-radio-button>
        </n-radio-group>
        <n-button size="small" :disabled="!canEdit" @click="showVersionModal = true">
          版本
        </n-button>
        <n-button size="small" :disabled="!canEdit" @click="showExportModal = true">
          导出
        </n-button>
        <n-button
          type="primary"
          size="small"
          :loading="saving"
          :disabled="!canEdit"
          @click="handleSave"
        >
          保存
        </n-button>
      </n-space>
    </div>

    <div v-if="!canEdit" class="editor-placeholder">
      请从左侧选择一份简历开始编辑
    </div>

    <div v-else class="editor-body">
      <div v-if="loading" class="editor-loading">正在加载简历内容…</div>

      <!-- 编辑：textarea 自带滚动条，白底黑字 -->
      <textarea
        v-if="displayMode === 'edit'"
        v-model="content"
        class="resume-textarea"
        :disabled="loading"
        spellcheck="false"
        placeholder="在此编辑简历 Markdown 内容..."
      />

      <div v-else-if="displayMode === 'preview'" class="resume-preview-box">
        <md-preview :model-value="content" language="zh-CN" />
      </div>

      <md-editor
        v-else
        ref="editorRef"
        v-model="content"
        language="zh-CN"
        preview
        class="resume-split-editor"
        :toolbars="[
          'bold',
          'underline',
          'italic',
          '-',
          'title',
          'strikeThrough',
          'quote',
          'unorderedList',
          'orderedList',
          '-',
          'code',
          'link',
          'table',
          'revoke',
          'next',
          '=',
          'preview',
          'fullscreen',
        ]"
        placeholder="在此编辑简历 Markdown 内容..."
      />
    </div>

    <VersionHistoryModal
      v-model:show="showVersionModal"
      :resume-id="resumeId"
      :current-content="content"
      @restored="handleRestored"
    />

    <ExportDialog
      v-model:show="showExportModal"
      :resume-id="resumeId"
      :markdown-content="content"
    />
  </div>
</template>

<style scoped>
.editor-shell {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.editor-toolbar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--n-border-color);
  margin-bottom: 8px;
}

.editor-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--n-text-color);
}

.editor-placeholder {
  flex: 1;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--n-text-color-3);
  border: 1px dashed var(--n-border-color);
  border-radius: 8px;
  background: var(--n-color-modal);
}

/* 中间简历正文区：占满剩余高度 */
.editor-body {
  position: relative;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--n-border-color);
  border-radius: 6px;
  background: #ffffff;
}

.editor-loading {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.85);
  color: var(--n-text-color-2);
  font-size: 14px;
}

.resume-textarea {
  flex: 1;
  width: 100%;
  min-height: 0;
  margin: 0;
  padding: 16px 18px;
  border: none;
  outline: none;
  resize: none;
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: auto;
  font-family: Menlo, Consolas, 'Courier New', 'Microsoft YaHei', monospace;
  font-size: 14px;
  line-height: 1.75;
  color: #1a1a1a;
  background: #ffffff;
  caret-color: #18a058;
}

.resume-textarea:disabled {
  opacity: 0.6;
}

.resume-preview-box {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 12px 16px 20px;
  background: #ffffff;
  color: var(--n-text-color);
}

.resume-split-editor {
  flex: 1;
  min-height: 0 !important;
  height: 100% !important;
  border: none !important;
}
</style>

<style>
.ro-center-editor .resume-split-editor.md-editor {
  height: 100% !important;
  max-height: 100% !important;
}

.ro-center-editor .resume-split-editor .md-editor-content {
  flex: 1;
  min-height: 0;
  height: 0 !important;
}

.ro-center-editor .resume-split-editor .cm-scroller,
.ro-center-editor .resume-split-editor.has-preview .cm-scroller {
  overflow-y: auto !important;
}

.ro-center-editor .resume-split-editor .md-editor-preview-wrapper {
  overflow-y: auto !important;
}
</style>
