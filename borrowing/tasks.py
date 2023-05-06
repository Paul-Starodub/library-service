import asyncio

from celery import shared_task

from borrowing.monitoring import filtering_borrowing
from borrowing.telegram_notification import send_message


@shared_task
def run_sync_with_api() -> None:
    message = filtering_borrowing()
    asyncio.run(send_message(message=message))
