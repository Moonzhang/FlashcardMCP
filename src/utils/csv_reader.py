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
    Converts a CSV file into a flashcard JSON data structure using column indices.

    Args:
        file_path (str): Path to the CSV file.
        title (Optional[str]): (Optional) Title of the flashcard set. Defaults to the filename if not provided.
        front_columns (Optional[List[int]]): (Optional) List of column indices to be used as the front of the cards (defaults to [0]).
        back_columns (Optional[List[int]]): (Optional) List of column indices to be used as the back of the cards (defaults to [1]).
        tags_column_index (Optional[int]): (Optional) Column index for tags, where multiple tags are separated by commas.
        has_header (bool): (Optional) Whether the CSV file contains a header row (defaults to True).
        column_separator (str): (Optional) Separator used when concatenating content from multiple columns (defaults to a space).

    Returns:
        Dict[str, Any]: JSON data conforming to the flashcard system format and validated.

    Raises:
        FileNotFoundError: If the CSV file is not found.
        Exception: If other errors occur during reading or processing the CSV file.
        ValueError: If no valid data rows are found in the CSV file to create cards.
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
                    next(reader)  # Skip header row
                except StopIteration:
                    pass # File is empty

            for row in reader:
                if not row: # Skip empty rows
                    continue

                # 计算所需的最大列索引
                all_columns = front_columns + back_columns
                if tags_column_index is not None:
                    all_columns.append(tags_column_index)
                max_index = max(all_columns) if all_columns else 0
                
                if len(row) <= max_index:
                    # If the number of columns in the row is not enough to get all the required indices, skip this row
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
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading or processing CSV file: {str(e)}")

    if not cards:
        raise ValueError("No valid data rows found in the CSV file to create cards.")

    # 构建初步的JSON结构
    flashcard_data = {
        "metadata": {
            "title": title,
            "description": f"Flashcard set generated from {os.path.basename(file_path)} with {len(cards)} cards.",
        },
        "cards": cards
    }

    # 使用json_validator进行验证和规范化
    normalized_data = normalize_json_data(flashcard_data)
    
    return normalized_data