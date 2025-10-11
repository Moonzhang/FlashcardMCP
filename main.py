#!/usr/bin/env python3
"""
闪卡生成MCP服务器 - 使用RouteMap和MCPType.EXCLUDE方式

基于现有的FastAPI应用，使用RouteMap模式控制端点暴露，
仅暴露/api/public/路径下的端点作为MCP工具，排除所有其他端点。
"""
"""
Flashcard Generation MCP Server - Using RouteMap and MCPType.EXCLUDE

Based on the existing FastAPI application, uses RouteMap mode to control endpoint exposure.
Only exposes endpoints under the /api/ path as MCP tools, excluding all other endpoints.
"""

from fastmcp import FastMCP
from src.main import app

# 根据GitHub文档正确导入RouteMap和RouteType
# Correctly import RouteMap and RouteType according to GitHub documentation
from fastmcp.server.openapi import RouteMap, RouteType

if __name__ == "__main__":
    print("启动FlashcardMCP服务器 - RouteMap模式")
    print("Starting FlashcardMCP Server - RouteMap Mode")
    print("只暴露以下端点作为MCP工具:")
    print("Only exposing the following endpoints as MCP tools:")
    print("- /api/convert_to_flashcards")
    print("- /api/export_pdf") 
    print("- /api/upload_csv")
    print("其他端点将被排除")
    print("Other endpoints will be excluded")
    
    # 使用RouteMap方式创建MCP服务器
    # Create MCP server using RouteMap mode
    mcp = FastMCP.from_fastapi(
        app=app,
        name="FlashcardMCP",
        route_maps=[
            # 只暴露 /api/ 下的端点作为工具
            # Only expose endpoints under /api/ as tools
            RouteMap(
                methods=["POST"],
                pattern=r"^/api/.*",
                route_type=RouteType.TOOL
            ),
        ],
    )
    
    mcp.run()
