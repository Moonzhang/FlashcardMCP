#!/usr/bin/env python3
"""
测试CSV上传API的脚本
"""

import requests
import json

def generate_flashcards_from_json(json_data):
    """从JSON数据生成HTML闪卡"""
    
    # 闪卡生成API端点
    url = "http://localhost:8080/convert_to_flashcards"
    
    try:
        print("\n正在生成HTML闪卡...")
        
        # 发送POST请求生成闪卡
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=json_data, headers=headers)
        
        print(f"闪卡生成响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ HTML闪卡生成成功!")
            
            # 检查响应格式：{'success': True, 'result': {'html': html_content}}
            if 'result' in result and 'html' in result['result']:
                html_content = result['result']['html']
                
                # 保存HTML文件
                output_file = "csv_upload_flashcards.html"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"📄 HTML闪卡已保存到: {output_file}")
                print(f"📊 HTML内容长度: {len(html_content)} 字符")
                
                return html_content
            else:
                print("❌ 响应中没有找到HTML内容")
                print(f"实际响应结构: {list(result.keys())}")
                return None
        else:
            print("❌ HTML闪卡生成失败!")
            try:
                error_info = response.json()
                print(f"错误信息: {error_info}")
            except:
                print(f"响应内容: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 生成HTML闪卡时出现错误: {str(e)}")
        return None

def test_csv_upload():
    """测试CSV文件上传API"""
    
    # API端点
    url = "http://localhost:8080/upload_csv"
    
    # 测试用的CSV文件路径
    csv_file_path = "tests/词语表.csv"
    
    try:
        # 准备文件上传
        with open(csv_file_path, 'rb') as f:
            files = {'file': ('词语表.csv', f, 'text/csv')}
            
            # 可选参数
            data = {
                'front_columns': '0',  # 第一列作为正面
                'back_columns': '1,2',  # 第二列和第三列合并作为背面
                'has_header': True,
                'title': '词语表测试',
                'column_separator': ' '  # 用空格分隔多列内容
            }
            
            print("正在上传CSV文件...")
            response = requests.post(url, files=files, data=data)
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ CSV上传成功!")
                print(f"成功状态: {result.get('success')}")
                
                # 显示转换后的数据结构
                if 'result' in result:
                    json_data = result['result']
                    print(f"标题: {json_data.get('metadata', {}).get('title', 'N/A')}")
                    print(f"描述: {json_data.get('metadata', {}).get('description', 'N/A')}")
                    print(f"卡片数量: {len(json_data.get('cards', []))}")
                    
                    # 显示前3张卡片
                    cards = json_data.get('cards', [])
                    for i, card in enumerate(cards[:3]):
                        print(f"卡片 {i+1}: {card.get('front')} -> {card.get('back')}")
                        if card.get('tags'):
                            print(f"  标签: {card.get('tags')}")
                    
                    # 生成HTML闪卡
                    html_content = generate_flashcards_from_json(json_data)
                    
                    if html_content:
                        print("\n🎉 完整流程测试成功!")
                        print("✅ CSV文件上传 → JSON转换 → HTML闪卡生成")
                        return json_data, html_content
                    else:
                        print("\n⚠️ CSV上传成功，但HTML闪卡生成失败")
                        return json_data, None
                else:
                    print("响应中没有找到结果数据")
                    return None, None
            else:
                print("❌ CSV上传失败!")
                try:
                    error_info = response.json()
                    print(f"错误信息: {error_info}")
                except:
                    print(f"响应内容: {response.text}")
                return None, None
                    
    except FileNotFoundError:
        print(f"❌ 找不到测试文件: {csv_file_path}")
        return None, None
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行 (python src/main.py)")
        return None, None
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return None, None

if __name__ == "__main__":
    print("=== CSV上传API测试 ===")
    test_csv_upload()