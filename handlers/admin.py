from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import ADMIN_ID
from texts import ADMIN_MENU_TITLE, ADMIN_NO_ACCESS, ADMIN_TODAY_HEADER
from utils.storage import load_json

TZ = ZoneInfo("Asia/Tashkent")

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id == int(ADMIN_ID)


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not _is_admin(message.from_user.id):
        await message.answer(ADMIN_NO_ACCESS)
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Записи на сегодня", callback_data="admin:today")]
        ]
    )
    await message.answer(ADMIN_MENU_TITLE, reply_markup=kb)


@router.callback_query(F.data == "admin:today")
async def admin_today(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer(ADMIN_NO_ACCESS, show_alert=True)
        return

    bookings = load_json("data/bookings.json") or []
    users = load_json("data/users.json") or {}
    today = datetime.now(TZ).date().isoformat()

    todays = [
        b for b in bookings
        if b.get("date") == today and b.get("status") == "active"
    ]
    todays.sort(key=lambda b: b.get("time", ""))

    if todays:
        lines = []
        for b in todays:
            client = users.get(str(b.get("user_id")), {})
            name = client.get("name", "—")
            lines.append(f"• {b.get('time', '—')} — {name}")
        body = "\n".join(lines)
    else:
        body = "Записей нет."

    await callback.message.answer(f"{ADMIN_TODAY_HEADER}\n{body}")
    await callback.answer()