#!/usr/bin/env python3
"""
测试CSV上传API的脚本 - 专注于API调用和不同输出参数的调试
"""

import requests
import json

def test_csv_upload_with_format(output_format='json'):
    """测试CSV文件上传API的不同输出格式"""
    
    # API端点
    url = "http://localhost:8080/api/upload_csv"
    
    # 测试用的CSV文件路径
    csv_file_path = "test_upload_csv.csv"
    
    try:
        # 准备文件上传
        with open(csv_file_path, 'rb') as f:
            files = {'file': ('test_upload_csv.csv', f, 'text/csv')}
            
            # 可选参数
            data = {
                'front_columns': '0',  # 第一列作为正面
                'back_columns': '1',   # 第二列作为背面
                'tags_column': '2',    # 第三列作为标签
                'has_header': True,
                'title': f'测试闪卡_{output_format}输出',
                'output_format': output_format  # 指定输出格式
            }
            
            print(f"正在上传CSV文件并生成{output_format.upper()}格式...")
            response = requests.post(url, files=files, data=data)
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ CSV上传并{output_format.upper()}生成成功!")
                
                if output_format == 'json':
                    result = response.json()
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
                        
                        return json_data
                    else:
                        print("响应中没有找到结果数据")
                        return None
                        
                elif output_format == 'html':
                    result = response.json()
                    print(f"成功状态: {result.get('success')}")
                    
                    # 显示HTML结果
                    if 'result' in result and 'html' in result['result']:
                        html_content = result['result']['html']
                        
                        # 保存HTML文件
                        output_file = f"test_csv_upload_{output_format}_output.html"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        
                        print(f"📄 HTML闪卡已保存到: {output_file}")
                        print(f"📊 HTML内容长度: {len(html_content)} 字符")
                        
                        return html_content
                    else:
                        print("❌ 响应中没有找到HTML内容")
                        return None
                        
                elif output_format == 'pdf':
                    # PDF格式直接返回二进制数据
                    pdf_content = response.content
                    
                    # 保存PDF文件
                    output_file = f"test_csv_upload_{output_format}_output.pdf"
                    with open(output_file, 'wb') as f:
                        f.write(pdf_content)
                    
                    print(f"📄 PDF闪卡已保存到: {output_file}")
                    print(f"📊 PDF文件大小: {len(pdf_content)} 字节")
                    
                    return pdf_content
                    
            else:
                print(f"❌ CSV上传失败!")
                try:
                    error_info = response.json()
                    print(f"错误信息: {error_info}")
                except:
                    print(f"响应内容: {response.text}")
                return None
                    
    except FileNotFoundError:
        print(f"❌ 找不到测试文件: {csv_file_path}")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行 (python src/main.py)")
        return None
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return None

def test_all_formats():
    """测试所有输出格式"""
    formats = ['json', 'html', 'pdf']
    
    for fmt in formats:
        print(f"\n{'='*50}")
        print(f"测试 {fmt.upper()} 输出格式")
        print(f"{'='*50}")
        
        result = test_csv_upload_with_format(fmt)
        
        if result:
            print(f"✅ {fmt.upper()} 格式测试成功")
        else:
            print(f"❌ {fmt.upper()} 格式测试失败")

if __name__ == "__main__":
    print("=== CSV上传API不同输出格式测试 ===")
    test_all_formats()