#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表生成功能模块
支持生成各种类型的图表并返回base64编码的图片
"""

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import base64
from io import BytesIO
import json
from typing import Dict, List, Any, Optional


class ChartGenerator:
    """图表生成器"""
    
    def __init__(self):
        """初始化图表生成器"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def generate_chart(self, chart_type: str, data: Dict[str, Any], title: str = "", options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成图表
        
        Args:
            chart_type: 图表类型（bar, line, pie, scatter, etc.）
            data: 图表数据
            title: 图表标题
            options: 其他选项
            
        Returns:
            包含base64编码图片的字典
        """
        try:
            # 创建图表
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if chart_type == 'bar':
                self._create_bar_chart(ax, data, options)
            elif chart_type == 'line':
                self._create_line_chart(ax, data, options)
            elif chart_type == 'pie':
                self._create_pie_chart(ax, data, options)
            elif chart_type == 'scatter':
                self._create_scatter_chart(ax, data, options)
            else:
                return {
                    'success': False,
                    'error': f'不支持的图表类型: {chart_type}'
                }
            
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
                'title': title
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_bar_chart(self, ax, data: Dict[str, Any], options: Dict[str, Any] = None):
        """创建柱状图"""
        labels = data.get('labels', [])
        values = data.get('values', [])
        
        if not labels or not values:
            raise ValueError('柱状图需要labels和values数据')
        
        colors = options.get('colors', None) if options else None
        if colors and len(colors) == len(values):
            ax.bar(labels, values, color=colors)
        else:
            ax.bar(labels, values)
        
        ax.set_xlabel(data.get('x_label', ''), fontsize=12)
        ax.set_ylabel(data.get('y_label', ''), fontsize=12)
        ax.grid(axis='y', alpha=0.3)
    
    def _create_line_chart(self, ax, data: Dict[str, Any], options: Dict[str, Any] = None):
        """创建折线图"""
        labels = data.get('labels', [])
        values = data.get('values', [])
        
        if not labels or not values:
            raise ValueError('折线图需要labels和values数据')
        
        ax.plot(labels, values, marker='o', linewidth=2, markersize=6)
        ax.set_xlabel(data.get('x_label', ''), fontsize=12)
        ax.set_ylabel(data.get('y_label', ''), fontsize=12)
        ax.grid(True, alpha=0.3)
    
    def _create_pie_chart(self, ax, data: Dict[str, Any], options: Dict[str, Any] = None):
        """创建饼图"""
        labels = data.get('labels', [])
        values = data.get('values', [])
        
        if not labels or not values:
            raise ValueError('饼图需要labels和values数据')
        
        colors = options.get('colors', None) if options else None
        if colors and len(colors) == len(values):
            ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        else:
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    
    def _create_scatter_chart(self, ax, data: Dict[str, Any], options: Dict[str, Any] = None):
        """创建散点图"""
        x_values = data.get('x_values', [])
        y_values = data.get('y_values', [])
        
        if not x_values or not y_values:
            raise ValueError('散点图需要x_values和y_values数据')
        
        ax.scatter(x_values, y_values, alpha=0.6, s=50)
        ax.set_xlabel(data.get('x_label', ''), fontsize=12)
        ax.set_ylabel(data.get('y_label', ''), fontsize=12)
        ax.grid(True, alpha=0.3)
    
    def analyze_and_suggest_chart(self, data: List[Dict[str, Any]], context: str = "") -> Dict[str, Any]:
        """
        分析数据并建议合适的图表类型
        
        Args:
            data: 数据列表
            context: 上下文信息
            
        Returns:
            建议的图表类型和配置
        """
        if not data or len(data) == 0:
            return {
                'success': False,
                'error': '没有数据可供分析'
            }
        
        # 分析数据结构
        first_item = data[0]
        
        # 如果数据是字典列表
        if isinstance(first_item, dict):
            keys = list(first_item.keys())
            
            # 如果有数值字段，建议柱状图
            numeric_keys = [k for k in keys if isinstance(first_item.get(k), (int, float))]
            
            if len(numeric_keys) > 0:
                # 提取标签和数值
                labels = [str(item.get(keys[0], i)) for i, item in enumerate(data)]
                values = [item.get(numeric_keys[0], 0) for item in data]
                
                return {
                    'success': True,
                    'chart_type': 'bar',
                    'data': {
                        'labels': labels,
                        'values': values,
                        'x_label': keys[0],
                        'y_label': numeric_keys[0]
                    },
                    'title': f'{numeric_keys[0]}统计'
                }
        
        return {
            'success': False,
            'error': '无法确定合适的图表类型'
        }
