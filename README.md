# 桌面Excel分析助手

一个基于Electron的桌面应用，支持Excel文件上传、AI分析、图表生成和结果导出功能。

## 功能特点

- 📁 Excel文件上传和读取
- 💬 与AI大模型对话进行数据分析
- 📊 自动生成数据可视化图表
- 📈 详细的分析结果和建议
- 💾 分析结果导出为Excel文件
- 🐍 支持Python代码执行（可选）

## 技术栈

- **前端框架**: Electron
- **Excel处理**: xlsx
- **AI集成**: 文心一言（通过OpenAI兼容API）
- **图表生成**: ECharts
- **Python集成**: python-shell
- **HTTP请求**: axios

## 安装说明

### 1. 安装依赖

#### 1.1 安装Node.js

前往 [Node.js官网](https://nodejs.org/) 下载并安装最新版本的Node.js。

#### 1.2 安装Python（可选，用于执行Python代码）

前往 [Python官网](https://www.python.org/) 下载并安装Python 3.7+版本。

#### 1.3 安装项目依赖

在项目目录下运行：

```bash
npm install
```

### 2. 配置AI模型

项目已默认配置了文心一言模型，使用以下配置：

- API Key: `iNjoFN6OE1BS_tio6SWa478Dw6DPbIuKpccEOp7wKOh_f3xf6eDxS0EGgHTYYJG-j3tp-TdGuNATgl0l2WJ0wQ`
- API Base: `https://api.modelarts-maas.com/openai/v1`
- Model: `qwen3-coder-480b-a35b-instruct`

如需修改配置，请编辑 `services/aiService.js` 文件。

## 使用方法

### 1. 启动应用

在项目目录下运行：

```bash
npm start
```

### 2. 上传Excel文件

点击"选择Excel文件"按钮，选择要分析的Excel文件。

### 3. 输入分析需求

在对话框中输入您的分析需求，例如：

- "分析销售额的趋势"
- "计算各产品的平均利润"
- "找出销售额最高的前10个产品"

### 4. 查看分析结果

- 右侧面板会显示AI生成的分析结果
- 自动生成数据可视化图表
- 可以点击"导出分析结果"按钮将结果导出为Excel文件

## 项目结构

```
desk-mate/
├── main.js              # Electron主进程
├── preload.js           # 预加载脚本
├── index.html           # 主界面
├── package.json         # 项目配置
├── services/
│   ├── excelService.js  # Excel处理服务
│   ├── aiService.js     # AI服务
│   └── pythonService.js # Python执行服务
└── README.md            # 项目说明
```

## 注意事项

1. **网络连接**: 使用AI功能需要稳定的网络连接
2. **文件大小**: 建议处理小于10MB的Excel文件，以获得更好的性能
3. **数据隐私**: 分析过程中，数据会被发送到AI模型进行处理，请确保数据安全
4. **Python依赖**: 如果需要执行Python代码，确保已安装必要的Python库

## 故障排除

### 常见问题

1. **应用无法启动**
   - 检查Node.js是否正确安装
   - 运行 `npm install` 重新安装依赖

2. **Excel文件读取失败**
   - 确保文件格式为 .xlsx、.xls 或 .csv
   - 检查文件是否被其他程序占用

3. **AI分析失败**
   - 检查网络连接
   - 确认API Key和模型配置正确

4. **图表不显示**
   - 检查ECharts是否正确加载
   - 确保数据格式正确

## 开发说明

### 调试模式

```bash
npm run dev
```

### 打包应用

```bash
npm run build
```

## 许可证

MIT License
