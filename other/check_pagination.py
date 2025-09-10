import requests
from bs4 import BeautifulSoup
import re

def check_pagination():
    url = 'https://bj.58.com/hulianwangtx/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f'状态码: {response.status_code}')
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找分页区域
        pagination = soup.find('div', class_='pagesout')
        if pagination:
            print('找到分页区域:')
            print(pagination.prettify())
            
            # 提取所有链接
            links = pagination.find_all('a', href=True)
            print('\n分页链接:')
            for link in links:
                href = link.get('href')
                text = link.get_text().strip()
                print(f'  文本: "{text}" -> 链接: {href}')
        else:
            print('未找到分页区域')
            
        # 查找所有包含pn的链接
        all_links = soup.find_all('a', href=True)
        pn_links = [link for link in all_links if 'pn' in link.get('href', '')]
        
        print('\n所有包含pn的链接:')
        for link in pn_links[:10]:  # 只显示前10个
            href = link.get('href')
            text = link.get_text().strip()
            print(f'  "{text}" -> {href}')
            
    except Exception as e:
        print(f'请求失败: {e}')

if __name__ == '__main__':
    check_pagination()