# AI 匹配分析页面 - 历史数据选择功能

## 功能说明

在 AI 匹配分析页面添加了选择历史简历和历史 JD 的功能，用户不再需要每次都重新上传简历和解析 JD，可以直接从历史记录中选择进行分析。

## 用户体验改进

### 之前的流程
1. 上传简历 → 2. 解析 JD → 3. 匹配分析

**问题**：每次分析都需要重新上传和解析，非常繁琐

### 现在的流程
1. 在匹配分析页面直接选择历史简历和历史 JD → 2. 点击"开始分析"

**优势**：
- 快速选择已有数据进行分析
- 支持多次分析不同组合
- 保留原有的上传新数据功能

## 修改的文件

### 1. 前端页面
**文件**：`src/views/AnalysisView.vue`

**修改内容**：
1. 添加历史数据加载逻辑
   - `resumeHistory`：简历历史列表
   - `jdHistory`：JD 历史列表
   - `loadHistory()`：加载历史数据的方法

2. 添加选择框
   - 简历选择下拉框（`n-select`）
   - JD 选择下拉框（`n-select`）
   - 支持搜索和过滤

3. 更新分析逻辑
   - 使用选中的 `selectedResumeId` 和 `selectedJdId`
   - 分析完成后更新 store

4. 优化 UI
   - 添加"选择数据"卡片
   - 显示加载状态
   - 提供"上传新简历/JD"按钮

### 2. API 类型定义
**文件**：`src/api/history.ts`

**修改内容**：
1. 更新 `JDHistory` 接口
   - 删除 `company`、`position`、`location` 字段
   - 添加 `keywords` 字段（关键词列表）

2. 更新 `JDDetail` 接口
   - 删除 `company`、`position`、`location`、`salary_range`、`benefits` 字段
   - 保留核心字段：`raw_text`、`required_skills`、`preferred_skills`、`responsibilities`、`requirements`、`keywords`

3. 添加类型别名
   - `JDHistoryItem = JDHistory`
   - `ResumeHistoryItem = ResumeHistory`

## 使用方式

### 1. 选择历史数据
1. 进入"匹配分析"页面
2. 在"选择数据"卡片中：
   - 从"选择简历"下拉框中选择历史简历
   - 从"选择 JD"下拉框中选择历史 JD
3. 点击"开始分析"按钮

### 2. 上传新数据
1. 点击"上传新简历/JD"按钮
2. 跳转到简历上传页面
3. 按照原有流程操作

## 技术细节

### 数据加载
```typescript
const loadHistory = async () => {
  // 加载简历历史
  const resumes = await getResumeHistory(20)
  resumeHistory.value = resumes
  
  // 加载 JD 历史
  const response = await fetch('/api/history/jds?limit=20', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
  if (response.ok) {
    jdHistory.value = await response.json()
  }
}
```

### 选项格式化
```typescript
// 简历选项：显示姓名和创建日期
const resumeOptions = computed(() => 
  resumeHistory.value.map(resume => ({
    label: `${resume.name || '未命名'} (${new Date(resume.created_at).toLocaleDateString()})`,
    value: resume.resume_id
  }))
)

// JD 选项：显示前 3 个关键词和创建日期
const jdOptions = computed(() => 
  jdHistory.value.map(jd => ({
    label: `${jd.keywords?.slice(0, 3).join(', ') || 'JD'} (${new Date(jd.created_at).toLocaleDateString()})`,
    value: jd.jd_id
  }))
)
```

### 分析逻辑
```typescript
const performAnalysis = async () => {
  // 使用选中的 ID 进行分析
  const response = await analyzeMatch(selectedResumeId.value!, selectedJdId.value!)
  
  // 更新 store
  matchStore.setMatchId(response.match_id)
  matchStore.setAnalysis(response.analysis)
  matchStore.setEnhancements(response.enhancements)
  matchStore.setReport(response.report_markdown)
  
  // 同步更新 resumeStore 和 jdStore
  resumeStore.setResumeId(selectedResumeId.value!)
  jdStore.setJdId(selectedJdId.value!)
}
```

## 注意事项

1. **权限验证**：需要用户登录才能查看历史数据
2. **数据限制**：默认加载最近 20 条记录
3. **搜索功能**：下拉框支持搜索和过滤
4. **清空选择**：下拉框支持清空当前选择
5. **自动分析**：如果 URL 中已有 resumeId 和 jdId，页面加载时会自动分析

## 后续优化建议

1. **分页加载**：历史数据较多时支持分页或无限滚动
2. **收藏功能**：支持收藏常用的简历和 JD
3. **批量分析**：支持一次选择多个 JD 与同一份简历进行批量分析
4. **对比功能**：支持对比不同简历与同一 JD 的匹配度
5. **标签管理**：为简历和 JD 添加标签，方便分类和筛选
