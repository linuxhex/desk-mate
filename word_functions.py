#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word文档处理功能模块
提供Word文档的读取、创建、编辑等功能
"""

import os
from typing import Dict, List, Any, Optional


class WordFunctions:
    """Word文档处理功能类"""
    
    def __init__(self):
        """初始化Word文档处理功能"""
        pass
    
    def read_word_file(self, file_path: str) -> Dict[str, Any]:
        """
        读取Word文档
        
        Args:
            file_path: Word文档路径
            
        Returns:
            文档内容和信息
        """
        try:
            # 尝试使用python-docx读取
            try:
                from docx import Document
                doc = Document(file_path)
                
                # 提取文本内容
                paragraphs = []
                for para in doc.paragraphs:
                    if para.text.strip():
                        paragraphs.append(para.text)
                
                # 提取表格内容
                tables = []
                for table in doc.tables:
                    table_data = []
                    for row in table.rows:
                        row_data = [cell.text for cell in row.cells]
                        table_data.append(row_data)
                    tables.append(table_data)
                
                return {
                    'success': True,
                    'file_path': file_path,
                    'paragraphs': paragraphs,
                    'paragraph_count': len(paragraphs),
                    'tables': tables,
                    'table_count': len(tables),
                    'word_count': sum(len(p.split()) for p in paragraphs)
                }
                
            except ImportError:
                # 如果没有安装python-docx，尝试使用其他方法
                import zipfile
                import xml.etree.ElementTree as ET
                
                # Word文档实际上是zip文件
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    # 读取document.xml
                    with zip_ref.open('word/document.xml') as xml_file:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        
                        # 提取文本
                        text_elements = root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
                        paragraphs = [elem.text for elem in text_elements if elem.text]
                        
                        return {
                            'success': True,
                            'file_path': file_path,
                            'paragraphs': paragraphs,
                            'paragraph_count': len(paragraphs),
                            'word_count': sum(len(p.split()) for p in paragraphs)
                        }
                        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_word_file(self, file_path: str, content: str, title: str = "") -> Dict[str, Any]:
        """
        创建Word文档
        
        Args:
            file_path: 文件路径
            content: 文档内容
            title: 文档标题
            
        Returns:
            创建结果
        """
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 尝试使用python-docx创建
            try:
                from docx import Document
                doc = Document()
                
                # 添加标题
                if title:
                    doc.add_heading(title, 0)
                
                # 添加内容
                paragraphs = content.split('\n')
                for para in paragraphs:
                    if para.strip():
                        doc.add_paragraph(para)
                
                # 保存文档
                doc.save(file_path)
                
                return {
                    'success': True,
                    'file_path': os.path.abspath(file_path),
                    'size': os.path.getsize(file_path)
                }
                
            except ImportError:
                # 如果没有安装python-docx，创建简单的文本文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    if title:
                        f.write(f"{title}\n\n")
                    f.write(content)
                
                return {
                    'success': True,
                    'file_path': file_path,
                    'size': os.path.getsize(file_path),
                    'note': '已创建为文本文件（未安装python-docx库）'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_text_from_word(self, file_path: str) -> Dict[str, Any]:
        """
        从Word文档中提取纯文本
        
        Args:
            file_path: Word文档路径
            
        Returns:
            提取的文本内容
        """
        result = self.read_word_file(file_path)
        
        if result.get('success'):
            text = '\n'.join(result.get('paragraphs', []))
            return {
                'success': True,
                'text': text,
                'word_count': result.get('word_count', 0)
            }
        else:
            return result
