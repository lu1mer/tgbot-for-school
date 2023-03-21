from aiogram import Bot,types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,BotCommand, BotCommandScopeDefault
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from parse_excel import excel_to_json
import json

import datetime
import sqlite3
storage = MemoryStorage()
admin_id = 612579531
token = '5579241270:AAEXkjIVCrDcSLLKjfR6SFH8C72JYgOPzz4'
bot = Bot(token=token)
dp = Dispatcher(bot,storage=storage)
PERSON='00'

db = sqlite3.connect('id.db')
cursor = db.cursor()
db.commit()

btn_zam = KeyboardButton('Замены')
btn_notice = KeyboardButton('Включить уведомления')
zamen = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_zam,btn_notice)


btn_today = KeyboardButton('На сегодня')
btn_tomorrow = KeyboardButton('На завтра')
den = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_today,btn_tomorrow)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Начало работы'
        ),

    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())



class Test(StatesGroup):
    test1 = State()

class Client(StatesGroup):
    client = State()
class Clas(StatesGroup):
    clas = State()

@dp.message_handler(commands=['start','help'],state=None)
async def command_start(message: types.Message):
    await set_commands(bot)
    global zamen
    if message.from_user.id != admin_id:
        if len(cursor.execute("SELECT id FROM ids WHERE notice='T'").fetchall()) != 0 and str(message.from_user.id) in \
                cursor.execute("SELECT id FROM ids WHERE notice='T'").fetchall()[0]:
            zamen = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_zam)
        else:
            zamen = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_zam, btn_notice)
        await Clas.clas.set()
        await bot.send_message(message.from_user.id, '''Приветствую, этот бот создан для просматривания замен в 9 Лицее.\nУкажите ваш класс в формате цБ (пример - 3Л)'''
                                                 )
    else:
        zamen = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_zam)
        await bot.send_message(message.from_user.id,'Что вы хотите добавить/изменить',reply_markup=zamen)
        await main_dialog(message)
@dp.message_handler(state=Clas.clas)
async def clas1(message: types.Message,state: FSMContext):
    global PERSON
    PERSON = message.text
    if str(message.from_user.id) in [i[0] for i in cursor.execute("SELECT id FROM ids").fetchall()]:
        cursor.execute('''UPDATE ids SET class = ? WHERE id = ?''', (PERSON, str(message.from_user.id)))
        db.commit()
        print('312')
    else:
        cursor.execute(f"INSERT INTO ids VALUES ('{message.from_user.id}','{PERSON}','F')")
        db.commit()
    print(cursor.execute("SELECT id,class FROM ids").fetchall())
    await bot.send_message(message.from_user.id,'Приняли',reply_markup=zamen)
    await main_dialog(message)
    await state.finish()


@dp.message_handler()
async def main_dialog(message: types.Message):
    global cursor,zamen,PERSON,db
    if message.text == 'Замены':
        if message.from_user.id == admin_id:
            await admin_service(message)
        else:
            await client(message)
    if message.text == 'Включить уведомления':
        cursor.execute('''UPDATE ids SET notice = ? WHERE id = ?''', ('T', str(message.from_user.id)))
        db.commit()
        zamen = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_zam)
        await bot.send_message(message.from_user.id,'Уведомления включены',reply_markup=zamen)

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
        print(datetime.datetime.now())
        datezamen = (datetime.date.today() + datetime.timedelta(days=d)).strftime('%d.%m.%y')
    else:
        datezamen = message.text
    with open('zam.json', encoding='utf-8') as f:
        zam_d = json.load(f)
    print(cursor.execute(f"SELECT class FROM ids WHERE id='{message.from_user.id}'").fetchone()[0])
    try:
        s = zam_d[datezamen]
        for i in s:
            if i[0] == cursor.execute(f"SELECT class FROM ids WHERE id='{message.from_user.id}'").fetchone()[0]:
                print(message.from_user.id,cursor.execute(f"SELECT class FROM ids WHERE id='{message.from_user.id}'").fetchone()[0],i[0])
                await bot.send_message(message.from_user.id,f'{i[0]} - {i[1]} урок - {i[2]}',reply_markup=zamen)

    except:
        await bot.send_message(message.from_user.id,'На такую дату нет замен',reply_markup=zamen)
        await state.finish()
    await state.finish()


@dp.message_handler(state=None)
async def admin_service(message: types.Message):
    await Test.test1.set()
    await bot.send_message(admin_id, 'Пришлите файл с заменами')

@dp.message_handler(state=Test.test1,content_types=[types.ContentType.DOCUMENT])
async def state1(message: types.Message, state: FSMContext):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "zam.xlsx")
    await state.finish()
    datezamen = excel_to_json('zam.xlsx')
    for row in cursor.execute("SELECT id,class,notice FROM ids").fetchall():
        print(row)
        if row[2] == 'T':
            t=False
            with open('zam.json', encoding='utf-8') as f:
                zam_d = json.load(f)
            try:
                s = zam_d[datezamen]
                if row[1] != '00':
                    for i in s:
                        if i[0] == row[1]:
                            if t == False:
                                await bot.send_message(int(row[0]), f'Замены на {datezamen}')
                                t=True
                            await bot.send_message(int(row[0]), f'{row[1]} - {i[1]} урок - {i[2]}', reply_markup=zamen)
                else:
                    for i in s:
                        await bot.send_message(int(row[0]), f'{i[0]} - {i[1]} урок - {i[2]}', reply_markup=zamen)

            except:
                print('43')


    await bot.send_message(message.from_user.id,'Замены перемещены в базу данных')
#except:
#     await bot.send_message(message.from_user.id, 'Неправильный файл')
#     await main_dialog(message)

executor.start_polling(dp, skip_updates=True)
db.close()