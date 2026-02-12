#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
办公智能体 - 简化版本
直接调用千问API，不需要复杂的框架
"""

import os
import json
import sys
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

# 导入requests库
try:
    import requests
except ImportError:
    print("请先安装requests: pip install requests")
    sys.exit(1)

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


class OfficeAgent:
    """办公智能体"""
    
    def __init__(self, api_key: str, api_endpoint: str, model: str):
        """
        初始化办公智能体
        
        Args:
            api_key: 千问API密钥
            api_endpoint: API endpoint
            model: 使用的模型
        """
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.model = model
        self.conversation_history = []
        
    def call_qwen_api(self, messages: List[Dict[str, str]]) -> str:
        """
        调用千问API
        
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
            
            # 增加重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        self.api_endpoint,
                        headers=headers,
                        json=data,
                        timeout=60  # 增加超时时间到60秒
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        if attempt < max_retries - 1:
                            time.sleep(2)  # 等待2秒后重试
                            continue
                        return "API请求失败: " + str(response.status_code) + " - " + response.text
                        
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        time.sleep(2)  # 等待2秒后重试
                        continue
                    return "调用API超时，请稍后重试"
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(2)  # 等待2秒后重试
                        continue
                    return "调用API失败: " + str(e)
                
        except Exception as e:
            return "调用API失败: " + str(e)
    
    def process_message(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """
        处理用户消息
        
        Args:
            user_message: 用户消息
            context: 上下文信息
            
        Returns:
            智能体响应
        """
        # 构建系统提示
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
            import re
            function_calls = re.findall(r'<function_call>(.*?)</function_call>', response, re.DOTALL)
            
            if function_calls:
                # 执行功能调用
                function_results = []
                for call_str in function_calls:
                    try:
                        call_data = json.loads(call_str)
                        function_name = call_data.get('function')
                        parameters = call_data.get('parameters', {})
                        
                        # 执行功能
                        if function_name == 'list_directory':
                            result = office_functions.list_directory(parameters.get('path'))
                        elif function_name == 'read_file':
                            result = office_functions.read_file(parameters.get('file_path'))
                        elif function_name == 'create_file':
                            result = office_functions.create_file(
                                parameters.get('file_path'),
                                parameters.get('content', '')
                            )
                        elif function_name == 'get_system_info':
                            result = office_functions.get_system_info()
                        elif function_name == 'get_weather':
                            if weather_functions:
                                result = weather_functions.get_weather(parameters.get('city', '南京'))
                            else:
                                result = {'success': False, 'error': '天气查询功能不可用'}
                        else:
                            result = {'success': False, 'error': f'未知功能: {function_name}'}
                        
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
            'error': '读取输入文件失败: ' + str(e)
        }, ensure_ascii=False))
        sys.exit(1)
    
    # 获取参数
    message = input_data.get('message', '')
    context = input_data.get('context', {})
    api_key = input_data.get('api_key', '')
    api_endpoint = input_data.get('api_endpoint', 'https://api.modelarts-maas.com/openai/v1/chat/completions')
    model = input_data.get('model', 'qwen3-coder-480b-a35b-instruct')
    
    if not api_key:
        print(json.dumps({
            'success': False,
            'error': '请提供API密钥'
        }, ensure_ascii=False))
        sys.exit(1)
    
    if not message:
        print(json.dumps({
            'success': False,
            'error': '请提供消息'
        }, ensure_ascii=False))
        sys.exit(1)
    
    # 创建智能体
    agent = OfficeAgent(api_key, api_endpoint, model)
    
    # 处理消息
    result = agent.process_message(message, context)
    
    # 输出结果
    print(json.dumps({
        'success': True,
        'result': result
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
