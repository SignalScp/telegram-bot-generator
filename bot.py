import asyncio
import logging
import subprocess
import tempfile
import os
from datetime import datetime
from openai import OpenAI
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from html import escape

# Настройки
MAIN_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замени на свой токен

# OnlySq API клиент
client = OpenAI(
    base_url="https://api.onlysq.ru/ai/openai",
    api_key="openai"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальные переменные
bot = Bot(token=MAIN_BOT_TOKEN)
dp = Dispatcher()
active_bots = {}  # {bot_id: {process, token, code, created_at}}
user_states = {}  # {user_id: {state, code}}

# === ФУНКЦИИ УПРАВЛЕНИЯ БОТАМИ ===

async def start_bot_process(bot_id: str, token: str, code: str):
    """Запускает бота в отдельном процессе"""
    try:
        # Создаем временный файл с кодом
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            # Добавляем токен в код
            full_code = code.replace('YOUR_BOT_TOKEN', token)
            f.write(full_code)
            temp_file = f.name
        
        # Запускаем процесс
        process = subprocess.Popen(
            ['python', temp_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем немного, чтобы проверить запуск
        await asyncio.sleep(2)
        
        if process.poll() is not None:
            # Процесс завершился - ошибка
            stdout, stderr = process.communicate()
            error_msg = stderr if stderr else stdout
            os.unlink(temp_file)
            return False, f"Ошибка запуска:\n{error_msg[:500]}"
        
        # Сохраняем информацию о боте
        active_bots[bot_id] = {
            'process': process,
            'temp_file': temp_file,
            'token': token,
            'code': code,
            'created_at': datetime.now()
        }
        
        return True, "Бот успешно запущен!"
        
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

async def stop_bot_process(bot_id: str):
    """Останавливает бота"""
    if bot_id not in active_bots:
        return False, "Бот не найден"
    
    try:
        bot_info = active_bots[bot_id]
        process = bot_info['process']
        
        # Убиваем процесс
        process.terminate()
        process.wait(timeout=5)
        
        # Удаляем временный файл
        try:
            os.unlink(bot_info['temp_file'])
        except:
            pass
        
        del active_bots[bot_id]
        return True, "Бот остановлен"
        
    except Exception as e:
        return False, f"Ошибка при остановке: {str(e)}"

# === КОМАНДЫ ===

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 <b>Привет!</b>\n\n"
        "🤖 Я помогу тебе создать Telegram бота с помощью AI!\n\n"
        "🚀 <b>Что я умею:</b>\n"
        "• Генерировать код бота по описанию\n"
        "• Запускать ботов для тестирования\n"
        "• Управлять несколькими ботами\n\n"
        "📚 <b>Команды:</b>\n"
        "/create - создать бота\n"
        "/list - список ботов\n"
        "/help - справка",
        parse_mode="HTML"
    )

@dp.message(F.text == "/create")
async def cmd_create(message: Message):
    user_id = message.from_user.id
    user_states[user_id] = {'state': 'waiting_description'}
    
    await message.answer(
        "📝 <b>Опиши, какой бот тебе нужен?</b>\n\n"
        "Примеры:\n"
        "• Бот, который отвечает на /start и /help\n"
        "• Бот-калькулятор, который считает примеры\n"
        "• Бот для сохранения заметок\n\n"
        "✍️ Опиши подробно, что должен делать бот:",
        parse_mode="HTML"
    )

@dp.message(F.text == "/list")
async def cmd_list(message: Message):
    if not active_bots:
        await message.answer("🚨 Нет активных ботов\n\nСоздай нового: /create")
        return
    
    text = "🤖 <b>Активные боты:</b>\n\n"
    
    for bot_id, bot in active_bots.items():
        status = "✅ Работает" if bot['process'].poll() is None else "❌ Остановлен"
        created = bot['created_at'].strftime("%H:%M:%S")
        text += f"🔹 ID: <code>{bot['id']}</code>\n{status}\n\n"
    
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text.startswith("/stop"))
async def cmd_stop(message: Message):
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "❌ Укажи ID бота\n\n"
            "Использование: /stop bot_123_0\n"
            "Посмотри список: /list"
        )
        return
    
    bot_id = parts[1].strip()
    success, msg = await stop_bot_process(bot_id)
    emoji = "✅" if success else "❌"
    await message.answer(f"{emoji} {msg}")

@dp.message(F.text.startswith("/edit"))
async def cmd_edit(message: Message):
    """Команда для правки кода бота"""
    parts = message.text.split(maxsplit=2)
    
    if len(parts) < 3:
        await message.answer(
            "❌ Укажи ID бота и описание правок\n\n"
            "Использование: /edit bot_123_0 добавь команду /hello\n"
            "Посмотри список: /list"
        )
        return
    
    bot_id = parts[1].strip()
    edit_request = parts[2].strip()
    
    if bot_id not in active_bots:
        await message.answer(f"❌ Бот {bot_id} не найден\nПосмотри список: /list")
        return
    
    # Останавливаем бота перед правкой
    await stop_bot_process(bot_id)
    
    status_msg = await message.answer("🔧 Вношу правки в код...")
    
    try:
        old_code = active_bots[bot_id]['code']
        
        # Используем AI для правки кода
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Ты опытный Python разработчик. Внеси правки в код Telegram бота на aiogram 3. Верни ТОЛЬКО исправленный код без объяснений."
                },
                {
                    "role": "user",
                    "content": f"Исходный код:\n{old_code}\n\nПравки: {edit_request}"
                }
            ],
            temperature=0.7
        )
        
        new_code = response.choices[0].message.content.strip()
        
        # Убираем markdown форматирование
        if new_code.startswith("```python"):
            new_code = new_code[9:]
        if new_code.startswith("```"):
            new_code = new_code[3:]
        if new_code.endswith("```"):
            new_code = new_code[:-3]
        new_code = new_code.strip()
        
        # Обновляем код
        active_bots[bot_id]['code'] = new_code
        
        # Перезапускаем бота
        token = active_bots[bot_id]['token']
        success, msg = await start_bot_process(bot_id, token, new_code)
        
        if success:
            await status_msg.edit_text(
                f"✅ Правки внесены и бот перезапущен!\n\n"
                f"🤖 ID: <code>{bot_id}</code>\n"
                f"📝 Изменения: {edit_request}\n\n"
                f"Скачать код: /download {bot_id}",
                parse_mode="HTML"
            )
        else:
            await status_msg.edit_text(
                f"❌ Правки внесены, но ошибка при запуске:\n{msg}\n\n"
                f"Скачай код и проверь: /download {bot_id}"
            )
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка при внесении правок:\n{str(e)}")

@dp.message(F.text.startswith("/download"))
async def cmd_download(message: Message):
    """Команда для скачивания кода бота"""
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "❌ Укажи ID бота\n\n"
            "Использование: /download bot_123_0\n"
            "Посмотри список: /list"
        )
        return
    
    bot_id = parts[1].strip()
    
    if bot_id not in active_bots:
        await message.answer(f"❌ Бот {bot_id} не найден\nПосмотри список: /list")
        return
    
    try:
        code = active_bots[bot_id]['code']
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_path = f.name
        
        # Отправляем файл
        file = FSInputFile(temp_path, filename=f"{bot_id}.py")
        await message.answer_document(file, caption=f"📦 Код бота <code>{bot_id}</code>", parse_mode="HTML")
        
        # Удаляем временный файл
        os.unlink(temp_path)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при скачивании:\n{str(e)}")

@dp.message(F.text.startswith("/requirements"))
async def cmd_requirements(message: Message):
    """Команда для скачивания requirements.txt"""
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "❌ Укажи ID бота\n\n"
            "Использование: /requirements bot_123_0\n"
            "Посмотри список: /list"
        )
        return
    
    bot_id = parts[1].strip()
    
    if bot_id not in active_bots:
        await message.answer(f"❌ Бот {bot_id} не найден\nПосмотри список: /list")
        return
    
    try:
        # Создаем requirements.txt
        requirements_content = """aiogram==3.15.0
aiohttp>=3.11.11
"""
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(requirements_content)
            temp_path = f.name
        
        # Отправляем файл
        file = FSInputFile(temp_path, filename="requirements.txt")
        await message.answer_document(
            file, 
            caption=f"📦 Requirements для бота <code>{bot_id}</code>\n\nУстанови: <code>pip install -r requirements.txt</code>",
            parse_mode="HTML"
        )
        
        # Удаляем временный файл
        os.unlink(temp_path)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании requirements:\n{str(e)}")

@dp.message(F.text == "/help")
async def cmd_help(message: Message):
    await message.answer(
        "📚 <b>Команды бота</b>\n\n"
        "/create - создать нового бота\n"
        "/list - список активных ботов\n"
        "/stop bot_id - остановить бота\n"
        "/edit bot_id описание - внести правки в бота\n"
        "/download bot_id - скачать код в .py\n"
        "/requirements bot_id - скачать requirements.txt\n"
        "/help - эта справка\n\n"
        "💡 <b>Как пользоваться:</b>\n"
        "1. Отправь /create\n"
        "2. Опиши, что должен делать бот\n"
        "3. Отправь токен от @BotFather\n"
        "4. Готово! Протестируй бота\n\n"
        "🔧 <b>Правки и скачивание:</b>\n"
        "• /edit bot_123_0 добавь команду /hello\n"
        "• /download bot_123_0 - получить .py файл\n"
        "• /requirements bot_123_0 - зависимости\n\n"
        "📝 Токен бота выглядит так:\n"
        "<code>1234567890:ABCdefGHIjklMNOpqrs</code>",
        parse_mode="HTML"
    )

@dp.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id
    
    # Проверяем, есть ли состояние пользователя
    if user_id not in user_states:
        await message.answer(
            "🤔 Давай начнем!\n\n"
            "Используй команды:\n"
            "/create - создать бота\n"
            "/help - справка"
        )
        return
    
    state = user_states[user_id]['state']
    
    # Этап 1: Получаем описание
    if state == 'waiting_description':
        description = message.text
        status_msg = await message.answer("⚙️ Генерирую код бота...")
        
        try:
            # Генерируем код через AI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты опытный Python разработчик. Создай Telegram бота на aiogram 3. "
                            "Верни ТОЛЬКО код, без объяснений. Используй YOUR_BOT_TOKEN как токен."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Создай бота: {description}"
                    }
                ],
                temperature=0.7
            )
            
            code = response.choices[0].message.content.strip()
            
            # Убираем markdown форматирование
            if code.startswith("```python"):
                code = code[9:]
            if code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
            code = code.strip()
            
            # Сохраняем код
            user_states[user_id]['code'] = code
            user_states[user_id]['state'] = 'waiting_token'
            
            await status_msg.edit_text(
                "✅ <b>Код готов!</b>\n\n"
                "🔑 Теперь отправь мне токен бота от @BotFather\n\n"
                "📝 Токен выглядит так:\n"
                "<code>1234567890:ABCdefGHIjklMNOpqrs</code>",
                parse_mode="HTML"
            )
            
        except Exception as e:
            await status_msg.edit_text(
                f"❌ Ошибка генерации:\n{str(e)}\n\n"
                "Попробуй снова: /create"
            )
            del user_states[user_id]
    
    # Этап 2: Получаем токен и запускаем
    elif state == 'waiting_token':
        token = message.text.strip()
        
        # Проверка формата токена
        if ':' not in token or len(token) < 20:
            await message.answer(
                "❌ Неверный формат токена\n\n"
                "Токен должен быть вида:\n"
                "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11\n\n"
                "Получи токен у @BotFather"
            )
            return
        
        code = user_states[user_id]['code']
        bot_id = f"bot_{user_id}_{len(active_bots)}"
        
        status_msg = await message.answer("🚀 Запускаю бота...")
        
        success, msg = await start_bot_process(bot_id, token, code)
        
        if success:
            await status_msg.edit_text(
                f"✅ <b>Бот запущен!</b>\n\n"
                f"🤖 ID: <code>{bot_id}</code>\n"
                f"📱 Найди его в Telegram и протестируй\n\n"
                f"Команды:\n"
                f"/list - список ботов\n"
                f"<code>/stop {bot_id}</code> - остановить",
                parse_mode="HTML"
            )
        else:
            # Используем parse_mode=None для текста с ошибками
            error_text = f"❌ Ошибка запуска бота\n\n{msg}\n\nПопробуй создать заново: /create"
            await status_msg.edit_text(error_text)
        
        # Очищаем состояние
        del user_states[user_id]

# === ЗАПУСК ===
async def main():
    logger.info("🚀 Бот-генератор запущен!")
    logger.info(f"🤖 Используется OpenAI SDK с OnlySq API")
    logger.info(f"🌐 Base URL: https://api.onlysq.ru/ai/openai")
    logger.info(f"🤖 Модель: gpt-4o-mini")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())