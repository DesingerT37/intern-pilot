<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useResumeStore } from '../stores/resume'
import { uploadResume, parseResume } from '../api/resume'
import { 
  NCard, 
  NUpload, 
  NUploadDragger, 
  NButton, 
  NSpace, 
  NProgress, 
  NSpin, 
  NAlert,
  NDescriptions,
  NDescriptionsItem,
  NTag,
  NIcon,
  useMessage,
  type UploadFileInfo
} from 'naive-ui'
import { CloudUploadOutline, DocumentTextOutline, CheckmarkCircleOutline } from '@vicons/ionicons5'

const router = useRouter()
const message = useMessage()
const resumeStore = useResumeStore()

const uploadStatus = ref<'idle' | 'uploading' | 'parsing' | 'success' | 'error'>('idle')
const uploadProgress = ref(0)
const errorMessage = ref('')

const isProcessing = computed(() => uploadStatus.value === 'uploading' || uploadStatus.value === 'parsing')
const isSuccess = computed(() => uploadStatus.value === 'success')

/**
 * 处理文件上传
 */
const handleFileChange = async (options: { fileList: UploadFileInfo[] }) => {
  const fileList = options.fileList
  
  if (fileList.length === 0) return
  
  const file = fileList[0].file
  if (!file) return
  
  // 验证文件类型
  const allowedTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
    'text/markdown'
  ]
  
  if (!allowedTypes.includes(file.type) && !file.name.endsWith('.md')) {
    message.error('仅支持 PDF、Word、Markdown 格式')
    return
  }
  
  // 验证文件大小 (10MB)
  if (file.size > 10 * 1024 * 1024) {
    message.error('文件大小不能超过 10MB')
    return
  }
  
  try {
    uploadStatus.value = 'uploading'
    uploadProgress.value = 30
    errorMessage.value = ''
    
    // 上传文件
    const uploadResponse = await uploadResume(file)
    resumeStore.setResumeId(uploadResponse.resume_id)
    resumeStore.setResumeFile(file)
    
    uploadProgress.value = 60
    uploadStatus.value = 'parsing'
    
    // 解析简历
    const parseResponse = await parseResume(uploadResponse.resume_id)
    resumeStore.setResumeData(parseResponse.resume_data)
    
    uploadProgress.value = 100
    uploadStatus.value = 'success'
    
    message.success('简历解析成功！')
    
  } catch (error: any) {
    uploadStatus.value = 'error'
    errorMessage.value = error.response?.data?.detail || error.message || '上传失败'
    message.error(errorMessage.value)
  }
}

/**
 * 前往下一步
 */
const goToNextStep = () => {
  router.push('/jd')
}

/**
 * 重新上传
 */
const resetUpload = () => {
  uploadStatus.value = 'idle'
  uploadProgress.value = 0
  errorMessage.value = ''
  resumeStore.clearResume()
}
</script>

<template>
  <div style="max-width: 900px; margin: 0 auto">
    <n-card title="📄 上传简历">
      <template #header-extra>
        <n-tag type="info">步骤 1/3</n-tag>
      </template>
      
      <!-- 上传区域 -->
      <div v-if="!isSuccess">
        <n-upload
          :max="1"
          :show-file-list="false"
          :disabled="isProcessing"
          @change="handleFileChange"
        >
          <n-upload-dragger>
            <div style="margin-bottom: 12px">
              <n-icon size="48" :depth="3">
                <cloud-upload-outline />
              </n-icon>
            </div>
            <div style="font-size: 16px; margin-bottom: 8px">
              点击或拖拽文件到此区域上传
            </div>
            <div style="font-size: 14px; color: #999">
              支持 PDF、Word (.docx)、Markdown (.md) 格式，文件大小不超过 10MB
            </div>
          </n-upload-dragger>
        </n-upload>
        
        <!-- 上传进度 -->
        <div v-if="isProcessing" style="margin-top: 24px">
          <n-spin size="small">
            <template #description>
              <div style="margin-top: 12px">
                {{ uploadStatus === 'uploading' ? '正在上传...' : '正在解析简历...' }}
              </div>
            </template>
          </n-spin>
          <n-progress
            type="line"
            :percentage="uploadProgress"
            :show-indicator="false"
            style="margin-top: 16px"
          />
        </div>
        
        <!-- 错误提示 -->
        <n-alert v-if="uploadStatus === 'error'" type="error" style="margin-top: 24px">
          {{ errorMessage }}
          <template #action>
            <n-button size="small" @click="resetUpload">重试</n-button>
          </template>
        </n-alert>
      </div>
      
      <!-- 解析成功 -->
      <div v-else>
        <n-alert type="success" style="margin-bottom: 24px">
          <template #icon>
            <n-icon>
              <checkmark-circle-outline />
            </n-icon>
          </template>
          简历解析成功！已提取关键信息
        </n-alert>
        
        <!-- 简历信息预览 -->
        <n-card title="简历信息" style="margin-bottom: 24px">
          <n-descriptions :column="2" bordered>
            <n-descriptions-item label="姓名">
              {{ resumeStore.resumeData?.name || '-' }}
            </n-descriptions-item>
            <n-descriptions-item label="目标职位">
              {{ resumeStore.resumeData?.target_position || '-' }}
            </n-descriptions-item>
            <n-descriptions-item label="邮箱">
              {{ resumeStore.resumeData?.email || '-' }}
            </n-descriptions-item>
            <n-descriptions-item label="电话">
              {{ resumeStore.resumeData?.phone || '-' }}
            </n-descriptions-item>
            <n-descriptions-item label="教育背景" :span="2">
              <n-space v-if="resumeStore.resumeData?.education?.length">
                <n-tag v-for="(edu, idx) in resumeStore.resumeData.education" :key="idx" type="info">
                  {{ edu.school }} - {{ edu.degree }}
                </n-tag>
              </n-space>
              <span v-else>-</span>
            </n-descriptions-item>
            <n-descriptions-item label="技能" :span="2">
              <n-space v-if="resumeStore.resumeData?.skills?.length">
                <n-tag v-for="(skill, idx) in resumeStore.resumeData.skills" :key="idx" type="success">
                  {{ skill }}
                </n-tag>
              </n-space>
              <span v-else>-</span>
            </n-descriptions-item>
            <n-descriptions-item label="项目经历">
              {{ resumeStore.resumeData?.projects?.length || 0 }} 个
            </n-descriptions-item>
            <n-descriptions-item label="工作经历">
              {{ resumeStore.resumeData?.work_experience?.length || 0 }} 个
            </n-descriptions-item>
          </n-descriptions>
        </n-card>
        
        <!-- 操作按钮 -->
        <n-space justify="space-between">
          <n-button @click="resetUpload">重新上传</n-button>
          <n-button type="primary" @click="goToNextStep">
            下一步：粘贴 JD →
          </n-button>
        </n-space>
      </div>
    </n-card>
  </div>
</template>

<style scoped>
</style>
