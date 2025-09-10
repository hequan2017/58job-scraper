import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_real_url(url):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    real_url = driver.current_url
    driver.quit()
    return real_url

def get_company_contact_selenium(url):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.implicitly_wait(5)

    contact_name = email = phone = ""
    try:
        items = driver.find_elements("css selector", ".contact .c_detail_item")
        for item in items:
            key = item.find_element("tag name", "span").text.strip()
            value = item.find_element("tag name", "em").text.strip()
            if "联系人" in key:
                contact_name = value
            elif "邮箱" in key:
                email = value
            elif "电话" in key:
                phone = value
    except Exception as e:
        print("抓取联系方式失败:", e)
    driver.quit()
    return {"联系人": contact_name, "招聘邮箱": email, "联系电话": phone}

def get_job_detail(url):
    try:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        driver.implicitly_wait(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        # 基本信息
        title = soup.find("span", class_="pos_title").get_text(strip=True) if soup.find("span", class_="pos_title") else ""
        salary = soup.find("span", class_="pos_salary").get_text(strip=True) if soup.find("span", class_="pos_salary") else ""
        job_name = soup.find("span", class_="pos_name").get_text(strip=True) if soup.find("span", class_="pos_name") else ""

        # 招聘条件
        conditions_block = soup.find("div", class_="pos_base_condition")
        conditions_list = []
        if conditions_block:
            for c in conditions_block.find_all("span"):
                text = c.get_text(strip=True).replace("\n", "")
                if text:
                    conditions_list.append(text)
        recruit_conditions = " | ".join(conditions_list)

        location = soup.find("div", class_="pos-area").get_text(strip=True) if soup.find("div", class_="pos-area") else ""
        update_time = soup.find("span", class_="pos_base_update").get_text(strip=True) if soup.find("span", class_="pos_base_update") else ""
        views = soup.find("span", class_="pos_base_browser").get_text(strip=True) if soup.find("span", class_="pos_base_browser") else ""

        # 公司信息
        company_block = soup.find("div", class_="subitem_con company_baseInfo")
        company_name = company_block.find("a").get_text(strip=True) if company_block and company_block.find("a") else ""
        company_link = company_block.find("a")["href"] if company_block and company_block.find("a") else ""
        company_industry = company_block.find("p", class_="comp_baseInfo_belong").get_text(strip=True) if company_block else ""
        company_scale = company_block.find("p", class_="comp_baseInfo_scale").get_text(strip=True) if company_block else ""

        # 公司福利
        welfare_block = soup.find("div", class_="pos_welfare")
        welfare_list = [span.get_text(strip=True) for span in welfare_block.find_all("span", class_="pos_welfare_item")] if welfare_block else []
        company_welfare = " | ".join(welfare_list)

        # 职位描述
        job_desc = ""
        desc_block = soup.find("div", class_="subitem_con pos_description")
        if desc_block:
            posDes_block = desc_block.find("div", class_="posDes")
            if posDes_block:
                des_block = posDes_block.find("div", class_="des")
                if des_block:
                    job_desc = " ".join([line.strip() for line in des_block.strings if line.strip()])

        # 公司介绍
        company_intro = ""
        company_intro_block = soup.find("div", class_="intro")
        if company_intro_block:
            company_intro = " ".join([p.get_text(strip=True) for p in company_intro_block.find_all(["p", "div"])])

        # 联系方式
        contact_info = get_company_contact_selenium(company_link) if company_link else {"联系人": "", "招聘邮箱": "", "联系电话": ""}

        return {
            "职位名": job_name,
            "岗位类型": title,
            "薪资": salary,
            "招聘条件": recruit_conditions,
            "工作地点": location,
            "更新时间": update_time,
            "浏览量": views,
            "公司名": company_name,
            "公司链接": company_link,
            "公司行业": company_industry,
            "公司规模": company_scale,
            "公司福利": company_welfare,
            "职位描述": job_desc,
            "公司介绍": company_intro,
            "联系人": contact_info["联系人"],
            "招聘邮箱": contact_info["招聘邮箱"],
            "联系电话": contact_info["联系电话"]
        }
    except Exception as e:
        print("抓取职位详情失败:", e)
        return None

def get_job_list(list_url):
    """抓取列表页所有职位"""
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(list_url)
    driver.implicitly_wait(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    jobs = []
    for job_li in soup.find_all("li", class_="job_item"):
        title_tag = job_li.find("span", class_="name")
        title = title_tag.get_text(strip=True) if title_tag else ""
        a_tag = title_tag.find_parent("a") if title_tag else None
        job_url = a_tag["href"] if a_tag and a_tag.has_attr("href") else ""
        if title and job_url:
            jobs.append((title, job_url))
    return jobs

if __name__ == "__main__":
    list_url = "https://xa.58.com/hulianwangtx/?PGTID=0d402f88-0209-9eab-d90c-05ba2b785523&ClickID=5"
    jobs = get_job_list(list_url)
    print(f"列表页共抓取到 {len(jobs)} 个职位")

    # 创建空 DataFrame
    df = pd.DataFrame()

    for i, (title, job_url) in enumerate(jobs, 1):
        print(f"\n抓取第 {i} 个职位: {title}")
        print(f"原始跳转链接: {job_url}")

        if job_url:
            real_url = get_real_url(job_url)
            print(f"真实职位链接: {real_url}")

            detail = get_job_detail(real_url)
            if detail:
                # 写入 DataFrame
                df = pd.concat([df, pd.DataFrame([detail])], ignore_index=True)
                # 每抓一个职位立即写入 Excel
                df.to_excel("58职位信息.xlsx", index=False)
                print("写入成功")
            else:
                print("抓取职位详情失败")

        print("暂停 30 秒...")
        time.sleep(30)
