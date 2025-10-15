# FlashCardMCP / 闪卡生成MCP服务

**Version: 10.1**

- [English](README_en.md)
- [中文](README_zh.md)

---

## 项目介绍

FlashCardMCP 是一个基于 FastMCP 的 MCP 服务，用于将 JSON/CSV 格式的 Markdown 内容转换为交互式闪卡页面。这个服务适用于学习、教学和知识管理以及任何你想要的场景，可以帮助用户创建自己的数字闪卡集。
- **专注内容**：使用Markdown格式，符合LLM的输出，让用户专注于内容的输出，而不是格式等其他无关紧要的内容；
- **稳定输出**：采用函数稳定生成闪卡，支持CSS格式Style输入，满足个性化需求；
- **场景化模板**： 预制模板用于预设的不同场景，后续会进一步拓展；
- **PDF输出**：闪卡可打印成PDF（8连卡），进一步满足不同场景下，以及现实多种场景下的使用和记忆。

## 功能特性

1. **Markdown 支持**: 闪卡内容支持完整的 Markdown 语法，包括标题、列表、代码块、表格等
2. **交互式闪卡**: 点击卡片可以翻转查看背面内容
3. **多种模板**: 提供 Default、Minimal、Listen 三种不同的闪卡模板
4. **语音功能**: Listen 模板支持语音播放和听写模式（考虑到兼容性，目前仅是Web Speech API，效果一般）
5. **响应式设计**: 适配不同屏幕尺寸
6. **打印支持**: 支持导出 PDF 和打印功能
7. **数据验证**: 内置数据格式验证功能
8. **CSV 转换**: 支持从 CSV 数据快速创建闪卡

## FastMCP 配置

本项目使用 FastMCP 框架构建 MCP 服务，提供以下功能：

- **Resources（资源）**: 通过 GET 端点暴露只读数据
- **Tools（工具）**: 通过 POST 端点提供可执行功能
- **多种返回类型**: 支持文本、JSON、图像、音频等格式

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