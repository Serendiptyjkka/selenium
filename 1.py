from selenium import webdriver
from lxml import etree
import re
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv


class LagouSpider(object):
    driver_path = r"D:\BaiduNetdiskDownload\chromedriver.exe"

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=LagouSpider.driver_path)
        self.url = 'https://www.lagou.com/jobs/list_python/p-city_0?&cl=true&fromSearch=true&labelWords=&suginput='
        self.positions = []

    def run(self):
        self.driver.get(self.url)
        while True:
            source = self.driver.page_source  # 通过driver。page_source这个技术可以直接获得源代码不是通过检查获得的那种简陋的源代码，而是通过AJKS技术获得的源代码
            WebDriverWait(driver=self.driver, timeout=10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='pager_container']/span[last()]"))
            )
            self.parse_list_page(source)
            next_btn = self.driver.find_element_by_xpath(
                "//div[@class='pager_container']/span[last()]")  # 找到下一页标签
            if "pager_next_disabled" in next_btn.get_attribute("class"):  # 获取该标签下的属性
                break
            else:
                next_btn.click()  # 点击下一页
            # time.sleep()

    def parse_list_page(self, source):
        html = etree.HTML(source)
        links = html.xpath("//a[@class='position_link']/@href")
        for link in links:
            self.request_detail_page(link)
            time.sleep(2)

    def request_detail_page(self, url):
        self.driver.execute_script("window.open('%s')" % url)
        self.driver.switch_to.window(self.driver.window_handles[1])
        WebDriverWait(self.driver, timeout=10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[@class='name']"))
        )
        source = self.driver.page_source
        self.parse_detail_page(source)
        # 关闭当前的详情页
        self.driver.close()
        # 继续切换回职位列表页
        self.driver.switch_to.window(self.driver.window_handles[0])

    def parse_detail_page(self, source):
        html = etree.HTML(source)
        position_name = html.xpath("//h1[@class='name']/text()")[0]
        job_requests_spans = html.xpath("//dd[@class='job_request']//span")
        salary = job_requests_spans[0].xpath('.//text()')[0].strip()
        city = job_requests_spans[1].xpath('.//text()')[0].strip()
        city = re.sub(r"[\s/]", "", city)
        work_years = job_requests_spans[2].xpath('.//text()')[0].strip()
        work_years = re.sub(r"[\s/]]", "", work_years)
        education = job_requests_spans[3].xpath('.//text()')[0].strip()
        education = re.sub(r"[\s/]", "", education)
        desc = "".join(html.xpath("//dd[@class='job_bt']//text()")).strip()
        position = {
            '职位': position_name,
            '月薪': salary,
            '工作地点': city,
            '工作经验': work_years,
            '学历': education,
            '职位描述': desc
        }
        self.positions.append(position)
        headers = {'职位', '月薪', '工作地点', '工作经验', '学历', '职位描述'}
        with open('position.csv', 'w', encoding='utf-8', newline='') as fp:
            writer = csv.DictWriter(fp, headers)
            writer.writeheader()
            writer.writerows(self.positions)
        print(position)


if __name__ == '__main__':
    spider = LagouSpider()
    spider.run()