# FlashCardMCP / 闪卡生成MCP服务

**Version: 10.1**

[English](#english) | [中文](#中文)

---

## English

A FastMCP-based MCP server for converting JSON-formatted Markdown content into interactive flashcard pages.

### Project Overview

FlashCardMCP is a FastMCP-based MCP service designed to convert Markdown content in JSON/CSV format into interactive flashcard pages. This service is suitable for learning, teaching, knowledge management, and any other scenario you desire, helping users create their own digital flashcard sets.
- **Content Focus**: Utilizes Markdown format, aligning with LLM output, allowing users to concentrate on content creation rather than irrelevant formatting details.
- **Stable Output**: Employs functions to stably generate flashcards, supporting CSS style input to meet personalized needs.
- **Scenario-Based Templates**: Provides pre-built templates for various scenarios, with further expansion planned.
- **PDF Output**: Flashcards can be printed as PDFs (8 cards per sheet), further accommodating different scenarios and real-world applications for use and memorization.        

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

1. **flashcard-templates**
   - **URI**: `resource://flashcard-templates`
   - **Description**: Get information about all available flashcard templates and their configurations
   - **Return Format**: JSON format template configuration information

#### Tools

1. **create_flashcards_from_json**
   - **Description**: Create interactive HTML flashcards from JSON card data
   - **Parameters**: 
     - `cards`: List of flashcard data with 'front', 'back', and optional 'tags'
     - `title`: Title for the flashcard set
     - `description`: Description of the flashcard set
     - `template`: Template type ('minimal', 'default', 'elegant')
     - `theme`: Theme ('light' or 'dark')
   - **Returns**: Generated HTML content as string

2. **generate_flashcards_pdf**
   - **Description**: Generate PDF flashcards from JSON card data
   - **Parameters**: 
     - `cards`: List of flashcard data with 'front', 'back', and optional 'tags'
     - `title`: Title for the flashcard set
     - `description`: Description of the flashcard set
     - `layout`: Layout type ('single' or 'a4_8')
     - `output_path`: Directory path to save the PDF file
   - **Returns**: Success message with file path and size information

3. **convert_csv_to_json**
   - **Description**: Convert CSV content to flashcard JSON format
   - **Parameters**: 
     - `csv_content`: Raw CSV content as string
     - `front_columns`: Comma-separated column indices for card front (e.g., "0,1")
     - `back_columns`: Comma-separated column indices for card back (e.g., "2,3")
     - `tags_column`: Column index for tags (optional)
     - `has_header`: Whether CSV has header row
     - `title`: Title for the flashcard set
     - `description`: Description of the flashcard set
     - `column_separator`: Separator for multi-column content
     - `template`: Template type for styling
     - `theme`: Theme for styling
   - **Returns**: JSON string of complete flashcard data

4. **validate_flashcard_data**
   - **Description**: Validate flashcard JSON data structure
   - **Parameters**: 
     - `flashcard_json`: Flashcard data in JSON format
   - **Returns**: Validation result message
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

Replace the path with the actual path to your FlashCardMCP directory.

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

## Output Examples

The project provides various output examples in the `sample/` directory:

### HTML Flashcard Examples
- **card_template_sample.html**: Complete example of Default template, showcasing fluid grid layout and flip animations
- **minimal_template_sample.html**: Minimal template example with single-card centered display for focused learning
- **listen_template_sample.html**: Listen template example supporting voice playback and dictation mode

### PDF Output Examples
The `sample/pdf_generate/` directory contains PDF flashcard examples for various scenarios:
- **康奈尔笔记法闪卡_8卡片布局.pdf**: Cornell Note-taking method flashcards
- **基础测试_8卡片布局.pdf**: Basic knowledge test flashcards
- **Markdown测试_8卡片布局.pdf**: Markdown syntax support demonstration
- **词语表闪卡练习_8卡片布局.pdf**: Vocabulary learning flashcards
- **日文注音测试_8卡片布局.pdf**: Multi-language support example

All PDFs use A4 paper with 8-card layout, suitable for printing and physical use.

## Version History

### Version 10.1 (Current)
- Updated version information in all README files
- Corrected MCP tools and resources descriptions to match actual functionality
- Updated MCP client configuration with correct `uv run` command
- Improved documentation structure and content
- Added output examples showcase

### Future Version Plans
- Add more flashcard templates
- Optimize voice functionality
- Add online Demo page
- Support more export formats

### License

[GPL License](LICENSE)