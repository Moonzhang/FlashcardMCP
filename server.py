#!/usr/bin/env python3
"""
FlashCard Generator MCP Server

This server provides tools for generating flashcards from various data sources,
including CSV files, JSON data, and creating HTML/PDF outputs.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

# Import handlers and utilities
from src.handlers.card_generator import generate_flashcards
from src.handlers.pdf_generator import generate_flashcards_pdf_async
from src.utils.csv_reader import convert_csv_to_json_data
from src.utils.json_validator import FlashcardData, validate_json_structure
from config import FLASHCARD_CONFIG

# Initialize FastMCP server
mcp = FastMCP(name="FlashcardGenerator")

@mcp.resource("resource://flashcard-templates")
def get_flashcard_templates() -> str:
    """
    Get available flashcard templates and their configurations.
    
    Returns:
        JSON string containing template information
    """
    try:
        # 从配置中动态获取模板信息
        templates = {
            name: {
                "name": name.capitalize(),
                "description": details.get("description", f"{name.capitalize()} template"),
            }
            for name, details in FLASHCARD_CONFIG.get('available_templates', {}).items()
        }
        
        # PDF布局目前是固定的，将来可以考虑也加入配置
        layouts = {
            "single": {
                "name": "Single Card Layout",
                "description": "One flashcard per page for detailed view",
                "page_size": "A4",
                "cards_per_page": 1,
                "best_for": ["Teaching materials", "Large text content", "Detailed explanations"]
            },
            "a4_8": {
                "name": "A4 Eight Cards Layout", 
                "description": "Eight flashcards per A4 page for efficient printing",
                "page_size": "A4",
                "cards_per_page": 8,
                "best_for": ["Bulk printing", "Study cards", "Portable learning"]
            }
        }
        
        # 从配置中动态获取主题信息
        themes = FLASHCARD_CONFIG.get('available_themes', [])

        return json.dumps({
            "templates": templates,
            "layouts": layouts,
            "supported_formats": ["HTML", "PDF"],
            "themes": themes
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to load template information: {str(e)}",
            "templates": {},
            "layouts": {}
        }, ensure_ascii=False, indent=2)

# Comprehensive Flashcard Assistant Prompt
@mcp.prompt
def flashcard_assistant(
    user_input: str, 
    context: str = "general", 
    data_type: str = "unknown",
    output_preference: str = "auto"
) -> str:
    """
    Comprehensive flashcard generation assistant with resource querying, intent recognition, and tool recommendation capabilities.
    
    Args:
        user_input: User's input text describing their flashcard needs
        context: Context information (general, learning, teaching, sharing, printing)
        data_type: Type of input data (csv, json)
        output_preference: Preferred output format (html, pdf, auto)
    
    Returns:
        Complete analysis and recommendations for flashcard generation
    """
    # 从配置动态生成模板和布局的帮助信息
    templates_info = "\n".join(
        [f"- **{name}**: {details.get('description', 'No description available.')}" for name, details in FLASHCARD_CONFIG.get('available_templates', {}).items()]
    )
    
    # 布局信息保持静态
    layouts_info = """- **single**: One flashcard per page for detailed view
  - Best for: Teaching materials, large text content, detailed explanations
  
- **a4_8**: Eight flashcards per A4 page for efficient printing
  - Best for: Bulk printing, study cards, portable learning"""

    # 从配置动态生成主题的帮助信息
    themes_info = ", ".join(FLASHCARD_CONFIG.get('available_themes', []))

    return f"""# Flashcard Generation Assistant

## User Request Analysis
**Input**: "{user_input}"
**Context**: {context}
**Data Type**: {data_type}
**Output Preference**: {output_preference}

## Available Resources Query

### Templates Available:
{templates_info}

### PDF Layouts Available:
{layouts_info}

### Themes Available:
- {themes_info}

## Intent Recognition & Analysis

### Primary Intent Detection:
1. **CSV Data Processing**: Keywords like "CSV", "table", "convert", "import", "spreadsheet"
   → Recommended Tool: `convert_csv_to_json`

2. **Interactive Web Flashcards**: Keywords like "HTML", "web", "online", "interactive", "practice"
   → Recommended Tool: `create_flashcards_from_json`

3. **Printable PDF Generation**: Keywords like "PDF", "print", "paper", "download", "offline"
   → Recommended Tool: `generate_flashcards_pdf`

4. **Data Validation**: Keywords like "validate", "check", "format", "error", "structure"
   → Recommended Tool: `validate_flashcard_data`

## Tool Selection Strategy

### Workflow Recommendations:

1. **CSV Input Workflow**:
   ```
   Step 1: convert_csv_to_json (process raw CSV data)
   Step 2: validate_flashcard_data (ensure data integrity)
   Step 3: create_flashcards_from_json OR generate_flashcards_pdf
   ```

2. **JSON Input Workflow**:
   ```
   Step 1: validate_flashcard_data (verify structure)
   Step 2: create_flashcards_from_json OR generate_flashcards_pdf
   ```

## Parameter Configuration Guide

### Template Selection Logic:
- **Learning/Practice** → "minimal", "listen"
- **Teaching/Presentation** → "default"

### Theme Selection Logic:
- **Daytime Use** → "light", "basic"
- **Evening Study** → "dark"
- **Print Output** → "light" (better contrast)

### Layout Selection Logic:
- **Individual Study** → "single"
- **Batch Learning** → "a4_8"
- **Teaching Materials** → "single"

## Markdown Content Guidelines

When creating flashcard content using Markdown, please pay attention to the following to ensure correct rendering, especially in PDFs:

- **Escape Characters**: Special characters in Markdown (like `*`, `_`, `[`, `]`, `(`, `)`) should be escaped with a backslash (`\`) if you want them to appear as literal characters. For example, to display `*literal*`, you should write `\*literal\*`.
- **Mathematical Formulas**: For mathematical formulas using LaTeX, ensure you are using the correct syntax that your rendering engine supports. For example, for block-level formulas, use `$$...$$`, and for inline formulas, use `$...$`. Make sure backslashes in LaTeX commands are properly escaped if necessary (e.g., `\frac` might need to be `\\frac` depending on the context).

---

**Next Steps**: Based on this analysis, please proceed with the recommended tool calls using the suggested parameters.
"""

@mcp.tool
def create_flashcards_from_json(
    cards: List[Dict[str, Any]],
    title: str = "My Flashcard Set",
    description: str = "Flashcards generated using MCP tools",
    template: str = "minimal",
    theme: str = "light"
) -> str:
    """
    Create interactive HTML flashcards from JSON card data.
    
    Args:
        cards: List of flashcard data with 'front', 'back', and optional 'tags'
        title: Title for the flashcard set
        description: Description of the flashcard set
        template: Template type ('minimal', 'default', 'elegant')
        theme: Theme ('light' or 'dark')
    
    Returns:
        HTML content as string
    """
    try:
        # Prepare flashcard data structure
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
        
        # Generate HTML content
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
    output_path: str = "",
    show_deck_name: bool = False,
    show_card_index: bool = False
) -> str:
    """
    Generate PDF flashcards from JSON card data.
    
    Args:
        cards: List of flashcard data with 'front', 'back', and optional 'tags'
        title: Title for the flashcard set
        description: Description of the flashcard set
        layout: Layout type ('single' or 'a4_8')
        output_path: Directory path to save the PDF file
        show_deck_name: Whether to show the title on the PDF
        show_card_index: Whether to show the card index on the PDF
    
    Returns:
        Success message with file path and size information
    """
    try:
        import os
        import re
        
        # Prepare flashcard data structure
        flashcard_data = {
            "metadata": {
                "title": title,
                "description": description
            },
            "style": {
                "template": "minimal",
                "theme": "light",
                "show_deck_name": show_deck_name,
                "show_card_index": show_card_index,
            },
            "cards": cards
        }
        
        # Generate PDF content
        pdf_bytes = await generate_flashcards_pdf_async(flashcard_data, layout)
        
        # Determine output directory (default to config.OUTPUT_DIR)
        try:
            from config import OUTPUT_DIR as DEFAULT_OUTPUT_DIR
        except Exception:
            DEFAULT_OUTPUT_DIR = "test_output"
        output_path = output_path or DEFAULT_OUTPUT_DIR
        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)
        
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        if not safe_title:
            safe_title = "flashcards"
        
        # Add layout suffix for clarity
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
    Convert CSV content to flashcard JSON format.
    
    Args:
        csv_content: Raw CSV content as string
        front_columns: Comma-separated column indices for card front (e.g., "0,1")
        back_columns: Comma-separated column indices for card back (e.g., "2,3")
        tags_column: Column index for tags (optional)
        has_header: Whether CSV has header row
        title: Title for the flashcard set
        description: Description of the flashcard set
        column_separator: Separator for multi-column content
        template: Template type for styling
        theme: Theme for styling
    
    Returns:
        JSON string of complete flashcard data
    """
    try:
        import tempfile
        import os
        from datetime import datetime
        from src.utils.json_validator import normalize_json_data, validate_json_structure
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name

        try:
            # Parse column indices
            front_col_indices = [int(x.strip()) for x in front_columns.split(',')]
            back_col_indices = [int(x.strip()) for x in back_columns.split(',')]
            
            # Convert CSV to basic JSON structure
            basic_data = convert_csv_to_json_data(
                file_path=temp_file_path,
                front_columns=front_col_indices,
                back_columns=back_col_indices,
                tags_column_index=tags_column,
                has_header=has_header,
                title=title,
                column_separator=column_separator
            )
            
            # Create complete flashcard data structure
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
            
            # Validate the generated structure
            validation_result = validate_json_structure(complete_flashcard_data)
            if not validation_result.get('is_valid', False):
                raise ValueError(f"Generated JSON structure validation failed: {validation_result.get('error', 'Unknown error')}")
            
            # Normalize the data
            normalized_data = normalize_json_data(complete_flashcard_data)
            
            # Return JSON string
            return json.dumps(normalized_data, ensure_ascii=False, indent=2)

        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    except Exception as e:
        raise ValueError(f"CSV conversion failed: {str(e)}")

@mcp.tool
def validate_flashcard_data(flashcard_json: Dict[str, Any]) -> str:
    """
    Validate flashcard JSON data structure.
    
    Args:
        flashcard_json: Flashcard data in JSON format
    
    Returns:
        Validation result message
    """
    try:
        # Perform validation
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
    # Run the MCP server
    mcp.run()