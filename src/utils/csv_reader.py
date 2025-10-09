import csv
from typing import List, Dict, Any
'''
    This is a temp testing files for transfer CSV to pdf.
'''


def read_vocabulary_csv(file_path: str) -> List[Dict[str, str]]:
    """
    读取词语表CSV文件并返回词汇数据列表
    
    Args:
        file_path: CSV文件路径
        
    Returns:
        包含词汇数据的字典列表，每个字典包含：
        - word: 单词/短语
        - pos: 词性
        - definition: 释义
    """
    vocabulary_data = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # 获取CSV列数据，处理可能的列名变化
                word = row.get('单词/短语', '').strip()
                pos = row.get('词性', '').strip()
                definition = row.get('释义', '').strip()
                
                # 跳过空行
                if not word:
                    continue
                    
                vocabulary_data.append({
                    'word': word,
                    'pos': pos,
                    'definition': definition
                })
                
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV文件未找到: {file_path}")
    except Exception as e:
        raise Exception(f"读取CSV文件时出错: {str(e)}")
    
    return vocabulary_data


def convert_vocabulary_to_flashcard_data(vocabulary_data: List[Dict[str, str]], 
                                       title: str = "英语词汇闪卡") -> Dict[str, Any]:
    """
    将词汇数据转换为闪卡JSON格式
    
    Args:
        vocabulary_data: 词汇数据列表
        title: 闪卡集标题
        
    Returns:
        符合闪卡系统格式的JSON数据
    """
    cards = []
    
    for i, vocab in enumerate(vocabulary_data, 1):
        # 正面：英文单词/短语
        front_content = vocab['word']
        
        # 反面：词性 + 释义
        back_content = f"**{vocab['pos']}**\n\n{vocab['definition']}"
        
        card = {
            "id": f"vocab-{i}",
            "front": front_content,
            "back": back_content,
            "tags": ["vocabulary", "english"]
        }
        cards.append(card)
    
    flashcard_data = {
        "metadata": {
            "title": title,
            "description": f"包含{len(cards)}个英语词汇的闪卡集",
            "version": "1.0",
            "created_at": "2024-01-01",
            "tags": ["vocabulary", "english", "study"]
        },
        "style": {
            "template": "default",
            "theme": "light",
            "colors": {
                "primary": "#2563eb",
                "secondary": "#64748b",
                "background": "#ffffff",
                "text": "#1e293b",
                "card_bg": "#f8fafc",
                "card_border": "#e2e8f0"
            },
            "font": "Arial, sans-serif"
        },
        "cards": cards
    }
    
    return flashcard_data