import pandas as pd
import json

# 要删除的公司名称
company_to_remove = '广东天杰国际人才科技有限公司'

# 读取Excel文件
print("正在读取Excel文件...")
df = pd.read_excel('58同城多城市职位详细信息.xlsx')
print(f"原始数据总记录数: {len(df)}")

# 检查是否存在该公司的记录
tianjie_data = df[df['企业名称'] == company_to_remove]
print(f"\n{company_to_remove}的记录数: {len(tianjie_data)}")

if len(tianjie_data) > 0:
    print("\n具体记录:")
    print(tianjie_data[['岗位名称', '所属区域', '薪资范围起', '薪资范围至']].to_string())
    
    # 删除该公司的记录
    df_filtered = df[df['企业名称'] != company_to_remove]
    print(f"\n删除后数据记录数: {len(df_filtered)}")
    
    # 保存更新后的Excel文件
    df_filtered.to_excel('58同城多城市职位详细信息.xlsx', index=False)
    print("Excel文件已更新")
    
    # 读取JSON文件
    print("\n正在读取JSON文件...")
    with open('58同城多城市职位详细信息.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    print(f"原始JSON数据记录数: {len(json_data)}")
    
    # 删除JSON中该公司的记录
    json_filtered = [record for record in json_data if record.get('企业名称') != company_to_remove]
    print(f"删除后JSON数据记录数: {len(json_filtered)}")
    
    # 保存更新后的JSON文件
    with open('58同城多城市职位详细信息.json', 'w', encoding='utf-8') as f:
        json.dump(json_filtered, f, ensure_ascii=False, indent=2)
    print("JSON文件已更新")
    
    print(f"\n✅ 成功删除 {company_to_remove} 的所有记录")
else:
    print(f"\n❌ 未找到 {company_to_remove} 的记录")