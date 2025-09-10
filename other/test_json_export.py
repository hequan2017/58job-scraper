#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json
import os
from enhanced_job_scraper import Enhanced58JobScraper

def test_json_export():
    """测试Excel和JSON同时导出功能"""
    
    # 创建测试数据
    test_data = [
        {
            '企业名称': '测试公司A',
            '岗位名称': 'Python开发工程师',
            '薪资范围起': 8000,
            '薪资范围止': 12000,
            '工作地点': '北京市朝阳区',
            '学历要求': '本科',
            '工作经验': '1-3年',
            '工作职责': '负责Python后端开发',
            '任职要求': '熟悉Python、Django等技术',
            '所属区域': '北京市朝阳区'
        },
        {
            '企业名称': '测试公司B',
            '岗位名称': 'Java开发工程师',
            '薪资范围起': 10000,
            '薪资范围止': 15000,
            '工作地点': '上海市浦东新区',
            '学历要求': '本科',
            '工作经验': '2-5年',
            '工作职责': '负责Java后端开发',
            '任职要求': '熟悉Java、Spring等技术',
            '所属区域': '上海市浦东新区'
        }
    ]
    
    # 创建爬虫实例
    scraper = Enhanced58JobScraper()
    
    # 测试文件名
    test_excel_file = "测试职位数据.xlsx"
    test_json_file = "测试职位数据.json"
    
    # 清理之前的测试文件
    for file in [test_excel_file, test_json_file]:
        if os.path.exists(file):
            os.remove(file)
            print(f"已删除旧的测试文件: {file}")
    
    print("\n=== 测试批量保存功能 ===")
    # 测试save_to_excel方法（应该同时生成JSON）
    result = scraper.save_to_excel(test_data, test_excel_file)
    
    if result:
        print(f"✓ Excel文件已创建: {test_excel_file}")
        print(f"✓ JSON文件应该已创建: {test_json_file}")
        
        # 验证文件是否存在
        if os.path.exists(test_excel_file):
            print(f"✓ 确认Excel文件存在")
        else:
            print(f"✗ Excel文件不存在")
            
        if os.path.exists(test_json_file):
            print(f"✓ 确认JSON文件存在")
            
            # 读取并验证JSON内容
            with open(test_json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            print(f"✓ JSON文件包含 {len(json_data)} 条记录")
            print(f"✓ 第一条记录: {json_data[0]['企业名称']} - {json_data[0]['岗位名称']}")
        else:
            print(f"✗ JSON文件不存在")
    
    print("\n=== 测试单条保存功能 ===")
    # 测试save_single_job_to_excel方法（应该同时更新JSON）
    additional_job = {
        '企业名称': '测试公司C',
        '岗位名称': 'React前端工程师',
        '薪资范围起': 9000,
        '薪资范围止': 14000,
        '工作地点': '深圳市南山区',
        '学历要求': '本科',
        '工作经验': '1-3年',
        '工作职责': '负责React前端开发',
        '任职要求': '熟悉React、Vue等技术',
        '所属区域': '深圳市南山区'
    }
    
    scraper.save_single_job_to_excel(additional_job, test_excel_file)
    
    # 验证更新后的文件
    if os.path.exists(test_json_file):
        with open(test_json_file, 'r', encoding='utf-8') as f:
            updated_json_data = json.load(f)
        print(f"✓ 更新后JSON文件包含 {len(updated_json_data)} 条记录")
        print(f"✓ 最后一条记录: {updated_json_data[-1]['企业名称']} - {updated_json_data[-1]['岗位名称']}")
    
    # 清理测试文件
    for file in [test_excel_file, test_json_file]:
        if os.path.exists(file):
            os.remove(file)
            print(f"已清理测试文件: {file}")
    
    print("\n=== 测试完成 ===")
    scraper.close()

if __name__ == "__main__":
    test_json_export()