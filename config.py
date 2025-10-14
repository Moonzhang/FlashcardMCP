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
    # 默认模板名称
    'default_template': 'card_template.html',
    
    # 可用的模板列表
    'available_templates': {
        'default': {
            'file_path': 'card_template.html',
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
        # 未来可以在这里添加更多模板
    },
    
    # 默认样式配置
    'default_style': {
        'theme': 'light',
        'colors': {
            'primary': '#007bff',
            'secondary': '#6c757d',
            'background': '#ffffff',
            'text': '#333333',
            'card_bg': '#ffffff',
            'card_border': '#dddddd'
        },
        'font': 'Arial, sans-serif'
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
            'card_border': '#444444'
        }
    },
    
    # 卡片尺寸配置
    'card_dimensions': {
        'height': 250,  # 像素
        'min_width': 300  # 像素
    }
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
    
    # 确保模板目录存在
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)

# 在导入时确保目录存在
try:
    ensure_directories()
except Exception as e:
    print(f"警告: 创建必要目录时出错: {str(e)}")
    print("程序将继续运行，但某些功能可能受到影响")

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