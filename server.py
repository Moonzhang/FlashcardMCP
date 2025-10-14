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
    layout: str = "a4_8"
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
    
    Returns:
        Base64 encoded string of the PDF file
    """
    try:
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
        
        # Convert to base64 encoding
        import base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return f"PDF file generated, size: {len(pdf_bytes)} bytes. Base64 encoding: {pdf_base64[:100]}..."
        
    except Exception as e:
        raise ValueError(f"PDF generation failed: {str(e)}")

@mcp.tool
def convert_csv_to_flashcards(
    csv_content: str,
    front_columns: str = "0",
    back_columns: str = "1",
    tags_column: Optional[int] = None,
    has_header: bool = True,
    title: str = "CSV Imported Flashcards",
    column_separator: str = " "
) -> str:
    """
    Convert CSV data to flashcard HTML page.
    
    This tool can parse CSV format data and convert it to flashcards. Supports flexible
    column mapping configuration, allowing specification of which columns serve as
    card front, back, and tags.
    
    Args:
        csv_content: Text content of the CSV file
        front_columns: Column indices for front content, multiple columns separated by commas (e.g., "0,1")
        back_columns: Column indices for back content, multiple columns separated by commas (e.g., "2,3")
        tags_column: Index of the tags column (optional)
        has_header: Whether CSV contains header row
        title: Title of the generated flashcard set
        column_separator: Separator for multi-column content
    
    Returns:
        Generated flashcard HTML content
    """
    try:
        # Save CSV content to temporary file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(csv_content)
            temp_file_path = temp_file.name
        
        try:
            # Parse column index strings to integer lists
            front_col_indices = [int(x.strip()) for x in front_columns.split(',')]
            back_col_indices = [int(x.strip()) for x in back_columns.split(',')]
            
            # Use existing CSV conversion function
            flashcard_data = convert_csv_to_json_data(
                file_path=temp_file_path,
                front_columns=front_col_indices,
                back_columns=back_col_indices,
                tags_column_index=tags_column,
                has_header=has_header,
                title=title,
                column_separator=column_separator
            )
            
            # Generate flashcard HTML
            html_content = generate_flashcards(flashcard_data)
            return html_content
            
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
