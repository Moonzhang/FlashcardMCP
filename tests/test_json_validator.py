import unittest
import json
from src.utils.json_validator import validate_json_structure, normalize_json_data

class TestJsonValidator(unittest.TestCase):
    
    def setUp(self):
        # 有效的 JSON 数据示例
        self.valid_json = {
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
            "metadata": {
                "title": "测试闪卡集",
                "description": "这是一个测试用的闪卡集",
                "version": "1.0",
                "author": "测试用户",
                "created_at": "2023-01-01T00:00:00Z"
            },
            "style": {
                "template": "default",
                "theme": "light",
                "font": "Arial, sans-serif",
                "colors": {
                    "primary": "#007bff",
                    "secondary": "#6c757d",
                    "background": "ffffff",
                    "text": "333333",
                    "card_bg": "ffffff",
                    "card_border": "dddddd"
                }
            }
        }
        
        # 缺少必要字段的 JSON 数据
        self.invalid_json_missing_fields = {
            # 缺少 required 的 cards 字段
        }
        
        # 格式错误的 JSON 数据
        self.invalid_json_format = {
            "cards": "这应该是一个数组而不是字符串"
        }
        
        # 最小化的有效 JSON 数据（只有必需字段）
        self.minimal_valid_json = {
            "cards": [
                {
                    "front": "问题",
                    "back": "答案"
                }
            ]
        }
        
    def test_valid_json_validation(self):
        """测试有效的 JSON 数据验证"""
        result = validate_json_structure(self.valid_json)
        self.assertTrue(result["is_valid"])
        self.assertIsNone(result["error"])
        
    def test_invalid_json_missing_fields(self):
        """测试缺少必要字段的 JSON 数据验证"""
        result = validate_json_structure(self.invalid_json_missing_fields)
        self.assertFalse(result["is_valid"])
        self.assertIsNotNone(result["error"])
        
    def test_invalid_json_format(self):
        """测试格式错误的 JSON 数据验证"""
        result = validate_json_structure(self.invalid_json_format)
        self.assertFalse(result["is_valid"])
        self.assertIsNotNone(result["error"])
        
    def test_minimal_valid_json_validation(self):
        """测试最小化的有效 JSON 数据验证"""
        result = validate_json_structure(self.minimal_valid_json)
        self.assertTrue(result["is_valid"])
        self.assertIsNone(result["error"])
        
    def test_json_normalization(self):
        """测试 JSON 数据规范化"""
        normalized_data = normalize_json_data(self.minimal_valid_json)
        
        # 检查规范化后的数据是否包含了所有可选字段的默认值
        self.assertIn("metadata", normalized_data)
        self.assertIn("style", normalized_data)
        
        # 检查默认值是否正确设置
        self.assertEqual(normalized_data["metadata"]["description"], "")
        self.assertEqual(normalized_data["style"]["theme"], "light")
        self.assertEqual(normalized_data["style"]["font"], "Arial, sans-serif")
        
    def test_json_normalization_with_existing_values(self):
        """测试带有已有值的 JSON 数据规范化"""
        normalized_data = normalize_json_data(self.valid_json)
        
        # 检查已有值是否被保留
        self.assertEqual(normalized_data["metadata"]["title"], self.valid_json["metadata"]["title"])
        self.assertEqual(normalized_data["metadata"]["description"], self.valid_json["metadata"]["description"])
        self.assertEqual(normalized_data["style"]["theme"], self.valid_json["style"]["theme"])
        
        # 检查卡片数量是否一致
        self.assertEqual(len(normalized_data["cards"]), len(self.valid_json["cards"]))
        
    def test_card_id_generation(self):
        """测试卡片 ID 自动生成"""
        normalized_data = normalize_json_data(self.valid_json)
        
        # 检查每张卡片是否都有唯一的 ID
        card_ids = [card["id"] for card in normalized_data["cards"]]
        self.assertEqual(len(card_ids), len(set(card_ids)))  # 确保所有 ID 都是唯一的
        
        # 检查 ID 格式是否正确（应该是字符串）
        for card_id in card_ids:
            self.assertIsInstance(card_id, str)
            self.assertTrue(len(card_id) > 0)
            
    def test_edge_case_empty_cards(self):
        """测试边缘情况：空卡片列表"""
        empty_cards_json = {
            "metadata": {
                "title": "空卡片测试"
            },
            "cards": []
        }
        
        # 验证应该失败，因为至少需要一张卡片
        result = validate_json_structure(empty_cards_json)
        self.assertFalse(result["is_valid"])
        self.assertIsNotNone(result["error"])
        
    def test_edge_case_card_without_back(self):
        """测试边缘情况：缺少背面内容的卡片"""
        invalid_card_json = {
            "metadata": {
                "title": "无效卡片测试"
            },
            "cards": [
                {
                    "front": "只有正面的卡片"
                    # 缺少 required 的 back 字段
                }
            ]
        }
        
        result = validate_json_structure(invalid_card_json)
        self.assertFalse(result["is_valid"])
        self.assertIsNotNone(result["error"])

if __name__ == '__main__':
    unittest.main()