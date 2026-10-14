import re
from datetime import datetime, date
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.reply import phone_keyboard, main_menu
from states import Registration
from texts import (
    WELCOME_TEXT,
    REG_ASK_NAME,
    REG_ASK_PHONE,
    REG_INVALID_NAME,
    REG_INVALID_PHONE,
    REG_DONE,
    HELP_TEXT,
)
from utils.storage import load_json, save_json, add_log

TZ = ZoneInfo("Asia/Tashkent")
# Номер Узбекистана: 998 и 9 цифр, знак + может отсутствовать
PHONE_RE = re.compile(r"^\+?998\d{9}$")

router = Router()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    users = load_json("data/users.json") or {}
    if str(message.from_user.id) in users:
        await message.answer(WELCOME_TEXT, reply_markup=main_menu)
        return

    await state.set_state(Registration.name)
    await message.answer(REG_ASK_NAME)


# Выше хендлера имени: во время регистрации /help не должен сохраниться как имя.
@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(HELP_TEXT)


@router.message(Registration.name)
async def get_name(message: Message, state: FSMContext):
    if not message.text or len(message.text.split()) < 2:
        await message.answer(REG_INVALID_NAME)
        return

    await state.update_data(name=message.text)
    await state.set_state(Registration.phone)
    await message.answer(REG_ASK_PHONE, reply_markup=phone_keyboard)


@router.message(Registration.phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if not PHONE_RE.fullmatch(phone):
        await message.answer(REG_INVALID_PHONE, reply_markup=phone_keyboard)
        return

    data = await state.get_data()
    users = load_json("data/users.json") or {}
    users[str(message.from_user.id)] = {
        "name": data["name"],
        "phone": phone,
        "registered": datetime.now(TZ).date().isoformat(),
    }
    save_json("data/users.json", users)
    add_log(message.from_user.id, "register", data["name"])

    await state.clear()
    await message.answer(REG_DONE, reply_markup=main_menu)


@router.message(Registration.phone)
async def wrong_phone(message: Message):
    await message.answer(REG_INVALID_PHONE, reply_markup=phone_keyboard)