# FlashCardMCP / 闪卡生成MCP服务

**版本: 10.1**

[English](#english) | [中文](#中文)

---

## 中文

一个基于 FastMCP 的 MCP 服务，用于将 JSON/CSV 格式的 Markdown 内容转换为交互式闪卡页面。

### 项目介绍


FlashCardMCP 是一个基于 FastMCP 的 MCP 服务，用于将 JSON/CSV 格式的 Markdown 内容转换为交互式闪卡页面。这个服务适用于学习、教学和知识管理以及任何你想要的场景，可以帮助用户创建自己的数字闪卡集。
- **专注内容**：使用Markdown格式，符合LLM的输出，让用户专注于内容的输出，而不是格式等其他无关紧要的内容；
- **稳定输出**：采用函数稳定生成闪卡，支持CSS格式Style输入，满足个性化需求；
- **场景化模板**： 预制模板用于预设的不同场景，后续会进一步拓展；
- **PDF输出**：闪卡可打印成PDF（8连卡），进一步满足不同场景下，以及现实多种场景下的使用和记忆。

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

### 可用的MCP工具和资源

服务器通过MCP协议暴露以下工具和资源：

#### 资源

1. **flashcard-templates**
   - **URI**：`resource://flashcard-templates`
   - **描述**：获取所有可用闪卡模板的信息和配置
   - **返回格式**：JSON格式的模板配置信息

#### 工具

1. **create_flashcards_from_json**
   - **描述**：从JSON数据创建交互式HTML闪卡
   - **参数**：
     - `cards`：闪卡数据列表，包含'front'、'back'和可选的'tags'
     - `title`：闪卡集标题
     - `description`：闪卡集描述
     - `template`：模板类型（'minimal'、'default'、'elegant'）
     - `theme`：主题（'light'或'dark'）
   - **返回**：生成的HTML内容字符串

2. **generate_flashcards_pdf**
   - **描述**：从JSON数据生成PDF格式闪卡
   - **参数**：
     - `cards`：闪卡数据列表，包含'front'、'back'和可选的'tags'
     - `title`：闪卡集标题
     - `description`：闪卡集描述
     - `layout`：布局类型（'single'或'a4_8'）
     - `output_path`：保存PDF文件的目录路径
   - **返回**：成功消息，包含文件路径和大小信息

3. **convert_csv_to_json**
   - **描述**：将CSV内容转换为闪卡JSON格式
   - **参数**：
     - `csv_content`：原始CSV内容字符串
     - `front_columns`：卡片正面的列索引（如"0,1"）
     - `back_columns`：卡片背面的列索引（如"2,3"）
     - `tags_column`：标签列索引（可选）
     - `has_header`：CSV是否有标题行
     - `title`：闪卡集标题
     - `description`：闪卡集描述
     - `column_separator`：多列内容分隔符
     - `template`：样式模板类型
     - `theme`：样式主题
   - **返回**：完整闪卡数据的JSON字符串

4. **validate_flashcard_data**
   - **描述**：验证闪卡JSON数据结构
   - **参数**：
     - `flashcard_json`：JSON格式的闪卡数据
   - **返回**：验证结果消息

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
    "FlashcardGenerator": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "fastmcp",
        "fastmcp",
        "run",
        "/Users/yinlei/Programming/showRoom/FlaskCardMCP/server.py"
      ]
    }
  }
}
```

请将路径替换为您的 FlashCardMCP 目录的实际路径。
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

## 输出效果展示

项目在 `sample/` 目录中提供了多种输出效果的示例：

### HTML 闪卡示例
- **card_template_sample.html**: Default 模板的完整示例，展示流式网格布局和翻转动画效果
- **minimal_template_sample.html**: Minimal 模板示例，单卡片居中显示，适合专注学习
- **listen_template_sample.html**: Listen 模板示例，支持语音播放和听写模式

### PDF 输出示例
`sample/pdf_generate/` 目录包含多种场景的PDF闪卡示例：
所有PDF采用A4纸8卡片布局，适合打印和实体使用。

## 版本记录

### Version 10.1 (当前版本)
- 更新了所有README文件中的版本信息
- 修正了MCP工具和资源的描述，确保与实际功能一致
- 更新了MCP客户端配置，使用正确的`uv run`命令
- 完善了文档结构和内容
- 增加了输出效果展示模块

### 未来版本计划
- 增加更多闪卡模板
- 优化语音功能
- 添加在线Demo页面


### 许可证

[GPL License](LICENSE)