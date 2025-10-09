# FlaskCardMCP

一个基于 FastMCP 的 MCP 服务，用于将 JSON 格式的 Markdown 内容转换为交互式闪卡页面。

## 项目介绍

FlaskCardMCP 是一个简单而强大的 MCP 服务，它可以接收包含 Markdown 内容的 JSON 数据，并将其转换为美观、交互式的闪卡页面。这个服务适用于学习、教学和知识管理场景，可以帮助用户创建自己的数字闪卡集。

## 技术栈

- **FastMCP**: 用于构建 MCP 服务的核心框架
- **Python-Markdown**: 用于解析 Markdown 内容
- **Uvicorn**: ASGI服务器（FastMCP的依赖）
- **自定义模板引擎**: 用于HTML模板渲染，替代Jinja2
- **自定义验证逻辑**: 用于数据验证，替代Pydantic

## 快速开始

### 安装依赖

使用 UV 安装项目依赖：

```bash
uv pip install -r requirements.txt
```

或者使用标准的 pip 命令：

```bash
pip install -r requirements.txt
```

### 运行 MCP 服务

```bash
python src/main.py
```

### 测试 MCP 服务

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

## JSON 数据格式

要使用 FlaskCardMCP，您需要提供符合以下格式的 JSON 数据：

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

### 字段说明

- `title` (必需): 闪卡集的标题
- `description` (可选): 闪卡集的描述
- `cards` (必需): 闪卡列表，每个闪卡包含：
  - `front` (必需): 卡片正面内容（支持 Markdown 格式）
  - `back` (必需): 卡片背面内容（支持 Markdown 格式）
  - `tags` (可选): 标签列表，用于分类和筛选
- `style` (可选): 样式配置，用于自定义闪卡页面的外观
  - `theme`: 主题（light、dark 或 custom）
  - `font`: 字体设置
  - `colors`: 自定义颜色设置（当 theme 为 custom 时生效）
- `metadata` (可选): 元数据信息

## 功能特性

1. **Markdown 支持**: 闪卡内容支持完整的 Markdown 语法，包括标题、列表、代码块、表格等
2. **交互式闪卡**: 点击卡片可以翻转查看背面内容
3. **主题切换**: 支持浅色主题、深色主题和自定义主题
4. **标签筛选**: 可以根据标签筛选闪卡
5. **搜索功能**: 可以搜索闪卡内容
6. **导航功能**: 支持键盘导航和按钮导航
7. **随机打乱**: 可以随机打乱闪卡顺序
8. **响应式设计**: 适配不同屏幕尺寸

## 项目结构

```
FlaskCardMCP/
├── src/
│   ├── main.py          # 主入口文件
│   ├── handlers/        # 处理函数
│   │   ├── __init__.py
│   │   └── card_generator.py  # 闪卡生成器
│   ├── utils/           # 工具函数
│   │   ├── __init__.py
│   │   ├── json_validator.py  # JSON 验证器
│   │   └── markdown_parser.py  # Markdown 解析器
│   └── templates/       # HTML 模板
│       ├── __init__.py
│       └── card_template.html  # 闪卡页面模板
├── tests/               # 测试文件
│   ├── run_tests.py     # 测试运行脚本
│   ├── test_json_validator.py  # JSON 验证器测试
│   ├── test_markdown_parser.py  # Markdown 解析器测试
│   ├── test_card_generator.py  # 闪卡生成器测试
│   └── test_data.json   # 测试数据
├── project_docs/        # 项目文档
│   ├── PRD.md           # 产品需求文档
│   ├── 技术配置.md      # 技术配置文档
│   └── 转换流程设计.md    # 转换流程设计文档
├── requirements.txt     # 项目依赖
└── README.md            # 项目说明
```

## 使用示例

### 通过 HTTP 请求调用

```bash
curl -X POST http://localhost:8000/convert_to_flashcards \
  -H "Content-Type: application/json" \
  -d '{"title": "测试闪卡集", "cards": [{"front": "问题", "back": "答案"}]}'
```

### 使用测试数据

项目提供了多个测试数据示例，可以在 `tests/test_data.json` 文件中找到。您可以使用这些数据来测试 MCP 的不同功能。

## 开发指南

### 代码规范

- 遵循 PEP 8 代码风格指南
- 为所有函数和类添加文档字符串
- 编写单元测试覆盖核心功能

### 开发流程

1. 克隆项目仓库
2. 安装依赖：`uv pip install -r requirements.txt`
3. 进行代码修改
4. 运行测试：`python tests/run_tests.py`
5. 确保所有测试通过后再提交代码

## 部署指南

### 本地部署

1. 安装所有依赖：`uv pip install -r requirements.txt`
2. 运行服务：`python src/main.py`

### 生产环境部署

对于生产环境，建议使用 Gunicorn 或 Uvicorn 作为 WSGI/ASGI 服务器：

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 常见问题

### Q: 如何自定义闪卡页面的样式？

A: 您可以在 JSON 数据中提供 `style` 字段来自定义闪卡页面的样式，包括主题、字体和颜色。

### Q: 支持哪些 Markdown 语法？

A: 支持大部分标准 Markdown 语法，包括标题、列表、代码块、表格、链接、图片等。

### Q: 如何添加自定义扩展？

A: 您可以修改 `src/utils/markdown_parser.py` 文件中的 `MarkdownParser` 类来添加自定义的 Markdown 扩展。

## 许可证

[MIT License](LICENSE)