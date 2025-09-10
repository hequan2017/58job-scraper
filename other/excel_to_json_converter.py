import pandas as pd
import json
from datetime import datetime
import os

def excel_to_json(excel_file, json_file=None):
    """
    将Excel文件转换为JSON格式
    
    Args:
        excel_file (str): Excel文件路径
        json_file (str): 输出的JSON文件路径，如果为None则自动生成
    """
    try:
        # 检查Excel文件是否存在
        if not os.path.exists(excel_file):
            print(f"错误：Excel文件 {excel_file} 不存在")
            return False
        
        # 读取Excel文件
        print(f"正在读取Excel文件: {excel_file}")
        df = pd.read_excel(excel_file)
        
        # 显示基本信息
        print(f"✓ 成功读取Excel文件")
        print(f"  - 总行数: {len(df)}")
        print(f"  - 总列数: {len(df.columns)}")
        print(f"  - 列名: {list(df.columns)}")
        
        # 处理NaN值，将其转换为空字符串
        df = df.fillna('')
        
        # 转换为字典列表
        data_list = df.to_dict('records')
        
        # 如果没有指定JSON文件名，自动生成
        if json_file is None:
            base_name = os.path.splitext(excel_file)[0]
            json_file = f"{base_name}.json"
        
        # 保存为JSON文件
        print(f"正在保存为JSON文件: {json_file}")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 成功转换并保存为JSON文件")
        print(f"  - 输出文件: {json_file}")
        print(f"  - 数据条数: {len(data_list)}")
        
        # 显示前3条数据作为预览
        if data_list:
            print("\n前3条数据预览:")
            for i, item in enumerate(data_list[:3]):
                print(f"\n第{i+1}条数据:")
                for key, value in item.items():
                    if len(str(value)) > 50:
                        print(f"  {key}: {str(value)[:50]}...")
                    else:
                        print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"转换过程中发生错误: {e}")
        return False

def main():
    """
    主函数
    """
    # Excel文件路径
    excel_file = "58同城多城市职位详细信息.xlsx"
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        print(f"错误：找不到Excel文件 {excel_file}")
        print("请确保文件存在于当前目录中")
        return
    
    # 转换为JSON
    json_file = "58同城多城市职位详细信息.json"
    
    print("=" * 60)
    print("Excel转JSON转换器")
    print("=" * 60)
    print(f"输入文件: {excel_file}")
    print(f"输出文件: {json_file}")
    print("-" * 60)
    
    success = excel_to_json(excel_file, json_file)
    
    if success:
        print("-" * 60)
        print("✓ 转换完成！")
        print(f"JSON文件已保存为: {json_file}")
    else:
        print("-" * 60)
        print("✗ 转换失败！")

if __name__ == "__main__":
    main()