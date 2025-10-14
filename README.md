# FlashCardMCP / 闪卡生成MCP服务

- [English](README_en.md)
- [中文](README_zh.md)

---

## 项目介绍

FlashCardMCP 是一个基于 FastMCP 的 MCP 服务，用于将 JSON 格式的 Markdown 内容转换为交互式闪卡页面。这个服务适用于学习、教学和知识管理场景，可以帮助用户创建自己的数字闪卡集。

## 功能特性

1. **Markdown 支持**: 闪卡内容支持完整的 Markdown 语法，包括标题、列表、代码块、表格等
2. **交互式闪卡**: 点击卡片可以翻转查看背面内容
3. **多种模板**: 提供 Default、Minimal、Listen 三种不同的闪卡模板
4. **语音功能**: Listen 模板支持语音播放和听写模式
5. **响应式设计**: 适配不同屏幕尺寸
6. **打印支持**: 支持导出 PDF 和打印功能
7. **数据验证**: 内置数据格式验证功能
8. **CSV 转换**: 支持从 CSV 数据快速创建闪卡

## FastMCP 配置

本项目使用 FastMCP 框架构建 MCP 服务，提供以下功能：

- **Resources（资源）**: 通过 GET 端点暴露只读数据
- **Tools（工具）**: 通过 POST 端点提供可执行功能
- **多种返回类型**: 支持文本、JSON、图像、音频等格式

### 可用的 MCP 工具和资源

#### Resources
- `get_flashcard_templates`: 获取所有可用的闪卡模板信息

#### Tools
- `create_flashcards_from_json`: 从 JSON 数据创建闪卡 HTML 页面
- `generate_flashcards_pdf`: 将闪卡导出为 PDF 文件
- `convert_csv_to_flashcards`: 将 CSV 数据转换为闪卡 HTML
- `validate_flashcard_data`: 验证闪卡数据的格式正确性

## 闪卡模板

### 1. Default 模板
- 流式网格布局，每行显示2张卡片
- 适合桌面浏览和批量查看闪卡

### 2. Minimal 模板
- 单卡片居中显示
- 适合专注学习和逐张复习

### 3. Listen 模板
- 单卡片 + 底部控制面板
- 支持语音播放和听写模式
- 适合语言学习和语音复习

## Demo 页面

> **注意**: Demo 页面功能正在开发中，将在后续版本中提供在线演示。

## 快速开始

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

MCP 服务器默认使用 STDIO 传输协议，与 Claude Desktop 等 MCP 客户端兼容：

```bash
python server.py
```

## 许可证

本项目采用 GPL 协议。