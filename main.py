# telegram_store_bot/main.py
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import sqlite3
import os

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("store.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS cash_register (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER,
    date TEXT,
    start_amount REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT,
    name TEXT,
    memory TEXT,
    battery TEXT,
    condition TEXT,
    imei TEXT UNIQUE,
    purchase_price REAL,
    supplier TEXT,
    supplier_phone TEXT,
    added_by INTEGER,
    date_added TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imei TEXT,
    sold_by INTEGER,
    date_sold TEXT,
    sale_price REAL,
    customer_info TEXT,
    document_photo_id TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER,
    date TEXT,
    amount REAL,
    description TEXT
)
''')

conn.commit()

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("🧾 Внести начальную сумму"),
    KeyboardButton("📦 Приёмка товара"),
    KeyboardButton("💰 Продажа товара"),
    KeyboardButton("📉 Расходы"),
    KeyboardButton("📊 Касса")
)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Вы вошли как Продавец.", reply_markup=main_menu)

@dp.message_handler(lambda m: m.text == "🧾 Внести начальную сумму")
async def start_amount(message: types.Message):
    today = datetime.today().strftime('%Y-%m-%d')
    cursor.execute("SELECT * FROM cash_register WHERE seller_id=? AND date=?", (message.from_user.id, today))
    if cursor.fetchone():
        await message.answer("Сумма уже внесена на сегодня.")
    else:
        await message.answer("Введите сумму для начала дня:")
        dp.register_message_handler(get_start_amount, state=None)

async def get_start_amount(message: types.Message):
    try:
        amount = float(message.text)
        today = datetime.today().strftime('%Y-%m-%d')
        cursor.execute("INSERT INTO cash_register (seller_id, date, start_amount) VALUES (?, ?, ?)",
                       (message.from_user.id, today, amount))
        conn.commit()
        await message.answer("Сумма успешно внесена.", reply_markup=main_menu)
    except:
        await message.answer("Введите корректную сумму:")
        return

# Остальные обработчики будут добавлены в следующем шаге

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
