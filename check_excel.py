import pandas as pd

try:
    df = pd.read_excel('58同城多城市职位详细信息.xlsx')
    print(f'行数: {len(df)}')
    print(f'列数: {len(df.columns)}')
    print('列名:')
    print(df.columns.tolist())
    if len(df) > 0:
        print('前几行数据:')
        print(df.head())
    else:
        print('Excel文件只有表头，没有数据行')
except Exception as e:
    print(f'读取Excel文件时出错: {e}')