<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import markdownItHighlight from 'markdown-it-highlightjs'
import 'highlight.js/styles/github.css'
import {
  NInput,
  NButton,
  NSpace,
  NTag,
  NEmpty,
  NAlert,
  useMessage,
} from 'naive-ui'
import {
  streamChatWithAI,
  type ResumeChatMessage,
  type ResumeChatRequest,
} from '@/api/resumeOptimization'
import { getApiErrorMessage } from '@/utils/apiError'

const props = defineProps<{
  resumeId: string | null
  resumeContent: string
  pendingMessage?: string
}>()

const emit = defineEmits<{
  applySection: [text: string]
  'update:pendingMessage': [value: string]
}>()

const message = useMessage()
const inputText = ref('')
const chatHistory = ref<ResumeChatMessage[]>([])
const streaming = ref(false)
const streamContent = ref('')
const lastMetadata = ref<{
  modified_section?: string | null
  section_type?: string | null
  explanation?: string | null
} | null>(null)
const messagesRef = ref<HTMLElement | null>(null)
const abortController = ref<AbortController | null>(null)
const lastError = ref<string | null>(null)
const lastFailedMessage = ref<string | null>(null)
const showRetry = ref(false)

const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
}).use(markdownItHighlight)

const renderMd = (text: string) => md.render(text)

const displayMessages = computed(() => {
  const list = [...chatHistory.value]
  if (streaming.value && streamContent.value) {
    list.push({ role: 'assistant', content: streamContent.value })
  }
  return list
})

const hasMessages = computed(
  () => displayMessages.value.length > 0 || (streaming.value && !streamContent.value)
)

watch(
  () => props.pendingMessage,
  (text) => {
    if (text) {
      inputText.value = text
      emit('update:pendingMessage', '')
      nextTick(() => sendMessage())
    }
  }
)

const scrollToBottom = async () => {
  await nextTick()
  const el = messagesRef.value
  if (el) el.scrollTop = el.scrollHeight
}

const doStream = async (text: string, context: ResumeChatMessage[]) => {
  const request: ResumeChatRequest = {
    resume_id: props.resumeId!,
    resume_content: props.resumeContent,
    message: text,
    context,
  }

  abortController.value = new AbortController()
  lastError.value = null
  showRetry.value = false

  await streamChatWithAI(
    request,
    {
      onContent: (chunk) => {
        streamContent.value += chunk
        scrollToBottom()
      },
      onMetadata: (meta) => {
        lastMetadata.value = meta
      },
      onError: (err) => {
        lastError.value = err
        message.error(err)
      },
      onDone: () => {},
    },
    abortController.value.signal
  )

  chatHistory.value.push({
    role: 'assistant',
    content: streamContent.value,
    timestamp: new Date().toISOString(),
    modified_section: lastMetadata.value?.modified_section,
    section_type: lastMetadata.value?.section_type,
    explanation: lastMetadata.value?.explanation,
  })
}

const sendMessage = async (retryText?: string) => {
  const text = (retryText ?? inputText.value).trim()
  if (!text) return
  if (!props.resumeId) {
    message.warning('请先选择简历')
    return
  }
  if (streaming.value) {
    message.warning('请等待当前回复完成')
    return
  }

  streaming.value = true
  streamContent.value = ''
  lastMetadata.value = null
  lastFailedMessage.value = text

  if (!retryText) {
    chatHistory.value.push({
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    })
    inputText.value = ''
  }

  await scrollToBottom()

  const ctxForApi = chatHistory.value.slice(0, -1).slice(-10)

  try {
    await doStream(text, ctxForApi)
    showRetry.value = false
    lastFailedMessage.value = null
  } catch (err: unknown) {
    if ((err as Error).name === 'AbortError') return

    const errMsg = getApiErrorMessage(err, 'AI 对话失败')
    lastError.value = errMsg
    showRetry.value = true
    message.error(errMsg)
    if (!retryText) {
      inputText.value = text
    }
  } finally {
    streaming.value = false
    streamContent.value = ''
    abortController.value = null
    await scrollToBottom()
  }
}

const retryLastMessage = () => {
  if (lastFailedMessage.value) {
    sendMessage(lastFailedMessage.value)
  }
}

const applyLastSection = () => {
  const last = [...chatHistory.value]
    .reverse()
    .find((m) => m.role === 'assistant' && m.modified_section)
  if (last?.modified_section) {
    emit('applySection', last.modified_section)
    message.success('已应用到编辑器')
  } else {
    message.warning('没有可应用的修改段落')
  }
}

const clearHistory = () => {
  chatHistory.value = []
  streamContent.value = ''
  lastMetadata.value = null
  lastError.value = null
  showRetry.value = false
  message.info('对话历史已清空（仅本地）')
}

const stopStream = () => {
  abortController.value?.abort()
  streaming.value = false
}

defineExpose({ clearHistory, sendMessage })
</script>

<template>
  <div class="chat-panel">
    <header class="chat-header">
      <span class="chat-title">AI 简历助手</span>
      <n-space :size="6">
        <n-button size="tiny" :disabled="!chatHistory.length" @click="applyLastSection">
          应用到编辑器
        </n-button>
        <n-button size="tiny" quaternary @click="clearHistory">清空</n-button>
        <n-button v-if="streaming" size="tiny" type="error" @click="stopStream">停止</n-button>
      </n-space>
    </header>

    <div v-if="showRetry && lastError" class="retry-bar">
      <n-alert type="warning" closable @close="showRetry = false">
        {{ lastError }}
      </n-alert>
      <n-button
        size="small"
        type="primary"
        :loading="streaming"
        style="margin-top: 6px"
        @click="retryLastMessage"
      >
        重试上一条消息
      </n-button>
    </div>

    <!-- 消息区：占满 header 与输入框之间的空间 -->
    <div ref="messagesRef" class="chat-messages">
      <div v-if="!hasMessages" class="chat-empty-hint">
        <n-empty size="small" description="向 AI 描述你想如何优化简历">
          <template #extra>
            <n-text depth="3" style="font-size: 12px">
              可从右侧建议点击「发送给 AI」，或直接在下方输入
            </n-text>
          </template>
        </n-empty>
      </div>

      <template v-else>
        <div
          v-for="(msg, idx) in displayMessages"
          :key="idx"
          class="chat-bubble"
          :class="msg.role"
        >
          <n-tag size="small" :type="msg.role === 'user' ? 'info' : 'success'" style="margin-bottom: 4px">
            {{ msg.role === 'user' ? '你' : 'AI' }}
          </n-tag>
          <div class="md-body" v-html="renderMd(msg.content)" />
          <div v-if="msg.modified_section && msg.role === 'assistant'" class="section-actions">
            <n-button size="tiny" type="primary" @click="emit('applySection', msg.modified_section!)">
              应用此段落
            </n-button>
            <n-tag v-if="msg.section_type" size="tiny">{{ msg.section_type }}</n-tag>
          </div>
        </div>
        <div v-if="streaming && !streamContent" class="chat-loading">AI 正在思考...</div>
      </template>
    </div>

    <!-- 输入区：紧贴消息区下方 -->
    <footer class="chat-input">
      <n-input
        v-model:value="inputText"
        type="textarea"
        placeholder="例如：帮我优化项目经历，突出技术栈和量化成果..."
        :autosize="{ minRows: 2, maxRows: 4 }"
        :disabled="streaming"
        @keydown.enter.ctrl="sendMessage()"
      />
      <n-button
        type="primary"
        :loading="streaming"
        :disabled="!resumeId"
        class="send-btn"
        block
        @click="sendMessage()"
      >
        发送 (Ctrl+Enter)
      </n-button>
    </footer>
  </div>
</template>

<style scoped>
.chat-panel {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
  padding: 10px 12px 12px;
  background: var(--n-color);
}

.chat-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--n-border-color);
}

.chat-title {
  font-weight: 600;
  font-size: 14px;
}

.retry-bar {
  flex-shrink: 0;
  margin-bottom: 8px;
}

/* 消息列表：中间可滚动，不再固定 200px */
.chat-messages {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 8px 10px;
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  background: #fafafa;
  box-sizing: border-box;
}

/* 空状态靠上显示，不要垂直居中占满整块 */
.chat-empty-hint {
  padding: 16px 8px;
}

.chat-empty-hint :deep(.n-empty) {
  padding: 0;
}

.chat-bubble {
  margin-bottom: 12px;
  padding: 8px 10px;
  border-radius: 8px;
}

.chat-bubble.user {
  background: rgba(32, 128, 240, 0.08);
}

.chat-bubble.assistant {
  background: rgba(24, 160, 88, 0.08);
}

.chat-loading {
  color: var(--n-text-color-3);
  font-size: 13px;
  padding: 8px 4px;
}

.chat-input {
  flex-shrink: 0;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--n-border-color);
}

.send-btn {
  margin-top: 8px;
}

.md-body :deep(pre) {
  overflow-x: auto;
  padding: 8px;
  border-radius: 4px;
  background: #f0f0f0;
}

.section-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
</style>
