#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按照指定格式将Excel文件转换为JSON格式
"""

import pandas as pd
import json
import os
from datetime import datetime

def excel_to_custom_json(excel_file, json_file=None):
    """
    按照用户指定格式将Excel文件转换为JSON格式
    
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
        
        # 处理数据格式
        data_list = []
        
        for index, row in df.iterrows():
            # 根据工作地点推断抓取城市
            work_location = str(row.get('工作地点', '')).strip()
            city = ""
            if work_location:
                if '北京' in work_location:
                    city = "北京"
                elif '上海' in work_location:
                    city = "上海"
                elif '广州' in work_location:
                    city = "广州"
                elif '深圳' in work_location:
                    city = "深圳"
                elif '杭州' in work_location:
                    city = "杭州"
                elif '成都' in work_location:
                    city = "成都"
                elif '武汉' in work_location:
                    city = "武汉"
                elif '西安' in work_location:
                    city = "西安"
                elif '南京' in work_location:
                    city = "南京"
                elif '天津' in work_location:
                    city = "天津"
                elif '重庆' in work_location:
                    city = "重庆"
                elif '苏州' in work_location:
                    city = "苏州"
                elif '长沙' in work_location:
                    city = "长沙"
                elif '郑州' in work_location:
                    city = "郑州"
                elif '青岛' in work_location:
                    city = "青岛"
                else:
                    # 尝试从工作地点提取城市名
                    parts = work_location.split(' - ')
                    if len(parts) > 0:
                        city = parts[0].strip()
            
            # 构建记录
            record = {
                "企业名称": str(row.get('企业名称', '')).strip(),
                "企业类型": str(row.get('企业类型', '')).strip(),
                "社会信用码": str(row.get('社会信用码', '')).strip(),
                "企业规模": str(row.get('企业规模', '')).strip(),
                "注册资本(万)": str(row.get('注册资本(万)', '')).strip(),
                "所属区域": str(row.get('所属区域', '')).strip(),
                "联系人": str(row.get('联系人', '')).strip(),
                "联系方式": str(row.get('联系方式', '')).strip(),
                "联系邮箱": str(row.get('联系邮箱', '')).strip(),
                "办公地址": str(row.get('办公地址', '')).strip(),
                "企业简介": str(row.get('企业简介', '')).strip(),
                "营业执照": str(row.get('营业执照', '')).strip(),
                "企业相册": str(row.get('企业相册', '')).strip(),
                "岗位名称": str(row.get('岗位名称', '')).strip(),
                "薪资类型": str(row.get('薪资类型', '')).strip(),
                "薪资范围起": str(row.get('薪资范围起', '')).strip(),
                "薪资范围至": str(row.get('薪资范围至', '')).strip(),
                "工作地点": str(row.get('工作地点', '')).strip(),
                "岗位要求": str(row.get('岗位要求', '')).strip(),
                "学历要求": str(row.get('学历要求', '')).strip(),
                "招聘人数": int(row.get('招聘人数', 0)) if pd.notna(row.get('招聘人数')) else 1,
                "发布时间": str(row.get('发布时间', '')).strip(),
                "结束时间": str(row.get('结束时间', '')).strip(),
                "工作职责": str(row.get('工作职责', '')).strip(),
                "任职要求": str(row.get('任职要求', '')).strip(),
                "抓取城市": city
            }
            
            # 清理空值，将'nan'、'NaN'等转换为空字符串
            for key, value in record.items():
                if key == "招聘人数":
                    continue  # 保持数字类型
                if pd.isna(value) or str(value).lower() in ['nan', 'none', 'null']:
                    record[key] = ""
                elif isinstance(value, str):
                    record[key] = value.replace('nan', '').replace('NaN', '').strip()
            
            data_list.append(record)
        
        # 如果没有指定JSON文件名，自动生成
        if json_file is None:
            base_name = os.path.splitext(excel_file)[0]
            json_file = f"{base_name}_custom_format.json"
        
        print(f"正在写入JSON文件: {json_file}")
        
        # 写入JSON文件
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 转换完成！")
        print(f"📊 总记录数: {len(data_list)}")
        print(f"📁 输出文件: {json_file}")
        
        # 显示前2条记录作为预览
        if data_list:
            print("\n📋 数据预览（前2条记录）:")
            for i, record in enumerate(data_list[:2], 1):
                print(f"\n记录 {i}:")
                print(f"  企业名称: {record['企业名称']}")
                print(f"  岗位名称: {record['岗位名称']}")
                print(f"  工作地点: {record['工作地点']}")
                print(f"  抓取城市: {record['抓取城市']}")
                print(f"  薪资范围: {record['薪资范围起']}-{record['薪资范围至']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    主函数
    """
    # Excel文件路径
    excel_file = "315个.xlsx"
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        print(f"错误：找不到Excel文件 - {excel_file}")
        print("请确保文件在当前目录下")
        return
    
    # 执行转换
    success = excel_to_custom_json(excel_file, "315个_custom.json")
    
    if success:
        print("\n🎉 Excel到自定义JSON格式转换成功完成！")
        print("格式特点：")
        print("- 所有字段都是字符串格式（除招聘人数为数字）")
        print("- 添加了'抓取城市'字段")
        print("- 清理了NaN和空值")
    else:
        print("\n❌ 转换过程中出现错误")

if __name__ == "__main__":
    main()