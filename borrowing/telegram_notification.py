import telegram

from library_service import settings


async def send_message(message: str) -> None:
    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)
