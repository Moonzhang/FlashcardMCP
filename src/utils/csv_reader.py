import csv
import os
from typing import Dict, Any, Optional, List
from src.utils.json_validator import normalize_json_data

def convert_csv_to_json_data(
    file_path: str,
    title: Optional[str] = None,
    front_columns: Optional[List[int]] = None,
    back_columns: Optional[List[int]] = None,
    tags_column_index: Optional[int] = None,
    has_header: bool = True,
    column_separator: str = " "
) -> Dict[str, Any]:
    """
    通用CSV到闪卡JSON转换器，使用列索引。

    Converts a CSV file into a flashcard JSON data structure using column indices.

    Args:
        file_path (str): CSV文件路径。
                         Path to the CSV file.
        title (Optional[str]): (可选) 闪卡集的标题。如果未提供，则默认为文件名。
                               (Optional) Title of the flashcard set. Defaults to the filename if not provided.
        front_columns (Optional[List[int]]): (可选) 作为卡片正面的列索引列表（默认为[0]）。
                                             (Optional) List of column indices to be used as the front of the cards (defaults to [0]).
        back_columns (Optional[List[int]]): (可选) 作为卡片背面的列索引列表（默认为[1]）。
                                            (Optional) List of column indices to be used as the back of the cards (defaults to [1]).
        tags_column_index (Optional[int]): (可选) 作为标签的列索引，多个标签用逗号分隔。
                                           (Optional) Column index for tags, where multiple tags are separated by commas.
        has_header (bool): (可选) CSV文件是否包含标题行（默认为True）。
                           (Optional) Whether the CSV file contains a header row (defaults to True).
        column_separator (str): (可选) 多列内容合并时的分隔符（默认为空格）。
                                (Optional) Separator used when concatenating content from multiple columns (defaults to a space).

    Returns:
        Dict[str, Any]: 符合闪卡系统格式并通过验证的JSON数据。
                        JSON data conforming to the flashcard system format and validated.

    Raises:
        FileNotFoundError: 如果CSV文件未找到。
                           If the CSV file is not found.
        Exception: 读取或处理CSV文件时发生其他错误。
                   If other errors occur during reading or processing the CSV file.
        ValueError: 如果CSV文件中没有找到有效的数据行来创建卡片。
                    If no valid data rows are found in the CSV file to create cards.
    """
    if title is None:
        title = os.path.splitext(os.path.basename(file_path))[0]

    # 设置默认列索引
    if front_columns is None:
        front_columns = [0]
    if back_columns is None:
        back_columns = [1]

    cards = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            if has_header:
                try:
                    next(reader)  # 跳过标题行
                except StopIteration:
                    pass # 文件为空

            for row in reader:
                if not row: # 跳过空行
                    continue

                # 计算所需的最大列索引
                all_columns = front_columns + back_columns
                if tags_column_index is not None:
                    all_columns.append(tags_column_index)
                max_index = max(all_columns) if all_columns else 0
                
                if len(row) <= max_index:
                    # 如果行中的列数不足以获取所需的所有索引，则跳过此行
                    continue

                # 合并front列的内容
                front_parts = []
                for col_idx in front_columns:
                    if col_idx < len(row) and row[col_idx].strip():
                        front_parts.append(row[col_idx].strip())
                front_content = column_separator.join(front_parts)

                # 合并back列的内容
                back_parts = []
                for col_idx in back_columns:
                    if col_idx < len(row) and row[col_idx].strip():
                        back_parts.append(row[col_idx].strip())
                back_content = column_separator.join(back_parts)

                if not front_content:
                    continue

                card: Dict[str, Any] = {
                    "front": front_content,
                    "back": back_content,
                }

                if tags_column_index is not None and len(row) > tags_column_index:
                    tags_str = row[tags_column_index].strip()
                    if tags_str:
                        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                        if tags:
                            card["tags"] = tags
                
                cards.append(card)

    except FileNotFoundError:
        raise FileNotFoundError(f"CSV文件未找到: {file_path}")
    except Exception as e:
        raise Exception(f"读取或处理CSV文件时出错: {str(e)}")

    if not cards:
        raise ValueError("CSV文件中没有找到有效的数据行来创建卡片。")

    # 构建初步的JSON结构
    flashcard_data = {
        "metadata": {
            "title": title,
            "description": f"从 {os.path.basename(file_path)} 生成的包含 {len(cards)} 张卡片的闪卡集。",
        },
        "cards": cards
    }

    # 使用json_validator进行验证和规范化
    normalized_data = normalize_json_data(flashcard_data)
    
    return normalized_data