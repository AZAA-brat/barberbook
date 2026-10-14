WELCOME_TEXT = (
    "💈 <b>BarberBook</b>\n\n"
    "Добро пожаловать в наш барбершоп!\n"
    "Здесь ты можешь записаться к мастеру "
    "и управлять своими записями.\n\n"
    "👇 <b>Выбери нужный раздел в меню.</b>"
)
CMD_START_DESC = "Запустить бота"
CMD_HELP_DESC = "Помощь и список команд"
CMD_ADMIN_DESC = "Панель администратора"
BOT_DESCRIPTION = (
    "💈 BarberBook — запись в барбершоп онлайн. "
    "Выбирай услугу, мастера и удобное время."
)
HELP_TEXT = (
    "ℹ️ <b>Помощь — BarberBook</b>\n\n"
    "Доступные команды:\n"
    "▫️ /start — главное меню\n"
    "▫️ /help — помощь и список команд\n"
    "▫️ /admin — панель администратора\n\n"
    "✂️ Выбирай услугу и записывайся к мастеру "
    "через меню бота."
)
ERROR_GENERIC = "⚠️ Что-то пошло не так. Попробуйте ещё раз."
BTN_BACK = "⬅️ Назад"
BTN_CANCEL = "❌ Отмена"

REG_ASK_NAME = "Как вас зовут? Введите имя и фамилию."
REG_INVALID_NAME = "Введите имя и фамилию через пробел, например: <i>Азиз Икрамов</i>"
REG_ASK_PHONE = "Отправьте ваш номер телефона кнопкой ниже."
REG_INVALID_PHONE = "Не похоже на номер телефона. Используйте кнопку «Отправить контакт»."
REG_DONE = "✅ <b>Регистрация завершена!</b>\nТеперь вы можете записаться."

BTN_BOOK = "✂️ Записаться"
BTN_MY_BOOKINGS = "📋 Мои записи"
BTN_PRICES = "💰 Услуги и цены"
BTN_CONTACTS = "📍 Контакты"
BTN_REVIEW = "⭐️ Оставить отзыв"
BTN_SEND_CONTACT = "📱 Отправить контакт"

BOOK_CHOOSE_SERVICE = "Выберите услугу:"
BOOK_CHOOSE_MASTER = "Выберите мастера:"
BOOK_CHOOSE_DATE = (
    "📅 Выберите дату:\n\n"
    "📍 — сегодня   ✖ — нет свободного времени"
)
BOOK_DATE_IN_PAST = "Эта дата уже прошла, выберите другую"
BOOK_DATE_CHOSEN = "📅 Дата: {date}"
BOOK_CHOOSE_TIME = "Выберите свободное время:"
BOOK_NO_SLOTS = "На эту дату свободного времени нет. Выберите другой день."
BOOK_SLOT_TAKEN = "😔 Это время только что заняли. Выберите другое."
BOOK_DETAILS = (
    "Услуга: {service}\n"
    "Мастер: {master}\n"
    "Дата: {date}\n"
    "Время: {time}\n"
    "Цена: {price} сум"
)
BOOK_CONFIRM_TEMPLATE = "<b>Проверьте запись:</b>\n" + BOOK_DETAILS
BOOK_SAVED = "🎉 Вы записаны! Ждём вас."
BOOK_ABORTED = "Запись отменена. Возвращайтесь, когда будет удобно 👋"
BOOK_EXPIRED = "Эта запись уже неактуальна. Нажмите «✂️ Записаться», чтобы начать заново."
BTN_CONFIRM = "✅ Подтвердить"

WEEKDAYS_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
BOOK_DATE_BTN = "{weekday} {date}"
BOOK_DATE_BTN_TODAY = "📍 {weekday} {date}"
BOOK_DATE_BTN_BUSY = "✖ {weekday} {date}"

MY_BOOKINGS_EMPTY = "У вас пока нет записей."
MY_BOOKINGS_HEADER = "<b>Ваши записи:</b>"
BOOKING_CANCELLED = "Запись отменена."
CONTACTS_TEXT = (
    "<b>BarberBook</b>\n"
    "📍 Адрес: ул. Пример, 1\n"
    "🕘 Часы работы: 10:00–20:00"
)
ADMIN_MENU_TITLE = "<b>Админ-панель</b>"
ADMIN_NO_ACCESS = "⛔️ Доступ только для администратора."
ADMIN_TODAY_HEADER = "<b>Записи на сегодня:</b>"
ADMIN_NEW_BOOKING = "🆕 <b>Новая запись #{id}</b>\nКлиент: {client}\n" + BOOK_DETAILS
BROADCAST_ASK_TEXT = "Введите текст рассылки:"
BROADCAST_SENT = "✅ Рассылка отправлена."

REVIEW_ASK_RATING = "Оцените нас от 1 до 5 звёзд:"
REVIEW_ASK_TEXT = "Напишите пару слов о визите:"
REVIEW_THANKS = "Спасибо за отзыв! 🙏"
