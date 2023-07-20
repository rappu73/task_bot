import asyncio
import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup

storage = MemoryStorage()
bot = Bot(TOKEN)  # указываем Token для бота
dp = Dispatcher(bot, storage=storage)

admin = id  # указываем ID для руководителя

# указываем Имена и ID для сотрудников
list = {'User1': id,
        'User2': id,
        'User3': id,
        'User4': id
        }

# Помощь для админа
help_admin = '''
1) вызовите команду /task
2) напиши новую задачу для сотрудкика
3) укажите время на выполнение задачи
4) выберите нужного сотрудника из меню бота'''

# Помощь для сотрудника
help_user = '''
1) Ждите когда вам придёт задание
2) Выполните задание
3) Отчитайте о результате выполнения'''


class UserState(StatesGroup):
    work = State()
    times = State()
    rab = State()

# Старт бота
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.from_user.id == admin:
        await bot.send_message(admin, help_admin)
    else:
        await message.answer(help_user)

# Для админа вызаваем команду дать задание
@dp.message_handler(commands=['task'])
async def task(message: types.Message):
    await bot.send_message(admin, 'Напиши задание')
    await UserState.work.set()

# Для админа вызаваем команду указать время на задание
@dp.message_handler(state=UserState.work)
async def time(message: types.Message, state: FSMContext):
    await state.update_data(work=message.text)
    await bot.send_message(admin, 'Задай время на выполнение')
    await UserState.times.set()

# Для админа вызаваем команду указать сотрудника для задания
@dp.message_handler(state=UserState.times)
async def answer_time(message: types.Message, state: FSMContext):
    await state.update_data(times=message.text)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('User1')   # указываем Имя для сотрудника
    btn2 = types.KeyboardButton('User2')   # указываем Имя для сотрудника
    btn3 = types.KeyboardButton('User3')   # указываем Имя для сотрудника
    btn4 = types.KeyboardButton('User4')   # указываем Имя для сотрудника
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    await bot.send_message(admin, 'Выбери сотрудника из меню', reply_markup=markup)
    await UserState.rab.set()

# Отпраляем выбранному сотруднику задание с 2-мя кнопками: "Выполнено"/"Не выполнено"
@dp.message_handler(state=UserState.rab)
async def info(message: types.Message, state: FSMContext):
    await state.update_data(rab=message.text)
    data = await state.get_data()
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text='Выполнено', callback_data='yes'))
    markup.add(types.InlineKeyboardButton(text='Не выполнено', callback_data='no'))
    await bot.send_message(admin, f"Вы отправили задание {data['work']} сотруднику: {data['rab']}")
    await bot.send_message(list[(message['text'])], f"{data['rab']}, Выполни задание: {data['work']}. Время на выполнение: {data['times']}", reply_markup=markup)

    await state.finish()
    await bot.send_message(admin, help_admin)

###### Пока не могу решить как правильно присылать админу сообщение, если сотрудник не выполнил задание за заданное время  ######

    # async def eternity():
    #     time.sleep(10)
    #
    # try:
    #     await asyncio.wait_for(eternity(), timeout=10)
    #
    # except asyncio.TimeoutError:
    #     await message.answer(f"{data['rab']} проигнорировал задание")

# Обрабатываем результат нажатия кнопки сотрудником
@dp.callback_query_handler()
async def callback(call):
    if call.data == 'yes':
        for name in list:
            if list[name] == call.message['chat']['id']:
                await call.bot.send_message(admin, f'{name} выполнил задание')
                await call.message.answer('Спасибо за выполненное задание')
                await call.message.answer('/start')

    if call.data == 'no':
        for name in list:
            if list[name] == call.message['chat']['id']:
                await call.bot.send_message(admin, f'{name} не выполнил задание')
                await call.message.answer('Вы не выполнили задание')
                await call.message.answer('/start')

# Обрабатываем любой текст
@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    await message.answer('Неизвестная команда')
    if message.from_user.id == admin:
        await bot.send_message(admin, help_admin)
    else:
        await message.answer(help_user)


executor.start_polling(dp)
