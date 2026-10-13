from datetime import timedelta, timezone

from dotenv import load_dotenv
import os
load_dotenv()

tokenbot = os.getenv("BOT_TOKEN")
admintoken = os.getenv("ADMIN_ID")

WORK_START = "10:00"
WORK_END = "20:00"
SLOT_STEP = 30  # шаг сетки времени, минут
BOOKING_DAYS = 7  # на сколько дней вперёд можно записаться

# Ташкент, UTC+5 без перехода на летнее время. Фиксированный сдвиг вместо zoneinfo,
# чтобы не тянуть tzdata на Windows и не зависеть от часового пояса сервера.
TIMEZONE = timezone(timedelta(hours=5))
