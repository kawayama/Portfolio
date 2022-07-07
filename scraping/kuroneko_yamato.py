import datetime
import time

from bs4 import BeautifulSoup
import requests

from utils import notification
import pprint


INQUIRE_URL = r'https://toi.kuronekoyamato.co.jp/cgi-bin/tneko'


def inquire_about_package(package_number):
    """配達状況を問い合わせる

    参考: https://qiita.com/the_red/items/39eea9ea20f5a81d66e7

    Args:
        package_number (int): 荷物番号

    Returns:
        dict: 荷物情報
            package_number (int): 荷物番号
            status (str): 配達状況
            status_detail (str): 配達状況の詳細
            is_finished (bool): 配達が完了しているかどうか
            package_type (str): 荷物の種類
            delivery_time (str): 荷物の配達予定時間
            detail (list): 荷物の配達状況
                dict: 配達状況
                    title (str): 状況
                    date (str): 日時
                    name (str): 場所
    """
    data = {'number01': str(package_number)}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(INQUIRE_URL, data=data, headers=headers)

    if r.status_code != 200:
        print('荷物情報の取得に失敗しました')
        return {}

    soup = BeautifulSoup(r.content, 'html.parser')

    status = soup.select_one('.tracking-invoice-block-state-title').text
    status_detail = soup.select_one('.tracking-invoice-block-state-summary').text
    is_finished = status == '配達完了'

    summary_dom_list = soup.select('.tracking-invoice-block-summary li')
    package_type = summary_dom_list[0].select_one('.data').text
    delivery_time = summary_dom_list[1].select_one('.data').text

    detail_dom_list = soup.select('.tracking-invoice-block-detail li')
    detail_list = []
    for detail_dom in detail_dom_list:
        if detail_dom.select_one('name') is None:
            name = detail_dom.select_one('.name').text
        else:
            name = detail_dom.select_one('.name a').text

        detail_list.append({
            'title': detail_dom.select_one('.item').text,
            'date': detail_dom.select_one('.date').text,
            'name': name,
        })

    return {
        'package_number': package_number,
        'status': status,
        'status_detail': status_detail,
        'is_finished': is_finished,
        'package_type': package_type,
        'delivery_time': delivery_time,
        'details': detail_list,
    }


def monitor_package(package_number, interval_min=30):
    """荷物の配達状況を監視する

    荷物の配達状況が更新されるとLineに通知する。
    配達完了になると自動で終了する。

    Args:
        package_number (int): 荷物番号
        interval_min (int): 監視の間隔 (分)
    """
    print(f"start: {package_number}")

    before_package_info = {}
    while True:
        package_info = inquire_about_package(package_number)
        print('get: package info')

        if package_info != before_package_info:
            print(f"update: {pprint.pformat(package_info)}")
            package_info_str = _get_text_from_package_info(package_info)
            notification.notify_to_line(f'荷物番号{package_number}の配送状況が更新されました\n\n{package_info_str}')
            before_package_info = package_info.copy()

        if package_info['is_finished']:
            print(f"finish: {package_number}")
            break

        dt = datetime.datetime.now() + datetime.timedelta(minutes=interval_min)
        while datetime.datetime.now() < dt:
            time.sleep(60)


def _get_text_from_package_info(package_info):
    """荷物情報から文字列に変換する

    以下の形式で記述。
    ```
    ステータス: 配達完了 (このお品物はお届けが済んでおります。)
    配達予定日時: -
    配達状況:
      XX月XX日 XX:XX  荷物受付  (XXX支店)
      XX月XX日 XX:XX  発送済み  (XXX支店)
      XX月XX日 XX:XX  配達完了  (XXXセンター)
    ```
    配達予定日時の値がない場合は、配達予定日時の行を表示しない。

    Args:
        package_info (dict): 荷物情報

    Returns:
        str: 荷物情報の文字列
    """

    delivery_status_text = ''
    for item in package_info['details']:
        delivery_status_text += f"  {item['date']}  {item['title']}  ({item['name']})\n"

    delivery_time_text = ''
    if package_info['delivery_time'] != '-':
        delivery_time_text = f"{package_info['delivery_time']}\n"

    info_text = (
        f"{package_info['status']} ({package_info['status_detail']})\n"
        f"{delivery_time_text}"
        f"{delivery_status_text}"
    )

    return info_text


if __name__ == '__main__':
    monitor_package(000000000000, 10)
