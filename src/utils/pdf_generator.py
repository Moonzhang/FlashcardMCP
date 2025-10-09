"""
PDF生成器模块
使用Playwright进行HTML到PDF的转换
"""

import os
import asyncio
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from .json_validator import FlashcardData
from .markdown_parser import MarkdownParser


def get_template_path() -> str:
    """获取模板文件路径"""
    current_dir = Path(__file__).parent.parent
    template_dir = current_dir / "templates"
    return str(template_dir)


async def generate_flashcards_pdf_async(
    flashcard_data: dict,
    layout: str = "single"
) -> bytes:
    """
    异步生成闪卡PDF
    
    Args:
        flashcard_data: 闪卡数据字典
        layout: 布局类型 ('single' 或 'a4_8')
    
    Returns:
        PDF文件的字节数据
    
    Raises:
        ValueError: 当数据验证失败时
        RuntimeError: 当PDF生成失败时
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
        processed_card = {
            "front": markdown_parser.parse(card.front),
            "back": markdown_parser.parse(card.back)
        }
        processed_cards.append(processed_card)
    
    # 渲染HTML
    html_content = template.render(
        title=data.metadata.title if data.metadata else "闪卡集",
        cards=processed_cards,
        layout=layout,
        style=data.style.dict() if data.style else {}
    )
    
    # 使用Playwright生成PDF
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 设置页面内容
        await page.set_content(html_content, wait_until="networkidle")
        
        # 根据布局设置PDF选项
        pdf_options = {
            "format": "A4",
            "print_background": True,
            "margin": {
                "top": "20px",
                "bottom": "20px", 
                "left": "20px",
                "right": "20px"
            }
        }
        
        if layout == "single":
            # 单页布局：每页一张卡片，竖版
            pdf_options["format"] = "A4"
            pdf_options["landscape"] = False
        elif layout == "a4_8":
            # 8卡片布局：A4页面8张卡片，横版
            pdf_options["format"] = "A4"
            pdf_options["landscape"] = True
        
        # 生成PDF
        pdf_bytes = await page.pdf(**pdf_options)
        
        await browser.close()
        
        if pdf_bytes is None:
            raise RuntimeError("PDF生成失败")
        
        return pdf_bytes


def generate_flashcards_pdf(
    flashcard_data: dict,
    layout: str = "single"
) -> bytes:
    """
    同步包装器：生成闪卡PDF
    
    Args:
        flashcard_data: 闪卡数据字典
        layout: 布局类型 ('single' 或 'a4_8')
    
    Returns:
        PDF文件的字节数据
    """
    return asyncio.run(generate_flashcards_pdf_async(flashcard_data, layout))


def save_pdf_to_file(pdf_bytes: bytes, output_path: str, filename: str) -> str:
    """将PDF字节数据保存到文件
    
    Args:
        pdf_bytes: PDF字节数据
        output_path: 输出目录路径
        filename: 文件名
    
    Returns:
        完整的文件路径
    """
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
    生成并保存PDF文件
    
    Args:
        flashcard_data: 闪卡数据字典
        output_path: 输出目录路径
        filename: 文件名
        layout: 布局类型 ('single' 或 'a4_8')
    
    Returns:
        保存的文件完整路径
    """
    # 确保输出目录存在
    os.makedirs(output_path, exist_ok=True)
    
    # 生成PDF
    pdf_bytes = generate_flashcards_pdf(flashcard_data, layout)
    
    # 保存文件
    full_path = os.path.join(output_path, filename)
    with open(full_path, 'wb') as f:
        f.write(pdf_bytes)
    
    return full_path