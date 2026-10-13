from datetime import datetime, date
from zoneinfo import ZoneInfo

from utils.storage import load_json

TZ = ZoneInfo("Asia/Tashkent")
OPEN = 10 * 60
CLOSE = 20 * 60
STEP = 30


def load_data():
    services = load_json("data/services.json")
    masters = load_json("data/masters.json")
    bookings = load_json("data/bookings.json")

    if services is None or masters is None or bookings is None:
        return None
    return services, masters, bookings


def _to_minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _from_minutes(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def get_free_slots(master_id, day, service_id):
    data = load_data()
    if data is None:
        return []
    services, masters, bookings = data

    service = next((s for s in services if s["id"] == service_id), None)
    master = next((m for m in masters if m["id"] == master_id), None)
    if service is None or master is None:
        return []
    if service_id not in master["services"]:
        return []

    try:
        target = date.fromisoformat(day)
    except ValueError:
        return []

    now = datetime.now(TZ)
    today = now.date()
    if target < today:
        return []

    names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if master["day_off"] == names[target.weekday()]:
        return []

    busy = []
    for b in bookings:
        if b["master_id"] != master_id or b["date"] != day or b["status"] != "active":
            continue
        b_service = next((s for s in services if s["id"] == b["service_id"]), None)
        if b_service is None:
            continue
        start = _to_minutes(b["time"])
        busy.append((start, start + b_service["duration"]))

    earliest = OPEN
    if target == today:
        now_min = now.hour * 60 + now.minute
        earliest = max(OPEN, -(-now_min // STEP) * STEP)

    duration = service["duration"]
    free = []
    for start in range(OPEN, CLOSE, STEP):
        if start < earliest:
            continue
        end = start + duration
        if end > CLOSE:
            break
        if any(start < b_end and b_start < end for b_start, b_end in busy):
            continue
        free.append(_from_minutes(start))

    return free