import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

BOT_TOKEN = "8842619890:AAGCoBI_arrd1yX4HpFDvGe_iS3JUz4oGM4"
ADMIN_ID = 7677636892  
ADMIN_USERNAME = "qodirov_7o7"  

CHANNEL_ID = "-100123456789"  
CHANNEL_LINK = "https://t.me/kanal_nomi"  

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A'zo bo'lish", url="https://t.me/o_zingizning_kanalingiz")]
    ])


conn = sqlite3.connect("kinobot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS movies (code TEXT PRIMARY KEY, name TEXT, link TEXT)")
conn.commit()

async def check_sub(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except Exception:
        return False

def get_sub_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_query_data="check_subscription")]
    ])

def get_user_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍💻 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}")]
    ])

@dp.message(CommandStart())
async def start_cmd(message: Message):
    user_id = message.from_user.id
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
    except Exception:
        pass

    if await check_sub(user_id):
        await message.answer(f"Salom {message.from_user.full_name}!\nKino kodini kiriting:", reply_markup=get_user_keyboard())
    else:
        await message.answer("⚠️ Botdan foydalanish uchun kanalimizga obuna bo'ling:", reply_markup=get_sub_keyboard())

@dp.callback_query(F.data == "check_subscription")
async def check_sub_callback(call: CallbackQuery):
    if await check_sub(call.from_user.id):
        await call.message.delete()
        await call.message.answer("🎉 Obuna tasdiqlandi! Kino kodini kiriting:", reply_markup=get_user_keyboard())
    else:
        await call.answer("❌ Siz hali kanalga obuna bo'lmagansiz!", show_alert=True)

@dp.message(Command("panel"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = "🛠 Admin Panel\n\n➕ Qo'shish: /add kod | Nom | Link\n➖ O'chirish: /del kod_yoki_nomi\n📊 Statistika: /stat\n📢 Xabar: /send xabar_matni"
    await message.answer(text)

@dp.message(Command("add"))
async def add_movie(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        args = message.text.split("/add ")[1].split("|")
        code = args[0].strip()
        name = args[1].strip()
        link = args[2].strip()
        cursor.execute("INSERT OR REPLACE INTO movies (code, name, link) VALUES (?, ?, ?)", (code, name, link))
        conn.commit()
        await message.answer(f"✅ Qo'shildi:\nKod: {code}\nNomi: {name}")
    except Exception:
        await message.answer("❌ Format xato! /add kod | Nom | Link")

@dp.message(Command("del"))
async def del_movie(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    search_val = message.text.replace("/del ", "").strip()
    cursor.execute("DELETE FROM movies WHERE code = ? OR name = ?", (search_val, search_val))
    conn.commit()
    await message.answer(f"🗑 O'chirildi: {search_val}")

@dp.message(Command("stat"))
async def get_stat(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    cursor.execute("SELECT COUNT(*) FROM users")
    u_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM movies")
    m_count = cursor.fetchone()[0]
    await message.answer(f"📊 Statistika:\n\n👤 Foydalanuvchilar: {u_count}\n🎬 Kinolar: {m_count}")

@dp.message(Command("send"))
async def send_reklama(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    text_to_send = message.text.replace("/send ", "").strip()
    if not text_to_send:
        await message.answer("Matn yozing.")
        return
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    await message.answer("📢 Yuborilmoqda...")
    count = 0
    for user in users:
        try:
            await bot.send_message(chat_id=user[0], text=text_to_send)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            continue
    await message.answer(f"✅ {count} ta odamga yetib bordi.")

@dp.message(F.text)
async def search_movie(message: Message):
    user_id = message.from_user.id
    if not await check_sub(user_id):
        await message.answer("⚠️ Kanalga obuna bo'ling:", reply_markup=get_sub_keyboard())
        return
    kod = message.text.strip()
    cursor.execute("SELECT name, link FROM movies WHERE code = ?", (kod,))
    res = cursor.fetchone()
    if res:
        await message.answer(f"🎬 Nomi: {res[0]}\n\n🍿 Link: {res[1]}", reply_markup=get_user_keyboard())
    else:
        await message.answer("❌ Kino topilmadi.", reply_markup=get_user_keyboard())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
