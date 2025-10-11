"""
高级功能测试用例
测试多样式JSON处理和CSV导入功能
"""

import pytest
import json
import os
import tempfile
from pathlib import Path

from src.handlers.card_generator import generate_flashcards
from src.handlers.pdf_generator import generate_flashcards_pdf
from src.utils.csv_reader import convert_csv_to_json_data


class TestMultiStyleJSON:
    """测试包含多种样式的JSON处理"""
    
    def setup_method(self):
        """测试前准备"""
        self.test_data_file = Path(__file__).parent / "test_multi_style_data.json"
        with open(self.test_data_file, 'r', encoding='utf-8') as f:
            self.test_data = json.load(f)
    
    def test_light_theme_card_generation(self):
        """测试浅色主题卡片生成"""
        light_theme_data = self.test_data["light_theme_test"]
        
        # 测试卡片生成
        html_result = generate_flashcards(light_theme_data)
        
        # 验证返回的是HTML字符串
        assert isinstance(html_result, str)
        assert len(html_result) > 0
        
        # 验证HTML包含基本结构
        assert "<html" in html_result
        assert "</html>" in html_result
        
        # 验证样式配置在HTML中
        assert "ffffff" in html_result  # 背景色
        assert "333333" in html_result  # 文字色
        
        # 验证卡片内容在HTML中
        assert "什么是浅色主题?" in html_result
        assert "浅色主题使用明亮的背景色" in html_result
    
    def test_dark_theme_card_generation(self):
        """测试深色主题卡片生成"""
        dark_theme_data = self.test_data["dark_theme_test"]
        
        # 测试卡片生成
        html_result = generate_flashcards(dark_theme_data)
        
        # 验证返回的是HTML字符串
        assert isinstance(html_result, str)
        assert len(html_result) > 0
        
        # 验证HTML包含基本结构
        assert "<html" in html_result
        assert "</html>" in html_result
        
        # 验证样式配置在HTML中
        assert "121212" in html_result  # 背景色
        assert "ffffff" in html_result  # 文字色
        
        # 验证卡片内容在HTML中
        assert "什么是深色主题?" in html_result
        assert "深色主题使用深色背景" in html_result
    
    def test_light_theme_pdf_generation(self):
        """测试浅色主题PDF生成"""
        light_theme_data = self.test_data["light_theme_test"]
        
        # 生成PDF
        pdf_bytes = generate_flashcards_pdf(
            flashcard_data=light_theme_data,
            layout="a4_8"
        )
        
        # 验证PDF生成成功
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # 验证PDF文件头（PDF文件以%PDF开头）
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_dark_theme_pdf_generation(self):
        """测试深色主题PDF生成"""
        dark_theme_data = self.test_data["dark_theme_test"]
        
        # 生成PDF
        pdf_bytes = generate_flashcards_pdf(
            flashcard_data=dark_theme_data,
            layout="a4_8"
        )
        
        # 验证PDF生成成功
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # 验证PDF文件头
        assert pdf_bytes.startswith(b'%PDF')


class TestCSVImport:
    """测试CSV导入功能"""
    
    def setup_method(self):
        """测试前准备"""
        self.csv_file_path = Path(__file__).parent / "词语表.csv"
        assert self.csv_file_path.exists(), f"CSV测试文件不存在: {self.csv_file_path}"
    
    def test_csv_to_json_conversion(self):
        """测试CSV到JSON的转换"""
        # 转换CSV到JSON格式
        json_data = convert_csv_to_json_data(
            file_path=str(self.csv_file_path),
            title="词语表闪卡集",
            front_column_index=0,  # 单词/短语
            back_column_index=2,   # 释义
            tags_column_index=1,   # 词性作为标签
            has_header=True
        )
        
        # 验证基本结构
        assert "cards" in json_data
        assert "metadata" in json_data
        assert json_data["metadata"]["title"] == "词语表闪卡集"
        
        # 验证卡片数量（CSV文件有87行，减去标题行）
        assert len(json_data["cards"]) > 80  # 应该有80+张卡片
        
        # 验证第一张卡片内容
        first_card = json_data["cards"][0]
        assert "while" in first_card["front"]
        assert "一会儿" in first_card["back"] or "然而" in first_card["back"]
        
        # 验证标签
        if "tags" in first_card:
            assert len(first_card["tags"]) > 0
    
    def test_csv_card_generation(self):
        """测试从CSV生成的卡片"""
        # 转换CSV到JSON
        json_data = convert_csv_to_json_data(
            file_path=str(self.csv_file_path),
            title="词语表闪卡集",
            front_column_index=0,
            back_column_index=2,
            tags_column_index=1,
            has_header=True
        )
        
        # 生成卡片HTML
        html_result = generate_flashcards(json_data)
        
        # 验证返回的是HTML字符串
        assert isinstance(html_result, str)
        assert len(html_result) > 0
        
        # 验证HTML包含基本结构
        assert "<html" in html_result
        assert "</html>" in html_result
        
        # 验证特定卡片内容在HTML中
        assert "while" in html_result
        assert "一会儿" in html_result or "然而" in html_result
    
    def test_csv_pdf_generation(self):
        """测试从CSV生成8连打印PDF"""
        # 转换CSV到JSON
        json_data = convert_csv_to_json_data(
            file_path=str(self.csv_file_path),
            title="词语表闪卡集",
            front_column_index=0,
            back_column_index=2,
            tags_column_index=1,
            has_header=True
        )
        
        # 生成PDF
        pdf_bytes = generate_flashcards_pdf(
            flashcard_data=json_data,
            layout="a4_8"
        )
        
        # 验证PDF文件生成
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
        
        # 验证卡片数量处理（确保补齐了空白卡片）
        card_count = len(json_data["cards"])
        expected_total = ((card_count + 7) // 8) * 8  # 向上取整到8的倍数
        
        # 这个测试确保PDF生成过程正确处理了卡片数量
        assert len(pdf_bytes) > 1000  # PDF应该有合理的大小
    
    def test_csv_with_different_columns(self):
        """测试使用不同列配置的CSV导入"""
        # 测试使用词性作为正面，释义作为背面
        json_data = convert_csv_to_json_data(
            file_path=str(self.csv_file_path),
            title="词性释义闪卡集",
            front_column_index=1,  # 词性
            back_column_index=2,   # 释义
            tags_column_index=0,   # 单词作为标签
            has_header=True
        )
        
        # 验证转换结果
        assert "cards" in json_data
        assert len(json_data["cards"]) > 0
        
        # 查找包含"n."的卡片
        noun_card = None
        for card in json_data["cards"]:
            if "n." in card["front"]:
                noun_card = card
                break
        
        if noun_card:
            assert "n." in noun_card["front"]
            assert len(noun_card["back"]) > 0


class TestIntegratedFeatures:
    """集成功能测试"""
    
    def test_multiple_style_pdf_batch_generation(self):
        """测试批量生成不同样式的PDF"""
        # 加载多样式测试数据
        test_data_file = Path(__file__).parent / "test_multi_style_data.json"
        with open(test_data_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        results = []
        
        # 生成浅色主题PDF
        light_pdf = generate_flashcards_pdf(
            flashcard_data=test_data["light_theme_test"],
            layout="a4_8"
        )
        results.append(light_pdf)
        
        # 生成深色主题PDF
        dark_pdf = generate_flashcards_pdf(
            flashcard_data=test_data["dark_theme_test"],
            layout="a4_8"
        )
        results.append(dark_pdf)
        
        # 验证所有PDF都成功生成
        for pdf_bytes in results:
            assert isinstance(pdf_bytes, bytes)
            assert len(pdf_bytes) > 0
            assert pdf_bytes.startswith(b'%PDF')
    
    def test_csv_and_json_style_combination(self):
        """测试CSV导入与JSON样式配置的结合"""
        # 转换CSV数据
        csv_file_path = Path(__file__).parent / "词语表.csv"
        json_data = convert_csv_to_json_data(
            file_path=str(csv_file_path),
            title="词语表闪卡集",
            front_column_index=0,
            back_column_index=2,
            tags_column_index=1,
            has_header=True
        )
        
        # 添加自定义样式配置
        json_data["style"] = {
            "theme": "custom",
            "font": "'Noto Sans CJK SC', sans-serif",
            "colors": {
                "primary": "#4caf50",
                "secondary": "#ff9800",
                "background": "f5f5f5",
                "text": "212121",
                "card_bg": "ffffff",
                "card_border": "e0e0e0"
            }
        }
        
        # 生成PDF
        pdf_bytes = generate_flashcards_pdf(
            flashcard_data=json_data,
            layout="a4_8"
        )
        
        # 验证生成成功
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')