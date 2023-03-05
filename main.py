from aiogram import Bot,types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import openpyxl
import json
import os
import datetime
storage = MemoryStorage()
admin_id = 612579531
admin_id = 6125795311
token = '5579241270:AAEXkjIVCrDcSLLKjfR6SFH8C72JYgOPzz4'
bot = Bot(token=token)
dp = Dispatcher(bot,storage=storage)
PERSON='00'

btn_zam = KeyboardButton('Замены')
zamen = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_zam)

btn_today = KeyboardButton('На сегодня')
btn_tomorrow = KeyboardButton('На завтра')
den = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_today,btn_tomorrow)
def excel(name):
    with open('zam.json',encoding='utf-8') as f:
        zamen_dict = json.load(f)
    book = openpyxl.open(name,read_only=True)
    sheet = book.active
    date = sheet[2][0].value
    date = date.strftime('%d.%m.%y')
    zamen_dict[date] = []
    for row in sheet:
        if row[1].value != 'Класс':
            zamen_dict[date].append([row[1].value,row[2].value,row[3].value])
    print(zamen_dict)
    with open('zam.json', 'w',encoding='utf-8') as outfile:
        json.dump(zamen_dict, outfile,ensure_ascii=False)




class Test(StatesGroup):
    test1 = State()

class Client(StatesGroup):
    client = State()
class Clas(StatesGroup):
    clas = State()

@dp.message_handler(commands=['start','help'],state=None)
async def command_start(message: types.Message):
    if message.from_user.id != admin_id:
        await Clas.clas.set()
        await bot.send_message(message.from_user.id, '''Приветствую, этот бот создан для просматривания замен в 9 Лицее.\nУкажите ваш класс'''
                                                 )
    else:
        await bot.send_message(message.from_user.id,'Что вы хотите добавить/изменить',reply_markup=zamen)
        await main_dialog(message)
@dp.message_handler(state=Clas.clas)
async def clas1(message: types.Message,state: FSMContext):
    global PERSON
    PERSON = message.text
    await bot.send_message(message.from_user.id,'Приняли',reply_markup=zamen)
    await main_dialog(message)
    await state.finish()


@dp.message_handler()
async def main_dialog(message: types.Message):
    if message.text == 'Замены':
        if message.from_user.id == admin_id:
            await admin_service(message)
        else:
            await client(message)

@dp.message_handler(state=None)
async def client(message: types.Message):
    await Client.client.set()
    await bot.send_message(message.from_user.id, 'На какой дату вы хотите посмотреть замены? (формат - дд.мм.гг) или воспользуйтесь кнопками',reply_markup=den)

@dp.message_handler(state=Client.client)
async def state1(message: types.Message, state: FSMContext):
    if message.text == 'На сегодня' or message.text == 'На завтра':
        if message.text == 'На сегодня':
            d = 0
        else:
            d=1
        datezamen = (datetime.date.today() + datetime.timedelta(days=d)).strftime('%d.%m.%y')
    else:
        datezamen = message.text
    with open('zam.json', encoding='utf-8') as f:
        zam_d = json.load(f)
    try:
        s = zam_d[datezamen]
        if PERSON != '00':
            for i in s:
                if i[0] == PERSON:
                    await bot.send_message(message.from_user.id,f'{PERSON} - {i[1]} урок - {i[2]}',reply_markup=zamen)
        else:
            for i in s:
                await bot.send_message(message.from_user.id, f'{i[0]} - {i[1]} урок - {i[2]}',reply_markup=zamen)

    except:
        await bot.send_message(message.from_user.id,'Вы неправильно ввели дату или на такую дату нет еще замен')
    await state.finish()

@dp.message_handler(state=None)
async def admin_service(message: types.Message):
    await Test.test1.set()
    await bot.send_message(admin_id, 'Пришлите файл с заменами')

@dp.message_handler(state=Test.test1,content_types=[types.ContentType.DOCUMENT])
async def state1(message: types.Message, state: FSMContext):
    print('123')
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "zam.xlsx")
    await state.finish()
    excel('zam.xlsx')
    await bot.send_message(admin_id,'Замены перемещены в базу данных')

executor.start_polling(dp, skip_updates=True)