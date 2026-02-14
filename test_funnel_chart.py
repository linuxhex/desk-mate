#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试漏斗图生成功能
"""

from smart_chart_selector import SmartChartSelector

# 测试数据 - 信息流线索跟进数据
test_data = [
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "广东-韶关", "是否接通": "否", "是否加上微信": "否", "是否有效意向": "否", "是否高概率可成交客户": "否"},
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "北京-北京", "角色分类": "电转电换租老司机", "意向车型": "油车", "是否有效意向": "否", "是否高概率可成交客户": "否"},
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "河北-石家庄", "是否接通": "是", "是否加上微信": "是", "是否有效意向": "否", "是否高概率可成交客户": "否"}
]

# 创建智能图表选择器实例
selector = SmartChartSelector()

# 测试转化指标计算
print("=== 测试转化指标计算 ===")
conversion_result = selector.calculate_conversion_metrics(test_data)
print(f"总线索量: {conversion_result.get('total_leads')}")
print(f"接通数: {conversion_result.get('connected_count')}")
print(f"添加微信数: {conversion_result.get('wechat_count')}")
print(f"有效意向数: {conversion_result.get('intent_count')}")
print(f"高概率成交数: {conversion_result.get('high_prob_count')}")
print(f"接通率: {conversion_result.get('connected_rate')}%")
print(f"微信添加率: {conversion_result.get('wechat_rate')}%")
print(f"有效意向率: {conversion_result.get('intent_rate')}%")
print(f"高概率成交率: {conversion_result.get('high_prob_rate')}%")
print(f"漏斗数据: {conversion_result.get('funnel_data')}")

# 测试图表生成
print("\n=== 测试图表生成 ===")
chart_result = selector.generate_smart_chart(
    test_data,
    context="信息流线索跟进数据，分析关键转化指标：接通率、微信添加率、有效意向率、高概率成交率等",
    title="信息流线索跟进转化漏斗分析"
)

print(f"图表生成成功: {chart_result.get('success')}")
print(f"图表类型: {chart_result.get('chart_type')}")
print(f"图表标题: {chart_result.get('title')}")
print(f"推荐原因: {chart_result.get('reason')}")
print(f"漏斗数据: {chart_result.get('funnel_data')}")

if chart_result.get('funnel_data'):
    print("\n=== 漏斗数据详情 ===")
    for item in chart_result.get('funnel_data'):
        print(f"{item['name']}: {item['value']} ({item['rate']}%)")

print("\n测试完成！")
