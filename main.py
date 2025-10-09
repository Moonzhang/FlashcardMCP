import os
import sys
import base64
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入fastmcp的服务
from fastmcp import FastMCP

# 导入闪卡生成和验证功能
from src.handlers.card_generator import generate_flashcards
from src.utils.pdf_generator import generate_flashcards_pdf
from src.utils.json_validator import validate_json_structure, normalize_json_data

# 创建 FastMCP 服务器实例
mcp = FastMCP("闪卡生成MCP服务器")

@mcp.tool()
def generate_flashcard(flashcard_data: dict) -> Dict[str, Any]:
    """根据JSON数据生成闪卡HTML页面
    
    Args:
        flashcard_data: 闪卡数据的JSON对象，包含metadata、style和cards字段
        
    Returns:
        包含生成结果的字典，包括success状态、html_content和message
    """
    try:
        # 生成闪卡HTML
        html_content = generate_flashcards(flashcard_data)
        
        # 返回成功响应
        return {
            "success": True,
            "html_content": html_content,
            "message": "闪卡生成成功"
        }
    except Exception as e:
        # 处理错误
        return {
            "success": False,
            "error": str(e),
            "message": "闪卡生成失败"
        }

@mcp.tool()
def validate_flashcard_data(flashcard_data: dict) -> Dict[str, Any]:
    """验证闪卡数据的有效性
    
    Args:
        flashcard_data: 需要验证的闪卡数据
        
    Returns:
        包含验证结果的字典，包括success状态、normalized_data和message
    """
    try:
        # 验证数据结构
        validate_json_structure(flashcard_data)
        
        # 规范化数据
        normalized_data = normalize_json_data(flashcard_data)
        
        # 返回成功响应
        return {
            "success": True,
            "normalized_data": normalized_data,
            "message": "闪卡数据验证成功",
            "card_count": len(normalized_data.get("cards", []))
        }
    except ValueError as e:
        # 处理验证错误
        return {
            "success": False,
            "error": str(e),
            "message": "闪卡数据验证失败"
        }

@mcp.tool()
def list_flashcard_templates() -> Dict[str, Any]:
    """列出可用的闪卡模板
    
    Returns:
        包含可用模板列表的字典
    """
    try:
        # 导入配置
        from config import FLASHCARD_CONFIG
        
        # 从配置中获取可用模板
        available_templates = FLASHCARD_CONFIG.get('available_templates', {})
        
        # 转换为所需格式的模板列表
        templates = []
        for template_name, template_info in available_templates.items():
            templates.append({
                "name": template_name,
                "description": template_info.get('description', f"{template_name}模板"),
                "file_path": template_info.get('file_path', '')
            })
        
        # 返回模板列表
        return {
            "success": True,
            "templates": templates,
            "message": "模板列表获取成功"
        }
    except Exception as e:
        # 处理错误
        return {
            "success": False,
            "error": str(e),
            "message": "模板列表获取失败"
        }

@mcp.tool()
def export_flashcards_pdf(flashcard_data: dict, layout: str = "a4_8", filename: str = "flashcards.pdf") -> Dict[str, Any]:
    """根据现有闪卡数据导出正反两面的PDF
    
    Args:
        flashcard_data: 闪卡数据的JSON对象（与生成HTML所用结构一致）
        layout: 打印布局，'single' 单张/页 或 'a4_8' 每页八张
        filename: 导出的PDF文件名
        
    Returns:
        包含PDF导出结果的字典
    """
    try:
        # 验证并规范化数据
        validate_json_structure(flashcard_data)
        normalized_data = normalize_json_data(flashcard_data)

        # 生成PDF字节流（基于 html→pdf，支持布局）
        pdf_bytes = generate_flashcards_pdf(normalized_data, layout=layout)

        # 编码为base64便于通过MCP传输
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return {
            "success": True,
            "pdf_base64": pdf_b64,
            "filename": filename,
            "message": "PDF导出成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "PDF导出失败"
        }

# 导入配置
from config import SERVER_CONFIG

# 运行服务器
if __name__ == "__main__":
    print("闪卡生成MCP服务器已启动")
    print("可用工具:")
    print("- generate_flashcard: 根据JSON数据生成闪卡HTML页面")
    print("- validate_flashcard_data: 验证闪卡数据的有效性")
    print("- list_flashcard_templates: 列出可用的闪卡模板")
    print("- export_flashcards_pdf: 导出闪卡为PDF格式")
    
    # 使用 FastMCP 的标准运行方式
    mcp.run()

# 示例用法
def create_sample_flashcards():
    """创建示例闪卡数据"""
    sample_data = {
        "metadata": {
            "title": "Python编程基础",
            "description": "Python编程语言的基础概念闪卡"
        },
        "style": {
            "template": "default",
            "theme": "light",
            "colors": {
                "primary": "#3776ab",
                "secondary": "#6c757d"
            },
            "font": "Arial, sans-serif"
        },
        "cards": [
            {
                "front": "什么是Python?",
                "back": "Python是一种高级、解释型、通用型编程语言，以其简洁的语法和强大的生态系统而闻名。",
                "tags": ["编程", "Python", "基础"]
            },
            {
                "front": "Python的主要特点是什么?",
                "back": "\n".join([
                    "- 简单易学的语法",
                    "- 解释执行，无需编译",
                    "- 面向对象编程",
                    "- 丰富的标准库",
                    "- 广泛的第三方库支持"
                ]),
                "tags": ["编程", "Python", "特性"]
            },
            {
                "front": "Python中的数据类型有哪些?",
                "back": "\n".join([
                    "**基本类型:**",
                    "- 整数 (int)",
                    "- 浮点数 (float)",
                    "- 字符串 (str)",
                    "- 布尔值 (bool)",
                    "",
                    "**复合类型:**",
                    "- 列表 (list)",
                    "- 元组 (tuple)",
                    "- 字典 (dict)",
                    "- 集合 (set)"
                ]),
                "tags": ["编程", "Python", "数据类型"]
            },
            {
                "front": "如何在Python中定义函数?",
                "back": "使用`def`关键字定义函数：\n\n```python\ndef my_function(parameter1, parameter2):\n    # 函数体\n    return result\n```\n\n调用函数：`my_function(value1, value2)`",
                "tags": ["编程", "Python", "函数"]
            },
            {
                "front": "Python中的异常处理如何实现?",
                "back": "使用`try-except`语句进行异常处理：\n\n```python\ntry:\n    # 可能引发异常的代码\nexcept ExceptionType as e:\n    # 异常处理代码\nfinally:\n    # 无论是否发生异常都会执行的代码\n```",
                "tags": ["编程", "Python", "异常处理"]
            }
        ]
    }
    
    return sample_data