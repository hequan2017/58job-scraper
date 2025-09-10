import json

with open('58同城多城市职位详细信息.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
print(f'JSON总条数: {len(data)}')
print(f'JSON字段数: {len(data[0]) if data else 0}')
if data:
    print(f'第一条数据的字段: {list(data[0].keys())}')