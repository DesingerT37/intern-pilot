<script setup lang="ts">
import { ref } from 'vue'
import { saveAs } from 'file-saver'
import {
  NModal,
  NForm,
  NFormItem,
  NRadioGroup,
  NRadio,
  NSelect,
  NButton,
  NSpace,
  useMessage,
} from 'naive-ui'
import { exportResume } from '@/api/resumeOptimization'
import { getApiErrorMessage } from '@/utils/apiError'

const props = defineProps<{
  show: boolean
  resumeId: string | null
  markdownContent: string
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
}>()

const message = useMessage()
const exporting = ref(false)
const format = ref<'pdf' | 'docx' | 'markdown'>('pdf')
const style = ref('default')

const styleOptions = [
  { label: '默认', value: 'default' },
  { label: '现代', value: 'modern' },
  { label: '经典', value: 'classic' },
]

const handleExport = async () => {
  if (!props.resumeId) {
    message.warning('请先选择简历')
    return
  }
  if (!props.markdownContent.trim()) {
    message.warning('简历内容为空')
    return
  }

  exporting.value = true
  const loadingMsg = message.loading('正在导出...', { duration: 0 })

  try {
    if (format.value === 'markdown') {
      const blob = new Blob([props.markdownContent], { type: 'text/markdown;charset=utf-8' })
      saveAs(blob, `resume_${props.resumeId.slice(0, 8)}.md`)
      message.success('Markdown 已下载')
    } else {
      const blob = await exportResume({
        resume_id: props.resumeId,
        markdown_content: props.markdownContent,
        format: format.value,
        style: style.value,
      })
      const ext = format.value === 'pdf' ? 'pdf' : 'docx'
      saveAs(blob, `resume_${props.resumeId.slice(0, 8)}.${ext}`)
      message.success(`${ext.toUpperCase()} 已下载`)
    }
    emit('update:show', false)
  } catch (err) {
    const errMsg = getApiErrorMessage(err, '导出失败')
    message.error(errMsg)
    if (format.value !== 'markdown') {
      message.info('可尝试导出为 Markdown 作为降级方案', { duration: 5000 })
    }
  } finally {
    loadingMsg.destroy()
    exporting.value = false
  }
}
</script>

<template>
  <n-modal
    :show="show"
    preset="card"
    title="导出简历"
    style="width: 420px"
    @update:show="emit('update:show', $event)"
  >
    <n-form label-placement="left" label-width="80">
      <n-form-item label="格式">
        <n-radio-group v-model:value="format">
          <n-space>
            <n-radio value="pdf">PDF</n-radio>
            <n-radio value="docx">DOCX</n-radio>
            <n-radio value="markdown">Markdown</n-radio>
          </n-space>
        </n-radio-group>
      </n-form-item>
      <n-form-item v-if="format !== 'markdown'" label="样式">
        <n-select v-model:value="style" :options="styleOptions" style="width: 100%" />
      </n-form-item>
    </n-form>
    <n-space justify="end">
      <n-button @click="emit('update:show', false)">取消</n-button>
      <n-button type="primary" :loading="exporting" @click="handleExport">导出</n-button>
    </n-space>
  </n-modal>
</template>
