#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的图表生成流程
"""

from smart_chart_selector import SmartChartSelector
import json

# 测试数据 - 信息流线索跟进数据
test_data = [
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "广东-韶关", "是否接通": "否", "是否加上微信": "否", "是否有效意向": "否", "是否高概率可成交客户": "否"},
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "北京-北京", "角色分类": "电转电换租老司机", "意向车型": "油车", "是否有效意向": "否", "是否高概率可成交客户": "否"},
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "河北-石家庄", "是否接通": "是", "是否加上微信": "是", "是否有效意向": "否", "是否高概率可成交客户": "否"}
]

# 创建智能图表选择器实例
selector = SmartChartSelector()

print("=== 测试完整的图表生成流程 ===")

# 模拟调用 generate_smart_chart 函数
result = selector.generate_smart_chart(
    test_data,
    context="信息流线索跟进数据，分析关键转化指标：接通率、微信添加率、有效意向率、高概率成交率等",
    title="信息流线索跟进转化漏斗分析"
)

print(f"\n图表生成结果: {result.get('success')}")
print(f"图表类型: {result.get('chart_type')}")
print(f"图表标题: {result.get('title')}")
print(f"推荐原因: {result.get('reason')}")

# 模拟 format_function_result 函数
if result.get('success'):
    funnel_data = result.get('funnel_data')
    
    chart_config = {
        'chart_type': result.get('chart_type', 'unknown'),
        'title': result.get('title', ''),
        'reason': result.get('reason', ''),
        'data': funnel_data if funnel_data else test_data
    }
    
    # 使用ECHARTS:标记，让前端使用ECharts渲染
    chart_json = json.dumps(chart_config, ensure_ascii=False)
    formatted_result = f"[ECHARTS:{chart_json}:END_ECHARTS]"
    
    print(f"\n格式化后的结果: {formatted_result[:200]}...")
    print(f"\n完整格式化结果: {formatted_result}")
    
    # 检查格式
    if '[ECHARTS:' in formatted_result and ':END_ECHARTS]' in formatted_result:
        print("\n✓ 格式检查通过：包含[ECHARTS:...:END_ECHARTS]标记")
    else:
        print("\n✗ 格式检查失败：不包含[ECHARTS:...:END_ECHARTS]标记")
    
    # 检查是否可以被正确解析
    chart_match = formatted_result.match(r'\[ECHARTS:(.*?):END_ECHARTS\]')
    if chart_match:
        print("✓ 正则表达式匹配成功")
        try:
            chart_config_parsed = json.loads(chart_match.group(1))
            print(f"✓ JSON解析成功")
            print(f"  图表类型: {chart_config_parsed.get('chart_type')}")
            print(f"  图表标题: {chart_config_parsed.get('title')}")
            print(f"  数据项数量: {len(chart_config_parsed.get('data', []))}")
        except Exception as e:
            print(f"✗ JSON解析失败: {e}")
    else:
        print("✗ 正则表达式匹配失败")

print("\n测试完成！")
