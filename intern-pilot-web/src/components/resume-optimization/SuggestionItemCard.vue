<script setup lang="ts">
import { NButton, NTag, NText } from 'naive-ui'
import type { Suggestion } from '@/api/resumeOptimization'

defineProps<{
  suggestion: Suggestion
  sourceLabel: string
  sourceType?: 'info' | 'warning' | 'default'
}>()

const emit = defineEmits<{
  sendToAi: [suggestion: Suggestion]
  copy: [suggestion: Suggestion]
}>()

const priorityType = (p: number) => {
  if (p <= 2) return 'error'
  if (p <= 3) return 'warning'
  return 'default'
}

const categoryLabel: Record<string, string> = {
  skill: '技能',
  project: '项目',
  description: '描述',
  format: '格式',
}
</script>

<template>
  <article class="suggestion-item">
    <header class="suggestion-item__head">
      <h4 class="suggestion-item__title">{{ suggestion.title }}</h4>
      <n-tag :type="priorityType(suggestion.priority)" size="small" round>
        P{{ suggestion.priority }}
      </n-tag>
    </header>

    <div class="suggestion-item__meta">
      <n-tag :type="sourceType || 'default'" size="tiny" :bordered="false">{{ sourceLabel }}</n-tag>
      <n-tag size="tiny">{{ categoryLabel[suggestion.category] || suggestion.category }}</n-tag>
    </div>

    <n-text depth="3" class="suggestion-item__desc">{{ suggestion.description }}</n-text>

    <div v-if="suggestion.example" class="suggestion-item__example">
      <n-text depth="3" style="font-size: 11px">示例</n-text>
      <pre>{{ suggestion.example }}</pre>
    </div>

    <footer class="suggestion-item__actions">
      <n-button size="small" type="primary" @click="emit('sendToAi', suggestion)">
        发送本条给 AI
      </n-button>
      <n-button size="small" quaternary @click="emit('copy', suggestion)">
        复制本条
      </n-button>
    </footer>
  </article>
</template>

<style scoped>
.suggestion-item {
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 10px;
  background: #ffffff;
  box-sizing: border-box;
}

.suggestion-item__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}

.suggestion-item__title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--n-text-color);
  flex: 1;
  word-break: break-word;
}

.suggestion-item__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.suggestion-item__desc {
  display: block;
  font-size: 13px;
  line-height: 1.6;
  word-break: break-word;
}

.suggestion-item__example {
  margin-top: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.03);
  border-left: 3px solid var(--n-border-color);
}

.suggestion-item__example pre {
  margin: 4px 0 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 12px;
  line-height: 1.5;
  color: var(--n-text-color-2);
}

.suggestion-item__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px dashed var(--n-border-color);
}
</style>
