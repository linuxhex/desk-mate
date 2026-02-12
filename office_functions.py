#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
办公助手功能模块
提供各种办公相关的功能
"""

import os
import json
import sys
import platform
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime


class OfficeFunctions:
    """办公助手功能类"""
    
    def __init__(self):
        self.system = platform.system()
    
    def analyze_excel_data(self, data: List[Dict[str, Any]], analysis_type: str = 'general') -> Dict[str, Any]:
        """
        分析Excel数据
        
        Args:
            data: Excel数据列表
            analysis_type: 分析类型（general, recruitment等）
            
        Returns:
            分析结果
        """
        try:
            if not data or len(data) == 0:
                return {
                    'success': False,
                    'error': '没有数据可供分析'
                }
            
            import pandas as pd
            df = pd.DataFrame(data)
            
            # 基本统计信息
            result = {
                'success': True,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'analysis_type': analysis_type
            }
            
            # 根据分析类型进行不同的分析
            if analysis_type == 'recruitment':
                # 招聘岗位分析
                result['analysis'] = self._analyze_recruitment(df)
            else:
                # 通用分析
                result['analysis'] = self._analyze_general(df)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_recruitment(self, df) -> Dict[str, Any]:
        """
        分析招聘岗位数据
        
        Args:
            df: pandas DataFrame
            
        Returns:
            分析结果
        """
        analysis = {}
        
        # 尝试识别常见列名
        possible_cols = {
            '招聘人数': ['招聘人数', '人数', '招考人数', '计划招聘人数'],
            '学历要求': ['学历要求', '学历', '最低学历', '学历层次'],
            '专业要求': ['专业要求', '专业', '所需专业'],
            '工作地点': ['工作地点', '地点', '工作区域', '地区'],
            '岗位名称': ['岗位名称', '岗位', '职位名称', '职位']
        }
        
        # 找到匹配的列
        col_mapping = {}
        for key, possible_names in possible_cols.items():
            for col in df.columns:
                if any(name in str(col) for name in possible_names):
                    col_mapping[key] = col
                    break
        
        # 分析招聘人数
        if '招聘人数' in col_mapping:
            col = col_mapping['招聘人数']
            # 尝试提取数字
            df['招聘人数_数值'] = pd.to_numeric(df[col].astype(str).str.extract(r'(\d+)')[0], errors='coerce')
            top_recruitment = df.nlargest(10, '招聘人数_数值')[['岗位名称', col]].to_dict('records') if '岗位名称' in col_mapping else []
            analysis['招聘人数最多的岗位'] = top_recruitment
        
        # 分析学历要求
        if '学历要求' in col_mapping:
            col = col_mapping['学历要求']
            education_stats = df[col].value_counts().to_dict()
            analysis['学历要求分布'] = education_stats
        
        # 分析工作地点
        if '工作地点' in col_mapping:
            col = col_mapping['工作地点']
            location_stats = df[col].value_counts().head(10).to_dict()
            analysis['工作地点分布'] = location_stats
        
        # 推荐最好考的岗位
        recommendations = []
        if '招聘人数' in col_mapping and '学历要求' in col_mapping:
            # 筛选招聘人数多、学历要求低的岗位
            df_filtered = df[df['招聘人数_数值'] >= 2]  # 招聘人数>=2
            if len(df_filtered) > 0:
                # 按学历要求排序（专科<本科<研究生）
                education_order = {'专科': 1, '大专': 1, '本科': 2, '研究生': 3, '硕士': 3, '博士': 4}
                df_filtered['学历等级'] = df_filtered[col_mapping['学历要求']].map(lambda x: education_order.get(str(x), 2))
                df_sorted = df_filtered.sort_values(['招聘人数_数值', '学历等级'], ascending=[False, True])
                recommendations = df_sorted.head(20).to_dict('records')
        
        analysis['推荐岗位（招聘人数多、学历要求相对较低）'] = recommendations
        
        return analysis
    
    def _analyze_general(self, df) -> Dict[str, Any]:
        """
        通用数据分析
        
        Args:
            df: pandas DataFrame
            
        Returns:
            分析结果
        """
        analysis = {}
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            analysis['数值列统计'] = df[numeric_cols].describe().to_dict()
        
        # 文本列统计
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        if text_cols:
            text_stats = {}
            for col in text_cols[:5]:  # 只统计前5个文本列
                text_stats[col] = {
                    '唯一值数量': df[col].nunique(),
                    '最常见值': df[col].mode().iloc[0] if len(df[col].mode()) > 0 else None
                }
            analysis['文本列统计'] = text_stats
        
        return analysis
    
    def create_analysis_excel(self, data: List[Dict[str, Any]], analysis_result: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """
        创建包含分析结果的Excel文件
        
        Args:
            data: 原始数据
            analysis_result: 分析结果
            output_file: 输出文件路径
            
        Returns:
            创建结果
        """
        try:
            import pandas as pd
            
            # 确保目录存在
            directory = os.path.dirname(output_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 创建Excel写入器
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 写入原始数据
                df_data = pd.DataFrame(data)
                df_data.to_excel(writer, sheet_name='原始数据', index=False)
                
                # 写入分析结果
                if 'analysis' in analysis_result:
                    analysis_dict = analysis_result['analysis']
                    
                    # 为每个分析结果创建一个sheet
                    for key, value in analysis_dict.items():
                        if isinstance(value, list):
                            df_analysis = pd.DataFrame(value)
                            sheet_name = key[:31]  # Excel sheet名称最多31个字符
                            df_analysis.to_excel(writer, sheet_name=sheet_name, index=False)
                        elif isinstance(value, dict):
                            df_analysis = pd.DataFrame(list(value.items()), columns=['项目', '数值'])
                            sheet_name = key[:31]
                            df_analysis.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return {
                'success': True,
                'output_file': os.path.abspath(output_file),
                'rows': len(data),
                'size': os.path.getsize(output_file)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_directory(self, directory: str = None) -> Dict[str, Any]:
        """
        列出目录内容
        
        Args:
            directory: 目录路径（可选），默认为桌面
            
        Returns:
            目录内容信息
        """
        try:
            # 如果没有指定目录，默认使用桌面
            if not directory:
                if self.system == "Windows":
                    directory = os.path.join(os.path.expanduser("~"), "Desktop")
                else:
                    directory = os.path.expanduser("~")
            
            # 检查目录是否存在
            if not os.path.exists(directory):
                return {
                    'success': False,
                    'error': f'目录不存在: {directory}'
                }
            
            items = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                item_info = {
                    'name': item,
                    'path': item_path,
                    'is_directory': os.path.isdir(item_path),
                    'size': os.path.getsize(item_path) if os.path.isfile(item_path) else 0,
                    'modified': datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M:%S')
                }
                items.append(item_info)
            
            return {
                'success': True,
                'directory': directory,
                'items': items,
                'count': len(items)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容
        """
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'文件不存在: {file_path}'
                }
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                return {
                    'success': False,
                    'error': '文件太大，超过10MB限制'
                }
            
            # 尝试读取文件
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 如果UTF-8失败，尝试其他编码
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        content = f.read()
                except:
                    return {
                        'success': False,
                        'error': '无法读取文件，可能是二进制文件'
                    }
            
            return {
                'success': True,
                'file_path': file_path,
                'content': content,
                'size': file_size,
                'lines': len(content.split('\n'))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        创建文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
            
        Returns:
            创建结果
        """
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 获取绝对路径
            absolute_path = os.path.abspath(file_path)
            
            return {
                'success': True,
                'file_path': absolute_path,
                'size': len(content.encode('utf-8'))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def copy_excel_file(self, source_file: str, data: List[Dict[str, Any]], output_file: str = None, 
                        columns: List[str] = None, rows: List[int] = None, 
                        sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """
        复制Excel文件，支持按行列细分数据
        
        Args:
            source_file: 源文件路径
            data: Excel数据
            output_file: 输出文件路径（可选）
            columns: 要写入的列名列表（可选）
            rows: 要写入的行号列表（可选）
            sheet_name: 工作表名称（可选）
            
        Returns:
            复制结果
        """
        try:
            # 如果没有指定输出文件，则在同一目录下创建副本
            if not output_file:
                base_name = os.path.basename(source_file)
                name, ext = os.path.splitext(base_name)
                output_file = os.path.join(os.path.dirname(source_file), f"{name}_copy{ext}")
            
            # 确保目录存在
            directory = os.path.dirname(output_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 使用pandas创建Excel文件
            import pandas as pd
            df = pd.DataFrame(data)
            
            # 如果指定了列，只写入这些列
            if columns:
                df = df[columns]
            
            # 如果指定了行，只写入这些行
            if rows:
                df = df.iloc[rows]
            
            # 根据文件扩展名选择保存格式
            if output_file.endswith('.xlsx'):
                df.to_excel(output_file, index=False, engine='openpyxl', sheet_name=sheet_name)
            elif output_file.endswith('.xls'):
                df.to_excel(output_file, index=False, engine='xlwt', sheet_name=sheet_name)
            else:
                # 默认使用xlsx格式
                df.to_excel(output_file, index=False, engine='openpyxl', sheet_name=sheet_name)
            
            return {
                'success': True,
                'source_file': os.path.abspath(source_file),
                'output_file': os.path.abspath(output_file),
                'rows': len(df),
                'columns': len(df.columns) if columns else len(data[0]) if data else 0,
                'size': os.path.getsize(output_file)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            删除结果
        """
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'文件不存在: {file_path}'
                }
            
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path)
            
            return {
                'success': True,
                'message': f'已删除: {file_path}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息
        
        Returns:
            系统信息
        """
        try:
            return {
                'success': True,
                'system': self.system,
                'node': platform.node(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'user': os.path.expanduser("~"),
                'desktop': os.path.join(os.path.expanduser("~"), "Desktop")
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        执行系统命令
        
        Args:
            command: 系统命令
            
        Returns:
            执行结果
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'
            )
            
            return {
                'success': True,
                'command': command,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '命令执行超时'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """测试功能"""
    functions = OfficeFunctions()
    
    # 测试系统信息
    print("系统信息:")
    print(json.dumps(functions.get_system_info(), indent=2, ensure_ascii=False))
    
    # 测试列出目录
    print("\n桌面内容:")
    print(json.dumps(functions.list_directory(), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
