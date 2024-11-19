import requests
import pandas as pd
from bs4 import BeautifulSoup


# 爬虫接口
def api(urls):
    # 发送请求获取网页内容
    response = requests.get(urls)

    # 如果请求成功，返回状态码 200
    if response.status_code == 200:
        html_content = response.text  # 获取网页内容

        # 解析HTML内容
        soup = BeautifulSoup(html_content, 'html.parser')

        # 查找所有的<tr>标签
        tr_tags = soup.find_all('tr')

        # 解析基金温度数据
        temps = [
            (
                tr.find_all('a', href=True)[0].text.strip(),  # 提取指数名称
                float(tr.find('td', {'colspan': '3'}).text.strip())  # 提取基金温度
            )
            for tr in tr_tags
            if len(tr.find_all('a', href=True)) >= 2  # 确保至少有2个<a>标签
               and tr.find('td', {'colspan': '3'})  # 确保有有效的<td>标签
               and tr.find('td', {'colspan': '3'}).text.strip().replace('.', '', 1).isdigit()  # 确保基金温度有效
        ]
        temp = pd.DataFrame(temps)
        print(temp)
    else:
        print(f"请求失败，状态码：{response.status_code}")


# 目标网站 URL
url = 'http://caf-qibei.com/index?type=html'
api(urls=url)
