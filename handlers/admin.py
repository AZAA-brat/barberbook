import asyncio
import html
from collections import Counter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import admintoken
from states import Broadcast
from texts import (
    ADMIN_MENU_TITLE,
    ADMIN_NO_ACCESS,
    ADMIN_TODAY_HEADER,
    BROADCAST_ASK_TEXT,
    BROADCAST_SENT,
)
from utils.storage import load_json, save_json, add_log

TZ = ZoneInfo("Asia/Tashkent")
BOOKINGS_FILE = "data/bookings.json"
USERS_FILE = "data/users.json"
SERVICES_FILE = "data/services.json"
REVIEWS_FILE = "data/reviews.json"

REVIEWS_LIMIT = 5
REVIEW_TEXT_MAX = 300

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id == int(admintoken)


def _load_bookings():
    return load_json(BOOKINGS_FILE) or []


def _load_users():
    return load_json(USERS_FILE) or {}


def _load_reviews():
    return load_json(REVIEWS_FILE) or []


def _load_services() -> dict:
    """Возвращает {id: service}. Поддерживает и список, и словарь."""
    data = load_json(SERVICES_FILE) or {}
    if isinstance(data, list):
        return {str(s.get("id")): s for s in data}
    return {str(k): v for k, v in data.items()}


def _booking_price(booking: dict, services: dict) -> int:
    """Цена записи: своя цена в записи, иначе цена услуги из services.json."""
    price = booking.get("price")
    if price is None:
        key = booking.get("service_id", booking.get("service"))
        price = services.get(str(key), {}).get("price", 0)
    try:
        return int(price)
    except (TypeError, ValueError):
        return 0


def _fmt_money(amount: int) -> str:
    return f"{amount:,}".replace(",", " ") + " сум"


def _stars(rating) -> str:
    try:
        n = max(0, min(5, int(rating)))
    except (TypeError, ValueError):
        return "—"
    return "⭐" * n


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not _is_admin(message.from_user.id):
        await message.answer(ADMIN_NO_ACCESS)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Записи на сегодня", callback_data="admin:today")],
        [InlineKeyboardButton(text="Статистика за неделю", callback_data="admin:stats")],
        [InlineKeyboardButton(text="Последние отзывы", callback_data="admin:reviews")],
        [InlineKeyboardButton(text="Рассылка", callback_data="admin:broadcast")],
    ])
    await message.answer(ADMIN_MENU_TITLE, reply_markup=kb)


@router.callback_query(F.data == "admin:today")
async def admin_today(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer(ADMIN_NO_ACCESS, show_alert=True)
        return

    bookings = _load_bookings()
    users = _load_users()
    today = datetime.now(TZ).date().isoformat()

    todays = sorted(
        (b for b in bookings if b.get("date") == today and b.get("status") == "active"),
        key=lambda b: b.get("time", ""),
    )

    if todays:
        lines = []
        for b in todays:
            client = users.get(str(b.get("user_id")), {})
            name = html.escape(client.get("name", "—"))
            lines.append(f"• {b.get('time', '—')} — {name}")
        body = "\n".join(lines)
    else:
        body = "Записей нет."

    await callback.message.answer(f"{ADMIN_TODAY_HEADER}\n{body}")
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer(ADMIN_NO_ACCESS, show_alert=True)
        return

    today = datetime.now(TZ).date()
    week_start = today - timedelta(days=6)  # 7 дней, включая сегодня
    start_iso, end_iso = week_start.isoformat(), today.isoformat()

    services = _load_services()
    week = [
        b for b in _load_bookings()
        if b.get("status") == "active"
        and start_iso <= str(b.get("date", "")) <= end_iso
    ]

    period = f"{week_start:%d.%m} — {today:%d.%m}"

    if not week:
        await callback.message.answer(
            f"📊 Статистика за неделю ({period})\n\nЗаписей за этот период нет."
        )
        await callback.answer()
        return

    revenue = sum(_booking_price(b, services) for b in week)

    masters = Counter(b.get("master") for b in week if b.get("master"))
    if masters:
        top_master, top_count = masters.most_common(1)[0]
        master_line = f"{html.escape(str(top_master))} ({top_count} зап.)"
    else:
        master_line = "—"

    await callback.message.answer(
        f"📊 <b>Статистика за неделю</b> ({period})\n\n"
        f"Записей: {len(week)}\n"
        f"Выручка: {_fmt_money(revenue)}\n"
        f"Самый загруженный мастер: {master_line}",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "admin:reviews")
async def admin_reviews(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer(ADMIN_NO_ACCESS, show_alert=True)
        return

    reviews = sorted(
        _load_reviews(),
        key=lambda r: str(r.get("created_at", "")),
        reverse=True,
    )[:REVIEWS_LIMIT]

    if not reviews:
        await callback.message.answer("Отзывов пока нет.")
        await callback.answer()
        return

    users = _load_users()
    blocks = []
    for r in reviews:
        name = users.get(str(r.get("user_id")), {}).get("name", "Клиент")
        text = str(r.get("text", "")).strip()
        if len(text) > REVIEW_TEXT_MAX:
            text = text[:REVIEW_TEXT_MAX].rstrip() + "…"
        date_part = str(r.get("created_at", ""))[:10]
        header = f"{_stars(r.get('rating'))} <b>{html.escape(str(name))}</b>"
        if date_part:
            header += f" · {html.escape(date_part)}"
        blocks.append(f"{header}\n{html.escape(text) or '—'}")

    await callback.message.answer(
        "💬 <b>Последние отзывы</b>\n\n" + "\n\n".join(blocks),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:cancel:"))
async def cancel_booking(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer(ADMIN_NO_ACCESS, show_alert=True)
        return

    booking_id = callback.data.removeprefix("admin:cancel:")
    bookings = _load_bookings()
    booking = next((b for b in bookings if str(b.get("id")) == booking_id), None)

    if booking is None or booking.get("status") != "active":
        await callback.answer("Запись не найдена или уже отменена.", show_alert=True)
        return

    booking["status"] = "cancelled"
    save_json(BOOKINGS_FILE, bookings)
    add_log(callback.from_user.id, "cancel_booking", f"booking_id={booking_id}")
    await callback.answer()

    notified = "у записи нет user_id, клиент не найден"
    client_id = booking.get("user_id")
    if client_id is not None:
        try:
            await callback.bot.send_message(
                client_id,
                f"Ваша запись на {booking.get('date')} в {booking.get('time')} отменена. "
                "Если нужно, запишитесь на другое время.",
            )
            notified = "клиент уведомлён"
        except TelegramAPIError:
            notified = "не удалось уведомить клиента"

    await callback.message.answer(f"Запись {booking_id} отменена, {notified}.")


@router.callback_query(F.data == "admin:broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer(ADMIN_NO_ACCESS, show_alert=True)
        return
    await state.set_state(Broadcast.text)
    await callback.answer()
    await callback.message.answer(BROADCAST_ASK_TEXT)


@router.message(Broadcast.text)
async def broadcast_preview(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        await state.clear()
        await message.answer(ADMIN_NO_ACCESS)
        return
    if not message.text:
        await message.answer("Пришлите текст сообщением.")
        return

    text_html = message.html_text
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Отправить", callback_data="admin:broadcast_send"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="admin:broadcast_cancel"),
    ]])
    try:
        await message.answer(f"Предпросмотр:\n\n{text_html}", parse_mode="HTML", reply_markup=kb)
    except TelegramBadRequest:
        await message.answer("Ошибка в HTML-тегах. Проверьте текст и пришлите заново.")
        return

    await state.update_data(broadcast_text=text_html)
    await state.set_state(Broadcast.confirm)


@router.callback_query(F.data == "admin:broadcast_send")
async def broadcast_send(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer(ADMIN_NO_ACCESS, show_alert=True)
        return

    text = (await state.get_data()).get("broadcast_text")
    if not text:
        await callback.answer("Текст не найден, начните заново.", show_alert=True)
        return
    await state.clear()
    await callback.answer("Рассылка запущена")

    sent = failed = 0
    for uid in _load_users():
        try:
            await callback.bot.send_message(int(uid), text, parse_mode="HTML")
            sent += 1
        except (TelegramAPIError, ValueError):
            failed += 1
        await asyncio.sleep(0.05)

    await callback.message.answer(
        f"{BROADCAST_SENT}\nДоставлено: {sent}, не доставлено: {failed}."
    )


@router.callback_query(F.data == "admin:broadcast_cancel")
async def broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.answer("Рассылка отменена.")
