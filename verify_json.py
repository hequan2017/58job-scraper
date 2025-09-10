#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证JSON文件格式和内容
"""

import json
import os

def verify_json_format(json_file):
    """
    验证JSON文件格式
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 JSON文件验证结果:")
        print(f"总记录数: {len(data)}")
        
        if data:
            first_record = data[0]
            print(f"第一条记录的字段数: {len(first_record)}")
            print("\n字段列表:")
            for k, v in first_record.items():
                print(f"  {k}: {type(v).__name__}")
            
            # 检查必要字段
            required_fields = ["企业名称", "岗位名称", "工作地点", "抓取城市"]
            missing_fields = [field for field in required_fields if field not in first_record]
            if missing_fields:
                print(f"\n❌ 缺少必要字段: {missing_fields}")
            else:
                print(f"\n✅ 所有必要字段都存在")
            
            # 显示前3条记录的关键信息
            print("\n📋 前3条记录预览:")
            for i, record in enumerate(data[:3], 1):
                print(f"\n记录 {i}:")
                print(f"  企业名称: {record.get('企业名称', 'N/A')}")
                print(f"  岗位名称: {record.get('岗位名称', 'N/A')}")
                print(f"  工作地点: {record.get('工作地点', 'N/A')}")
                print(f"  抓取城市: {record.get('抓取城市', 'N/A')}")
                print(f"  薪资范围: {record.get('薪资范围起', 'N/A')}-{record.get('薪资范围至', 'N/A')}")
        
        # 文件大小
        file_size = os.path.getsize(json_file) / 1024 / 1024
        print(f"\n📁 文件大小: {file_size:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        return False

if __name__ == "__main__":
    json_file = "315个_custom.json"
    if os.path.exists(json_file):
        verify_json_format(json_file)
    else:
        print(f"❌ 文件不存在: {json_file}")