# desk-mate - Electron + Python 数据助手 AI 约束

## AI 启动加载机制 (Codex / Claude Code / Cursor)
- `AGENTS.md`、`CLAUDE.md`、`.cursor/rules/main.mdc` 都只引用本文件。
- AI 开始写代码前必须先确认 Node 与 Python 的边界。

## 写代码前预检查 (MANDATORY)
1. 确认改动层：`main.js/preload.js`、页面文件、`services/*`、Python 脚本。
2. 列出数据链路：文件读取 -> AI 分析 -> 图表/导出。
3. 明确新增字段在 JS 与 Python 两侧的传递方式。
4. 限定最小改动，禁止顺带重构。

## 字段加载清单 (MANDATORY)
- 数据字段变更必须同步：Excel 解析结果、AI 输入上下文、图表渲染字段、导出字段。
- JS <-> Python 交互参数必须定义明确结构，禁止裸字符串拼接协议。
- API 配置字段（模型、地址、密钥）必须集中在服务层，禁止散落页面。

## 工程特性约束
- 主进程负责系统能力，渲染层只负责交互与展示。
- Python 执行必须通过 `services/pythonService.js` 一类封装。
- 文件读写必须做路径与扩展名校验。

## 验证要求
- 前端/主进程改动：`npm run build`
- Python 改动：`python3 -m py_compile *.py`

## 安全约束
- 禁止提交真实 API Key（当前仓内若存在历史明文，后续改动不得继续扩散）。
