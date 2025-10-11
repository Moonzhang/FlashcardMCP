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
- **Jinja2**：Template engine
- **Pydantic**：Data validation

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

### Project Structure

```
FlashCardMCP/
├── main.py             # MCP server entry point
├── src/
│   ├── main.py         # FastAPI server (for development testing)
│   ├── handlers/       # Handler functions
│   │   ├── card_generator.py  # Flashcard generator
│   │   └── pdf_generator.py   # PDF generator
│   ├── utils/          # Utility functions
│   │   ├── json_validator.py  # JSON validator
│   │   ├── markdown_parser.py # Markdown parser
│   │   └── csv_reader.py      # CSV reader
│   └── templates/      # HTML templates
│       └── card_template.html # Flashcard page template
├── tests/              # Test files
├── project_docs/       # Project documentation
├── requirements.txt    # Project dependencies
└── README.md          # Project description
```

### Development Guide

#### Code Style

- Follow PEP 8 style guide
- Add docstrings to all functions and classes
- Write unit tests to cover core functionality

#### Development Workflow

1. Clone the project repository
2. Install dependencies: `uv pip install -r requirements.txt`
3. Make code changes
4. Run tests: `python tests/run_tests.py`
5. Ensure all tests pass before committing code

### Deployment Guide

#### Local Deployment

1. Install all dependencies: `uv pip install -r requirements.txt`
2. Run MCP service: `python main.py`

### FAQ

#### Q: How to customize flashcard page style?

A: You can provide a `style` field in the JSON data to customize the flashcard page style, including theme, font, and colors.

#### Q: Which Markdown syntax is supported?

A: Most standard Markdown syntax is supported, including headers, lists, code blocks, tables, links, images, etc.

#### Q: How to add custom extensions?

A: You can modify the `MarkdownParser` class in `src/utils/markdown_parser.py` to add custom Markdown extensions.

#### Q: What is the difference between MCP server and FastAPI server?

A: `main.py` is a standard MCP server for communication with Claude Desktop and other MCP clients. `src/main.py` is a FastAPI server, mainly used for development testing and Web interface access.

### License

[MIT License](LICENSE)