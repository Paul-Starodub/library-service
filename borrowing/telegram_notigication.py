import requests

from library_service import settings


def borrowing_telegram_notification(message: str) -> str:
    params = {"chat_id": settings.TELEGRAM_CHAT_ID, "text": message}
    url_result = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    result = requests.get(url_result, params=params).json()
    return result
