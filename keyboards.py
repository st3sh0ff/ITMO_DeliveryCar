from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

inline_kb_full = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Заказы", callback_data='/orders'),
         InlineKeyboardButton(text="Доставщики", callback_data='/deliverers')],
        [InlineKeyboardButton(text="Сообщения", callback_data='/msg')],
        [InlineKeyboardButton(text="Завершенные заказы", callback_data='/completed ')]
    ]
)

markup_request = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить свою локацию 🗺️", request_location=True)],
        [KeyboardButton(text="Указать адрес")]
    ],
    resize_keyboard=True
)

markup_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Заказчики"), KeyboardButton(text="Доставщики")],
        [KeyboardButton(text="Заказы"), KeyboardButton(text="Выход")]
    ],
    resize_keyboard=True
)

markup_admin_remove = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Удалить запись")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

markup_admin_order = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Посмотреть заказы")],
        [KeyboardButton(text="Создать заказ")],
        [KeyboardButton(text="Удалить заказ")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

start = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start")],
        [KeyboardButton(text="/help")],
        [KeyboardButton(text="/apps")]
    ],
    resize_keyboard=True
)
