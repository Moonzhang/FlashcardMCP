from src.utils.json_validator import validate_json_structure, normalize_json_data
from src.utils.markdown_parser import MarkdownParser
import os
from config import FLASHCARD_CONFIG, TEMPLATES_DIR
from jinja2 import Template, Environment, FileSystemLoader

# 模板目录路径 - 使用 config.py 中的配置
_template_dir = TEMPLATES_DIR


def generate_flashcards(json_data):
    """
    生成闪卡 HTML 内容。

    Generate flashcard HTML content.
    """
    # 验证并规范化 JSON 数据
    is_valid, errors = validate_json_structure(json_data)
    if not is_valid:
        raise ValueError(f"Invalid JSON structure: {errors}")

    normalized_data = normalize_json_data(json_data)

    # 解析元数据
    metadata = normalized_data.get('metadata', {})
    title = metadata.get('title', 'Untitled Flashcard Set')
    description = metadata.get('description', '')

    # 提取样式配置
    style_config = normalized_data.get('style', {})
    # 使用 config 中的默认模板名称作为回退
    template = style_config.get('template', FLASHCARD_CONFIG.get('default_template_name', 'minimal'))

    # 准备模板上下文
    md_parser = MarkdownParser()
    
    # 提取闪卡数据并转换 Markdown
    cards = []
    for card_data in normalized_data.get('cards', []):
        card_id = card_data.get('id', f"card-{len(cards) + 1}")
        front_content = md_parser.parse(card_data.get('front', ''))
        back_content = md_parser.parse(card_data.get('back', ''))
        tags = card_data.get('tags', [])
        
        cards.append({
            'id': card_id,
            'front': front_content,
            'back': back_content,
            'tags': tags
        })
    
    # 生成 HTML 内容
    html_content = render_flashcard_template(
        title=title,
        description=description,
        cards=cards,
        template=template,
        style_params=style_config,
        deck_name=title
    )
    
    return html_content


def render_flashcard_template(title, description, cards, template='minimal', style_params=None, deck_name='FlashCard'):
    """
    渲染闪卡模板，将闪卡数据、元数据和样式参数组合成 HTML 字符串。

    Renders a flashcard template, combining flashcard data, metadata, and style parameters into an HTML string.

    Args:
        title (str): 闪卡集的标题。
                     Title of the flashcard set.
        description (str): 闪卡集的描述。
                           Description of the flashcard set.
        cards (list): 包含闪卡内容的字典列表。
                      List of dictionaries containing flashcard content.
        template (str): 要使用的模板名称（例如 'minimal'）。
                        Name of the template to use (e.g., 'minimal').
        style_params (dict, optional): 包含样式配置的字典。默认为 None。
                                       Dictionary containing style configurations. Defaults to None.
        deck_name (str): 闪卡组的名称。默认为 'FlashCard'。
                         Name of the flashcard deck. Defaults to 'FlashCard'.

    Returns:
        str: 渲染后的 HTML 字符串。
             Rendered HTML string.
    """

    
    # 获取模板配置
    available_templates = FLASHCARD_CONFIG.get('available_templates', {})
    
    # 尝试从配置中获取模板文件路径
    template_file = None
    if template in available_templates:
        template_config = available_templates[template]
        # 适配新的配置结构：模板配置现在是字典，包含file_path字段
        if isinstance(template_config, dict):
            template_file = template_config.get('file_path')
        else:
            # 兼容旧的配置结构：直接是文件名字符串
            template_file = template_config
    else:
        pass
    
    # 尝试加载模板文件
    template_content = None
    if template_file:
        template_path = os.path.join(_template_dir, template_file)
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            except Exception as e:
                pass
        else:
            pass
    
    # 如果仍然没有找到模板，使用 config 中的默认模板名称回退到 'available_templates' 对应模板
    if not template_content:
        fallback_template_name = FLASHCARD_CONFIG.get('default_template_name', 'default')
        template = fallback_template_name
        template_config = available_templates.get(template, {})
        if isinstance(template_config, dict):
            template_file = template_config.get('file_path')
        else:
            template_file = template_config
        
        if template_file:
            template_path = os.path.join(_template_dir, template_file)
            if os.path.exists(template_path):
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                except Exception as e:
                    pass
            else:
                pass
        else:
            pass
    
    # 如果还是没有找到模板内容，抛出异常
    if not template_content:
        raise ValueError(f"No template found for '{template}' and default template is also unavailable")

    
    # 初始化 style_params
    if style_params is None:
        style_params = {}

    # 从 style_params 中获取主题和颜色配置
    # 优先使用 style_params，其次使用 config 的默认样式
    default_style = FLASHCARD_CONFIG.get('default_style', {})
    theme = style_params.get('theme', default_style.get('theme', 'light'))
    colors = style_params.get('colors', {})
    # 新增：显示控制 & 紧凑排版 & 字数限制（统一回退到 config 默认）
    show_deck_name = bool(style_params.get('show_deck_name', default_style.get('show_deck_name', False)))
    show_card_index = bool(style_params.get('show_card_index', default_style.get('show_card_index', False)))
    show_tags = bool(style_params.get('show_tags', default_style.get('show_tags', True)))
    deck_name_style = style_params.get('deck_name_style', '')
    card_index_style = style_params.get('card_index_style', '')
    compact_typography = bool(style_params.get('compact_typography', default_style.get('compact_typography', True)))
    front_char_limit = style_params.get('front_char_limit') if style_params.get('front_char_limit') is not None else default_style.get('front_char_limit')
    back_char_limit = style_params.get('back_char_limit') if style_params.get('back_char_limit') is not None else default_style.get('back_char_limit')
    # 主题类（用于控制背面风格 basic/advance/detail，不更改尺寸）
    theme_class = f"theme-{theme}" if theme in ['basic','advance','detail'] else ("theme-dark" if theme == 'dark' else 'theme-light')

    # 设置默认颜色
    default_colors = {
        'primary': '#007bff',
        'secondary': '#6c757d',
        'background': '#ffffff' if theme != 'dark' else '#1a1a1a',
        'text': '#333333' if theme != 'dark' else '#ffffff',
        'card_bg': '#ffffff' if theme != 'dark' else '#2d2d2d',
        'card_front_bg': '#ffffff',
        'card_back_bg': '#f5f5f5',
        'card_border': '#dddddd' if theme != 'dark' else '#444444'
    }

    # 根据主题获取默认颜色
    theme_style_key = f'{theme}_theme_style'
    theme_config = FLASHCARD_CONFIG.get(theme_style_key, FLASHCARD_CONFIG['default_style'])
    default_colors = theme_config.get('colors', FLASHCARD_CONFIG['default_style']['colors'])

    # 合并用户自定义颜色和默认颜色
    for key, value in default_colors.items():
        if key in colors:
            # 确保颜色值以#开头
            color_value = colors[key]
            if isinstance(color_value, str) and not color_value.startswith('#'):
                color_value = '#' + color_value
            default_colors[key] = color_value
    
    # 从 style_params 中获取新的CSS样式值，如果不存在则使用默认值
    card_width = style_params.get('card_width', default_style.get('card_width'))
    card_height = style_params.get('card_height', default_style.get('card_height')) 
    card_front_text_align = style_params.get('card_front_text_align', 'center')
    card_back_text_align = style_params.get('card_back_text_align', 'left')
    card_border = style_params.get('card_border') or default_colors.get('card_border')
    card_border_radius = style_params.get('card_border_radius', '8px')
    card_padding = style_params.get('card_padding', '20px')
    card_box_shadow = style_params.get('card_box_shadow', '0 2px 4px rgba(0,0,0,0.1)')

    # 字体相关 - 支持CSS font简写，从font变量中提取字体族
    font_css = style_params.get('font', default_style.get('font', 'Arial, sans-serif'))
    # 前后字体
    card_front_font = style_params.get('card_front_font')
    card_back_font = style_params.get('card_back_font')

    # 生成卡片HTML片段（简化预览环境）
    description_section = f"<p class=\"description\">{description}</p>" if description else ""
    filter_section = ""
    cards_html = "".join([
        f"<div class=\"card\"><div class=\"card-front\">{c['front']}</div><div class=\"card-back\">{c['back']}</div></div>" for c in cards
    ])

    context = {
        'title': title,
        'theme': theme,
        'theme_class': theme_class,
        'compact_typography': compact_typography,
        'show_deck_name': show_deck_name,
        'show_card_index': show_card_index,
        'show_tags': show_tags,
        'deck_name_style': deck_name_style,
        'card_index_style': card_index_style,
        'front_char_limit': front_char_limit,
        'back_char_limit': back_char_limit,
        'total_cards': str(len(cards)),
        'primary_color': default_colors['primary'],
        'secondary_color': default_colors['secondary'],
        'background_color': default_colors['background'],
        'text_color': default_colors['text'],
        'card_bg': default_colors['card_bg'],
        'card_front_bg': default_colors['card_front_bg'],
        'card_back_bg': default_colors['card_back_bg'],
        'card_border': card_border,
        'card_border_radius': card_border_radius,
        'card_width': card_width,
        'card_height': card_height,
        'card_front_text_align': card_front_text_align,
        'card_back_text_align': card_back_text_align,
        'card_padding': card_padding,
        'card_box_shadow': card_box_shadow,
        'font_css': font_css,
        'card_front_font': card_front_font,
        'card_back_font': card_back_font,
        'description_section': description_section,
        'filter_section': filter_section,
        'cards': cards,
        'cards_html': cards_html,
        'deck_name': deck_name
    }

    # 检查是否使用模板继承
    if template_content and '{% extends' in template_content:
        # 使用 Environment 和 FileSystemLoader 来支持模板继承
        env = Environment(loader=FileSystemLoader(_template_dir))
        # 使用配置中的实际文件名而不是 template.html
        template_config = FLASHCARD_CONFIG['available_templates'].get(template, {})
        template_filename = template_config.get('file_path', f"{template}.html")
        tmpl = env.get_template(template_filename)
        rendered_html = tmpl.render(**context)
    else:
        # 使用传统的 Template 方式
        tmpl = Template(template_content)
        rendered_html = tmpl.render(**context)
    
    return rendered_html
