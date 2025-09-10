from enhanced_job_scraper import Enhanced58JobScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_find_page3():
    print("=== 测试从第2页查找第3页链接 ===")
    
    # 创建爬虫实例
    scraper = Enhanced58JobScraper(headless=False)  # 使用可视化模式便于调试
    
    try:
        # 第2页URL
        page2_url = "https://bj.58.com/hulianwangtx/pn2/?pid=864205153882931200&PGTID=0d365063-0000-14e6-127f-56086578ded1&ClickID=1"
        print(f"\n访问第2页: {page2_url}")
        
        # 访问第2页
        scraper.driver.get(page2_url)
        time.sleep(3)
        
        # 查找分页区域
        try:
            pagination = WebDriverWait(scraper.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pager, .page-wrap, .pagination, [class*='page'], [class*='pager']"))
            )
            print("\n找到分页区域")
            
            # 查找第3页链接
            page3_links = scraper.driver.find_elements(By.XPATH, "//a[contains(text(), '3') or @title='3' or contains(@href, 'pn3')]")
            
            if page3_links:
                print(f"\n找到 {len(page3_links)} 个第3页相关链接")
                for i, link in enumerate(page3_links):
                    page3_url = link.get_attribute('href')
                    link_text = link.text.strip()
                    print(f"链接{i+1}: 文本='{link_text}', URL={page3_url}")
                    
                    if page3_url and 'pid=' in page3_url:
                        page3_pid = page3_url.split('pid=')[1].split('&')[0] if '&' in page3_url.split('pid=')[1] else page3_url.split('pid=')[1]
                        print(f"  -> PID: {page3_pid}")
                    elif page3_url:
                        print(f"  -> 无PID参数")
                    else:
                        print(f"  -> URL为空")
                    
            else:
                print("\n未找到第3页链接，查找下一页链接")
                next_links = scraper.driver.find_elements(By.XPATH, "//a[contains(text(), '下一页') or contains(text(), 'next') or contains(@class, 'next')]")
                
                if next_links:
                    next_url = next_links[0].get_attribute('href')
                    print(f"找到下一页链接: {next_url}")
                    
                    # 提取PID参数
                    if 'pid=' in next_url:
                        next_pid = next_url.split('pid=')[1].split('&')[0] if '&' in next_url.split('pid=')[1] else next_url.split('pid=')[1]
                        print(f"下一页PID: {next_pid}")
                else:
                    print("未找到下一页链接")
                    
            # 显示所有分页链接
            print("\n=== 所有分页链接 ===")
            all_page_links = scraper.driver.find_elements(By.XPATH, "//a[contains(@href, 'pn') or contains(text(), '页') or contains(text(), 'next') or contains(text(), 'prev')]")
            for i, link in enumerate(all_page_links[:10]):  # 只显示前10个
                href = link.get_attribute('href')
                text = link.text.strip()
                print(f"{i+1}. 文本: '{text}' -> {href}")
                
        except Exception as e:
            print(f"查找分页区域失败: {e}")
            
        # 等待用户观察
        input("\n按回车键继续...")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.close()
        except:
            pass

if __name__ == "__main__":
    test_find_page3()