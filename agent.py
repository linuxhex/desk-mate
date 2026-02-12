#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
办公智能体 - 使用CrewAI实现
支持与大模型交互，处理Excel、文档、邮件等办公任务
"""

import os
import json
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# 导入CrewAI相关库
try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import BaseTool
    from pydantic import BaseModel, Field
except ImportError:
    print("请先安装CrewAI: pip install crewai")
    sys.exit(1)

# 导入大模型相关库
try:
    from langchain_openai import ChatOpenAI
    from langchain_community.tools import DuckDuckGoSearchRun
except ImportError:
    print("请先安装LangChain: pip install langchain-openai langchain-community")
    sys.exit(1)

# 千问API配置
QWEN_API_KEY = "iNjoFN6OE1BS_tio6SWa478Dw6DPbIuKpccEOp7wKOh_f3xf6eDxS0EGgHTYYJG-j3tp-TdGuNATgl0l2WJ0wQ"
QWEN_API_ENDPOINT = "https://api.modelarts-maas.com/openai/v1/chat/completions"
QWEN_MODEL = "qwen3-coder-480b-a35b-instruct"


class ExcelAnalysisTool(BaseTool):
    """Excel数据分析工具"""
    name: str = "Excel分析工具"
    description: str = "用于分析Excel数据，提供数据洞察和建议"

    def _run(self, file_path: str, query: str = "") -> str:
        """
        执行Excel分析
        
        Args:
            file_path: Excel文件路径
            query: 分析查询
            
        Returns:
            分析结果
        """
        try:
            import pandas as pd
            
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 基本统计信息
            result = f"文件: {os.path.basename(file_path)}\n"
            result += f"行数: {len(df)}\n"
            result += f"列数: {len(df.columns)}\n"
            result += f"列名: {', '.join(df.columns)}\n\n"
            
            # 数值列统计
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                result += "数值列统计:\n"
                for col in numeric_cols:
                    result += f"  {col}:\n"
                    result += f"    最小值: {df[col].min()}\n"
                    result += f"    最大值: {df[col].max()}\n"
                    result += f"    平均值: {df[col].mean():.2f}\n"
                    result += f"    标准差: {df[col].std():.2f}\n\n"
            
            # 分类列统计
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                result += "分类列统计:\n"
                for col in categorical_cols[:3]:  # 只显示前3个分类列
                    result += f"  {col}:\n"
                    value_counts = df[col].value_counts()
                    for value, count in value_counts.head(5).items():
                        result += f"    {value}: {count}\n"
                    result += "\n"
            
            return result
            
        except Exception as e:
            return f"分析失败: {str(e)}"


class DocumentProcessingTool(BaseTool):
    """文档处理工具"""
    name: str = "文档处理工具"
    description: str = "用于处理文档，提取关键信息"

    def _run(self, file_path: str, task: str = "") -> str:
        """
        执行文档处理
        
        Args:
            file_path: 文档文件路径
            task: 处理任务
            
        Returns:
            处理结果
        """
        try:
            # 根据文件类型选择处理方式
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return f"文档内容:\n{content[:1000]}..." if len(content) > 1000 else f"文档内容:\n{content}"
            
            elif file_ext == '.pdf':
                # 这里需要安装PyPDF2: pip install PyPDF2
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        content = ""
                        for page in reader.pages:
                            content += page.extract_text()
                    return f"PDF内容:\n{content[:1000]}..." if len(content) > 1000 else f"PDF内容:\n{content}"
                except ImportError:
                    return "PDF处理需要安装PyPDF2: pip install PyPDF2"
            
            else:
                return f"不支持的文件类型: {file_ext}"
                
        except Exception as e:
            return f"处理失败: {str(e)}"


class EmailManagementTool(BaseTool):
    """邮件管理工具"""
    name: str = "邮件管理工具"
    description: str = "用于管理邮件，撰写和发送邮件"

    def _run(self, action: str, recipient: str = "", subject: str = "", content: str = "") -> str:
        """
        执行邮件管理
        
        Args:
            action: 操作类型 (compose, send, list)
            recipient: 收件人
            subject: 邮件主题
            content: 邮件内容
            
        Returns:
            操作结果
        """
        try:
            if action == "compose":
                email = f"收件人: {recipient}\n"
                email += f"主题: {subject}\n"
                email += f"内容:\n{content}"
                return f"邮件草稿已创建:\n{email}"
            
            elif action == "send":
                return f"邮件已发送给 {recipient}"
            
            elif action == "list":
                return "邮件列表:\n1. 来自 boss@company.com: 项目进度报告\n2. 来自 client@partner.com: 合同确认"
            
            else:
                return f"不支持的操作: {action}"
                
        except Exception as e:
            return f"操作失败: {str(e)}"


class ReportGenerationTool(BaseTool):
    """报告生成工具"""
    name: str = "报告生成工具"
    description: str = "用于生成报告，总结工作内容"

    def _run(self, data: str, report_type: str = "summary") -> str:
        """
        执行报告生成
        
        Args:
            data: 数据内容
            report_type: 报告类型
            
        Returns:
            生成的报告
        """
        try:
            report = f"报告类型: {report_type}\n"
            report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            if report_type == "summary":
                report += "摘要报告\n"
                report += "-" * 50 + "\n"
                report += data[:500]
                
            elif report_type == "detailed":
                report += "详细报告\n"
                report += "-" * 50 + "\n"
                report += data
                
            else:
                report += f"自定义报告\n"
                report += "-" * 50 + "\n"
                report += data
            
            return report
            
        except Exception as e:
            return f"生成失败: {str(e)}"


class OfficeAgent:
    """办公智能体 - 使用CrewAI实现"""
    
    def __init__(self, api_key: str = "", model: str = "qwen3-coder-480b-a35b-instruct"):
        """
        初始化办公智能体
        
        Args:
            api_key: 千问API密钥
            model: 使用的模型
        """
        # 初始化大模型 - 使用千问API
        self.llm = ChatOpenAI(
            api_key=api_key or QWEN_API_KEY,
            model=model,
            temperature=0.7,
            base_url=QWEN_API_ENDPOINT.replace('/chat/completions', '')
        )
        
        # 创建工具
        self.tools = [
            ExcelAnalysisTool(),
            DocumentProcessingTool(),
            EmailManagementTool(),
            ReportGenerationTool(),
            DuckDuckGoSearchRun()
        ]
        
        # 创建智能体
        self.agents = self._create_agents()
        
        # 创建团队
        self.crew = Crew(
            agents=self.agents,
            process=Process.sequential,
            verbose=True
        )
    
    def _create_agents(self) -> List[Agent]:
        """创建智能体团队"""
        
        # 数据分析专家
        data_analyst = Agent(
            role='数据分析专家',
            goal='分析Excel数据，提供数据洞察和建议',
            backstory='你是一位经验丰富的数据分析专家，擅长从数据中发现有价值的信息和趋势。',
            verbose=True,
            llm=self.llm,
            tools=[self.tools[0], self.tools[4]]  # Excel分析工具 + 搜索工具
        )
        
        # 文档处理专家
        document_processor = Agent(
            role='文档处理专家',
            goal='处理文档，提取关键信息',
            backstory='你是一位专业的文档处理专家，能够快速准确地提取文档中的关键信息。',
            verbose=True,
            llm=self.llm,
            tools=[self.tools[1]]  # 文档处理工具
        )
        
        # 邮件管理专家
        email_manager = Agent(
            role='邮件管理专家',
            goal='管理邮件，撰写和发送邮件',
            backstory='你是一位专业的邮件管理专家，能够高效地处理各种邮件任务。',
            verbose=True,
            llm=self.llm,
            tools=[self.tools[2]]  # 邮件管理工具
        )
        
        # 报告生成专家
        report_generator = Agent(
            role='报告生成专家',
            goal='生成报告，总结工作内容',
            backstory='你是一位专业的报告生成专家，能够将复杂的信息整理成清晰易懂的报告。',
            verbose=True,
            llm=self.llm,
            tools=[self.tools[3]]  # 报告生成工具
        )
        
        return [data_analyst, document_processor, email_manager, report_generator]
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            message: 用户消息
            context: 上下文信息
            
        Returns:
            处理结果
        """
        try:
            # 构建上下文
            if context is None:
                context = {}
            
            # 创建任务
            task = Task(
                description=f"""
                用户请求: {message}
                
                上下文信息:
                - 文件: {context.get('files', [])}
                - 数据: {context.get('data', [])}
                
                请根据用户请求，选择合适的工具和智能体来完成任务。
                """,
                expected_output="详细的处理结果和建议",
                agent=self.agents[0]  # 默认使用数据分析专家
            )
            
            # 执行任务
            result = self.crew.kickoff([task])
            
            return {
                "success": True,
                "result": str(result),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def process_multi_turn_conversation(self, messages: List[Dict[str, str]], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理多轮对话
        
        Args:
            messages: 消息列表
            context: 上下文信息
            
        Returns:
            处理结果
        """
        try:
            results = []
            
            for message in messages:
                result = self.process_message(message['content'], context)
                results.append(result)
                
                # 更新上下文
                if context is None:
                    context = {}
                context['previous_result'] = result
            
            return {
                "success": True,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def main():
    """主函数 - 用于测试"""
    
    # 创建智能体 - 使用千问API
    agent = OfficeAgent(
        api_key=QWEN_API_KEY,
        model=QWEN_MODEL
    )
    
    # 测试消息
    test_messages = [
        "你好，我是新用户，请介绍一下你的功能",
        "我有一个Excel文件，请帮我分析数据",
        "请帮我写一封邮件给老板，汇报工作进度"
    ]
    
    for message in test_messages:
        print(f"\n用户: {message}")
        result = agent.process_message(message)
        print(f"智能体: {result.get('result', result.get('error', '未知错误'))}")


if __name__ == "__main__":
    # 从命令行参数读取消息
    if len(sys.argv) > 1:
        # 从文件读取输入
        input_file = sys.argv[1]
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        # 创建智能体
        agent = OfficeAgent(
            api_key=input_data.get('api_key', ''),
            model=input_data.get('model', 'gpt-4')
        )
        
        # 处理消息
        if 'messages' in input_data:
            result = agent.process_multi_turn_conversation(
                input_data['messages'],
                input_data.get('context')
            )
        else:
            result = agent.process_message(
                input_data.get('message', ''),
                input_data.get('context')
            )
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 运行测试
        main()
