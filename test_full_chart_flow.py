#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的图表生成流程测试
测试从数据到图表渲染的完整流程
"""

import sys
import json
from smart_chart_selector import SmartChartSelector

# 创建图表选择器
chart_selector = SmartChartSelector()

# 测试数据（模拟用户上传的Excel数据）
test_data = [
    {"城市": "北京", "数量": 100},
    {"城市": "上海", "数量": 80},
    {"城市": "广州", "数量": 60},
    {"城市": "深圳", "数量": 50}
]

print("=" * 80)
print("完整的图表生成流程测试")
print("=" * 80)

# 步骤1：分析数据并建议图表
print("\n步骤1：分析数据并建议图表...")
analysis = chart_selector.analyze_data_and_suggest_chart(test_data, "测试图表")
print("分析结果:")
print(json.dumps(analysis, ensure_ascii=False, indent=2))

# 步骤2：生成图表
print("\n步骤2：生成图表...")
result = chart_selector.generate_smart_chart(test_data, "测试图表", "测试标题")
print("图表生成结果:")
if result.get('success'):
    print("✅ 图表生成成功！")
    print(f"图表类型: {result.get('chart_type')}")
    print(f"标题: {result.get('title')}")
    print(f"原因: {result.get('reason')}")
    if result.get('image'):
        print(f"图片数据长度: {len(result.get('image'))}")
else:
    print("❌ 图表生成失败！")
    print(f"错误: {result.get('error')}")

# 步骤3：模拟format_function_result函数的处理
print("\n步骤3：模拟format_function_result函数的处理...")
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
    print("✅ 格式化后的图表结果:")
    print(formatted_result[:200] + "...")
else:
    print("❌ 图表生成失败，无法格式化结果")

# 步骤4：检查前端是否能正确解析
print("\n步骤4：检查前端是否能正确解析...")
import re
if formatted_result and '[ECHARTS:' in formatted_result and ':END_ECHARTS]' in formatted_result:
    # 提取图表配置数据
    chart_match = re.search(r'\[ECHARTS:(.*?):END_ECHARTS\]', formatted_result)
    if chart_match:
        try:
            chart_config_parsed = json.loads(chart_match.group(1))
            print("✅ 前端可以正确解析图表配置数据:")
            print(json.dumps(chart_config_parsed, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"❌ 前端解析失败: {str(e)}")
    else:
        print("❌ 前端正则表达式匹配失败")
else:
    print("❌ 格式化结果不包含[ECHARTS:...:END_ECHARTS]标记")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
