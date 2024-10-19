import requests
from lxml import etree

# 请求网页
url = "http://fund.eastmoney.com/company/default.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

# 解析HTML
html = etree.HTML(response.text)

# 使用XPath提取基金公司和管理规模
companies = html.xpath('//*[@id="gspmTbl"]/tbody/tr/td[2]/a/text()')
sizes = html.xpath('//*[@id="gspmTbl"]/tbody/tr/td[6]/p/text()')

# 新的列表用于存储规模大于1000的公司名称
large_fund_companies = []

# 遍历公司和管理规模，筛选管理规模大于1000的公司
for company, size in zip(companies, sizes):
    # 清理并转换规模数据（假设以“亿”为单位）
    size_clean = size.replace('亿', '').replace(',', '').strip()
    try:
        size_value = float(size_clean)
        if size_value > 1000:
            large_fund_companies.append(company.strip())
    except ValueError:
        # 忽略无法转换的值
        continue

# 输出结果
print("管理规模大于1000亿的基金公司:")
print(large_fund_companies)
