#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图表生成和格式化的完整流程
"""

import json
from smart_chart_selector import SmartChartSelector

# 测试数据 - 信息流线索跟进数据
test_data = [
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "广东-韶关", "是否接通": "否", "是否加上微信": "否", "是否有效意向": "否", "是否高概率可成交客户": "否"},
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "北京-北京", "角色分类": "电转电换租老司机", "意向车型": "油车", "是否有效意向": "否", "是否高概率可成交客户": "否"},
    {"__EMPTY": "字节-通投智选", "日期": 46028, "自动定位城市": "河北-石家庄", "是否接通": "是", "是否加上微信": "是", "是否有效意向": "否", "是否高概率可成交客户": "否"}
]

# 创建智能图表选择器实例
selector = SmartChartSelector()

print("=" * 80)
print("测试图表生成和格式化的完整流程")
print("=" * 80)

# 模拟调用 generate_smart_chart 函数
print("\n1. 调用 generate_smart_chart 函数...")
result = selector.generate_smart_chart(
    test_data,
    context="信息流线索跟进数据，分析关键转化指标：接通率、微信添加率、有效意向率、高概率成交率等",
    title="信息流线索跟进转化漏斗分析"
)

print(f"   图表生成结果: {result.get('success')}")
print(f"   图表类型: {result.get('chart_type')}")
print(f"   图表标题: {result.get('title')}")
print(f"   推荐原因: {result.get('reason')}")

# 模拟 format_function_result 函数
print("\n2. 调用 format_function_result 函数...")
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
    
    print(f"   格式化后的结果长度: {len(formatted_result)}")
    print(f"   格式化后的结果前200字符: {formatted_result[:200]}...")
    
    # 检查格式
    print("\n3. 检查格式...")
    if '[ECHARTS:' in formatted_result and ':END_ECHARTS]' in formatted_result:
        print("   ✓ 格式检查通过：包含[ECHARTS:...:END_ECHARTS]标记")
    else:
        print("   ✗ 格式检查失败：不包含[ECHARTS:...:END_ECHARTS]标记")
    
    # 检查是否可以被正确解析
    print("\n4. 检查正则表达式匹配...")
    import re
    chart_match = re.search(r'\[ECHARTS:(.*?):END_ECHARTS\]', formatted_result)
    if chart_match:
        print("   ✓ 正则表达式匹配成功")
        print(f"   匹配到的内容长度: {len(chart_match.group(1))}")
        
        try:
            chart_config_parsed = json.loads(chart_match.group(1))
            print("   ✓ JSON解析成功")
            print(f"     图表类型: {chart_config_parsed.get('chart_type')}")
            print(f"     图表标题: {chart_config_parsed.get('title')}")
            print(f"     数据项数量: {len(chart_config_parsed.get('data', []))}")
            
            # 检查数据格式
            print("\n5. 检查数据格式...")
            data = chart_config_parsed.get('data', [])
            if data and len(data) > 0:
                first_item = data[0]
                print(f"     第一个数据项: {first_item}")
                if 'name' in first_item and 'value' in first_item and 'rate' in first_item:
                    print("     ✓ 数据格式正确：包含name、value、rate字段")
                else:
                    print("     ✗ 数据格式错误：缺少必要字段")
                    print(f"       可用字段: {list(first_item.keys())}")
            else:
                print("     ✗ 数据为空")
        except Exception as e:
            print(f"   ✗ JSON解析失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("   ✗ 正则表达式匹配失败")
        
    # 打印完整的格式化结果
    print("\n6. 完整的格式化结果:")
    print(formatted_result)

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)
