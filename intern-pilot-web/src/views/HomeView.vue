<script setup lang="ts">
import { useRouter } from 'vue-router'
import { NCard, NButton, NSpace, NSteps, NStep } from 'naive-ui'

const router = useRouter()

const goToResume = () => {
  router.push('/resume')
}
</script>

<template>
  <div style="max-width: 1200px; margin: 0 auto">
    <div style="text-align: center; margin-bottom: 48px">
      <h1 style="font-size: 48px; margin-bottom: 16px">🎯 InternPilot</h1>
      <p style="font-size: 24px; color: #666">AI实习求职助手 - 让简历更匹配岗位需求</p>
    </div>

    <n-card title="使用流程" style="margin-bottom: 32px">
      <div style="padding: 40px 0; display: flex; justify-content: space-between; align-items: flex-start; gap: 48px">
        <!-- 步骤 1 -->
        <div style="flex: 1; text-align: center">
          <div style="width: 48px; height: 48px; border-radius: 50%; background: #18a058; color: white; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; margin: 0 auto 16px">
            1
          </div>
          <h3 style="margin-bottom: 8px; font-size: 18px">上传简历</h3>
          <p style="color: #999; font-size: 14px">支持 PDF、Word、Markdown 格式</p>
        </div>

        <!-- 连接线 -->
        <div style="flex: 0 0 auto; padding-top: 24px">
          <div style="width: 80px; height: 2px; background: #e0e0e0"></div>
        </div>

        <!-- 步骤 2 -->
        <div style="flex: 1; text-align: center">
          <div style="width: 48px; height: 48px; border-radius: 50%; background: #e0e0e0; color: #666; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; margin: 0 auto 16px">
            2
          </div>
          <h3 style="margin-bottom: 8px; font-size: 18px">粘贴 JD</h3>
          <p style="color: #999; font-size: 14px">输入目标岗位的职位描述</p>
        </div>

        <!-- 连接线 -->
        <div style="flex: 0 0 auto; padding-top: 24px">
          <div style="width: 80px; height: 2px; background: #e0e0e0"></div>
        </div>

        <!-- 步骤 3 -->
        <div style="flex: 1; text-align: center">
          <div style="width: 48px; height: 48px; border-radius: 50%; background: #e0e0e0; color: #666; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; margin: 0 auto 16px">
            3
          </div>
          <h3 style="margin-bottom: 8px; font-size: 18px">AI 分析</h3>
          <p style="color: #999; font-size: 14px">智能匹配分析，生成优化建议</p>
        </div>
      </div>
    </n-card>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-bottom: 32px">
      <n-card title="✨ 核心功能">
        <n-space vertical>
          <div>📄 智能简历解析</div>
          <div>🎯 精准匹配分析</div>
          <div>💡 针对性优化建议</div>
          <div>📊 匹配度评分</div>
        </n-space>
      </n-card>

      <n-card title="🚀 技术特点">
        <n-space vertical>
          <div>🤖 大模型驱动</div>
          <div>⚡ 快速响应</div>
          <div>🎨 现代化界面</div>
          <div>🔒 数据安全</div>
        </n-space>
      </n-card>

      <n-card title="📈 使用场景">
        <n-space vertical>
          <div>🎓 实习申请</div>
          <div>💼 校招准备</div>
          <div>📝 简历优化</div>
          <div>🔍 岗位匹配</div>
        </n-space>
      </n-card>
    </div>

    <div style="text-align: center">
      <n-button type="primary" size="large" @click="goToResume" style="padding: 0 48px; height: 48px; font-size: 18px">
        开始使用 →
      </n-button>
    </div>
  </div>
</template>

<style scoped>
</style>
