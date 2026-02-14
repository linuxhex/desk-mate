#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的图表生成流程
"""

import sys
import json
from smart_chart_selector import SmartChartSelector

# 创建图表选择器
chart_selector = SmartChartSelector()

# 测试数据
test_data = [
    {"城市": "北京", "数量": 100},
    {"城市": "上海", "数量": 80},
    {"城市": "广州", "数量": 60},
    {"城市": "深圳", "数量": 50}
]

# 生成图表
result = chart_selector.generate_smart_chart(test_data, "测试图表", "测试标题")

# 模拟format_function_result函数的处理
if result.get('success'):
    # 返回图表配置数据（JSON格式），而不是base64图片
    chart_config = {
        'chart_type': result.get('chart_type', 'unknown'),
        'title': result.get('title', ''),
        'reason': result.get('reason', ''),
        'data': test_data  # 返回原始数据，让前端渲染
    }
    # 使用ECHARTS:标记，让前端使用ECharts渲染
    chart_json = json.dumps(chart_config, ensure_ascii=False)
    formatted_result = f"[ECHARTS:{chart_json}:END_ECHARTS]"
    print("格式化后的图表结果:")
    print(formatted_result)
    print("\n图表配置:")
    print(json.dumps(chart_config, ensure_ascii=False, indent=2))
else:
    print(f"图表生成失败: {result.get('error', '未知错误')}")
