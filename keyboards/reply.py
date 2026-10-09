from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from texts import (
    BTN_SEND_CONTACT, BTN_BOOK, BTN_MY_BOOKINGS,
    BTN_PRICES, BTN_CONTACTS, BTN_REVIEW
)

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_SEND_CONTACT, request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_BOOK), KeyboardButton(text=BTN_MY_BOOKINGS)],
        [KeyboardButton(text=BTN_PRICES), KeyboardButton(text=BTN_CONTACTS)],
        [KeyboardButton(text=BTN_REVIEW)]
    ],
    resize_keyboard=True
)