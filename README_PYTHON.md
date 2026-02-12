# 办公智能体 - 使用CrewAI实现

这是一个使用CrewAI框架实现的办公智能体，支持与大模型交互，处理Excel、文档、邮件等办公任务。

## 架构说明

- **前端**: Electron桌面应用
- **后端**: Python智能体（使用CrewAI框架）
- **通信**: Node.js通过IPC调用Python脚本
- **大模型**: 千问API（qwen3-coder-480b-a35b-instruct）

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置千问API密钥

千问API密钥已经配置在代码中，无需额外配置。

如需修改，可以编辑`.env`文件或`agent.py`文件中的`QWEN_API_KEY`变量。

### 3. 启动Electron应用

```bash
npm start
```

## 功能特性

### 智能体团队

1. **数据分析专家**: 分析Excel数据，提供数据洞察和建议
2. **文档处理专家**: 处理文档，提取关键信息
3. **邮件管理专家**: 管理邮件，撰写和发送邮件
4. **报告生成专家**: 生成报告，总结工作内容

### 工具集

1. **Excel分析工具**: 分析Excel数据，提供统计信息
2. **文档处理工具**: 处理文档，提取关键信息
3. **邮件管理工具**: 管理邮件，撰写和发送邮件
4. **报告生成工具**: 生成报告，总结工作内容
5. **搜索工具**: 使用DuckDuckGo进行网络搜索

## 使用示例

### 1. 上传Excel文件

点击"上传文件"按钮，选择Excel文件。

### 2. 发送消息

在输入框中输入消息，例如：

- "你好，请介绍一下你的功能"
- "请帮我分析这个Excel文件"
- "请帮我写一封邮件给老板，汇报工作进度"
- "请帮我生成一份报告"

### 3. 查看结果

智能体会根据你的请求，选择合适的工具和智能体来完成任务，并将结果显示在对话框中。

## 技术栈

- **前端**: Electron + HTML + CSS + JavaScript
- **后端**: Python + CrewAI + LangChain
- **大模型**: OpenAI GPT-4
- **数据处理**: Pandas + OpenPyXL
- **文档处理**: PyPDF2

## 开发说明

### 添加新工具

在`agent.py`中添加新的工具类，继承`BaseTool`：

```python
class MyCustomTool(BaseTool):
    name: str = "我的自定义工具"
    description: str = "工具描述"
    
    def _run(self, param1: str, param2: str = "") -> str:
        # 实现工具逻辑
        return "结果"
```

### 添加新智能体

在`OfficeAgent`类的`_create_agents`方法中添加新的智能体：

```python
my_agent = Agent(
    role='我的智能体',
    goal='智能体目标',
    backstory='智能体背景故事',
    verbose=True,
    llm=self.llm,
    tools=[self.tools[0]]
)
```

## 故障排除

### Python未安装

确保Python已安装，并且可以在命令行中运行`python`命令。

### 依赖安装失败

使用国内镜像源安装：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### API密钥错误

千问API密钥已经配置在代码中，无需额外配置。如需修改，请编辑`.env`文件或`agent.py`文件中的`QWEN_API_KEY`变量。

### Python脚本执行失败

检查Python脚本是否有语法错误，确保所有依赖都已正确安装。

## 许可证

MIT License
