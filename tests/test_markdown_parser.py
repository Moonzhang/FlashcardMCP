import unittest
from src.utils.markdown_parser import MarkdownParser, create_custom_parser

class TestMarkdownParser(unittest.TestCase):
    
    def setUp(self):
        # 创建 MarkdownParser 实例
        self.parser = MarkdownParser()
    
    def test_basic_markdown_parsing(self):
        """测试基本的 Markdown 解析功能"""
        markdown_text = "# 标题\n\n这是一个**粗体**文本和*斜体*文本。"
        html_output = self.parser.parse(markdown_text)
        
        # 检查解析结果是否包含预期的 HTML 标签
        self.assertIn("<h1>", html_output)
        self.assertIn("<strong>", html_output)
        self.assertIn("<em>", html_output)
        
    def test_code_block_parsing(self):
        """测试代码块解析功能"""
        markdown_text = "```python\nprint('Hello, World!')\n```"
        html_output = self.parser.parse(markdown_text)
        
        # 检查代码块是否被正确解析
        self.assertIn("<pre>", html_output)
        self.assertIn("<code", html_output)
        self.assertIn("print('Hello, World!')", html_output)
        
    def test_table_parsing(self):
        """测试表格解析功能"""
        markdown_text = "| 名称 | 描述 |\n|-----|-----|\n| 项目1 | 这是项目1的描述 |\n| 项目2 | 这是项目2的描述 |"
        html_output = self.parser.parse(markdown_text)
        
        # 检查表格是否被正确解析
        self.assertIn("<table", html_output)
        self.assertIn("<tr>", html_output)
        self.assertIn("<td>", html_output)
        self.assertIn("项目1", html_output)
        
    def test_list_parsing(self):
        """测试列表解析功能"""
        # 无序列表
        ul_text = "- 项目1\n- 项目2\n- 项目3"
        ul_html = self.parser.parse(ul_text)
        self.assertIn("<ul>", ul_html)
        self.assertIn("<li>", ul_html)
        
        # 有序列表
        ol_text = "1. 第一项\n2. 第二项\n3. 第三项"
        ol_html = self.parser.parse(ol_text)
        self.assertIn("<ol>", ol_html)
        self.assertIn("<li>", ol_html)
        
    def test_link_and_image_parsing(self):
        """测试链接和图片解析功能"""
        markdown_text = "[链接文本](https://example.com)\n![图片描述](https://example.com/image.jpg)"
        html_output = self.parser.parse(markdown_text)
        
        # 检查链接是否被正确解析
        self.assertIn("<a href=", html_output)
        self.assertIn("链接文本", html_output)
        self.assertIn("https://example.com", html_output)
        
        # 检查图片是否被正确解析
        self.assertIn("<img src=", html_output)
        self.assertIn("图片描述", html_output)
        self.assertIn("https://example.com/image.jpg", html_output)
        
    def test_blockquote_parsing(self):
        """测试引用块解析功能"""
        markdown_text = "> 这是一个引用文本\n> 这是引用的第二行"
        html_output = self.parser.parse(markdown_text)
        
        # 检查引用块是否被正确解析
        self.assertIn("<blockquote>", html_output)
        self.assertIn("这是一个引用文本", html_output)
        self.assertIn("这是引用的第二行", html_output)
        
    def test_admonition_parsing(self):
        """测试警告框解析功能"""
        markdown_text = "!!! note\n    这是一个提示框内容"
        html_output = self.parser.parse(markdown_text)
        
        # 检查警告框是否被正确解析
        self.assertIn("<div class=\"admonition note\">", html_output)
        self.assertIn("这是一个提示框内容", html_output)
        
    def test_toc_generation(self):
        """测试目录生成功能"""
        markdown_text = "# 一级标题\n## 二级标题\n### 三级标题\n## 另一个二级标题"
        # 创建启用了目录扩展的解析器
        toc_parser = MarkdownParser(extensions=['toc'])
        html_output = toc_parser.parse(markdown_text)
        
        # 检查目录是否被正确生成
        self.assertIn("<div class=\"toc\">", html_output)
        self.assertIn("<li><a href=\"#一级标题\">一级标题</a>", html_output)
        self.assertIn("<li><a href=\"#二级标题\">二级标题</a>", html_output)
        
    def test_empty_string_parsing(self):
        """测试空字符串解析"""
        html_output = self.parser.parse("")
        self.assertEqual(html_output, "")
        
    def test_special_characters_escaping(self):
        """测试特殊字符转义"""
        markdown_text = "这是一个包含特殊字符的文本: & < > \" '"
        html_output = self.parser.parse(markdown_text)
        
        # 检查特殊字符是否被正确转义
        self.assertIn("&amp;", html_output)  # & 转义为 &amp;
        self.assertIn("&lt;", html_output)   # < 转义为 &lt;
        self.assertIn("&gt;", html_output)   # > 转义为 &gt;
        self.assertIn("&quot;", html_output)  # " 转义为 &quot;
        self.assertIn("&#x27;", html_output)  # ' 转义为 &#x27;
        
    def test_custom_parser_creation(self):
        """测试创建自定义解析器"""
        # 创建只启用了基本功能的解析器
        minimal_parser = create_custom_parser(extensions=['extra'])
        markdown_text = "# 标题\n\n这是一个测试文本"
        html_output = minimal_parser.parse(markdown_text)
        
        # 验证解析结果
        self.assertIn("<h1>", html_output)
        self.assertIn("这是一个测试文本", html_output)
        
    def test_parse_with_metadata(self):
        """测试解析带有元数据的 Markdown 文本"""
        # 注意：这个功能需要扩展支持
        try:
            # 即使没有实际的元数据，方法也应该正常运行
            result = self.parser.parse_with_metadata("# 标题")
            self.assertIsInstance(result, dict)
            self.assertIn("html", result)
            self.assertIn("toc", result)
            self.assertIn("<h1>", result["html"])
        except NotImplementedError:
            # 如果方法未实现，跳过此测试
            self.skipTest("parse_with_metadata 方法尚未实现完整功能")

if __name__ == '__main__':
    unittest.main()