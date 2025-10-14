# FlashCard MCP Server 与 Dify 集成操作指南

## 概述

本指南将详细介绍如何将 FlashCard MCP Server 集成到 Dify 平台中，使您能够在 Dify 的 AI 应用中使用闪卡生成功能。

## 什么是 MCP (Model Context Protocol)

MCP (Model Context Protocol) 是由 Anthropic 开发的开放标准协议 <mcreference link="https://docs.dify.ai/en/learn-more/extended-reading/dify-docs-mcp" index="2">2</mcreference>，它为 AI 模型提供了与外部工具和数据源交互的标准化接口。通过 MCP，AI 模型可以访问软件工具和数据，实现更丰富的功能集成。

### MCP 的核心组件

- **Tools（工具）**: 可执行的功能，通过 POST 端点提供 <mcreference link="https://github.com/jlowin/fastmcp" index="2">2</mcreference>
- **Resources（资源）**: 只读的数据端点，通过 GET 请求访问 <mcreference link="https://github.com/jlowin/fastmcp" index="2">2</mcreference>
- **Prompts（提示）**: 定义交互模式的模板

## 前置条件

### 系统要求
- Python 3.8 或更高版本
- uv 包管理器
- 网络连接（用于 HTTP 传输）

### Dify 要求
- Dify v1.6.0 或更高版本（支持原生 MCP 集成）<mcreference link="https://dify.ai/blog/v1-6-0-built-in-two-way-mcp-support" index="3">3</mcreference>
- 管理员权限（用于配置 MCP 服务器）

## 第一部分：准备 FlashCard MCP Server

### 1. 项目设置

确保您的 FlashCard MCP 项目已正确设置：

```bash
# 克隆或进入项目目录
cd /path/to/FlashCardMCP

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv sync
```

### 2. 配置服务器

检查 `config.py` 中的服务器配置：

```python
SERVER_CONFIG = {
    'host': '127.0.0.1',  # 本地访问
    'port': 8000,         # 端口号
    'debug': True,
    'reload': True,
    'workers': 1
}
```

### 3. 启动 MCP Server

使用 HTTP 传输模式启动服务器：

```bash
# 方法1：直接运行
python server.py

# 方法2：使用 uv 运行
uv run server.py
```

服务器启动后，MCP 端点将在以下地址可用：
```
http://127.0.0.1:8000/mcp/
```

### 4. 验证服务器运行

您可以通过以下方式验证服务器是否正常运行：

```bash
# 检查服务器状态
curl http://127.0.0.1:8000/mcp/

# 或者查看可用的工具和资源
curl -X POST http://127.0.0.1:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

## 第二部分：在 Dify 中配置 MCP Server

### 1. 访问 Dify MCP 配置

1. 登录您的 Dify 实例
2. 导航到 **工具** (Tools) 页面
3. 选择 **MCP** 选项 <mcreference link="https://dify.ai/blog/v1-6-0-built-in-two-way-mcp-support" index="3">3</mcreference>

### 2. 添加 MCP Server

点击 **添加服务器** 按钮，填写以下信息：

#### 基本配置
- **服务器名称**: `FlashCardGenerator`
- **服务器标识符**: `flashcard-mcp-server`
- **MCP 服务器 URL**: `http://127.0.0.1:8000/mcp/`
- **协议版本**: `2025-03-26` <mcreference link="https://dify.ai/blog/v1-6-0-built-in-two-way-mcp-support" index="3">3</mcreference>

#### 高级配置（可选）
- **超时设置**: 30 秒
- **重试次数**: 3
- **描述**: "闪卡生成 MCP 服务器，提供闪卡创建、PDF 导出、CSV 转换等功能"

### 3. 测试连接

配置完成后：
1. 点击 **测试连接** 按钮
2. 确认连接状态显示为 **已连接**
3. 验证可用工具列表显示以下工具：
   - `create_flashcards_from_json`
   - `generate_flashcards_pdf`
   - `convert_csv_to_flashcards`
   - `validate_flashcard_data`

### 4. 保存配置

确认所有设置正确后，点击 **保存** 按钮完成配置。

## 第三部分：在 Dify 应用中使用 MCP 工具

### 1. 创建新的 Agent 应用

1. 在 Dify 中创建新的 **Agent** 应用
2. 在应用配置中，导航到 **工具** 部分
3. 启用 FlashCard MCP 服务器中的工具 <mcreference link="https://dify.ai/blog/dify-mcp-plugin-hands-on-guide-integrating-zapier-for-effortless-agent-tool-calls" index="4">4</mcreference>

### 2. 配置可用工具

选择您需要的工具：

#### create_flashcards_from_json
- **功能**: 从 JSON 数据创建闪卡
- **参数**: 
  - `cards`: 闪卡数据列表
  - `title`: 闪卡集标题
  - `template`: 模板选择（default/minimal/listen）
  - `theme`: 主题（light/dark）

#### generate_flashcards_pdf
- **功能**: 生成 PDF 格式的闪卡
- **参数**:
  - `cards`: 闪卡数据列表
  - `title`: PDF 标题
  - `layout`: 布局选项

#### convert_csv_to_flashcards
- **功能**: 将 CSV 数据转换为闪卡
- **参数**:
  - `csv_content`: CSV 内容
  - `front_columns`: 正面列索引
  - `back_columns`: 背面列索引

#### validate_flashcard_data
- **功能**: 验证闪卡数据格式
- **参数**:
  - `flashcard_json`: 待验证的 JSON 数据

### 3. 测试工具功能

在 Agent 应用中测试工具：

```
用户: 请帮我创建一套关于 Python 基础的闪卡

Agent 将自动：
1. 生成适当的闪卡内容
2. 调用 create_flashcards_from_json 工具
3. 返回生成的闪卡 HTML 页面链接
```

## 第四部分：高级配置和优化

### 1. 网络配置

如果需要在不同机器上运行 Dify 和 MCP Server：

#### 修改服务器配置
```python
# config.py
SERVER_CONFIG = {
    'host': '0.0.0.0',  # 允许外部访问
    'port': 8000,
    'debug': False,     # 生产环境关闭调试
    'reload': False,
    'workers': 1
}
```

#### 更新 Dify 配置
```
MCP 服务器 URL: http://YOUR_SERVER_IP:8000/mcp/
```

### 2. 安全配置

#### 添加认证（推荐）
```python
# 在 server.py 中添加认证中间件
from fastmcp.auth import APIKeyAuth

mcp = FastMCP(
    name="FlashcardGenerator",
    auth=APIKeyAuth(api_key="your-secret-api-key")
)
```

#### 在 Dify 中配置认证
在 MCP 服务器配置中添加：
- **认证类型**: API Key
- **API Key**: `your-secret-api-key`

### 3. 性能优化

#### 增加工作进程
```python
SERVER_CONFIG = {
    'host': '0.0.0.0',
    'port': 8000,
    'workers': 4  # 增加工作进程数
}
```

#### 启用缓存
```python
# 在工具函数中添加缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_template_processing(template_name):
    # 缓存模板处理结果
    pass
```

## 第五部分：故障排除

### 常见问题

#### 1. 连接失败
**问题**: Dify 无法连接到 MCP Server
**解决方案**:
- 检查服务器是否正在运行
- 验证 URL 和端口是否正确
- 检查防火墙设置
- 确认网络连通性

#### 2. 工具不可用
**问题**: MCP 工具在 Dify 中不显示
**解决方案**:
- 验证服务器配置正确
- 检查工具装饰器是否正确应用
- 重启 MCP Server
- 刷新 Dify 中的 MCP 配置

#### 3. 性能问题
**问题**: 工具调用响应缓慢
**解决方案**:
- 增加服务器工作进程数
- 优化工具函数性能
- 启用适当的缓存机制
- 检查网络延迟

### 调试技巧

#### 启用详细日志
```python
# config.py
LOGGING_CONFIG = {
    # ... 现有配置
    'loggers': {
        'mcp': {
            'level': 'DEBUG',  # 启用调试日志
            'handlers': ['console', 'file']
        }
    }
}
```

#### 监控工具调用
```python
# 在工具函数中添加日志
import logging
logger = logging.getLogger(__name__)

@mcp.tool
def create_flashcards_from_json(cards, **kwargs):
    logger.info(f"Creating flashcards with {len(cards)} cards")
    # ... 工具逻辑
    logger.info("Flashcards created successfully")
```

## 第六部分：最佳实践

### 1. 开发建议

- **版本控制**: 为 MCP Server 使用语义化版本控制
- **文档**: 保持工具描述和参数文档的更新
- **测试**: 为每个 MCP 工具编写单元测试
- **监控**: 实施适当的日志记录和监控

### 2. 部署建议

- **环境隔离**: 在不同环境中使用不同的配置
- **负载均衡**: 对于高负载场景，考虑使用负载均衡器
- **备份**: 定期备份配置和数据
- **更新策略**: 制定平滑的更新和回滚策略

### 3. 安全建议

- **认证**: 始终在生产环境中启用认证
- **HTTPS**: 在生产环境中使用 HTTPS
- **访问控制**: 限制对 MCP Server 的网络访问
- **日志审计**: 记录所有工具调用以进行审计

## 结论

通过本指南，您应该能够成功地将 FlashCard MCP Server 集成到 Dify 平台中。这种集成使您能够在 Dify 的 AI 应用中利用强大的闪卡生成功能，为用户提供更丰富的学习工具体验。

如果您在集成过程中遇到任何问题，请参考故障排除部分或查阅相关文档。

## 参考资源

- [FastMCP 官方文档](https://gofastmcp.com/)
- [Dify MCP 集成指南](https://docs.dify.ai/en/guides/tools/mcp)
- [Model Context Protocol 规范](https://modelcontextprotocol.io/)
- [FlashCard MCP Server 项目文档](./README.md)

---

*最后更新: 2024年12月*