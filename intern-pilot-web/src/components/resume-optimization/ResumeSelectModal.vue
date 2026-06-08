<script setup lang="ts">
import { NModal } from 'naive-ui'
import ResumeSelector from './ResumeSelector.vue'
import type { ResumeListItem } from '@/api/resumeOptimization'

defineProps<{
  show: boolean
  selectedId?: string | null
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  select: [resume: ResumeListItem]
}>()

const handleSelect = (resume: ResumeListItem) => {
  emit('select', resume)
  emit('update:show', false)
}
</script>

<template>
  <n-modal
    :show="show"
    preset="card"
    title="选择简历"
    style="width: min(560px, 92vw)"
    :mask-closable="true"
    @update:show="emit('update:show', $event)"
  >
    <ResumeSelector embedded :selected-id="selectedId" @select="handleSelect" />
  </n-modal>
</template>
