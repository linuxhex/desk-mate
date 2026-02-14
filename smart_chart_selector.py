#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能图表选择和展示功能模块
根据数据特征自动选择最优图表类型
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import base64
from io import BytesIO
from typing import Dict, List, Any, Optional


class SmartChartSelector:
    """智能图表选择器"""
    
    def __init__(self):
        """初始化图表选择器"""
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def analyze_data_and_suggest_chart(self, data: List[Dict[str, Any]], context: str = "") -> Dict[str, Any]:
        """
        分析数据并建议最优图表类型
        
        Args:
            data: 数据列表
            context: 上下文信息
            
        Returns:
            建议的图表类型和配置
        """
        try:
            if not data or len(data) == 0:
                return {
                    'success': False,
                    'error': '没有数据可供分析'
                }
            
            df = pd.DataFrame(data)
            
            # 分析数据特征
            features = self._analyze_data_features(df)
            
            # 根据特征选择最优图表
            chart_recommendation = self._recommend_chart(features, context)
            
            return {
                'success': True,
                'features': features,
                'recommendation': chart_recommendation
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_data_features(self, df) -> Dict[str, Any]:
        """
        分析数据特征
        
        Args:
            df: pandas DataFrame
            
        Returns:
            数据特征
        """
        features = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': [],
            'text_columns': [],
            'datetime_columns': [],
            'numeric_ratio': 0,
            'unique_text_values': {}
        }
        
        # 分析每列的数据类型
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                features['numeric_columns'].append(col)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                features['datetime_columns'].append(col)
            else:
                features['text_columns'].append(col)
                # 统计唯一值数量
                unique_count = df[col].nunique()
                features['unique_text_values'][col] = unique_count
        
        # 计算数值列比例
        if features['total_columns'] > 0:
            features['numeric_ratio'] = len(features['numeric_columns']) / features['total_columns']
        
        return features
    
    def _recommend_chart(self, features: Dict[str, Any], context: str) -> Dict[str, Any]:
        """
        根据数据特征推荐图表类型
        
        Args:
            features: 数据特征
            context: 上下文信息
            
        Returns:
            图表推荐
        """
        recommendation = {
            'chart_type': 'bar',
            'reason': '',
            'config': {}
        }
        
        # 根据上下文关键词调整推荐
        context_lower = context.lower() if context else ""
        
        # 如果提到趋势、变化等关键词
        if any(keyword in context_lower for keyword in ['趋势', '变化', '走势', '增长', '下降']):
            recommendation['chart_type'] = 'line'
            recommendation['reason'] = '数据涉及趋势分析，推荐使用折线图'
        
        # 如果提到占比、比例等关键词
        elif any(keyword in context_lower for keyword in ['占比', '比例', '百分比', '分布']):
            recommendation['chart_type'] = 'pie'
            recommendation['reason'] = '数据涉及占比分析，推荐使用饼图'
        
        # 如果提到关系、相关性等关键词
        elif any(keyword in context_lower for keyword in ['关系', '相关', '对比', '比较']):
            if len(features['numeric_columns']) >= 2:
                recommendation['chart_type'] = 'scatter'
                recommendation['reason'] = '数据涉及关系分析，推荐使用散点图'
            else:
                recommendation['chart_type'] = 'bar'
                recommendation['reason'] = '数据涉及对比分析，推荐使用柱状图'
        
        # 根据数据特征推荐
        else:
            # 如果有日期列，推荐折线图
            if features['datetime_columns']:
                recommendation['chart_type'] = 'line'
                recommendation['reason'] = '数据包含时间维度，推荐使用折线图'
            
            # 如果数值列比例高，推荐柱状图
            elif features['numeric_ratio'] > 0.5:
                recommendation['chart_type'] = 'bar'
                recommendation['reason'] = '数据以数值为主，推荐使用柱状图'
            
            # 如果文本列唯一值较少，推荐饼图
            elif features['text_columns']:
                # 找到唯一值最少的文本列
                min_unique = min(features['unique_text_values'].values())
                if min_unique <= 10:
                    recommendation['chart_type'] = 'pie'
                    recommendation['reason'] = '数据分类较少，推荐使用饼图'
                else:
                    recommendation['chart_type'] = 'bar'
                    recommendation['reason'] = '数据分类较多，推荐使用柱状图'
            
            # 默认推荐柱状图
            else:
                recommendation['chart_type'] = 'bar'
                recommendation['reason'] = '默认推荐使用柱状图'
        
        return recommendation
    
    def calculate_conversion_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算信息流线索跟进数据的转化指标
        
        Args:
            data: 信息流线索跟进数据
            
        Returns:
            包含转化指标的字典
        """
        try:
            if not data:
                return {
                    'success': False,
                    'error': '没有数据可供分析'
                }
            
            total_leads = len(data)
            
            # 计算各阶段转化数
            connected_count = sum(1 for item in data if item.get('是否接通') == '是')
            wechat_count = sum(1 for item in data if item.get('是否加上微信') == '是')
            intent_count = sum(1 for item in data if item.get('是否有效意向') == '是')
            high_prob_count = sum(1 for item in data if item.get('是否高概率可成交客户') == '是')
            
            # 计算转化率
            connected_rate = round((connected_count / total_leads) * 100, 2) if total_leads > 0 else 0
            wechat_rate = round((wechat_count / connected_count) * 100, 2) if connected_count > 0 else 0
            intent_rate = round((intent_count / wechat_count) * 100, 2) if wechat_count > 0 else 0
            high_prob_rate = round((high_prob_count / intent_count) * 100, 2) if intent_count > 0 else 0
            
            # 为漏斗图准备数据
            funnel_data = [
                {'name': '总线索量', 'value': total_leads, 'rate': 100},
                {'name': '接通', 'value': connected_count, 'rate': connected_rate},
                {'name': '添加微信', 'value': wechat_count, 'rate': wechat_rate},
                {'name': '有效意向', 'value': intent_count, 'rate': intent_rate},
                {'name': '高概率成交', 'value': high_prob_count, 'rate': high_prob_rate}
            ]
            
            return {
                'success': True,
                'total_leads': total_leads,
                'connected_count': connected_count,
                'wechat_count': wechat_count,
                'intent_count': intent_count,
                'high_prob_count': high_prob_count,
                'connected_rate': connected_rate,
                'wechat_rate': wechat_rate,
                'intent_rate': intent_rate,
                'high_prob_rate': high_prob_rate,
                'funnel_data': funnel_data
            }
            
        except Exception as e:
            print(f"计算转化指标失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_smart_chart(self, data: List[Dict[str, Any]], context: str = "", title: str = "") -> Dict[str, Any]:
        """
        智能生成图表
        
        Args:
            data: 数据列表
            context: 上下文信息
            title: 图表标题
            
        Returns:
            包含base64编码图片的字典
        """
        try:
            print(f"开始生成图表，数据行数: {len(data) if data else 0}")
            
            # 检查是否是信息流线索跟进数据
            is_funnel_data = False
            funnel_data = None
            
            # 检查数据中是否包含转化漏斗相关字段
            if data and all(key in data[0] for key in ['是否接通', '是否加上微信', '是否有效意向', '是否高概率可成交客户']):
                is_funnel_data = True
                # 计算转化指标
                conversion_result = self.calculate_conversion_metrics(data)
                if conversion_result.get('success'):
                    funnel_data = conversion_result['funnel_data']
                    print(f"计算转化指标成功，漏斗数据: {funnel_data}")
            
            if is_funnel_data and funnel_data:
                # 强制使用漏斗图
                chart_type = 'funnel'
                reason = '数据包含转化漏斗信息，推荐使用漏斗图'
            else:
                # 分析数据并推荐图表
                analysis = self.analyze_data_and_suggest_chart(data, context)
                
                print(f"数据分析结果: {analysis.get('success')}")
                
                if not analysis.get('success'):
                    print(f"数据分析失败: {analysis.get('error')}")
                    return analysis
                
                recommendation = analysis['recommendation']
                chart_type = recommendation['chart_type']
                reason = recommendation['reason']
            
            print(f"推荐的图表类型: {chart_type}")
            
            # 生成图表
            df = pd.DataFrame(data)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if chart_type == 'bar':
                self._create_smart_bar_chart(ax, df, context)
            elif chart_type == 'line':
                self._create_smart_line_chart(ax, df, context)
            elif chart_type == 'pie':
                self._create_smart_pie_chart(ax, df, context)
            elif chart_type == 'scatter':
                self._create_smart_scatter_chart(ax, df, context)
            elif chart_type == 'funnel':
                # 创建漏斗图
                self._create_smart_funnel_chart(ax, funnel_data, context)
            
            # 设置标题
            if title:
                ax.set_title(title, fontsize=14, fontweight='bold')
            
            # 调整布局
            plt.tight_layout()
            
            # 转换为base64
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close(fig)
            
            print(f"图表生成成功，图片数据长度: {len(image_base64)}")
            
            return {
                'success': True,
                'chart_type': chart_type,
                'image': image_base64,
                'title': title,
                'reason': reason,
                'funnel_data': funnel_data  # 添加漏斗数据，供前端使用
            }
            
        except Exception as e:
            print(f"图表生成失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_smart_bar_chart(self, ax, df, context: str):
        """创建智能柱状图"""
        # 选择合适的列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if numeric_cols and text_cols:
            # 使用第一个文本列作为X轴，第一个数值列作为Y轴
            x_col = text_cols[0]
            y_col = numeric_cols[0]
            
            # 聚合数据
            grouped = df.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(10)
            
            ax.bar(range(len(grouped)), grouped.values)
            ax.set_xticks(range(len(grouped)))
            ax.set_xticklabels(grouped.index, rotation=45, ha='right')
            ax.set_xlabel(x_col, fontsize=12)
            ax.set_ylabel(y_col, fontsize=12)
            ax.grid(axis='y', alpha=0.3)
        elif numeric_cols:
            # 只有数值列，显示前10个数值
            y_col = numeric_cols[0]
            data = df[y_col].head(10)
            ax.bar(range(len(data)), data.values)
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels(range(1, len(data) + 1))
            ax.set_ylabel(y_col, fontsize=12)
            ax.grid(axis='y', alpha=0.3)
    
    def _create_smart_line_chart(self, ax, df, context: str):
        """创建智能折线图"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            y_col = numeric_cols[0]
            ax.plot(range(len(df)), df[y_col], marker='o', linewidth=2, markersize=6)
            ax.set_xlabel('序号', fontsize=12)
            ax.set_ylabel(y_col, fontsize=12)
            ax.grid(True, alpha=0.3)
    
    def _create_smart_pie_chart(self, ax, df, context: str):
        """创建智能饼图"""
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if text_cols:
            # 选择唯一值最少的文本列
            best_col = min(text_cols, key=lambda col: df[col].nunique())
            
            # 统计值
            value_counts = df[best_col].value_counts().head(10)
            
            ax.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%', startangle=90)
    
    def _create_smart_scatter_chart(self, ax, df, context: str):
        """创建智能散点图"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            
            ax.scatter(df[x_col], df[y_col], alpha=0.6, s=50)
            ax.set_xlabel(x_col, fontsize=12)
            ax.set_ylabel(y_col, fontsize=12)
            ax.grid(True, alpha=0.3)
    
    def _create_smart_funnel_chart(self, ax, funnel_data, context: str):
        """创建智能漏斗图"""
        if not funnel_data:
            return
        
        # 提取数据
        labels = [item['name'] for item in funnel_data]
        values = [item['value'] for item in funnel_data]
        
        # 创建水平条形图模拟漏斗图
        y_pos = range(len(labels))
        
        # 计算条形宽度（模拟漏斗效果）
        max_value = max(values)
        widths = [v / max_value for v in values]
        
        # 绘制漏斗图
        bars = ax.barh(y_pos, values, height=0.6, color='#58a6ff', alpha=0.8)
        
        # 设置标签和标题
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=12)
        ax.set_xlabel('数量', fontsize=12)
        
        # 添加数值标签
        for i, (bar, value) in enumerate(zip(bars, values)):
            ax.text(value + 5, bar.get_y() + bar.get_height()/2, f'{value} ({funnel_data[i]["rate"]}%)',
                    va='center', fontsize=10, color='#c9d1d9')
        
        # 设置背景和网格
        ax.set_facecolor('#21262d')
        ax.grid(axis='x', alpha=0.3)
