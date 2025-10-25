import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from config import FLASHCARD_CONFIG


class Card(BaseModel):
    id: Optional[str] = None
    front: str = Field(..., min_length=1)
    back: str = ""
    tags: List[str] = Field(default_factory=list)
    
    @field_validator('front', mode='before')
    def check_empty_string(cls, v):
        """
        Validates that the front of the card string is not empty or contains only whitespace characters.

        Args:
            v (str): The string to validate.

        Returns:
            str: The validated string.

        Raises:
            ValueError: If the string is empty or contains only whitespace characters.
        """
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
    
    # 字体相关 - 支持CSS font简写，使用config中的默认值
    font: str = "Arial,  PingFang SC, Microsoft YaHei,  sans-serif"
    card_front_font: str = "24px/1.2 Arial, sans-serif, "
    card_back_font: str = "18px/1.2 Arial, sans-serif"
    
    # 卡片尺寸 - 与config.py保持一致
    card_width: str = "74.25mm"
    card_height: str = "105mm"
    
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

    # 显示控制 - 与config.py保持一致
    show_deck_name: bool = False
    show_card_index: bool = False
    deck_name_style: str = ""
    card_index_style: str = ""

    # 紧凑排版与字符数限制 - 与config.py保持一致
    compact_typography: bool = True
    front_char_limit: Optional[int] = 180
    back_char_limit: Optional[int] = 380
    
    @field_validator('theme')
    def validate_theme(cls, v):
        """
        Validates if the theme value is valid.

        Args:
            v (str): The theme string to validate.

        Returns:
            str: The validated theme string.

        Raises:
            ValueError: If the theme value is invalid.
        """
        # 支持的主题类型：
        # - light/dark: 基础颜色主题
        # - basic/advance/detail: 卡片背面样式主题
        valid_themes = FLASHCARD_CONFIG.get('available_themes', ['light', 'dark'])
        if v not in valid_themes:
            raise ValueError(f"无效的主题: {v}，有效主题为: {valid_themes}")
        return v
    
    @field_validator('font', 'card_front_font', 'card_back_font')
    def validate_font(cls, v):
        """Validate font CSS values"""
        if not v or not isinstance(v, str):
            raise ValueError('字体值必须是字符串')
        return v.strip()
    
    @field_validator('card_front_background', 'card_back_background')
    def validate_background(cls, v):
        """Validate background CSS values (color, image, gradient, etc.)"""
        if not v or not isinstance(v, str):
            raise ValueError('背景值必须是字符串')
        return v.strip()
    
    @field_validator('card_width', 'card_height')
    def validate_dimensions(cls, v):
        """Validate dimension values (px, %, em, rem, vw, vh, mm, cm, in, pt)"""
        if not isinstance(v, str):
            raise ValueError('尺寸值必须是字符串')
        v = v.strip()
        if not re.match(r'^\d+(\.\d+)?(px|%|em|rem|vw|vh|mm|cm|in|pt)$', v):
            raise ValueError('尺寸值格式无效，应为数字+单位（如300px, 50%, 2em, 74.25mm）')
        return v
    
    @field_validator('card_border')
    def validate_border(cls, v):
        """Validate border CSS values"""
        if not v or not isinstance(v, str):
            raise ValueError('边框值必须是字符串')
        return v.strip()
    
    @field_validator('card_border_radius', 'card_padding')
    def validate_css_length(cls, v):
        """Validate CSS length values"""
        if not re.match(r'^\d+(\.\d+)?(px|%|em|rem)(\s+\d+(\.\d+)?(px|%|em|rem))*$', v.strip()):
            raise ValueError('CSS长度值格式无效')
        return v.strip()
    
    @field_validator('card_front_text_align', 'card_back_text_align')
    def validate_text_align(cls, v):
        """
        Validate text alignment values.
        """
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
        """
        Validates that the flashcard list is not empty.

        Args:
            v (List[Card]): The list of flashcards to validate.

        Returns:
            List[Card]: The validated list of flashcards.

        Raises:
            ValueError: If the flashcard list is empty.
        """
        if not v:
            raise ValueError('闪卡列表不能为空')
        return v


def validate_json_structure(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates if the input JSON data structure conforms to the `FlashcardData` Pydantic model definition.

    Args:
        json_data (Dict[str, Any]): The JSON data dictionary to be validated.

    Returns:
        Dict[str, Any]: A dictionary containing the validation result. If validation is successful, returns `{"is_valid": True, "error": None}`;
                        if validation fails, returns `{"is_valid": False, "error": "error message"}`.
    """
    try:
        # 使用 Pydantic 模型进行验证
        validated_data = FlashcardData(**json_data)
        return {"is_valid": True, "error": None}
    except Exception as e:
        return {"is_valid": False, "error": str(e)}


def normalize_json_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes the input JSON data, populating missing default values and generating unique IDs for cards without them.

    Args:
        json_data (Dict[str, Any]): The raw JSON dictionary containing flashcard data.

    Returns:
        Dict[str, Any]: The normalized flashcard data dictionary with all missing default values populated and each card having an ID.
    """
    # 使用 Pydantic 模型进行验证和规范化
    flashcard_data = FlashcardData(**json_data)
    
    # 填充 id 字段
    for i, card in enumerate(flashcard_data.cards):
        if card.id is None:
            card.id = f"card-{i + 1}"
    
    # 使用自定义序列化处理datetime对象
    result = flashcard_data.model_dump(exclude_unset=False)
    
    # 处理datetime序列化
    if result.get('metadata') and result['metadata'].get('created_at'):
        if isinstance(result['metadata']['created_at'], datetime):
            result['metadata']['created_at'] = result['metadata']['created_at'].isoformat()
            
    return result