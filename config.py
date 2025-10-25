import os
import sys

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 确保src目录在Python路径中
sys.path.append(PROJECT_ROOT)

def get_path(*path_parts):
    """获取项目内的绝对路径"""
    return os.path.join(PROJECT_ROOT, *path_parts)

# 模板目录
TEMPLATES_DIR = get_path('src', 'templates')

# 静态文件目录
STATIC_DIR = get_path('static')

# 默认输出目录
OUTPUT_DIR = get_path('test_output')

# MCP服务器配置
SERVER_CONFIG = {
    'host': '127.0.0.1',
    'port': 8000,
    'debug': True,
    'reload': True,
    'workers': 1
}

# 闪卡生成配置
FLASHCARD_CONFIG = {
    # 默认模板文件（兼容旧逻辑）
    'default_template': 'default.html',
    # 新增：默认模板名称（用于生成器回退使用）
    'default_template_name': 'default',
    
    # 可用的模板列表
    'available_templates': {
        'default': {
            'file_path': 'default.html',
            'description': '默认模板，提供基本的闪卡功能和样式'
        },
        'minimal': {
            'file_path': 'minimal.html',
            'description': '极简模板，仅展示卡片内容'
        },
        'listen': {
            'file_path': 'listen.html',
            'description': '听写模板，支持语音合成和听写功能'
        }
        # 未来可以在这里添加更多模板 Support more template configuration;
    },
    
    # 可用的主题列表
    'available_themes': ['light', 'dark', 'basic', 'advance', 'detail'],
    
    # 默认样式配置（统一默认参数）
    'default_style': {
        'theme': 'light',
        'colors': {
            'primary': '#007bff',
            'secondary': '#6c757d',
            'background': '#ffffff',
            'text': '#333333',
            'card_bg': '#ffffff',
            'card_front_bg': '#ffffff',
            'card_back_bg': '#f8f9fa',
            'card_border': '#dddddd'
        },
        'font': 'Arial,  PingFang SC, Microsoft YaHei,  sans-serif',
        # 统一控制与限制
        'compact_typography': True,
        'show_deck_name': False,
        'show_card_index': False,
        'show_tags': False,
        'front_char_limit': 180,
        'back_char_limit': 380,
        # 卡片尺寸配置
        'card_height': '105mm',
        'card_width': '74.25mm',
        # PDF 页码与叠加样式（新增默认值）
        'deck_name_style': 'font-weight:600; font-size:14px;',
        'card_index_style': 'position:absolute; top:6px; right:8px; font-size:12px;',
    },
    
    # 暗色主题默认配置
    'dark_theme_style': {
        'theme': 'dark',
        'colors': {
            'primary': '#007bff',
            'secondary': '#6c757d',
            'background': '#1a1a1a',
            'text': '#ffffff',
            'card_bg': '#2d2d2d',
            'card_border': '#444444',
            'card_front_bg': '#2d2d2d',
            'card_back_bg': '#2d2d2d'
        }
    },

    # 基础主题配置 (basic)
    'basic_theme_style': {
        'theme': 'basic',
        'colors': {
            'primary': '#4caf50',
            'secondary': '#81c784',
            'background': '#f5f5f5',
            'text': '#424242',
            'card_bg': '#f0f0f0',
            'card_border': '#cccccc',
            'card_front_bg': '#f0f0f0',
            'card_back_bg': '#f0f0f0'
        }
    },

    # 进阶主题配置 (advance)
    'advance_theme_style': {
        'theme': 'advance',
        'colors': {
            'primary': '#ff9800',
            'secondary': '#ffb74d',
            'background': '#fffde7',
            'text': '#5d4037',
            'card_bg': '#fff8e1',
            'card_border': '#bcaaa4',
            'card_front_bg': '#fff8e1',
            'card_back_bg': '#fff8e1'
        }
    },

    # 详细主题配置 (detail)
    'detail_theme_style': {
        'theme': 'detail',
        'colors': {
            'primary': '#2196f3',
            'secondary': '#64b5f6',
            'background': '#e1f5fe',
            'text': '#1976d2',
            'card_bg': '#e3f2fd',
            'card_border': '#90caf9',
            'card_front_bg': '#e3f2fd',
            'card_back_bg': '#e3f2fd'
        }
    },

}

# Markdown解析器配置
MARKDOWN_CONFIG = {
    # 默认扩展
    'default_extensions': [
        'fenced_code',  # 支持 fenced code blocks
        'tables',       # 支持表格
        'codehilite',   # 代码高亮
        'toc',          # 目录生成
        'admonition'    # 提示框支持
    ],
    
    # 扩展配置
    'extension_configs': {
        'codehilite': {
            'css_class': 'highlight',
            'linenums': False
        },
        'toc': {
            'title': '目录',
            'permalink': True
        }
    }
}

# JSON验证配置
JSON_VALIDATION_CONFIG = {
    # 允许的最大卡片数量
    'max_cards': 1000,
    
    # 允许的最大卡片内容长度
    'max_content_length': 10000,
    
    # 允许的最大标签数量
    'max_tags_per_card': 10,
    
    # 允许的最大标签长度
    'max_tag_length': 50
}

# 日志配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'simple': {
            'format': '%(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': get_path('logs', 'app.log'),
            'formatter': 'default',
            'level': 'DEBUG',
            'encoding': 'utf-8'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG'
    },
    'loggers': {
        'mcp': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'src': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# API路径配置
API_PATHS = {
    'generate_flashcard': '/api/generate-flashcard',
    'validate_flashcard_data': '/api/validate-flashcard-data',
    'list_templates': '/api/list-templates',
    'health_check': '/api/health'
}

# 创建必要的目录
def ensure_directories():
    """确保必要的目录存在"""
    # 确保日志目录存在
    log_dir = get_path('logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 确保静态目录存在
    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR)

    # 确保输出目录存在
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # 确保模板目录存在
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)

# 在导入时确保目录存在
ensure_directories()


# 根据环境变量加载不同配置
def load_env_config(env='development'):
    """根据环境加载不同的配置"""
    config_map = {
        'development': {
            'debug': True,
            'log_level': 'DEBUG'
        },
        'production': {
            'debug': False,
            'log_level': 'INFO',
            'workers': 4
        },
        'testing': {
            'debug': False,
            'log_level': 'INFO'
        }
    }
    
    # 获取当前环境的配置
    env_config = config_map.get(env, config_map['development'])
    
    # 更新SERVER_CONFIG
    for key, value in env_config.items():
        if key in SERVER_CONFIG:
            SERVER_CONFIG[key] = value
    
    return env_config

# 尝试从环境变量获取当前环境
current_env = os.environ.get('APP_ENV', 'development')

env_specific_config = load_env_config(current_env)

# 导出所有配置变量
__all__ = [
    'PROJECT_ROOT',
    'TEMPLATES_DIR',
    'STATIC_DIR',
    'OUTPUT_DIR',
    'SERVER_CONFIG',
    'FLASHCARD_CONFIG',
    'MARKDOWN_CONFIG',
    'JSON_VALIDATION_CONFIG',
    'LOGGING_CONFIG',
    'API_PATHS',
    'get_path',
    'ensure_directories',
    'load_env_config',
    'env_specific_config'
]