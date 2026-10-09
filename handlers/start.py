from datetime import date
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from states import Registration
from keyboards.reply import phone_keyboard, main_menu
from texts import (
    WELCOME_TEXT, REG_ASK_NAME, REG_INVALID_NAME,
    REG_ASK_PHONE, REG_INVALID_PHONE, REG_DONE
)
from utils.storage import load_json, save_json, add_log
router = Router()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    users = load_json("data/users.json") or {}
    if str(message.from_user.id) in users:
        await message.answer(WELCOME_TEXT, reply_markup=main_menu)
        return
    await state.set_state(Registration.name)
    await message.answer(REG_ASK_NAME)

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
    data = await state.get_data()
    users = load_json("data/users.json") or {}

    users[str(message.from_user.id)] = {
        "name": data["name"],
        "phone": message.contact.phone_number,
        "registered": date.today().isoformat()
    }
    save_json("data/users.json", users)
    add_log(message.from_user.id, "register", data["name"])

    await state.clear()
    await message.answer(REG_DONE, reply_markup=main_menu)
@router.message(Registration.phone)
async def wrong_phone(message: Message):
    await message.answer(REG_INVALID_PHONE, reply_markup=phone_keyboard)
