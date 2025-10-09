from utils.json_validator import validate_json_structure, normalize_json_data
from utils.markdown_parser import MarkdownParser
import os
from config import FLASHCARD_CONFIG
try:
    from jinja2 import Template
    HAS_JINJA = True
except Exception:
    Template = None
    HAS_JINJA = False

# 设置模板目录
_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

def generate_flashcards(json_data):
    """根据 JSON 数据生成闪卡 HTML 页面"""
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
    title = metadata.get('title', '最小化测试闪卡集')
    description = metadata.get('description', '')
    
    # 提取样式配置
    style_config = normalized_data.get('style', {})
    template = style_config.get('template', 'default')
    theme = style_config.get('theme', 'light')
    colors = style_config.get('colors', {})
    font = style_config.get('font', 'Arial, sans-serif')
    
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
        theme=theme,
        colors=colors,
        font=font,
        template=template
    )
    
    return html_content


def render_flashcard_template(title, description, cards, theme, colors, font, template='default'):
    """渲染闪卡模板生成 HTML 内容"""
    try:
        # 从配置中获取可用模板
        available_templates = FLASHCARD_CONFIG.get('available_templates', {})
        
        # 获取指定模板的信息
        template_info = available_templates.get(template, {})
        template_file = template_info.get('file_path', '')

        # 如果配置了模板文件路径，优先尝试解析
        candidate_path = ''
        if template_file:
            # 支持相对路径：相对模板目录
            candidate_path = template_file if os.path.isabs(template_file) else os.path.join(_template_dir, template_file)
            if os.path.exists(candidate_path):
                with open(candidate_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            else:
                # 回退：尝试根据模板名称在模板目录查找
                template_path = os.path.join(_template_dir, f'{template}.html')
                if os.path.exists(template_path):
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                else:
                    # 如果模板文件不存在，使用内联模板
                    template_content = get_inline_template()
        else:
            # 未配置具体文件路径，则根据模板名称查找
            template_path = os.path.join(_template_dir, f'{template}.html')
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            else:
                template_content = get_inline_template()
    except Exception as e:
        print(f"警告: 加载模板文件失败: {str(e)}")
        # 使用内联模板
        template_content = get_inline_template()
    
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
    for card in cards:
        # 生成标签HTML
        tags_html = ''
        if card['tags']:
            tags_html = ''.join([f'<span class="card-tag">{tag}</span>' for tag in card['tags']])
            tags_html = f'<div class="card-tags">{tags_html}</div>'
        
        # 添加data-tags属性
        data_tags = ','.join(card['tags'])
        
        # 生成卡片HTML
        cards_html += f'''
        <div class="card" id="{card['id']}" data-tags="{data_tags}">
            <div class="card-inner">
                <div class="card-front">
                    <div class="deck-name">{title}</div>
                    <div class="card-content">
                        {card['front']}
                    </div>
                    {tags_html}
                </div>
                <div class="card-back">
                    <div class="card-content">
                        {card['back']}
                    </div>
                </div>
            </div>
        </div>
        '''
    
    # 选择渲染方式：优先使用Jinja2（当模板包含Jinja占位符或指定了jinja模板）
    use_jinja = HAS_JINJA and (template == 'jinja' or '{{' in template_content)
    context = {
        'title': title,
        'description': description,
        'font_family': font,
        'theme': theme,
        'total_cards': str(len(cards)),
        'primary_color': default_colors['primary'],
        'secondary_color': default_colors['secondary'],
        'background_color': default_colors['background'],
        'text_color': default_colors['text'],
        'card_bg': default_colors['card_bg'],
        'card_front_bg': default_colors['card_front_bg'],
        'card_back_bg': default_colors['card_back_bg'],
        'card_border': default_colors['card_border'],
        'description_section': description_section,
        'filter_section': filter_section,
        'cards_html': cards_html
    }
    
    if use_jinja and Template is not None:
        try:
            tmpl = Template(template_content)
            return tmpl.render(**context)
        except Exception as e:
            print(f"警告: Jinja渲染失败，回退到字符串替换: {str(e)}")
            # 继续使用字符串替换回退
    
    # 使用简单的字符串替换作为回退
    html_content = template_content
    html_content = html_content.replace('{title}', title)
    html_content = html_content.replace('{description}', description)
    html_content = html_content.replace('{font_family}', font)
    html_content = html_content.replace('{theme}', theme)
    html_content = html_content.replace('{total_cards}', str(len(cards)))
    html_content = html_content.replace('{primary_color}', default_colors['primary'])
    html_content = html_content.replace('{secondary_color}', default_colors['secondary'])
    html_content = html_content.replace('{background_color}', default_colors['background'])
    html_content = html_content.replace('{text_color}', default_colors['text'])
    html_content = html_content.replace('{card_bg}', default_colors['card_bg'])
    html_content = html_content.replace('{card_front_bg}', default_colors['card_front_bg'])
    html_content = html_content.replace('{card_back_bg}', default_colors['card_back_bg'])
    html_content = html_content.replace('{card_border}', default_colors['card_border'])
    html_content = html_content.replace('{description_section}', description_section)
    html_content = html_content.replace('{filter_section}', filter_section)
    html_content = html_content.replace('{cards_html}', cards_html)
    return html_content

def get_inline_template():
    """提供内联的模板内容，以防模板文件不存在"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <style>
        /* theme: {theme} */
        /* font: {font_family} */
        :root {
            --primary-color: {primary_color};
            --secondary-color: {secondary_color};
            --background-color: {background_color};
            --text-color: {text_color};
            --card-bg: {card_bg};
            --card-front-bg: {card_front_bg};
            --card-back-bg: {card_back_bg};
            --card-border: {card_border};
            --font-family: {font_family};
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
            width: 100%;
            height: 250px;
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
        }
        
        .card-back {
            transform: rotateY(180deg);
            background-color: var(--card-back-bg);
        }
        
        .card-content {
            max-height: 100%;
            overflow-y: auto;
            width: 100%;
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
</head>
<body>
    <div class="container">
        <!-- 极简模板的内联版本：仅保留卡片网格 -->
        <div class="flashcard-grid">
            {cards_html}
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


def test_flashcard_generation():
    """测试闪卡生成功能"""
    # 测试数据
    test_data = {
        "metadata": {
            "title": "测试闪卡集",
            "description": "这是一个测试用的闪卡集"
        },
        "style": {
            "template": "default",
            "theme": "light",
            "colors": {
                "primary": "#007bff",
                "secondary": "#6c757d"
            },
            "font": "Arial, sans-serif"
        },
        "cards": [
            {
                "front": "什么是Python?",
                "back": "Python是一种高级编程语言，以其简洁的语法和强大的生态系统而闻名。",
                "tags": ["编程", "Python"]
            },
            {
                "front": "什么是HTML?",
                "back": "HTML是用于创建网页的标记语言。",
                "tags": ["网页开发", "前端"]
            }
        ]
    }
    
    try:
        # 生成闪卡HTML
        html_content = generate_flashcards(test_data)
        
        # 检查HTML内容是否包含预期的元素
        if '测试闪卡集' in html_content and '什么是Python?' in html_content:
            print("闪卡生成成功！")
            print(f"生成的HTML内容长度: {len(html_content)} 字符")
        else:
            print("警告: 生成的HTML内容不包含预期的元素")
    except Exception as e:
        print(f"错误: 闪卡生成失败: {str(e)}")


if __name__ == "__main__":
    # 运行测试
    test_flashcard_generation()