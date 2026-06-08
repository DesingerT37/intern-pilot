# InternPilot Web

AI实习求职助手 - 前端应用

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全
- **Vite** - 快速构建工具
- **Naive UI** - Vue 3 组件库
- **Pinia** - 状态管理
- **Axios** - HTTP 客户端

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问: http://localhost:5173

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
src/
├── api/              # API 调用
├── assets/           # 静态资源
├── components/       # 公共组件
├── composables/      # 组合式函数
├── stores/           # Pinia 状态管理
├── types/            # TypeScript 类型定义
├── views/            # 页面组件
├── App.vue           # 根组件
└── main.ts           # 入口文件
```

## 开发进度

### Sprint 0 ✅ (已完成)
- [x] 项目脚手架
- [x] Vite + Vue 3 + TypeScript
- [x] Naive UI 集成
- [x] Pinia 状态管理
- [x] Axios 配置
- [x] 基础目录结构

### Sprint 1 (进行中)
- [ ] 简历上传页面
- [ ] JD 输入页面
- [ ] 分析结果展示页面
- [ ] 路由配置

## API 代理配置

开发环境下，所有 `/api` 请求会被代理到 `http://localhost:8000`

配置文件: `vite.config.ts`

## 许可证

MIT
