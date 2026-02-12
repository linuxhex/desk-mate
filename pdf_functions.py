#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF文档处理功能模块
提供PDF文档的读取、创建、编辑等功能
"""

import os
from typing import Dict, List, Any, Optional


class PDFFunctions:
    """PDF文档处理功能类"""
    
    def __init__(self):
        """初始化PDF文档处理功能"""
        pass
    
    def read_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """
        读取PDF文档
        
        Args:
            file_path: PDF文档路径
            
        Returns:
            文档内容和信息
        """
        try:
            # 尝试使用PyPDF2读取
            try:
                from PyPDF2 import PdfReader
                
                reader = PdfReader(file_path)
                
                # 提取文本内容
                pages = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text.strip():
                        pages.append(text)
                
                return {
                    'success': True,
                    'file_path': file_path,
                    'pages': pages,
                    'page_count': len(reader.pages),
                    'word_count': sum(len(p.split()) for p in pages)
                }
                
            except ImportError:
                # 尝试使用pdfplumber
                try:
                    import pdfplumber
                    
                    pages = []
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                pages.append(text)
                    
                    return {
                        'success': True,
                        'file_path': file_path,
                        'pages': pages,
                        'page_count': len(pages),
                        'word_count': sum(len(p.split()) for p in pages)
                    }
                    
                except ImportError:
                    # 尝试使用pymupdf
                    try:
                        import fitz  # pymupdf
                        
                        doc = fitz.open(file_path)
                        pages = []
                        
                        for page in doc:
                            text = page.get_text()
                            if text.strip():
                                pages.append(text)
                        
                        return {
                            'success': True,
                            'file_path': file_path,
                            'pages': pages,
                            'page_count': len(doc),
                            'word_count': sum(len(p.split()) for p in pages)
                        }
                        
                    except ImportError:
                        return {
                            'success': False,
                            'error': '未安装PDF处理库（PyPDF2、pdfplumber或pymupdf）'
                        }
                        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_pdf_file(self, file_path: str, content: str, title: str = "") -> Dict[str, Any]:
        """
        创建PDF文档
        
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
            
            # 尝试使用reportlab创建
            try:
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.pdfgen import canvas
                from reportlab.lib.units import inch
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
                
                # 创建PDF
                c = canvas.Canvas(file_path, pagesize=A4)
                width, height = A4
                
                # 尝试注册中文字体
                try:
                    # Windows系统字体路径
                    font_path = "C:/Windows/Fonts/simhei.ttf"
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('SimHei', font_path))
                        c.setFont('SimHei', 12)
                    else:
                        c.setFont('Helvetica', 12)
                except:
                    c.setFont('Helvetica', 12)
                
                # 添加标题
                if title:
                    c.setFontSize(16)
                    c.drawString(1*inch, height - 1*inch, title)
                    c.setFontSize(12)
                    y_position = height - 1.5*inch
                else:
                    y_position = height - 1*inch
                
                # 添加内容
                lines = content.split('\n')
                for line in lines:
                    if y_position < 1*inch:
                        c.showPage()
                        y_position = height - 1*inch
                    
                    c.drawString(1*inch, y_position, line[:80])  # 限制每行字符数
                    y_position -= 0.3*inch
                
                c.save()
                
                return {
                    'success': True,
                    'file_path': os.path.abspath(file_path),
                    'size': os.path.getsize(file_path)
                }
                
            except ImportError:
                # 如果没有安装reportlab，创建简单的文本文件
                with open(file_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                    if title:
                        f.write(f"{title}\n\n")
                    f.write(content)
                
                return {
                    'success': True,
                    'file_path': file_path.replace('.pdf', '.txt'),
                    'size': os.path.getsize(file_path.replace('.pdf', '.txt')),
                    'note': '已创建为文本文件（未安装reportlab库）'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_text_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        从PDF文档中提取纯文本
        
        Args:
            file_path: PDF文档路径
            
        Returns:
            提取的文本内容
        """
        result = self.read_pdf_file(file_path)
        
        if result.get('success'):
            text = '\n\n'.join(result.get('pages', []))
            return {
                'success': True,
                'text': text,
                'word_count': result.get('word_count', 0)
            }
        else:
            return result
