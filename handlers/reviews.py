import html
import json
import os
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from texts import BTN_REVIEW, REVIEW_ASK_TEXT

router = Router()

ADMIN_IDS = [
    int(admin_id)
    for admin_id in os.getenv("ADMIN_ID", "").split(",")
    if admin_id.strip()
]


class ReviewStates(StatesGroup):
    rating = State()
    text = State()


@router.message(Command("review"))
@router.message(F.text == BTN_REVIEW)
async def start_review(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()

    for star in range(1, 6):
        builder.button(
            text="⭐" * star,
            callback_data=f"review_rating:{star}"
        )

    builder.adjust(1)

    await message.answer(
        "Оцените нашу работу:",
        reply_markup=builder.as_markup()
    )

    await state.set_state(ReviewStates.rating)


@router.callback_query(
    F.data.startswith("review_rating:"),
    ReviewStates.rating
)
async def choose_rating(
    callback: CallbackQuery,
    state: FSMContext
):
    rating = int(callback.data.split(":")[1])

    await state.update_data(rating=rating)
    await state.set_state(ReviewStates.text)

    await callback.message.edit_text(
        f"Ваша оценка: {'⭐' * rating}\n\n"
        "Теперь напишите свой отзыв:"
    )

    await callback.answer()


@router.message(ReviewStates.text)
async def save_review(
    message: Message,
    state: FSMContext
):
    if not message.text:
        await message.answer(REVIEW_ASK_TEXT)
        return

    data = await state.get_data()

    review = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "name": message.from_user.full_name,
        "rating": data["rating"],
        "text": message.text,
        "date": datetime.now().isoformat(timespec="seconds")
    }

    try:
        with open("reviews.json", "r", encoding="utf-8") as file:
            reviews = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        reviews = []

    reviews.append(review)

    with open("reviews.json", "w", encoding="utf-8") as file:
        json.dump(
            reviews,
            file,
            ensure_ascii=False,
            indent=4
        )

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                admin_id,
                f"📝 Новый отзыв!\n\n"
                f"👤 Имя: {html.escape(review['name'])}\n"
                f"🆔 ID: {review['user_id']}\n"
                f"⭐ Оценка: {review['rating']}/5\n"
                f"💬 Отзыв: {html.escape(review['text'])}"
            )
        except Exception:
            pass

    await message.answer("✅ Спасибо за ваш отзыв!")
    await state.clear()
