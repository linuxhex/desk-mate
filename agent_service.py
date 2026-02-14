#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
办公助手HTTP服务
提供高性能的API接口，避免重复启动Python解释器
"""

import os
import json
import sys
import time
import re
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import lru_cache
import hashlib
import time as time_module

# 导入功能模块
try:
    from office_functions import OfficeFunctions
    office_functions = OfficeFunctions()
except ImportError:
    print("警告: 无法导入office_functions模块，部分功能将不可用")
    office_functions = None

# 导入天气功能模块
try:
    from weather_functions import WeatherFunctions
    weather_functions = WeatherFunctions()
except ImportError:
    print("警告: 无法导入weather_functions模块，天气查询功能将不可用")
    weather_functions = None

# 导入图表生成模块
try:
    from chart_generator import ChartGenerator
    chart_generator = ChartGenerator()
except ImportError:
    print("警告: 无法导入chart_generator模块，图表生成功能将不可用")
    chart_generator = None

# 导入Word文档处理模块
try:
    from word_functions import WordFunctions
    word_functions = WordFunctions()
except ImportError:
    print("警告: 无法导入word_functions模块，Word文档处理功能将不可用")
    word_functions = None

# 导入PDF文档处理模块
try:
    from pdf_functions import PDFFunctions
    pdf_functions = PDFFunctions()
except ImportError:
    print("警告: 无法导入pdf_functions模块，PDF文档处理功能将不可用")
    pdf_functions = None

# 导入智能图表选择模块
try:
    from smart_chart_selector import SmartChartSelector
    smart_chart_selector = SmartChartSelector()
except ImportError:
    print("警告: 无法导入smart_chart_selector模块，智能图表选择功能将不可用")
    smart_chart_selector = None

# 缓存
cache = {
    'weather': {},
    'system_info': None,
    'directories': {},
    'common_answers': {}  # 常见问题缓存
}

# 常见问题预设答案
COMMON_ANSWERS = {
    '你好': '您好！我是您的办公助手，可以帮助您处理Excel数据、文档、邮件等各类办公任务。请问有什么我可以帮您的吗？',
    '你是谁': '我是您的办公助手，可以帮助您处理Excel数据、文档、邮件等各类办公任务。我可以：\n1. Excel数据分析和可视化\n2. 文档处理和转换\n3. 文件系统操作\n4. 天气查询\n5. 系统信息查询\n\n请问有什么我可以帮您的吗？',
    '你能做什么': '我可以帮您处理以下任务：\n1. Excel数据分析和可视化\n2. 文档处理和转换\n3. 文件系统操作（浏览目录、读取文件、创建文件等）\n4. 天气查询\n5. 系统信息查询\n6. 邮件管理和发送\n7. 生成报告和总结\n\n请告诉我您的具体需求，我会为您提供专业的帮助。',
    '谢谢': '不客气！如果还有其他问题，随时可以问我。',
    '再见': '再见！祝您工作顺利！'
}

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局智能体实例
agents = {}  # 存储不同会话的智能体实例


class OfficeAgentService:
    """办公智能体服务"""
    
    # AI平台配置
    AI_PLATFORMS = {
        'qwen': {
            'name': '千问（Qwen）',
            'api_key': 'iNjoFN6OE1BS_tio6SWa478Dw6DPbIuKpccEOp7wKOh_f3xf6eDxS0EGgHTYYJG-j3tp-TdGuNATgl0l2WJ0wQ',
            'api_endpoint': 'https://api.modelarts-maas.com/openai/v1/chat/completions',
            'model': 'qwen3-coder-480b-a35b-instruct',
            'description': '中文理解能力强，适合办公场景',
            'strengths': ['Excel数据分析', '中文文档处理', '办公任务']
        },
        'deepseek': {
            'name': 'DeepSeek',
            'api_key': '',  # 需要用户配置
            'api_endpoint': 'https://api.deepseek.com/v1/chat/completions',
            'model': 'deepseek-chat',
            'description': '代码能力强，适合技术任务',
            'strengths': ['代码生成', '技术问题解决', '编程辅助']
        },
        'kimi': {
            'name': 'Kimi',
            'api_key': '',  # 需要用户配置
            'api_endpoint': 'https://api.moonshot.cn/v1/chat/completions',
            'model': 'moonshot-v1-8k',
            'description': '长文本处理能力强，适合文档分析',
            'strengths': ['长文档分析', '内容总结', '深度理解']
        },
        'yuanbao': {
            'name': '元宝',
            'api_key': '',  # 需要用户配置
            'api_endpoint': 'https://api.yuanbao.tencent.com/v1/chat/completions',
            'model': 'yuanbao-chat',
            'description': '综合能力强，适合多场景',
            'strengths': ['多任务处理', '智能对话', '内容创作']
        },
        'doubao': {
            'name': '豆包',
            'api_key': '',  # 需要用户配置
            'api_endpoint': 'https://api.doubao.com/v1/chat/completions',
            'model': 'doubao-chat',
            'description': '交互能力强，适合日常对话',
            'strengths': ['日常对话', '知识问答', '娱乐互动']
        }
    }
    
    def __init__(self, api_key: str = None, api_endpoint: str = None, model: str = None, platform: str = 'qwen'):
        """
        初始化办公智能体
        
        Args:
            api_key: API密钥（可选）
            api_endpoint: API endpoint（可选）
            model: 使用的模型（可选）
            platform: 使用的平台（默认为千问）
        """
        # 如果指定了平台，使用平台的配置
        if platform in self.AI_PLATFORMS:
            platform_config = self.AI_PLATFORMS[platform]
            self.api_key = platform_config['api_key']
            self.api_endpoint = platform_config['api_endpoint']
            self.model = platform_config['model']
            self.current_platform = platform
        else:
            # 向后兼容：使用传入的参数
            self.api_key = api_key or 'iNjoFN6OE1BS_tio6SWa478Dw6DPbIuKpccEOp7wKOh_f3xf6eDxS0EGgHTYYJG-j3tp-TdGuNATgl0l2WJ0wQ'
            self.api_endpoint = api_endpoint or 'https://api.modelarts-maas.com/openai/v1/chat/completions'
            self.model = model or 'qwen3-coder-480b-a35b-instruct'
            self.current_platform = 'qwen'
        
        self.conversation_history = []
    
    def recommend_platform(self, user_message: str) -> str:
        """
        根据用户消息推荐最适合的AI平台
        
        Args:
            user_message: 用户消息
            
        Returns:
            推荐的平台名称
        """
        message_lower = user_message.lower()
        
        # 根据关键词推荐平台
        if any(keyword in message_lower for keyword in ['代码', '编程', 'bug', 'debug', '开发', '技术']):
            return 'deepseek'
        elif any(keyword in message_lower for keyword in ['文档', '总结', '长文本', '论文', '报告']):
            return 'kimi'
        elif any(keyword in message_lower for keyword in ['日常', '聊天', '娱乐', '闲聊', '笑话']):
            return 'doubao'
        elif any(keyword in message_lower for keyword in ['创作', '写作', '文案', '内容']):
            return 'yuanbao'
        else:
            # 默认使用千问
            return 'qwen'
    
    def detect_simple_function(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        检测是否是简单功能（不需要调用API）
        
        Args:
            user_message: 用户消息
            
        Returns:
            功能调用信息，如果不是简单功能则返回None
        """
        message_lower = user_message.lower()
        
        # 检测系统信息查询
        if '系统信息' in message_lower or '电脑配置' in message_lower:
            return {
                'function': 'get_system_info',
                'parameters': {}
            }
        
        # 检测文件浏览
        if any(keyword in message_lower for keyword in ['桌面', '文件夹', '目录', '查看文件']):
            return {
                'function': 'list_directory',
                'parameters': {'path': None}
            }
        
        return None
    
    def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行功能
        
        Args:
            function_name: 功能名称
            parameters: 参数
            
        Returns:
            执行结果
        """
        # 检查缓存
        if function_name == 'get_weather':
            city = parameters.get('city', '南京')
            cache_key = f"weather_{city}"
            
            # 检查缓存是否有效（30分钟）
            if cache_key in cache['weather']:
                cached_data = cache['weather'][cache_key]
                if time.time() - cached_data['timestamp'] < 1800:  # 30分钟
                    return cached_data['data']
            
            # 执行功能
            if weather_functions:
                result = weather_functions.get_weather(city)
                # 缓存结果
                cache['weather'][cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                return result
            else:
                return {'success': False, 'error': '天气查询功能不可用'}
        
        elif function_name == 'get_system_info':
            # 检查缓存
            if cache['system_info'] and time.time() - cache['system_info']['timestamp'] < 3600:  # 1小时
                return cache['system_info']['data']
            
            # 执行功能
            if office_functions:
                result = office_functions.get_system_info()
                # 缓存结果
                cache['system_info'] = {
                    'data': result,
                    'timestamp': time.time()
                }
                return result
            else:
                return {'success': False, 'error': '系统信息查询功能不可用'}
        
        elif function_name == 'list_directory':
            path = parameters.get('path')
            
            # 检查缓存
            cache_key = f"dir_{path}"
            if cache_key in cache['directories']:
                cached_data = cache['directories'][cache_key]
                if time.time() - cached_data['timestamp'] < 60:  # 1分钟
                    return cached_data['data']
            
            # 执行功能
            if office_functions:
                result = office_functions.list_directory(path)
                # 缓存结果
                cache['directories'][cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                return result
            else:
                return {'success': False, 'error': '文件浏览功能不可用'}
        
        elif function_name == 'read_file':
            if office_functions:
                return office_functions.read_file(parameters.get('file_path'))
            else:
                return {'success': False, 'error': '文件读取功能不可用'}
        
        elif function_name == 'create_file':
            if office_functions:
                return office_functions.create_file(
                    parameters.get('file_path'),
                    parameters.get('content', '')
                )
            else:
                return {'success': False, 'error': '文件创建功能不可用'}
        
        elif function_name == 'generate_chart':
            if chart_generator:
                return chart_generator.generate_chart(
                    parameters.get('chart_type', 'bar'),
                    parameters.get('data', {}),
                    parameters.get('title', ''),
                    parameters.get('options', {})
                )
            else:
                return {'success': False, 'error': '图表生成功能不可用'}
        
        elif function_name == 'copy_excel_file':
            if office_functions:
                return office_functions.copy_excel_file(
                    parameters.get('source_file'),
                    parameters.get('data', []),
                    parameters.get('output_file')
                )
            else:
                return {'success': False, 'error': 'Excel文件复制功能不可用'}
        
        elif function_name == 'analyze_excel_data':
            if office_functions:
                return office_functions.analyze_excel_data(
                    parameters.get('data', []),
                    parameters.get('analysis_type', 'general')
                )
            else:
                return {'success': False, 'error': 'Excel数据分析功能不可用'}
        
        elif function_name == 'create_analysis_excel':
            if office_functions:
                return office_functions.create_analysis_excel(
                    parameters.get('data', []),
                    parameters.get('analysis_result', {}),
                    parameters.get('output_file')
                )
            else:
                return {'success': False, 'error': '分析结果Excel创建功能不可用'}
        
        elif function_name == 'read_word_file':
            if word_functions:
                return word_functions.read_word_file(parameters.get('file_path'))
            else:
                return {'success': False, 'error': 'Word文档读取功能不可用'}
        
        elif function_name == 'create_word_file':
            if word_functions:
                return word_functions.create_word_file(
                    parameters.get('file_path'),
                    parameters.get('content', ''),
                    parameters.get('title', '')
                )
            else:
                return {'success': False, 'error': 'Word文档创建功能不可用'}
        
        elif function_name == 'read_pdf_file':
            if pdf_functions:
                return pdf_functions.read_pdf_file(parameters.get('file_path'))
            else:
                return {'success': False, 'error': 'PDF文档读取功能不可用'}
        
        elif function_name == 'create_pdf_file':
            if pdf_functions:
                return pdf_functions.create_pdf_file(
                    parameters.get('file_path'),
                    parameters.get('content', ''),
                    parameters.get('title', '')
                )
            else:
                return {'success': False, 'error': 'PDF文档创建功能不可用'}
        
        elif function_name == 'generate_smart_chart':
            if smart_chart_selector:
                return smart_chart_selector.generate_smart_chart(
                    parameters.get('data', []),
                    parameters.get('context', ''),
                    parameters.get('title', '')
                )
            else:
                return {'success': False, 'error': '智能图表生成功能不可用'}
        
        else:
            return {'success': False, 'error': f'未知功能: {function_name}'}
    
    def format_function_result(self, function_name: str, result: Dict[str, Any], parameters: Dict[str, Any] = None) -> str:
        """
        格式化功能结果为用户友好的文本
        
        Args:
            function_name: 功能名称
            result: 执行结果
            parameters: 功能参数（可选）
            
        Returns:
            格式化的文本
        """
        if parameters is None:
            parameters = {}
        if not result.get('success'):
            return f"执行失败: {result.get('error', '未知错误')}"
        
        if function_name == 'get_weather':
            data = result
            return f"""
{data.get('city', '未知')}天气：
温度：{data.get('temperature', 'N/A')}°C（体感温度：{data.get('feels_like', 'N/A')}°C）
天气：{data.get('description', 'N/A')}
湿度：{data.get('humidity', 'N/A')}%
风速：{data.get('wind_speed', 'N/A')} km/h（{data.get('wind_direction', 'N/A')}）
气压：{data.get('pressure', 'N/A')} mb
能见度：{data.get('visibility', 'N/A')} km
紫外线指数：{data.get('uv_index', 'N/A')}
"""
        
        elif function_name == 'get_system_info':
            data = result
            return f"""
系统信息：
操作系统：{data.get('system', 'N/A')} {data.get('release', '')}
计算机名：{data.get('node', 'N/A')}
处理器：{data.get('processor', 'N/A')}
架构：{data.get('machine', 'N/A')}
Python版本：{data.get('python_version', 'N/A')}
用户目录：{data.get('user', 'N/A')}
桌面路径：{data.get('desktop', 'N/A')}
"""
        
        elif function_name == 'list_directory':
            data = result
            items = data.get('items', [])
            output = f"目录：{data.get('directory', 'N/A')}\n"
            output += f"共 {data.get('count', 0)} 个项目\n\n"
            
            # 分类显示
            folders = [item for item in items if item.get('is_directory')]
            files = [item for item in items if not item.get('is_directory')]
            
            if folders:
                output += "文件夹：\n"
                for folder in folders[:10]:  # 只显示前10个
                    output += f"  📁 {folder.get('name', 'N/A')}\n"
                if len(folders) > 10:
                    output += f"  ... 还有 {len(folders) - 10} 个文件夹\n"
            
            if files:
                output += "\n文件：\n"
                for file in files[:10]:  # 只显示前10个
                    size = file.get('size', 0)
                    size_str = f"{size} B" if size < 1024 else f"{size // 1024} KB"
                    output += f"  📄 {file.get('name', 'N/A')} ({size_str})\n"
                if len(files) > 10:
                    output += f"  ... 还有 {len(files) - 10} 个文件\n"
            
            return output
        
        elif function_name == 'generate_smart_chart':
            # 处理图表生成结果
            print(f"图表生成结果: {result}")
            if result.get('success'):
                # 检查是否有漏斗数据
                funnel_data = result.get('funnel_data')
                
                # 构建图表配置
                chart_config = {
                    'chart_type': result.get('chart_type', 'unknown'),
                    'title': result.get('title', ''),
                    'reason': result.get('reason', ''),
                    'data': funnel_data if funnel_data else parameters.get('data', [])  # 如果有漏斗数据，使用漏斗数据
                }
                # 使用ECHARTS:标记，让前端使用ECharts渲染
                import json as json_module
                chart_json = json_module.dumps(chart_config, ensure_ascii=False)
                formatted_result = f"[ECHARTS:{chart_json}:END_ECHARTS]"
                print(f"格式化后的图表结果: {formatted_result[:200]}...")
                return formatted_result
            else:
                return f"图表生成失败: {result.get('error', '未知错误')}"
        
        else:
            return json.dumps(result, ensure_ascii=False, indent=2)
    
    def call_qwen_api(self, messages: List[Dict[str, str]]) -> str:
        """
        调用千问API
        
        Args:
            messages: 消息列表
            
        Returns:
            API响应
        """
        try:
            import requests
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.api_key
            }
            
            data = {
                'model': self.model,
                'messages': messages,
                'temperature': 0.5,  # 降低temperature，提高响应速度
                'max_tokens': 1000,  # 减少max_tokens，提高响应速度
                'top_p': 0.9,  # 添加top_p参数
                'frequency_penalty': 0.0,  # 添加frequency_penalty参数
                'presence_penalty': 0.0  # 添加presence_penalty参数
            }
            
            # 增加重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        self.api_endpoint,
                        headers=headers,
                        json=data,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                        return "API请求失败: " + str(response.status_code) + " - " + response.text
                        
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return "调用API超时，请稍后重试"
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return "调用API失败: " + str(e)
                
        except Exception as e:
            return "调用API失败: " + str(e)
    
    def _format_context_info(self, context: Dict[str, Any]) -> str:
        """
        格式化上下文信息，使用提示词压缩技术，保留关键信息
        
        Args:
            context: 上下文信息
            
        Returns:
            格式化后的上下文信息字符串
        """
        context_info = "\n\n上下文信息：\n"
        
        # 处理文件列表
        if 'files' in context and context['files']:
            context_info += f"文件: {', '.join(context['files'])}\n"
        
        # 处理数据列表（Excel数据）
        if 'data' in context and context['data']:
            data_list = context['data']
            if isinstance(data_list, list) and len(data_list) > 0:
                # 使用提示词压缩技术，保留关键信息
                context_info += f"数据概览：\n"
                context_info += f"- 数据集数量: {len(data_list)}\n"
                
                # 对每个数据集进行压缩处理
                for i, data in enumerate(data_list):
                    if isinstance(data, list):
                        context_info += f"- 数据集{i+1}: {len(data)}行\n"
                        
                        # 提取关键信息：列名、数据类型、统计信息
                        if len(data) > 0 and isinstance(data[0], dict):
                            # 提取列名
                            columns = list(data[0].keys())
                            context_info += f"  列名: {', '.join(columns[:10])}"
                            if len(columns) > 10:
                                context_info += f" ... (共{len(columns)}列)"
                            context_info += "\n"
                            
                            # 提取数据类型和统计信息
                            numeric_cols = []
                            text_cols = []
                            
                            for col in columns:
                                values = [row.get(col) for row in data if row.get(col) is not None]
                                if values and isinstance(values[0], (int, float)):
                                    numeric_cols.append(col)
                                else:
                                    text_cols.append(col)
                            
                            if numeric_cols:
                                context_info += f"  数值列: {', '.join(numeric_cols[:5])}"
                                if len(numeric_cols) > 5:
                                    context_info += f" ... (共{len(numeric_cols)}列)"
                                context_info += "\n"
                            
                            if text_cols:
                                context_info += f"  文本列: {', '.join(text_cols[:5])}"
                                if len(text_cols) > 5:
                                    context_info += f" ... (共{text_cols}列)"
                                context_info += "\n"
                            
                            # 显示前3行数据作为示例
                            context_info += f"  示例数据（前3行）:\n"
                            for j, row in enumerate(data[:3]):
                                # 只显示前5个字段
                                fields = list(row.items())[:5]
                                row_str = ", ".join([f"{k}: {v}" for k, v in fields])
                                context_info += f"    {row_str}\n"
                        else:
                            context_info += f"  数据类型: {type(data[0]).__name__}\n"
        
        # 限制总长度，但保留关键信息
        if len(context_info) > 8000:
            # 压缩提示词，但保留关键信息
            context_info = context_info[:8000] + "\n... (数据已压缩，保留关键信息)"
        
        return context_info
    
    def process_message(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """
        处理用户消息
        
        Args:
            user_message: 用户消息
            context: 上下文信息
            
        Returns:
            智能体响应
        """
        print(f"\n{'='*60}")
        print(f"开始处理消息: {user_message}")
        print(f"上下文信息: {context.keys() if context else 'None'}")
        
        # 第零步：检查是否是常见问题（最快）
        message_lower = user_message.lower().strip()
        for key, answer in COMMON_ANSWERS.items():
            if key in message_lower or message_lower in key:
                return answer
        
        # 第一步：检测是否是简单功能
        simple_function = self.detect_simple_function(user_message)
        
        if simple_function:
            # 直接执行功能，不调用API
            function_name = simple_function['function']
            parameters = simple_function['parameters']
            
            print(f"检测到简单功能: {function_name}")
            print(f"参数: {parameters}")
            
            result = self.execute_function(function_name, parameters)
            formatted_result = self.format_function_result(function_name, result)
            
            print(f"执行结果: {formatted_result[:100]}...")
            
            # 保存到历史
            self.conversation_history.append({'role': 'user', 'content': user_message})
            self.conversation_history.append({'role': 'assistant', 'content': formatted_result})
            
            # 限制历史长度
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return formatted_result
        
        # 第二步：对于复杂功能，调用API
        print("未检测到简单功能，准备调用API...")
        
        # 智能推荐平台
        recommended_platform = self.recommend_platform(user_message)
        if recommended_platform != self.current_platform:
            print(f"智能推荐切换到平台: {recommended_platform}")
            # 切换到推荐的平台
            if recommended_platform in self.AI_PLATFORMS:
                platform_config = self.AI_PLATFORMS[recommended_platform]
                self.api_key = platform_config['api_key']
                self.api_endpoint = platform_config['api_endpoint']
                self.model = platform_config['model']
                self.current_platform = recommended_platform
                print(f"已切换到平台: {platform_config['name']}")
        
        system_prompt = f"""你是一个专业的办公助手，擅长处理Excel数据、文档、邮件等办公任务。

你的能力包括：
1. Excel数据分析和可视化
2. Word文档处理和转换
3. PDF文档处理和转换
4. 文件系统操作（浏览目录、读取文件、创建文件等）
5. 邮件管理和发送
6. 生成报告和总结
7. 天气查询
8. 网络搜索和信息查询
9. 系统信息查询
10. 智能图表生成和展示

重要提示：
- 如果用户上传了Excel文件，数据已经在上下文信息中，请直接分析数据，不要调用read_file或list_directory
- 只有当用户需要查看桌面或文件夹内容时，才调用list_directory
- 只有当用户需要读取未上传的文件时，才调用read_file
- **图表生成要求**：当用户要求分析数据或生成图表时，必须自动调用generate_smart_chart功能，系统会根据数据特征自动选择最优图表类型（柱状图、饼图、折线图、散点图、雷达图、漏斗图、表格等）
- **图表结果处理**：generate_smart_chart功能会返回[ECHARTS:...:END_ECHARTS]格式的数据，这是图表配置数据，前端会自动渲染图表，**AI不需要处理图表数据，只需要直接返回给用户即可，不要说"遇到了技术问题"**
- **重要提示**：当功能执行结果包含[ECHARTS:...:END_ECHARTS]格式的数据时，这是图表配置数据，前端会自动渲染图表，AI只需要简单说明"图表已生成"即可，不要说"遇到了技术问题"或"技术问题"
- **特别说明**：[ECHARTS:...:END_ECHARTS]格式的数据是图表配置数据，前端会自动识别并渲染图表，AI不需要处理这些数据，只需要直接返回给用户即可，不要说"遇到了技术问题"或"技术问题"，不要尝试解析或处理这些数据
- **数据准确性要求**：分析Excel数据时，必须基于表格中真实存在的数据进行分析，绝对禁止编造不存在的数据（如"今日头条"、"百度"等）
- 如果表格中没有某列或某行，明确告知用户，不要编造数据
- 分析结果必须准确反映表格内容，不要编造任何数据
- **一次性处理要求**：必须一次性处理全部数据，绝对禁止分批处理数据，避免数据丢失
- **结果汇总要求**：如果需要分批处理，必须汇总所有分批的结果，只在所有分批完成后才在对话框展示最终结果
- 当用户需要以下操作时，请使用以下格式调用功能：

查看桌面或文件夹内容：
<function_call>{"function": "list_directory", "parameters": {"path": "路径"}}</function_call>

读取文件内容（仅用于未上传的文件）：
<function_call>{"function": "read_file", "parameters": {"file_path": "文件路径"}}</function_call>

创建文件：
<function_call>{"function": "create_file", "parameters": {"file_path": "文件路径", "content": "文件内容"}}</function_call>

复制Excel文件（用于已上传的Excel文件）：
<function_call>{"function": "copy_excel_file", "parameters": {"source_file": "源文件路径", "data": [数据列表], "output_file": "输出文件路径（可选）", "columns": "要写入的列名列表（可选）", "rows": "要写入的行号列表（可选）", "sheet_name": "工作表名称（可选）"}}</function_call>

分析Excel数据（用于已上传的Excel文件）：
<function_call>{"function": "analyze_excel_data", "parameters": {"data": [数据列表], "analysis_type": "recruitment"}}</function_call>

**生成图表（用于已上传的Excel文件，当用户要求分析数据或生成图表时，必须调用此功能）：**
<function_call>{"function": "generate_smart_chart", "parameters": {"data": [数据列表], "context": "分析上下文", "title": "图表标题"}}</function_call>

**重要：当用户要求分析数据或生成图表时，必须调用generate_smart_chart功能，而不是analyze_excel_data功能！**

创建包含分析结果的Excel文件：
<function_call>{"function": "create_analysis_excel", "parameters": {"data": [数据列表], "analysis_result": {分析结果}, "output_file": "输出文件路径"}}</function_call>

读取Word文档：
<function_call>{"function": "read_word_file", "parameters": {"file_path": "文件路径"}}</function_call>

创建Word文档：
<function_call>{"function": "create_word_file", "parameters": {"file_path": "文件路径", "content": "文档内容", "title": "文档标题（可选）"}}</function_call>

读取PDF文档：
<function_call>{"function": "read_pdf_file", "parameters": {"file_path": "文件路径"}}</function_call>

创建PDF文档：
<function_call>{"function": "create_pdf_file", "parameters": {"file_path": "文件路径", "content": "文档内容", "title": "文档标题（可选）"}}</function_call>

智能生成图表（自动选择最优图表类型）：
<function_call>{"function": "generate_smart_chart", "parameters": {"data": [数据列表], "context": "上下文信息", "title": "图表标题（可选）"}}</function_call>

查询天气：
<function_call>{"function": "get_weather", "parameters": {"city": "城市名"}}</function_call>

获取系统信息：
<function_call>{"function": "get_system_info", "parameters": {}}

请用简洁、专业的语言回答用户的问题。如果用户上传了文件，请根据文件内容提供相应的建议和帮助。

重要提示：
- 当用户要求分析Excel数据时，先调用analyze_excel_data进行分析，然后根据分析结果回答用户问题
- 当用户要求将分析结果保存到新Excel文件时，先调用analyze_excel_data，然后调用create_analysis_excel创建文件
- 当用户要求复制或创建新的Excel文件时，使用copy_excel_file功能，并传入已上传的数据
- 当用户要求生成图表时，使用generate_smart_chart功能，系统会自动选择最优图表类型
- 当创建文件时，请明确告知用户文件的保存位置
- 当读取文件时，请说明文件的内容和大小
- 当浏览目录时，请列出主要的文件和文件夹
- 如果用户没有指定路径，默认使用桌面路径
- 当查询天气时，请提供详细的天气信息
- 不要在回复中显示功能调用的过程，直接返回最终结果"""
        
        # 构建消息列表
        messages = [
            {'role': 'system', 'content': system_prompt}
        ]
        
        # 添加历史对话
        for msg in self.conversation_history:
            messages.append(msg)
        
        # 添加当前消息
        messages.append({'role': 'user', 'content': user_message})
        
        # 如果有上下文信息，添加到消息中
        if context:
            # 处理上下文信息，避免超过API长度限制
            context_info = self._format_context_info(context)
            messages[-1]['content'] += context_info
            print(f"添加上下文信息，长度: {len(context_info)}")
        
        # 调用API
        print("调用API...")
        response = self.call_qwen_api(messages)
        print(f"API响应长度: {len(response)}")
        print(f"API响应前200字符: {response[:200]}")
        
        # 检查是否有功能调用（支持两种格式：<function_call>和直接JSON）
        function_calls = []
        
        # 格式1: <function_call>{"function": "xxx", "parameters": {}}</function_call>
        if '<function_call>' in response and office_functions:
            print("检测到<function_call>格式的功能调用...")
            function_calls = re.findall(r'<function_call>(.*?)</function_call>', response, re.DOTALL)
        
        # 格式2: 直接的JSON格式 {"function": "xxx", "parameters": {}}
        elif '{' in response and '"function"' in response:
            print("检测到JSON格式的功能调用...")
            # 尝试提取JSON格式的函数调用
            # 查找包含"function"的JSON对象
            json_start = response.find('{"function"')
            if json_start != -1:
                # 找到匹配的结束位置
                json_end = json_start
                brace_count = 0
                for i in range(json_start, len(response)):
                    if response[i] == '{':
                        brace_count += 1
                    elif response[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                if json_end > json_start:
                    json_str = response[json_start:json_end]
                    try:
                        # 验证是否是有效的JSON
                        json_data = json.loads(json_str)
                        if 'function' in json_data:
                            function_calls.append(json_str)
                            print(f"找到有效的函数调用JSON: {json_str[:100]}...")
                    except Exception as e:
                        print(f"JSON解析失败: {e}")
        
        if function_calls:
            print(f"发现 {len(function_calls)} 个功能调用")
            # 执行功能调用
            function_results = []
            
            for call_str in function_calls:
                try:
                    # 处理不同格式的函数调用
                    if call_str.startswith('{'):
                        # 直接JSON格式
                        call_data = json.loads(call_str)
                    else:
                        # <function_call>格式
                        call_data = json.loads(call_str)
                    
                    function_name = call_data.get('function')
                    parameters = call_data.get('parameters', {})
                    
                    print(f"\n调用功能: {function_name}")
                    print(f"参数: {json.dumps(parameters, ensure_ascii=False, indent=2)}")
                    
                    # 执行功能
                    result = self.execute_function(function_name, parameters)
                    
                    print(f"执行结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    
                    # 格式化功能结果
                    formatted_result = self.format_function_result(function_name, result, parameters)
                    print(f"格式化后的结果: {formatted_result[:200] if len(formatted_result) > 200 else formatted_result}")
                        
                    function_results.append({
                        'function': function_name,
                        'result': formatted_result
                    })
                except Exception as e:
                    print(f"功能调用失败: {str(e)}")
                    function_results.append({
                        'function': 'unknown',
                        'result': {'success': False, 'error': str(e)}
                    })
                
                # 将功能结果添加到消息中，再次调用API
                function_result_str = "\n\n功能执行结果：\n"
                for fr in function_results:
                    function_result_str += f"\n功能: {fr['function']}\n"
                    # 检查结果是否包含[ECHARTS:...:END_ECHARTS]格式的数据
                    if isinstance(fr['result'], str) and '[ECHARTS:' in fr['result'] and ':END_ECHARTS]' in fr['result']:
                        # 如果结果已经是ECHARTS格式的字符串，直接返回
                        print(f"检测到图表数据，直接返回给前端")
                        print(f"返回的图表数据: {fr['result'][:200]}...")
                        return fr['result']
                    # 否则，格式化结果
                    result_str = json.dumps(fr['result'], ensure_ascii=False, indent=2) if isinstance(fr['result'], dict) else str(fr['result'])
                    function_result_str += f"结果: {result_str}\n"
                
                print(f"功能结果字符串: {function_result_str[:500]}...")
                
                messages.append({'role': 'assistant', 'content': response})
                messages.append({'role': 'user', 'content': function_result_str + "\n请根据这些结果回答用户的问题。"})
                
                # 再次调用API获取最终响应
                response = self.call_qwen_api(messages)
        
        # 保存到历史
        self.conversation_history.append({'role': 'user', 'content': user_message})
        self.conversation_history.append({'role': 'assistant', 'content': response})
        
        # 限制历史长度
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        return response
    
    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.get_json()
        
        message = data.get('message', '')
        context = data.get('context', {})
        api_key = data.get('api_key', '')
        api_endpoint = data.get('api_endpoint', '')
        model = data.get('model', '')
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({
                'success': False,
                'error': '请提供消息'
            })
        
        if not api_key or not api_endpoint or not model:
            return jsonify({
                'success': False,
                'error': '缺少必要的API配置'
            })
        
        # 获取或创建智能体实例
        if session_id not in agents:
            agents[session_id] = OfficeAgentService(api_key, api_endpoint, model)
        
        agent = agents[session_id]
        
        # 处理消息
        result = agent.process_message(message, context)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/clear_history', methods=['POST'])
def clear_history():
    """清除对话历史"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        
        if session_id in agents:
            agents[session_id].clear_history()
        
        return jsonify({
            'success': True,
            'message': '对话历史已清除'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """清除缓存"""
    global cache
    cache = {
        'weather': {},
        'system_info': None,
        'directories': {}
    }
    
    return jsonify({
        'success': True,
        'message': '缓存已清除'
    })


if __name__ == '__main__':
    print("=" * 60)
    print("办公助手HTTP服务启动中...")
    print("=" * 60)
    print(f"服务地址: http://localhost:5000")
    print(f"健康检查: http://localhost:5000/health")
    print(f"聊天接口: http://localhost:5000/chat")
    print("=" * 60)
    
    # 启动Flask服务
    app.run(host='localhost', port=5000, debug=False, threaded=True)
