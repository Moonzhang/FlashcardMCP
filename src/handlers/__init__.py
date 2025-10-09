# handlers 模块初始化文件

# 从子模块导入所有公开的函数和类
from .card_generator import generate_flashcards

# 定义模块的公开接口
__all__ = [
    "generate_flashcards"
]