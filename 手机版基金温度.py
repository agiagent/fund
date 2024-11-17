import requests  # 导入requests库用于发送网络请求
from bs4 import BeautifulSoup  # 导入BeautifulSoup库用于解析HTML


# 定义一个安全发送网络请求的函数，接受URL、会话对象和一个标记是否返回JSON格式的数据
def safe_request(url, session, is_json=True):
    try:
        response = session.get(url)  # 使用session发送GET请求到指定的URL
        response.raise_for_status()  # 检查请求是否成功，如果不成功会抛出异常
        return response.json() if is_json else response.text  # 根据is_json返回JSON或文本内容
    except requests.RequestException as e:  # 捕获请求过程中的异常
        print(f"Error requesting '{url}': {e}")  # 打印错误信息
        return None  # 出现异常返回None


# 定义一个从原始数据中提取基金数据的函数
def extract_fund_data(raw_data, keys, code_mappings):
    code_set = {mapping['cn'] for mapping in code_mappings}  # 从映射中提取所有基金代码构成一个集合
    return [
        {key: float(item['cell'][key].rstrip('%')) if key != 'fund_id' else item['cell'][key]
         for key in keys if key in item['cell']}  # 提取每项数据，将百分比转换为浮点数，除非是基金ID
        for item in raw_data if 'cell' in item and item['cell']['fund_id'] in code_set
    ]  # 遍历原始数据中的每一项，只处理包含'cell'且基金ID在代码集合中的项


# 定义一个更新基金代码信息的函数
def update_fund_codes(urls, session, code_mappings, keys):
    for url in urls:  # 遍历所有URL
        raw_data = safe_request(url, session)  # 发送安全请求获取原始数据
        if raw_data:  # 如果请求成功获取到数据
            cleaned_data = extract_fund_data(raw_data.get('rows', []), keys, code_mappings)  # 提取并清洗数据
            for data_item in cleaned_data:  # 遍历每一项清洗后的数据
                for code_mapping in code_mappings:  # 遍历每一项代码映射
                    if code_mapping['cn'] == data_item['fund_id']:  # 如果代码匹配
                        code_mapping.update({k: data_item[k] for k in keys[1:]})  # 更新映射信息
                        code_mapping['return'] = code_mapping.pop('increase_rt')  # 更改键名'increase_rt'为'return'
                        code_mapping['yield'] = code_mapping.pop('discount_rt')  # 更改键名'discount_rt'为'yield'


# 定义一个获取指数温度的函数
def get_index_temps(api, session):
    html_content = safe_request(api, session, is_json=False)  # 请求HTML内容
    if html_content is None:  # 如果请求失败
        return []

    soup = BeautifulSoup(html_content, 'html.parser')  # 使用BeautifulSoup解析HTML内容
    tr_tags = soup.find_all('tr')  # 查找所有的<tr>标签
    index_temps = [(tr.find_all('a', href=True)[0].text.strip(), float(tr.find('td', {'colspan': '3'}).text.strip()))
                   for tr in tr_tags if len(tr.find_all('a', href=True)) >= 2 and tr.find('td', {'colspan': '3'}) and
                   tr.find('td', {'colspan': '3'}).text.strip().replace('.', '', 1).isdigit()]
    return index_temps  # 返回解析出的指数温度数据


# 定义一个整合温度信息到基金代码映射的函数
def integrate_temps_with_funds(temperatures, code_mappings):
    id_to_code = {code['id']: code for code in code_mappings}  # 创建一个ID到代码的映射
    for index_id, temp in temperatures:  # 遍历所有温度信息
        if index_id in id_to_code:
            id_to_code[index_id]['temp'] = temp  # 将温度信息添加到相应的代码映射中
    return sorted([code for code in code_mappings if 'temp' in code], key=lambda x: x['temp'])  # 返回包含温度信息的代码映射，按温度排序


# 定义一个根据条件过滤基金的函数
def filter_funds(funds, condition):
    return [{'名称': fund['name'], '代码': fund['cw'], '温度': fund['temp'], '涨跌': fund['return']} for fund in funds if
            condition(fund)]  # 返回满足条件的基金信息列表


session = requests.Session()  # 创建一个会话对象，用于维持会话状态
urls = [
    'https://www.jisilu.cn/data/etf/etf_list/?___jsl=LST___t=1663138938775&rp=25&page=1',
    'https://www.jisilu.cn/data/qdii/qdii_list/A?___jsl=LST___t=1665370506235&rp=22&page=1',
    'https://www.jisilu.cn/data/qdii/qdii_list/E?___jsl=LST___t=1665371145110&rp=22&page=1'
]  # 定义要访问的URL列表
keys = ['fund_id', 'price', 'increase_rt', 'discount_rt']  # 定义要提取的数据键
code_mappings = [  # 定义基金代码映射
    {'id': '000905', 'name': '中证500', 'cn': '510500', 'cw': '160119'},
    {'id': '399975', 'name': '证券公司', 'cn': '512000', 'cw': '004069'},
    {'id': '399324', 'name': '深证红利', 'cn': '159905', 'cw': '481012'},
    {'id': '000922', 'name': '中证红利', 'cn': '515890', 'cw': '100032'},
    {'id': 'H30533', 'name': '互联网50', 'cn': '513050', 'cw': '006327'},
    {'id': '399006', 'name': '创业板指', 'cn': '159915', 'cw': '161022'},
    {'id': '399971', 'name': '中证传媒', 'cn': '512980', 'cw': '004752'},
    {'id': 'HSI', 'name': '恒生指数', 'cn': '159920', 'cw': '164705'},
    {'id': '000300', 'name': '沪深300', 'cn': '510300', 'cw': '160706'},
    {'id': 'SPX', 'name': '标普500', 'cn': '513500', 'cw': '050025'},
    {'id': 'GDAXI', 'name': '德国DAX', 'cn': '513030', 'cw': '000614'},
    {'id': '000932', 'name': '中证消费', 'cn': '159928', 'cw': '000248'},
    {'id': '399987', 'name': '中证酒', 'cn': '512690', 'cw': '160632'},
    {'id': '399396', 'name': '国证食品', 'cn': '159843', 'cw': '160222'},
    {'id': '399998', 'name': '中证煤炭', 'cn': '515220', 'cw': '161032'}
]

update_fund_codes(urls, session, code_mappings, keys)  # 更新基金代码信息
temperatures_api = 'http://caf-qibei.com/index?type=html'  # 定义指数温度API的URL
temps = get_index_temps(temperatures_api, session)  # 获取指数温度
funds = integrate_temps_with_funds(temps, code_mappings)  # 将温度信息整合到基金代码映射中

low_temp_funds = filter_funds(funds, lambda x: x['return'] < -1)  # 筛选出回报率小于-2%的基金
high_temp_funds = filter_funds(funds, lambda x: x['return'] > 1)  # 筛选出回报率大于2%的基金

print('【低温数据】：')  # 打印低温基金信息
for i in low_temp_funds:
    print(i)
print('【高温数据】：')  # 打印高温基金信息
for i in high_temp_funds:
    print(i)
