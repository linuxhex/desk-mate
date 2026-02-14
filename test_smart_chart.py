#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试generate_smart_chart功能是否有问题
"""

import sys
import json
from smart_chart_selector import SmartChartSelector

# 创建图表选择器
chart_selector = SmartChartSelector()

# 测试数据（模拟用户上传的Excel数据）
test_data = [
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "广东-韶关", "是否接通": "否", "是否加上微信": "否"},
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "北京-北京", "角色分类": "电转电换租老司机", "意向车型": "油车"},
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "河北-石家庄", "是否接通": "是", "是否加上微信": "是"}
]

# 测试分析数据并建议图表
print("测试分析数据并建议图表...")
analysis = chart_selector.analyze_data_and_suggest_chart(test_data, "展示信息流线索的转化漏斗")
print("分析结果:")
print(json.dumps(analysis, ensure_ascii=False, indent=2))

# 测试生成图表
print("\n测试生成图表...")
result = chart_selector.generate_smart_chart(test_data, "展示信息流线索的转化漏斗", "线索转化漏斗分析")
print("图表生成结果:")
if result.get('success'):
    print("图表生成成功！")
    print(f"图表类型: {result.get('chart_type')}")
    print(f"标题: {result.get('title')}")
    print(f"原因: {result.get('reason')}")
    if result.get('image'):
        print(f"图片数据长度: {len(result.get('image'))}")
else:
    print("图表生成失败！")
    print(f"错误: {result.get('error')}")
