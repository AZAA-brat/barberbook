from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.exceptions import TelegramAPIError
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from config import ADMIN_ID
from texts import (
    BTN_MY_BOOKINGS,
    BOOKING_CANCELLED,
    MY_BOOKINGS_EMPTY,
    MY_BOOKINGS_HEADER,
)
from utils.storage import load_json, save_json, add_log

router = Router()
TZ = ZoneInfo("Asia/Tashkent")
BOOKINGS_FILE = "data/bookings.json"


def _is_upcoming(booking: dict, now: datetime) -> bool:
    try:
        when = datetime.fromisoformat(f"{booking['date']} {booking['time']}")
    except (KeyError, ValueError):
        return False
    return when.replace(tzinfo=TZ) > now


def _fmt(booking: dict) -> str:
    day = datetime.fromisoformat(booking["date"]).strftime("%d.%m.%Y")
    return f"{day} в {booking['time']}"


@router.message(F.text == BTN_MY_BOOKINGS)
async def show_my_bookings(message: Message):
    now = datetime.now(TZ)
    bookings = load_json(BOOKINGS_FILE) or []

    mine = sorted(
        (
            b for b in bookings
            if b.get("user_id") == message.from_user.id
            and b.get("status") == "active"
            and _is_upcoming(b, now)
        ),
        key=lambda b: (b["date"], b["time"]),
    )

    if not mine:
        await message.answer(MY_BOOKINGS_EMPTY)
        return

    await message.answer(MY_BOOKINGS_HEADER, parse_mode="HTML")
    for b in mine:
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel:{b['id']}")
        ]])
        await message.answer(f"📅 {_fmt(b)}", reply_markup=kb)


@router.callback_query(F.data.startswith("cancel:"))
async def cancel_booking(callback: CallbackQuery):
    booking_id = callback.data.removeprefix("cancel:")
    bookings = load_json(BOOKINGS_FILE) or []

    booking = next(
        (b for b in bookings
         if str(b.get("id")) == booking_id
         and b.get("user_id") == callback.from_user.id),
        None,
    )
    if booking is None or booking.get("status") != "active":
        await callback.answer("Запись не найдена или уже отменена.", show_alert=True)
        return

    booking["status"] = "cancelled"
    save_json(BOOKINGS_FILE, bookings)
    add_log(callback.from_user.id, "cancel_booking", f"id={booking_id}")

    await callback.answer()
    await callback.message.edit_text(BOOKING_CANCELLED)

    try:
        await callback.bot.send_message(
            int(ADMIN_ID),
            f"⚠️ Клиент {callback.from_user.full_name} отменил запись: {_fmt(booking)}",
        )
    except TelegramAPIError:
        add_log(callback.from_user.id, "notify_admin_failed", f"id={booking_id}")