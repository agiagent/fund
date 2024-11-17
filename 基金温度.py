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


session = requests.Session()  # 创建一个会话对象，用于维持会话状态

temperatures_api = 'http://caf-qibei.com/index?type=html'  # 定义指数温度API的URL
temps = get_index_temps(temperatures_api, session)  # 获取指数温度
print(temps)
