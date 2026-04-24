# desk-mate - 桌面 Excel 分析助手

## Tech Stack
- Electron
- Node.js + TypeScript
- Excel 处理

## Build Commands
- `npm run dev` - 开发
- `npm run build` - 构建

---

## Architecture (IMPORTANT)

### 分层模型
```
src/
├── main/          (Electron 主进程)
├── renderer/      (渲染进程，UI)
├── services/      (服务层)
└── utils/         (工具函数)
```

### Electron 规范 (IMPORTANT)
- 主进程负责文件系统、原生 API
- 渲染进程负责 UI
- IPC 通信使用统一通道

---

## Code Style (IMPORTANT)

### 命名规范
- 文件: `kebab-case.ts`
- 类名: `PascalCase`
- 函数: `camelCase`

### 代码质量
- 单函数 ≤ 80 行
- 嵌套层级 ≤ 3 层

### 注释规范
- ❌ 不要写冗余注释
- ✅ 只写 WHY

---

## Excel 处理规范 (IMPORTANT)
- 大文件使用流式处理
- 内存占用需要控制
- 支持常见格式 (xlsx, xls, csv)

---

## Security (IMPORTANT)
- 文件访问需要用户确认
- 敏感数据不持久化
