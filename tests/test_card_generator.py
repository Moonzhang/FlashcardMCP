import unittest
import json
import os
from src.handlers.card_generator import generate_flashcards

class TestCardGenerator(unittest.TestCase):
    
    def setUp(self):
        # 有效的 JSON 数据示例
        self.valid_json_data = {
            "metadata": {
                "title": "测试闪卡集",
                "description": "这是一个测试用的闪卡集"
            },
            "cards": [
                {
                    "front": "什么是 Python?",
                    "back": "Python 是一种高级编程语言，以其简洁的语法和强大的生态系统而闻名。",
                    "tags": ["编程", "Python"]
                },
                {
                    "front": "FastMCP 的主要功能是什么?",
                    "back": "FastMCP 是一个用于构建 MCP 服务的快速开发框架，支持各种处理函数和路由配置。",
                    "tags": ["MCP", "FastMCP"]
                }
            ],
            "style": {
                "template": "default",
                "theme": "light",
                "font": "Arial, sans-serif"
            }
        }
        
        # 最小化的有效 JSON 数据
        self.minimal_json_data = {
            "cards": [
                {
                    "front": "问题",
                    "back": "答案"
                }
            ]
        }
        
        # 包含 Markdown 格式的 JSON 数据
        self.markdown_json_data = {
            "metadata": {
                "title": "Markdown 闪卡测试"
            },
            "cards": [
                {
                    "front": "# 这是一个标题",
                    "back": "这是**粗体**文本和*斜体*文本\n\n```python\nprint('Hello, World!')\n```"
                }
            ]
        }

        # 加载扩展测试数据集（填空、图片标题、表格、日文RUBY）
        try:
            with open(os.path.join(os.path.dirname(__file__), 'test_data.json'), 'r', encoding='utf-8') as f:
                self.test_data = json.load(f)
            self.fill_blank_json_data = self.test_data.get('fill_blank_test')
            self.image_title_json_data = self.test_data.get('image_title_test')
            self.table_json_data = self.test_data.get('table_test')
            self.japanese_ruby_json_data = self.test_data.get('japanese_ruby_test')
        except Exception:
            self.test_data = None
            self.fill_blank_json_data = None
            self.image_title_json_data = None
            self.table_json_data = None
            self.japanese_ruby_json_data = None
        
    def test_basic_flashcard_generation(self):
        """测试基本的闪卡生成功能"""
        html_output = generate_flashcards(self.valid_json_data)
        
        # 检查生成的 HTML 是否包含预期内容
        self.assertIn("<html", html_output)
        self.assertIn("<body", html_output)
        self.assertIn("测试闪卡集", html_output)  # 检查标题是否包含
        self.assertIn("什么是 Python?", html_output)  # 检查卡片内容是否包含
        self.assertIn("FastMCP 的主要功能是什么?", html_output)  # 检查另一张卡片内容
        
    def test_minimal_flashcard_generation(self):
        """测试使用最小化数据生成闪卡"""
        html_output = generate_flashcards(self.minimal_json_data)
        
        # 检查生成的 HTML 是否包含预期内容
        self.assertIn("<html", html_output)
        self.assertIn("FlashCard", html_output)  # 检查标题是否包含
        self.assertIn("问题", html_output)  # 检查卡片正面内容
        self.assertIn("答案", html_output)  # 检查卡片背面内容
        
    def test_markdown_flashcard_generation(self):
        """测试包含 Markdown 格式的闪卡生成"""
        html_output = generate_flashcards(self.markdown_json_data)
        
        # 检查 Markdown 是否被正确解析
        self.assertIn("<h1>", html_output)  # 标题应该被解析为 h1 标签
        self.assertIn("<strong>", html_output)  # 粗体应该被解析为 strong 标签
        self.assertIn("<em>", html_output)  # 斜体应该被解析为 em 标签
        self.assertIn("<pre>", html_output)  # 代码块应该被解析为 pre 标签
        self.assertIn("<code", html_output)  # 代码应该被包裹在 code 标签中
        
    def test_flashcard_count(self):
        """测试生成的闪卡数量是否正确"""
        html_output = generate_flashcards(self.valid_json_data)
        
        # 计算生成的卡片数量（通过计算 card-front 类的数量）
        card_front_count = html_output.count('class="card-front"')
        self.assertEqual(card_front_count, len(self.valid_json_data["cards"]))
        
        # 每个卡片应该有正面和背面
        card_count = html_output.count('class="card"')
        self.assertEqual(card_count, len(self.valid_json_data["cards"]))
        
    def test_flashcard_tags_generation(self):
        """测试闪卡标签生成功能"""
        html_output = generate_flashcards(self.valid_json_data)
        
        # 检查标签是否被正确生成
        for card in self.valid_json_data["cards"]:
            if "tags" in card:
                for tag in card["tags"]:
                    self.assertIn(f'<span class="card-tag">{tag}</span>', html_output)
        
    def test_theme_application(self):
        """测试主题应用功能"""
        # 测试亮色主题
        light_html = generate_flashcards(self.valid_json_data)
        self.assertIn('--primary-color:', light_html)
        self.assertIn('--background-color:', light_html)
        
        # 修改数据为深色主题
        dark_theme_data = self.valid_json_data.copy()
        dark_theme_data["style"]["theme"] = "dark"
        dark_html = generate_flashcards(dark_theme_data)
        self.assertIn('--primary-color:', dark_html)
        self.assertIn('--background-color:', dark_html)
        
    def test_font_application(self):
        """测试字体应用功能"""
        html_output = generate_flashcards(self.valid_json_data)
        
        # 检查字体设置是否正确应用
        self.assertIn('--font-family: Arial, sans-serif;', html_output)
        
    def test_invalid_input_handling(self):
        """测试处理无效输入的情况"""
        # 测试使用 None 作为输入
        with self.assertRaises(Exception):
            generate_flashcards(None)
        
        # 测试使用空字典作为输入
        with self.assertRaises(Exception):
            generate_flashcards({})
        
    def test_html_structure_validation(self):
        """测试生成的 HTML 结构是否完整"""
        html_output = generate_flashcards(self.valid_json_data)
        
        # 检查 HTML 结构是否完整
        self.assertTrue(html_output.startswith('<!DOCTYPE html>'))
        self.assertIn('</html>', html_output)  # 确保有结束标签
        self.assertIn('<head>', html_output) and self.assertIn('</head>', html_output)
        self.assertIn('<body>', html_output) and self.assertIn('</body>', html_output)
        
        # 检查必要的 CSS 和 JavaScript 是否包含
        self.assertIn('<style>', html_output) and self.assertIn('</style>', html_output)
        self.assertIn('<script>', html_output) and self.assertIn('</script>', html_output)
        
    def test_interactive_features(self):
        """测试生成的 HTML 是否包含交互功能"""
        html_output = generate_flashcards(self.valid_json_data)
        
        # 检查是否包含交互功能所需的 JavaScript 代码
        self.assertIn('addEventListener', html_output)  # 事件监听器
        self.assertIn('click', html_output)  # 点击事件
        self.assertIn('flipped', html_output)  # 翻转类
        
    def test_cross_browser_compatibility(self):
        """测试生成的 HTML 是否考虑了跨浏览器兼容性"""
        html_output = generate_flashcards(self.valid_json_data)
        
        # 检查是否包含了跨浏览器兼容的代码
        self.assertIn('-webkit-backface-visibility: hidden;', html_output)  # WebKit 前缀
        self.assertIn('backface-visibility: hidden;', html_output)  # 标准属性

    def test_fill_blank_flashcards(self):
        """测试填空题类型的卡片渲染"""
        self.assertIsNotNone(self.fill_blank_json_data)
        html_output = generate_flashcards(self.fill_blank_json_data)
        self.assertIn('Python 是一种', html_output)
        self.assertIn('HTTP 的默认端口', html_output)
        # 卡片集合名称出现在左上角
        self.assertIn('<div class="deck-name">FlashCard</div>', html_output)

    def test_image_title_flashcards(self):
        """测试包含图片与标题的卡片渲染"""
        self.assertIsNotNone(self.image_title_json_data)
        html_output = generate_flashcards(self.image_title_json_data)
        # 标题和图片应被解析
        self.assertRegex(html_output, r'<h[12]')
        self.assertIn('<img', html_output)
        # 卡片集合名称
        self.assertIn('<div class="deck-name">FlashCard</div>', html_output)

    def test_table_flashcards(self):
        """测试包含表格的卡片渲染"""
        self.assertIsNotNone(self.table_json_data)
        html_output = generate_flashcards(self.table_json_data)
        # 表格结构应存在
        self.assertIn('<table>', html_output)
        # 卡片集合名称
        self.assertIn('<div class="deck-name">FlashCard</div>', html_output)

    def test_japanese_ruby_flashcards(self):
        """测试日文 RUBY 注音标签渲染通过"""
        self.assertIsNotNone(self.japanese_ruby_json_data)
        html_output = generate_flashcards(self.japanese_ruby_json_data)
        # ruby 标签应直通
        self.assertIn('<ruby>', html_output)
        self.assertIn('<rt>', html_output)
        # 中文解释存在
        self.assertIn('我去学校', html_output)
        # 卡片集合名称 - 修改为检查实际的标题
        self.assertIn('日文语法与注音测试', html_output)

if __name__ == '__main__':
    unittest.main()