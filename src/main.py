from fastapi import FastAPI, Request, UploadFile, File, Form, APIRouter
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
import os
import io
import json
import uvicorn
import traceback
import urllib.parse
import uuid
import logging
import sys
import re
from typing import Optional, List, cast
from starlette.types import ASGIApp
from src.handlers.card_generator import generate_flashcards
from src.handlers.pdf_generator import generate_flashcards_pdf_async
from src.utils.csv_reader import convert_csv_to_json_data
from src.utils.json_validator import FlashcardData  # 导入 FlashcardData 模型
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastmcp import FastMCP # 导入 FastMCP
from config import TEMPLATES_DIR, FLASHCARD_CONFIG, STATIC_DIR  # 导入模板目录配置、闪卡配置与静态目录

# 使用 config.py 中的模板目录配置
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# 创建 FastAPI 应用实例
app = FastAPI(title="FastAPI Card Generator", description="基于 FastAPI 的闪卡生成服务")

# 配置日志记录器，使用标准输出流确保在 uvicorn 下可见
logger = logging.getLogger("flashcard")
logger.setLevel(logging.INFO)
_stream = logging.StreamHandler(sys.stdout)
_stream.setLevel(logging.INFO)
_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
_stream.setFormatter(_formatter)
if not logger.handlers:
    logger.addHandler(_stream)
logger.propagate = False

# 创建 API 路由器，用于组织对外工具端点

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FlashCardMCP app started")
    yield
    logger.info("FlashCardMCP app shutdown")


app = FastAPI(lifespan=lifespan)

api_router = APIRouter(prefix="/api", tags=["api"])
"""
API router, used to organize external tool endpoints.
"""

# 将 API 路由器包含到主应用中
# app.include_router(api_router)  # moved to end

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"[http] {request.method} {request.url.path}{'?' + request.url.query if request.url.query else ''}")
    response = await call_next(request)
    return response

# 创建 FastMCP 应用实例并挂载到 FastAPI 应用
mcp_app = FastMCP.from_fastapi(app=app)
app.mount("/mcp", cast(ASGIApp, mcp_app))

# 挂载静态文件目录，提供 /static 资源访问
try:
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    logger.info(f"[startup] Mounted static directory: {STATIC_DIR}")
except Exception as e:
    logger.warning(f"[startup] Failed to mount static directory {STATIC_DIR}: {e}")

@app.get("/")
async def index(request: Request):
    """
    Home page route.
    Displays the welcome page of the application.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/preview")
async def preview(request: Request, dataset: str = "all", template: str = "minimal", theme_param: Optional[str] = None, show_title: bool = True, show_card_index: bool = True):
    """
    Preview flashcard page.
    Loads `tests/test_data.json`, merges datasets if needed, and renders HTML via `generate_flashcards` using the selected template.

    Args:
        dataset (str): Dataset name, currently only "all" is supported, meaning all datasets are merged.
        template (str): Template name to use for rendering (e.g., "minimal", "listen", "default"). Defaults to "minimal".

    Returns:
        HTMLResponse: Response containing the generated flashcard HTML content.
    """
    try:
        logger.info(f"[preview] dataset={dataset}, template={template}, theme_param={theme_param}, show_title={show_title}, show_card_index={show_card_index}")
        # 修复 __file__ 未定义的问题，使用当前工作目录
        project_root = os.path.abspath(os.path.join(os.getcwd()))
        sample_path = os.path.join(project_root, 'tests', 'test_data.json')
        logger.info(f"[preview] sample_path={sample_path}, exists={os.path.exists(sample_path)}")

        def _default_sample():
            """
            Generates a default flashcard sample data.
            Used when the `tests/test_data.json` file does not exist or cannot be loaded.

            Returns:
                dict: Dictionary containing default flashcard data.
            """
            return {
                "metadata": {"title": "Preview_dataset", "description": "preview dataset page show"},
                "style": {"template": template, "theme": theme_param or "light"},
                "cards": [
                    {"front": "Question/问题", "back": "Answer/答案", "tags": ["Preview"]}
                ]
            }

        def _build_preview_json(template_name):
            """
            Builds the JSON data required for preview flashcards.
            Loads data from `tests/test_data.json`, merges cards from all datasets, and formats them according to the specified template requirements.
            Returns default sample data if the file does not exist or is empty.

            Args:
                template_name (str): The template name to use for rendering.

            Returns:
                dict: Formatted flashcard JSON data.
            """
            if os.path.exists(sample_path):
                with open(sample_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                # 合并所有数据集的 cards
                merged_cards = []
                title_for_deck = "Preview Flashcard Set"
                description_for_deck = "tests/test_data.json Merged View"
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
                                if title_for_deck == "Preview Flashcard Set":
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
                # 合并样式：优先使用 test_data.json 中的 style，再覆盖模板与主题
                merged_style = {}
                if isinstance(loaded, dict):
                    if isinstance(loaded.get('style'), dict):
                        merged_style = dict(loaded['style'])
                    else:
                        for _, v in loaded.items():
                            if isinstance(v, dict) and isinstance(v.get('style'), dict):
                                merged_style = dict(v['style'])
                                break
                merged_style['template'] = template_name
                merged_style['theme'] = theme_param or merged_style.get('theme', 'light')
                # 新增：允许通过查询参数控制标题和序号显示，默认开启
                merged_style['show_title'] = merged_style.get('show_title', show_title)
                merged_style['show_card_index'] = merged_style.get('show_card_index', show_card_index)
                return {
                    "metadata": {
                        "title": title_for_deck,
                        "description": description_for_deck
                    },
                    "style": merged_style,
                    "cards": merged_cards if merged_cards else _default_sample()["cards"]
                }
            else:
                return _default_sample()

        def _rewrite_file_uri_to_static(cards):
            """将 file:// 路径规范化为 /static 以便浏览器加载。"""
            normalized = []
            for c in cards:
                if not isinstance(c, dict):
                    normalized.append(c)
                    continue
                new_c = dict(c)
                for side in ("front", "back"):
                    val = new_c.get(side)
                    if isinstance(val, str):
                        new_c[side] = re.sub(r"src=\"file://[^\"]*/static/", "src=\"/static/", val)
                        # 同时处理 Markdown 图片语法中的路径
                        new_c[side] = re.sub(r"\(file://[^\)]*/static/", "(/static/", new_c[side])
                normalized.append(new_c)
            return normalized

        sample_json = _build_preview_json(template)
        # 规范化图片路径，避免 file:// 在 http 环境下被浏览器阻止
        sample_json["cards"] = _rewrite_file_uri_to_static(sample_json.get("cards", []))

        logger.info(f"sample_json={json.dumps(sample_json, ensure_ascii=False, indent=2)}")
        logger.info(f"[preview] style={sample_json.get('style')}, cards={len(sample_json.get('cards', []))}")

        # 使用生成器根据 JSON 渲染为完整 HTML
        html_content = generate_flashcards(sample_json)
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.exception("Preview generation failed")
        return HTMLResponse(status_code=500, content=f"<p>Preview generation failed: {e}</p>")

@app.get("/preview_pdf")
async def preview_pdf(layout: str = 'a4_8', show_title: bool = True, show_card_index: bool = True, show_page_number: bool = True):
    """
    Exports the merged data from the preview page directly to a PDF and returns it as a download stream.

    Args:
        layout (str): Controls the printing layout of the PDF. Possible values are 'single' or 'a4_8' (default).

    Returns:
        StreamingResponse: Response containing the generated PDF file, available for download.
        HTMLResponse: Returns an error message if PDF generation fails.
    """
    try:
        # 修复 __file__ 未定义的问题，使用当前工作目录
        project_root = os.path.abspath(os.path.join(os.getcwd()))
        sample_path = os.path.join(project_root, 'tests', 'test_data.json')

        def _default_sample():
            """
            Generates a default flashcard sample data.
            Used when the `tests/test_data.json` file does not exist or cannot be loaded.

            Returns:
                dict: Dictionary containing default flashcard data.
            """
            return {
                "metadata": {"title": "Preview Flashcard Set", "description": "Sample data generated flashcard page"},
                "style": {"template": "default", "theme": "light"},
                "cards": [{"front": "Question", "back": "Answer", "tags": ["Example"]}]
            }

        def _build_preview_json():
            """
            Builds the JSON data required for preview flashcards.
            Loads data from `tests/test_data.json`, merges cards from all datasets, and formats them according to the minimal template requirements.
            Returns default sample data if the file does not exist or is empty.

            Returns:
                dict: Formatted flashcard JSON data.
            """
            if os.path.exists(sample_path):
                with open(sample_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                merged_cards = []
                title_for_deck = "Preview Flashcard Set"
                description_for_deck = "tests/test_data.json Merged View"
                if isinstance(loaded, dict) and 'cards' in loaded:
                    merged_cards.extend(loaded.get('cards', []))
                    meta = loaded.get('metadata', {})
                    title_for_deck = meta.get('title', title_for_deck)
                    description_for_deck = meta.get('description', description_for_deck)
                elif isinstance(loaded, dict):
                    for key, v in loaded.items():
                        if isinstance(v, dict):
                            if isinstance(v.get('metadata'), dict) and v['metadata'].get('title'):
                                if title_for_deck == "Preview Flashcard Set":
                                    title_for_deck = v['metadata'].get('title')
                            cards = v.get('cards')
                            if isinstance(cards, list):
                                for c in cards:
                                    if isinstance(c, dict):
                                        tags = c.get('tags', [])
                                        if key not in tags:
                                            c['tags'] = tags + [key]
                                        merged_cards.append(c)
                # 合并样式：优先使用 test_data.json 中的 style
                merged_style = {}
                if isinstance(loaded, dict):
                    if isinstance(loaded.get('style'), dict):
                        merged_style = dict(loaded['style'])
                    else:
                        for _, v in loaded.items():
                            if isinstance(v, dict) and isinstance(v.get('style'), dict):
                                merged_style = dict(v['style'])
                                break
                # 保持 PDF 模板自身的布局需求，不强制覆盖 template
                if 'template' not in merged_style:
                    merged_style['template'] = 'minimal'
                if 'theme' not in merged_style:
                    merged_style['theme'] = 'light'
                # 新增：允许通过查询参数控制标题、序号与页码显示，默认开启
                merged_style['show_title'] = merged_style.get('show_title', show_title)
                merged_style['show_card_index'] = merged_style.get('show_card_index', show_card_index)
                merged_style['show_page_number'] = merged_style.get('show_page_number', show_page_number)
                return {
                    "metadata": {"title": title_for_deck, "description": description_for_deck},
                    "style": merged_style,
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
        logger.exception("Preview PDF generation failed")
        return HTMLResponse(status_code=500, content=f"<p>Preview PDF generation failed: {e}</p>")



@api_router.post("/convert_to_flashcards")
async def convert_to_flashcards(flashcard_data: FlashcardData):
    """
    Receives JSON data and returns the generated flashcard HTML.

    Args:
        flashcard_data (FlashcardData): Pydantic model containing flashcard data.
    """
    try:
        # 将 Pydantic 模型转换为字典，并包含所有字段
        json_data = flashcard_data.model_dump(exclude_unset=False)
        
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
    Receives flashcard JSON, generates a PDF according to the layout, and returns a download stream.

    Args:
        request (Request): FastAPI Request object, containing flashcard JSON data.

    Returns:
        StreamingResponse: Response containing the generated PDF file, available for download.
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
    """
    Receives a CSV file and converts it into flashcard format.
    
    Args:
    - file: Uploaded CSV file.
    - front_columns: Columns for the front content (comma-separated column indices, e.g., "0" or "0,1", default "0").
    - back_columns: Columns for the back content (comma-separated column indices, e.g., "1,2", default "1").
    - tags_column: Column for tags (optional, 0-indexed).
    - has_header: Whether the CSV file has a header row (default True).
    - title: Title of the flashcard set (optional, defaults to filename).
    - column_separator: Separator for merging multiple column contents (default space).
    - output_format: Output format (json/html/pdf, default html).

    Returns:
        JSONResponse | StreamingResponse: Returns flashcard data in JSON format, HTML content, or a PDF file stream based on `output_format`.
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
        
        return JSONResponse(status_code=500, content={
            'success': False,
            'error': 'UNKNOWN_ERROR',
            'message': '未知错误，请稍后重试'
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            'success': False,
            'error': 'INTERNAL_SERVER_ERROR',
            'message': f'服务器内部错误: {str(e)}'
        })


app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)