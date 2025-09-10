#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将Excel文件转换为JSON格式
"""

import pandas as pd
import json
import os
from datetime import datetime

def excel_to_json(excel_file, json_file=None):
    """
    将Excel文件转换为JSON格式
    
    Args:
        excel_file (str): Excel文件路径
        json_file (str): 输出JSON文件路径，如果为None则自动生成
    """
    try:
        # 检查Excel文件是否存在
        if not os.path.exists(excel_file):
            print(f"错误：Excel文件不存在 - {excel_file}")
            return False
        
        print(f"正在读取Excel文件: {excel_file}")
        
        # 读取Excel文件
        df = pd.read_excel(excel_file)
        
        # 显示基本信息
        print(f"数据行数: {len(df)}")
        print(f"数据列数: {len(df.columns)}")
        print(f"列名: {list(df.columns)}")
        
        # 处理NaN值，转换为None
        df = df.where(pd.notnull(df), None)
        
        # 转换为字典列表
        data_list = df.to_dict('records')
        
        # 如果没有指定JSON文件名，自动生成
        if json_file is None:
            base_name = os.path.splitext(excel_file)[0]
            json_file = f"{base_name}.json"
        
        print(f"正在写入JSON文件: {json_file}")
        
        # 写入JSON文件
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'source_file': os.path.basename(excel_file),
                    'total_records': len(data_list),
                    'columns': list(df.columns),
                    'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                'data': data_list
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 转换完成！")
        print(f"📊 总记录数: {len(data_list)}")
        print(f"📁 输出文件: {json_file}")
        
        # 显示前3条记录作为预览
        if data_list:
            print("\n📋 数据预览（前3条记录）:")
            for i, record in enumerate(data_list[:3], 1):
                print(f"\n记录 {i}:")
                for key, value in record.items():
                    if value is not None:
                        print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")
        return False

def main():
    """
    主函数
    """
    # Excel文件路径
    excel_file = "58同城多城市职位详细信息.xlsx"
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        print(f"错误：找不到Excel文件 - {excel_file}")
        print("请确保文件在当前目录下")
        return
    
    # 执行转换
    success = excel_to_json(excel_file)
    
    if success:
        print("\n🎉 Excel到JSON转换成功完成！")
    else:
        print("\n❌ 转换过程中出现错误")

if __name__ == "__main__":
    main()