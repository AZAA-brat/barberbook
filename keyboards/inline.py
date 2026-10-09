import calendar
from datetime import date

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

MONTHS = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


class CalendarCb(CallbackData, prefix="cal"):
    action: str
    year: int = 0
    month: int = 0
    day: int = 0


def shift_month(year, month, n):
    index = year * 12 + month - 1 + n
    return index // 12, index % 12 + 1


def calendar_kb(year, month, busy_days=(), months_before=0, months_after=2):
    today = date.today()
    ignore = CalendarCb(action="ignore").pack()
    builder = InlineKeyboardBuilder()

    tabs = []
    for n in range(-months_before, months_after + 1):
        y, m = shift_month(today.year, today.month, n)
        if (y, m) == (year, month):
            tabs.append(InlineKeyboardButton(text=f"• {MONTHS[m - 1]} •", callback_data=ignore))
        else:
            cb = CalendarCb(action="month", year=y, month=m).pack()
            tabs.append(InlineKeyboardButton(text=MONTHS[m - 1], callback_data=cb))
    builder.row(*tabs, width=3)

    builder.row(*[InlineKeyboardButton(text=wd, callback_data=ignore) for wd in WEEKDAYS])

    for week in calendar.monthcalendar(year, month):
        if date(year, month, max(week)) < today:
            continue
        row = []
        for day in week:
            if day == 0 or date(year, month, day) < today:
                row.append(InlineKeyboardButton(text=" ", callback_data=ignore))
            elif date(year, month, day) in busy_days:
                row.append(InlineKeyboardButton(text="✖", callback_data=ignore))
            else:
                text = f"📍{day}" if date(year, month, day) == today else str(day)
                cb = CalendarCb(action="day", year=year, month=month, day=day).pack()
                row.append(InlineKeyboardButton(text=text, callback_data=cb))
        builder.row(*row)

    return builder.as_markup()
