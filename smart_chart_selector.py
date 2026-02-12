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
            # 分析数据并推荐图表
            analysis = self.analyze_data_and_suggest_chart(data, context)
            
            if not analysis.get('success'):
                return analysis
            
            recommendation = analysis['recommendation']
            chart_type = recommendation['chart_type']
            
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
            
            return {
                'success': True,
                'chart_type': chart_type,
                'image': image_base64,
                'title': title,
                'reason': recommendation['reason']
            }
            
        except Exception as e:
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
