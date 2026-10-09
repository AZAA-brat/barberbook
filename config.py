from dotenv import load_dotenv
import os
load_dotenv()

tokenbot = os.getenv("BOT_TOKEN")
admintoken = os.getenv("ADMIN_ID")

WORK_START = "10:00"
WORK_END = "20:00"