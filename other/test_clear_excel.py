import pandas as pd
import os
from enhanced_job_scraper import Enhanced58JobScraper

def test_clear_excel():
    filename = "58同城多城市职位详细信息.xlsx"
    
    print(f"测试清空Excel数据功能")
    print(f"目标文件: {filename}")
    
    # 检查文件是否存在
    if os.path.exists(filename):
        print(f"文件存在，当前大小: {os.path.getsize(filename)} 字节")
        
        # 读取现有数据
        try:
            df = pd.read_excel(filename)
            print(f"当前数据行数: {len(df)}")
            print(f"当前列数: {len(df.columns)}")
            print(f"列名: {list(df.columns)}")
        except Exception as e:
            print(f"读取文件失败: {e}")
    else:
        print("文件不存在")
    
    # 创建爬虫实例并测试清空功能
    scraper = Enhanced58JobScraper(headless=True)
    
    print("\n开始清空Excel数据...")
    scraper.clear_excel_data(filename)
    
    # 检查清空后的状态
    if os.path.exists(filename):
        print(f"\n清空后文件大小: {os.path.getsize(filename)} 字节")
        
        try:
            df = pd.read_excel(filename)
            print(f"清空后数据行数: {len(df)}")
            print(f"清空后列数: {len(df.columns)}")
            print(f"列名: {list(df.columns)}")
        except Exception as e:
            print(f"读取清空后文件失败: {e}")
    else:
        print("清空后文件不存在")
    
    scraper.close()
    print("\n测试完成")

if __name__ == "__main__":
    test_clear_excel()