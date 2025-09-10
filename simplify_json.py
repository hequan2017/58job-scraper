#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化JSON文件结构，去掉metadata包装，只保留纯数据数组
"""

import json
import os

def simplify_json(input_file, output_file=None):
    """
    简化JSON文件结构，去掉metadata包装
    
    Args:
        input_file (str): 输入JSON文件路径
        output_file (str): 输出JSON文件路径，如果为None则覆盖原文件
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_file):
            print(f"错误：JSON文件不存在 - {input_file}")
            return False
        
        print(f"正在读取JSON文件: {input_file}")
        
        # 读取JSON文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查文件结构
        if 'data' not in data:
            print("错误：JSON文件中没有找到'data'字段")
            return False
        
        # 提取纯数据数组
        pure_data = data['data']
        
        print(f"提取到 {len(pure_data)} 条记录")
        
        # 如果没有指定输出文件，覆盖原文件
        if output_file is None:
            output_file = input_file
        
        print(f"正在写入简化后的JSON文件: {output_file}")
        
        # 写入简化后的JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(pure_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 简化完成！")
        print(f"📊 记录数: {len(pure_data)}")
        print(f"📁 输出文件: {output_file}")
        
        # 显示文件大小对比
        file_size = os.path.getsize(output_file)
        print(f"📦 文件大小: {round(file_size/1024/1024, 2)} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ 简化失败: {str(e)}")
        return False

def main():
    """
    主函数
    """
    # JSON文件路径
    json_file = "58同城多城市职位详细信息.json"
    
    # 检查文件是否存在
    if not os.path.exists(json_file):
        print(f"错误：找不到JSON文件 - {json_file}")
        print("请确保文件在当前目录下")
        return
    
    # 执行简化
    success = simplify_json(json_file)
    
    if success:
        print("\n🎉 JSON文件简化成功完成！")
        print("现在JSON文件只包含纯数据数组，没有metadata包装")
    else:
        print("\n❌ 简化过程中出现错误")

if __name__ == "__main__":
    main()