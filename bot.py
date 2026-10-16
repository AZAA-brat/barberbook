from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import SimpleEventIsolation
import asyncio
import logging
import handlers.admin as admin
import handlers.booking as booking
import handlers.info as info
import handlers.my_bookings as my_bookings
import handlers.reviews as reviews
import handlers.start as start
import handlers.help as help
from config import tokenbot
from texts import CMD_START_DESC, CMD_HELP_DESC, CMD_ADMIN_DESC, BOT_DESCRIPTION

bot = Bot(token=tokenbot, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(events_isolation=SimpleEventIsolation())
dp.include_routers(admin.router, booking.router, info.router, my_bookings.router, reviews.router, start.router, help.router)

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(level=logging.INFO)
    if not ADMIN_IDS:
        logger.warning("ADMIN_ID в .env пустой или не число: /admin и уведомления админу работать не будут")
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())

async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description=CMD_START_DESC),
        BotCommand(command="help", description=CMD_HELP_DESC),
        BotCommand(command="admin", description=CMD_ADMIN_DESC),
    ]
    await bot.set_my_commands(commands)
    await bot.set_my_description(description=BOT_DESCRIPTION)
