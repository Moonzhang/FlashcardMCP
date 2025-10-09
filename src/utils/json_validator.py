import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Card(BaseModel):
    id: Optional[str] = None
    front: str = Field(..., min_length=1)
    back: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    
    @field_validator('front', 'back', mode='before')
    def check_empty_string(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError('字符串不能为空或只包含空白字符')
        return v


class Metadata(BaseModel):
    title: str = "最小化测试闪卡集"
    description: str = ""
    version: str = "1.0.0"
    created_at: Optional[datetime] = None


class Style(BaseModel):
    template: str = "default"
    theme: str = "light"
    colors: Dict[str, Any] = Field(default_factory=dict)
    font: str = "Arial, sans-serif"
    
    @field_validator('theme')
    def validate_theme(cls, v):
        valid_themes = ['light', 'dark', 'custom']
        if v not in valid_themes:
            raise ValueError(f"无效的主题: {v}，有效主题为: {valid_themes}")
        return v


class FlashcardData(BaseModel):
    cards: List[Card]
    metadata: Optional[Metadata] = Field(default_factory=Metadata)
    style: Optional[Style] = Field(default_factory=Style)
    
    @field_validator('cards')
    def check_cards_not_empty(cls, v):
        if not v:
            raise ValueError('闪卡列表不能为空')
        return v


def validate_json_structure(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """验证 JSON 数据的结构是否符合要求"""
    try:
        # 使用 Pydantic 模型进行验证
        validated_data = FlashcardData(**json_data)
        return {"is_valid": True, "error": None}
    except Exception as e:
        return {"is_valid": False, "error": str(e)}


def normalize_json_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """规范化 JSON 数据，填充缺失的默认值"""
    # 使用 Pydantic 模型进行验证和规范化
    flashcard_data = FlashcardData(**json_data)
    
    # 填充 id 字段
    for i, card in enumerate(flashcard_data.cards):
        if card.id is None:
            card.id = f"card-{i + 1}"
            
    return flashcard_data.dict(exclude_unset=True)


# 测试函数
def test_json_validation():
    """测试 JSON 验证功能"""
    # 测试有效的 JSON 数据
    valid_data = {
        "metadata": {
            "title": "测试闪卡集",
            "description": "这是一个测试用的闪卡集"
        },
        "cards": [
            {
                "id": "test-1",
                "front": "什么是Python？",
                "back": "Python是一种高级编程语言。",
                "tags": ["编程", "Python"]
            },
            {
                "front": "什么是Flask？",
                "back": "Flask是一个轻量级的Python Web框架。"
            }
        ],
        "style": {
                "template": "default",
                "theme": "light",
                "colors": {
                    "primary": "#007bff"
                }
            }
    }
    
    try:
        validation_result = validate_json_structure(valid_data)
        if validation_result["is_valid"]:
            normalized_data = normalize_json_data(valid_data)
            print("有效的 JSON 数据验证通过！")
            print("规范化后的数据:", normalized_data)
        else:
            print(f"错误: {validation_result['error']}")
    except ValueError as e:
        print(f"错误: {e}")
    
    # 测试无效的 JSON 数据（空闪卡列表）
    invalid_data_1 = {
        "metadata": {
            "title": "测试闪卡集"
        },
        "cards": [],
        "style": {
            "template": "default",
            "theme": "light"
        }
    }
    
    try:
        validation_result = validate_json_structure(invalid_data_1)
        if validation_result["is_valid"]:
            print("错误: 应该检测到空闪卡列表")
        else:
            print(f"预期的错误: {validation_result['error']}")
    except ValueError as e:
        print(f"预期的错误: {e}")
    
    # 测试无效的 JSON 数据（缺少闪卡内容）
    invalid_data_2 = {
        "metadata": {
            "title": "测试闪卡集"
        },
        "cards": [
            {
                "front": "",
                "back": "Python是一种高级编程语言。"
            }
        ],
        "style": {
            "template": "default",
            "theme": "light"
        }
    }
    
    try:
        validation_result = validate_json_structure(invalid_data_2)
        if validation_result["is_valid"]:
            print("错误: 应该检测到空的闪卡内容")
        else:
            print(f"预期的错误: {validation_result['error']}")
    except ValueError as e:
        print(f"预期的错误: {e}")


if __name__ == "__main__":
    # 运行测试
    test_json_validation()
