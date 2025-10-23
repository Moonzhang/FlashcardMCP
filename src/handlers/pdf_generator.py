"""
PDF生成器模块
使用Playwright进行HTML到PDF的转换
"""

import os
import asyncio
import base64
import mimetypes
import re
import urllib.parse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from src.utils.json_validator import FlashcardData
from src.utils.markdown_parser import MarkdownParser
from config import FLASHCARD_CONFIG  # 新增：引入默认样式配置


def get_template_path() -> str:
    """
    获取用于渲染闪卡 PDF 的 HTML 模板文件路径。

    Retrieves the file path for HTML templates used to render flashcard PDFs.

    Returns:
        str: 模板目录的绝对路径。
             Absolute path to the templates directory.
    """
    current_dir = Path(__file__).parent.parent
    template_dir = current_dir / "templates"
    return str(template_dir)


def _to_data_uri(path: str) -> str:
    """将本地文件转为 data URI（支持 png/jpg/webp/svg 等）。"""
    if path.startswith("file://"):
        parsed = urllib.parse.urlparse(path)
        path = parsed.path
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        # 默认按二进制处理
        mime = "application/octet-stream"
    with open(path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def inline_images_in_html(html: str) -> str:
    """将 HTML 中本地或静态路径图片内联为 data URI，避免 PDF 环境加载失败。"""
    root = Path(__file__).resolve().parent.parent.parent  # 项目根
    static_dir = root / "static"

    def _resolve_local_path(src: str) -> str:
        # 已是 data/http(s) 则跳过
        if src.startswith("data:") or src.startswith("http://") or src.startswith("https://"):
            return ""
        # file:// 形式
        if src.startswith("file://"):
            return urllib.parse.urlparse(src).path
        # /static/ 开头
        if src.startswith("/static/"):
            return str(static_dir / src[len("/static/"):])
        # 绝对路径
        if os.path.isabs(src):
            return src
        # 相对路径：按项目根尝试
        return str(root / src)

    pattern = r"<img\s[^>]*src=\"([^\"]+)\""

    def _repl(m: re.Match) -> str:
        src = m.group(1)
        path = _resolve_local_path(src)
        if path and os.path.exists(path):
            try:
                data_uri = _to_data_uri(path)
                return m.group(0).replace(src, data_uri)
            except Exception:
                return m.group(0)  # 失败则保持原样
        return m.group(0)

    return re.sub(pattern, _repl, html)


async def generate_flashcards_pdf_async(
    flashcard_data: dict,
    layout: str = "a4_8"
 ) -> bytes:
    """
    异步生成闪卡 PDF 文件。

    Asynchronously generates a flashcard PDF file.

    Args:
        flashcard_data (dict): 包含闪卡数据、元数据和样式配置的字典。
                               Dictionary containing flashcard data, metadata, and style configurations.
        layout (str): PDF 布局类型，可以是 'single'（单张卡片一页）或 'a4_8'（A4 页面八张卡片）。默认为 "a4_8"。
                      PDF layout type, can be 'single' (one card per page) or 'a4_8' (eight cards per A4 page). Defaults to "a4_8".

    Returns:
        bytes: 生成的 PDF 文件的字节数据。
               Byte data of the generated PDF file.

    Raises:
        ValueError: 当输入数据验证失败时抛出。
                    Raised when input data validation fails.
        RuntimeError: 当 PDF 生成过程失败时抛出。
                      Raised when the PDF generation process fails.
    """
    # 验证和规范化数据
    try:
        data = FlashcardData(**flashcard_data)
    except Exception as e:
        raise ValueError(f"数据验证失败: {e}")
    
    # 设置模板环境
    template_dir = get_template_path()
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("playwright_card_template.html")
    
    # 初始化Markdown解析器
    markdown_parser = MarkdownParser()
    
    # 处理卡片内容，将Markdown转换为HTML
    processed_cards = []
    for card in data.cards:
        front_html = markdown_parser.parse(card.front)
        back_html = markdown_parser.parse(card.back)
        # 内联本地/静态图片，避免 PDF 环境加载失败
        front_html = inline_images_in_html(front_html)
        back_html = inline_images_in_html(back_html)
        processed_card = {"front": front_html, "back": back_html}
        processed_cards.append(processed_card)
    
    # 如果是A4八卡片布局，补齐空白卡片以满足每页8张的要求
    if layout == "a4_8":
        cards_per_page = 8
        total_cards = len(processed_cards)
        
        # 计算需要补齐的空白卡片数量
        if total_cards % cards_per_page != 0:
            blank_cards_needed = cards_per_page - (total_cards % cards_per_page)
            
            # 添加空白卡片
            for _ in range(blank_cards_needed):
                processed_cards.append({"front": "", "back": ""})

    # ------------------------
    # 对齐样式上下文到 minimal.html
    # ------------------------
    # 统一默认样式与传入样式
    default_style = FLASHCARD_CONFIG.get('default_style', {})
    style_params = data.style.model_dump() if data.style else {}

    # 新增：将关键样式键回退到默认值，保证模板中的 style.* 可用
    if 'colors' not in style_params:
        style_params['colors'] = {}
    style_params.setdefault('show_title', default_style.get('show_title', False))
    style_params.setdefault('show_page_number', default_style.get('show_page_number', True))
    style_params.setdefault('deck_name_style', default_style.get('deck_name_style', ''))
    style_params.setdefault('card_index_style', default_style.get('card_index_style', ''))
    style_params.setdefault('page_number_style', default_style.get('page_number_style', ''))
    # 让 style.layout 与函数入参保持一致（HTML 预览忽略该键，PDF 使用）
    style_params.setdefault('layout', layout)

    # 主题与颜色
    theme = style_params.get('theme', default_style.get('theme', 'light'))
    theme_class = (
        f"theme-{theme}" if theme in ['basic', 'advance', 'detail'] else (
            "theme-dark" if theme == 'dark' else 'theme-light'
        )
    )

    # 默认主题颜色集合
    theme_style_key = f"{theme}_theme_style"
    theme_config = FLASHCARD_CONFIG.get(theme_style_key, FLASHCARD_CONFIG.get('default_style', {}))
    default_colors = theme_config.get('colors', FLASHCARD_CONFIG.get('default_style', {}).get('colors', {})).copy()
    user_colors = style_params.get('colors', {}) or {}
    for key, val in user_colors.items():
        if isinstance(val, str) and not val.startswith('#'):
            val = f"#{val}"
        default_colors[key] = val

    # 尺寸与边距、边框
    card_width = style_params.get('card_width', default_style.get('card_width'))
    card_height = style_params.get('card_height', default_style.get('card_height'))
    card_border = style_params.get('card_border') or default_colors.get('card_border')
    card_border_radius = style_params.get('card_border_radius', '8px')
    card_padding = style_params.get('card_padding', '20px')
    card_box_shadow = style_params.get('card_box_shadow', '0 2px 4px rgba(0,0,0,0.1)')

    # 文本对齐
    card_front_text_align = style_params.get('card_front_text_align', 'center')
    card_back_text_align = style_params.get('card_back_text_align', 'left')

    # 字体
    font_css = style_params.get('font', default_style.get('font', 'Arial, sans-serif'))
    card_front_font = style_params.get('card_front_font')
    card_back_font = style_params.get('card_back_font')

    # 显示控制与字数限制
    compact_typography = bool(style_params.get('compact_typography', default_style.get('compact_typography', True)))
    show_deck_name = bool(style_params.get('show_title', default_style.get('show_title', False)))
    show_card_index = bool(style_params.get('show_card_index', default_style.get('show_card_index', False)))
    show_tags = bool(style_params.get('show_tags', default_style.get('show_tags', True)))
    deck_name_style = style_params.get('deck_name_style', '')
    card_index_style = style_params.get('card_index_style', '')
    front_char_limit = style_params.get('front_char_limit') if style_params.get('front_char_limit') is not None else default_style.get('front_char_limit')
    back_char_limit = style_params.get('back_char_limit') if style_params.get('back_char_limit') is not None else default_style.get('back_char_limit')

    # 构建与 minimal.html 一致的上下文
    title_str = data.metadata.title if data.metadata else "闪卡集"
    context = {
        'title': title_str,
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
        'total_cards': str(len(processed_cards)),
        'primary_color': default_colors.get('primary'),
        'secondary_color': default_colors.get('secondary'),
        'background_color': default_colors.get('background'),
        'text_color': default_colors.get('text'),
        'card_bg': default_colors.get('card_bg'),
        'card_front_bg': default_colors.get('card_front_bg', default_colors.get('card_bg')),
        'card_back_bg': default_colors.get('card_back_bg', default_colors.get('card_bg')),
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
        'description_section': "",
        'filter_section': "",
        'cards': processed_cards,
        'cards_html': "",
        'deck_name': title_str,
        # PDF 模板专用
        'layout': layout,
        'style': style_params
    }
    
    # 渲染HTML（继承 minimal.html，因此会复用相同的变量与样式）
    html_content = template.render(**context)
    
    # 使用Playwright生成PDF
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 设置页面内容
        await page.set_content(html_content, wait_until="domcontentloaded")

        # 等待外部资源：MathJax、图片与字体
        try:
            # 等待MathJax加载并完成排版（若存在）
            await page.wait_for_function("() => window.MathJax && MathJax.typesetPromise", timeout=10000)
            await page.evaluate("async () => { if (window.MathJax && MathJax.typesetPromise) { await MathJax.typesetPromise(); } }")
        except Exception:
            pass

        # 等待所有图片加载完成
        try:
            await page.evaluate('''
                async () => {
                    const images = Array.from(document.images);
                    await Promise.all(images.map(img => {
                        if (img.decode) return img.decode().catch(() => {});
                        if (img.complete) return Promise.resolve();
                        return new Promise(res => { img.onload = () => res(); img.onerror = () => res(); });
                    }));
                    if (document.fonts && document.fonts.ready) {
                        await document.fonts.ready;
                    }
                }
            ''')
        except Exception:
            pass

        # 注入JavaScript以动态调整字体大小（同时支持 single 与 a4_8 结构）
        await page.evaluate('''
            async () => {
                const sides = document.querySelectorAll(".card .card-front, .card .card-back, .card .card-side");
                for (const side of sides) {
                    const content = side.querySelector(".card-content");
                    if (!content) continue;
                    let fontSize = parseFloat(getComputedStyle(content).fontSize);
                    const available = side.clientHeight - 2; // 微调容错
                    while (content.scrollHeight > available && fontSize > 8) {
                        fontSize -= 0.5;
                        content.style.fontSize = `${fontSize}px`;
                        await new Promise(r => requestAnimationFrame(r));
                    }
                }
            }
        ''')
        
        # 根据布局设置PDF选项
        pdf_options = {
            "format": "A4",
            "print_background": True,
            "margin": {"top": "0", "bottom": "0", "left": "0", "right": "0"}
        }
        
        if layout == "single":
            # 单页布局：每页一张卡片，竖版
            pdf_options["landscape"] = False
        elif layout == "a4_8":
            # 8卡片布局：A4页面8张卡片，横版，与模板CSS一致
            pdf_options["landscape"] = True
        
        # 生成PDF
        pdf_bytes = await page.pdf(**pdf_options)
        
        await browser.close()
        
        if pdf_bytes is None:
            raise RuntimeError("PDF生成失败")
        
        return pdf_bytes


def generate_flashcards_pdf(
    flashcard_data: dict,
    layout: str = "a4_8"
 ) -> bytes:
    """
    同步包装器，用于生成闪卡 PDF 文件。
    此函数是 `generate_flashcards_pdf_async` 的同步版本，通过 `asyncio.run` 执行异步逻辑。

    Synchronous wrapper for generating flashcard PDF files.
    This function is a synchronous version of `generate_flashcards_pdf_async`, executing asynchronous logic via `asyncio.run`.

    Args:
        flashcard_data (dict): 包含闪卡数据、元数据和样式配置的字典。
                               Dictionary containing flashcard data, metadata, and style configurations.
        layout (str): PDF 布局类型，可以是 'single'（单张卡片一页）或 'a4_8'（A4 页面八张卡片）。默认为 "a4_8"。
                      PDF layout type, can be 'single' (one card per page) or 'a4_8' (eight cards per A4 page). Defaults to "a4_8".

    Returns:
        bytes: 生成的 PDF 文件的字节数据。
               Byte data of the generated PDF file.
    """
    return asyncio.run(generate_flashcards_pdf_async(flashcard_data, layout))


def save_pdf_to_file(pdf_bytes: bytes, output_path: str, filename: str) -> str:
    """
    将 PDF 字节数据保存到指定文件路径。

    Saves PDF byte data to the specified file path.

    Args:
        pdf_bytes (bytes): 要保存的 PDF 文件的字节数据。
                           Byte data of the PDF file to be saved.
        output_path (str): PDF 文件保存的目录路径。如果目录不存在，将自动创建。
                           Directory path where the PDF file will be saved. The directory will be created if it does not exist.
        filename (str): 要保存的 PDF 文件的名称（例如 "flashcards.pdf"）。
                        Name of the PDF file to be saved (e.g., "flashcards.pdf").

    Returns:
        str: 保存的 PDF 文件的完整绝对路径。
             The full absolute path to the saved PDF file.
    """
    # 统一输出目录：若未提供则使用配置默认值
    if not output_path:
        try:
            from config import OUTPUT_DIR as DEFAULT_OUTPUT_DIR
        except Exception:
            DEFAULT_OUTPUT_DIR = "test_output"
        output_path = DEFAULT_OUTPUT_DIR
    # 确保输出目录存在
    os.makedirs(output_path, exist_ok=True)
    
    # 构建完整文件路径
    full_path = os.path.join(output_path, filename)
    
    # 写入文件
    with open(full_path, 'wb') as f:
        f.write(pdf_bytes)
    
    return full_path


def generate_and_save_pdf(
    flashcard_data: dict,
    output_path: str,
    filename: str,
    layout: str = "single"
 ) -> str:
    """
    生成闪卡 PDF 文件并将其保存到指定路径。
    此函数结合了 PDF 生成和文件保存的步骤。

    Generates a flashcard PDF file and saves it to the specified path.
    This function combines the PDF generation and file saving steps.

    Args:
        flashcard_data (dict): 包含闪卡数据、元数据和样式配置的字典。
                               Dictionary containing flashcard data, metadata, and style configurations.
        output_path (str): PDF 文件保存的目录路径。如果目录不存在，将自动创建。
                           Directory path where the PDF file will be saved. The directory will be created if it does not exist.
        filename (str): 要保存的 PDF 文件的名称（例如 "flashcards.pdf"）。
                        Name of the PDF file to be saved (e.g., "flashcards.pdf").
        layout (str): PDF 布局类型，可以是 'single'（单张卡片一页）或 'a4_8'（A4 页面八张卡片）。默认为 "single"。
                      PDF layout type, can be 'single' (one card per page) or 'a4_8' (eight cards per A4 page). Defaults to "single".

    Returns:
        str: 保存的 PDF 文件的完整绝对路径。
             The full absolute path to the saved PDF file.
    """
    # 统一输出目录：若未提供则使用配置默认值
    if not output_path:
        try:
            from config import OUTPUT_DIR as DEFAULT_OUTPUT_DIR
        except Exception:
            DEFAULT_OUTPUT_DIR = "test_output"
        output_path = DEFAULT_OUTPUT_DIR
    # 确保输出目录存在
    os.makedirs(output_path, exist_ok=True)
    
    # 生成PDF
    pdf_bytes = generate_flashcards_pdf(flashcard_data, layout)
    
    # 保存文件
    full_path = os.path.join(output_path, filename)
    with open(full_path, 'wb') as f:
        f.write(pdf_bytes)
    
    return full_path