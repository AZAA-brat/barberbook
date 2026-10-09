import json
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_json(filename):
    try:
        with open(os.path.join(BASE_DIR, filename), 'r', encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_json(filename, data):
    with open(os.path.join(BASE_DIR, filename), 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_log(user_id, action, details):
    date = datetime.now()
    with open(os.path.join(BASE_DIR, "data/logs.txt"), "a", encoding="utf-8") as f:
        f.write(f"{date} | {user_id} | {action} | {details}\n")
