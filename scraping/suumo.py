import re
from pprint import pprint

import requests
from bs4 import BeautifulSoup


def get_info(url):
    """スーモの物件ページから情報を取得する

    Args:
        url (str): 物件ページのURL

    Returns:
        dict: 物件情報 (部屋の特長・設備, 物件概要)

    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # 部屋の特徴・設備
    features = soup.select_one('#contents > .section > div > ul > li').text.split('、')

    # 物件概要
    th_list = soup.select('#contents > .section > table th')
    td_list = soup.select('#contents > .section > table td')
    overview = {
        item1.text: re.sub(r'\s', '', item2.text)
        for item1, item2 in zip(th_list, td_list)
    }

    return {
        '部屋の特徴・設備': features,
        '物件概要': overview,
    }


if __name__ == '__main__':
    pprint(get_info('https://suumo.jp/chintai/jnc_000067842508/?bc=100288615133'))
