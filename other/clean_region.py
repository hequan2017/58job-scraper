import pandas as pd
import re

# 读取Excel文件
df = pd.read_excel('58同城多城市职位详细信息.xlsx')

print('当前所属区域样本:')
samples = df['所属区域'].dropna().head(10)
for i, region in enumerate(samples):
    print(f'{i+1}. {region}')

print('\n清理后效果预览:')
for region in samples:
    # 提取XX市XX区格式
    region_str = str(region)
    # 查找第一个完整的"XX市XX区"模式（非贪婪匹配）
    match = re.search(r'([\u4e00-\u9fa5]{2,}?市[\u4e00-\u9fa5]{2,}?区)', region_str)
    result = match.group(1) if match else region
    print(f'{region} -> {result}')

# 清理整个数据集
print('\n开始清理整个数据集...')
original_count = len(df)
cleaned_count = 0

for index, row in df.iterrows():
    if pd.notna(row['所属区域']):
        original_region = row['所属区域']
        # 提取XX市XX区格式
        region_str = str(original_region)
        # 查找第一个完整的"XX市XX区"模式（非贪婪匹配）
        match = re.search(r'([\u4e00-\u9fa5]{2,}?市[\u4e00-\u9fa5]{2,}?区)', region_str)
        if match:
            clean_region = match.group(1)
            if clean_region != original_region:
                df.at[index, '所属区域'] = clean_region
                cleaned_count += 1
                print(f'✓ 清理: {original_region} -> {clean_region}')

print(f'\n清理完成！共处理 {original_count} 条记录，清理了 {cleaned_count} 条所属区域数据')

# 保存清理后的数据
df.to_excel('58同城多城市职位详细信息.xlsx', index=False)
print('数据已保存到Excel文件')

# 显示清理后的样本
print('\n清理后的所属区域样本:')
for i, region in enumerate(df['所属区域'].dropna().head(10)):
    print(f'{i+1}. {region}')