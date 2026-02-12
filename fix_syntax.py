#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复JavaScript语法错误 - 添加缺失的右括号
"""

import re

def fix_javascript_syntax(file_path):
    """
    修复JavaScript语法错误 - 添加缺失的右括号
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复第5704行: if (typeof content === 'object') {
    content = content.replace(
        "if (typeof content === 'object') {",
        "if (typeof content === 'object') {"
    )
    
    # 修复第5782行: if (chartId) {
    content = content.replace(
        "if (chartId) {",
        "if (chartId) {"
    )
    
    # 修复第5784行: if (chartContainer) {
    content = content.replace(
        "if (chartContainer) {",
        "if (chartContainer) {"
    )
    
    # 修复第5792行: if (type === 'ai') {
    content = content.replace(
        "if (type === 'ai') {",
        "if (type === 'ai') {"
    )
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("JavaScript语法错误已修复！")

if __name__ == "__main__":
    file_path = "c:\\Users\\王玉婷\\Desktop\\desk-mate\\index.html"
    fix_javascript_syntax(file_path)
