import datetime
import re
from pprint import pprint

import requests
from bs4 import BeautifulSoup

URL = {
    'Tokyo': {
        'Tiyoda': 'https://weather.yahoo.co.jp/weather/13/4410/13101.html',
    },
    'Kanagawa': {
        'Nishi': 'https://weather.yahoo.co.jp/weather/14/4610/14103.html',
    },
}


def get_weather(url):
    """天気を辞書型で取得する

    Args:
        url (str): 取得する地域のYahoo天気のURL

    Returns:
        dict: 天気情報 (today, tommorow, weekly)

    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    return {
        'today': _parse_date_table(soup, '#yjw_pinpoint_today table tr'),
        'tommorow': _parse_date_table(soup, '#yjw_pinpoint_tomorrow table tr'),
        'weekly': _parse_weekly_table(soup, '#yjw_week table tr')
    }


def _parse_date_table(soup, selector):
    """1日の天気のテーブルから情報を取得する"""
    date_item_list = [[re.sub(r'(^\n*| *|\n*$)', '', item.text)
                       for i, item in enumerate(tr_dom.select('td')) if i != 0]
                      for tr_dom in soup.select(selector)]

    date_dict = {}
    for hour, weather, temperature, humidity, p_amount, wind in zip(*date_item_list):
        hour_num = hour[:-1]
        wind_list = wind.split('\n')

        date_dict[hour_num] = {
            'weather': weather,
            'temperature': temperature,
            'humidity': humidity,
            'precipitation_amount': p_amount,
            'wind_direction': wind_list[0],
            'wind_speed': wind_list[1],
        }

    return date_dict


def _parse_weekly_table(soup, selector):
    """1週間の天気のテーブルから情報を取得する"""
    weekly_item_list = [[re.sub(r'(^\n*| *|\n*$)', '', item.text)
                         for i, item in enumerate(tr_dom.select('td')) if i != 0]
                        for tr_dom in soup.select(selector)]

    weekly_dict = {}
    for date, weather, temperature, rainy_percent in zip(*weekly_item_list):
        date_ins = datetime.datetime.strptime(date.replace('\n', '').split('(')[0], '%m月%d日').date()
        date_ins = _get_closest_date(date_ins)
        temperature_list = temperature.split('\n')

        weekly_dict[date_ins] = {
            'weather': weather,
            'temperature_upper': temperature_list[0],
            'temperature_lower': temperature_list[1],
            'rainy percent': rainy_percent,
        }

    return weekly_dict


def _get_closest_date(date):
    """日付から適当と考えられる年を取得する"""
    today = datetime.date.today()
    date1 = date.replace(year=today.year)
    date2 = date.replace(year=today.year + 1)
    diff1 = today - date1
    diff2 = today - date2
    if diff1 < diff2:
        return date1
    else:
        return date2


if __name__ == '__main__':
    pprint(
        get_weather(URL['Tokyo']['Tiyoda'])
    )
