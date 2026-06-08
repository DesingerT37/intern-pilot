<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  NModal,
  NList,
  NListItem,
  NThing,
  NButton,
  NSpace,
  NInput,
  NSpin,
  NEmpty,
  NPopconfirm,
  NText,
  useMessage,
} from 'naive-ui'
import {
  listResumeVersions,
  getResumeVersion,
  createResumeVersion,
  updateResumeContent,
  type VersionListItem,
} from '@/api/resumeOptimization'
import { getApiErrorMessage } from '@/utils/apiError'

const props = defineProps<{
  show: boolean
  resumeId: string | null
  currentContent: string
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  restored: [content: string]
}>()

const message = useMessage()
const loading = ref(false)
const creating = ref(false)
const versions = ref<VersionListItem[]>([])
const versionDescription = ref('')

const loadVersions = async () => {
  if (!props.resumeId) return
  loading.value = true
  try {
    versions.value = await listResumeVersions(props.resumeId)
  } catch (err) {
    message.error(getApiErrorMessage(err, '加载版本历史失败'))
  } finally {
    loading.value = false
  }
}

watch(
  () => props.show,
  (visible) => {
    if (visible) loadVersions()
  }
)

const handleCreateVersion = async () => {
  if (!props.resumeId) return
  creating.value = true
  try {
    await updateResumeContent(props.resumeId, props.currentContent)
    await createResumeVersion(props.resumeId, versionDescription.value || undefined)
    message.success('版本快照已创建')
    versionDescription.value = ''
    await loadVersions()
  } catch (err) {
    message.error(getApiErrorMessage(err, '创建版本失败'))
  } finally {
    creating.value = false
  }
}

const handleRestore = async (versionId: string) => {
  if (!props.resumeId) return
  loading.value = true
  try {
    const version = await getResumeVersion(props.resumeId, versionId)
    emit('restored', version.content)
    message.success('已回滚到所选版本（请保存以写入服务器）')
    emit('update:show', false)
  } catch (err) {
    message.error(getApiErrorMessage(err, '回滚失败'))
  } finally {
    loading.value = false
  }
}

const formatDate = (s: string) => new Date(s).toLocaleString('zh-CN')
</script>

<template>
  <n-modal
    :show="show"
    preset="card"
    title="版本历史"
    style="width: 560px; max-width: 95vw"
    @update:show="emit('update:show', $event)"
  >
    <n-space vertical :size="12">
      <n-space>
        <n-input
          v-model:value="versionDescription"
          placeholder="版本说明（可选）"
          size="small"
          style="flex: 1"
        />
        <n-button
          type="primary"
          size="small"
          :loading="creating"
          :disabled="!resumeId"
          @click="handleCreateVersion"
        >
          创建快照
        </n-button>
      </n-space>

      <n-spin :show="loading">
        <n-list v-if="versions.length" bordered>
          <n-list-item v-for="v in versions" :key="v.version_id">
            <n-thing
              :title="v.description || '未命名版本'"
              :description="formatDate(v.created_at)"
            >
              <n-text depth="3" style="font-size: 12px; display: block; margin-top: 4px">
                {{ v.content_preview }}
              </n-text>
              <template #footer>
                <n-popconfirm @positive-click="handleRestore(v.version_id)">
                  <template #trigger>
                    <n-button size="tiny" type="primary">回滚到此版本</n-button>
                  </template>
                  将用该版本内容替换当前编辑器内容，是否继续？
                </n-popconfirm>
              </template>
            </n-thing>
          </n-list-item>
        </n-list>
        <n-empty v-else description="暂无版本记录" />
      </n-spin>
    </n-space>
  </n-modal>
</template>
