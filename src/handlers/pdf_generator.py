"""
PDF生成器模块
使用Playwright进行HTML到PDF的转换
"""

import os
import asyncio
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from src.utils.json_validator import FlashcardData
from src.utils.markdown_parser import MarkdownParser


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
        processed_card = {
            "front": markdown_parser.parse(card.front),
            "back": markdown_parser.parse(card.back)
        }
        processed_cards.append(processed_card)
    
    # 如果是A4八卡片布局，补齐空白卡片以满足每页8张的要求
    if layout == "a4_8":
        cards_per_page = 8
        total_cards = len(processed_cards)
        
        # 计算需要补齐的空白卡片数量
        if total_cards % cards_per_page != 0:
            blank_cards_needed = cards_per_page - (total_cards % cards_per_page)
            
            # 添加空白卡片
            for i in range(blank_cards_needed):
                blank_card = {
                    "front": "",
                    "back": ""
                }
                processed_cards.append(blank_card)
    
    # 渲染HTML
    html_content = template.render(
        title=data.metadata.title if data.metadata else "闪卡集",
        cards=processed_cards,
        layout=layout,
        style=data.style.model_dump() if data.style else {}
    )
    
    # 使用Playwright生成PDF
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 设置页面内容
        await page.set_content(html_content, wait_until="networkidle")
        
        # 注入JavaScript以动态调整字体大小
        await page.evaluate('''
            async () => {
                const cards = document.querySelectorAll(".card-side");
                for (const card of cards) {
                    const content = card.querySelector(".card-content");
                    if (content) {
                        let fontSize = parseFloat(window.getComputedStyle(content).fontSize);
                        while (content.scrollHeight > card.clientHeight && fontSize > 8) {
                            fontSize -= 0.5;
                            content.style.fontSize = `${fontSize}px`;
                            // 等待DOM更新
                            await new Promise(resolve => requestAnimationFrame(resolve));
                        }
                    }
                }
            }
        ''')
        
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
            # 8卡片布局：A4页面8张卡片，竖版（与模板CSS匹配）
            pdf_options["format"] = "A4"
            pdf_options["landscape"] = False
        
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
    # 确保输出目录存在
    os.makedirs(output_path, exist_ok=True)
    
    # 生成PDF
    pdf_bytes = generate_flashcards_pdf(flashcard_data, layout)
    
    # 保存文件
    full_path = os.path.join(output_path, filename)
    with open(full_path, 'wb') as f:
        f.write(pdf_bytes)
    
    return full_path