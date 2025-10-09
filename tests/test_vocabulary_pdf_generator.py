#!/usr/bin/env python3
"""
词汇表PDF卡片生成测试脚本

该脚本从CSV文件读取词汇数据，生成双面PDF闪卡：
- 正面：英文单词/短语
- 反面：词性 + 中文释义
- 页面居中显示
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.utils.csv_reader import read_vocabulary_csv, convert_vocabulary_to_flashcard_data
from src.utils.pdf_generator import generate_flashcards_pdf


def create_vocabulary_pdf(csv_file_path: str, output_pdf_path: str, layout: str = 'single'):
    """
    从CSV文件创建词汇PDF卡片
    
    Args:
        csv_file_path: CSV文件路径
        output_pdf_path: 输出PDF文件路径
        layout: 布局模式 ('single' 每页一张卡片, 'a4_8' 每页8张卡片)
    """
    try:
        print(f"正在读取CSV文件: {csv_file_path}")
        
        # 读取CSV数据
        vocabulary_data = read_vocabulary_csv(csv_file_path)
        print(f"成功读取 {len(vocabulary_data)} 个词汇")
        
        # 转换为闪卡数据格式
        flashcard_data = convert_vocabulary_to_flashcard_data(
            vocabulary_data, 
            title="英语词汇学习卡片"
        )
        
        print(f"正在生成PDF文件 (布局: {layout})...")
        
        # 生成PDF
        pdf_bytes = generate_flashcards_pdf(flashcard_data, layout=layout)
        
        # 保存PDF文件
        with open(output_pdf_path, 'wb') as f:
            f.write(pdf_bytes)
            
        print(f"PDF文件已生成: {output_pdf_path}")
        print(f"文件大小: {len(pdf_bytes)} 字节")
        
        return True
        
    except Exception as e:
        print(f"生成PDF时出错: {str(e)}")
        return False


def main():
    """主函数"""
    # 设置文件路径
    csv_file = project_root / "tests" / "词语表.csv"
    
    # 创建输出目录
    output_dir = project_root / "tests" / "output"
    output_dir.mkdir(exist_ok=True)
    
    # 生成不同布局的PDF文件
    layouts = {
        'single': '单页卡片_词汇表.pdf',
        'a4_8': '8卡片页面_词汇表.pdf'
    }
    
    print("=" * 50)
    print("词汇表PDF卡片生成器")
    print("=" * 50)
    
    if not csv_file.exists():
        print(f"错误: CSV文件不存在 - {csv_file}")
        return
    
    success_count = 0
    
    for layout, filename in layouts.items():
        output_path = output_dir / filename
        print(f"\n正在生成 {layout} 布局的PDF...")
        
        if create_vocabulary_pdf(str(csv_file), str(output_path), layout):
            success_count += 1
            print(f"✓ 成功生成: {output_path}")
        else:
            print(f"✗ 生成失败: {filename}")
    
    print(f"\n生成完成! 成功生成 {success_count}/{len(layouts)} 个PDF文件")
    print(f"输出目录: {output_dir}")
    
    # 显示生成的文件信息
    print("\n生成的文件:")
    for pdf_file in output_dir.glob("*.pdf"):
        size_mb = pdf_file.stat().st_size / (1024 * 1024)
        print(f"  - {pdf_file.name} ({size_mb:.2f} MB)")


def test_single_card():
    """测试生成单个卡片的PDF"""
    print("\n" + "=" * 30)
    print("测试单个卡片生成")
    print("=" * 30)
    
    # 创建测试数据
    test_data = [
        {
            'word': 'hello',
            'pos': 'n. / interj.',
            'definition': '你好；问候'
        }
    ]
    
    # 转换为闪卡格式
    flashcard_data = convert_vocabulary_to_flashcard_data(
        test_data, 
        title="测试卡片"
    )
    
    try:
        # 生成PDF
        pdf_bytes = generate_flashcards_pdf(flashcard_data, layout='single')
        
        # 保存测试文件
        output_dir = project_root / "tests" / "output"
        output_dir.mkdir(exist_ok=True)
        test_file = output_dir / "test_single_card.pdf"
        
        with open(test_file, 'wb') as f:
            f.write(pdf_bytes)
            
        print(f"✓ 测试成功! 生成文件: {test_file}")
        print(f"  文件大小: {len(pdf_bytes)} 字节")
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")


if __name__ == "__main__":
    # 运行主程序
    main()
    
    # 运行单卡片测试
    test_single_card()
    
    print("\n" + "=" * 50)
    print("脚本执行完成!")
    print("=" * 50)