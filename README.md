# FlashCardMCP / 闪卡生成MCP服务

[English](#english) | [中文](#中文)

---

## English

A FastMCP-based MCP server for converting JSON-formatted Markdown content into interactive flashcard pages.

### Project Overview

FlashCardMCP is a simple yet powerful MCP server that receives JSON data containing Markdown content and converts it into beautiful, interactive flashcard pages. This service is ideal for learning, teaching, and knowledge management scenarios, helping users create their own digital flashcard collections.

### Tech Stack

- **FastMCP**: Core framework for building MCP servers <mcreference link="https://github.com/jlowin/fastmcp" index="1">1</mcreference>
- **Python-Markdown**: For parsing Markdown content
- **Custom Template Engine**: For HTML template rendering (replaces Jinja2)
- **Custom Validation Logic**: For data validation (replaces Pydantic)

### Quick Start

#### Install Dependencies

Install project dependencies using UV:

```bash
uv pip install -r requirements.txt
```

Or use standard pip:

```bash
pip install -r requirements.txt
```

#### Run MCP Server

The MCP server uses STDIO transport by default, which is compatible with Claude Desktop and other MCP clients: <mcreference link="https://gofastmcp.com/deployment/running-server" index="2">2</mcreference>

```bash
python main.py
```

#### Test MCP Server

You can use the provided test scripts to run all tests:

```bash
python tests/run_tests.py
```

Or run specific test modules:

```bash
python tests/run_tests.py json     # Run JSON validator tests
python tests/run_tests.py markdown # Run Markdown parser tests
python tests/run_tests.py card     # Run flashcard generator tests
```

### MCP Tools Available

The server exposes the following tools through the MCP protocol: <mcreference link="https://gofastmcp.com/getting-started/quickstart" index="3">3</mcreference>

- **generate_flashcard**: Generate flashcard HTML pages from JSON data
- **validate_flashcard_data**: Validate flashcard data structure
- **list_flashcard_templates**: List available flashcard templates
- **export_flashcards_pdf**: Export flashcards to PDF format

### JSON Data Format

To use FlashCardMCP, provide JSON data in the following format:

```json
{
  "title": "Flashcard Set Title",
  "description": "Flashcard Set Description",
  "cards": [
    {
      "front": "Front content (supports Markdown)",
      "back": "Back content (supports Markdown)",
      "tags": ["tag1", "tag2"]
    }
    // More cards...
  ],
  "style": {
    "theme": "light", // Options: light, dark, custom
    "font": "Arial, sans-serif",
    "colors": {
      "primary": "#007bff",
      "secondary": "#6c757d",
      "background": "ffffff",
      "text": "333333",
      "card_bg": "ffffff",
      "card_border": "dddddd"
    }
  },
  "metadata": {
    "version": "1.0",
    "author": "Author Name",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

### Features

1. **Markdown Support**: Full Markdown syntax support including headers, lists, code blocks, tables
2. **Interactive Flashcards**: Click cards to flip and view back content
3. **Theme Switching**: Support for light, dark, and custom themes
4. **Tag Filtering**: Filter flashcards by tags
5. **Search Functionality**: Search through flashcard content
6. **Navigation**: Keyboard and button navigation support
7. **Shuffle**: Randomly shuffle flashcard order
8. **Responsive Design**: Adapts to different screen sizes

### MCP Client Configuration

#### Claude Desktop Configuration

To use this MCP server with Claude Desktop, add the following configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "flashcard-mcp": {
      "command": "python",
      "args": ["/path/to/FlashCardMCP/main.py"],
      "cwd": "/path/to/FlashCardMCP"
    }
  }
}
```

Replace `/path/to/FlashCardMCP` with the actual path to your FlashCardMCP directory.

#### Alternative Configuration (using uv)

If you're using UV for Python environment management:

```json
{
  "mcpServers": {
    "flashcard-mcp": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/path/to/FlashCardMCP"
    }
  }
}
```

#### Available MCP Tools

Once configured, the following tools will be available in Claude Desktop:

- **convert_to_flashcards**: Convert text/JSON data to interactive flashcard HTML
- **export_pdf**: Export flashcards to PDF format  
- **upload_csv**: Process CSV files and convert to flashcards

#### Verification

After adding the configuration:

1. Restart Claude Desktop
2. The FlashCardMCP server should appear in your available tools
3. You can test by asking Claude to "create flashcards from this content" with any text

---

## 中文

一个基于 FastMCP 的 MCP 服务，用于将 JSON 格式的 Markdown 内容转换为交互式闪卡页面。

### 项目介绍

FlashCardMCP 是一个简单而强大的 MCP 服务，它可以接收包含 Markdown 内容的 JSON 数据，并将其转换为美观、交互式的闪卡页面。这个服务适用于学习、教学和知识管理场景，可以帮助用户创建自己的数字闪卡集。

### 技术栈

- **FastMCP**: 用于构建 MCP 服务的核心框架 <mcreference link="https://github.com/jlowin/fastmcp" index="1">1</mcreference>
- **Python-Markdown**: 用于解析 Markdown 内容
- **自定义模板引擎**: 用于HTML模板渲染，替代Jinja2
- **自定义验证逻辑**: 用于数据验证，替代Pydantic

### 快速开始

#### 安装依赖

使用 UV 安装项目依赖：

```bash
uv pip install -r requirements.txt
```

或者使用标准的 pip 命令：

```bash
pip install -r requirements.txt
```

#### 运行 MCP 服务

MCP 服务器默认使用 STDIO 传输协议，与 Claude Desktop 等 MCP 客户端兼容： <mcreference link="https://gofastmcp.com/deployment/running-server" index="2">2</mcreference>

```bash
python main.py
```

#### 测试 MCP 服务

您可以使用提供的测试脚本来运行所有测试：

```bash
python tests/run_tests.py
```

或者运行特定的测试模块：

```bash
python tests/run_tests.py json  # 运行 JSON 验证器测试
python tests/run_tests.py markdown  # 运行 Markdown 解析器测试
python tests/run_tests.py card  # 运行闪卡生成器测试
```

### 可用的 MCP 工具

服务器通过 MCP 协议暴露以下工具： <mcreference link="https://gofastmcp.com/getting-started/quickstart" index="3">3</mcreference>

- **generate_flashcard**: 根据JSON数据生成闪卡HTML页面
- **validate_flashcard_data**: 验证闪卡数据的有效性
- **list_flashcard_templates**: 列出可用的闪卡模板
- **export_flashcards_pdf**: 导出闪卡为PDF格式

### JSON 数据格式

要使用 FlashCardMCP，您需要提供符合以下格式的 JSON 数据：

```json
{
  "title": "闪卡集标题",
  "description": "闪卡集描述",
  "cards": [
    {
      "front": "卡片正面内容 (支持 Markdown)",
      "back": "卡片背面内容 (支持 Markdown)",
      "tags": ["标签1", "标签2"]
    }
    // 更多卡片...
  ],
  "style": {
    "theme": "light", // 可选值: light, dark, custom
    "font": "Arial, sans-serif",
    "colors": {
      "primary": "#007bff",
      "secondary": "#6c757d",
      "background": "ffffff",
      "text": "333333",
      "card_bg": "ffffff",
      "card_border": "dddddd"
    }
  },
  "metadata": {
    "version": "1.0",
    "author": "作者名称",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

### 功能特性

1. **Markdown 支持**: 闪卡内容支持完整的 Markdown 语法，包括标题、列表、代码块、表格等
2. **交互式闪卡**: 点击卡片可以翻转查看背面内容
3. **主题切换**: 支持浅色主题、深色主题和自定义主题
4. **标签筛选**: 可以根据标签筛选闪卡
5. **搜索功能**: 可以搜索闪卡内容
6. **导航功能**: 支持键盘导航和按钮导航
7. **随机打乱**: 可以随机打乱闪卡顺序
8. **响应式设计**: 适配不同屏幕尺寸

### MCP 客户端配置

#### Claude Desktop 配置

要在 Claude Desktop 中使用此 MCP 服务器，请将以下配置添加到 Claude Desktop 配置文件中：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "flashcard-mcp": {
      "command": "python",
      "args": ["/path/to/FlashCardMCP/main.py"],
      "cwd": "/path/to/FlashCardMCP"
    }
  }
}
```

请将 `/path/to/FlashCardMCP` 替换为您的 FlashCardMCP 目录的实际路径。

#### 替代配置（使用 uv）

如果您使用 UV 进行 Python 环境管理：

```json
{
  "mcpServers": {
    "flashcard-mcp": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/path/to/FlashCardMCP"
    }
  }
}
```

#### 可用的 MCP 工具

配置完成后，以下工具将在 Claude Desktop 中可用：

- **convert_to_flashcards**: 将文本/JSON数据转换为交互式闪卡HTML
- **export_pdf**: 将闪卡导出为PDF格式
- **upload_csv**: 处理CSV文件并转换为闪卡

#### 验证配置

添加配置后：

1. 重启 Claude Desktop
2. FlashCardMCP 服务器应该出现在您的可用工具中
3. 您可以通过要求 Claude "从这些内容创建闪卡" 来测试任何文本内容

### 项目结构

```
FlashCardMCP/
├── main.py             # MCP 服务器主入口文件
├── src/
│   ├── main.py         # FastAPI 服务器 (用于开发测试)
│   ├── handlers/       # 处理函数
│   │   ├── card_generator.py  # 闪卡生成器
│   │   └── pdf_generator.py   # PDF 生成器
│   ├── utils/          # 工具函数
│   │   ├── json_validator.py  # JSON 验证器
│   │   ├── markdown_parser.py # Markdown 解析器
│   │   └── csv_reader.py      # CSV 读取器
│   └── templates/      # HTML 模板
│       └── card_template.html # 闪卡页面模板
├── tests/              # 测试文件
├── project_docs/       # 项目文档
├── requirements.txt    # 项目依赖
└── README.md          # 项目说明
```

### 开发指南

#### 代码规范

- 遵循 PEP 8 代码风格指南
- 为所有函数和类添加文档字符串
- 编写单元测试覆盖核心功能

#### 开发流程

1. 克隆项目仓库
2. 安装依赖：`uv pip install -r requirements.txt`
3. 进行代码修改
4. 运行测试：`python tests/run_tests.py`
5. 确保所有测试通过后再提交代码

### 部署指南

#### 本地部署

1. 安装所有依赖：`uv pip install -r requirements.txt`
2. 运行 MCP 服务：`python main.py`

#### 生产环境部署

对于生产环境，可以使用 FastMCP Cloud 进行部署： <mcreference link="https://gofastmcp.com/getting-started/quickstart" index="3">3</mcreference>

```bash
# 推送到 GitHub 仓库后，在 FastMCP Cloud 中创建项目
# 使用 main.py:mcp 作为服务器入口点
```

### 常见问题

#### Q: 如何自定义闪卡页面的样式？

A: 您可以在 JSON 数据中提供 `style` 字段来自定义闪卡页面的样式，包括主题、字体和颜色。

#### Q: 支持哪些 Markdown 语法？

A: 支持大部分标准 Markdown 语法，包括标题、列表、代码块、表格、链接、图片等。

#### Q: 如何添加自定义扩展？

A: 您可以修改 `src/utils/markdown_parser.py` 文件中的 `MarkdownParser` 类来添加自定义的 Markdown 扩展。

#### Q: MCP 服务器和 FastAPI 服务器有什么区别？

A: `main.py` 是标准的 MCP 服务器，用于与 Claude Desktop 等 MCP 客户端通信。`src/main.py` 是 FastAPI 服务器，主要用于开发测试和 Web 界面访问。

### 许可证

[MIT License](LICENSE)