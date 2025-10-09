from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
import os
import io
import json
import uvicorn
from handlers.card_generator import generate_flashcards
from utils.pdf_generator import generate_flashcards_pdf

# 创建 FastAPI 应用实例
app = FastAPI(title="FastAPI Card Generator", description="基于 FastAPI 的闪卡生成服务")

@app.post("/convert_to_flashcards")
async def convert_to_flashcards(request: Request):
    """接收 JSON 数据并返回生成的闪卡 HTML"""
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

@app.get("/")
async def index():
    """简单的首页介绍"""
    html = '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FastAPI Card Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
            code { font-family: monospace; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>FastAPI Card Generator API</h1>
        <p>使用 POST 请求调用 <code>/convert_to_flashcards</code> 接口生成闪卡。</p>
        <p>请求示例：</p>
        <pre><code>curl -X POST -H "Content-Type: application/json" -d '{\n  "cards": [\n    {\n      "front": "问题 1",\n      "back": "答案 1"\n    },\n    {\n      "front": "问题 2",\n      "back": "答案 2"\n    }\n  ]\n}' http://localhost:5000/convert_to_flashcards</code></pre>
        <p>预览页面：<a href="/preview">/preview</a></p>
        <p>预览页导出 PDF：
            <a href="/preview_pdf?layout=a4_8">/preview_pdf?layout=a4_8</a>
            ，或单卡每页：
            <a href="/preview_pdf?layout=single">/preview_pdf?layout=single</a>
        </p>
    </body>
    </html>
    '''
    return HTMLResponse(content=html)

@app.get("/preview")
async def preview(dataset: str = "all"):
    """预览：将 tests/test_data.json 中所有数据集合并为一个卡片集，并使用极简模板
    - 合并所有数据集的 `cards` 到一个数组
    - 仅展示卡片，无搜索、标题区及其他控件
    - 卡片左上角显示集合标题，正面白色，背面浅灰色
    """
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        sample_path = os.path.join(project_root, 'tests', 'test_data.json')

        def _default_sample():
            return {
                "metadata": {"title": "预览闪卡集", "description": "示例数据生成的闪卡页面"},
                "style": {"template": "default", "theme": "light"},
                "cards": [
                    {"front": "问题", "back": "答案", "tags": ["示例"]}
                ]
            }

        def _build_preview_json():
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
                        "font": "Arial, sans-serif"
                    },
                    "cards": merged_cards if merged_cards else _default_sample()["cards"]
                }
            else:
                return _default_sample()

        sample_json = _build_preview_json()

        html_content = generate_flashcards(sample_json)
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(status_code=500, content=f"<p>预览生成失败: {e}</p>")

@app.get("/preview_pdf")
async def preview_pdf(layout: str = 'a4_8'):
    """将预览页的合并数据直接导出为 PDF 并返回下载流。

    支持参数：
    - layout: 'single' 或 'a4_8'（默认），控制打印布局
    """
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        sample_path = os.path.join(project_root, 'tests', 'test_data.json')

        def _default_sample():
            return {
                "metadata": {"title": "预览闪卡集", "description": "示例数据生成的闪卡页面"},
                "style": {"template": "default", "theme": "light"},
                "cards": [{"front": "问题", "back": "答案", "tags": ["示例"]}]
            }

        def _build_preview_json():
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
        pdf_bytes = generate_flashcards_pdf(sample_json, layout=layout)
        filename = sample_json.get('metadata', {}).get('title', 'preview') + '.pdf'
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        # 提供友好提示，通常是 wkhtmltopdf 未安装或不可用
        return HTMLResponse(status_code=500, content=f"<p>预览 PDF 生成失败: {e}</p><p>请确认已安装系统依赖 wkhtmltopdf，并在 PATH 或设置环境变量 WKHTMLTOPDF_BINARY。</p>")

@app.post("/export_pdf")
async def export_pdf(request: Request):
    """接收闪卡 JSON，按布局生成 PDF 并返回下载流。

    支持参数：
    - layout: 'single' 或 'a4_8'（默认），控制打印布局
    """
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"error": "请求体必须是有效的 JSON"}, status_code=400)

    try:
        layout = payload.get('layout', 'a4_8')
        pdf_bytes = generate_flashcards_pdf(payload, layout=layout)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    filename = payload.get('metadata', {}).get('title', 'flashcards') + '.pdf'
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )


if __name__ == "__main__":
    print("启动 FastAPI 闪卡生成服务...")
    print("访问 http://localhost:5000 查看首页")
    print("访问 http://localhost:5000/preview 预览闪卡页面")
    print("使用 POST 请求调用 /convert_to_flashcards 接口来生成闪卡")
    uvicorn.run(app, host="0.0.0.0", port=5000)