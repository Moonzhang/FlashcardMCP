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
uv sync
```

或者使用标准的 pip 命令：

```bash
pip install -e .
```

#### 运行 MCP 服务

MCP 服务器默认使用 STDIO 传输协议，与 Claude Desktop 等 MCP 客户端兼容： <mcreference link="https://gofastmcp.com/deployment/running-server" index="2">2</mcreference>

```bash
python server.py
```

### FastMCP 配置

本项目使用 FastMCP 框架构建 MCP 服务。FastMCP 提供了一个 Pythonic 的接口来创建 MCP 服务器，支持以下特性： <mcreference link="https://gofastmcp.com/getting-started/quickstart" index="3">3</mcreference>

- **Resources（资源）**: 通过 GET 端点暴露只读数据 <mcreference link="https://gofastmcp.com/getting-started/quickstart" index="4">4</mcreference>
- **Tools（工具）**: 通过 POST 端点提供可执行功能 <mcreference link="https://gofastmcp.com/getting-started/quickstart" index="5">5</mcreference>
- **多种返回类型**: 支持文本、JSON、图像、音频等格式 <mcreference link="https://gofastmcp.com/getting-started/quickstart" index="6">6</mcreference>

#### 配置文件

项目配置通过 `config.py` 文件管理，包含以下设置：

- **服务器配置**: 主机地址、端口、调试模式等
- **模板配置**: 可用模板列表及其描述
- **路径配置**: 模板目录、静态文件目录等

### 可用的 MCP 工具和资源

服务器通过 MCP 协议暴露以下工具和资源：

#### Resources（资源）

1. **get_flashcard_templates**
   - **描述**: 获取所有可用的闪卡模板信息
   - **用法**: 返回模板列表，包含模板名称、文件路径和功能描述
   - **返回格式**: JSON 格式的模板配置信息

#### Tools（工具）

1. **create_flashcards_from_json**
   - **描述**: 从 JSON 数据创建闪卡 HTML 页面
   - **参数**: 
     - `data`: 包含闪卡内容的 JSON 数据
     - `template`: 模板名称（可选，默认为 "default"）
   - **用法**: 将结构化的闪卡数据转换为交互式 HTML 页面
   - **返回**: 生成的 HTML 内容

2. **generate_flashcards_pdf**
   - **描述**: 将闪卡导出为 PDF 文件
   - **参数**: 
     - `data`: 闪卡数据
     - `template`: 模板名称（可选）
   - **用法**: 生成适合打印的 PDF 格式闪卡
   - **返回**: PDF 文件的二进制数据

3. **convert_csv_to_flashcards**
   - **描述**: 将 CSV 数据转换为闪卡 HTML
   - **参数**: 
     - `csv_data`: CSV 格式的数据
     - `template`: 模板名称（可选）
   - **用法**: 从表格数据快速创建闪卡
   - **返回**: 生成的 HTML 内容

4. **validate_flashcard_data**
   - **描述**: 验证闪卡数据的格式正确性
   - **参数**: 
     - `data`: 待验证的闪卡数据
   - **用法**: 检查数据结构是否符合闪卡格式要求
   - **返回**: 验证结果和错误信息（如有）

### 闪卡模板功能

项目提供三种不同的闪卡模板，每种模板都有其独特的功能和使用场景：

#### 1. Default 模板（默认模板）
- **文件**: `card_template.html`
- **布局**: 流式网格布局，每行显示2张卡片
- **功能特性**:
  - 响应式设计，适配不同屏幕尺寸
  - 支持打印功能，自动调整为 A7 尺寸
  - 卡片翻转动画效果
  - 键盘导航支持（方向键、空格键）
  - 卡片索引显示
- **适用场景**: 适合桌面浏览和批量查看闪卡

#### 2. Minimal 模板（极简模板）
- **文件**: `minimal.html`
- **布局**: 单卡片居中显示
- **功能特性**:
  - 简洁的单卡片界面
  - 键盘导航（方向键切换卡片）
  - 点击翻转功能
  - 卡片计数器显示
  - 专注学习模式
- **适用场景**: 适合专注学习和逐张复习

#### 3. Listen 模板（听写模板）
- **文件**: `listen.html`
- **布局**: 单卡片 + 底部控制面板
- **功能特性**:
  - 语音播放功能（使用 Web Speech API）
  - 听写模式：隐藏内容，仅播放语音
  - 底部固定控制按钮
  - 键盘快捷键支持：
    - P: 播放/暂停
    - R: 显示/隐藏答案
    - 左右箭头: 切换卡片
  - 视觉状态指示器
  - 优化的移动端体验
- **适用场景**: 适合语言学习、听写练习和语音复习

### Demo 页面展示

> **注意**: Demo 页面功能正在开发中，将在后续版本中提供在线演示。

计划中的 Demo 页面将包含：
- 各种模板的实时预览
- 交互式功能演示
- 样例数据展示
- 使用教程和最佳实践

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
├── server.py           # MCP 服务器主入口文件
├── config.py           # 配置文件
├── mcp-config.json     # MCP 配置文件
├── pyproject.toml      # 项目配置和依赖
├── uv.lock            # UV 锁定文件
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
│       ├── card_template.html # 闪卡页面模板
│       ├── index.html         # 主页模板
│       ├── minimal.html       # 简化模板
│       └── playwright_card_template.html # Playwright 模板
├── static/             # 静态文件目录
└── README.md          # 项目说明
```

### 开发指南

#### 代码规范

- 遵循 PEP 8 代码风格指南
- 为所有函数和类添加文档字符串
- 编写清洁和可维护的代码

#### 开发流程

1. 克隆项目仓库
2. 安装依赖：`uv sync`
3. 进行代码修改
4. 确保代码质量后再提交代码

### 部署指南

#### 本地部署

1. 安装所有依赖：`uv sync`
2. 运行 MCP 服务：`python server.py`

### 常见问题

#### Q: 如何自定义闪卡页面的样式？

A: 您可以在 JSON 数据中提供 `style` 字段来自定义闪卡页面的样式，包括主题、字体和颜色。

#### Q: 支持哪些 Markdown 语法？

A: 支持大部分标准 Markdown 语法，包括标题、列表、代码块、表格、链接、图片等。

#### Q: 如何添加自定义扩展？

A: 您可以修改 `src/utils/markdown_parser.py` 文件中的 `MarkdownParser` 类来添加自定义的 Markdown 扩展。

#### Q: MCP 服务器和 FastAPI 服务器有什么区别？

A: `server.py` 是标准的 MCP 服务器，用于与 Claude Desktop 等 MCP 客户端通信。`src/main.py` 是 FastAPI 服务器，主要用于开发测试和 Web 界面访问。

### 许可证

[GPL License](LICENSE)