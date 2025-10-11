from fastapi import FastAPI, Request, UploadFile, File, Form, APIRouter
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
import os
import io
import json
import uvicorn
import traceback
import urllib.parse
import uuid
from typing import Optional, List
from src.handlers.card_generator import generate_flashcards
from src.handlers.pdf_generator import generate_flashcards_pdf_async
from src.utils.csv_reader import convert_csv_to_json_data
from fastapi.templating import Jinja2Templates

# 传递基础模板
templates = Jinja2Templates(directory="src/templates")

# 创建 FastAPI 应用实例
app = FastAPI(title="FastAPI Card Generator", description="基于 FastAPI 的闪卡生成服务")

# 创建 API 路由器，用于组织对外工具端点
api_router = APIRouter(prefix="/api", tags=["api"])
"""
API 路由器，用于组织对外工具端点。
API router, used to organize external tool endpoints.
"""

@app.get("/")
async def index(request: Request):
    """
    首页路由。
    显示应用程序的欢迎页面。

    Home page route.
    Displays the welcome page of the application.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/preview")
async def preview(dataset: str = "all"):
    """
    预览闪卡页面。
    将 `tests/test_data.json` 中所有数据集合并为一个卡片集，并使用极简模板进行展示。
    卡片左上角显示集合标题，正面白色，背面浅灰色。

    Preview flashcard page.
    Merges all datasets from `tests/test_data.json` into a single card set and displays them using a minimal template.
    The collection title is shown in the top-left corner of the card, with white front and light gray back.

    Args:
        dataset (str): 数据集名称，目前仅支持 "all"，表示合并所有数据集。
                       Dataset name, currently only "all" is supported, meaning all datasets are merged.

    Returns:
        HTMLResponse: 包含生成的闪卡 HTML 内容的响应。
                      HTMLResponse: Response containing the generated flashcard HTML content.
    """
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        sample_path = os.path.join(project_root, 'tests', 'test_data.json')

        def _default_sample():
            """
            生成一个默认的闪卡样本数据。
            当 `tests/test_data.json` 文件不存在或无法加载时使用。

            Generates a default flashcard sample data.
            Used when the `tests/test_data.json` file does not exist or cannot be loaded.

            Returns:
                dict: 包含默认闪卡数据的字典。
                      dict: Dictionary containing default flashcard data.
            """
            return {
                "metadata": {"title": "预览闪卡集", "description": "示例数据生成的闪卡页面"},
                "style": {"template": "default", "theme": "light"},
                "cards": [
                    {"front": "问题", "back": "答案", "tags": ["示例"]}
                ]
            }

        def _build_preview_json():
            """
            构建预览闪卡所需的 JSON 数据。
            从 `tests/test_data.json` 加载数据，合并所有数据集的卡片，并根据极简模板要求进行格式化。
            如果文件不存在或为空，则返回默认样本数据。

            Builds the JSON data required for preview flashcards.
            Loads data from `tests/test_data.json`, merges cards from all datasets, and formats them according to the minimal template requirements.
            Returns default sample data if the file does not exist or is empty.

            Returns:
                dict: 格式化后的闪卡 JSON 数据。
                      dict: Formatted flashcard JSON data.
            """
            if os.path.exists(sample_path):
                with open(sample_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                # 合并所有数据集的 cards
                merged_cards = []
                title_for_deck = "预览闪卡集"
                description_for_deck = "tests/test_data.json 合并视图"
                # 如果顶层就是一个数据集
                if isinstance(loaded, dict) and 'cards' in loaded:
                    merged_cards.extend(loaded.get('cards', []))
                    meta = loaded.get('metadata', {})
                    title_for_deck = meta.get('title', title_for_deck)
                    description_for_deck = meta.get('description', description_for_deck)
                elif isinstance(loaded, dict):
                    for key, v in loaded.items():
                        if isinstance(v, dict):
                            # 收集标题（若存在）
                            if isinstance(v.get('metadata'), dict) and v['metadata'].get('title'):
                                # 选第一个作为集合名
                                if title_for_deck == "预览闪卡集":
                                    title_for_deck = v['metadata'].get('title')
                            # 合并卡片
                            cards = v.get('cards')
                            if isinstance(cards, list):
                                # 为每张卡添加 tags 标识来源数据集
                                for c in cards:
                                    if isinstance(c, dict):
                                        tags = c.get('tags', [])
                                        if key not in tags:
                                            c['tags'] = tags + [key]
                                        merged_cards.append(c)
                # 组装极简模板所需 json
                return {
                    "metadata": {
                        "title": title_for_deck,
                        "description": description_for_deck
                    },
                    "style": {
                        "template": "minimal",
                        "theme": "light",
                        "colors": {
                            "card_front_bg": "#ffffff",
                            "card_back_bg": "#f5f5f5"
                        },
                        "font": "Arial, sans-serif",
                        "card_width": "300px",
                        "card_height": "200px",
                        "card_front_image": "none",
                        "card_back_image": "none",
                        "card_front_text_align": "center",
                        "card_back_text_align": "center",
                        "font_size": "16px",
                        "front_font_size": "24px",
                        "back_font_size": "18px"
                    },
                    "cards": merged_cards if merged_cards else _default_sample()["cards"]
                }
            else:
                return _default_sample()

        sample_json = _build_preview_json()

        html_content = generate_flashcards(json_data=sample_json)

        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(status_code=500, content=f"<p>预览生成失败: {e}</p>")

@app.get("/preview_pdf")
async def preview_pdf(layout: str = 'a4_8'):
    """
    将预览页的合并数据直接导出为 PDF 并返回下载流。

    Exports the merged data from the preview page directly to a PDF and returns it as a download stream.

    Args:
        layout (str): 控制 PDF 的打印布局。可选值有 'single' 或 'a4_8'（默认）。
                      Controls the printing layout of the PDF. Possible values are 'single' or 'a4_8' (default).

    Returns:
        StreamingResponse: 包含生成的 PDF 文件的响应，可供下载。
                           StreamingResponse: Response containing the generated PDF file, available for download.
        HTMLResponse: 如果生成 PDF 失败，返回错误信息。
                      HTMLResponse: Returns an error message if PDF generation fails.
    """
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        sample_path = os.path.join(project_root, 'tests', 'test_data.json')

        def _default_sample():
            """
            生成一个默认的闪卡样本数据。
            当 `tests/test_data.json` 文件不存在或无法加载时使用。

            Generates a default flashcard sample data.
            Used when the `tests/test_data.json` file does not exist or cannot be loaded.

            Returns:
                dict: 包含默认闪卡数据的字典。
                      dict: Dictionary containing default flashcard data.
            """
            return {
                "metadata": {"title": "预览闪卡集", "description": "示例数据生成的闪卡页面"},
                "style": {"template": "default", "theme": "light"},
                "cards": [{"front": "问题", "back": "答案", "tags": ["示例"]}]
            }

        def _build_preview_json():
            """
            构建预览闪卡所需的 JSON 数据。
            从 `tests/test_data.json` 加载数据，合并所有数据集的卡片，并根据极简模板要求进行格式化。
            如果文件不存在或为空，则返回默认样本数据。

            Builds the JSON data required for preview flashcards.
            Loads data from `tests/test_data.json`, merges cards from all datasets, and formats them according to the minimal template requirements.
            Returns default sample data if the file does not exist or is empty.

            Returns:
                dict: 格式化后的闪卡 JSON 数据。
                      dict: Formatted flashcard JSON data.
            """
            if os.path.exists(sample_path):
                with open(sample_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                merged_cards = []
                title_for_deck = "预览闪卡集"
                description_for_deck = "tests/test_data.json 合并视图"
                if isinstance(loaded, dict) and 'cards' in loaded:
                    merged_cards.extend(loaded.get('cards', []))
                    meta = loaded.get('metadata', {})
                    title_for_deck = meta.get('title', title_for_deck)
                    description_for_deck = meta.get('description', description_for_deck)
                elif isinstance(loaded, dict):
                    for key, v in loaded.items():
                        if isinstance(v, dict):
                            if isinstance(v.get('metadata'), dict) and v['metadata'].get('title'):
                                if title_for_deck == "预览闪卡集":
                                    title_for_deck = v['metadata'].get('title')
                            cards = v.get('cards')
                            if isinstance(cards, list):
                                for c in cards:
                                    if isinstance(c, dict):
                                        tags = c.get('tags', [])
                                        if key not in tags:
                                            c['tags'] = tags + [key]
                                        merged_cards.append(c)
                return {
                    "metadata": {"title": title_for_deck, "description": description_for_deck},
                    "style": {
                        "template": "minimal",
                        "theme": "light",
                        "colors": {"card_front_bg": "#ffffff", "card_back_bg": "#f5f5f5"},
                        "font": "Arial, sans-serif"
                    },
                    "cards": merged_cards if merged_cards else _default_sample()["cards"]
                }
            else:
                return _default_sample()

        sample_json = _build_preview_json()
        pdf_bytes = await generate_flashcards_pdf_async(sample_json, layout=layout)
        unique_id = uuid.uuid4().hex[:8]  # 生成一个8位的随机字符串
        filename = f"{sample_json.get('metadata', {}).get('title', 'preview')}_{unique_id}.pdf"
        encoded_filename = urllib.parse.quote(filename)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type='application/pdf',
            headers={'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except Exception as e:
        # 打印完整的异常堆栈信息
        traceback.print_exc()
        # 提供友好提示
        return HTMLResponse(status_code=500, content=f"<p>预览 PDF 生成失败: {e}</p>")



@api_router.post("/convert_to_flashcards")
async def convert_to_flashcards(request: Request):
    """
    接收 JSON 数据并返回生成的闪卡 HTML。

    Receives JSON data and returns the generated flashcard HTML.

    Args:
        request (Request): FastAPI 请求对象，包含 JSON 格式的闪卡数据。
                           FastAPI Request object, containing flashcard data in JSON format.

    Returns:
        JSONResponse: 包含生成的 HTML 内容或错误信息的 JSON 响应。
                      JSONResponse: JSON response containing the generated HTML content or an error message.
    """
    try:
        json_data = await request.json()
        if not json_data:
            return JSONResponse(status_code=400, content={
                'success': False,
                'error': 'CONVERSION_ERROR',
                'message': '请求中未包含 JSON 数据'
            })

        html_content = generate_flashcards(json_data)
        return JSONResponse(content={
            'success': True,
            'result': {'html': html_content}
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            'success': False,
            'error': 'CONVERSION_ERROR',
            'message': f'闪卡转换失败: {str(e)}'
        })



@api_router.post("/export_pdf")
async def export_pdf(request: Request):
    """
    接收闪卡 JSON，按布局生成 PDF 并返回下载流。

    Receives flashcard JSON, generates a PDF according to the layout, and returns a download stream.

    Args:
        request (Request): FastAPI 请求对象，包含闪卡 JSON 数据。
                           FastAPI Request object, containing flashcard JSON data.

    Returns:
        StreamingResponse: 包含生成的 PDF 文件的响应，可供下载。
                           StreamingResponse: Response containing the generated PDF file, available for download.
        JSONResponse: 如果生成 PDF 失败，返回错误信息。
                      JSONResponse: Returns an error message if PDF generation fails.
    """
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"error": "请求体必须是有效的 JSON"}, status_code=400)

    try:
        layout = payload.get('layout', 'a4_8')
        pdf_bytes = await generate_flashcards_pdf_async(payload, layout=layout)
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{payload.get('metadata', {}).get('title', 'flashcards')}_{unique_id}.pdf"
        encoded_filename = urllib.parse.quote(filename)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type='application/pdf',
            headers={'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@api_router.post("/upload_csv")
async def upload_csv(
    file: UploadFile = File(...),
    front_columns: str = Form("0"),
    back_columns: str = Form("1,2"),
    tags_column: Optional[int] = Form(None),
    has_header: bool = Form(True),
    title: Optional[str] = Form(None),
    column_separator: str = Form(" "),
    output_format: str = Form("html")
 ):
    """接收CSV文件并转换为闪卡格式。
    Receives a CSV file and converts it into flashcard format.
    
    参数：
    Args:
    - file: 上传的CSV文件
            Uploaded CSV file.
    - front_columns: 正面内容所在列（逗号分隔的列索引，如"0"或"0,1"，默认"0"）
                     Columns for the front content (comma-separated column indices, e.g., "0" or "0,1", default "0").
    - back_columns: 背面内容所在列（逗号分隔的列索引，如"1,2"，默认"1"）
                    Columns for the back content (comma-separated column indices, e.g., "1,2", default "1").
    - tags_column: 标签所在列（可选，从0开始）
                   Column for tags (optional, 0-indexed).
    - has_header: 是否包含标题行（默认True）
                  Whether the CSV file has a header row (default True).
    - title: 闪卡集标题（可选，默认使用文件名）
             Title of the flashcard set (optional, defaults to filename).
    - column_separator: 多列内容合并时的分隔符（默认为空格）
                        Separator for merging multiple column contents (default space).
    - output_format: 输出格式（json/html/pdf，默认html）
                     Output format (json/html/pdf, default html).

    返回：
    Returns:
        JSONResponse | StreamingResponse: 根据 `output_format` 返回 JSON 格式的闪卡数据、HTML 内容或 PDF 文件流。
                                          Returns flashcard data in JSON format, HTML content, or a PDF file stream based on `output_format`.
    """
    try:
        # 验证输出格式
        if output_format not in ["json", "html", "pdf"]:
            return JSONResponse(status_code=400, content={
                'success': False,
                'error': 'INVALID_OUTPUT_FORMAT',
                'message': '输出格式必须是json、html或pdf之一'
            })
        
        # 验证文件类型
        if not file.filename or not file.filename.endswith('.csv'):
            return JSONResponse(status_code=400, content={
                'success': False,
                'error': 'INVALID_FILE_TYPE',
                'message': '只支持CSV文件格式'
            })
        
        # 解析列索引字符串为列表
        try:
            front_column_list = [int(x.strip()) for x in front_columns.split(',') if x.strip()]
            back_column_list = [int(x.strip()) for x in back_columns.split(',') if x.strip()]
        except ValueError:
            return JSONResponse(status_code=400, content={
                'success': False,
                'error': 'INVALID_COLUMN_INDEX',
                'message': '列索引必须是有效的数字，用逗号分隔'
            })
        
        # 读取文件内容并保存到临时文件
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # 创建临时文件
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        # 使用文件名作为默认标题
        if not title:
            title = file.filename.replace('.csv', '')
        
        try:
            # 转换CSV为JSON格式
            json_data = convert_csv_to_json_data(
                file_path=temp_file_path,
                title=title,
                front_columns=front_column_list,
                back_columns=back_column_list,
                tags_column_index=tags_column,
                has_header=has_header,
                column_separator=column_separator
            )
            
            # 根据输出格式返回不同的结果
            if output_format == "json":
                return JSONResponse(content={
                    'success': True,
                    'result': json_data
                })
            elif output_format == "html":
                html_content = generate_flashcards(json_data)
                return JSONResponse(content={
                    'success': True,
                    'result': {'html': html_content}
                })
            elif output_format == "pdf":
                pdf_bytes = await generate_flashcards_pdf_async(json_data, layout='a4_8')
                unique_id = uuid.uuid4().hex[:8]
                filename = f"{title}_{unique_id}.pdf"
                encoded_filename = urllib.parse.quote(filename)
                return StreamingResponse(
                    io.BytesIO(pdf_bytes),
                    media_type='application/pdf',
                    headers={'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}"}
                )
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
    except Exception as e:
        return JSONResponse(status_code=500, content={
            'success': False,
            'error': 'CSV_CONVERSION_ERROR',
            'message': f'CSV转换失败: {str(e)}'
        })


# 将 API 路由器包含到主应用中
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)