# 定义爬虫接口函数
import requests
from bs4 import BeautifulSoup
import pandas as pd


def api(url):
    # 发送请求获取网页内容
    response = requests.get(url)

    # 如果请求成功，返回状态码 200
    if response.status_code == 200:
        html_content = response.text  # 获取网页内容

        # 解析HTML内容
        soup = BeautifulSoup(html_content, 'html.parser')
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return None

    return soup


def extract_bond_yield(soup):
    """
    从HTML中提取十年期国债收益率，标识符为 id="idEpvDate"。
    """
    bond_yield_element = soup.find('td', {'id': 'idEpvDate'})
    if bond_yield_element:
        bond_yield = bond_yield_element.text.strip()
        return bond_yield
    return None


def clean_data(url):
    soup = api(url)
    if soup is None:
        return None

    # 提取十年期国债收益率
    bond_yield = extract_bond_yield(soup)

    # 查找所有的 <table> 标签
    tables = soup.find_all('table', {'id': 'stock'})
    cleaned_data = []

    # 处理每个表格
    for table in tables:
        rows = table.find_all('tr')[2:]  # 跳过表头

        for row in rows:
            # 提取每行的列数据
            columns = row.find_all('td')
            if not columns:
                continue  # 跳过没有数据的行

            data = {}

            # 提取PE_TTM
            pe_ttm = columns[0].text.strip() if len(columns) > 0 else None
            data['PE_TTM'] = pe_ttm

            # 提取EPV（期望收益）
            epv = columns[2].text.strip() if len(columns) > 2 else None
            data['EPV'] = epv

            # 提取股市吸引力
            if '股市吸引力' in columns[0].text:
                stock_attraction = columns[1].text.strip() if len(columns) > 1 else None
                data['股市吸引力'] = stock_attraction

            # 提取巴菲特指数
            if '巴菲特指数' in columns[0].text:
                buffett_index = columns[1].text.strip() if len(columns) > 1 else None
                data['巴菲特指数'] = buffett_index

            # 提取七日换手率
            if '七日换手率' in columns[0].text:
                turnover_rate = columns[1].text.strip() if len(columns) > 1 else None
                data['七日换手率'] = turnover_rate

            cleaned_data.append(data)

    return cleaned_data, bond_yield


# 示例URL，替换为实际的网页URL
url = "http://caf-qibei.com/index?type=html"  # 替换为实际的网页URL
data, bond_yield = clean_data(url)


# 处理其他数据的提取
if data:
    PE_TTM = data[2]['PE_TTM']
    GZ = bond_yield
    EPV = data[2]['EPV']
    XYL = data[5]['股市吸引力']
    BFT = data[6]['巴菲特指数']
    HSL = data[7]['七日换手率']
    print(PE_TTM)
    print(GZ)
    print(EPV)
    print(XYL)
    print(BFT)
    print(HSL)
