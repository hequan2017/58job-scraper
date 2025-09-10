import pandas as pd
import re

# 读取Excel文件
df = pd.read_excel('58同城多城市职位详细信息.xlsx')

print('当前所属区域样本:')
samples = df['所属区域'].dropna().head(20)
for i, region in enumerate(samples):
    print(f'{i+1}. {region}')

print('\n清理后效果预览:')
for region in samples:
    region_str = str(region)
    
    # 过滤掉包含无关词汇的内容
    unwanted_keywords = ['找工作', '免费发布', '登记简历', '公司福利', '饭补', '加班补助', 
                       '交通便利', '餐补', '市中心区', '不匹配', '人公司', '福利', '补助', '便利',
                       '有限公司', '科技有限公司', '信息科技', '华南地区', '华北地区', '华东地区', 
                       '华西地区', '在华', '地区', '公司在', '注册地位于', '注册地址', '营业执照', '工商注册']
    
    if any(unwanted in region_str for unwanted in unwanted_keywords):
        result = ''  # 如果包含无关词汇，清空
        print(f'{region} -> [已清空-包含无关内容]')
    else:
        # 优先查找"XX省XX市XX区"格式，然后查找"XX市XX区"格式（非贪婪匹配）
        region_match = re.search(r'([\u4e00-\u9fa5]{2,4}省[\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)', region_str)
        if not region_match:
            region_match = re.search(r'([\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)', region_str)
        
        if region_match:
            result = region_match.group(1)
            # 确保长度合理
            if len(result) > 10:
                result = ''
                print(f'{region} -> [已清空-长度异常]')
            else:
                print(f'{region} -> {result}')
        else:
            result = ''
            print(f'{region} -> [已清空-格式不标准]')

# 清理整个数据集
print('\n开始清理整个数据集...')
original_count = len(df)
cleaned_count = 0
cleared_count = 0

for index, row in df.iterrows():
    if pd.notna(row['所属区域']):
        original_region = row['所属区域']
        region_str = str(original_region)
        
        # 过滤掉包含无关词汇的内容
        unwanted_keywords = ['找工作', '免费发布', '登记简历', '公司福利', '饭补', '加班补助', 
                           '交通便利', '餐补', '市中心区', '不匹配', '人公司', '福利', '补助', '便利',
                           '有限公司', '科技有限公司', '信息科技', '华南地区', '华北地区', '华东地区', 
                           '华西地区', '在华', '地区', '公司在', '注册地位于', '注册地址', '营业执照', '工商注册']
        
        if any(unwanted in region_str for unwanted in unwanted_keywords):
            df.at[index, '所属区域'] = ''  # 清空包含无关词汇的内容
            cleared_count += 1
            print(f'× 清空无关内容: {original_region}')
        else:
            # 优先查找"XX省XX市XX区"格式，然后查找"XX市XX区"格式（非贪婪匹配）
            region_match = re.search(r'([\u4e00-\u9fa5]{2,4}省[\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)', region_str)
            if not region_match:
                region_match = re.search(r'([\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)', region_str)
            
            if region_match:
                clean_region = region_match.group(1)
                # 确保长度合理
                if len(clean_region) <= 10:
                    if clean_region != original_region:
                        df.at[index, '所属区域'] = clean_region
                        cleaned_count += 1
                        print(f'✓ 清理: {original_region} -> {clean_region}')
                else:
                    df.at[index, '所属区域'] = ''
                    cleared_count += 1
                    print(f'× 清空长度异常: {original_region}')
            else:
                df.at[index, '所属区域'] = ''
                cleared_count += 1
                print(f'× 清空格式不标准: {original_region}')

print(f'\n清理完成！')
print(f'共处理 {original_count} 条记录')
print(f'清理了 {cleaned_count} 条所属区域数据')
print(f'清空了 {cleared_count} 条无效数据')

# 保存清理后的数据
df.to_excel('58同城多城市职位详细信息.xlsx', index=False)
print('数据已保存到Excel文件')

# 显示清理后的样本
print('\n清理后的所属区域样本:')
valid_regions = df['所属区域'].dropna()
valid_regions = valid_regions[valid_regions != '']
for i, region in enumerate(valid_regions.head(10)):
    print(f'{i+1}. {region}')

print(f'\n有效所属区域数量: {len(valid_regions)}')
print(f'空白所属区域数量: {len(df) - len(valid_regions)}')