#!/usr/bin/env python3
"""
测试基本闪卡生成功能
"""

from src.handlers.card_generator import generate_flashcards

# 使用与测试相同的数据
test_data = {
    "metadata": {
        "title": "测试闪卡集",
        "description": "这是一个测试用的闪卡集"
    },
    "cards": [
        {
            "front": "什么是 Python?",
            "back": "Python 是一种高级编程语言，以其简洁的语法和强大的生态系统而闻名。",
            "tags": ["编程", "Python"]
        },
        {
            "front": "FastMCP 的主要功能是什么?",
            "back": "FastMCP 是一个用于构建 MCP 服务的快速开发框架，支持各种处理函数和路由配置。",
            "tags": ["MCP", "FastMCP"]
        }
    ],
    "style": {
        "template": "default",
        "theme": "light",
        "font": "Arial, sans-serif"
    }
}

print("=== 生成基本闪卡 ===")
html_output = generate_flashcards(test_data)

# 检查关键内容
print(f"HTML长度: {len(html_output)} 字符")

# 检查标题
if "测试闪卡集" in html_output:
    print("✓ 标题 '测试闪卡集' 存在")
else:
    print("✗ 标题 '测试闪卡集' 不存在")

# 检查卡片内容
if "什么是 Python?" in html_output:
    print("✓ 卡片内容 '什么是 Python?' 存在")
else:
    print("✗ 卡片内容 '什么是 Python?' 不存在")

# 检查标签
if '<span class="card-tag">编程</span>' in html_output:
    print("✓ 标签 '编程' 存在")
else:
    print("✗ 标签 '编程' 不存在")

# 检查字体设置
if '--font-family: Arial, sans-serif;' in html_output:
    print("✓ 字体设置存在")
else:
    print("✗ 字体设置不存在")

# 检查交互功能
has_interaction = 'addEventListener' in html_output and 'click' in html_output and 'keydown' in html_output
print(f"{'✓' if has_interaction else '✗'} 交互功能{'存在' if has_interaction else '不存在'}")

# 检查主题设置
has_theme = '--primary-color:' in html_output and '--background-color:' in html_output
print(f"{'✓' if has_theme else '✗'} 主题设置{'存在' if has_theme else '不存在'}")

# 保存输出
with open('test_basic_output.html', 'w', encoding='utf-8') as f:
    f.write(html_output)

print("\n生成的HTML已保存到: test_basic_output.html")