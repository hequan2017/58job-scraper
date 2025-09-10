import re

# 测试字符串
test_cases = [
    '公司相册企业未添加相册公司地址企业未添加地址广东省佛山市顺德区',
    '北京市房山区阳光北大街北京市房山区',
    '天津市西青区大寺镇王庄子村赤龙澜园小区',
    '公司位于郑州市上街区高科技孵化园区',
    '广东省深圳市南山区'
]

print('测试地址清理效果:')
print('=' * 50)

for test_str in test_cases:
    print(f'原始: {test_str}')
    
    # 优先查找"XX省XX市XX区"格式，然后查找"XX市XX区"格式（非贪婪匹配）
    region_match = re.search(r'([\u4e00-\u9fa5]{2,}?省[\u4e00-\u9fa5]{2,}?市[\u4e00-\u9fa5]{2,}?区)', test_str)
    if not region_match:
        region_match = re.search(r'([\u4e00-\u9fa5]{2,}?市[\u4e00-\u9fa5]{2,}?区)', test_str)
    
    if region_match:
        result = region_match.group(1)
        # 进一步检查结果是否包含无关词汇，如果包含则尝试更精确的匹配
        unwanted_words = ['公司', '企业', '地址', '相册', '未添加', '位于']
        if any(word in result for word in unwanted_words):
            # 尝试更精确的匹配，只匹配末尾的省市区
            precise_match = re.search(r'([\u4e00-\u9fa5]{2,4}省[\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)$', test_str)
            if not precise_match:
                precise_match = re.search(r'([\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)$', test_str)
            result = precise_match.group(1) if precise_match else result
    else:
        result = test_str
    print(f'清理: {result}')
    print('-' * 30)