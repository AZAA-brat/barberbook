from datetime import timedelta, timezone

from dotenv import load_dotenv
import os
load_dotenv()

tokenbot = os.getenv("BOT_TOKEN")
admintoken = os.getenv("ADMIN_ID")

WORK_START = "10:00"
WORK_END = "20:00"
SLOT_STEP = 30
BOOKING_DAYS = 7

TIMEZONE = timezone(timedelta(hours=5))
