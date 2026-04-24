# desk-mate - 桌面 Excel 分析助手

## Tech Stack
- Electron + Node.js + TypeScript

## Build Commands
- `npm run dev` - 开发
- `npm run build` - 构建
- `npm run test` - 测试

---

## Architecture (IMPORTANT)

### 分层模型
```
src/
├── controllers/   (API 入口)
├── services/      (业务逻辑)
├── models/        (数据模型)
├── utils/         (工具函数)
└── tests/         (测试用例)
```

---

## Code Style (IMPORTANT)

### 命名规范
- 文件: `kebab-case.ts` 或 `kebab-case.js`
- 类名: `PascalCase`
- 函数: `camelCase`
- 常量: `UPPER_SNAKE_CASE`

### 代码质量限制 (IMPORTANT)
- 单函数 ≤ 80 行（超过必须拆分）
- 单类 ≤ 500 行（超过必须拆分）
- 嵌套层级 ≤ 3 层（使用提前 return）

### 注释规范 (IMPORTANT)
- ❌ 不要写冗余注释，代码本身应自解释
- ✅ 只在必要时写注释：
  - 复杂业务逻辑的 WHY（为什么这么做）
  - 非显而易见的约束或边界条件
  - 临时方案或待优化的 TODO
- ❌ 禁止注释描述 WHAT（代码做了什么）

### Map 使用限制 (IMPORTANT)
- ✅ `Map` 只能在方法内部使用，作为临时数据结构
- ❌ 禁止 `Map` 作为方法参数传递
- ❌ 禁止 `Map` 作为方法返回值
- ✅ 如需传递键值对，定义明确的 interface 或 type

---

## Git Workflow (IMPORTANT)
- 主分支: `master`
- 功能分支: `feature/YYYYMMDD_XXX*`
- 修复分支: `hotfix/YYYYMMDD_XXX*`
- Commit 格式:
  - `feat(scope): message` - 新功能
  - `fix(scope): message` - Bug 修复
  - `refactor(scope): message` - 重构
  - `docs: message` - 文档更新
  - `chore: message` - 构建/工具变动

---

## Security (IMPORTANT)
- Never commit API keys or secrets
- Validate all user input
- 文件访问需要用户确认
