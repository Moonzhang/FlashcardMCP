from src.utils.json_validator import validate_json_structure, normalize_json_data
from src.utils.markdown_parser import MarkdownParser
import os
from config import FLASHCARD_CONFIG, TEMPLATES_DIR
from jinja2 import Template, Environment, FileSystemLoader

# 模板目录路径 - 使用 config.py 中的配置
_template_dir = TEMPLATES_DIR

def generate_flashcards(json_data):
    """
    根据 JSON 数据生成闪卡 HTML 页面。

    Generates flashcard HTML pages based on JSON data.

    Args:
        json_data (dict): 包含闪卡数据、元数据和样式配置的 JSON 字典。
                          JSON dictionary containing flashcard data, metadata, and style configurations.

    Returns:
        str: 渲染后的闪卡 HTML 内容。
             Rendered flashcard HTML content.

    Raises:
        ValueError: 如果 JSON 结构无效或闪卡转换失败。
                    If the JSON structure is invalid or flashcard conversion fails.
    """
    # 验证 JSON 结构：使用返回的字典结果并在无效时抛出异常
    validation_result = validate_json_structure(json_data)
    if isinstance(validation_result, dict):
        if not validation_result.get('is_valid', False):
            raise ValueError(validation_result.get('error') or 'Invalid JSON structure')
    else:
        # 如果实现变动为抛异常，捕获并转换为统一异常
        try:
            validate_json_structure(json_data)
        except ValueError as e:
            raise ValueError(f"Invalid JSON structure: {str(e)}")
    
    # 规范化 JSON 数据
    normalized_data = normalize_json_data(json_data)
    
    # 提取元数据
    metadata = normalized_data.get('metadata', {})
    title = metadata.get('title', 'FlashCard')
    description = metadata.get('description', '')
    
    # 提取样式配置
    style_config = normalized_data.get('style', {})
    template = style_config.get('template', 'minimal')
    
    # 创建 Markdown 解析器实例
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
    # 添加调试信息
    print(f"🔍 [DEBUG] render_flashcard_template called with template='{template}'")
    
    # 获取模板配置
    available_templates = FLASHCARD_CONFIG.get('available_templates', {})
    print(f"🔍 [DEBUG] available_templates: {available_templates}")
    
    # 尝试从配置中获取模板文件路径
    template_file = None
    if template in available_templates:
        template_config = available_templates[template]
        print(f"🔍 [DEBUG] Template config for '{template}': {template_config}")
        # 适配新的配置结构：模板配置现在是字典，包含file_path字段
        if isinstance(template_config, dict):
            template_file = template_config.get('file_path')
        else:
            # 兼容旧的配置结构：直接是文件名字符串
            template_file = template_config
        print(f"🔍 [DEBUG] Extracted template_file: {template_file}")
        print(f"🔍 [DEBUG] template_file type: {type(template_file)}")
    else:
        print(f"🔍 [DEBUG] Template '{template}' not found in available_templates")
    
    # 尝试加载模板文件
    template_content = None
    if template_file:
        template_path = os.path.join(_template_dir, template_file)
        print(f"🔍 [DEBUG] Trying to load template from: {template_path}")
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                print(f"🔍 [DEBUG] Successfully loaded template from {template_path}")
            except Exception as e:
                print(f"🔍 [DEBUG] Failed to load template from {template_path}: {e}")
        else:
            print(f"🔍 [DEBUG] Template file does not exist: {template_path}")
    
    # 如果没有找到模板文件，检查是否有其他可用的模板文件
    if not template_content:
        print(f"🔍 [DEBUG] Template '{template}' not found in configuration, checking available templates")
        # 不再尝试直接查找 template.html，因为这会导致配置不一致
    
    # 如果仍然没有找到模板，使用内联模板
    if not template_content:
        print(f"🔍 [DEBUG] No template file found, using inline template")
        template_content = get_inline_template()

    # 初始化 style_params
    if style_params is None:
        style_params = {}

    # 从 style_params 中获取主题和颜色配置
    theme = style_params.get('theme', 'light')
    colors = style_params.get('colors', {})
    font = style_params.get('font', 'Arial, sans-serif')

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

    # 合并用户自定义颜色和默认颜色
    for key, value in default_colors.items():
        if key in colors:
            # 确保颜色值以#开头
            color_value = colors[key]
            if not color_value.startswith('#'):
                color_value = '#' + color_value
            default_colors[key] = color_value
    
    # 从 style_params 中获取新的CSS样式值，如果不存在则使用默认值
    card_width = style_params.get('card_width', '300px')
    card_height = style_params.get('card_height', '200px')
    card_front_background = style_params.get('card_front_background', '#ffffff')
    card_back_background = style_params.get('card_back_background', '#f5f5f5')
    card_front_text_align = style_params.get('card_front_text_align', 'center')
    card_back_text_align = style_params.get('card_back_text_align', 'center')
    card_border = style_params.get('card_border', '1px solid #dddddd')
    card_border_radius = style_params.get('card_border_radius', '8px')
    card_padding = style_params.get('card_padding', '20px')
    card_box_shadow = style_params.get('card_box_shadow', '0 2px 4px rgba(0,0,0,0.1)')
    
    # 字体相关 - 支持CSS font简写，从font变量中提取字体族
    font_css = style_params.get('font', 'Arial, sans-serif')
    # 从font_css中提取字体族部分，用于font_family
    if 'px' in font_css or '/' in font_css:
        # 如果包含字体大小信息，提取字体族部分
        font_parts = font_css.split()
        if len(font_parts) >= 2:
            font = ' '.join(font_parts[1:])  # 去掉字体大小，保留字体族
        else:
            font = font_css
    else:
        font = font_css
    card_front_font = style_params.get('card_front_font', '24px/1.2 Arial, sans-serif')
    card_back_font = style_params.get('card_back_font', '18px/1.2 Arial, sans-serif')
    
    # 生成描述部分
    description_section = f'<p>{description}</p>' if description else ''
    
    # 生成过滤器部分
    all_tags = set()
    for card in cards:
        all_tags.update(card['tags'])
    
    filter_section = ''
    if all_tags:
        filter_buttons = ['<button class="filter-btn active" data-tag="all">全部</button>']
        for tag in sorted(all_tags):
            filter_buttons.append(f'<button class="filter-btn" data-tag="{tag}">{tag}</button>')
        
        filter_section = f'''
        <!-- 过滤器 -->
        <div class="filter-container" id="filterContainer">
            {''.join(filter_buttons)}
        </div>
        '''

    # 生成闪卡内容
    cards_html = ''
    for i, card in enumerate(cards):
        card_id = f"card-{i}"
        tags_str = ','.join(card['tags']) if card['tags'] else ''
        
        # 生成标签HTML
        tags_html = ''
        if card['tags']:
            tag_elements = [f'<span class="card-tag">{tag}</span>' for tag in card['tags']]
            tags_html = f'<div class="card-tags">{"".join(tag_elements)}</div>'
        
        cards_html += f'''
        <div class="card" id="{card_id}" data-tags="{tags_str}">
            <div class="card-inner">
                <div class="card-front">
                    <div class="deck-name">{deck_name}</div>
                    <div class="card-content">{card['front']}</div>
                    {tags_html}
                </div>
                <div class="card-back">
                    <div class="card-content">{card['back']}</div>
                </div>
            </div>
        </div>
        '''
    
    # 选择渲染方式：优先使用Jinja2
    context = {
        'title': title,
        'description': description,
        'cards': cards,  # 直接传递卡片列表
        'font_family': font,
        'theme': theme,
        'total_cards': str(len(cards)),
        'primary_color': default_colors['primary'],
        'secondary_color': default_colors['secondary'],
        'background_color': default_colors['background'],
        'text_color': default_colors['text'],
        'card_bg': default_colors['card_bg'],
        'card_front_bg': card_front_background,
        'card_back_bg': card_back_background,
        'card_border': card_border,
        'card_width': card_width,
        'card_height': card_height,
        'card_front_text_align': card_front_text_align,
        'card_back_text_align': card_back_text_align,
        'card_border_radius': card_border_radius,
        'card_padding': card_padding,
        'card_box_shadow': card_box_shadow,
        'font_css': font_css,
        'card_front_font': card_front_font,
        'card_back_font': card_back_font,
        'description_section': description_section,
        'filter_section': filter_section,
        'cards_html': cards_html,
        'deck_name': deck_name
    }
    
    # 添加模板内容调试信息
    print(f"🔍 [DEBUG] Template content length: {len(template_content)}")
    print(f"🔍 [DEBUG] Template content preview (first 200 chars): {template_content[:200]}")
    
    # 检查是否使用模板继承
    if template_content and '{% extends' in template_content:
        # 使用 Environment 和 FileSystemLoader 来支持模板继承
        print(f"🔍 [DEBUG] Template uses inheritance, using Environment with FileSystemLoader")
        env = Environment(loader=FileSystemLoader(_template_dir))
        # 使用配置中的实际文件名而不是 template.html
        template_config = FLASHCARD_CONFIG['available_templates'].get(template, {})
        template_filename = template_config.get('file_path', f"{template}.html")
        tmpl = env.get_template(template_filename)
        rendered_html = tmpl.render(**context)
    else:
        # 使用传统的 Template 方式
        print(f"🔍 [DEBUG] Template does not use inheritance, using Template directly")
        tmpl = Template(template_content)
        rendered_html = tmpl.render(**context)
    
    print(f"🔍 [DEBUG] Rendered HTML length: {len(rendered_html)}")
    print(f"🔍 [DEBUG] Rendered HTML preview (first 200 chars): {rendered_html[:200]}")
    
    return rendered_html

def get_inline_template():
    """
    提供内联的默认闪卡 HTML 模板内容。

    Provides inline default flashcard HTML template content.

    Returns:
        str: 包含默认 HTML 模板的字符串。
             String containing the default HTML template.
    """
    return '''<!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{{ title }}</title>
                <meta name="description" content="{{ description }}">
                <style>
                    /* theme: {{ theme }} */
                    /* font: {{ font_family }} */
                    :root {
                        --primary-color: {{ primary_color }};
                        --secondary-color: {{ secondary_color }};
                        --background-color: {{ background_color }};
                        --text-color: {{ text_color }};
                        --card-bg: {{ card_bg }};
                        --card-front-bg: {{ card_front_bg }};
                        --card-back-bg: {{ card_back_bg }};
                        --card-border: {{ card_border }};
                        --card-border-radius: {{ card_border_radius }};
                        --card-padding: {{ card_padding }};
                        --card-box-shadow: {{ card_box_shadow }};
                        --font-family: {{ font_family }};
                        --font-css: {{ font_css }};
                        --card-front-font: {{ card_front_font }};
                        --card-back-font: {{ card_back_font }};
                        --card-width: {{ card_width }};
                        --card-height: {{ card_height }};
                        --card-front-text-align: {{ card_front_text_align }};
                        --card-back-text-align: {{ card_back_text_align }};
                    }
                    
                    * {
                        box-sizing: border-box;
                        margin: 0;
                        padding: 0;
                    }
                    
                    body {
                        font-family: var(--font-family);
                        background-color: var(--background-color);
                        color: var(--text-color);
                        line-height: 1.6;
                        padding: 20px;
                        font-size: var(--font-size);
                    }
                    
                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                    }
                    
                    header {
                        text-align: center;
                        margin-bottom: 30px;
                        padding: 20px;
                        border-bottom: 1px solid var(--card-border);
                    }
                    
                    h1 {
                        color: var(--primary-color);
                        margin-bottom: 10px;
                    }
                    
                    .flashcard-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                        gap: 20px;
                        margin-bottom: 30px;
                    }
                    
                    .card {
                        width: var(--card-width);
                        height: var(--card-height);
                        perspective: 1000px;
                        cursor: pointer;
                    }
                    
                    .card-inner {
                        position: relative;
                        width: 100%;
                        height: 100%;
                        text-align: center;
                        transition: transform 0.6s;
                        transform-style: preserve-3d;
                        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                        border-radius: 8px;
                    }
                    
                    .card.flipped .card-inner {
                        transform: rotateY(180deg);
                    }
                    
                    .card-front, .card-back {
                        position: absolute;
                        width: 100%;
                        height: 100%;
                        -webkit-backface-visibility: hidden;
                        backface-visibility: hidden;
                        padding: 20px;
                        overflow-y: auto;
                        background-color: var(--card-front-bg);
                        border: 1px solid var(--card-border);
                        border-radius: 8px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        background-image: var(--card-front-image);
                        background-size: cover;
                        background-position: center;
                    }
                    
                    .card-back {
                        transform: rotateY(180deg);
                        background-color: var(--card-back-bg);
                        background-image: var(--card-back-image);
                    }
                    
                    .card-content {
                        max-height: 100%;
                        overflow-y: auto;
                        width: 100%;
                        font-size: var(--font-size);
                    }
                    
                    .card-front .card-content {
                        text-align: var(--card-front-text-align);
                        font-size: var(--front-font-size);
                    }
                    
                    .card-back .card-content {
                        text-align: var(--card-back-text-align);
                        font-size: var(--back-font-size);
                    }
                    
                    .card-tags {
                        display: flex;
                        flex-wrap: wrap;
                        gap: 5px;
                        margin-top: 10px;
                        justify-content: center;
                    }
                    
                    .card-tag {
                        background-color: var(--secondary-color);
                        color: white;
                        padding: 2px 8px;
                        border-radius: 12px;
                        font-size: 0.8em;
                    }
                    
                    .card-controls {
                        display: flex;
                        justify-content: center;
                        gap: 10px;
                        margin-bottom: 20px;
                        flex-wrap: wrap;
                    }
                    
                    button {
                        background-color: var(--primary-color);
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-family: inherit;
                    }
                    
                    button:hover {
                        opacity: 0.8;
                    }
                    
                    /* 响应式设计 */
                    @media (max-width: 768px) {
                        .flashcard-grid {
                            grid-template-columns: 1fr;
                        }
                        
                        .card {
                            height: 200px;
                        }
                    }
                </style>
                {% if font_css %}
                <style>
                    @import url('{{ font_css }}');
                </style>
                {% endif %}
            </head>
            <body>
                <h1>{{ title }}</h1>
                {% if description_section %}
                <div class="description-section">
                    {{ description_section }}
                </div>
                {% endif %}
                {% if filter_section %}
                <div class="filter-section">
                    {{ filter_section }}
                </div>
                {% endif %}
                <div class="container">
                    <div class="flashcard-grid">
                        {% for card in cards %}
                        <div class="card" id="{{ card.id }}" data-tags="{{ card.tags | join(',') }}">
                            <div class="card-inner">
                                <div class="card-front">
                                    <div class="deck-name">{{ deck_name }}</div>
                                     <div class="card-content">
                                        {{ card.front }}
                                    </div>
                                    {% if card.tags %}
                                    <div class="card-tags">
                                        {% for tag in card.tags %}
                                        <span class="card-tag">{{ tag }}</span>
                                        {% endfor %}
                                    </div>
                                    {% endif %}
                                </div>
                                <div class="card-back">
                                    <div class="card-content">
                                        {{ card.back }}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                <script>
                    // 页面加载完成后执行
                    document.addEventListener('DOMContentLoaded', function() {
                        // 获取DOM元素
                        const cards = document.querySelectorAll('.card');
                        
                        // 为所有卡片添加翻转功能
                        cards.forEach(card => {
                            card.addEventListener('click', function() {
                                this.classList.toggle('flipped');
                            });
                        });
                    });
                </script>
            </body>
            </html>'''
