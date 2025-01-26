import logging
import time

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.markdown import text as md_text
import keyboards
from sqlite import db_start, send_customer, send_deliver, remove_deliver, remove_customer, send_orders, add_orders, \
    add_customer, add_deliver, get_cus, get_del_id, get_cus_id, select, upd_orders

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7659984232:AAHIns96tmUjShalBUfZTIgAt_4XZM3ZZiA'


async def on_startup():
    await db_start()


storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)

global order_id


# States


class Form(StatesGroup):
    role = State()
    car_apps = State()

    """for deliver"""
    car_mark = State()
    remoteness = State()
    adr = State()
    geo = State()
    car_app = State()
    latitude = State()
    longitude = State()
    agree = State()
    geo_agree = State()
    search = State()
    end = State()

    """for customer"""
    adr_to = State()
    timing = State()
    radius = State()
    cus_agree = State()

    """for admin"""
    auth = State()
    ex = State()
    acc = State()
    back = State()
    remove = State()
    customer_id = State()
    deliver_id = State()
    status = State()
    order = State()


@dp.message(Command('admin'))
async def auth_admin(message: types.Message):
    await Form.auth.set()
    await bot.send_message(message.chat.id, "Введите пароль")


@dp.message(F.state == Form.auth)
async def auth_admin(message: types.Message, state: FSMContext):
    if message.text == "1":
        async with state.proxy() as data:
            await Form.acc.set()
            data['auth'] = True
            await bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboards.markup_admin)
    else:
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Выход")
        markup1.add(item1)
        await state.finish()
        await message.reply("Пароль не верный")
        await bot.send_message(message.chat.id, "Для начала работы с ботом введите /start",
                               reply_markup=keyboards.start)


@dp.message(F.state == Form.acc)
async def auth_admin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['acc'] = message.text
    if message.text == "Доставщики":
        await bot.send_message(message.chat.id, f"Доставщики: ", reply_markup=keyboards.markup_admin_remove)
        await bot.send_message(message.chat.id, await send_deliver())
        await Form.back.set()

    elif message.text == "Заказчики":
        await bot.send_message(message.chat.id, f"Заказчики: ", reply_markup=keyboards.markup_admin_remove)
        await bot.send_message(message.chat.id, await send_customer())
        await Form.back.set()

    elif message.text == "Заказы":
        await bot.send_message(message.chat.id, f"Выберите действие", reply_markup=keyboards.markup_admin_order)
        """await bot.send_message(message.chat.id, await send_orders())"""
        await Form.order.set()

    elif message.text == "Выход":
        await state.finish()
        await message.reply("Возвращайтесь", reply_markup=keyboards.markup_admin)

    else:
        await bot.send_message(message.chat.id, "блин", reply_markup=keyboards.markup_admin)


@dp.message(F.state == Form.back)
async def back_admin(message: types.Message):
    if message.text == "Удалить запись":
        await bot.send_message(message.chat.id, f"Для того, что бы удалить запись укажите user_id: ")
        await Form.remove.set()

    elif message.text == "Назад":
        await bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboards.markup_admin)
        await Form.acc.set()
    else:
        await bot.send_message(message.chat.id, "блин", reply_markup=keyboards.markup_admin)


@dp.message(F.state == Form.order)
async def order_admin(message: types.Message):
    if message.text == "Посмотреть заказы":
        await bot.send_message(message.chat.id, f"Заказы: ")
        await bot.send_message(message.chat.id, await send_orders())

    elif message.text == "Создать заказ":
        await bot.send_message(message.chat.id, "Что бы создать заказ введите id заказчика",
                               reply_markup=keyboards.markup_admin)
        await Form.customer_id.set()

    elif message.text == "Удалить заказ":
        await bot.send_message(message.chat.id, f"Для того, что бы удалить запись укажите user_id: ")
        await Form.acc.set()

    elif message.text == "Назад":
        await bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboards.markup_admin)
        await Form.acc.set()

    else:
        await bot.send_message(message.chat.id, "блин", reply_markup=keyboards.markup_admin)


@dp.message(F.state == Form.customer_id)
async def create_order_customer_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['customer_id'] = message.text

        data['status'] = "создан"
    await bot.send_message(message.chat.id, "введите id доставщика")
    await Form.deliver_id.set()
    await bot.send_message(message.chat.id, str(await get_cus(message.text)))

    if message.text == "Назад":
        await bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboards.markup_admin)
        await Form.acc.set()


@dp.message(F.state == Form.deliver_id)
async def create_order(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboards.markup_admin)
        await Form.acc.set()
    else:
        async with state.proxy() as data:
            data['deliver_id'] = message.text
        await bot.send_message(message.chat.id, "заказ создан", reply_markup=keyboards.markup_admin)
        await add_orders(state, user_id=message.date)
        await Form.acc.set()


@dp.message(F.state == Form.remove)
async def back_admin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Назад":
            await bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboards.markup_admin)
            await Form.acc.set()
        else:
            await bot.send_message(message.chat.id, f"Запись с user_id {message.text} удалена",
                                   reply_markup=keyboards.markup_admin)
            print(message.text)
            if data['acc'] == "Заказы":
                await remove_customer(message.text)
            elif data['acc'] == "Доставщики":
                await remove_deliver(message.text)

            await Form.acc.set()


@dp.callback_query()
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    code = callback_query.data[-1]
    print(f"callback code={code}")
    await bot.send_message(callback_query.from_user.id, f'Нажата инлайн кнопка! code={code}')


@dp.message(Command("geo"))
async def geo(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    await bot.send_message(message.chat.id, "Привет! Нажми на кнопку и передай мне свое местоположение",
                           reply_markup=keyboard)


@dp.message(F.content_type.in_({"location"}))
async def location(message):
    if message.location is not None:
        await bot.send_location(message.chat.id, message.location.latitude, message.location.longitude)
        cus_id = await get_cus_id(message.chat.id)
        await bot.send_location(cus_id, message.location.latitude, message.location.longitude)


@dp.message(Command("apps"))
async def apps(message):
    await bot.send_message(message.chat.id, "Напишите приложения для аренды машины каршеринга, "
                                            "к которым вы имеете доступ.")

    await Form.car_apps.set()


@dp.message(F.state == Form.car_apps)
async def add_car_apps(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['car_apps'] = message.text
        await bot.send_message(message.chat.id, "Супер, для начала работы с ботом введите /start",
                               reply_markup=keyboards.start)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await bot.send_message(message.chat.id, "Эта инструкция поможет разобраться с использованием данного бота,\n"
                                            "для начала работы с ботом введите /start, \n"
                                            "далее на выбор будут предложены две роли: Заказчик и Доставщик \n"
                                            "(Только не пугайтесь, поработать курьером для доставки машины прийдется "
                                            "только во время вашей поездки, на работу мы Вас не пытаемся устроить).\n"
                                            "Перед началом работы пропишите команду /apps, что бы мы знали какие"
                                            " машины каршеринга вам можно доставлять. \n"
                                            "Что бы получить доступ к админ-панели введите команду /admin , "
                                            "но учтите, что нужен пароль!\n"
                                            "На этом все, удачного пользования!",
                           reply_markup=keyboards.start)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await bot.send_message(message.chat.id, "В разработке", reply_markup=keyboards.start)


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.role)

    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_name = message.from_user.first_name
    logging.info(f'{user_id=} {user_full_name=} {time.asctime()}')

    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Заказать"), KeyboardButton(text="Доставить")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        f"Привет, {user_name}! Этот бот разработан в рамках дисциплины Создание Технологического Бизнеса",
        reply_markup=markup
    )


@dp.message(Form.role, F.text.in_({"Заказать", "Доставить", "Выход"}))
async def process_role(message: types.Message, state: FSMContext):
    if message.text == "Доставить":
        await state.update_data(role="deliver")
        await state.set_state(Form.car_app)

        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Яндекс Драйв"), KeyboardButton(text="Делимобиль")],
                [KeyboardButton(text="Ситидрайв"), KeyboardButton(text="BelkaCar")]
            ],
            resize_keyboard=True
        )

        await message.answer("Какое приложение для каршеринга вы используете?", reply_markup=markup)

    elif message.text == "Заказать":
        await state.update_data(role="customer")
        await state.set_state(Form.adr_to)
        
        markup = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Выход")]],
            resize_keyboard=True
        )
        
        await message.answer("Укажите адрес", reply_markup=markup)

    elif message.text == "Выход":
        await state.clear()
        await message.reply("Возвращайтесь", reply_markup=keyboards.start)


@dp.message(Form.car_app)
async def process_car_app(message: types.Message, state: FSMContext):
    if message.text == "Выход":
        await state.clear()
        await message.reply("Возвращайтесь", reply_markup=keyboards.start)
    else:
        await state.update_data(car_app=message.text)
        await state.set_state(Form.car_mark)
        markup = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Выход")]],
            resize_keyboard=True
        )
        await message.answer("Укажите модель и номер машины?", reply_markup=markup)


@dp.message(Form.adr_to)
async def process_adr_to(message: types.Message, state: FSMContext):
    if message.text == "Выход":
        await state.clear()
        await message.reply("Возвращайтесь", reply_markup=keyboards.start)
    else:
        await state.update_data(adr_to=message.text)
        await state.set_state(Form.timing)
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="В течение 15 минут")],
                [KeyboardButton(text="В течение 30 минут")],
                [KeyboardButton(text="В течение часа")],
                [KeyboardButton(text="Выход")]
            ],
            resize_keyboard=True
        )
        await message.answer("Время доставки?", reply_markup=markup)


@dp.message(Form.car_mark)
async def process_car(message: types.Message, state: FSMContext):
    if message.text == "Выход":
        await state.clear()
        await message.reply("Возвращайтесь", reply_markup=keyboards.start)
    else:
        await state.update_data(car_mark=message.text)
        await state.set_state(Form.remoteness)
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Заказы рядом"), KeyboardButton(text="Заказы по адресу")]
            ],
            resize_keyboard=True
        )
        await message.answer(f"Машина {message.text}", reply_markup=markup)


@dp.message(Form.timing)
async def process_timing(message: types.Message, state: FSMContext):
    if message.text == "Выход":
        await state.clear()
        await message.reply("Возвращайтесь", reply_markup=keyboards.start)
    else:
        await state.update_data(timing=message.text)
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="3 км- 49₽")],
                [KeyboardButton(text="2 км- 99₽")],
                [KeyboardButton(text="1 км- 149₽")],
                [KeyboardButton(text="Точно по адресу- 249₽")]
            ],
            resize_keyboard=True
        )
        await message.answer("В каком радиусе доставить?", reply_markup=markup)
        await state.set_state(Form.radius)


@dp.message(Form.remoteness)
async def process_remoteness(message: types.Message, state: FSMContext):
    if message.text == "Заказы рядом":
        await state.update_data(remoteness="nearby")
        await state.set_state(Form.adr)
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Отправить местоположение", request_location=True)]
            ],
            resize_keyboard=True
        )
        await message.answer("Отправьте геопозицию или укажите адрес", reply_markup=markup)
    elif message.text == "Заказы по адресу":
        await state.update_data(remoteness="at")
        await state.set_state(Form.adr)
        await message.answer("Укажите адрес")
    elif message.text == "Выход":
        await state.clear()
        await message.reply("Возвращайтесь", reply_markup=keyboards.start)


@dp.message(Form.radius)
async def process_radius(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(radius=message.text)
    
    await message.answer(
        md_text(
            md_text('role: ', data['role']),
            md_text('adr_to:', data['adr_to']),
            md_text('timing:', data['timing']),
            md_text('radius:', message.text),
            sep='\n',
        ),
        reply_markup=keyboards.start,
    )
    
    await add_customer(state, customer_id=message.date, user_id=message.from_user.id)
    await message.answer("Идет поиск...")
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="3 км- 49₽")],
            [KeyboardButton(text="2 км- 99₽")],
            [KeyboardButton(text="1 км- 149₽")],
            [KeyboardButton(text="Точно по адресу- 249₽")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Если поиск идет слишком долго- выберите радиус доставки заново",
        reply_markup=markup
    )
    
    del_id = None
    while del_id is None:
        del_id = await get_del_id(message.chat.id)
    
    markup_request = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/Выполнен"), KeyboardButton(text="/Сорван")]],
        resize_keyboard=True
    )
    await message.answer(
        f'Ваш заказ принят: \n'
        f'Приложение каршеринга: {await select("car_app", "deliver", "user_id", del_id)}\n'
        f'Машина {await select("car_mark", "deliver", "user_id", del_id)}',
        reply_markup=markup_request
    )
    await state.clear()


@dp.message(Form.adr)
async def process_adr(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    if message.location is not None:
        await state.update_data(adr=f"{message.location.latitude}, {message.location.longitude}")
    else:
        await state.update_data(adr=message.text)
    
    await state.update_data(latitude="0", longitude="0")
    
    await message.answer(
        md_text(
            md_text('role: ', data['role']),
            md_text('car app:', data['car_app']),
            md_text('car mark:', data['car_mark']),
            md_text('adr:', message.text if message.location is None else f"{message.location.latitude}, {message.location.longitude}"),
            sep='\n',
        ),
        reply_markup=keyboards.start,
    )
    
    await add_deliver(state, deliver_id=message.date, user_id=message.from_user.id)
    await message.answer("Идет поиск...")
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отправить местоположение", request_location=True)]],
        resize_keyboard=True
    )
    await message.answer(
        "Если поиск идет слишком долго- отправьте геолокацию или адрес заново",
        reply_markup=markup
    )
    
    cus_id = None
    while cus_id is None:
        cus_id = await get_cus_id(message.chat.id)
    
    markup_request = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Принять заявку"), KeyboardButton(text="Отклонить заявку")]],
        resize_keyboard=True
    )
    await message.answer(
        f'В данном районе есть заказ: \n'
        f'{await select("radius", "customer", "user_id", cus_id)}\n'
        f'{await select("adr_to", "customer", "user_id", cus_id)}',
        reply_markup=markup_request
    )
    await state.set_state(Form.agree)


@dp.message(Form.agree)
async def process_radius(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        if message.text == "Принять заявку":
            data['agree'] = "yes"
            await Form.geo_agree.set()
            markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton('Поделиться геопозицией🗺️', request_location=True), KeyboardButton('Не делиться'))
            await bot.send_message(message.chat.id, "Делиться геопозицией?", reply_markup=markup_request)
        elif message.text == "Отклонить заявку":
            data['agree'] = "no"
            await bot.send_message(message.chat.id, "Очень жаль, отправте заявку на доставку снова",
                                   reply_markup=keyboards.start)
            await state.finish()


@dp.message(Form.geo_agree)
async def process_radius(message: types.Message, state: FSMContext):
    markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/Подъезжаю'))
    async with state.proxy() as data:
        if message.location is not None:
            data['geo_agree'] = message.location
            await bot.send_message(message.chat.id, "Супер")
            await state.finish()
        else:
            data['geo_agree'] = "no"
            await bot.send_message(message.chat.id, "Очень жаль")
            await state.finish()
    await bot.send_message(message.chat.id, "Отправте /Подъезжаю когда вам останется 5 минут до конца поездки",
                           reply_markup=markup_request)


@dp.message(Command("Подъезжаю"))
async def process_radius(message: types.Message, state: FSMContext):
    await bot.send_message(await get_cus_id(message.chat.id), "Водитель подъезжает, включите автобронирование")
    markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('/Выполнен'), KeyboardButton('/Сорван'))
    await bot.send_message(message.chat.id, "Супер", reply_markup=markup_request)
    await state.finish()


@dp.message(Command("Выполнен"))
async def process_radius(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data['role'] == "deliver":
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
            keyboard.add(button_geo)
            await bot.send_message(message.chat.id, "Чудесно, отправте свою геолокацию",
                                   reply_markup=keyboard)
        elif data['role'] == "customer":
            await bot.send_message(message.chat.id, "Супер", reply_markup=keyboards.start)
            await bot.send_message(400156846, f"Выволнение заказа подтверждено заказчиком {message.chat.id}",
                                   reply_markup=keyboards.start)
            await upd_orders("выполнен", "customer_id", message.chat.id)


@dp.message(Command("Сорван"))
async def process_radius(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, "Жаль...(", reply_markup=keyboards.start)
    async with state.proxy() as data:
        if data['role'] == "deliver":
            await upd_orders("сорван", "deliver_id", message.chat.id)
        elif data['role'] == "customer":
            await upd_orders("сорван", "customer_id", message.chat.id)


async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register all handlers
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(process_role, Form.role, F.text.in_({"Заказать", "Доставить", "Выход"}))
    dp.message.register(process_car_app, Form.car_app)
    dp.message.register(process_adr_to, Form.adr_to)
    dp.message.register(process_car, Form.car_mark)
    dp.message.register(process_timing, Form.timing)
    dp.message.register(process_remoteness, Form.remoteness)
    dp.message.register(process_radius, Form.radius)
    dp.message.register(process_adr, Form.adr)
    
    # Register other handlers...
    dp.message.register(auth_admin, Command('admin'))
    dp.message.register(auth_admin, F.state == Form.auth)
    dp.message.register(auth_admin, F.state == Form.acc)
    dp.message.register(back_admin, F.state == Form.back)
    dp.message.register(order_admin, F.state == Form.order)
    dp.message.register(create_order_customer_id, F.state == Form.customer_id)
    dp.message.register(create_order, F.state == Form.deliver_id)
    dp.message.register(back_admin, F.state == Form.remove)
    dp.message.register(geo, Command("geo"))
    dp.message.register(location, F.content_type.in_({"location"}))
    dp.message.register(apps, Command("apps"))
    dp.message.register(add_car_apps, F.state == Form.car_apps)
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(process_radius, F.state == Form.agree)
    dp.message.register(process_radius, F.state == Form.geo_agree)
    dp.message.register(process_radius, Command("Подъезжаю"))
    dp.message.register(process_radius, Command("Выполнен"))
    dp.message.register(process_radius, Command("Сорван"))
    
    # Register callback query handler separately
    dp.callback_query.register(process_callback_kb1btn1)
    
    # Register startup handler
    dp.startup.register(on_startup)
    
    # Start polling
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
