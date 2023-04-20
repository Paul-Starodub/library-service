import requests


def borrowing_telegram_notification(token: str, chat_id: str, message: str):
    url_result = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    result = requests.get(url_result).json()
    return result
