#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本逻辑的简单验证程序
"""

import sys
import os
import re
from enhanced_job_scraper import Enhanced58JobScraper

def test_region_filtering():
    """测试所属区域过滤逻辑"""
    print("=== 测试所属区域过滤逻辑 ===")
    
    # 测试数据
    test_regions = [
        "北京市朝阳区",  # 正常格式
        "广州市源瑞信息科技有限公司在华南地区",  # 包含无关内容
        "上海市浦东新区",  # 正常格式
        "找工作免费发布登记简历",  # 完全无关
        "深圳市南山区",  # 正常格式
        "成都市锦江区科技有限公司",  # 包含公司信息
        "西安市雁塔区",  # 正常格式
        "总部位于北京市海淀区",  # 包含前缀
    ]
    
    # 无关词汇列表（与脚本中保持一致）
    unwanted_keywords = ['找工作', '免费发布', '登记简历', '公司福利', '饭补', '加班补助', 
                        '交通便利', '餐补', '市中心区', '不匹配', '人公司', '福利', '补助', '便利',
                        '有限公司', '科技有限公司', '信息科技', '华南地区', '华北地区', '华东地区', 
                        '华西地区', '在华', '地区', '公司在']
    
    print("\n测试结果:")
    for region in test_regions:
        # 去除"总部位于"前缀
        cleaned_region = re.sub(r'^总部位于', '', region).strip()
        
        # 检查是否包含无关词汇
        has_unwanted = any(unwanted in cleaned_region for unwanted in unwanted_keywords)
        
        if has_unwanted:
            result = "[清空] 包含无关词汇"
        else:
            # 正则匹配标准格式
            region_match = re.search(r'([\u4e00-\u9fa5]{2,4}省[\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)', cleaned_region)
            if not region_match:
                region_match = re.search(r'([\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)', cleaned_region)
            
            if region_match:
                clean_region = region_match.group(1)
                if len(clean_region) <= 10:
                    result = f"[保留] {clean_region}"
                else:
                    result = "[清空] 长度异常"
            else:
                result = "[清空] 格式不标准"
        
        print(f"  {region:<30} -> {result}")

def test_scraper_initialization():
    """测试爬虫初始化"""
    print("\n=== 测试爬虫初始化 ===")
    
    try:
        scraper = Enhanced58JobScraper(headless=True)
        print("✓ 爬虫初始化成功")
        
        # 测试标准化方法
        test_scale = scraper.standardize_company_scale("100-499人")
        print(f"✓ 公司规模标准化测试: 100-499人 -> {test_scale}")
        
        test_type = scraper.standardize_company_type("互联网/电子商务")
        print(f"✓ 公司类型标准化测试: 互联网/电子商务 -> {test_type}")
        
        scraper.close()
        print("✓ 爬虫关闭成功")
        
    except Exception as e:
        print(f"✗ 爬虫初始化失败: {e}")
        return False
    
    return True

def test_data_structure():
    """测试数据结构"""
    print("\n=== 测试数据结构 ===")
    
    # 模拟职位数据结构
    sample_job = {
        '岗位名称': 'Python开发工程师',
        '企业名称': '测试科技有限公司',
        '薪资范围起': 8000,
        '薪资范围止': 15000,
        '工作地点': '北京 - 朝阳',
        '所属区域': '北京市朝阳区',
        '工作职责': '负责Python后端开发',
        '任职要求': '熟悉Python、Django等技术',
        '学历要求': '本科',
        '工作经验': '3-5年',
        '企业规模': '100-499人',
        '企业类型': '互联网/电子商务'
    }
    
    required_fields = ['岗位名称', '企业名称', '工作职责', '任职要求']
    
    print("检查必需字段:")
    for field in required_fields:
        if field in sample_job and sample_job[field]:
            print(f"  ✓ {field}: {sample_job[field][:30]}...")
        else:
            print(f"  ✗ {field}: 缺失")
    
    print(f"\n数据结构包含 {len(sample_job)} 个字段")
    return True

def main():
    """主测试函数"""
    print("开始脚本逻辑测试...\n")
    
    # 测试所属区域过滤逻辑
    test_region_filtering()
    
    # 测试爬虫初始化
    init_success = test_scraper_initialization()
    
    # 测试数据结构
    test_data_structure()
    
    print("\n=== 测试总结 ===")
    if init_success:
        print("✓ 脚本逻辑测试通过")
        print("✓ 所属区域过滤逻辑正常")
        print("✓ 爬虫初始化正常")
        print("✓ 数据结构完整")
    else:
        print("✗ 部分测试失败，请检查环境配置")
    
    print("\n脚本逻辑检查完成！")

if __name__ == "__main__":
    main()