import html
import logging
from datetime import date, datetime, timedelta

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User

import texts
from config import BOOKING_DAYS, TIMEZONE, admintoken
from keyboards.inline import (
    DateCb, MasterCb, NavCb, ServiceCb, TimeCb,
    confirm_kb, dates_kb, masters_kb, services_kb, times_kb,
)
from states import Booking
from utils.slots import get_free_slots
from utils.storage import add_log, load_json, save_json

router = Router()
logger = logging.getLogger(__name__)

SERVICES_FILE = "data/services.json"
MASTERS_FILE = "data/masters.json"
BOOKINGS_FILE = "data/bookings.json"


def find(filename, item_id):
    return next((item for item in load_json(filename) if item["id"] == item_id), None)


def upcoming_days():
    today = datetime.now(TIMEZONE).date()
    return [today + timedelta(days=i) for i in range(BOOKING_DAYS)]


def free_slots(data, day):
    service = find(SERVICES_FILE, data["service_id"])
    return get_free_slots(data["master_id"], day, service["duration"])


def format_date(day):
    return f"{day:%d.%m.%Y} ({texts.WEEKDAYS_SHORT[day.weekday()]})"


def details(data):
    service = find(SERVICES_FILE, data["service_id"])
    master = find(MASTERS_FILE, data["master_id"])
    return {
        "service": html.escape(service["name"]),
        "master": html.escape(master["name"]),
        "date": format_date(date.fromisoformat(data["date"])),
        "time": data["time"],
        "price": f"{service['price']:,}".replace(",", " "),
    }


async def edit(message: Message, text, reply_markup=None):
    # Повторный показ того же экрана (например, обновили даты после алерта) — не ошибка.
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in e.message:
            raise


# --- Шаги. Каждый ставит своё состояние и перерисовывает одно и то же сообщение. ---

async def ask_service(message: Message, state: FSMContext):
    await state.set_state(Booking.service)
    await edit(message, texts.BOOK_CHOOSE_SERVICE, services_kb(load_json(SERVICES_FILE)))


async def ask_master(message: Message, state: FSMContext):
    data = await state.get_data()
    masters = [m for m in load_json(MASTERS_FILE) if data["service_id"] in m["services"]]
    await state.set_state(Booking.master)
    await edit(message, texts.BOOK_CHOOSE_MASTER, masters_kb(masters))


async def ask_date(message: Message, state: FSMContext):
    data = await state.get_data()
    days = [(day, bool(free_slots(data, day))) for day in upcoming_days()]
    await state.set_state(Booking.date)
    await edit(message, texts.BOOK_CHOOSE_DATE, dates_kb(days, today=days[0][0]))


async def ask_time(message: Message, state: FSMContext):
    data = await state.get_data()
    day = date.fromisoformat(data["date"])
    slots = free_slots(data, day)
    if not slots:
        await ask_date(message, state)
        return
    await state.set_state(Booking.time)
    text = texts.BOOK_DATE_CHOSEN.format(date=format_date(day)) + "\n" + texts.BOOK_CHOOSE_TIME
    await edit(message, text, times_kb(slots))


async def ask_confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(Booking.confirm)
    await edit(message, texts.BOOK_CONFIRM_TEMPLATE.format(**details(data)), confirm_kb())


BACK_STEPS = {
    Booking.master.state: ask_service,
    Booking.date.state: ask_master,
    Booking.time.state: ask_date,
    Booking.confirm.state: ask_time,
}


# --- Хендлеры ---

@router.message(Command("book"))
@router.message(F.text == texts.BTN_BOOK)
async def start_booking(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Booking.service)
    await message.answer(texts.BOOK_CHOOSE_SERVICE, reply_markup=services_kb(load_json(SERVICES_FILE)))


@router.callback_query(Booking.service, ServiceCb.filter())
async def pick_service(callback: CallbackQuery, callback_data: ServiceCb, state: FSMContext):
    if find(SERVICES_FILE, callback_data.id) is None:
        return await expired(callback)
    await state.update_data(service_id=callback_data.id)
    await ask_master(callback.message, state)
    await callback.answer()


@router.callback_query(Booking.master, MasterCb.filter())
async def pick_master(callback: CallbackQuery, callback_data: MasterCb, state: FSMContext):
    data = await state.get_data()
    master = find(MASTERS_FILE, callback_data.id)
    if master is None or data["service_id"] not in master["services"]:
        return await expired(callback)
    await state.update_data(master_id=master["id"])
    await ask_date(callback.message, state)
    await callback.answer()


@router.callback_query(Booking.date, DateCb.filter())
async def pick_date(callback: CallbackQuery, callback_data: DateCb, state: FSMContext):
    day = date.fromisoformat(callback_data.day)
    if day not in upcoming_days():
        # Экран висел с прошлых суток — показываем актуальную неделю.
        await callback.answer(texts.BOOK_DATE_IN_PAST, show_alert=True)
        return await ask_date(callback.message, state)
    if not free_slots(await state.get_data(), day):
        await callback.answer(texts.BOOK_NO_SLOTS, show_alert=True)
        return await ask_date(callback.message, state)
    await state.update_data(date=day.isoformat())
    await ask_time(callback.message, state)
    await callback.answer()


@router.callback_query(Booking.time, TimeCb.filter())
async def pick_time(callback: CallbackQuery, callback_data: TimeCb, state: FSMContext):
    time = f"{callback_data.hour:02d}:{callback_data.minute:02d}"
    data = await state.get_data()
    if time not in free_slots(data, date.fromisoformat(data["date"])):
        await callback.answer(texts.BOOK_SLOT_TAKEN, show_alert=True)
        return await ask_time(callback.message, state)
    await state.update_data(time=time)
    await ask_confirm(callback.message, state)
    await callback.answer()


@router.callback_query(Booking.confirm, NavCb.filter(F.action == "confirm"))
async def confirm_booking(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    # Проверка слота и запись в файл идут без await между ними, поэтому
    # другой клиент не может занять это время в промежутке.
    if data["time"] not in free_slots(data, date.fromisoformat(data["date"])):
        await callback.answer(texts.BOOK_SLOT_TAKEN, show_alert=True)
        return await ask_time(callback.message, state)
    booking = save_booking(callback.from_user, data)
    await state.clear()

    add_log(callback.from_user.id, "booking_created",
            f"#{booking['id']} {booking['service']} | {booking['master']} | {booking['date']} {booking['time']}")
    booking_details = details(data)
    await edit(callback.message, texts.BOOK_SAVED + "\n\n" + texts.BOOK_DETAILS.format(**booking_details))
    await callback.answer()
    await notify_admin(bot, booking["id"], callback.from_user, booking_details)


@router.callback_query(StateFilter(Booking), NavCb.filter(F.action == "back"))
async def go_back(callback: CallbackQuery, state: FSMContext):
    previous_step = BACK_STEPS.get(await state.get_state())
    if previous_step is None:
        return await expired(callback)
    await previous_step(callback.message, state)
    await callback.answer()


@router.callback_query(StateFilter(Booking), NavCb.filter(F.action == "cancel"))
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await edit(callback.message, texts.BOOK_ABORTED)
    await callback.answer()


@router.callback_query(F.data.startswith("book_"))
async def expired(callback: CallbackQuery):
    """Кнопка из старого сообщения: запись уже завершена/отменена или бот перезапускался."""
    await callback.answer(texts.BOOK_EXPIRED, show_alert=True)
    if isinstance(callback.message, Message):
        await callback.message.edit_reply_markup(reply_markup=None)


# --- Сохранение и уведомление ---

def save_booking(user: User, data):
    service = find(SERVICES_FILE, data["service_id"])
    master = find(MASTERS_FILE, data["master_id"])
    bookings = load_json(BOOKINGS_FILE)
    booking = {
        "id": max((b["id"] for b in bookings), default=0) + 1,
        "user_id": user.id,
        "user_name": user.full_name,
        "username": user.username,
        "service_id": service["id"],
        "service": service["name"],
        "master_id": master["id"],
        "master": master["name"],
        "date": data["date"],
        "time": data["time"],
        "duration": service["duration"],
        "price": service["price"],
        "status": "active",
        "created_at": datetime.now(TIMEZONE).isoformat(timespec="seconds"),
    }
    bookings.append(booking)
    save_json(BOOKINGS_FILE, bookings)
    return booking


async def notify_admin(bot: Bot, booking_id, user: User, booking_details):
    if not admintoken:
        logger.warning("ADMIN_ID не задан, уведомление о записи #%s не отправлено", booking_id)
        return
    client = f'<a href="tg://user?id={user.id}">{html.escape(user.full_name)}</a>'
    if user.username:
        client += f" (@{user.username})"
    text = texts.ADMIN_NEW_BOOKING.format(id=booking_id, client=client, **booking_details)
    try:
        await bot.send_message(int(admintoken), text)
    except (TelegramAPIError, ValueError):
        # Запись уже сохранена, клиенту ошибку не показываем.
        logger.exception("Не удалось уведомить админа о записи #%s", booking_id)
