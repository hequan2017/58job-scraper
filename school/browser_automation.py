#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宜宾职业技术学院信息自动化脚本
使用Selenium自动化浏览器访问指定页面并点击专业设置
"""

import os
import sys
import time
import logging
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# 屏蔽Chrome的日志输出
os.environ['WDM_LOG_LEVEL'] = '0'
os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

# 配置日志输出到文件
def setup_logging():
    """配置日志输出到文件"""
    # 创建logs目录
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 生成日志文件名（包含时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f'browser_automation_{timestamp}.log')
    
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)  # 同时输出到控制台
        ]
    )
    
    return log_file

# 自定义print函数，同时输出到日志
def log_print(message):
    """自定义打印函数，同时输出到控制台和日志文件"""
    print(message)
    logging.info(message)


class BrowserAutomation:
    """浏览器自动化类"""
    
    def __init__(self):
        """初始化浏览器配置"""
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        try:
            # Chrome浏览器选项配置
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            # 屏蔽USB设备相关错误信息和其他日志
            chrome_options.add_argument('--disable-usb-keyboard-detect')
            chrome_options.add_argument('--disable-device-discovery-notifications')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--log-level=3')  # 只显示致命错误
            chrome_options.add_argument('--silent')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--disable-ipc-flooding-protection')
            chrome_options.add_argument('--disable-component-update')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-domain-reliability')
            chrome_options.add_argument('--disable-background-networking')
            chrome_options.add_argument('--disable-sync')
            chrome_options.add_argument('--disable-translate')
            chrome_options.add_argument('--hide-scrollbars')
            chrome_options.add_argument('--mute-audio')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--no-default-browser-check')
            chrome_options.add_argument('--disable-hang-monitor')
            chrome_options.add_argument('--disable-prompt-on-repost')
            chrome_options.add_argument('--disable-client-side-phishing-detection')
            chrome_options.add_argument('--disable-component-extensions-with-background-pages')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            
            # 屏蔽更多日志输出
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            # 禁用图片加载以提升速度
            prefs = {
                "profile.managed_default_content_settings.images": 2,  # 禁用图片
                "profile.default_content_setting_values.media_stream": 2,  # 禁用媒体流
                "profile.default_content_settings.popups": 0,  # 禁用弹窗
                "profile.managed_default_content_settings.media_stream": 2  # 禁用视频
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # 禁用扩展和插件
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-plugins-discovery")
            
            # 设置用户代理
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # 使用指定的chromedriver.exe路径
            chromedriver_path = r"E:\360WiFi\58job-scraper\other\chromedriver-win32\chromedriver.exe"
            # 创建Service并屏蔽日志
            service = Service(chromedriver_path, log_path='NUL')  # Windows下使用NUL屏蔽日志
            
            print(f"🔧 使用ChromeDriver路径: {chromedriver_path}")
            
            # 创建WebDriver实例
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 执行脚本来隐藏webdriver属性
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 设置等待对象
            self.wait = WebDriverWait(self.driver, 10)
            
            print("✅ Chrome浏览器驱动设置成功（已禁用图片和视频加载）")
            return True
            
        except Exception as e:
            print(f"❌ 设置浏览器驱动失败: {e}")
            return False
    
    def visit_page(self, url):
        """访问指定页面"""
        try:
            print(f"🌐 正在访问页面: {url}")
            self.driver.get(url)
            
            # 等待页面加载
            time.sleep(1)
            
            print("✅ 页面访问成功")
            return True
            
        except Exception as e:
            print(f"❌ 访问页面失败: {e}")
            return False
    
    def click_major_settings(self):
        """点击专业设置元素"""
        try:
            print("🔍 正在查找'专业设置'元素...")
            
            # 多种选择器策略
            selectors = [
                # 根据提供的具体div结构
                "div.l-view.block.l-tabs-tab.text-center[data-log-click*='专业设置']",
                # 根据文本内容查找
                "//div[contains(@class, 'l-tabs-tab') and contains(text(), '专业设置')]",
                # 更宽泛的查找
                "//div[contains(text(), '专业设置')]",
                # 根据role属性查找
                "div[role='tab'][aria-selected='false']:contains('专业设置')"
            ]
            
            element = None
            
            # 尝试不同的选择器
            for i, selector in enumerate(selectors):
                try:
                    if selector.startswith("//"):
                        # XPath选择器
                        element = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS选择器
                        element = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    print(f"✅ 使用选择器 {i+1} 找到'专业设置'元素")
                    break
                    
                except Exception:
                    continue
            
            if element is None:
                # 如果上述方法都失败，尝试查找所有包含"专业设置"文本的元素
                print("🔄 尝试备用查找方法...")
                elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '专业设置')]")
                
                if elements:
                    element = elements[0]
                    print("✅ 使用备用方法找到'专业设置'元素")
                else:
                    raise Exception("未找到'专业设置'元素")
            
            # 滚动到元素位置
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            
            # 点击元素
            element.click()
            print("✅ 成功点击'专业设置'元素")
            
            # 等待页面响应
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"❌ 点击'专业设置'元素失败: {e}")
            
            # 打印页面源码用于调试（前1000个字符）
            try:
                page_source = self.driver.page_source[:1000]
                print(f"📄 页面源码片段: {page_source}")
            except:
                pass
                
            return False
    
    def click_view_more(self):
        """点击查看更多按钮"""
        try:
            print("🔍 正在查找'查看更多'按钮...")
            
            # 多种选择器策略（按成功率排序，最有效的在前面）
            selectors = [
                # 根据div内容查找父级a标签（最有效的选择器）
                "//a[.//div[contains(text(), '查看更多')]]",
                # 更宽泛的查找
                "//a[contains(text(), '查看更多')]",
                "//a[contains(@role, 'button') and contains(text(), '查看更多')]",
                "//a[contains(@href, 'magic_frame') and contains(text(), '查看更多')]"
            ]
            
            element = None
            
            # 等待页面加载完成
            time.sleep(1)
            
            # 尝试不同的选择器（现在都是XPath选择器）
            for i, selector in enumerate(selectors):
                try:
                    element = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"✅ 使用选择器 {i+1} 找到'查看更多'按钮")
                    break
                    
                except Exception:
                    continue
            
            if element is None:
                # 如果上述方法都失败，尝试查找所有包含"查看更多"文本的a标签
                print("🔄 尝试备用查找方法...")
                elements = self.driver.find_elements(By.XPATH, "//a[contains(text(), '查看更多') or .//div[contains(text(), '查看更多')]]")
                
                if elements:
                    element = elements[0]
                    print("✅ 使用备用方法找到'查看更多'按钮")
                else:
                    raise Exception("未找到'查看更多'按钮")
            
            # 滚动到元素位置
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            
            # 获取元素的href属性用于验证
            href = element.get_attribute('href')
            print(f"📋 找到的链接: {href[:100]}..." if href and len(href) > 100 else f"📋 找到的链接: {href}")
            
            # 点击元素
            element.click()
            print("✅ 成功点击'查看更多'按钮")
            
            # 等待页面响应
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"❌ 点击'查看更多'按钮失败: {e}")
            
            # 打印页面源码用于调试（查找相关部分）
            try:
                page_source = self.driver.page_source
                if "查看更多" in page_source:
                    # 找到包含"查看更多"的部分
                    start_idx = page_source.find("查看更多") - 200
                    end_idx = page_source.find("查看更多") + 200
                    relevant_source = page_source[max(0, start_idx):end_idx]
                    print(f"📄 相关页面源码片段: {relevant_source}")
                else:
                    print("📄 页面中未找到'查看更多'文本")
            except:
                pass
                
            return False
    
    def extract_major_info(self):
        """提取专业信息"""
        try:
            print("🔍 正在提取专业信息...")
            
            # 等待页面加载完成
            time.sleep(2)
            
            # 查找包含专业信息的div元素
            selectors = [
                # 匹配新发现的格式：包含 l-paragraph paragraph_GpDVFO 类的链接
                "//a[contains(@class, 'l-paragraph paragraph_GpDVFO') and contains(@href, 'keyword=')]",
                # 匹配包含 line-clamp-3 color-dark 的链接
                "//a[contains(@class, 'line-clamp-3 color-dark') and contains(@href, 'keyword=')]",
                # 根据提供的具体结构查找
                "//div[contains(@class, 'l-view block l-flex ml-0 flex flex-col')]//a[contains(@class, 'l-text line-clamp-3')]",
                # 更宽泛的查找专业相关链接
                "//a[contains(@href, 'keyword=') and contains(@class, 'l-text')]",
                # 匹配所有包含专业关键词的链接
                "//a[contains(@href, 'keyword=') and (contains(@class, 'l-text') or contains(@class, 'l-paragraph'))]",
            ]
            
            majors = []
            
            # 尝试所有选择器，收集所有可能的专业信息
            for i, selector in enumerate(selectors):
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        print(f"✅ 选择器 {i+1} 找到 {len(elements)} 个专业元素")
                        for element in elements:
                            major_text = element.text.strip()
                            if major_text and len(major_text) > 1:  # 过滤空文本和单字符
                                majors.append(major_text)
                except Exception as e:
                    print(f"⚠️ 选择器 {i+1} 执行失败: {str(e)}")
                    continue
            
            if not majors:
                print("⚠️ 未找到专业信息，尝试备用方法...")
                # 备用方法：查找所有可能的专业链接
                try:
                    all_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'keyword=')]")
                    for link in all_links:
                        text = link.text.strip()
                        if text and any(keyword in text for keyword in ['技术', '专业', '工程', '管理', '设计']):
                            majors.append(text)
                except Exception:
                    pass
            
            # 去重并格式化输出
            unique_majors = list(dict.fromkeys(majors))  # 保持顺序的去重
            
            if unique_majors:
                print(f"🔍 总共找到 {len(unique_majors)} 个不重复的专业")
                
                
                # 从URL或页面标题中提取学校名称
                school_name = "宜宾职业技术学院"  # 根据搜索关键词确定
                
                # 优先显示计算机相关专业，然后是其他专业
                priority_majors = []
                other_majors = []
                
                for major in unique_majors:
                    if '计算机' in major or '网络' in major or '软件' in major or '信息' in major:
                        priority_majors.append(major)
                    else:
                        other_majors.append(major)
                
                # 合并列表，优先专业在前
                final_majors = priority_majors + other_majors
                major_list = ",".join(final_majors)  # 显示所有找到的专业
                
                result = f"学校：{school_name}, 专业：{major_list}"
                print("=" * 60)
                
                return result
            else:
                print("❌ 未找到任何专业信息")
                return None
                
        except Exception as e:
            print(f"❌ 提取专业信息失败: {str(e)}")
            return None
    
    def visit_toutiao_and_click_baike(self):
        """重新访问头条搜索页面并点击百科链接"""
        try:
            print("🔄 重新访问头条搜索页面...")
            
            # 访问头条搜索页面
            toutiao_url = "https://tsearch.toutiaoapi.com/search?keyword=%E5%AE%9C%E5%AE%BE%E8%81%8C%E4%B8%9A%E6%8A%80%E6%9C%AF%E5%AD%A6%E9%99%A2"
            if not self.visit_page(toutiao_url):
                return False
            
            print("🔍 正在查找百科链接...")
            
            # 等待页面加载
            time.sleep(2)
            
            # 查找包含"百科"标签的链接 - 使用更精确的选择器
            selectors = [
                # 根据提供的具体结构精确匹配
                "//a[@role='generic' and contains(@class, 'l-view block l-text line-clamp-2 t2 color-dark l-paragraph mb-8') and contains(@href, '/search/jump') and @data-log-click]//span[contains(@class, 'l-tag-new') and contains(text(), '百科')]/ancestor::a",
                # 匹配包含百科标签且href包含/search/jump的a标签
                "//a[contains(@href, '/search/jump') and .//span[contains(text(), '百科')] and contains(@class, 'l-view block l-text')]",
                # 根据data-log-click属性中的baike匹配
                "//a[contains(@data-log-click, 'baike') and contains(@href, '/search/jump')]",
                # 匹配包含百科标签和特定class的a标签
                "//a[contains(@class, 'l-view block l-text line-clamp-2 t2 color-dark l-paragraph mb-8') and .//span[contains(text(), '百科')]]",
                # 更简化但精确的查找方式
                "//span[contains(text(), '百科')]/ancestor::a[contains(@href, '/search/jump')]",
                # 备用：查找包含百科标签的a标签
                "//a[.//span[contains(text(), '百科')]]"
            ]
            
            element = None
            
            # 尝试不同的选择器
            for i, selector in enumerate(selectors):
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        print(f"🔍 选择器 {i+1} 找到 {len(elements)} 个候选元素")
                        # 查找包含宜宾职业技术学院信息的百科链接
                        for elem in elements:
                            try:
                                elem_text = elem.text
                                elem_href = elem.get_attribute('href')
                                print(f"📋 检查元素: {elem_text[:100]}...")
                                print(f"📋 链接: {elem_href[:100]}..." if elem_href else "📋 链接: 无")
                                
                                # 检查是否包含宜宾职业技术学院信息和百科标签
                                if ("宜宾职业技术学院" in elem_text and "百科" in elem_text) or \
                                   (elem_href and "/search/jump" in elem_href and "百科" in elem_text):
                                    element = elem
                                    print(f"✅ 使用选择器 {i+1} 找到匹配的百科链接")
                                    break
                            except Exception as e:
                                print(f"⚠️ 检查元素时出错: {e}")
                                continue
                        if element:
                            break
                except Exception as e:
                    print(f"⚠️ 选择器 {i+1} 执行失败: {e}")
                    continue
            
            if element is None:
                print("🔄 尝试备用查找方法...")
                # 备用方法：查找所有包含"百科"的链接
                try:
                    all_links = self.driver.find_elements(By.XPATH, "//a[contains(., '百科')]")
                    for link in all_links:
                        if "宜宾职业技术学院" in link.text:
                            element = link
                            print("✅ 使用备用方法找到百科链接")
                            break
                except Exception:
                    pass
            
            if element is None:
                print("❌ 未找到百科链接")
                # 打印页面源码用于调试
                try:
                    page_source = self.driver.page_source
                    if "百科" in page_source:
                        start_idx = page_source.find("百科") - 300
                        end_idx = page_source.find("百科") + 300
                        relevant_source = page_source[max(0, start_idx):end_idx]
                        print(f"📄 相关页面源码片段: {relevant_source}")
                    else:
                        print("📄 页面中未找到'百科'文本")
                except:
                    pass
                return False
            
            # 滚动到元素位置
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            
            # 获取元素的href属性用于验证
            href = element.get_attribute('href')
            print(f"📋 找到的百科链接: {href[:100]}..." if href and len(href) > 100 else f"📋 找到的百科链接: {href}")
            
            # 点击百科链接
            element.click()
            print("✅ 成功点击百科链接")
            
            # 等待页面跳转
            time.sleep(3)
            
            # 验证是否成功跳转到百科页面
            current_url = self.driver.current_url
            print(f"📍 当前页面URL: {current_url}")
            
            if "baike" in current_url or "百科" in self.driver.title:
                print("✅ 成功跳转到百科页面")
                
                # 提取学生人数信息
                student_count = self.extract_student_count()
                return student_count
            else:
                print("⚠️ 可能未成功跳转到百科页面")
                return None  # 返回None表示未成功获取学生人数
            
        except Exception as e:
            print(f"❌ 访问头条搜索页面或点击百科链接失败: {e}")
            return False
    
    def extract_student_count(self):
        """从百科页面提取学生人数信息"""
        try:
            print("🔍 正在提取学生人数信息...")
            
            # 等待页面完全加载
            time.sleep(3)
            
            # 根据提供的HTML结构查找学生人数
            selectors = [
                # 精确匹配提供的结构
                "//div[@class='container-ID5WgR notNodeView infoboxItem-zje7Gr preview-IM494y']//div[@data-infobox-label='学生人数']//div[@class='content-joo5TV preview-u2fsKV rt-editor-wrapper']//p",
                # 匹配包含学生人数标签的div
                "//div[@data-infobox-label='学生人数']//div[contains(@class, 'content-')]//p",
                # 更通用的查找方式
                "//div[contains(@data-infobox-label, '学生人数')]//p",
                # 查找包含学生人数文本的元素
                "//div[contains(text(), '学生人数')]/following-sibling::div//p",
                # 备用：查找包含"人"和数字的文本
                "//p[contains(text(), '人') and (contains(text(), '000') or contains(text(), '万'))]"
            ]
            
            student_count = None
            
            for i, selector in enumerate(selectors):
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        print(f"🔍 选择器 {i+1} 找到 {len(elements)} 个候选元素")
                        for elem in elements:
                            try:
                                text = elem.text.strip()
                                print(f"📋 检查文本: {text}")
                                
                                # 检查是否包含学生人数信息
                                if text and ("人" in text and any(char.isdigit() for char in text)):
                                    # 提取数字和相关信息
                                    if "余人" in text or "万人" in text or "000" in text:
                                        student_count = text
                                        print(f"✅ 使用选择器 {i+1} 找到学生人数: {student_count}")
                                        break
                            except Exception as e:
                                print(f"⚠️ 检查元素文本时出错: {e}")
                                continue
                        if student_count:
                            break
                except Exception as e:
                    print(f"⚠️ 选择器 {i+1} 执行失败: {e}")
                    continue
            
            if student_count is None:
                print("🔄 尝试备用查找方法...")
                try:
                    # 查找页面中所有包含"学生人数"的文本
                    page_source = self.driver.page_source
                    if "学生人数" in page_source:
                        # 使用正则表达式提取学生人数
                        import re
                        pattern = r'学生人数[^>]*>([^<]*\d+[^<]*人[^<]*)'
                        matches = re.findall(pattern, page_source)
                        if matches:
                            student_count = matches[0].strip()
                            print(f"✅ 使用正则表达式找到学生人数: {student_count}")
                        else:
                            # 更宽泛的搜索
                            pattern = r'(\d+[万千百十]?余?人)'
                            matches = re.findall(pattern, page_source)
                            if matches:
                                # 查找最可能的学生人数（通常是较大的数字）
                                for match in matches:
                                    if any(keyword in match for keyword in ['万', '000', '余']):
                                        student_count = match
                                        print(f"✅ 使用备用正则表达式找到学生人数: {student_count}")
                                        break
                except Exception as e:
                    print(f"⚠️ 备用查找方法失败: {e}")
            
            if student_count:
                # 提取数字部分
                import re
                numbers = re.findall(r'\d+', student_count)
                if numbers:
                    # 取第一个数字（通常是主要的学生人数）
                    numeric_count = numbers[0]
                    print(f"📊 成功提取学生人数: {student_count}")
                    print(f"📊 数字格式学生人数: {numeric_count}")
                    return numeric_count
                else:
                    print(f"📊 找到学生人数文本但无法提取数字: {student_count}")
                    return None
            else:
                print("❌ 未找到学生人数信息")
                return None
                
        except Exception as e:
            print(f"❌ 提取学生人数失败: {str(e)}")
            return None
    
    def close_browser(self):
        """关闭浏览器"""
        try:
            if self.driver:
                self.driver.quit()
                print("✅ 浏览器已关闭")
        except Exception as e:
            print(f"❌ 关闭浏览器失败: {e}")
    
    def run(self):
        """主运行方法"""
        target_url = "https://tsearch.toutiaoapi.com/search?keyword=%E5%AE%9C%E5%AE%BE%E8%81%8C%E4%B8%9A%E6%8A%80%E6%9C%AF%E5%AD%A6%E9%99%A2"
        
        print("🚀 开始执行浏览器自动化任务...")
        print("=" * 50)
        
        major_info = None
        student_count = None
        
        try:
            # 1. 设置浏览器驱动
            if not self.setup_driver():
                return False
            
            # 2. 访问目标页面
            if not self.visit_page(target_url):
                return False
            
            # 3. 点击专业设置
            if not self.click_major_settings():
                return False
            
            # 4. 点击查看更多按钮
            if not self.click_view_more():
                return False
            
            # 5. 提取专业信息
            major_info = self.extract_major_info()
            if major_info:
                print("📋 专业信息提取成功！")
                print(major_info)
            else:
                print("⚠️ 未能提取到专业信息")
            
            # 6. 重新访问头条搜索页面并点击百科链接
            if major_info:  # 只有在成功提取专业信息后才继续
                student_count = self.visit_toutiao_and_click_baike()
                if student_count is None:
                    print("⚠️ 访问头条搜索页面或点击百科链接失败")
            
            # 8. 整合并展示完整信息
            print("=" * 50)
            print("📊 完整学校信息汇总:")
            print("=" * 50)
            
            if major_info and student_count:
                # 提取学校名称和专业列表
                if "学校：" in major_info and "专业：" in major_info:
                    school_name = major_info.split("学校：")[1].split(",")[0].strip()
                    majors = major_info.split("专业：")[1].strip()
                    
                    complete_info = f"学校：{school_name}, 学生人数：{student_count}, 专业：{majors}"
                    print(complete_info)
                else:
                    print(f"{major_info}")
                    print(f"学生人数：{student_count}")
            elif major_info:
                print(f"{major_info}")
                if student_count:
                    print(f"学生人数：{student_count}")
                else:
                    print("⚠️ 未能获取到学生人数信息")
            elif student_count:
                print(f"学校：宜宾职业技术学院, 学生人数：{student_count}")
            else:
                print("⚠️ 未能获取到完整的学校信息")
            
            print("=" * 50)
            print("🎉 所有任务执行成功！")
            print("✅ 已成功点击'专业设置'")
            print("✅ 已成功点击'查看更多'")
            if major_info:
                print("✅ 已成功提取专业信息")
                print("✅ 已成功访问头条搜索页面并点击百科链接")
                if student_count:
                    print("✅ 已成功提取学生人数信息")
                else:
                    print("⚠️ 未能提取到学生人数信息")
            # 保持浏览器打开3秒以便观察结果
            print("⏰ 浏览器将在3秒后关闭...")
            time.sleep(30)
            
            return True
            
        except Exception as e:
            print(f"❌ 执行过程中发生错误: {e}")
            return False
            
        finally:
            # 确保浏览器被关闭
            self.close_browser()


def main():
    """主函数"""
    # 初始化日志配置
    log_file = setup_logging()
    log_print(f"📝 日志文件已创建: {log_file}")
    log_print("🚀 开始执行浏览器自动化脚本")
    
    automation = BrowserAutomation()
    success = automation.run()
    
    if success:
        log_print("\n✅ 脚本执行完成")
        sys.exit(0)
    else:
        log_print("\n❌ 脚本执行失败")
        sys.exit(1)


if __name__ == "__main__":
    main()