from aiogram import Router, F
from aiogram.types import Message
from texts import BTN_PRICES
from utils.storage import load_json

router = Router()

@router.message(F.text == BTN_PRICES)
async def show_services(message: Message):
    data = load_json("data/services.json") or {}
    services = data or []
    if not services:
        await message.answer("Пока услуг нет.")
        return
    text = "💰 УСЛУГИ И ЦЕНЫ\n\n"
    for service in services:
        text += (
            f"🔹 {service['name']}\n"
            f"💵 Цена: {service['price']:,} сум\n"
            f"📝 {service['duration']}\n\n"
        )
    await message.answer(text)