#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图表生成功能
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

# 打印结果
print("图表生成结果:")
print(json.dumps(result, ensure_ascii=False, indent=2))

# 检查是否成功
if result.get('success'):
    print("\n图表生成成功！")
    print(f"图表类型: {result.get('chart_type')}")
    print(f"标题: {result.get('title')}")
    print(f"原因: {result.get('reason')}")
    if result.get('image'):
        print(f"图片数据长度: {len(result.get('image'))}")
else:
    print("\n图表生成失败！")
    print(f"错误: {result.get('error')}")
