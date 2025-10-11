import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Card(BaseModel):
    id: Optional[str] = None
    front: str = Field(..., min_length=1)
    back: str = ""
    tags: List[str] = Field(default_factory=list)
    
    @field_validator('front', mode='before')
    def check_empty_string(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError('字符串不能为空或只包含空白字符')
        return v


class Metadata(BaseModel):
    title: str = "FlashCard"
    description: str = ""
    version: str = "1.0.0"
    created_at: Optional[datetime] = None


class Style(BaseModel):
    template: str = "minimal"
    theme: str = "light"
    colors: Dict[str, Any] = Field(default_factory=dict)
    
    # 字体相关 - 支持CSS font简写
    font: str = "Arial, sans-serif"
    card_front_font: str = "24px/1.2 Arial, sans-serif"
    card_back_font: str = "18px/1.2 Arial, sans-serif"
    
    # 卡片尺寸
    card_width: str = "300px"
    card_height: str = "200px"
    
    # 背景 - 支持颜色、渐变、图片
    card_front_background: str = "#ffffff"
    card_back_background: str = "#f5f5f5"
    
    # 文本对齐
    card_front_text_align: str = "center"
    card_back_text_align: str = "center"
    
    # 边框和装饰
    card_border: str = "1px solid #dddddd"
    card_border_radius: str = "8px"
    card_padding: str = "20px"
    card_box_shadow: str = "0 2px 4px rgba(0,0,0,0.1)"
    
    @field_validator('theme')
    def validate_theme(cls, v):
        valid_themes = ['light', 'dark', 'custom']
        if v not in valid_themes:
            raise ValueError(f"无效的主题: {v}，有效主题为: {valid_themes}")
        return v
    
    @field_validator('font', 'card_front_font', 'card_back_font')
    def validate_font(cls, v):
        """验证字体CSS值"""
        if not v or not isinstance(v, str):
            raise ValueError('字体值必须是字符串')
        return v.strip()
    
    @field_validator('card_front_background', 'card_back_background')
    def validate_background(cls, v):
        """验证背景CSS值（颜色、图片、渐变等）"""
        if not v or not isinstance(v, str):
            raise ValueError('背景值必须是字符串')
        return v.strip()
    
    @field_validator('card_width', 'card_height')
    def validate_dimensions(cls, v):
        """验证尺寸值（px, %, em, rem等）"""
        if not re.match(r'^\d+(\.\d+)?(px|%|em|rem|vw|vh)$', v.strip()):
            raise ValueError('尺寸值格式无效，应为数字+单位（如300px, 50%, 2em）')
        return v.strip()
    
    @field_validator('card_border')
    def validate_border(cls, v):
        """验证边框CSS值"""
        if not v or not isinstance(v, str):
            raise ValueError('边框值必须是字符串')
        return v.strip()
    
    @field_validator('card_border_radius', 'card_padding')
    def validate_css_length(cls, v):
        """验证CSS长度值"""
        if not re.match(r'^\d+(\.\d+)?(px|%|em|rem)(\s+\d+(\.\d+)?(px|%|em|rem))*$', v.strip()):
            raise ValueError('CSS长度值格式无效')
        return v.strip()
    
    @field_validator('card_front_text_align', 'card_back_text_align')
    def validate_text_align(cls, v):
        """验证文本对齐值"""
        valid_aligns = ['left', 'center', 'right', 'justify', 'start', 'end']
        if v not in valid_aligns:
            raise ValueError(f"无效的文本对齐值: {v}，有效值为: {valid_aligns}")
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
            
    return flashcard_data.model_dump(exclude_unset=False)