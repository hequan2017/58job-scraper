from enhanced_job_scraper import Enhanced58JobScraper
import time

def test_url_generation():
    """测试URL生成逻辑"""
    print("=== 测试URL生成逻辑 ===")
    
    scraper = Enhanced58JobScraper(headless=True)
    
    try:
        # 测试北京的URL生成
        base_url = "https://bj.58.com/hulianwangtx/"
        print(f"\n测试基础URL: {base_url}")
        
        # 先测试2页URL
        print("\n=== 测试生成2页URL ===")
        urls = scraper.generate_page_urls(base_url, max_pages=2)
        
        print(f"\n生成的URL列表:")
        for i, url in enumerate(urls, 1):
            print(f"第{i}页: {url}")
        
        # 检查是否有重复URL
        unique_urls = set(urls)
        if len(urls) == len(unique_urls):
            print("\n✓ URL生成正确，没有重复")
        else:
            print("\n✗ 发现重复URL:")
            for url in urls:
                if urls.count(url) > 1:
                    print(f"  重复URL: {url}")
        
        print(f"\n总共生成 {len(urls)} 个URL")
        
        # 检查PID是否不同
        if len(urls) >= 2:
            url1_pid = None
            url2_pid = None
            
            if len(urls) > 0 and 'pid=' in urls[0]:
                url1_pid = urls[0].split('pid=')[1].split('&')[0] if '&' in urls[0].split('pid=')[1] else urls[0].split('pid=')[1]
            if len(urls) > 1 and 'pid=' in urls[1]:
                url2_pid = urls[1].split('pid=')[1].split('&')[0] if '&' in urls[1].split('pid=')[1] else urls[1].split('pid=')[1]
            
            print(f"\n第1页PID: {url1_pid if url1_pid else '无'}")
            print(f"第2页PID: {url2_pid if url2_pid else '无'}")
            
            if url1_pid and url2_pid and url1_pid != url2_pid:
                print("\n✓ PID参数不同，修复成功！")
            elif url1_pid == url2_pid:
                print("\n✗ PID参数相同，仍需修复")
            elif not url1_pid and url2_pid:
                print("\n✓ 第1页无PID，第2页有PID，这是正常的！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.close()
        except:
            pass

if __name__ == "__main__":
    test_url_generation()