from celery import shared_task

from borrowing.monitoring import filtering_borrowing
from borrowing.telegram_notification import borrowing_telegram_notification


@shared_task
def run_sync_with_api() -> None:
    message = filtering_borrowing()
    if len(message) > 4096:
        for char in range(0, len(message), 4096):
            borrowing_telegram_notification(message=message[char: char + 4096])
        else:
            borrowing_telegram_notification(message=message)
