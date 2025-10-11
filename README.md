# FlashCardMCP / 闪卡生成MCP服务

- [English](README_en.md)
- [中文](README_zh.md)

---

## 项目介绍

FlashCardMCP 是一个简单而强大的 MCP 服务，它可以接收包含 Markdown 内容的 JSON 数据，并将其转换为美观、交互式的闪卡页面。这个服务适用于学习、教学和知识管理场景，可以帮助用户创建自己的数字闪卡集。

## 功能特性

1. **Markdown 支持**: 闪卡内容支持完整的 Markdown 语法，包括标题、列表、代码块、表格等
2. **交互式闪卡**: 点击卡片可以翻转查看背面内容
8. **响应式设计**: 适配不同屏幕尺寸

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

MCP 服务器默认使用 STDIO 传输协议，与 Claude Desktop 等 MCP 客户端兼容： <mcreference link="https://gofastmcp.com/deployment/running-server" index="2">2</mcreference>

```bash
python server.py
```



## 许可证

本项目采用 GPL 协议。