from datetime import date

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import texts
from keyboards.inline import CalendarCb, MONTHS, calendar_kb
from states import Booking

router = Router()


def calendar_text(year, month):
    return texts.CHOOSE_DATE.format(month=MONTHS[month - 1], year=year)


async def ask_date(message: Message, state: FSMContext):
    today = date.today()
    await state.set_state(Booking.date)
    await message.answer(calendar_text(today.year, today.month),
                         reply_markup=calendar_kb(today.year, today.month))


@router.callback_query(CalendarCb.filter(F.action == "ignore"))
async def calendar_ignore(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(CalendarCb.filter(F.action == "month"))
async def calendar_switch_month(callback: CallbackQuery, callback_data: CalendarCb):
    year, month = callback_data.year, callback_data.month
    await callback.message.edit_text(calendar_text(year, month),
                                     reply_markup=calendar_kb(year, month))
    await callback.answer()


@router.callback_query(Booking.date, CalendarCb.filter(F.action == "day"))
async def calendar_pick_day(callback: CallbackQuery, callback_data: CalendarCb, state: FSMContext):
    picked = date(callback_data.year, callback_data.month, callback_data.day)
    today = date.today()
    if picked < today:
        await callback.answer(texts.DATE_IN_PAST, show_alert=True)
        await callback.message.edit_text(calendar_text(today.year, today.month),
                                         reply_markup=calendar_kb(today.year, today.month))
        return

    await state.update_data(date=picked.isoformat())
    await state.set_state(Booking.time)
    await callback.message.edit_text(texts.DATE_CHOSEN.format(date=picked.strftime("%d.%m.%Y")))
    await callback.answer()
