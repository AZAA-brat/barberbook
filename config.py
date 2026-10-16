from datetime import timedelta, timezone

from dotenv import load_dotenv
import os
load_dotenv()

tokenbot = os.getenv("BOT_TOKEN")
admintoken = os.getenv("ADMIN_ID")
# Несколько админов — через запятую: ADMIN_ID=111,222
ADMIN_IDS = [int(x) for x in (admintoken or "").split(",") if x.strip().isdigit()]

WORK_START = "10:00"
WORK_END = "20:00"
SLOT_STEP = 30
BOOKING_DAYS = 7

TIMEZONE = timezone(timedelta(hours=5))
