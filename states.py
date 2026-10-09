from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

router = Router()

class Registration(StatesGroup):
    name = State()
    phone = State()

class Booking(StatesGroup):
    service = State()
    master = State()
    date = State()
    time = State()
    confirm = State()

class Review(StatesGroup):
    rating = State()
    text = State()

class Broadcast(StatesGroup):
    text = State()
    confirm = State()


