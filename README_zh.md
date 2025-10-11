# FlashCardMCP / 闪卡生成MCP服务

[English](#english) | [中文](#中文)

---

## 中文

一个基于 FastMCP 的 MCP 服务，用于将 JSON 格式的 Markdown 内容转换为交互式闪卡页面。

### 项目介绍

FlashCardMCP 是一个简单而强大的 MCP 服务，它可以接收包含 Markdown 内容的 JSON 数据，并将其转换为美观、交互式的闪卡页面。这个服务适用于学习、教学和知识管理场景，可以帮助用户创建自己的数字闪卡集。

### 技术栈

- **FastMCP**: 用于构建 MCP 服务的核心框架 <mcreference link="https://github.com/jlowin/fastmcp" index="1">1</mcreference>
- **Python-Markdown**: 用于解析 Markdown 内容
- **Jinja2**：模板引擎
- **Pydantic**：数据验证

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

[GPL License](LICENSE)