import requests  # 导入requests库，用于发送网络请求
from bs4 import BeautifulSoup  # 导入BeautifulSoup库，用于解析HTML
import pandas as pd  # 导入pandas库，用于数据处理和显示
from typing import Union  # 导入Union，用于类型提示


# 定义一个安全发送网络请求的函数，接受URL、会话对象和一个标记是否返回JSON格式的数据
def safe_request(url: str, session: requests.Session, is_json: bool = True) -> Union[dict, str, None]:
    """
    发送网络请求并处理错误，返回JSON数据或文本数据。

    :param url: 请求的URL地址
    :param session: 会话对象，用于发送请求
    :param is_json: 是否返回JSON格式的数据，默认返回JSON
    :return: JSON数据或文本数据，若请求失败则返回None
    """
    try:
        response = session.get(url)  # 使用会话对象发送GET请求
        response.raise_for_status()  # 检查请求是否成功（200-299范围内）
        if is_json:
            return response.json()  # 如果is_json为True，返回JSON格式数据
        else:
            return response.text  # 否则返回HTML文本数据
    except requests.RequestException as e:  # 捕获网络请求相关的异常
        print(f"请求错误：{url}, 错误信息：{e}")  # 打印错误信息
        return None  # 请求失败时返回None


# 定义一个获取指数温度的函数
def get_index_temps(api: str, session: requests.Session) -> list[tuple[str, float]]:
    """
    获取指数温度数据并解析HTML内容。

    :param api: 请求指数温度API的URL地址
    :param session: 会话对象，用于发送请求
    :return: 返回一个包含指数名称和温度的元组列表
    """
    html_content = safe_request(api, session, is_json=False)  # 请求HTML内容
    if html_content is None:  # 如果请求失败
        return []

    soup = BeautifulSoup(html_content, 'html.parser')  # 解析HTML内容
    tr_tags = soup.find_all('tr')  # 查找所有的<tr>标签

    # 解析温度数据，筛选出有效的数据行
    index_temps = [
        (
            tr.find_all('a', href=True)[0].text.strip(),  # 提取指数名称
            float(tr.find('td', {'colspan': '3'}).text.strip())  # 提取指数温度
        )
        for tr in tr_tags
        if len(tr.find_all('a', href=True)) >= 2  # 确保至少有2个<a>标签
           and tr.find('td', {'colspan': '3'})  # 确保有有效的<td>标签
           and tr.find('td', {'colspan': '3'}).text.strip().replace('.', '', 1).isdigit()  # 确保温度值有效
    ]

    return index_temps  # 返回解析出的指数温度数据


# 创建一个会话对象，用于维持会话状态
session = requests.Session()

# 定义指数温度API的URL
temperatures_api = 'http://caf-qibei.com/index?type=html'  # TODO: 这里需要替换为实际的API地址

# 获取指数温度数据
temps = get_index_temps(temperatures_api, session)

# 使用pandas展示温度数据
if temps:
    # 将数据转换为DataFrame，便于显示和处理
    df = pd.DataFrame(temps, columns=['指数名称', '温度（°C）'])
    print(df)  # 打印温度数据
else:
    print("未获取到有效的温度数据")
