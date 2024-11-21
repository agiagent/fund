import requests


# 一、爬虫接口
def api(url, headers=None):
    """
    通用的 API 请求接口
    """
    if headers is None:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            )
        }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 如果响应状态码不是200，抛出异常
        return response.json()  # 直接解析为JSON
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except ValueError as e:
        print(f"JSON解析错误: {e}")
        return None


# 二、动态爬取数据
def fetch_fund_data(urls):
    """
    根据提供的URL列表，抓取基金数据并统一格式化
    """
    all_data = []
    for url in urls:
        result = api(url)
        if result and 'rows' in result:
            for item in result['rows']:
                cell = item.get('cell', {})
                all_data.append({
                    '基金代码': cell.get('fund_id', 'N/A'),
                    '现价': cell.get('price', 'N/A'),
                    '涨跌': cell.get('increase_rt', 'N/A'),
                    '溢价率': cell.get('discount_rt', 'N/A'),
                    '成交额': cell.get('volume', 'N/A')
                })
    return all_data


# 三、集思录数据URLs
fund_urls = [
    'https://www.jisilu.cn/data/etf/etf_list/?___jsl=LST___t=1693819271762&volume=500&unit_total=2&rp=25',
    'https://www.jisilu.cn/data/qdii/qdii_list/A?___jsl=LST___t=1665370506235&rp=22&page=1',
    'https://www.jisilu.cn/data/qdii/qdii_list/E?___jsl=LST___t=1665371145110&rp=22&page=1'
]

# 获取数据
data = fetch_fund_data(fund_urls)

# 打印结果
for item in data:
    print(item)
print(f"总共抓取到 {len(data)} 条数据")
