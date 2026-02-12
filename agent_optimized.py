#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
办公智能体 - 性能优化版本
支持异步API调用、智能功能识别、并行处理
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

# 简单功能关键词（不需要调用API的功能）
SIMPLE_FUNCTIONS = {
    '桌面': 'list_directory',
    '文件夹': 'list_directory',
    '目录': 'list_directory',
    '查看文件': 'list_directory',
    '系统信息': 'get_system_info',
    '电脑配置': 'get_system_info',
    '天气': 'get_weather',
    '气温': 'get_weather',
}

# 缓存
cache = {
    'weather': {},
    'system_info': None,
    'directories': {}
}


class OfficeAgentOptimized:
    """办公智能体 - 性能优化版本"""
    
    def __init__(self, api_key: str, api_endpoint: str, model: str):
        """
        初始化办公智能体
        
        Args:
            api_key: API密钥
            api_endpoint: API endpoint
            model: 使用的模型
        """
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.model = model
        self.conversation_history = []
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def detect_simple_function(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        检测是否是简单功能（不需要调用API）
        
        Args:
            user_message: 用户消息
            
        Returns:
            功能调用信息，如果不是简单功能则返回None
        """
        message_lower = user_message.lower()
        
        # 检测天气查询
        if '天气' in message_lower or '气温' in message_lower:
            # 提取城市名
            cities = ['南京', '北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安', '重庆']
            city = '南京'  # 默认城市
            for c in cities:
                if c in user_message:
                    city = c
                    break
            
            return {
                'function': 'get_weather',
                'parameters': {'city': city}
            }
        
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
        
        else:
            return {'success': False, 'error': f'未知功能: {function_name}'}
    
    def format_function_result(self, function_name: str, result: Dict[str, Any]) -> str:
        """
        格式化功能结果为用户友好的文本
        
        Args:
            function_name: 功能名称
            result: 执行结果
            
        Returns:
            格式化的文本
        """
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
        
        else:
            return json.dumps(result, ensure_ascii=False, indent=2)
    
    async def call_qwen_api_async(self, messages: List[Dict[str, str]]) -> str:
        """
        异步调用千问API
        
        Args:
            messages: 消息列表
            
        Returns:
            API响应
        """
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.api_key
            }
            
            data = {
                'model': self.model,
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 2000
            }
            
            # 使用异步请求
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for attempt in range(3):  # 最多重试3次
                    try:
                        async with session.post(
                            self.api_endpoint,
                            headers=headers,
                            json=data
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                return result['choices'][0]['message']['content']
                            else:
                                if attempt < 2:
                                    await asyncio.sleep(2)
                                    continue
                                return f"API请求失败: {response.status}"
                    
                    except asyncio.TimeoutError:
                        if attempt < 2:
                            await asyncio.sleep(2)
                            continue
                        return "调用API超时，请稍后重试"
                    except Exception as e:
                        if attempt < 2:
                            await asyncio.sleep(2)
                            continue
                        return f"调用API失败: {str(e)}"
        
        except Exception as e:
            return f"调用API失败: {str(e)}"
    
    def call_qwen_api(self, messages: List[Dict[str, str]]) -> str:
        """
        同步调用千问API（兼容旧版本）
        
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
                'temperature': 0.7,
                'max_tokens': 2000
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
    
    def process_message(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """
        处理用户消息 - 性能优化版本
        
        Args:
            user_message: 用户消息
            context: 上下文信息
            
        Returns:
            智能体响应
        """
        # 第一步：检测是否是简单功能
        simple_function = self.detect_simple_function(user_message)
        
        if simple_function:
            # 直接执行功能，不调用API
            function_name = simple_function['function']
            parameters = simple_function['parameters']
            
            result = self.execute_function(function_name, parameters)
            formatted_result = self.format_function_result(function_name, result)
            
            # 保存到历史
            self.conversation_history.append({'role': 'user', 'content': user_message})
            self.conversation_history.append({'role': 'assistant', 'content': formatted_result})
            
            # 限制历史长度
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return formatted_result
        
        # 第二步：对于复杂功能，调用API
        system_prompt = """你是一个专业的办公助手，擅长处理Excel数据、文档、邮件等办公任务。

你的能力包括：
1. Excel数据分析和可视化
2. 文档处理和转换
3. 文件系统操作（浏览目录、读取文件、创建文件等）
4. 邮件管理和发送
5. 生成报告和总结
6. 天气查询
7. 网络搜索和信息查询
8. 系统信息查询

当用户需要以下操作时，请使用以下格式调用功能：

查看桌面或文件夹内容：
<function_call>{"function": "list_directory", "parameters": {"path": "路径"}}</function_call>

读取文件内容：
<function_call>{"function": "read_file", "parameters": {"file_path": "文件路径"}}</function_call>

创建文件：
<function_call>{"function": "create_file", "parameters": {"file_path": "文件路径", "content": "文件内容"}}</function_call>

查询天气：
<function_call>{"function": "get_weather", "parameters": {"city": "城市名"}}</function_call>

获取系统信息：
<function_call>{"function": "get_system_info", "parameters": {}}

请用简洁、专业的语言回答用户的问题。如果用户上传了文件，请根据文件内容提供相应的建议和帮助。

重要提示：
- 当创建文件时，请明确告知用户文件的保存位置
- 当读取文件时，请说明文件的内容和大小
- 当浏览目录时，请列出主要的文件和文件夹
- 如果用户没有指定路径，默认使用桌面路径
- 当查询天气时，请提供详细的天气信息"""
        
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
            context_info = "\n\n上下文信息：\n" + json.dumps(context, ensure_ascii=False, indent=2)
            messages[-1]['content'] += context_info
        
        # 调用API
        response = self.call_qwen_api(messages)
        
        # 检查是否有功能调用
        if '<function_call>' in response and office_functions:
            # 解析功能调用
            function_calls = re.findall(r'<function_call>(.*?)</function_call>', response, re.DOTALL)
            
            if function_calls:
                # 并行执行功能调用
                function_results = []
                
                for call_str in function_calls:
                    try:
                        call_data = json.loads(call_str)
                        function_name = call_data.get('function')
                        parameters = call_data.get('parameters', {})
                        
                        # 执行功能
                        result = self.execute_function(function_name, parameters)
                        
                        function_results.append({
                            'function': function_name,
                            'result': result
                        })
                    except Exception as e:
                        function_results.append({
                            'function': 'unknown',
                            'result': {'success': False, 'error': str(e)}
                        })
                
                # 将功能结果添加到消息中，再次调用API
                function_result_str = "\n\n功能执行结果：\n"
                for fr in function_results:
                    function_result_str += f"\n功能: {fr['function']}\n"
                    function_result_str += f"结果: {json.dumps(fr['result'], ensure_ascii=False, indent=2)}\n"
                
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


def main():
    """主函数"""
    # 读取输入文件
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': '请提供输入文件路径'
        }, ensure_ascii=False))
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'读取输入文件失败: {str(e)}'
        }, ensure_ascii=False))
        sys.exit(1)
    
    # 获取参数
    message = input_data.get('message', '')
    context = input_data.get('context', {})
    api_key = input_data.get('api_key', '')
    api_endpoint = input_data.get('api_endpoint', '')
    model = input_data.get('model', '')
    
    if not api_key or not api_endpoint or not model:
        print(json.dumps({
            'success': False,
            'error': '缺少必要的API配置'
        }, ensure_ascii=False))
        sys.exit(1)
    
    if not message:
        print(json.dumps({
            'success': False,
            'error': '请提供消息'
        }, ensure_ascii=False))
        sys.exit(1)
    
    # 创建智能体
    agent = OfficeAgentOptimized(api_key, api_endpoint, model)
    
    # 处理消息
    result = agent.process_message(message, context)
    
    # 输出结果
    print(json.dumps({
        'success': True,
        'result': result
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
