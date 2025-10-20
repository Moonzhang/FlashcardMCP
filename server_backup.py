#!/usr/bin/env python3
"""
Flashcard Generation MCP Server
Directly uses @mcp.tool decorators to define tools with natural language naming and LLM-friendly descriptions
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

# Import existing handler functions
from src.handlers.card_generator import generate_flashcards
from src.handlers.pdf_generator import generate_flashcards_pdf_async
from src.utils.csv_reader import convert_csv_to_json_data
from src.utils.json_validator import FlashcardData, validate_json_structure
from config import FLASHCARD_CONFIG

# Create MCP server instance
mcp = FastMCP(name="FlashcardGenerator")

@mcp.resource("resource://flashcard-templates")
def get_flashcard_templates() -> str:
    """
    Get available flashcard template list and their usage descriptions.
    
    This resource provides information about all available flashcard templates in the system,
    including template names, file paths, and detailed descriptions.
    Users can use this resource to understand the characteristics and applicable scenarios
    of each template to choose the most suitable one.
    
    Returns:
        JSON formatted string containing all available template information
    """
    try:
        # Get template configuration
        available_templates = FLASHCARD_CONFIG.get('available_templates', {})
        default_template = FLASHCARD_CONFIG.get('default_template', 'card_template.html')
        
        # Build template list - return concise array format
        template_list = []
        
        # Add detailed information for each template
        for template_name, template_config in available_templates.items():
            template_info = {
                "name": template_name,
                "file_path": template_config.get('file_path', f"{template_name}.html"),
                "description": template_config.get('description', f"{template_name} template"),
                "is_default": template_name == "default" or template_config.get('file_path') == default_template
            }
            
            # Add template feature descriptions
            if template_name == "default":
                template_info["features"] = [
                    "Complete flashcard functionality",
                    "Rich styling options", 
                    "Responsive design",
                    "Tag filtering support",
                    "Interactive card flipping"
                ]
                template_info["best_for"] = "Flashcard applications requiring full functionality"
            elif template_name == "minimal":
                template_info["features"] = [
                    "Minimalist design",
                    "Fast loading",
                    "Content-focused display",
                    "Print-friendly"
                ]
                template_info["best_for"] = "Simple learning cards or printing purposes"
            
            template_list.append(template_info)
        
        # Return complete structure with metadata
        result = {
            "templates": template_list,
            "default_template": default_template,
            "total_count": len(template_list),
            "usage_guide": {
                "description": "Choose appropriate template to generate flashcard pages",
                "how_to_use": "Use template parameter to specify template name when calling create_flashcards_from_json tool"
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_info = {
            "error": "Failed to get template list",
            "message": str(e),
            "templates": []
        }
        return json.dumps(error_info, ensure_ascii=False, indent=2)

# 用户意图识别Prompt
@mcp.prompt
def identify_user_intent(user_input: str, data_type: str = "unknown") -> str:
    """
    分析用户输入，识别用户意图并推荐合适的工具和参数。
    
    Args:
        user_input: 用户的原始输入内容
        data_type: 数据类型提示 (csv, json, file_path, unknown)
    
    Returns:
        包含意图分析和工具推荐的详细指导
    """
    return f"""作为智能闪卡助手，请分析以下用户输入并识别意图：

用户输入："{user_input}"
数据类型：{data_type}

请按以下步骤分析：

1. **意图识别**：
   - CSV转换：关键词包含"CSV"、"表格"、"转换"、"导入"、"数据文件"
   - HTML生成：关键词包含"HTML"、"网页"、"在线"、"交互"、"练习页面"、"听写"
   - PDF生成：关键词包含"PDF"、"打印"、"纸质"、"下载"、"离线"
   - 数据验证：关键词包含"验证"、"检查"、"格式"、"错误"、"结构"

2. **工具推荐**：
   - CSV数据 → convert_csv_to_json
   - JSON数据 → create_flashcards_from_json (先用validate_flashcard_data验证)
   - PDF需求 → generate_flashcards_pdf
   - 验证需求 → validate_flashcard_data

3. **参数建议**：
   - 模板选择：学习练习用"minimal"，完整功能用"default"
   - 主题选择：默认"light"，也可选择"dark"
   - PDF布局：批量学习用"a4_8"，单独展示用"single"

4. **最佳实践**：
   - CSV处理：确保UTF-8编码，正确设置列索引
   - 模板选择：根据使用场景选择合适模板
   - PDF生成：考虑打印需求选择布局

@mcp.prompt
def select_tool_capabilities(intent: str, data_format: str, output_requirements: str) -> str:
    """
    根据识别的用户意图选择合适的工具能力和参数配置
    
    Args:
        intent: 用户意图 (csv_conversion, html_generation, pdf_generation, validation)
        data_format: 数据格式 (csv, json, file_path)
        output_requirements: 输出要求 (interactive, printable, validation_only)
    
    Returns:
        详细的工具调用指导和参数配置建议
    """
    return f"""Based on user intent '{intent}', data format '{data_format}' and output requirements '{output_requirements}', here are the tool capability recommendations:

## Tool Selection Strategy

### Main Tool Chains:
1. **CSV Conversion Scenario** (intent: csv_conversion):
   - Main tool: convert_csv_to_json
   - Parameter configuration:
     * front_columns: "0" (first column as front)
     * back_columns: "1" (second column as back)
     * has_header: true (contains header row)
     * title: auto-generated based on content
   - Follow-up tools: Choose HTML or PDF generation based on output_requirements

2. **HTML Generation Scenario** (intent: html_generation):
   - Pre-validation: validate_flashcard_data (ensure data structure is correct)
   - Main tool: create_flashcards_from_json
   - Parameter configuration:
     * template: "minimal" (for learning) or "default" (full features)
     * theme: "light" (default) or "dark" (dark theme)
     * title: descriptive title
     * description: brief description

3. **PDF Generation Scenario** (intent: pdf_generation):
   - Pre-validation: validate_flashcard_data
   - Main tool: generate_flashcards_pdf
   - Parameter configuration:
     * layout: "a4_8" (batch learning) or "single" (individual display)
     * title: PDF document title
     * description: document description

4. **Data Validation Scenario** (intent: validation):
   - Main tool: validate_flashcard_data
   - Purpose: ensure JSON data structure meets flashcard format requirements

## Parameter Configuration Guidelines

**Template Selection Logic**:
- Learning and practice -> "minimal" template
- Full feature display -> "default" template
- Dictation practice -> "minimal" + "light" theme

**Layout Selection Logic**:
- Batch printing for learning -> "a4_8" layout
- Individual card display -> "single" layout
- Mobile device viewing -> "a4_8" layout

**Theme Selection Logic**:
- Daytime use -> "light" theme
- Nighttime use -> "dark" theme
- Print output -> "light" theme

## Recommended Tool Call Flow:
1. Data preprocessing (CSV to JSON conversion if needed)
2. Data validation (validate_flashcard_data)
3. Content generation (HTML or PDF)
4. Result confirmation and optimization suggestions

Please choose appropriate tool combinations and parameter configurations based on specific scenarios."""


# 最终输出工具选择Prompt
@mcp.prompt
def select_final_output_tool(user_goal: str, available_data: str, preferred_format: str) -> str:
    """
    根据用户最终目标选择合适的输出工具和格式。
    
    Args:
        user_goal: 用户的最终目标 (learning, teaching, printing, sharing, archiving)
        available_data: 可用数据状态 (csv_raw, json_validated, html_ready, pdf_ready)
        preferred_format: 用户偏好格式 (interactive_web, printable_pdf, structured_json, all_formats)
    
    Returns:
        最终输出工具选择和优化建议
    """
    return f"""基于用户目标"{user_goal}"、数据状态"{available_data}"和格式偏好"{preferred_format}"，提供最终输出工具选择建议：

## 输出工具决策矩阵

### 学习场景优化 (user_goal: learning):
**推荐工具**: create_flashcards_from_json
- **模板选择**: "minimal" - 专注学习内容，减少干扰
- **主题选择**: "light" - 适合长时间学习
- **交互功能**: 启用翻转动画和进度跟踪
- **适用场景**: 个人学习、复习备考、记忆训练

### 教学场景优化 (user_goal: teaching):
**推荐工具**: create_flashcards_from_json + generate_flashcards_pdf
- **HTML版本**: "default"模板 + "light"主题 - 课堂演示
- **PDF版本**: "single"布局 - 制作教学材料
- **双重输出**: 在线互动 + 离线材料
- **适用场景**: 课堂教学、培训材料、学生分发

### 打印场景优化 (user_goal: printing):
**推荐工具**: generate_flashcards_pdf
- **布局选择**: "a4_8" - 节省纸张，批量打印
- **格式优化**: 高对比度，清晰字体
- **打印设置**: 建议双面打印，便于携带
- **适用场景**: 便携学习卡、考试复习、离线学习

### 分享场景优化 (user_goal: sharing):
**推荐工具**: create_flashcards_from_json
- **模板选择**: "default" - 完整功能展示
- **主题选择**: "light" - 通用兼容性
- **响应式设计**: 适配各种设备屏幕
- **适用场景**: 在线分享、协作学习、远程教学

### 归档场景优化 (user_goal: archiving):
**推荐工具**: 保持JSON格式 + 生成PDF备份
- **JSON保存**: 结构化数据，便于后续处理
- **PDF备份**: "single"布局，长期保存
- **元数据完整**: 包含创建时间、版本信息
- **适用场景**: 长期存储、数据备份、版本管理

## 格式偏好匹配

### 交互式网页 (preferred_format: interactive_web):
- **主工具**: create_flashcards_from_json
- **增强功能**: 键盘快捷键、进度统计、学习模式
- **优化建议**: 启用所有交互功能

### 可打印PDF (preferred_format: printable_pdf):
- **主工具**: generate_flashcards_pdf
- **布局优化**: 根据内容量选择"single"或"a4_8"
- **打印友好**: 高对比度、清晰边框

### 结构化JSON (preferred_format: structured_json):
- **保持原始**: 验证后的JSON格式
- **用途**: 数据交换、程序处理、批量操作

### 全格式输出 (preferred_format: all_formats):
- **完整流程**: JSON → HTML → PDF
- **用途**: 满足不同使用场景的完整解决方案

## 最终建议

根据分析结果，建议的工具调用顺序：
1. 确保数据已通过validate_flashcard_data验证
2. 根据user_goal和preferred_format选择主要输出工具
3. 如需多格式，按优先级依次生成
4. 提供使用建议和优化提示

选择最适合用户需求的输出方案。"""

@mcp.tool
def create_flashcards_from_json(
    cards: List[Dict[str, Any]],
    title: str = "My Flashcard Set",
    description: str = "Flashcards generated using MCP tools",
    template: str = "minimal",
    theme: str = "light"
) -> str:
    """
    Create flashcard HTML page based on provided card data.
    
    This tool can convert structured card data into beautiful flashcard pages,
    supporting multiple templates and themes. Each card contains a front (question)
    and back (answer), with optional tags for categorization.
    
    Args:
        cards: List of cards, each card contains front, back and optional tags
        title: Title of the flashcard set
        description: Description of the flashcard set
        template: Template type, options: "minimal", "default" or "elegant"
        theme: Theme, options: "light" or "dark"
    
    Returns:
        Generated flashcard HTML content
    """
    try:
        # Build standard JSON data structure
        flashcard_data = {
            "metadata": {
                "title": title,
                "description": description
            },
            "style": {
                "template": template,
                "theme": theme
            },
            "cards": cards
        }
        
        # Generate flashcard HTML
        html_content = generate_flashcards(flashcard_data)
        return html_content
        
    except Exception as e:
        raise ValueError(f"Flashcard generation failed: {str(e)}")

@mcp.tool
async def generate_flashcards_pdf(
    cards: List[Dict[str, Any]],
    title: str = "My Flashcard Set",
    description: str = "PDF format flashcards",
    layout: str = "a4_8",
    output_path: str = "sample"
) -> str:
    """
    Export flashcard data as PDF file.
    
    This tool can convert flashcard data to PDF format for easy printing and sharing.
    Supports different layout options, allowing single card per page or multiple cards per page.
    
    Args:
        cards: List of cards, each card contains front, back and optional tags
        title: Title of the flashcard set
        description: Description of the flashcard set
        layout: Layout type, "single" means one card per page, "a4_8" means eight cards per A4 page
        output_path: Directory path to save the PDF file (default: "sample")
    
    Returns:
        Path to the generated PDF file
    """
    try:
        import os
        import re
        
        # Build standard JSON data structure
        flashcard_data = {
            "metadata": {
                "title": title,
                "description": description
            },
            "style": {
                "template": "minimal",
                "theme": "light"
            },
            "cards": cards
        }
        
        # Call async function directly
        pdf_bytes = await generate_flashcards_pdf_async(flashcard_data, layout)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Generate safe filename from title
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        if not safe_title:
            safe_title = "flashcards"
        
        # Create filename with layout info
        layout_suffix = "单页布局" if layout == "single" else "8卡片布局"
        filename = f"{safe_title}_{layout_suffix}.pdf"
        file_path = os.path.join(output_path, filename)
        
        # Save PDF file
        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return f"PDF文件已生成并保存到: {file_path} (大小: {len(pdf_bytes)} 字节)"
        
    except Exception as e:
        raise ValueError(f"PDF generation failed: {str(e)}")

@mcp.tool
def convert_csv_to_json(
    csv_content: str,
    front_columns: str = "0",
    back_columns: str = "1",
    tags_column: Optional[int] = None,
    has_header: bool = True,
    title: str = "CSV Imported Flashcards",
    description: str = "Flashcards converted from CSV data",
    column_separator: str = " ",
    template: str = "minimal",
    theme: str = "light"
) -> str:
    """
    Convert CSV data to complete flashcard JSON format that conforms to FlashcardData model.
    
    This tool can parse CSV format data and convert it to structured JSON data for flashcards. 
    The output includes complete metadata, style configuration, and card data that conforms to
    the FlashcardData Pydantic model. The JSON structure is automatically validated before return.
    
    Args:
        csv_content: Text content of the CSV file
        front_columns: Column indices for front content, multiple columns separated by commas (e.g., "0,1")
        back_columns: Column indices for back content, multiple columns separated by commas (e.g., "2,3")
        tags_column: Index of the tags column (optional)
        has_header: Whether CSV contains header row
        title: Title of the generated flashcard set
        description: Description of the flashcard set
        column_separator: Separator for multi-column content
        template: Template type for styling (minimal, default, elegant)
        theme: Theme for styling (light, dark)
    
    Returns:
        Complete JSON formatted string containing validated flashcard data structure
    """
    try:
        import tempfile
        import os
        from datetime import datetime
        from src.utils.json_validator import normalize_json_data, validate_json_structure
        
        # Save CSV content to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name
        
        try:
            # Parse column index strings to integer lists
            front_col_indices = [int(x.strip()) for x in front_columns.split(',')]
            back_col_indices = [int(x.strip()) for x in back_columns.split(',')]
            
            # Use existing CSV conversion function to get basic card data
            basic_data = convert_csv_to_json_data(
                file_path=temp_file_path,
                front_columns=front_col_indices,
                back_columns=back_col_indices,
                tags_column_index=tags_column,
                has_header=has_header,
                title=title,
                column_separator=column_separator
            )
            
            # Build complete FlashcardData structure
            complete_flashcard_data = {
                "cards": basic_data.get("cards", []),
                "metadata": {
                    "title": title,
                    "description": description,
                    "version": "1.0.0",
                    "created_at": datetime.now().isoformat()
                },
                "style": {
                    "template": template,
                    "theme": theme,
                    "colors": {},
                    "font": "Arial, sans-serif",
                    "card_front_font": "24px/1.2 Arial, sans-serif",
                    "card_back_font": "18px/1.2 Arial, sans-serif",
                    "card_width": "300px",
                    "card_height": "200px",
                    "card_front_background": "#ffffff" if theme == "light" else "#2d2d2d",
                    "card_back_background": "#f5f5f5" if theme == "light" else "#3d3d3d",
                    "card_front_text_align": "center",
                    "card_back_text_align": "center",
                    "card_border": "1px solid #dddddd" if theme == "light" else "1px solid #555555",
                    "card_border_radius": "8px",
                    "card_padding": "20px",
                    "card_box_shadow": "0 2px 4px rgba(0,0,0,0.1)"
                }
            }
            
            # Validate the structure using json_validator
            validation_result = validate_json_structure(complete_flashcard_data)
            if not validation_result.get('is_valid', False):
                raise ValueError(f"Generated JSON structure validation failed: {validation_result.get('error', 'Unknown error')}")
            
            # Normalize the data (add IDs, fill defaults)
            normalized_data = normalize_json_data(complete_flashcard_data)
            
            # Return complete JSON formatted string
            return json.dumps(normalized_data, ensure_ascii=False, indent=2)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
        
    except Exception as e:
        raise ValueError(f"CSV conversion failed: {str(e)}")

@mcp.tool
def validate_flashcard_data(flashcard_json: Dict[str, Any]) -> str:
    """
    Validate whether the flashcard data structure is correct.
    
    This tool can check if the flashcard JSON data conforms to the expected format,
    helping users ensure data structure correctness and avoid generation errors.
    
    Args:
        flashcard_json: Flashcard JSON data to validate
    
    Returns:
        Description of validation results
    """
    try:
        validation_result = validate_json_structure(flashcard_json)
        
        if isinstance(validation_result, dict):
            if validation_result.get('is_valid', False):
                return "✅ Flashcard data structure validation passed! Data format is correct and can be used to generate flashcards."
            else:
                error_msg = validation_result.get('error', 'Unknown error')
                return f"❌ Flashcard data structure validation failed: {error_msg}"
        else:
            return "✅ Flashcard data structure validation passed!"
            
    except Exception as e:
        return f"❌ Error occurred during validation: {str(e)}"

if __name__ == "__main__":
    # Run MCP server
    mcp.run(transport="http")
