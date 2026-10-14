from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from texts import HELP_TEXT

router = Router()


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        HELP_TEXT,
        parse_mode="HTML",
    )