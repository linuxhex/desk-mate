#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
办公智能体 - 简化版本
直接调用千问API，不需要复杂的框架
"""

import os
import json
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# 导入requests库
try:
    import requests
except ImportError:
    print("请先安装requests: pip install requests")
    sys.exit(1)


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
            
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return "API请求失败: " + str(response.status_code) + " - " + response.text
                
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
3. 邮件管理和发送
4. 生成报告和总结
5. 网络搜索和信息查询

请用简洁、专业的语言回答用户的问题。如果用户上传了文件，请根据文件内容提供相应的建议和帮助。"""
        
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
