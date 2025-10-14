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
uv sync
```

Or use standard pip command:

```bash
pip install -e .
```

#### Run MCP Server

The MCP server uses STDIO transport by default, which is compatible with Claude Desktop and other MCP clients: <mcreference link="https://gofastmcp.com/deployment/running-server" index="2">2</mcreference>

```bash
python server.py
```

### FastMCP Configuration

This project uses the FastMCP framework to build MCP services. FastMCP provides a Pythonic interface for creating MCP servers with the following features: <mcreference link="https://gofastmcp.com/getting-started/quickstart" index="3">3</mcreference>

- **Resources**: Expose read-only data through GET endpoints <mcreference link="https://gofastmcp.com/getting-started/quickstart" index="4">4</mcreference>
- **Tools**: Provide executable functionality through POST endpoints <mcreference link="https://gofastmcp.com/getting-started/quickstart" index="5">5</mcreference>
- **Multiple Return Types**: Support for text, JSON, images, audio, and more <mcreference link="https://gofastmcp.com/getting-started/quickstart" index="6">6</mcreference>

#### Configuration File

Project configuration is managed through the `config.py` file, containing the following settings:

- **Server Configuration**: Host address, port, debug mode, etc.
- **Template Configuration**: Available template list and descriptions
- **Path Configuration**: Template directory, static file directory, etc.

### Available MCP Tools and Resources

The server exposes the following tools and resources through the MCP protocol:

#### Resources

1. **get_flashcard_templates**
   - **Description**: Get information about all available flashcard templates
   - **Usage**: Returns template list with names, file paths, and feature descriptions
   - **Return Format**: JSON format template configuration information

#### Tools

1. **create_flashcards_from_json**
   - **Description**: Create flashcard HTML pages from JSON data
   - **Parameters**: 
     - `data`: JSON data containing flashcard content
     - `template`: Template name (optional, defaults to "default")
   - **Usage**: Convert structured flashcard data into interactive HTML pages
   - **Returns**: Generated HTML content

2. **generate_flashcards_pdf**
   - **Description**: Export flashcards to PDF format
   - **Parameters**: 
     - `data`: Flashcard data
     - `template`: Template name (optional)
   - **Usage**: Generate print-ready PDF format flashcards
   - **Returns**: PDF file binary data

3. **convert_csv_to_flashcards**
   - **Description**: Convert CSV data to flashcard HTML
   - **Parameters**: 
     - `csv_data`: CSV format data
     - `template`: Template name (optional)
   - **Usage**: Quickly create flashcards from tabular data
   - **Returns**: Generated HTML content

4. **validate_flashcard_data**
   - **Description**: Validate flashcard data format correctness
   - **Parameters**: 
     - `data`: Flashcard data to validate
   - **Usage**: Check if data structure meets flashcard format requirements
   - **Returns**: Validation results and error messages (if any)

### Flashcard Template Features

The project provides three different flashcard templates, each with unique features and use cases:

#### 1. Default Template
- **File**: `card_template.html`
- **Layout**: Fluid grid layout displaying 2 cards per row
- **Features**:
  - Responsive design for different screen sizes
  - Print support with automatic A7 size adjustment
  - Card flip animation effects
  - Keyboard navigation support (arrow keys, spacebar)
  - Card index display
- **Use Cases**: Suitable for desktop browsing and batch flashcard viewing

#### 2. Minimal Template
- **File**: `minimal.html`
- **Layout**: Single card centered display
- **Features**:
  - Clean single-card interface
  - Keyboard navigation (arrow keys to switch cards)
  - Click-to-flip functionality
  - Card counter display
  - Focused study mode
- **Use Cases**: Suitable for focused learning and card-by-card review

#### 3. Listen Template
- **File**: `listen.html`
- **Layout**: Single card + bottom control panel
- **Features**:
  - Voice playback functionality (using Web Speech API)
  - Dictation mode: hide content, play audio only
  - Fixed bottom control buttons
  - Keyboard shortcut support:
    - P: Play/Pause
    - R: Show/Hide answer
    - Left/Right arrows: Switch cards
  - Visual status indicators
  - Optimized mobile experience
- **Use Cases**: Suitable for language learning, dictation practice, and audio review

### Demo Page Showcase

> **Note**: Demo page functionality is under development and will be available in future versions.

Planned Demo page will include:
- Real-time preview of various templates
- Interactive feature demonstrations
- Sample data showcases
- Usage tutorials and best practices

### MCP Tools Available

The server exposes the following tools through the MCP protocol: <mcreference link="https://gofastmcp.com/getting-started/quickstart" index="3">3</mcreference>

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
├── server.py           # MCP server entry point
├── config.py           # Configuration file
├── mcp-config.json     # MCP configuration file
├── pyproject.toml      # Project configuration and dependencies
├── uv.lock            # UV lock file
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
│       ├── card_template.html # Flashcard page template
│       ├── index.html         # Main page template
│       ├── minimal.html       # Minimal template
│       └── playwright_card_template.html # Playwright template
├── static/             # Static files directory
└── README.md          # Project description
```

### Development Guide

#### Code Style

- Follow PEP 8 style guide
- Add docstrings to all functions and classes
- Write clean and maintainable code

#### Development Workflow

1. Clone the project repository
2. Install dependencies: `uv sync`
3. Make code changes
4. Ensure code quality before committing

### Deployment Guide

#### Local Deployment

1. Install all dependencies: `uv sync`
2. Run MCP service: `python server.py`

### FAQ

#### Q: How to customize flashcard page style?

A: You can provide a `style` field in the JSON data to customize the flashcard page style, including theme, font, and colors.

#### Q: Which Markdown syntax is supported?

A: Most standard Markdown syntax is supported, including headers, lists, code blocks, tables, links, images, etc.

#### Q: How to add custom extensions?

A: You can modify the `MarkdownParser` class in `src/utils/markdown_parser.py` to add custom Markdown extensions.

#### Q: What is the difference between MCP server and FastAPI server?

A: `server.py` is a standard MCP server for communication with Claude Desktop and other MCP clients. `src/main.py` is a FastAPI server, mainly used for development testing and Web interface access.

### License

[GPL License](LICENSE)