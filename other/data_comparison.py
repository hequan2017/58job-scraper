import pandas as pd
import json
import os

def compare_excel_json_data(excel_file, json_file):
    """
    对比Excel文件和JSON文件的数据是否一致
    
    Args:
        excel_file (str): Excel文件路径
        json_file (str): JSON文件路径
    """
    print("=" * 60)
    print("Excel与JSON数据一致性检查")
    print("=" * 60)
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        print(f"错误：Excel文件 {excel_file} 不存在")
        return False
    
    if not os.path.exists(json_file):
        print(f"错误：JSON文件 {json_file} 不存在")
        return False
    
    try:
        # 读取Excel文件
        print(f"正在读取Excel文件: {excel_file}")
        excel_df = pd.read_excel(excel_file)
        excel_df = excel_df.fillna('')  # 处理NaN值
        excel_data = excel_df.to_dict('records')
        
        # 读取JSON文件
        print(f"正在读取JSON文件: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # 基本信息对比
        print(f"\n基本信息对比:")
        print(f"  Excel数据条数: {len(excel_data)}")
        print(f"  JSON数据条数: {len(json_data)}")
        print(f"  Excel列数: {len(excel_df.columns)}")
        print(f"  JSON字段数(第一条): {len(json_data[0]) if json_data else 0}")
        
        # 检查数据条数是否一致
        if len(excel_data) != len(json_data):
            print(f"\n❌ 数据条数不一致！")
            return False
        
        # 检查列名/字段名是否一致
        excel_columns = set(excel_df.columns)
        json_keys = set(json_data[0].keys()) if json_data else set()
        
        print(f"\n字段名对比:")
        print(f"  Excel列名: {sorted(excel_columns)}")
        print(f"  JSON字段名: {sorted(json_keys)}")
        
        if excel_columns != json_keys:
            print(f"\n❌ 字段名不一致！")
            missing_in_json = excel_columns - json_keys
            missing_in_excel = json_keys - excel_columns
            if missing_in_json:
                print(f"  JSON中缺少的字段: {missing_in_json}")
            if missing_in_excel:
                print(f"  Excel中缺少的字段: {missing_in_excel}")
            return False
        
        # 逐条对比数据内容
        print(f"\n正在逐条对比数据内容...")
        differences = []
        
        for i, (excel_row, json_row) in enumerate(zip(excel_data, json_data)):
            row_differences = []
            
            for column in excel_columns:
                excel_value = excel_row.get(column, '')
                json_value = json_row.get(column, '')
                
                # 处理数据类型差异（如数字转字符串等）
                excel_str = str(excel_value).strip() if excel_value != '' else ''
                json_str = str(json_value).strip() if json_value != '' else ''
                
                if excel_str != json_str:
                    row_differences.append({
                        'column': column,
                        'excel_value': excel_value,
                        'json_value': json_value
                    })
            
            if row_differences:
                differences.append({
                    'row_index': i,
                    'differences': row_differences
                })
        
        # 输出对比结果
        if not differences:
            print(f"✅ 数据内容完全一致！")
            print(f"  - 共对比了 {len(excel_data)} 条数据")
            print(f"  - 所有字段值都匹配")
            return True
        else:
            print(f"❌ 发现数据差异！")
            print(f"  - 总数据条数: {len(excel_data)}")
            print(f"  - 有差异的行数: {len(differences)}")
            
            # 显示前5个差异
            print(f"\n前5个差异详情:")
            for i, diff in enumerate(differences[:5]):
                print(f"\n第{diff['row_index']+1}行差异:")
                for field_diff in diff['differences'][:3]:  # 每行最多显示3个字段差异
                    print(f"  字段 '{field_diff['column']}':")
                    print(f"    Excel: {repr(field_diff['excel_value'])}")
                    print(f"    JSON:  {repr(field_diff['json_value'])}")
            
            if len(differences) > 5:
                print(f"\n... 还有 {len(differences) - 5} 行存在差异")
            
            return False
    
    except Exception as e:
        print(f"对比过程中发生错误: {e}")
        return False

def main():
    """
    主函数
    """
    excel_file = "58同城多城市职位详细信息.xlsx"
    json_file = "58同城多城市职位详细信息.json"
    
    # 执行对比
    is_consistent = compare_excel_json_data(excel_file, json_file)
    
    print("\n" + "=" * 60)
    if is_consistent:
        print("结论: Excel和JSON数据完全一致 ✅")
    else:
        print("结论: Excel和JSON数据存在差异 ❌")
    print("=" * 60)

if __name__ == "__main__":
    main()