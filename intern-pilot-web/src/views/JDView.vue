<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useResumeStore } from '../stores/resume'
import { useJDStore } from '../stores/jd'
import { parseJD } from '../api/jd'
import { 
  NCard, 
  NInput, 
  NButton, 
  NSpace, 
  NSpin, 
  NAlert,
  NTag,
  NDivider,
  useMessage
} from 'naive-ui'

const router = useRouter()
const message = useMessage()
const resumeStore = useResumeStore()
const jdStore = useJDStore()

const jdText = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const isParsed = ref(false)

const canParse = computed(() => jdText.value.trim().length > 50)

/**
 * 解析 JD
 */
const handleParseJD = async () => {
  if (!canParse.value) {
    message.warning('请输入完整的岗位描述（至少 50 字）')
    return
  }
  
  try {
    isLoading.value = true
    errorMessage.value = ''
    
    const response = await parseJD(jdText.value)
    
    jdStore.setJDId(response.jd_id)
    jdStore.setJDData(response.jd_data)
    jdStore.setKeywords(response.keywords)
    
    isParsed.value = true
    message.success('JD 解析成功！')
    
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || error.message || '解析失败'
    message.error(errorMessage.value)
  } finally {
    isLoading.value = false
  }
}

/**
 * 前往分析页面
 */
const goToAnalysis = () => {
  if (!resumeStore.resumeId) {
    message.warning('请先上传简历')
    router.push('/resume')
    return
  }
  
  if (!jdStore.jdId) {
    message.warning('请先解析 JD')
    return
  }
  
  router.push('/analysis')
}

/**
 * 重新输入
 */
const resetJD = () => {
  jdText.value = ''
  isParsed.value = false
  errorMessage.value = ''
  jdStore.clearJD()
}

/**
 * 返回上一步
 */
const goBack = () => {
  router.push('/resume')
}
</script>

<template>
  <div style="max-width: 900px; margin: 0 auto">
    <n-card title="🎯 粘贴岗位需求 (JD)">
      <template #header-extra>
        <n-tag type="info">步骤 2/3</n-tag>
      </template>
      
      <!-- 提示信息 -->
      <n-alert v-if="!resumeStore.resumeId" type="warning" style="margin-bottom: 16px">
        请先上传简历
        <template #action>
          <n-button size="small" @click="goBack">去上传</n-button>
        </template>
      </n-alert>
      
      <!-- JD 输入区域 -->
      <div v-if="!isParsed">
        <n-input
          v-model:value="jdText"
          type="textarea"
          placeholder="请粘贴完整的岗位描述（Job Description）&#10;&#10;包括：&#10;- 公司名称&#10;- 职位名称&#10;- 工作职责&#10;- 任职要求&#10;- 技能要求&#10;- 薪资范围（可选）&#10;- 福利待遇（可选）"
          :rows="15"
          :disabled="isLoading"
          show-count
          style="margin-bottom: 16px"
        />
        
        <n-space justify="space-between">
          <n-button @click="goBack">← 上一步</n-button>
          <n-button 
            type="primary" 
            :loading="isLoading"
            :disabled="!canParse"
            @click="handleParseJD"
          >
            {{ isLoading ? '解析中...' : '解析 JD' }}
          </n-button>
        </n-space>
        
        <!-- 错误提示 -->
        <n-alert v-if="errorMessage" type="error" style="margin-top: 16px">
          {{ errorMessage }}
        </n-alert>
      </div>
      
      <!-- 解析结果 -->
      <div v-else>
        <n-alert type="success" style="margin-bottom: 24px">
          JD 解析成功！已提取关键信息
        </n-alert>
        
        <!-- JD 信息展示 -->
        <div style="margin-bottom: 24px">
          <div style="margin-bottom: 16px">
            <strong style="font-size: 18px">{{ jdStore.jdData?.company }}</strong>
            <n-tag type="primary" style="margin-left: 12px">{{ jdStore.jdData?.position }}</n-tag>
          </div>
          
          <div v-if="jdStore.jdData?.location || jdStore.jdData?.salary_range" style="margin-bottom: 16px; color: #666">
            <span v-if="jdStore.jdData?.location">📍 {{ jdStore.jdData.location }}</span>
            <span v-if="jdStore.jdData?.salary_range" style="margin-left: 16px">💰 {{ jdStore.jdData.salary_range }}</span>
          </div>
          
          <n-divider style="margin: 16px 0" />
          
          <!-- 必备技能 -->
          <div v-if="jdStore.jdData?.required_skills?.length" style="margin-bottom: 16px">
            <div style="margin-bottom: 8px; font-weight: 600">必备技能：</div>
            <n-space>
              <n-tag v-for="(skill, idx) in jdStore.jdData.required_skills" :key="idx" type="error">
                {{ skill }}
              </n-tag>
            </n-space>
          </div>
          
          <!-- 加分项 -->
          <div v-if="jdStore.jdData?.preferred_skills?.length" style="margin-bottom: 16px">
            <div style="margin-bottom: 8px; font-weight: 600">加分项：</div>
            <n-space>
              <n-tag v-for="(skill, idx) in jdStore.jdData.preferred_skills" :key="idx" type="warning">
                {{ skill }}
              </n-tag>
            </n-space>
          </div>
          
          <!-- 关键词 -->
          <div v-if="jdStore.keywords?.length" style="margin-bottom: 16px">
            <div style="margin-bottom: 8px; font-weight: 600">关键词：</div>
            <n-space>
              <n-tag v-for="(keyword, idx) in jdStore.keywords" :key="idx" type="info">
                {{ keyword }}
              </n-tag>
            </n-space>
          </div>
          
          <!-- 工作职责 -->
          <div v-if="jdStore.jdData?.responsibilities?.length" style="margin-bottom: 16px">
            <div style="margin-bottom: 8px; font-weight: 600">工作职责：</div>
            <ul style="margin: 0; padding-left: 20px">
              <li v-for="(item, idx) in jdStore.jdData.responsibilities" :key="idx" style="margin-bottom: 4px">
                {{ item }}
              </li>
            </ul>
          </div>
          
          <!-- 任职要求 -->
          <div v-if="jdStore.jdData?.requirements?.length">
            <div style="margin-bottom: 8px; font-weight: 600">任职要求：</div>
            <ul style="margin: 0; padding-left: 20px">
              <li v-for="(item, idx) in jdStore.jdData.requirements" :key="idx" style="margin-bottom: 4px">
                {{ item }}
              </li>
            </ul>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <n-space justify="space-between">
          <n-button @click="resetJD">重新输入</n-button>
          <n-button type="primary" @click="goToAnalysis">
            下一步：AI 分析 →
          </n-button>
        </n-space>
      </div>
    </n-card>
  </div>
</template>

<style scoped>
ul {
  list-style-type: disc;
}
</style>
