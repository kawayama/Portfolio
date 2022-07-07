import json
import os

from plyer import notification
import requests


SLACK_API_URL = r'https://hooks.slack.com/services'
LINE_API_URL = r'https://notify-api.line.me/api/notify'

SLACK_API_KEY = {
    'general': 'XXX',
    'error': 'XXX'
}
LINE_API_KEY = 'XXX'


def notify_to_slack(content, channel='error'):
    """Incoming Webhookを用いたSlackへの通知メソッド

    Args:
        content (str): 通知する内容
        channel (str): 通知先のチャンネル

    Returns:
        bool: 通知が成功したかどうか

    Notes:
        APIに関する資料: https://api.slack.com/messaging/webhooks
    """
    api_key = SLACK_API_KEY
    if channel in api_key.keys():
        full_url = SLACK_API_URL + api_key[channel]
    else:
        return False

    data = {'text': content}
    r = requests.post(full_url, data=json.dumps(data))
    is_succeeded = r.status_code == 200

    return is_succeeded


def notify_to_line(text):
    """Line Notify APIを用いたLineへの通知メソッド

    Args:
        text (str): 通知するテキスト

    Returns:
        bool: 通知が成功したかどうか

    Notes:
        APIに関する資料：https://notify-bot.line.me/doc/ja/
    """
    api_key = LINE_API_KEY
    headers = {'Authorization': 'Bearer ' + api_key}
    data = {'message': f"\n{text}"}
    r = requests.post(LINE_API_URL, headers=headers, data=data)
    is_succeeded = r.status_code == 200
    return is_succeeded


def notify_to_pc(title, message):
    """PCに通知を送信する

    Args:
        title: 通知のタイトル
        message: 通知の内容
    """
    if os.name == 'nt':
        # plyer.notification
        notification.notify(
            title=title,
            message=message,
            app_name='MultiGetterX',
            timeout=10,
        )
    elif os.name == 'posix':
        os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")
    else:
        print('このOSは通知に対応していません')
