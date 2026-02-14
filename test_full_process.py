#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的图表生成流程，包括process_message函数的处理
"""

import sys
import json
from smart_chart_selector import SmartChartSelector

# 创建图表选择器
chart_selector = SmartChartSelector()

# 测试数据（模拟用户上传的Excel数据）
test_data = [
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "广东-韶关", "是否接通": "否", "是否加上微信": "否", "是否有效意向": "否", "是否高概率可成交客户": "否"},
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "北京-北京", "角色分类": "电转电换租老司机", "意向车型": "油车", "是否有效意向": "否", "是否高概率可成交客户": "否"},
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "河北-石家庄", "是否接通": "是", "是否加上微信": "是", "是否有效意向": "否", "是否高概率可成交客户": "否"}
]

print("=" * 80)
print("测试完整的图表生成流程，包括process_message函数的处理")
print("=" * 80)

# 步骤1：生成图表
print("\n步骤1：生成图表...")
result = chart_selector.generate_smart_chart(test_data, "信息流线索跟进数据，分析各关键指标的分布情况，包括接通率、微信添加率、意向客户比例等", "信息流线索跟进关键指标分析")
print("图表生成结果:")
if result.get('success'):
    print("✅ 图表生成成功！")
    print(f"图表类型: {result.get('chart_type')}")
    print(f"标题: {result.get('title')}")
    print(f"原因: {result.get('reason')}")
else:
    print("❌ 图表生成失败！")
    print(f"错误: {result.get('error')}")

# 步骤2：模拟format_function_result函数的处理
print("\n步骤2：模拟format_function_result函数的处理...")
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
    formatted_result = None

# 步骤3：模拟process_message函数的处理
print("\n步骤3：模拟process_message函数的处理...")
if formatted_result:
    # 检查结果是否包含[ECHARTS:...:END_ECHARTS]格式的数据
    result_str = formatted_result
    if '[ECHARTS:' in result_str and ':END_ECHARTS]' in result_str:
        # 如果包含图表数据，直接返回给前端，不再调用API
        print("✅ 检测到图表数据，直接返回给前端")
        print(f"返回的结果: {result_str[:200]}...")
    else:
        print("❌ 未检测到图表数据")
else:
    print("❌ 格式化结果为空")

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
