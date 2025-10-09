import os
import sys
import base64
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入我们的闪卡生成和验证功能
from src.handlers.card_generator import generate_flashcards
from src.utils.pdf_generator import generate_flashcards_pdf
from src.utils.json_validator import validate_json_structure, normalize_json_data

# 尝试导入fastmcp模块
try:
    import fastmcp
    from fastmcp import MCPServer, MCPTool
    from fastmcp.models import MCPRequest, MCPResponse
    HAS_FASTMCP = True
except ImportError:
    print("警告: 未找到fastmcp模块。请运行 'pip install -r requirements.txt' 安装所需依赖。")
    
    # 创建模拟类以便代码可以继续运行
    class MCPRequest:
        def __init__(self, params=None):
            self.params = params or {}
    
    class MCPResponse:
        def __init__(self, data=None):
            self.data = data or {}
    
    class MCPTool:
        def __init__(self, name, description, input_schema):
            self.name = name
            self.description = description
            self.input_schema = input_schema
        
        def handle(self, func):
            return func
    
    class MCPServer:
        def __init__(self):
            self.tools = {}
        
        def register_tool(self, tool):
            self.tools[tool.name] = tool
        
        def get_registered_tools(self):
            return self.tools.keys()
        
        def run(self, host='127.0.0.1', port=8000, debug=True):
            print(f"模拟运行服务器在 {host}:{port}")
            print("请注意：由于缺少fastmcp模块，服务器不会真正启动。")
    
    HAS_FASTMCP = False

class FlashcardMCPServer(MCPServer):
    """闪卡生成MCP服务器"""
    
    def __init__(self):
        """初始化MCP服务器"""
        super().__init__()
        
        # 注册工具
        self.register_tool(generate_flashcard_tool)
        self.register_tool(validate_flashcard_data_tool)
        self.register_tool(list_flashcard_templates_tool)
        self.register_tool(export_flashcards_pdf_tool)
    
    def on_start(self):
        """服务器启动时执行"""
        print("闪卡生成MCP服务器已启动")
        print("可用工具:")
        for tool_name in self.get_registered_tools():
            print(f"- {tool_name}")

# 创建工具实例
generate_flashcard_tool = MCPTool(
    name="generate_flashcard",
    description="根据JSON数据生成闪卡HTML页面",
    input_schema={
        "type": "object",
        "properties": {
            "flashcard_data": {
                "type": "object",
                "description": "闪卡数据的JSON对象",
                "properties": {
                    "metadata": {
                        "type": "object",
                        "description": "闪卡集的元数据",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"}
                        }
                    },
                    "style": {
                        "type": "object",
                        "description": "闪卡的样式配置",
                        "properties": {
                            "template": {"type": "string", "default": "default"},
                            "theme": {"type": "string"},
                            "colors": {"type": "object"},
                            "font": {"type": "string"}
                        }
                    },
                    "cards": {
                        "type": "array",
                        "description": "闪卡列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "front": {"type": "string"},
                                "back": {"type": "string"},
                                "tags": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["front", "back"]
                        }
                    }
                },
                "required": ["cards"]
            }
        },
        "required": ["flashcard_data"]
    }
)

validate_flashcard_data_tool = MCPTool(
    name="validate_flashcard_data",
    description="验证闪卡数据的有效性",
    input_schema={
        "type": "object",
        "properties": {
            "flashcard_data": {
                "type": "object",
                "description": "需要验证的闪卡数据"
            }
        },
        "required": ["flashcard_data"]
    }
)

list_flashcard_templates_tool = MCPTool(
    name="list_flashcard_templates",
    description="列出可用的闪卡模板",
    input_schema={"type": "object"}
)

# 导出 PDF 的工具定义
export_flashcards_pdf_tool = MCPTool(
    name="export_flashcards_pdf",
    description="根据现有闪卡数据导出正反两面的PDF",
    input_schema={
        "type": "object",
        "properties": {
            "flashcard_data": {
                "type": "object",
                "description": "闪卡数据的JSON对象（与生成HTML所用结构一致）"
            },
            "layout": {
                "type": "string",
                "description": "打印布局：'single' 单张/页 或 'a4_8' 每页八张",
                "enum": ["single", "a4_8"],
                "default": "a4_8"
            },
            "filename": {
                "type": "string",
                "description": "导出的PDF文件名",
                "default": "flashcards.pdf"
            }
        },
        "required": ["flashcard_data"]
    }
)

# 工具处理函数
@generate_flashcard_tool.handle
def handle_generate_flashcard(request: MCPRequest) -> Dict[str, Any]:
    """处理闪卡生成请求"""
    try:
        # 获取闪卡数据
        flashcard_data = request.params.get("flashcard_data", {})
        
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

@validate_flashcard_data_tool.handle
def handle_validate_flashcard_data(request: MCPRequest) -> Dict[str, Any]:
    """处理闪卡数据验证请求"""
    try:
        # 获取闪卡数据
        flashcard_data = request.params.get("flashcard_data", {})
        
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

@list_flashcard_templates_tool.handle
def handle_list_flashcard_templates(request: MCPRequest) -> Dict[str, Any]:
    """处理列出闪卡模板请求"""
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

# 工具处理函数：导出 PDF
@export_flashcards_pdf_tool.handle
def handle_export_flashcards_pdf(request: MCPRequest) -> Dict[str, Any]:
    """处理将闪卡导出为正反两面PDF的请求"""
    try:
        # 获取闪卡数据与文件名
        flashcard_data = request.params.get("flashcard_data", {})
        filename = request.params.get("filename", "flashcards.pdf")
        layout = request.params.get("layout", "a4_8")

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

# 创建并运行MCP服务器
if __name__ == "__main__":
    # 初始化MCP服务器
    server = FlashcardMCPServer()
    
    # 运行服务器
    server.run(
        host=SERVER_CONFIG.get('host', '127.0.0.1'),
        port=SERVER_CONFIG.get('port', 8000),
        debug=SERVER_CONFIG.get('debug', True)
    )

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