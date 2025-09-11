import time
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import re
import logging
import os
import sys

# 配置日志
def setup_logging():
    # 确保log目录存在
    if not os.path.exists('log'):
        os.makedirs('log')
    
    # 生成时间戳文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'log/{timestamp}.log'
    
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_filename

# 重写print函数，同时输出到控制台和日志
def log_print(*args, **kwargs):
    message = ' '.join(str(arg) for arg in args)
    logging.info(message)

# 错误日志打印函数（红色显示）
def log_error(*args, **kwargs):
    message = ' '.join(str(arg) for arg in args)
    logging.error(message)
    # 在控制台打印红色文字
    print(f"\033[91m{message}\033[0m")

# 设置日志
log_filename = setup_logging()
print(f"日志将保存到: {log_filename}")

# 替换print函数
original_print = print
print = log_print

class Enhanced58JobScraper:
    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-plugins")
        self.options.add_argument("--disable-images")
        # 禁用GPU相关错误信息
        self.options.add_argument("--disable-gpu-sandbox")
        self.options.add_argument("--disable-software-rasterizer")
        self.options.add_argument("--disable-background-timer-throttling")
        self.options.add_argument("--disable-backgrounding-occluded-windows")
        self.options.add_argument("--disable-renderer-backgrounding")
        self.options.add_argument("--disable-features=TranslateUI")
        self.options.add_argument("--disable-ipc-flooding-protection")
        # 禁用WebGL相关错误
        self.options.add_argument("--disable-webgl")
        self.options.add_argument("--disable-webgl2")
        # 设置日志级别来减少错误输出
        self.options.add_argument("--log-level=3")
        self.options.add_argument("--silent")
        self.options.add_argument("--disable-logging")
        self.options.add_argument("--disable-dev-tools")
        # self.options.add_argument("--disable-javascript")  # 注释掉，因为很多网站需要JavaScript
        self.options.add_argument("--window-size=1920,1080")
        # 添加更多性能优化选项
        self.options.add_argument("--disable-web-security")
        self.options.add_argument("--disable-features=VizDisplayCompositor")
        self.options.add_argument("--disable-background-timer-throttling")
        self.options.add_argument("--disable-renderer-backgrounding")
        self.options.add_argument("--disable-backgrounding-occluded-windows")
        self.options.add_argument("--disable-ipc-flooding-protection")
        # 禁用CSS和字体加载以提高速度
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2
        }
        self.options.add_experimental_option("prefs", prefs)
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # 尝试使用系统PATH中的ChromeDriver，如果失败则使用webdriver-manager
        try:
            self.driver = webdriver.Chrome(options=self.options)
        except Exception as e:
            print(f"使用系统ChromeDriver失败，尝试使用webdriver-manager: {e}")
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=self.options)
            except Exception as e2:
                print(f"webdriver-manager也失败了: {e2}")
                raise e2
        
        # 设置页面加载超时
        self.driver.set_page_load_timeout(15)  # 减少页面加载超时时间
        self.driver.implicitly_wait(5)  # 减少隐式等待时间
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def handle_captcha(self, max_retries=3):
        """自动处理验证码页面"""
        for attempt in range(max_retries):
            try:
                print(f"\n尝试自动处理验证码 (第{attempt + 1}次)...")
                
                # 尝试查找并点击跳过按钮或验证按钮
                skip_buttons = [
                    "//input[@id='btnSubmit']",  # 58同城验证码页面的特定按钮
                    "//button[@id='btnSubmit']",
                    "//input[@class='btn_tj']",
                    "//button[@class='btn_tj']",
                    "//input[@value='点击按钮进行验证']",
                    "//button[contains(text(), '跳过')]",
                    "//a[contains(text(), '跳过')]",
                    "//span[contains(text(), '跳过')]",
                    "//div[contains(text(), '跳过')]",
                    "//button[contains(@class, 'skip')]",
                    "//a[contains(@class, 'skip')]",
                    "//button[contains(text(), '继续访问')]",
                    "//a[contains(text(), '继续访问')]",
                    "//button[contains(text(), '返回')]",
                    "//a[contains(text(), '返回')]",
                    "//button[contains(text(), '确定')]",
                    "//a[contains(text(), '确定')]",
                    "//button[contains(text(), '点击按钮进行验证')]",
                    "//a[contains(text(), '点击按钮进行验证')]",
                    "//button[contains(text(), '进行验证')]",
                    "//a[contains(text(), '进行验证')]",
                    "//button[contains(text(), '验证')]",
                    "//a[contains(text(), '验证')]",
                    "//button[contains(@class, 'verify')]",
                    "//a[contains(@class, 'verify')]",
                    "//button[contains(@class, 'btn')]",
                    "//a[contains(@class, 'btn')]",
                    "//input[@type='submit']",
                    "//button[@type='submit']",
                    "//input[@type='button']",
                    "//button",
                    "//a[@href='javascript:;']"
                ]
                
                button_found = False
                for xpath in skip_buttons:
                    try:
                        button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        button.click()
                        print(f"✓ 成功点击跳过按钮: {xpath}")
                        button_found = True
                        time.sleep(2)
                        break
                    except:
                        continue
                
                if not button_found:
                    # 如果没有找到跳过按钮，尝试刷新页面
                    print("未找到跳过按钮，尝试刷新页面...")
                    self.driver.refresh()
                    time.sleep(3)
                
                # 检查是否还在验证码页面
                page_source = self.driver.page_source
                if "访问过于频繁，本次访问做以下验证码校验" not in page_source and "验证码校验" not in page_source:
                    print("✓ 验证码处理成功！")
                    return True
                    
            except Exception as e:
                print(f"自动处理验证码失败: {e}")
                
        print("自动处理验证码失败，需要手动处理...")
        return False
        
    def standardize_company_scale(self, scale_text):
        """
        将企业规模数字范围映射到标准化区间
        例如：10-49 -> 20-99
        """
        try:
            # 提取数字范围
            if '-' in scale_text or '~' in scale_text:
                # 处理范围格式，如 "10-49" 或 "10~49"
                numbers = re.findall(r'\d+', scale_text)
                if len(numbers) >= 2:
                    max_num = int(numbers[1])  # 使用范围的最大值进行匹配
                else:
                    max_num = int(numbers[0])
            else:
                # 处理单个数字
                numbers = re.findall(r'\d+', scale_text)
                if numbers:
                    max_num = int(numbers[0])
                else:
                    return scale_text  # 无法解析，返回原值
            
            # 根据最大值映射到标准区间
            if max_num <= 20:
                return "0-20"
            elif max_num <= 99:
                return "20-99"
            elif max_num <= 499:
                return "100-499"
            elif max_num <= 999:
                return "500-999"
            elif max_num <= 9999:
                return "1000-9999"
            else:
                return "10000+"
                
        except (ValueError, IndexError):
            # 解析失败，返回原值
            return scale_text
    
    def standardize_company_type(self, type_text):
        """
        将企业类型映射到标准化类型
        """
        if not type_text:
            return type_text
            
        # 标准企业类型列表
        standard_types = [
            "国有企业",
            "集体所有制企业", 
            "私营企业",
            "联营企业",
            "外商投资企业",
            "股份制企业",
            "个人独资企业",
            "合伙企业",
            "有限责任公司",
            "股份有限公司",
            "非法人组织企业",
            "农民专业合作组织"
        ]
        
        # 直接匹配
        for standard_type in standard_types:
            if standard_type in type_text:
                return standard_type
        
        # 模糊匹配规则
        type_text_lower = type_text.lower()
        
        # 有限责任公司的各种表述
        if any(keyword in type_text for keyword in ["有限责任公司", "有限公司", "责任有限公司"]):
            return "有限责任公司"
        
        # 股份有限公司的各种表述
        if any(keyword in type_text for keyword in ["股份有限公司", "股份公司"]):
            return "股份有限公司"
        
        # 私营企业相关
        if any(keyword in type_text for keyword in ["私营", "民营", "私人"]):
            return "私营企业"
        
        # 国有企业相关
        if any(keyword in type_text for keyword in ["国有", "国营", "央企", "国企"]):
            return "国有企业"
        
        # 外商投资企业相关
        if any(keyword in type_text for keyword in ["外商", "外资", "合资", "独资"]):
            return "外商投资企业"
        
        # 股份制企业相关
        if any(keyword in type_text for keyword in ["股份制", "股份合作"]):
            return "股份制企业"
        
        # 集体所有制企业相关
        if any(keyword in type_text for keyword in ["集体", "集体所有制"]):
            return "集体所有制企业"
        
        # 个人独资企业相关
        if any(keyword in type_text for keyword in ["个人独资", "独资"]):
            return "个人独资企业"
        
        # 合伙企业相关
        if any(keyword in type_text for keyword in ["合伙", "普通合伙", "有限合伙"]):
            return "合伙企业"
        
        # 联营企业相关
        if any(keyword in type_text for keyword in ["联营"]):
            return "联营企业"
        
        # 农民专业合作组织相关
        if any(keyword in type_text for keyword in ["合作社", "合作组织", "农民专业合作"]):
            return "农民专业合作组织"
        
        # 非法人组织企业相关
        if any(keyword in type_text for keyword in ["非法人", "分公司", "分支机构"]):
            return "非法人组织企业"
        
        # 如果都不匹配，返回原值
        return type_text
        
    def get_job_list_from_page(self, url):
        """从58同城列表页获取职位链接并进入详情页抓取信息"""
        print(f"正在访问: {url}")
        self.driver.get(url)
        time.sleep(0.5)  # 减少页面访问延时
        
        jobs_data = []
        try:
            # 等待页面加载
            WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 检测验证码并尝试自动处理
            page_source = self.driver.page_source
            if "访问过于频繁，本次访问做以下验证码校验" in page_source or "验证码校验" in page_source:
                print("\n检测到验证码页面...")
                # 先尝试自动处理验证码
                if self.handle_captcha():
                    print("验证码自动处理成功，继续执行...")
                else:
                    print("自动处理失败，请手动完成验证码验证...")
                    print("验证完成后，请按回车键继续...")
                    input()  # 等待用户按回车
                    print("继续执行...")
            
            # 获取所有职位链接
            job_links = self.get_job_links()
            print(f"找到 {len(job_links)} 个职位链接")
            
            # 处理当前页面的所有职位
            if job_links:
                for i, link in enumerate(job_links, 1):
                    try:
                        print(f"\n正在处理第{i}个职位")
                        job_data = self.scrape_job_detail_page(link)
                        if job_data:
                            jobs_data.append(job_data)
                            # 实时保存每个职位数据
                            self.save_single_job_to_excel(job_data, "58同城多城市职位详细信息.xlsx")
                            print(f"成功抓取第{i}个职位: {job_data.get('岗位名称', 'N/A')}")
                        else:
                            print(f"第{i}个职位数据为空")
                        
                        # 职位间延时，避免访问过于频繁
                        if i < len(job_links):
                            time.sleep(0.5)
                            
                    except Exception as e:
                        print(f"处理第{i}个职位失败: {e}")
                        continue
            else:
                print("当前页面没有找到职位链接")
                    
        except Exception as e:
            print(f"获取职位列表失败: {e}")
            
        return jobs_data
    
    def generate_page_urls(self, base_url, max_pages=5):
        """生成多页URL列表 - 通过点击下一页按钮获取真实的下一页链接"""
        url_list = [base_url]  # 第一页
        
        print(f"\n=== 开始生成 {max_pages} 页的URL列表 ===")
        print(f"第 1 页URL: {base_url}")
        
        if max_pages > 1:
            # 访问第一页
            self.driver.get(base_url)
            time.sleep(3)
            
            for page_num in range(2, max_pages + 1):
                try:
                    # 查找分页区域
                    from selenium.webdriver.common.by import By
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    
                    # 等待分页区域加载
                    wait = WebDriverWait(self.driver, 10)
                    pagination = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pagesout')))
                    
                    # 查找下一页按钮或具体页码链接
                    page_links = pagination.find_elements(By.TAG_NAME, 'a')
                    
                    next_page_element = None
                    for link in page_links:
                        text = link.text.strip()
                        href = link.get_attribute('href')
                        
                        # 优先查找具体页码
                        if text == str(page_num) and href and f'pn{page_num}' in href:
                            next_page_element = link
                            break
                        # 备选：查找"下一页"按钮
                        elif text in ['下一页', '下页', '>'] and href:
                            next_page_element = link
                    
                    if next_page_element:
                        # 点击下一页
                        self.driver.execute_script("arguments[0].click();", next_page_element)
                        time.sleep(3)
                        
                        # 获取当前页面URL
                        current_url = self.driver.current_url
                        url_list.append(current_url)
                        print(f"第 {page_num} 页URL: {current_url}")
                    else:
                        print(f"未找到第 {page_num} 页链接，停止生成")
                        break
                        
                except Exception as e:
                    print(f"获取第 {page_num} 页链接失败: {e}")
                    # 尝试使用默认格式
                    base_part = base_url.rstrip('/')
                    fallback_url = f"{base_part}/pn{page_num}/"
                    url_list.append(fallback_url)
                    print(f"第 {page_num} 页URL (默认格式): {fallback_url}")
                    
                    # 尝试访问默认URL
                    try:
                        self.driver.get(fallback_url)
                        time.sleep(2)
                    except:
                        pass
        
        print(f"\n=== URL列表生成完成，共 {len(url_list)} 个URL ===")
        return url_list
    
    def scrape_multiple_pages(self, base_url, max_pages=5):
        """抓取多页职位数据 - 先生成URL列表，再批量抓取"""
        # 第一步：生成所有页面的URL列表
        url_list = self.generate_page_urls(base_url, max_pages)
        
        # 第二步：批量抓取所有URL的数据
        all_jobs_data = []
        
        print(f"\n=== 开始批量抓取 {len(url_list)} 页的职位数据 ===")
        
        for i, url in enumerate(url_list, 1):
            try:
                print(f"\n--- 正在抓取第 {i} 页 ---")
                print(f"URL: {url}")
                
                # 抓取当前页面数据
                page_data = self.get_job_list_from_page(url)
                
                if page_data:
                    all_jobs_data.extend(page_data)
                    print(f"第 {i} 页成功抓取到 {len(page_data)} 个职位")
                    print(f"当前总计抓取职位数: {len(all_jobs_data)}")
                else:
                    print(f"第 {i} 页没有抓取到数据，可能已到最后一页")
                    if i > 1:  # 如果不是第一页且没有数据，可能已到最后一页
                        print(f"检测到第 {i} 页无数据，但继续抓取剩余页面")
                
                # 页面间延时，避免访问过于频繁
                if i < len(url_list):
                    print(f"等待 1 秒后继续下一页...")
                    time.sleep(1)  # 减少页面间延时
                    
            except Exception as e:
                print(f"抓取第 {i} 页时出错: {e}")
                continue
        
        print(f"\n=== 多页抓取完成，总共抓取到 {len(all_jobs_data)} 个职位 ===")
        return all_jobs_data
    
    def get_job_links(self):
        """获取当前页面所有职位的详情链接"""
        job_links = []
        try:
            # 尝试多种方式获取职位链接
            link_selectors = [
                "span.name",  # 用户指定的span.name元素
                "a[href*='shtml']",  # 58同城职位详情页通常以.shtml结尾
                "a[href*='job']",
                "a[href*='zhaopin']",
                ".job_name a",
                ".job-title a",
                ".title a"
            ]
            
            for selector in link_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if selector == "span.name":
                        # 对于span.name元素，需要找到其父级或相关的链接
                        try:
                            # 尝试找到包含该span的链接元素
                            parent_link = element.find_element(By.XPATH, "./ancestor::a[1]")
                            href = parent_link.get_attribute('href')
                        except:
                            # 如果span不在链接内，尝试找到同级或相邻的链接
                            try:
                                sibling_link = element.find_element(By.XPATH, "./following-sibling::a[1] | ./preceding-sibling::a[1]")
                                href = sibling_link.get_attribute('href')
                            except:
                                # 如果都找不到，尝试点击span元素本身看是否可点击
                                try:
                                    element.click()
                                    time.sleep(2)
                                    current_url = self.driver.current_url
                                    if current_url != self.driver.current_url:
                                        href = current_url
                                    else:
                                        href = None
                                except:
                                    href = None
                    else:
                        href = element.get_attribute('href')
                    
                    if href and ('shtml' in href or 'job' in href or 'zhaopin' in href or 'detail' in href):
                        if href not in job_links:
                            job_links.append(href)
                            
                if job_links:  # 如果找到链接就停止尝试其他选择器
                    break
                    
        except Exception as e:
            print(f"获取职位链接失败: {e}")
            
        return job_links
    
    def scrape_job_detail_page(self, job_url):
        """进入职位详情页面抓取完整信息"""
        job_data = {
            "企业名称": "",
            "企业类型": "",
            "社会信用码": "",
            "企业规模": "",
            "注册资本(万)": "",
            "所属区域": "",
            "联系人": "",
            "联系方式": "",
            "联系邮箱": "",
            "办公地址": "",
            "企业简介": "",
            "营业执照": "",
            "企业相册": "",
            "岗位名称": "",
            "薪资类型": "",
            "薪资范围起": "",
            "薪资范围至": "",
            "工作地点": "",
            "岗位要求": "",
            "学历要求": "",
            "招聘人数": "",
            "发布时间": "",
            "结束时间": "",
            "工作职责": "",
            "任职要求": ""
        }
        
        try:
            # 访问职位详情页
            self.driver.get(job_url)
            time.sleep(1)
            
            # 等待页面加载
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 检测验证码并尝试自动处理
            page_source = self.driver.page_source
            if "访问过于频繁，本次访问做以下验证码校验" in page_source or "验证码校验" in page_source:
                print("\n检测到验证码页面...")
                # 先尝试自动处理验证码
                if self.handle_captcha():
                    print("验证码自动处理成功，继续执行...")
                else:
                    print("自动处理失败，请手动完成验证码验证...")
                    print("验证完成后，请按回车键继续...")
                    input()  # 等待用户按回车
                    print("继续执行...")
                # 重新获取页面源码
                page_source = self.driver.page_source
            
            # 获取页面源码
            soup = BeautifulSoup(page_source, "html.parser")
            
            # 移除"您可能感兴趣的职位"等推荐区域
            for unwanted in soup.find_all(['div', 'section'], class_=lambda x: x and ('recommend' in x.lower() or 'interest' in x.lower() or 'similar' in x.lower())):
                unwanted.decompose()
            
            # 移除包含"您可能感兴趣"文本的区域
            for element in soup.find_all(string=lambda text: text and '您可能感兴趣' in text):
                parent = element.parent
                while parent and parent.name != 'body':
                    if parent.name in ['div', 'section', 'aside']:
                        parent.decompose()
                        break
                    parent = parent.parent
            
            # 只保留主要内容区域
            main_content = soup.find('div', class_=lambda x: x and ('main' in x.lower() or 'content' in x.lower() or 'detail' in x.lower()))
            if main_content:
                page_text = main_content.get_text()
            else:
                page_text = soup.get_text()
            
            # 提取岗位名称 - 基于实际HTML结构的选择器
            title_selectors = [
                ".pos_title", ".job-title", ".job_title", ".title", "h1", ".name",
                "[class*='title']:not([class*='recommend']):not([class*='similar'])",
                "[class*='name']:not([class*='recommend']):not([class*='similar'])"
            ]
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element and title_element.get_text().strip():
                    title_text = title_element.get_text().strip()
                    # 过滤掉包含推荐信息和培训广告的文本
                    if ('您可能感兴趣' not in title_text and '推荐职位' not in title_text and 
                        '培训广告' not in title_text):
                        job_data["岗位名称"] = title_text
                        break
            
            # 提取企业名称和企业链接 - 基于实际HTML结构的选择器
            company_url = None
            company_selectors = [
                ".baseInfo_link a", ".baseInfo_link", ".company-name", ".company_name", ".company", ".corp-name",
                "h1 + .company", ".job-company", ".employer-name",
                "[class*='company']:not([class*='recommend']):not([class*='similar'])"
            ]
            for selector in company_selectors:
                company_element = soup.select_one(selector)
                if company_element and company_element.get_text().strip():
                    company_text = company_element.get_text().strip()
                    # 过滤掉包含推荐信息和特定开头的文本，以及不包含"公司"字的企业名称
                    # 同时检查企业名称长度（3-20个字）和非空
                    if (company_text and len(company_text) >= 3 and len(company_text) <= 20 and
                        '您可能感兴趣' not in company_text and '推荐职位' not in company_text and 
                        not company_text.startswith('微信扫一扫快速求职') and '公司' in company_text):
                        job_data["企业名称"] = company_text
                        # 提取企业链接
                        if company_element.name == 'a' and company_element.get('href'):
                            company_url = company_element.get('href')
                            if not company_url.startswith('http'):
                                company_url = 'https:' + company_url if company_url.startswith('//') else 'https://58.com' + company_url
                        break
            
            # 如果没找到企业名称，用正则表达式从页面文本中提取
            if not job_data["企业名称"]:
                # 从页面文本的前半部分提取，避免推荐区域
                text_lines = page_text.split('\n')[:50]  # 只取前50行
                first_half_text = '\n'.join(text_lines)
                
                # 只匹配包含"公司"字的企业名称
                company_patterns = [
                    r'([\u4e00-\u9fa5]{2,20}公司)',
                    r'([A-Za-z\s]{2,30}(?:公司|Company))'
                ]
                for pattern in company_patterns:
                    match = re.search(pattern, first_half_text)
                    if match:
                        company_name = match.group(1).strip()
                        # 过滤掉以特定内容开头的企业名称，确保包含"公司"字
                        # 同时检查企业名称长度（3-20个字）和非空
                        if (company_name and len(company_name) >= 3 and len(company_name) <= 20 and
                            not company_name.startswith('微信扫一扫快速求职') and '公司' in company_name):
                            job_data["企业名称"] = company_name
                            break
            
            # 提取薪资信息 - 基于实际HTML结构和文本模式
            # 首先尝试从CSS选择器提取
            salary_element = soup.select_one(".pos_salary")
            if salary_element:
                salary_text = salary_element.get_text().strip()
                salary_match = re.search(r'(\d+)-(\d+)', salary_text)
                if salary_match:
                    job_data["薪资范围起"] = salary_match.group(1)
                    job_data["薪资范围至"] = salary_match.group(2)
            
            # 如果CSS选择器没找到，使用正则表达式
            if not job_data["薪资范围起"]:
                salary_patterns = [
                    r'(\d+)[-~](\d+)元/月',
                    r'(\d+)[-~](\d+)万/年',
                    r'(\d+)[-~](\d+)千/月',
                    r'薪资.*?(\d+)[-~](\d+)',
                    r'工资.*?(\d+)[-~](\d+)'
                ]
                
                # 从页面文本的前半部分提取薪资信息
                text_lines = page_text.split('\n')[:30]  # 只取前30行
                salary_text = '\n'.join(text_lines)
                
                for pattern in salary_patterns:
                    salary_match = re.search(pattern, salary_text)
                    if salary_match:
                        groups = salary_match.groups()
                        if len(groups) >= 2:
                            job_data["薪资范围起"] = groups[0]
                            job_data["薪资范围至"] = groups[1]
                        break
            
            # 薪资类型逻辑：默认为非面谈，如果薪资范围没有匹配到内容则设为面谈
            if job_data["薪资范围起"] and job_data["薪资范围至"]:
                job_data["薪资类型"] = "非面谈"
            else:
                job_data["薪资类型"] = "面谈"
            
            # 提取工作地点 - 只保留"北京 - 大兴"格式，去掉详细地址
            # 首先尝试从.pos_area_item提取基本信息
            location_elements = soup.select(".pos_area_item")
            if location_elements and len(location_elements) >= 2:
                # 只取前两个元素：城市和区域
                location_parts = [elem.get_text().strip() for elem in location_elements[:2]]
                basic_location = " - ".join(location_parts)
                job_data["工作地点"] = basic_location
            
            # 如果CSS选择器没找到，使用正则表达式，只匹配"城市 - 区域"格式
            if not job_data["工作地点"]:
                location_patterns = [
                    r'(北京)\s*[-\s]*([\u4e00-\u9fa5]+区)',
                    r'(上海)\s*[-\s]*([\u4e00-\u9fa5]+区)',
                    r'(广州)\s*[-\s]*([\u4e00-\u9fa5]+区)',
                    r'(深圳)\s*[-\s]*([\u4e00-\u9fa5]+区)',
                    r'([\u4e00-\u9fa5]+市?)\s*[-\s]*([\u4e00-\u9fa5]+区)'
                ]
                
                # 从页面文本的前半部分提取地点信息
                location_text = '\n'.join(page_text.split('\n')[:40])
                
                for pattern in location_patterns:
                    location_match = re.search(pattern, location_text)
                    if location_match:
                        city = location_match.group(1).replace('市', '')
                        district = location_match.group(2)
                        job_data["工作地点"] = f"{city} - {district}"
                        break
            
            # 提取学历要求 - 基于实际HTML结构
            # 首先尝试从CSS选择器提取
            condition_elements = soup.select(".item_condition")
            for elem in condition_elements:
                text = elem.get_text().strip()
                if any(edu in text for edu in ['博士', '硕士', '研究生', '本科', '大专', '专科', '高中', '中专', '初中', '学历不限']):
                    # 将初中、中专、高中统一显示为学历不限
                    if any(low_edu in text for low_edu in ['初中', '中专', '高中']):
                        job_data["学历要求"] = "学历不限"
                    else:
                        job_data["学历要求"] = text
                    break
            
            # 如果CSS选择器没找到，使用正则表达式
            if not job_data["学历要求"]:
                education_patterns = [
                    r'学历要求.*?(博士|硕士|研究生|本科|大专|专科|高中|中专|初中|不限)',
                    r'学历.*?(博士|硕士|研究生|本科|大专|专科|高中|中专|初中|不限)',
                    r'(博士|硕士|研究生|本科|大专|专科)以上',
                    r'要求.*?(博士|硕士|研究生|本科|大专|专科|高中|中专|初中)'
                ]
                
                # 从页面文本的前半部分提取学历信息
                education_text = '\n'.join(page_text.split('\n')[:50])
                
                for pattern in education_patterns:
                    edu_match = re.search(pattern, education_text)
                    if edu_match:
                        education_level = edu_match.group(1)
                        # 将初中、中专、高中统一显示为学历不限
                        if education_level in ['初中', '中专', '高中']:
                            job_data["学历要求"] = "学历不限"
                        else:
                            job_data["学历要求"] = education_level
                        break
            
            # 提取工作经验要求 - 基于实际HTML结构
            # 首先尝试从CSS选择器提取
            for elem in condition_elements:
                text = elem.get_text().strip()
                if any(exp in text for exp in ['经验', '年', '应届', '不限']):
                    if '学历' not in text and '招' not in text:  # 排除学历和招聘人数信息
                        job_data["岗位要求"] = text
                        break
            
            # 如果CSS选择器没找到，使用正则表达式
            if not job_data["岗位要求"]:
                exp_patterns = [
                    r'工作经验.*?(\d+)[-~](\d+)年',
                    r'经验.*?(\d+)[-~](\d+)年',
                    r'(\d+)年以上.*?经验',
                    r'经验.*?(\d+)年以上',
                    r'(无需经验|不限经验|应届毕业生|经验不限)'
                ]
                
                # 从页面文本的前半部分提取经验信息
                exp_text = '\n'.join(page_text.split('\n')[:50])
                
                for pattern in exp_patterns:
                    exp_match = re.search(pattern, exp_text)
                    if exp_match:
                        if len(exp_match.groups()) >= 2:
                            job_data["岗位要求"] = f"{exp_match.group(1)}-{exp_match.group(2)}年经验"
                        else:
                            job_data["岗位要求"] = exp_match.group(1)
                        break
            
            # 提取招聘人数 - 只匹配数字，默认为1
            recruit_number = 1  # 默认值
            
            # 首先尝试从CSS选择器提取
            for elem in condition_elements:
                text = elem.get_text().strip()
                if '招' in text and '人' in text:
                    # 从文本中提取数字
                    number_match = re.search(r'(\d+)', text)
                    if number_match:
                        recruit_number = int(number_match.group(1))
                    break
            
            # 如果CSS选择器没找到，使用正则表达式
            if recruit_number == 1:  # 如果还是默认值，继续尝试
                recruit_patterns = [
                    r'招聘.*?(\d+)人',
                    r'招.*?(\d+)人',
                    r'(\d+)人'
                ]
                
                # 从页面文本的前半部分提取招聘人数信息
                recruit_text = '\n'.join(page_text.split('\n')[:40])
                
                for pattern in recruit_patterns:
                    recruit_match = re.search(pattern, recruit_text)
                    if recruit_match:
                        try:
                            recruit_number = int(recruit_match.group(1))
                            break
                        except ValueError:
                            continue
            
            # 设置招聘人数为数字类型
            job_data["招聘人数"] = recruit_number
            
            # 提取发布时间
            time_patterns = [
                r'发布时间.*?(\d{4}-\d{2}-\d{2})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{2}-\d{2})',
                r'(今天|昨天|前天)',
                r'(\d+)小时前',
                r'(\d+)天前'
            ]
            
            for pattern in time_patterns:
                time_match = re.search(pattern, page_text)
                if time_match:
                    job_data["发布时间"] = time_match.group(1)
                    break
            
            # 提取工作职责和任职要求 - 基于用户要求的精确匹配
            # 首先尝试从职位描述区域提取
            job_desc_element = soup.select_one(".des")
            full_desc_text = ""
            if job_desc_element:
                desc_text = job_desc_element.get_text()
                full_desc_text = desc_text  # 保存完整描述文本
                
                # 提取岗位职责内容
                responsibility_patterns = [
                    r'岗位职责[：:]?\s*(.*?)(?=任职要求|福利待遇|联系方式|$)',
                    r'工作职责[：:]?\s*(.*?)(?=任职要求|福利待遇|联系方式|$)',
                    r'工作内容[：:]?\s*(.*?)(?=任职要求|福利待遇|联系方式|$)'
                ]
                
                for pattern in responsibility_patterns:
                    responsibility_match = re.search(pattern, desc_text, re.DOTALL)
                    if responsibility_match:
                        job_data["工作职责"] = responsibility_match.group(1).strip()[:500]
                        break
                
                # 提取任职要求内容
                requirement_patterns = [
                    r'任职要求[：:]?\s*(.*?)(?=福利待遇|联系方式|工作地点|$)',
                    r'职位要求[：:]?\s*(.*?)(?=福利待遇|联系方式|工作地点|$)'
                ]
                
                for pattern in requirement_patterns:
                    requirement_match = re.search(pattern, desc_text, re.DOTALL)
                    if requirement_match:
                        job_data["任职要求"] = requirement_match.group(1).strip()[:500]
                        break
            
            # 如果没有找到，使用页面文本进行提取
            if not job_data["工作职责"] or not job_data["任职要求"]:
                # 提取岗位职责
                if not job_data["工作职责"]:
                    responsibility_patterns = [
                        r'岗位职责[：:]?\s*(.*?)(?=任职要求|福利待遇|联系方式|工作地点|$)',
                        r'工作职责[：:]?\s*(.*?)(?=任职要求|福利待遇|联系方式|工作地点|$)',
                        r'工作内容[：:]?\s*(.*?)(?=任职要求|福利待遇|联系方式|工作地点|$)',
                        r'职责[：:]?\s*(.*?)(?=任职要求|福利待遇|联系方式|工作地点|$)'
                    ]
                    
                    for pattern in responsibility_patterns:
                        match = re.search(pattern, page_text, re.DOTALL)
                        if match:
                            job_data["工作职责"] = match.group(1).strip()[:500]
                            break
                
                # 提取任职要求
                if not job_data["任职要求"]:
                    requirement_patterns = [
                        r'任职要求[：:]?\s*(.*?)(?=福利待遇|联系方式|工作地点|公司简介|$)',
                        r'职位要求[：:]?\s*(.*?)(?=福利待遇|联系方式|工作地点|公司简介|$)',
                        r'岗位要求[：:]?\s*(.*?)(?=福利待遇|联系方式|工作地点|公司简介|$)',
                        r'要求[：:]?\s*(.*?)(?=福利待遇|联系方式|工作地点|公司简介|$)'
                    ]
                    
                    for pattern in requirement_patterns:
                        match = re.search(pattern, page_text, re.DOTALL)
                        if match:
                            job_data["任职要求"] = match.group(1).strip()[:500]
                            break
            
            # 如果工作职责和任职要求都没有匹配成功，将职位描述写入任职要求
            if not job_data["工作职责"] and not job_data["任职要求"] and full_desc_text:
                # 清理描述文本，去除多余的空白字符
                cleaned_desc = re.sub(r'\s+', ' ', full_desc_text.strip())
                job_data["任职要求"] = cleaned_desc[:500]
            
            # 清理工作职责和任职要求字段，去除开头的】符号
            if job_data["工作职责"] and job_data["工作职责"].startswith('】'):
                job_data["工作职责"] = job_data["工作职责"][1:].strip()
            
            if job_data["任职要求"] and job_data["任职要求"].startswith('】'):
                job_data["任职要求"] = job_data["任职要求"][1:].strip()

            # 提取联系方式
            contact_patterns = [
                r'联系电话.*?(1[3-9]\d{9})',
                r'电话.*?(1[3-9]\d{9})',
                r'手机.*?(1[3-9]\d{9})',
                r'(1[3-9]\d{9})'
            ]
            
            for pattern in contact_patterns:
                contact_match = re.search(pattern, page_text)
                if contact_match:
                    job_data["联系方式"] = contact_match.group(1)
                    break
            
            # 提取邮箱
            email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            email_match = re.search(email_pattern, page_text)
            if email_match:
                job_data["联系邮箱"] = email_match.group(1)
            
            # 提取办公地址
            address_patterns = [
                r'办公地址.*?([\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区.*?)(?=联系|电话|邮箱|$)',
                r'地址.*?([\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区.*?)(?=联系|电话|邮箱|$)',
                r'公司地址.*?([\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区.*?)(?=联系|电话|邮箱|$)'
            ]
            
            for pattern in address_patterns:
                address_match = re.search(pattern, page_text)
                if address_match:
                    job_data["办公地址"] = address_match.group(1).strip()[:100]  # 限制长度
                    break
            
        except Exception as e:
            print(f"抓取职位详情页失败: {e}")
        
        # 检查职位名称是否包含培训广告，如果包含则跳过该职位
        if job_data["岗位名称"] and "培训广告" in job_data["岗位名称"]:
            print(f"× 跳过培训广告职位: {job_data['岗位名称']}")
            return None
            
        # 如果找到了企业链接，抓取企业详细信息
        if company_url and job_data["企业名称"]:
            print(f"正在抓取企业详细信息: {job_data['企业名称']}")
            company_details = self.scrape_company_detail_page(company_url)
            # 将企业详细信息合并到job_data中
            for key, value in company_details.items():
                if value:  # 只更新非空值
                    job_data[key] = value
            
        return job_data

    def scrape_company_detail_page(self, company_url):
        """进入企业详情页面抓取企业详细信息"""
        company_data = {
            "企业类型": "",
            "社会信用码": "",
            "企业规模": "",
            "注册资本(万)": "",
            "所属区域": "",
            "联系人": "",
            "联系方式": "",
            "联系邮箱": "",
            "办公地址": "",
            "企业简介": "",
            "营业执照": "",
            "企业相册": ""
        }
        
        try:
            # 访问企业详情页
            self.driver.get(company_url)
            time.sleep(0.5)  # 减少企业详情页延时
            
            # 等待页面加载
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 检测验证码并尝试自动处理
            page_source = self.driver.page_source
            if "访问过于频繁，本次访问做以下验证码校验" in page_source or "验证码校验" in page_source:
                print("\n检测到验证码页面...")
                # 先尝试自动处理验证码
                if self.handle_captcha():
                    print("验证码自动处理成功，继续执行...")
                else:
                    print("自动处理失败，请手动完成验证码验证...")
                    print("验证完成后，请按回车键继续...")
                    input()  # 等待用户按回车
                    print("继续执行...")
                # 重新获取页面源码
                page_source = self.driver.page_source
            
            # 获取页面源码
            soup = BeautifulSoup(page_source, "html.parser")
            
            # 移除"您可能感兴趣的企业"等推荐区域
            for unwanted in soup.find_all(['div', 'section'], class_=lambda x: x and ('recommend' in x.lower() or 'interest' in x.lower() or 'similar' in x.lower())):
                unwanted.decompose()
            
            # 移除包含"您可能感兴趣"文本的区域
            for element in soup.find_all(string=lambda text: text and '您可能感兴趣' in text):
                parent = element.parent
                while parent and parent.name != 'body':
                    if parent.name in ['div', 'section', 'aside']:
                        parent.decompose()
                        break
                    parent = parent.parent
            
            # 获取页面文本
            page_text = soup.get_text()
            
            # 提取企业类型 - 只匹配具体的公司类型格式
            type_patterns = [
                r'(有限责任公司\([^)]+\))',
                r'(股份有限公司\([^)]+\))',
                r'(有限责任公司)',
                r'(股份有限公司)',
                r'公司类型[：:]?\s*(有限责任公司\([^)]+\))',
                r'公司类型[：:]?\s*(股份有限公司\([^)]+\))',
                r'公司类型[：:]?\s*(有限责任公司)',
                r'公司类型[：:]?\s*(股份有限公司)'
            ]
            for pattern in type_patterns:
                match = re.search(pattern, page_text)
                if match:
                    type_text = match.group(1).strip()
                    # 将企业类型标准化
                    standardized_type = self.standardize_company_type(type_text)
                    company_data["企业类型"] = standardized_type
                    break
            
            # 提取社会信用码
            credit_patterns = [
                r'社会信用代码[：:]?\s*([A-Z0-9]{18})',
                r'统一社会信用代码[：:]?\s*([A-Z0-9]{18})',
                r'信用代码[：:]?\s*([A-Z0-9]{18})',
                r'([A-Z0-9]{18})'
            ]
            for pattern in credit_patterns:
                match = re.search(pattern, page_text)
                if match:
                    company_data["社会信用码"] = match.group(1).strip()
                    break
            
            # 提取企业规模 - 只匹配员工规模的数字部分
            scale_patterns = [
                r'员工规模[：:]?\s*(\d+[-~]\d+)人',
                r'员工规模[：:]?\s*(\d+)人以上',
                r'员工规模[：:]?\s*(\d+)人以下',
                r'员工规模[：:]?\s*(\d+)人',
                r'公司规模[：:]?\s*(\d+[-~]\d+)人',
                r'公司规模[：:]?\s*(\d+)人以上',
                r'公司规模[：:]?\s*(\d+)人以下',
                r'公司规模[：:]?\s*(\d+)人',
                r'企业规模[：:]?\s*(\d+[-~]\d+)人',
                r'企业规模[：:]?\s*(\d+)人以上',
                r'企业规模[：:]?\s*(\d+)人以下',
                r'企业规模[：:]?\s*(\d+)人',
                r'规模[：:]?\s*(\d+[-~]\d+)人',
                r'规模[：:]?\s*(\d+)人以上',
                r'规模[：:]?\s*(\d+)人以下',
                r'规模[：:]?\s*(\d+)人'
            ]
            for pattern in scale_patterns:
                match = re.search(pattern, page_text)
                if match:
                    scale_number = match.group(1).strip()
                    # 只保存数字部分
                    if scale_number and '企业未添加' not in scale_number:
                        # 将数字范围映射到标准化规模区间
                        standardized_scale = self.standardize_company_scale(scale_number)
                        company_data["企业规模"] = standardized_scale
                        break
            
            # 提取注册资本
            capital_patterns = [
                r'注册资本[：:]?\s*([\d.]+万?)',
                r'注册资金[：:]?\s*([\d.]+万?)',
                r'资本[：:]?\s*([\d.]+万?)'
            ]
            for pattern in capital_patterns:
                match = re.search(pattern, page_text)
                if match:
                    capital_text = match.group(1).strip()
                    # 统一转换为万元
                    if '万' not in capital_text:
                        try:
                            capital_num = float(capital_text)
                            if capital_num > 10000:  # 如果大于1万，可能是元为单位
                                capital_text = str(capital_num / 10000)
                        except:
                            pass
                    company_data["注册资本(万)"] = capital_text
                    break
            
            # 提取所属区域 - 只匹配城市级别地址，过滤无用信息和重复地址
            region_patterns = [
                r'所属区域[：:]?\s*([\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区)',
                r'地区[：:]?\s*([\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区)',
                r'区域[：:]?\s*([\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区)',
                r'总部位于([\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区)',
                r'(?:^|\s)([\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)(?=\s|$)'
            ]
            for pattern in region_patterns:
                match = re.search(pattern, page_text)
                if match:
                    region_text = match.group(1).strip()
                    # 过滤掉包含无关词汇的内容
                    unwanted_keywords = ['注册地位于', '注册地址', '营业执照', '工商注册', '找工作', '免费发布', '登记简历', 
                                        '公司福利', '饭补', '加班补助', '交通便利', '餐补', '市中心区', '不匹配', 
                                        '人公司', '福利', '补助', '便利', '有限公司', '科技有限公司', '信息科技', 
                                        '华南地区', '华北地区', '华东地区', '华西地区', '在华', '地区', '公司在']
                    if not any(unwanted in region_text for unwanted in unwanted_keywords):
                        # 确保是标准的城市区域格式，且长度合理
                        if re.match(r'^[\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区$', region_text) and len(region_text) <= 10:
                            # 处理重复地址，只保留第一个"XX市XX区"格式
                            first_region_match = re.search(r'^([\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区)', region_text)
                            if first_region_match:
                                company_data["所属区域"] = first_region_match.group(1)
                            else:
                                company_data["所属区域"] = region_text
                            break
            
            # 进一步清理所属区域，去除重复的地址部分
            if company_data.get("所属区域"):
                region = company_data["所属区域"]
                # 处理类似"北京市房山区阳光北大街北京市房山区"的重复问题
                # 查找第一个完整的"XX市XX区"模式
                first_region_match = re.search(r'^([\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区)', region)
                if first_region_match:
                    clean_region = first_region_match.group(1)
                    company_data["所属区域"] = clean_region
            
            # 提取联系人 - 匹配特定HTML结构中的联系人姓名
            # 查找 <div class="c_detail_item"><span>联系人</span><i></i><em class="">姓名</em></div> 结构
            contact_div = soup.find('div', class_='c_detail_item')
            if contact_div:
                span = contact_div.find('span')
                if span and '联系人' in span.get_text():
                    em = contact_div.find('em')
                    if em:
                        contact_person = em.get_text().strip()
                        # 如果是"企业未添加联系人"或类似内容，则为空
                        if contact_person and '企业未添加' not in contact_person:
                            company_data["联系人"] = contact_person
            
            # 如果没有找到特定结构，使用备用正则表达式
            if not company_data.get("联系人"):
                contact_person_patterns = [
                    r'联系人[：:]?\s*([\u4e00-\u9fa5]{2,10})',
                    r'HR[：:]?\s*([\u4e00-\u9fa5]{2,10})',
                    r'招聘负责人[：:]?\s*([\u4e00-\u9fa5]{2,10})'
                ]
                for pattern in contact_person_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        contact_person = match.group(1).strip()
                        # 如果是"企业未添加"、"企业未添"或类似内容，则为空
                        if contact_person and not any(invalid in contact_person for invalid in ['企业未添加', '企业未添', '未添加', '未添']):
                            company_data["联系人"] = contact_person
                        break
            
            # 提取联系方式 - 如果是"企业未添加"就为空
            phone_patterns = [
                r'联系方式[：:]?\s*(1[3-9]\d{9})',
                r'联系电话[：:]?\s*(1[3-9]\d{9})',
                r'电话[：:]?\s*(1[3-9]\d{9})',
                r'手机[：:]?\s*(1[3-9]\d{9})',
                r'(1[3-9]\d{9})'
            ]
            # 先检查是否有"企业未添加"的情况
            if '企业未添加' not in page_text or '联系方式' not in page_text:
                for pattern in phone_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        phone_number = match.group(1).strip()
                        # 确保不是"企业未添加"相关内容
                        if phone_number and '企业未添加' not in phone_number and '未添加' not in phone_number:
                            company_data["联系方式"] = phone_number
                        break
            
            # 提取联系邮箱 - 匹配招聘邮箱，如果是"企业未添加"就为空
            email_patterns = [
                r'招聘邮箱[：:]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'邮箱[：:]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'邮件[：:]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ]
            # 先检查是否有"企业未添加"的情况
            if '企业未添加' not in page_text or '邮箱' not in page_text:
                for pattern in email_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        email_address = match.group(1).strip()
                        # 确保不是"企业未添加"相关内容
                        if email_address and '企业未添加' not in email_address and '未添加' not in email_address:
                            company_data["联系邮箱"] = email_address
                        break
            
            # 提取办公地址 - 匹配公司地址格式，如"北京-大兴-西红门 西红门鸿坤金融谷25号楼"
            address_patterns = [
                r'公司地址\s*([\u4e00-\u9fa5]+-[\u4e00-\u9fa5]+-[\u4e00-\u9fa5]+\s+[^\u4e00-\u9fa5]*[\u4e00-\u9fa5]+[^出口确定©]+?)(?=出口|确定|©|$)',
                r'办公地址\s*([\u4e00-\u9fa5]+-[\u4e00-\u9fa5]+-[\u4e00-\u9fa5]+\s+[^\u4e00-\u9fa5]*[\u4e00-\u9fa5]+[^出口确定©]+?)(?=出口|确定|©|$)',
                r'地址\s*([\u4e00-\u9fa5]+-[\u4e00-\u9fa5]+-[\u4e00-\u9fa5]+\s+[^出口确定©]+?)(?=出口|确定|©|$)',
                r'([\u4e00-\u9fa5]+-[\u4e00-\u9fa5]+-[\u4e00-\u9fa5]+\s+[\u4e00-\u9fa5]+[^出口确定©]*?)(?=出口|确定|©|$)'
            ]
            for pattern in address_patterns:
                match = re.search(pattern, page_text)
                if match:
                    address_text = match.group(1).strip()
                    # 清理地址文本，移除重复部分
                    address_text = re.sub(r'([\u4e00-\u9fa5]+)\1+', r'\1', address_text)  # 移除重复的中文字符
                    company_data["办公地址"] = address_text[:100]  # 限制长度
                    break
            
            # 提取企业简介 - 匹配特定HTML结构
            # 首先尝试匹配 <div class="introduction"><span class="c_title">公司简介</span><div class="introduction_box"><p><span>内容</span></p></div></div>
            intro_div = soup.find('div', class_='introduction')
            if intro_div:
                title_span = intro_div.find('span', class_='c_title')
                if title_span and '公司简介' in title_span.get_text():
                    intro_box = intro_div.find('div', class_='introduction_box')
                    if intro_box:
                        # 提取所有文本内容
                        intro_text = intro_box.get_text().strip()
                        # 清理文本，移除多余的空白字符
                        intro_text = re.sub(r'\s+', ' ', intro_text)
                        # 过滤掉包含特定内容的企业简介
                        if (intro_text and len(intro_text) > 10 and 
                            '企业未添加' not in intro_text and 
                            '老板使用58招人神器' not in intro_text and
                            '该信息通过58招才猫app发布' not in intro_text and
                            '老板忙得连写简介的时间都没有' not in intro_text and
                            '老板使用58APP商家版发布该职位' not in intro_text and
                            '招人的诚意大到无需描述' not in intro_text and
                            '58' not in intro_text):
                            company_data["企业简介"] = intro_text[:500]  # 增加长度限制
            
            # 如果没有找到特定结构，使用备用正则表达式
            if not company_data.get("企业简介"):
                intro_patterns = [
                    r'公司简介\s*([^公司相册企业未添加相册公司地址出口确定©]+?)(?=公司相册|企业未添加相册|公司地址|出口|确定|©|基本信息|工商信息|$)',
                    r'企业简介\s*([^公司相册企业未添加相册公司地址出口确定©]+?)(?=公司相册|企业未添加相册|公司地址|出口|确定|©|基本信息|工商信息|$)',
                    r'简介\s*([^公司相册企业未添加相册公司地址出口确定©]+?)(?=公司相册|企业未添加相册|公司地址|出口|确定|©|基本信息|工商信息|$)'
                ]
                for pattern in intro_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        intro_text = match.group(1).strip()
                        # 过滤掉无关信息
                        if (intro_text and len(intro_text) > 10 and 
                            '企业未添加' not in intro_text and 
                            '老板使用58招人神器' not in intro_text and
                            '该信息通过58招才猫app发布' not in intro_text and
                            '老板忙得连写简介的时间都没有' not in intro_text and
                            '老板使用58APP商家版发布该职位' not in intro_text and
                            '招人的诚意大到无需描述' not in intro_text and
                            '58' not in intro_text):
                            company_data["企业简介"] = intro_text[:300]  # 限制长度
                            break
            
            # 营业执照字段固定为空
            # company_data["营业执照"] 保持初始化时的空字符串
            
            # 提取企业相册 - 匹配图片地址，排除通用图片，优先匹配公司相册
            try:
                # 排除的通用图片URL
                excluded_urls = [
                    'https://pic1.58cdn.com.cn/nowater/cxnomark/n_v2e8d9dbce287f4e45bb5ebebbe90bb295.png',
                    'https://pic1.58cdn.com.cn/nowater/cxnomark/n_v2502726ab70ad4151ba43adc35fda265e.png'
                ]
                
                # 首先尝试查找公司相册区域的图片
                album_section = soup.find(string=re.compile(r'公司相册|企业相册'))
                image_urls = []
                
                if album_section:
                    # 找到相册区域后查找附近的图片
                    parent = album_section.parent
                    if parent:
                        # 向上查找包含相册的容器
                        for _ in range(3):  # 最多向上查找3层
                            if parent.parent:
                                parent = parent.parent
                            else:
                                break
                        
                        # 在相册容器中查找图片
                        img_elements = parent.find_all('img')
                    else:
                        img_elements = []
                else:
                    # 如果没有找到相册区域，查找所有图片
                    img_elements = soup.find_all('img')
                
                for img in img_elements:
                    src = img.get('src', '')
                    data_src = img.get('data-src', '')
                    
                    # 优先使用data-src，然后是src
                    img_url = data_src if data_src else src
                    
                    # 过滤有效的图片URL
                    if img_url and any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        # 转换为完整URL
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = 'https://pic1.58cdn.com.cn' + img_url
                        elif not img_url.startswith('http'):
                            continue
                        
                        # 排除通用图标、小图片和指定的通用图片
                        if (not any(exclude in img_url.lower() for exclude in ['icon', 'logo', 'avatar', 'default', 'placeholder']) 
                            and img_url not in excluded_urls):
                            image_urls.append(img_url)
                
                # 去重并用||分割
                if image_urls:
                    unique_urls = list(dict.fromkeys(image_urls))  # 去重保持顺序
                    company_data["企业相册"] = '||'.join(unique_urls[:10])  # 最多保留10张图片
                    
            except Exception as e:
                print(f"提取企业相册失败: {e}")
            
        except Exception as e:
            print(f"抓取企业详情页失败: {e}")
            
        return company_data

    def extract_job_from_item(self, item):
        """从单个职位项目中提取信息"""
        job_data = {
            "企业名称": "",
            "企业类型": "",
            "社会信用码": "",
            "企业规模": "",
            "注册资本(万)": "",
            "所属区域": "",
            "联系人": "",
            "联系方式": "",
            "联系邮箱": "",
            "办公地址": "",
            "企业简介": "",
            "营业执照": "",
            "企业相册": "",
            "岗位名称": "",
            "薪资类型": "",
            "薪资范围起": "",
            "薪资范围至": "",
            "工作地点": "",
            "岗位要求": "",
            "学历要求": "",
            "招聘人数": "",
            "发布时间": "",
            "结束时间": "",
            "工作职责": "",
            "任职要求": ""
        }
        
        try:
            item_text = item.get_text()
            
            # 提取岗位名称
            title_element = item.find("a") or item.find("h3") or item.find("h4")
            if title_element:
                job_data["岗位名称"] = title_element.get_text().strip()
            
            # 提取薪资信息
            salary_patterns = [
                r'(\d+)[-~](\d+)元/月',
                r'(\d+)[-~](\d+)元',
                r'(\d+)[-~](\d+)万/年',
                r'(\d+)[-~](\d+)万',
                r'(\d+)[-~](\d+)千/月',
                r'面议'
            ]
            
            for pattern in salary_patterns:
                salary_match = re.search(pattern, item_text)
                if salary_match:
                    if pattern == r'面议':
                        job_data["薪资类型"] = "面议"
                    else:
                        groups = salary_match.groups()
                        if len(groups) >= 2:
                            job_data["薪资范围起"] = groups[0]
                            job_data["薪资范围至"] = groups[1]
                            
                            if "月" in salary_match.group(0):
                                job_data["薪资类型"] = "月薪"
                            elif "年" in salary_match.group(0):
                                job_data["薪资类型"] = "年薪"
                            else:
                                job_data["薪资类型"] = "月薪"
                    break
            
            # 提取工作地点 - 只保留"城市 - 区域"格式
            location_patterns = [
                r'(北京)\s*[-\s]*([\u4e00-\u9fa5]+区)',
                r'(上海)\s*[-\s]*([\u4e00-\u9fa5]+区)',
                r'(广州)\s*[-\s]*([\u4e00-\u9fa5]+区)',
                r'(深圳)\s*[-\s]*([\u4e00-\u9fa5]+区)',
                r'([\u4e00-\u9fa5]+市?)\s*[-\s]*([\u4e00-\u9fa5]+区)'
            ]
            
            for pattern in location_patterns:
                location_match = re.search(pattern, item_text)
                if location_match:
                    city = location_match.group(1).replace('市', '')
                    district = location_match.group(2)
                    job_data["工作地点"] = f"{city} - {district}"
                    break
            
            # 提取学历要求
            education_patterns = [
                r'(博士|硕士|研究生|本科|大专|专科|高中|中专|初中|不限).*学历',
                r'学历.*(博士|硕士|研究生|本科|大专|专科|高中|中专|初中|不限)',
                r'(博士|硕士|研究生|本科|大专|专科)以上',
                r'(博士|硕士|研究生|本科|大专|专科|高中|中专|初中)'
            ]
            
            for pattern in education_patterns:
                edu_match = re.search(pattern, item_text)
                if edu_match:
                    education_text = edu_match.group(0)
                    # 将初中、中专、高中统一显示为学历不限
                    if any(low_edu in education_text for low_edu in ['初中', '中专', '高中']):
                        job_data["学历要求"] = "学历不限"
                    else:
                        job_data["学历要求"] = education_text
                    break
            
            # 提取工作经验
            exp_patterns = [
                r'(\d+)[-~](\d+)年.*经验',
                r'经验.*(\d+)[-~](\d+)年',
                r'(\d+)年以上.*经验',
                r'经验.*(\d+)年以上',
                r'(无需经验|不限经验|应届毕业生)'
            ]
            
            for pattern in exp_patterns:
                exp_match = re.search(pattern, item_text)
                if exp_match:
                    job_data["岗位要求"] = exp_match.group(0)
                    break
            
            # 提取发布时间
            time_patterns = [
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{2}-\d{2})',
                r'(今天|昨天|前天)',
                r'(\d+)小时前',
                r'(\d+)天前'
            ]
            
            for pattern in time_patterns:
                time_match = re.search(pattern, item_text)
                if time_match:
                    job_data["发布时间"] = time_match.group(0)
                    break
            
            # 尝试提取企业名称（通常在职位附近）- 只匹配包含"公司"字的企业名称
            company_patterns = [
                r'([\u4e00-\u9fa5]+公司)',
                r'([A-Za-z]+(?:公司|Company))'
            ]
            
            for pattern in company_patterns:
                company_match = re.search(pattern, item_text)
                if company_match:
                    company_name = company_match.group(1)
                    # 过滤掉以特定内容开头的企业名称，确保包含"公司"字
                    # 同时检查企业名称长度（3-20个字）和非空
                    if (company_name and len(company_name) >= 3 and len(company_name) <= 20 and
                        not company_name.startswith('微信扫一扫快速求职') and '公司' in company_name):
                        job_data["企业名称"] = company_name
                        break
                    
        except Exception as e:
            print(f"提取职位项目信息失败: {e}")
            
        return job_data
    
    def extract_jobs_from_full_page(self, soup):
        """从整个页面提取职位信息"""
        jobs_data = []
        
        try:
            page_text = soup.get_text()
            
            # 查找所有薪资信息作为职位的标识
            salary_pattern = r'(\d+)[-~](\d+)元/月'
            salary_matches = re.finditer(salary_pattern, page_text)
            
            for i, match in enumerate(salary_matches):
                if i >= 10:  # 限制10个职位
                    break
                    
                job_data = {
                    "企业名称": f"58同城招聘企业{i+1}",
                    "企业类型": "互联网/通信",
                    "社会信用码": "",
                    "企业规模": "",
                    "注册资本(万)": "",
                    "所属区域": "北京",
                    "联系人": "",
                    "联系方式": "",
                    "联系邮箱": "",
                    "办公地址": "",
                    "企业简介": "",
                    "营业执照": "",
                    "企业相册": "",
                    "岗位名称": f"技术岗位{i+1}",
                    "薪资类型": "月薪",
                    "薪资范围起": match.group(1),
                    "薪资范围至": match.group(2),
                    "工作地点": "北京",
                    "岗位要求": "相关工作经验",
                    "学历要求": "本科",
                    "招聘人数": "若干",
                    "发布时间": datetime.now().strftime("%Y-%m-%d"),
                    "结束时间": "",
                    "工作职责": "负责相关技术工作",
                    "任职要求": "具备相关技能和经验"
                }
                
                jobs_data.append(job_data)
                
        except Exception as e:
            print(f"从整个页面提取职位信息失败: {e}")
            
        return jobs_data
    
    def clear_excel_data(self, filename="58同城职位详细信息.xlsx"):
        """清空Excel文件的数据行，保留表头"""
        import os
        
        if os.path.exists(filename):
            try:
                # 读取现有文件获取表头
                existing_df = pd.read_excel(filename)
                
                # 创建只有表头的空DataFrame
                empty_df = pd.DataFrame(columns=existing_df.columns)
                
                # 保存空DataFrame（只有表头）
                empty_df.to_excel(filename, index=False)
                print(f"✓ 已清空 {filename} 的数据行，保留表头（共 {len(existing_df.columns)} 列）")
                
            except Exception as e:
                print(f"清空Excel文件失败: {e}")
                # 如果读取失败，创建一个带有标准表头的空文件
                standard_columns = [
                    '职位名称', '企业名称', '薪资范围起', '薪资范围止', '薪资单位', '工作地点', 
                    '所属区域', '发布时间', '学历要求', '工作经验', '工作职责', '职位要求', 
                    '企业规模', '企业类型', '企业地址', '抓取城市', '抓取时间'
                ]
                empty_df = pd.DataFrame(columns=standard_columns)
                empty_df.to_excel(filename, index=False)
                print(f"创建新的Excel文件 {filename} 并设置标准表头")
        else:
            print(f"文件 {filename} 不存在，将在保存数据时创建")
    
    def save_to_excel(self, data, filename="58同城职位详细信息.xlsx"):
        """保存数据到Excel文件"""
        if data:
            # 处理数据：补充所属区域和过滤条件
            processed_data = []
            for job in data:
                # 过滤掉企业名称为空的数据
                if not job.get('企业名称') or job.get('企业名称').strip() == '':
                    continue
                
                # 过滤掉工作职责为空的数据
                if not job.get('工作职责') or job.get('工作职责').strip() == '':
                    continue
                
                # 过滤掉任职要求为空的数据
                if not job.get('任职要求') or job.get('任职要求').strip() == '':
                    continue
                
                # 处理所属区域：如果为空，用工作地点的值替代，去掉横线并格式化
                if not job.get('所属区域') or job.get('所属区域').strip() == '':
                    work_location = job.get('工作地点', '')
                    if work_location and work_location.strip():
                        # 去掉横线，将"北京 - 大兴"格式转换为"北京大兴区"格式
                        formatted_location = work_location.replace(' - ', '').replace('-', '').strip()
                        # 如果不包含"区"字且长度大于2，添加"区"
                        if '区' not in formatted_location and len(formatted_location) > 2:
                            formatted_location += '区'
                        job['所属区域'] = formatted_location
                
                # 进一步清理所属区域，去除"总部位于"前缀和其他多余文字，只保留"XX省XX市XX区"或"XX市XX区"格式
                if job.get('所属区域'):
                    region = job['所属区域']
                    # 去除"总部位于"前缀
                    region = re.sub(r'^总部位于', '', region).strip()
                    
                    # 过滤掉包含无关词汇的内容
                    unwanted_keywords = ['找工作', '免费发布', '登记简历', '公司福利', '饭补', '加班补助', 
                                        '交通便利', '餐补', '市中心区', '不匹配', '人公司', '福利', '补助', '便利',
                                        '有限公司', '科技有限公司', '信息科技', '华南地区', '华北地区', '华东地区', 
                                        '华西地区', '在华', '地区', '公司在']
                    if any(unwanted in region for unwanted in unwanted_keywords):
                        job['所属区域'] = ''  # 如果包含无关词汇，清空该字段
                    else:
                        # 城市到省份的映射字典
                        city_to_province = {
                            '广州': '广东', '深圳': '广东', '东莞': '广东', '佛山': '广东', '中山': '广东', '珠海': '广东', '惠州': '广东', '江门': '广东', '湛江': '广东', '茂名': '广东', '肇庆': '广东', '梅州': '广东', '汕头': '广东', '河源': '广东', '阳江': '广东', '清远': '广东', '韶关': '广东', '揭阳': '广东', '潮州': '广东', '云浮': '广东', '汕尾': '广东',
                            '杭州': '浙江', '宁波': '浙江', '温州': '浙江', '嘉兴': '浙江', '湖州': '浙江', '绍兴': '浙江', '金华': '浙江', '衢州': '浙江', '舟山': '浙江', '台州': '浙江', '丽水': '浙江',
                            '南京': '江苏', '苏州': '江苏', '无锡': '江苏', '常州': '江苏', '镇江': '江苏', '南通': '江苏', '泰州': '江苏', '扬州': '江苏', '盐城': '江苏', '连云港': '江苏', '徐州': '江苏', '淮安': '江苏', '宿迁': '江苏',
                            '济南': '山东', '青岛': '山东', '淄博': '山东', '枣庄': '山东', '东营': '山东', '烟台': '山东', '潍坊': '山东', '济宁': '山东', '泰安': '山东', '威海': '山东', '日照': '山东', '临沂': '山东', '德州': '山东', '聊城': '山东', '滨州': '山东', '菏泽': '山东',
                            '郑州': '河南', '开封': '河南', '洛阳': '河南', '平顶山': '河南', '安阳': '河南', '鹤壁': '河南', '新乡': '河南', '焦作': '河南', '濮阳': '河南', '许昌': '河南', '漯河': '河南', '三门峡': '河南', '南阳': '河南', '商丘': '河南', '信阳': '河南', '周口': '河南', '驻马店': '河南',
                            '武汉': '湖北', '黄石': '湖北', '十堰': '湖北', '宜昌': '湖北', '襄阳': '湖北', '鄂州': '湖北', '荆门': '湖北', '孝感': '湖北', '荆州': '湖北', '黄冈': '湖北', '咸宁': '湖北', '随州': '湖北',
                            '长沙': '湖南', '株洲': '湖南', '湘潭': '湖南', '衡阳': '湖南', '邵阳': '湖南', '岳阳': '湖南', '常德': '湖南', '张家界': '湖南', '益阳': '湖南', '郴州': '湖南', '永州': '湖南', '怀化': '湖南', '娄底': '湖南',
                            '南昌': '江西', '景德镇': '江西', '萍乡': '江西', '九江': '江西', '新余': '江西', '鹰潭': '江西', '赣州': '江西', '吉安': '江西', '宜春': '江西', '抚州': '江西', '上饶': '江西',
                            '合肥': '安徽', '芜湖': '安徽', '蚌埠': '安徽', '淮南': '安徽', '马鞍山': '安徽', '淮北': '安徽', '铜陵': '安徽', '安庆': '安徽', '黄山': '安徽', '滁州': '安徽', '阜阳': '安徽', '宿州': '安徽', '六安': '安徽', '亳州': '安徽', '池州': '安徽', '宣城': '安徽',
                            '福州': '福建', '厦门': '福建', '莆田': '福建', '三明': '福建', '泉州': '福建', '漳州': '福建', '南平': '福建', '龙岩': '福建', '宁德': '福建',
                            '石家庄': '河北', '唐山': '河北', '秦皇岛': '河北', '邯郸': '河北', '邢台': '河北', '保定': '河北', '张家口': '河北', '承德': '河北', '沧州': '河北', '廊坊': '河北', '衡水': '河北',
                            '太原': '山西', '大同': '山西', '阳泉': '山西', '长治': '山西', '晋城': '山西', '朔州': '山西', '晋中': '山西', '运城': '山西', '忻州': '山西', '临汾': '山西', '吕梁': '山西',
                            '沈阳': '辽宁', '大连': '辽宁', '鞍山': '辽宁', '抚顺': '辽宁', '本溪': '辽宁', '丹东': '辽宁', '锦州': '辽宁', '营口': '辽宁', '阜新': '辽宁', '辽阳': '辽宁', '盘锦': '辽宁', '铁岭': '辽宁', '朝阳': '辽宁', '葫芦岛': '辽宁',
                            '长春': '吉林', '吉林': '吉林', '四平': '吉林', '辽源': '吉林', '通化': '吉林', '白山': '吉林', '松原': '吉林', '白城': '吉林',
                            '哈尔滨': '黑龙江', '齐齐哈尔': '黑龙江', '鸡西': '黑龙江', '鹤岗': '黑龙江', '双鸭山': '黑龙江', '大庆': '黑龙江', '伊春': '黑龙江', '佳木斯': '黑龙江', '七台河': '黑龙江', '牡丹江': '黑龙江', '黑河': '黑龙江', '绥化': '黑龙江',
                            '成都': '四川', '自贡': '四川', '攀枝花': '四川', '泸州': '四川', '德阳': '四川', '绵阳': '四川', '广元': '四川', '遂宁': '四川', '内江': '四川', '乐山': '四川', '南充': '四川', '眉山': '四川', '宜宾': '四川', '广安': '四川', '达州': '四川', '雅安': '四川', '巴中': '四川', '资阳': '四川',
                            '贵阳': '贵州', '六盘水': '贵州', '遵义': '贵州', '安顺': '贵州', '毕节': '贵州', '铜仁': '贵州',
                            '昆明': '云南', '曲靖': '云南', '玉溪': '云南', '保山': '云南', '昭通': '云南', '丽江': '云南', '普洱': '云南', '临沧': '云南',
                            '西安': '陕西', '铜川': '陕西', '宝鸡': '陕西', '咸阳': '陕西', '渭南': '陕西', '延安': '陕西', '汉中': '陕西', '榆林': '陕西', '安康': '陕西', '商洛': '陕西',
                            '兰州': '甘肃', '嘉峪关': '甘肃', '金昌': '甘肃', '白银': '甘肃', '天水': '甘肃', '武威': '甘肃', '张掖': '甘肃', '平凉': '甘肃', '酒泉': '甘肃', '庆阳': '甘肃', '定西': '甘肃', '陇南': '甘肃',
                            '西宁': '青海', '海东': '青海',
                            '银川': '宁夏', '石嘴山': '宁夏', '吴忠': '宁夏', '固原': '宁夏', '中卫': '宁夏',
                            '乌鲁木齐': '新疆', '克拉玛依': '新疆', '吐鲁番': '新疆', '哈密': '新疆',
                            '呼和浩特': '内蒙古', '包头': '内蒙古', '乌海': '内蒙古', '赤峰': '内蒙古', '通辽': '内蒙古', '鄂尔多斯': '内蒙古', '呼伦贝尔': '内蒙古', '巴彦淖尔': '内蒙古', '乌兰察布': '内蒙古',
                            '拉萨': '西藏', '日喀则': '西藏', '昌都': '西藏', '林芝': '西藏', '山南': '西藏', '那曲': '西藏',
                            '海口': '海南', '三亚': '海南', '三沙': '海南', '儋州': '海南'
                        }
                        
                        # 首先处理"广州荔湾区"这种格式（城市+区域，缺少"市"字）
                        city_district_match = re.search(r'^([\u4e00-\u9fa5]{2,4})([\u4e00-\u9fa5]{2,4}区)$', region)
                        if city_district_match:
                            city = city_district_match.group(1)
                            district = city_district_match.group(2)
                            
                            # 检查城市名是否在映射字典中，如果是则使用省市格式
                            if city in city_to_province:
                                province_name = city_to_province[city]
                                fixed_region = f"{province_name}省{city}市"
                            else:
                                fixed_region = f"{city}市{district}"
                            print(f"✓ 所属区域已自动修复: {region} -> {fixed_region}")
                            job['所属区域'] = fixed_region
                        else:
                            # 处理其他格式
                            city_fix_match = re.search(r'([\u4e00-\u9fa5]{2,4})(省)?([\u4e00-\u9fa5]{2,4})(市)?([\u4e00-\u9fa5]{2,4}区)', region)
                            if city_fix_match:
                                province = city_fix_match.group(1)
                                has_province = city_fix_match.group(2) is not None
                                city = city_fix_match.group(3)
                                has_city_suffix = city_fix_match.group(4) is not None
                                district = city_fix_match.group(5)
                                
                                # 构建标准格式（只对广东省去掉区级信息）
                                guangdong_cities = ['广州', '深圳', '珠海', '汕头', '佛山', '韶关', '湛江', '肇庆', '江门', '茂名', '惠州', '梅州', '汕尾', '河源', '阳江', '清远', '东莞', '中山', '潮州', '揭阳', '云浮']
                                
                                if has_province and not has_city_suffix:
                                    # "XX省XX区" -> 只对广东省去掉区级信息
                                    if province == '广东' and city in guangdong_cities:
                                        fixed_region = f"{province}省{city}市"
                                    else:
                                        fixed_region = f"{province}省{city}市{district}"
                                    job['所属区域'] = fixed_region
                                elif not has_province and not has_city_suffix:
                                    # "XXXX区" -> 根据城市名判断是否为广东省
                                    if len(city) >= 2:
                                        if city in guangdong_cities:
                                            fixed_region = f"广东省{city}市"
                                        elif city in city_to_province:
                                            province_name = city_to_province[city]
                                            fixed_region = f"{province_name}省{city}市{district}"
                                        else:
                                            fixed_region = f"{city}市{district}"
                                        job['所属区域'] = fixed_region
                                    else:
                                        job['所属区域'] = region  # 保持原样
                                elif not has_province and has_city_suffix:
                                    # "XX市XX区" -> 根据城市名判断是否为广东省
                                    if city in guangdong_cities:
                                        fixed_region = f"广东省{city}市"
                                    elif city in city_to_province:
                                        province_name = city_to_province[city]
                                        fixed_region = f"{province_name}省{city}市{district}"
                                    else:
                                        fixed_region = f"{city}市{district}"
                                    job['所属区域'] = fixed_region
                                else:
                                    # 已经是标准格式，只对广东省去掉区级信息
                                    if has_province and has_city_suffix:
                                        if province == '广东' and city in guangdong_cities:
                                            fixed_region = f"{province}省{city}市"
                                            job['所属区域'] = fixed_region
                                    else:
                                        job['所属区域'] = region  # 保持原样
                            
                            # 如果修复失败，尝试原有的正则匹配
                            # 优先查找"XX省XX市XX区"格式，然后查找"XX市XX区"格式
                            region_match = re.search(r'([\u4e00-\u9fa5]{2,4}省[\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)', region)
                            if not region_match:
                                region_match = re.search(r'([\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)', region)
                            if region_match:
                                clean_region = region_match.group(1)
                                # 检查是否为省市区格式，如果是则去掉区级信息
                                province_city_match = re.search(r'([\u4e00-\u9fa5]{2,4})省([\u4e00-\u9fa5]{2,4})市', clean_region)
                                if province_city_match:
                                    province_name = province_city_match.group(1)
                                    city_name = province_city_match.group(2)
                                    clean_region = f"{province_name}省{city_name}市"
                                # 确保长度合理
                                if len(clean_region) <= 10:
                                    job['所属区域'] = clean_region
                                else:
                                    job['所属区域'] = ''
                            else:
                                # 如果没有匹配到标准格式，清空该字段
                                job['所属区域'] = ''
                
                processed_data.append(job)
            
            if processed_data:
                df = pd.DataFrame(processed_data)
                df.to_excel(filename, index=False)
                print(f"数据已保存到 {filename}")
                
                # 同时导出JSON文件
                json_filename = filename.replace('.xlsx', '.json')
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(processed_data, f, ensure_ascii=False, indent=2)
                print(f"数据已同时导出为JSON: {json_filename}")
                
                # 打印详细统计信息
                print(f"\n=== 数据统计 ===")
                print(f"原始职位数: {len(data)}")
                print(f"过滤后职位数: {len(processed_data)}")
                filtered_count = len(data) - len(processed_data)
                print(f"过滤掉的职位数（企业名称为空、工作职责为空或任职要求为空）: {filtered_count}")
                print(f"有薪资信息的职位: {len([job for job in processed_data if job.get('薪资范围起')])}")
                print(f"有工作地点的职位: {len([job for job in processed_data if job.get('工作地点')])}")
                print(f"有学历要求的职位: {len([job for job in processed_data if job.get('学历要求')])}")
                print(f"所属区域已补充的职位: {len([job for job in processed_data if job.get('所属区域')])}")
                
                return True
            else:
                print("过滤后没有有效数据可保存（所有职位的企业名称、工作职责或任职要求都为空）")
                return False
        else:
            print("没有数据可保存")
            return False
    
    def save_single_job_to_excel(self, job_data, filename="58同城职位详细信息.xlsx"):
        """实时保存单个职位数据到Excel文件"""
        import os
        
        # 检查企业名称是否为空，如果为空则不保存
        if not job_data or not job_data.get('企业名称') or job_data.get('企业名称').strip() == '':
            log_error(f"× 跳过保存：企业名称为空的职位数据 - {job_data.get('岗位名称', 'N/A') if job_data else 'N/A'}")
            return False
        
        # 检查工作职责是否为空，如果为空则不保存
        if not job_data.get('工作职责') or job_data.get('工作职责').strip() == '':
            log_error(f"× 跳过保存：工作职责为空的职位数据 - {job_data.get('岗位名称', 'N/A')} - {job_data.get('企业名称', 'N/A')}")
            return False
        
        # 检查任职要求是否为空，如果为空则不保存
        if not job_data.get('任职要求') or job_data.get('任职要求').strip() == '':
            log_error(f"× 跳过保存：任职要求为空的职位数据 - {job_data.get('岗位名称', 'N/A')} - {job_data.get('企业名称', 'N/A')}")
            return False
        
        # 处理所属区域：如果为空，用工作地点的值替代，去掉横线并格式化
        if not job_data.get('所属区域') or job_data.get('所属区域').strip() == '':
            work_location = job_data.get('工作地点', '')
            if work_location and work_location.strip():
                # 去掉横线，将"北京 - 大兴"格式转换为"北京大兴区"格式
                formatted_location = work_location.replace(' - ', '').replace('-', '').strip()
                # 如果不包含"区"字且长度大于2，添加"区"
                if '区' not in formatted_location and len(formatted_location) > 2:
                    formatted_location += '区'
                job_data['所属区域'] = formatted_location
                print(f"✓ 所属区域已从工作地点补充: {work_location} -> {formatted_location}")
        
        # 进一步清理所属区域，去除"总部位于"前缀和其他多余文字，只保留"XX省XX市XX区"或"XX市XX区"格式
        if job_data.get('所属区域'):
            region = job_data['所属区域']
            # 去除"总部位于"前缀
            region = re.sub(r'^总部位于', '', region).strip()
            
            # 过滤掉包含无关词汇的内容
            unwanted_keywords = ['找工作', '免费发布', '登记简历', '公司福利', '饭补', '加班补助', 
                                '交通便利', '餐补', '市中心区', '不匹配', '人公司', '福利', '补助', '便利',
                                '有限公司', '科技有限公司', '信息科技', '华南地区', '华北地区', '华东地区', 
                                '华西地区', '在华', '地区', '公司在']
            if any(unwanted in region for unwanted in unwanted_keywords):
                job_data['所属区域'] = ''  # 如果包含无关词汇，清空该字段
                print(f"× 所属区域包含无关内容已清空: {region}")
            else:
                # 城市到省份的映射字典
                city_to_province = {
                    '广州': '广东', '深圳': '广东', '东莞': '广东', '佛山': '广东', '中山': '广东', '珠海': '广东', '惠州': '广东', '江门': '广东', '湛江': '广东', '茂名': '广东', '肇庆': '广东', '梅州': '广东', '汕头': '广东', '河源': '广东', '阳江': '广东', '清远': '广东', '韶关': '广东', '揭阳': '广东', '潮州': '广东', '云浮': '广东', '汕尾': '广东',
                    '杭州': '浙江', '宁波': '浙江', '温州': '浙江', '嘉兴': '浙江', '湖州': '浙江', '绍兴': '浙江', '金华': '浙江', '衢州': '浙江', '舟山': '浙江', '台州': '浙江', '丽水': '浙江',
                    '南京': '江苏', '苏州': '江苏', '无锡': '江苏', '常州': '江苏', '镇江': '江苏', '南通': '江苏', '泰州': '江苏', '扬州': '江苏', '盐城': '江苏', '连云港': '江苏', '徐州': '江苏', '淮安': '江苏', '宿迁': '江苏',
                    '济南': '山东', '青岛': '山东', '淄博': '山东', '枣庄': '山东', '东营': '山东', '烟台': '山东', '潍坊': '山东', '济宁': '山东', '泰安': '山东', '威海': '山东', '日照': '山东', '临沂': '山东', '德州': '山东', '聊城': '山东', '滨州': '山东', '菏泽': '山东',
                    '郑州': '河南', '开封': '河南', '洛阳': '河南', '平顶山': '河南', '安阳': '河南', '鹤壁': '河南', '新乡': '河南', '焦作': '河南', '濮阳': '河南', '许昌': '河南', '漯河': '河南', '三门峡': '河南', '南阳': '河南', '商丘': '河南', '信阳': '河南', '周口': '河南', '驻马店': '河南',
                    '武汉': '湖北', '黄石': '湖北', '十堰': '湖北', '宜昌': '湖北', '襄阳': '湖北', '鄂州': '湖北', '荆门': '湖北', '孝感': '湖北', '荆州': '湖北', '黄冈': '湖北', '咸宁': '湖北', '随州': '湖北',
                    '长沙': '湖南', '株洲': '湖南', '湘潭': '湖南', '衡阳': '湖南', '邵阳': '湖南', '岳阳': '湖南', '常德': '湖南', '张家界': '湖南', '益阳': '湖南', '郴州': '湖南', '永州': '湖南', '怀化': '湖南', '娄底': '湖南',
                    '南昌': '江西', '景德镇': '江西', '萍乡': '江西', '九江': '江西', '新余': '江西', '鹰潭': '江西', '赣州': '江西', '吉安': '江西', '宜春': '江西', '抚州': '江西', '上饶': '江西',
                    '合肥': '安徽', '芜湖': '安徽', '蚌埠': '安徽', '淮南': '安徽', '马鞍山': '安徽', '淮北': '安徽', '铜陵': '安徽', '安庆': '安徽', '黄山': '安徽', '滁州': '安徽', '阜阳': '安徽', '宿州': '安徽', '六安': '安徽', '亳州': '安徽', '池州': '安徽', '宣城': '安徽',
                    '福州': '福建', '厦门': '福建', '莆田': '福建', '三明': '福建', '泉州': '福建', '漳州': '福建', '南平': '福建', '龙岩': '福建', '宁德': '福建',
                    '石家庄': '河北', '唐山': '河北', '秦皇岛': '河北', '邯郸': '河北', '邢台': '河北', '保定': '河北', '张家口': '河北', '承德': '河北', '沧州': '河北', '廊坊': '河北', '衡水': '河北',
                    '太原': '山西', '大同': '山西', '阳泉': '山西', '长治': '山西', '晋城': '山西', '朔州': '山西', '晋中': '山西', '运城': '山西', '忻州': '山西', '临汾': '山西', '吕梁': '山西',
                    '沈阳': '辽宁', '大连': '辽宁', '鞍山': '辽宁', '抚顺': '辽宁', '本溪': '辽宁', '丹东': '辽宁', '锦州': '辽宁', '营口': '辽宁', '阜新': '辽宁', '辽阳': '辽宁', '盘锦': '辽宁', '铁岭': '辽宁', '朝阳': '辽宁', '葫芦岛': '辽宁',
                    '长春': '吉林', '吉林': '吉林', '四平': '吉林', '辽源': '吉林', '通化': '吉林', '白山': '吉林', '松原': '吉林', '白城': '吉林',
                    '哈尔滨': '黑龙江', '齐齐哈尔': '黑龙江', '鸡西': '黑龙江', '鹤岗': '黑龙江', '双鸭山': '黑龙江', '大庆': '黑龙江', '伊春': '黑龙江', '佳木斯': '黑龙江', '七台河': '黑龙江', '牡丹江': '黑龙江', '黑河': '黑龙江', '绥化': '黑龙江',
                    '成都': '四川', '自贡': '四川', '攀枝花': '四川', '泸州': '四川', '德阳': '四川', '绵阳': '四川', '广元': '四川', '遂宁': '四川', '内江': '四川', '乐山': '四川', '南充': '四川', '眉山': '四川', '宜宾': '四川', '广安': '四川', '达州': '四川', '雅安': '四川', '巴中': '四川', '资阳': '四川',
                    '贵阳': '贵州', '六盘水': '贵州', '遵义': '贵州', '安顺': '贵州', '毕节': '贵州', '铜仁': '贵州',
                    '昆明': '云南', '曲靖': '云南', '玉溪': '云南', '保山': '云南', '昭通': '云南', '丽江': '云南', '普洱': '云南', '临沧': '云南',
                    '西安': '陕西', '铜川': '陕西', '宝鸡': '陕西', '咸阳': '陕西', '渭南': '陕西', '延安': '陕西', '汉中': '陕西', '榆林': '陕西', '安康': '陕西', '商洛': '陕西',
                    '兰州': '甘肃', '嘉峪关': '甘肃', '金昌': '甘肃', '白银': '甘肃', '天水': '甘肃', '武威': '甘肃', '张掖': '甘肃', '平凉': '甘肃', '酒泉': '甘肃', '庆阳': '甘肃', '定西': '甘肃', '陇南': '甘肃',
                    '西宁': '青海', '海东': '青海',
                    '银川': '宁夏', '石嘴山': '宁夏', '吴忠': '宁夏', '固原': '宁夏', '中卫': '宁夏',
                    '乌鲁木齐': '新疆', '克拉玛依': '新疆', '吐鲁番': '新疆', '哈密': '新疆',
                    '呼和浩特': '内蒙古', '包头': '内蒙古', '乌海': '内蒙古', '赤峰': '内蒙古', '通辽': '内蒙古', '鄂尔多斯': '内蒙古', '呼伦贝尔': '内蒙古', '巴彦淖尔': '内蒙古', '乌兰察布': '内蒙古',
                    '拉萨': '西藏', '日喀则': '西藏', '昌都': '西藏', '林芝': '西藏', '山南': '西藏', '那曲': '西藏',
                    '海口': '海南', '三亚': '海南', '三沙': '海南', '儋州': '海南'
                }
                
                # 首先处理直辖市格式"北京朝阳区"这种格式
                municipality_district_match = re.search(r'^(北京|上海|天津|重庆)([\u4e00-\u9fa5]{2,4}区)$', region)
                if municipality_district_match:
                    municipality = municipality_district_match.group(1)
                    district = municipality_district_match.group(2)
                    fixed_region = f"{municipality}市{district}"
                    print(f"✓ 所属区域已自动修复: {region} -> {fixed_region}")
                    job_data['所属区域'] = fixed_region
                else:
                     # 处理"广州荔湾区"这种格式（城市+区域，缺少"市"字）
                     city_district_match = re.search(r'^([\u4e00-\u9fa5]{2,4})([\u4e00-\u9fa5]{2,4}区)$', region)
                     if city_district_match:
                         city = city_district_match.group(1)
                         district = city_district_match.group(2)
                         
                         # 广东省城市列表
                         guangdong_cities = ['广州', '深圳', '珠海', '汕头', '佛山', '韶关', '湛江', '肇庆', '江门', '茂名', '惠州', '梅州', '汕尾', '河源', '阳江', '清远', '东莞', '中山', '潮州', '揭阳', '云浮']
                         
                         # 检查城市名是否在映射字典中
                         if city in city_to_province:
                             province_name = city_to_province[city]
                             # 对广东省的城市去掉区级信息
                             if city in guangdong_cities:
                                 fixed_region = f"{province_name}省{city}市"
                             else:
                                 fixed_region = f"{province_name}省{city}市{district}"
                             print(f"✓ 所属区域已自动修复: {region} -> {fixed_region}")
                             job_data['所属区域'] = fixed_region
                         else:
                             # 如果城市名不在映射中，只添加"市"字
                             fixed_region = f"{city}市{district}"
                             print(f"✓ 所属区域已自动修复: {region} -> {fixed_region}")
                             job_data['所属区域'] = fixed_region
                     else:
                         # 处理其他格式
                         # 匹配"XX省XX区"或"XX市XX区"或"XXXX区"格式，并自动补充"省"和"市"字
                         city_fix_match = re.search(r'([\u4e00-\u9fa5]{2,4})(省)?([\u4e00-\u9fa5]{2,4})(市)?([\u4e00-\u9fa5]{2,4}区)', region)
                         if city_fix_match:
                             province = city_fix_match.group(1)
                             has_province = city_fix_match.group(2) is not None
                             city = city_fix_match.group(3)
                             has_city_suffix = city_fix_match.group(4) is not None
                             district = city_fix_match.group(5)
                             
                             # 构建标准格式（对所有省份去掉区级信息）
                             
                             if has_province and not has_city_suffix:
                                 # "XX省XX区" -> 只对广东省去掉区级信息
                                 if province == '广东':
                                     fixed_region = f"{province}省{city}市"
                                 else:
                                     fixed_region = f"{province}省{city}市{district}"
                                 print(f"✓ 所属区域已自动修复: {region} -> {fixed_region}")
                                 job_data['所属区域'] = fixed_region
                             elif not has_province and not has_city_suffix:
                                 # "XXXX区" -> 根据城市名判断省份并去掉区级信息
                                 if len(city) >= 2:
                                     if city in city_to_province:
                                         province_name = city_to_province[city]
                                         fixed_region = f"{province_name}省{city}市"
                                     else:
                                         fixed_region = f"{city}市{district}"
                                     print(f"✓ 所属区域已自动修复: {region} -> {fixed_region}")
                                     job_data['所属区域'] = fixed_region
                                 else:
                                     job_data['所属区域'] = region  # 保持原样
                             elif not has_province and has_city_suffix:
                                 # "XX市XX区" -> 根据城市名判断是否为广东省
                                 guangdong_cities = ['广州', '深圳', '珠海', '汕头', '佛山', '韶关', '湛江', '肇庆', '江门', '茂名', '惠州', '梅州', '汕尾', '河源', '阳江', '清远', '东莞', '中山', '潮州', '揭阳', '云浮']
                                 if city in guangdong_cities:
                                     fixed_region = f"广东省{city}市"
                                 elif city in city_to_province:
                                     province_name = city_to_province[city]
                                     fixed_region = f"{province_name}省{city}市{district}"
                                 else:
                                     fixed_region = f"{city}市{district}"
                                 print(f"✓ 所属区域已自动修复: {region} -> {fixed_region}")
                                 job_data['所属区域'] = fixed_region
                             else:
                                 # 已经是标准格式，只对广东省去掉区级信息
                                 if has_province and has_city_suffix:
                                     guangdong_cities = ['广州', '深圳', '珠海', '汕头', '佛山', '韶关', '湛江', '肇庆', '江门', '茂名', '惠州', '梅州', '汕尾', '河源', '阳江', '清远', '东莞', '中山', '潮州', '揭阳', '云浮']
                                     if province == '广东' and city in guangdong_cities:
                                         fixed_region = f"{province}省{city}市"
                                         print(f"✓ 所属区域已自动修复: {region} -> {fixed_region}")
                                         job_data['所属区域'] = fixed_region
                                     else:
                                         job_data['所属区域'] = region  # 保持原样
                                 else:
                                     job_data['所属区域'] = region  # 保持原样
                         else:
                             # 如果修复失败，尝试原有的正则匹配
                             # 优先查找"XX省XX市XX区"格式，然后查找"XX市XX区"格式
                             region_match = re.search(r'([\u4e00-\u9fa5]{2,4}省[\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)', region)
                             if not region_match:
                                 region_match = re.search(r'([\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区)', region)
                             
                             # 如果还没匹配到，尝试匹配直辖市格式"XX丰台区"并自动补充"市"字
                             if not region_match:
                                 # 匹配直辖市格式：北京、上海、天津、重庆 + 区名
                                 municipality_match = re.search(r'(北京|上海|天津|重庆)([\u4e00-\u9fa5]{2,4}区)', region)
                                 if municipality_match:
                                     municipality = municipality_match.group(1)
                                     district = municipality_match.group(2)
                                     clean_region = f"{municipality}市{district}"
                                     print(f"✓ 直辖市格式已标准化: {region} -> {clean_region}")
                                     job_data['所属区域'] = clean_region
                                 else:
                                     # 尝试匹配其他城市格式"XX高新区"、"XX开发区"等
                                     city_district_match = re.search(r'([\u4e00-\u9fa5]{2,4})(高新区|开发区|经济区|新区|工业区|科技园|软件园)', region)
                                     if city_district_match:
                                         city = city_district_match.group(1)
                                         district = city_district_match.group(2)
                                         # 检查是否为广东省的城市
                                         guangdong_cities = ['广州', '深圳', '珠海', '汕头', '佛山', '韶关', '湛江', '肇庆', '江门', '茂名', '惠州', '梅州', '汕尾', '河源', '阳江', '清远', '东莞', '中山', '潮州', '揭阳', '云浮']
                                         if city in guangdong_cities:
                                             clean_region = f"广东省{city}市"
                                         else:
                                             clean_region = f"{city}市{district}"
                                         print(f"✓ 城市区域格式已标准化: {region} -> {clean_region}")
                                         job_data['所属区域'] = clean_region
                                     else:
                                         # 如果没有匹配到任何标准格式，清空该字段
                                         job_data['所属区域'] = ''
                                         print(f"× 所属区域格式不标准已清空: {region}")
                             else:
                                 clean_region = region_match.group(1)
                                 # 检查是否为广东省，如果是则去掉区级信息
                                 guangdong_match = re.search(r'广东省([\u4e00-\u9fa5]{2,4})市', clean_region)
                                 if guangdong_match:
                                     city_name = guangdong_match.group(1)
                                     clean_region = f"广东省{city_name}市"
                                 # 确保长度合理
                                 if len(clean_region) <= 10:
                                     if clean_region != job_data['所属区域']:
                                         print(f"✓ 所属区域已清理: {job_data['所属区域']} -> {clean_region}")
                                     job_data['所属区域'] = clean_region
                                 else:
                                     job_data['所属区域'] = ''
                                     print(f"× 所属区域长度异常已清空: {clean_region}")
                
                # 最终验证修复后的格式是否符合标准
                final_region = job_data.get('所属区域', '')
                if final_region:
                    # 验证最终格式是否为"XX省XX市"、"XX市"、"XX市XX区"或"XX省XX市XX区"格式
                    if not (re.match(r'^[\u4e00-\u9fa5]{2,4}省[\u4e00-\u9fa5]{2,4}市$', final_region) or 
                           re.match(r'^[\u4e00-\u9fa5]{2,4}市$', final_region) or
                           re.match(r'^[\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区$', final_region) or
                           re.match(r'^[\u4e00-\u9fa5]{2,4}省[\u4e00-\u9fa5]{2,4}市[\u4e00-\u9fa5]{2,4}区$', final_region)):
                        job_data['所属区域'] = ''
                        print(f"× 所属区域最终格式验证失败已清空: {final_region}")

        # 检查所属区域是否为空，如果为空则不保存
        if not job_data.get('所属区域') or job_data.get('所属区域').strip() == '':
            log_error(f"× 跳过保存：所属区域为空的职位数据 - {job_data.get('岗位名称', 'N/A')} - {job_data.get('企业名称', 'N/A')}")
            return False

        if job_data:
            # 检查文件是否存在
            if os.path.exists(filename):
                # 文件存在，读取现有数据并追加
                existing_df = pd.read_excel(filename)
                new_df = pd.DataFrame([job_data])
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df.to_excel(filename, index=False)
                
                # 同时写入JSON文件
                json_filename = filename.replace('.xlsx', '.json')
                json_data = combined_df.to_dict('records')
                # 处理NaN值，将其替换为空字符串
                for record in json_data:
                    for key, value in record.items():
                        if pd.isna(value):
                            record[key] = ""
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
            else:
                # 文件不存在，创建新文件
                df = pd.DataFrame([job_data])
                df.to_excel(filename, index=False)
                
                # 同时创建JSON文件
                json_filename = filename.replace('.xlsx', '.json')
                json_data = df.to_dict('records')
                # 处理NaN值，将其替换为空字符串
                for record in json_data:
                    for key, value in record.items():
                        if pd.isna(value):
                            record[key] = ""
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 职位数据已实时保存到Excel和JSON: {job_data.get('岗位名称', 'N/A')} - {job_data.get('企业名称', 'N/A')}")
            return True
        return False
    

    
    def print_detailed_results(self, data):
        """打印详细的抓取结果"""
        print("\n=== 详细抓取结果 ===")
        for i, job in enumerate(data, 1):
            print(f"\n职位 {i}:")
            print(f"  企业名称: {job.get('企业名称', 'N/A')}")
            print(f"  岗位名称: {job.get('岗位名称', 'N/A')}")
            print(f"  薪资类型: {job.get('薪资类型', 'N/A')}")
            print(f"  薪资范围: {job.get('薪资范围起', 'N/A')}-{job.get('薪资范围至', 'N/A')}")
            print(f"  工作地点: {job.get('工作地点', 'N/A')}")
            print(f"  学历要求: {job.get('学历要求', 'N/A')}")
            print(f"  岗位要求: {job.get('岗位要求', 'N/A')}")
            print(f"  发布时间: {job.get('发布时间', 'N/A')}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()

def main():
    # 多个城市的URL列表（包含第一页和第二页）
    city_urls = {
        "北京": [
            "https://bj.58.com/hulianwangtx/",
        ],
        "上海": [
            "https://sh.58.com/hulianwangtx/",
        ],
        "广州": [
            "https://gz.58.com/hulianwangtx/",
        ],
        "深圳": [
            "https://sz.58.com/hulianwangtx/",
        ],
        "成都": [
            "https://cd.58.com/hulianwangtx/",
        ],
        "西安": [
            "https://xa.58.com/hulianwangtx/",
        ],
        "郑州": [
            "https://zz.58.com/hulianwangtx/",
        ]
    }
    
    scraper = Enhanced58JobScraper(headless=False)  # 设置为False可以看到浏览器操作
    
    # 清空Excel文件的数据行，保留表头
    scraper.clear_excel_data("58同城多城市职位详细信息.xlsx")
    
    # 清空JSON文件的所有数据
    json_filename = "58同城多城市职位详细信息.json"
    try:
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"✓ 已清空 {json_filename} 的所有数据")
    except Exception as e:
        print(f"清空JSON文件时出错: {e}")
    
    all_data = []  # 存储所有城市的数据
    
    try:
        for city_name, url_list in city_urls.items():
            print(f"\n开始抓取{city_name}的职位信息（前5页，当前页所有职位）...")
            
            try:
                # 使用第一个URL作为基础URL，抓取前5页
                base_url = url_list[0]
                
                # 抓取该城市前5页数据（当前页所有职位）
                city_data = scraper.scrape_multiple_pages(base_url, max_pages=5)
                
                if city_data:
                    # 为每个职位添加城市标识
                    for job in city_data:
                        job['抓取城市'] = city_name
                    
                    all_data.extend(city_data)
                    print(f"{city_name}成功抓取到 {len(city_data)} 个职位信息")
                else:
                    print(f"{city_name}未抓取到任何职位数据")
                    
            except Exception as e:
                print(f"{city_name}抓取出错: {e}")
                continue  # 继续抓取下一个城市
        
        if all_data:
            print(f"\n所有城市总共成功抓取到 {len(all_data)} 个职位信息")
            
            # 打印详细结果
            scraper.print_detailed_results(all_data)
            
            print("\n✓ 所有数据已通过实时保存功能写入Excel和JSON文件")
            
        else:
            print("所有城市都未抓取到任何职位数据")
            
    except Exception as e:
        print(f"程序执行出错: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()