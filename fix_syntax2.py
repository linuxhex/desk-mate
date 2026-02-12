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
    
    # 修复所有缺失的右括号
    # 匹配 if (...) { 后面没有 } 的情况
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        fixed_lines.append(line)
        
        # 检查是否是if语句，并且缺少右括号
        if 'if (' in line and ') {' in line and not line.strip().endswith('}'):
            # 检查下一行是否是缩进的代码
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # 如果下一行是缩进的代码，说明需要添加右括号
                if next_line.strip() and not next_line.strip().startswith('//') and not next_line.strip().startswith('}') and not next_line.strip().startswith('else'):
                    # 添加右括号
                    fixed_lines.append('}')
    
    content = '\n'.join(fixed_lines)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("JavaScript语法错误已修复！")

if __name__ == "__main__":
    file_path = "c:\\Users\\王玉婷\\Desktop\\desk-mate\\index.html"
    fix_javascript_syntax(file_path)
