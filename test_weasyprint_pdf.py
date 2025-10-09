#!/usr/bin/env python3
"""
测试playwright PDF生成功能
使用test_data.json中的数据生成PDF文件
"""

import json
import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.pdf_generator import generate_and_save_pdf


def test_playwright_pdf_generation():
    """测试playwright PDF生成功能"""
    
    # 读取测试数据
    test_data_path = os.path.join('tests', 'test_data.json')
    with open(test_data_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # 输出目录
    output_dir = os.path.join('tests', 'output')
    
    # 测试不同的数据集和布局
    test_cases = [
        ('basic_test', 'single', '基础测试_单页布局.pdf'),
        ('basic_test', 'a4_8', '基础测试_8卡片布局.pdf'),
        ('markdown_test', 'single', 'Markdown测试_单页布局.pdf'),
        ('markdown_test', 'a4_8', 'Markdown测试_8卡片布局.pdf'),
        ('style_test', 'a4_8', '样式测试_8卡片布局.pdf'),
        ('tags_test', 'a4_8', '标签测试_8卡片布局.pdf'),
        ('japanese_ruby_test', 'single', '日文注音测试_单页布局.pdf'),
        ('japanese_ruby_test', 'a4_8', '日文注音测试_8卡片布局.pdf'),
    ]
    
    print("开始测试playwright PDF生成功能...")
    print(f"输出目录: {output_dir}")
    print("-" * 50)
    
    for test_name, layout, filename in test_cases:
        if test_name not in test_data:
            print(f"跳过测试 {test_name}: 数据不存在")
            continue
            
        try:
            print(f"生成 {test_name} ({layout} 布局)...")
            
            # 生成PDF
            output_path = generate_and_save_pdf(
                flashcard_data=test_data[test_name],
                output_path=output_dir,
                filename=filename,
                layout=layout
            )
            
            print(f"✓ 成功生成: {output_path}")
            
            # 检查文件大小
            file_size = os.path.getsize(output_path)
            print(f"  文件大小: {file_size:,} bytes")
            
        except Exception as e:
            print(f"✗ 生成失败 {test_name}: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("测试完成!")


if __name__ == "__main__":
    test_playwright_pdf_generation()