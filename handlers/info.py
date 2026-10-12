import os

from aiogram import Router, F
from aiogram.types import Message, FSInputFile

from texts import BTN_PRICES, BTN_CONTACTS, CONTACTS_TEXT
from utils.storage import BASE_DIR, load_json

router = Router()

CONTACT_PHOTO = os.path.join(BASE_DIR, "data", "contact_photo.jpg")
SHOP_LAT = 41.311081
SHOP_LON = 69.240562


@router.message(F.text == BTN_PRICES)
async def show_services(message: Message):
    services = load_json("data/services.json") or []
    if not services:
        await message.answer("Пока услуг нет.")
        return

    lines = ["💰 <b>Услуги и цены</b>\n"]
    for s in services:
        lines.append(
            f"🔹 {s['name']}\n"
            f"💵 Цена: {s['price']:,} сум\n"
            f"⏱️ Длительность: {s['duration']} мин\n"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(F.text == BTN_CONTACTS)
async def show_contacts(message: Message):
    if os.path.exists(CONTACT_PHOTO):
        await message.answer_photo(
            FSInputFile(CONTACT_PHOTO),
            caption=CONTACTS_TEXT,
            parse_mode="HTML",
        )
    else:
        await message.answer(CONTACTS_TEXT, parse_mode="HTML")
    await message.answer_location(latitude=SHOP_LAT, longitude=SHOP_LON)