#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气查询功能模块
"""

import requests
import json
from typing import Dict, Any


class WeatherFunctions:
    """天气查询功能类"""
    
    def __init__(self):
        # 使用多个天气API，按优先级排序
        self.weather_apis = [
            {
                'name': 'wttr.in',
                'url': 'https://wttr.in',
                'format': 'j1'
            }
        ]
    
    def get_weather(self, city: str = "南京") -> Dict[str, Any]:
        """
        获取天气信息
        
        Args:
            city: 城市名称
            
        Returns:
            天气信息
        """
        max_retries = 2  # 减少重试次数
        timeout = 8  # 减少超时时间到8秒
        
        print(f"\n开始查询天气: {city}")
        
        for attempt in range(max_retries):
            try:
                # 使用wttr.in API
                api = self.weather_apis[0]  # 使用第一个API
                url = f"{api['url']}/{city}?format={api['format']}"
                
                print(f"尝试第{attempt + 1}次请求: {url}")
                response = requests.get(url, timeout=timeout)
                
                print(f"响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    print(f"API返回数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
                    
                    # 解析天气数据
                    current = data.get('current_condition', [{}])[0]
                    location = data.get('nearest_area', [{}])[0]
                    
                    weather_info = {
                        'success': True,
                        'city': location.get('areaName', [{}])[0].get('value', city),
                        'country': location.get('country', [{}])[0].get('value', ''),
                        'temperature': current.get('temp_C', 'N/A'),
                        'feels_like': current.get('FeelsLikeC', 'N/A'),
                        'description': current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                        'humidity': current.get('humidity', 'N/A'),
                        'wind_speed': current.get('windspeedKmph', 'N/A'),
                        'wind_direction': current.get('winddir16Point', 'N/A'),
                        'pressure': current.get('pressure', 'N/A'),
                        'visibility': current.get('visibility', 'N/A'),
                        'uv_index': current.get('uvIndex', 'N/A'),
                        'local_time': data.get('weather', [{}])[0].get('date', 'N/A')
                    }
                    
                    print(f"解析后的天气信息: {json.dumps(weather_info, ensure_ascii=False, indent=2)}")
                    
                    return weather_info
                else:
                    if attempt < max_retries - 1:
                        print(f"API请求失败，状态码: {response.status_code}")
                        continue
                    return {
                        'success': False,
                        'error': f'天气API请求失败: {response.status_code}'
                    }
                    
            except requests.exceptions.Timeout:
                print(f"请求超时: {url}")
                if attempt < max_retries - 1:
                    continue
                return {
                    'success': False,
                    'error': '天气API请求超时'
                }
            except Exception as e:
                print(f"请求异常: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                return {
                    'success': False,
                    'error': f'获取天气信息失败: {str(e)}'
                }
        
        # 如果所有重试都失败，返回错误
        print(f"天气查询失败，所有重试都已完成")
        return {
            'success': False,
            'error': '获取天气信息失败，请稍后重试'
        }
    
    def get_weather_simple(self, city: str = "南京") -> str:
        """
        获取简化的天气信息
        
        Args:
            city: 城市名称
            
        Returns:
            天气描述字符串
        """
        result = self.get_weather(city)
        
        if result['success']:
            return f"""
{result['city']}天气：
温度：{result['temperature']}°C（体感温度：{result['feels_like']}°C）
天气：{result['description']}
湿度：{result['humidity']}%
风速：{result['wind_speed']} km/h（{result['wind_direction']}）
气压：{result['pressure']} mb
能见度：{result['visibility']} km
紫外线指数：{result['uv_index']}
日期：{result['local_time']}
"""
        else:
            return f"获取天气信息失败: {result['error']}"


def main():
    """测试天气功能"""
    weather = WeatherFunctions()
    
    # 测试获取天气
    print("测试获取南京天气:")
    print(weather.get_weather_simple("南京"))
    
    print("\n测试获取北京天气:")
    print(weather.get_weather_simple("北京"))


if __name__ == '__main__':
    main()
