#!/usr/bin/env python3
"""
测试Playwright PDF生成功能
"""

import json
import os

from src.handlers.pdf_generator import generate_flashcards_pdf

def test_playwright_pdf_generation():
    """测试Playwright PDF生成功能"""
    
    # 读取测试数据
    with open('tests/test_data.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # 确保输出目录存在
    output_dir = 'tests/output'
    os.makedirs(output_dir, exist_ok=True)
    
    # 测试用例
    test_cases = [
        {
            'name': '基础测试',
            'data': test_data['basic_test'],
            'layouts': ['single', 'a4_8']
        },
        {
            'name': 'Markdown测试',
            'data': test_data['markdown_test'],
            'layouts': ['single', 'a4_8']
        },
        {
            'name': '日文注音测试',
            'data': test_data['japanese_ruby_test'],
            'layouts': ['single', 'a4_8']
        }
    ]
    
    print("开始测试Playwright PDF生成...")
    
    for test_case in test_cases:
        for layout in test_case['layouts']:
            layout_name = '单页布局' if layout == 'single' else '8卡片布局'
            filename = f"{test_case['name']}_{layout_name}.pdf"
            output_path = os.path.join(output_dir, filename)
            
            try:
                # 生成PDF
                print(f"生成 {filename}...")
                
                # 生成PDF字节数据
                pdf_bytes = generate_flashcards_pdf(
                    flashcard_data=test_case['data'],
                    layout=layout
                )
                
                # 保存PDF到文件
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                print(f"✓ 成功生成: {output_path}")
                
            except Exception as e:
                print(f"✗ 生成失败 {filename}: {str(e)}")
    
    print("\n测试完成！")
    print(f"PDF文件已保存到: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    test_playwright_pdf_generation()