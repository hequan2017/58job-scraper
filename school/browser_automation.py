#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宜宾职业技术学院信息自动化脚本
使用Selenium自动化浏览器访问指定页面并点击专业设置
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


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
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
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
            service = Service(chromedriver_path)
            
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
                
                # 检查是否包含计算机网络技术
                computer_majors = [major for major in unique_majors if '计算机' in major or '网络' in major]
                if computer_majors:
                    print(f"✅ 找到计算机相关专业: {computer_majors}")
                
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
                print("📋 提取结果:")
                print(result)
                print("=" * 60)
                
                return result
            else:
                print("❌ 未找到任何专业信息")
                return None
                
        except Exception as e:
            print(f"❌ 提取专业信息失败: {str(e)}")
            return None
    
        """点击学校详情页面链接 - 使用百科标签匹配"""
        try:
            print("🔍 正在查找百科标签...")
            
            # 等待页面加载
            time.sleep(3)
            
            # 查找包含"百科"文字的span标签
            baike_element = None
            try:
                # 使用XPath查找包含"百科"文字的span元素
                baike_xpath = "//span[contains(@class, 'l-tag-new') and contains(text(), '百科')]"
                baike_elements = self.driver.find_elements(By.XPATH, baike_xpath)
                
                if baike_elements:
                    baike_element = baike_elements[0]
                    print(f"✅ 找到百科标签: {baike_element.text}")
                    
                    # 查找百科标签的父级链接元素
                    parent_link = None
                    current_element = baike_element
                    
                    # 向上查找最多5层，寻找包含href的a标签
                    for i in range(5):
                        try:
                            current_element = current_element.find_element(By.XPATH, "..")
                            if current_element.tag_name == 'a' and current_element.get_attribute('href'):
                                href = current_element.get_attribute('href')
                                # 确保链接是百科相关的，避免跳转到错误页面
                                if href.startswith('https://www.baike.com'):
                                    parent_link = current_element
                                    break
                                elif any(keyword in href.lower() for keyword in ['baike', 'wiki', 'encyclopedia', '百科']):
                                    parent_link = current_element
                                    break
                                elif 'toutiao' in href and 'baike' in href:
                                    parent_link = current_element
                                    break
                        except:
                            break
                    
                    # 如果没找到父级链接，尝试查找同级或相邻的链接
                    if not parent_link:
                        try:
                            # 查找包含百科标签的链接
                            ancestor_link = baike_element.find_element(By.XPATH, "./ancestor::a[@href]")
                            href = ancestor_link.get_attribute('href')
                            if href.startswith('https://www.baike.com') or any(keyword in href.lower() for keyword in ['baike', 'wiki', 'encyclopedia', '百科']):
                                parent_link = ancestor_link
                        except:
                            pass
                    
                    if parent_link:
                        href = parent_link.get_attribute('href')
                        print(f"✅ 找到百科链接: {href}")
                        
                        # 验证链接是否为百科页面
                        if href.startswith('https://www.baike.com') or any(keyword in href.lower() for keyword in ['baike', 'wiki', 'encyclopedia', '百科']):
                            # 点击百科链接
                            try:
                                # 滚动到元素可见
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", parent_link)
                                time.sleep(1)
                                
                                # 尝试JavaScript点击
                                self.driver.execute_script("arguments[0].click();", parent_link)
                                print("✅ 已点击百科链接")
                            except:
                                # 如果JavaScript点击失败，尝试直接访问链接
                                if href and href != '#':
                                    self.driver.get(href)
                                    print("✅ 已直接访问百科页面")
                            
                            # 等待新页面加载
                            time.sleep(5)
                            return True
                        else:
                            print(f"⚠️ 链接不是百科页面，跳过: {href}")
                    else:
                        print("⚠️ 未找到百科标签对应的链接")
                else:
                    print("⚠️ 未找到百科标签")
                    
            except Exception as e:
                print(f"⚠️ 查找百科标签失败: {e}")
            
            # 如果没找到百科标签，尝试直接查找百科链接
            if not baike_element:
                print("🔍 尝试直接查找百科链接...")
                
                # 只查找真正的百科链接
                baike_selectors = [
                    "a[href^='https://www.baike.com']",  # 快懂百科
                ]
                
                for selector in baike_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            element = elements[0]
                            href = element.get_attribute('href')
                            if href and href != '#' and 'javascript:' not in href:
                                print(f"✅ 找到百科链接: {href}")
                                self.driver.execute_script("arguments[0].click();", element)
                                time.sleep(5)
                                return True
                    except Exception as e:
                        print(f"⚠️ 百科选择器 {selector} 失败: {e}")
                        continue
            
            print("❌ 未找到可用的百科链接")
            return False
            
        except Exception as e:
            print(f"❌ 点击学校详情页面链接失败: {e}")
            return False
    
    def extract_student_count(self):
        """提取学生人数信息"""
        try:
            print("🔍 正在提取学生人数信息...")
            
            # 等待页面加载
            time.sleep(3)
            
            # 查找学生人数相关的元素
            selectors = [
                # 头条百科样式
                'div[data-infobox-label="学生人数"] .content-joo5TV p',
                'div[data-infobox-label="学生人数"] .EDITOR_DOM p',
                '.item-p2Kn3L[data-infobox-label="学生人数"] p',
                '*[data-comment-key="学生人数"] p',
                # 百度百科样式
                '.basic-info .name:contains("学生人数") + .value',
                '.lemma-summary .para:contains("学生")',
                '.basic-info dt:contains("学生人数") + dd',
                # 学校官网样式
                '.info-item:contains("学生人数")',
                '.school-info:contains("学生")',
                '.statistics:contains("学生")',
                # 通用样式
                'td:contains("学生人数") + td',
                'th:contains("学生人数") + td',
                '.info:contains("学生")',
                '.data:contains("学生")'
            ]
            
            student_count = None
            for selector in selectors:
                try:
                    if ':contains(' in selector:
                        # 使用XPath处理contains
                        xpaths = [
                            "//div[contains(text(), '学生人数')]/following-sibling::div//p",
                            "//div[contains(text(), '学生人数')]/following-sibling::*",
                            "//td[contains(text(), '学生人数')]/following-sibling::td",
                            "//th[contains(text(), '学生人数')]/following-sibling::td",
                            "//dt[contains(text(), '学生人数')]/following-sibling::dd",
                            "//*[contains(text(), '学生人数')]/following-sibling::*",
                            "//*[contains(text(), '学生') and contains(text(), '人数')]",
                            "//*[contains(text(), '在校生')]",
                            "//*[contains(text(), '全日制学生')]"
                        ]
                        
                        for xpath in xpaths:
                            elements = self.driver.find_elements(By.XPATH, xpath)
                            if elements:
                                break
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elements:
                        for element in elements:
                            text = element.text.strip()
                            if text and any(char.isdigit() for char in text):
                                print(f"✅ 找到学生人数文本: {text}")
                                
                                # 提取数字部分
                                import re
                                numbers = re.findall(r'\d+', text)
                                if numbers:
                                    # 取最大的数字（通常是学生总数）
                                    student_count = max(numbers, key=int)
                                    print(f"✅ 提取到学生人数: {student_count}")
                                    break
                        if student_count:
                            break
                except Exception as e:
                    print(f"⚠️ 选择器 {selector} 查找失败: {e}")
                    continue
            
            # 如果还是没找到，尝试在整个页面中搜索
            if not student_count:
                print("🔍 在整个页面中搜索学生人数信息...")
                try:
                    page_text = self.driver.page_source
                    import re
                    
                    # 搜索包含学生人数的模式
                    patterns = [
                        r'学生人数[：:]\s*(\d+)',
                        r'在校生[：:]\s*(\d+)',
                        r'全日制学生[：:]\s*(\d+)',
                        r'学生总数[：:]\s*(\d+)',
                        r'(\d+)\s*余?人.*学生',
                        r'学生.*?(\d+)\s*余?人',
                        r'(\d{4,})\s*余?人',  # 4位以上数字+人
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, page_text, re.IGNORECASE)
                        if matches:
                            student_count = matches[0]
                            print(f"✅ 通过模式匹配找到学生人数: {student_count}")
                            break
                            
                except Exception as e:
                    print(f"⚠️ 页面文本搜索失败: {e}")
            
            if not student_count:
                print("❌ 未找到学生人数信息")
                print("💡 尝试截图以便调试...")
                self.take_screenshot("student_count_debug.png")
                return None
            
            return student_count
            
        except Exception as e:
            print(f"❌ 提取学生人数失败: {e}")
            return None

    def take_screenshot(self, filename="screenshot.png"):
        """截取屏幕截图"""
        try:
            # 确保截图保存在school目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            screenshot_path = os.path.join(script_dir, filename)
            
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 截图已保存: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            print(f"❌ 截图失败: {e}")
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
            
            
            # 8. 整合并展示完整信息
            print("=" * 50)
            print("📊 完整学校信息汇总:")
            print("=" * 50)
            
            if major_info and student_count:
                # 提取学校名称和专业列表
                if "学校：" in major_info and "专业：" in major_info:
                    school_name = major_info.split("学校：")[1].split(",")[0].strip()
                    majors = major_info.split("专业：")[1].strip()
                    
                    complete_info = f"学校：{school_name}, 学生人数：{student_count}人, 专业：{majors}"
                    print(complete_info)
                else:
                    print(f"{major_info}")
                    print(f"学生人数：{student_count}人")
            elif major_info:
                print(f"{major_info}")
                if student_count:
                    print(f"学生人数：{student_count}人")
            elif student_count:
                print(f"学校：宜宾职业技术学院, 学生人数：{student_count}人")
            else:
                print("⚠️ 未能获取到完整的学校信息")
            
            print("=" * 50)
            print("🎉 所有任务执行成功！")
            print("✅ 已成功点击'专业设置'")
            print("✅ 已成功点击'查看更多'")
            if major_info:
                print("✅ 已成功提取专业信息")
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
    automation = BrowserAutomation()
    success = automation.run()
    
    if success:
        print("\n✅ 脚本执行完成")
        sys.exit(0)
    else:
        print("\n❌ 脚本执行失败")
        sys.exit(1)


if __name__ == "__main__":
    main()