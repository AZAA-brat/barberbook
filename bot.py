from aiogram import Dispatcher, Bot
import asyncio
import logging
import handlers.admin as admin
import handlers.booking as booking
import handlers.info as info
import handlers.my_bookings as my_bookings
import handlers.reviews as reviews
import handlers.start as start
from config import tokenbot

bot = Bot(token=tokenbot)
dp = Dispatcher()
dp.include_routers(admin.router, booking.router, info.router, my_bookings.router, reviews.router, start.router)

logger = logging.getLogger(__name__)

async def main():
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())

