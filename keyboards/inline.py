from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import texts


# У всех кнопок записи префикс "book_" — по нему ловим нажатия на устаревшие сообщения.
class ServiceCb(CallbackData, prefix="book_s"):
    id: int


class MasterCb(CallbackData, prefix="book_m"):
    id: int


class DateCb(CallbackData, prefix="book_d"):
    day: str  # ISO: "2026-10-13"


class TimeCb(CallbackData, prefix="book_t"):
    # Часы и минуты отдельно: ":" — разделитель внутри callback_data, "10:30" упаковать нельзя.
    hour: int
    minute: int


class NavCb(CallbackData, prefix="book_n"):
    action: str  # back | cancel | confirm


def nav_buttons(back=True):
    buttons = [InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data=NavCb(action="cancel").pack())]
    if back:
        buttons.insert(0, InlineKeyboardButton(text=texts.BTN_BACK, callback_data=NavCb(action="back").pack()))
    return buttons


def services_kb(services):
    builder = InlineKeyboardBuilder()
    for service in services:
        builder.button(text=service["name"], callback_data=ServiceCb(id=service["id"]))
    builder.adjust(1)
    builder.row(*nav_buttons(back=False))
    return builder.as_markup()


def masters_kb(masters):
    builder = InlineKeyboardBuilder()
    for master in masters:
        builder.button(text=master["name"], callback_data=MasterCb(id=master["id"]))
    builder.adjust(2)
    builder.row(*nav_buttons())
    return builder.as_markup()


def dates_kb(days, today):
    """days — список (date, есть_свободное_время)."""
    builder = InlineKeyboardBuilder()
    for day, has_slots in days:
        if not has_slots:
            template = texts.BOOK_DATE_BTN_BUSY
        elif day == today:
            template = texts.BOOK_DATE_BTN_TODAY
        else:
            template = texts.BOOK_DATE_BTN
        text = template.format(weekday=texts.WEEKDAYS_SHORT[day.weekday()], date=day.strftime("%d.%m"))
        builder.button(text=text, callback_data=DateCb(day=day.isoformat()))
    builder.adjust(3)
    builder.row(*nav_buttons())
    return builder.as_markup()


def times_kb(slots):
    builder = InlineKeyboardBuilder()
    for slot in slots:
        hour, minute = map(int, slot.split(":"))
        builder.button(text=slot, callback_data=TimeCb(hour=hour, minute=minute))
    builder.adjust(4)
    builder.row(*nav_buttons())
    return builder.as_markup()


def confirm_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BTN_CONFIRM, callback_data=NavCb(action="confirm"))
    builder.row(*nav_buttons())
    return builder.as_markup()
