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
MAIN_BOT_TOKEN = "7963460845:AAFoa_MPJW_jKVAZ3wTs-wa7wYOqYy6FEIM"  # Замени на свой токен

# OnlySq API клиент
client = OpenAI(
    base_url="https://api.onlysq.ru/ai/openai",
    api_key="openai"
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=MAIN_BOT_TOKEN)
dp = Dispatcher()

# Хранилище состояний и активных ботов
user_states = {}
active_bots = {}

# === РАБОТА С AI ===
def generate_bot_code(prompt: str) -> tuple[str, str]:
    """Генерирует код бота через OnlySq API"""
    
    system_message = """Ты - эксперт по созданию Telegram ботов на Python с aiogram 3.x.
Создай ПОЛНЫЙ рабочий код бота.

ВАЖНО! Используй только aiogram 3.x синтаксис:
- from aiogram import Bot, Dispatcher, F
- from aiogram.types import Message
- from aiogram.filters import CommandStart
- НЕ используй aiogram.contrib (это старая версия 2.x!)
- НЕ используй MemoryStorage из contrib
- Токен бота берется из: os.environ.get('BOT_TOKEN')

Структура кода:
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
import os

bot = Bot(token=os.environ.get('BOT_TOKEN'))
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Я работаю!")

# Другие обработчики...

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

Требования:
- Код должен быть полностью рабочим
- Всё в одном файле
- Только aiogram 3.x синтаксис
- Верни ТОЛЬКО код Python без объяснений и markdown"""

    logger.info(f"🔄 Отправка запроса к OnlySq API")
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        
        code = completion.choices[0].message.content
        code = code.replace("```python", "").replace("```", "").strip()
        
        logger.info(f"✅ Код сгенерирован ({len(code)} символов)")
        return code, None
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Ошибка API: {error_msg}")
        return None, f"Ошибка API: {error_msg}"

def edit_bot_code(original_code: str, edit_prompt: str) -> tuple[str, str]:
    """Редактирует существующий код бота"""
    
    system_message = """Ты - эксперт по редактированию Telegram ботов на Python с aiogram 3.x.
Тебе дадут существующий код бота и описание изменений.
Внеси изменения в код согласно описанию.

ВАЖНО:
- Сохраняй aiogram 3.x синтаксис
- Токен бота должен быть: os.environ.get('BOT_TOKEN')
- Верни ТОЛЬКО исправленный код без объяснений и markdown"""

    user_message = f"""Исходный код:
```python
{original_code}
```

Изменения: {edit_prompt}

Верни полный исправленный код."""

    logger.info(f"🔄 Редактирование кода через AI")
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
        )
        
        code = completion.choices[0].message.content
        code = code.replace("```python", "").replace("```", "").strip()
        
        logger.info(f"✅ Код отредактирован ({len(code)} символов)")
        return code, None
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Ошибка API: {error_msg}")
        return None, f"Ошибка API: {error_msg}"

# === УПРАВЛЕНИЕ ПРОЦЕССАМИ ===
async def start_bot_process(bot_id: str, token: str, code: str) -> tuple[bool, str]:
    """Запускает бота в отдельном процессе"""
    try:
        temp_dir = tempfile.mkdtemp(prefix=f"bot_{bot_id}_")
        bot_file = os.path.join(temp_dir, "bot.py")
        
        with open(bot_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        env = os.environ.copy()
        env['BOT_TOKEN'] = token
        
        process = await asyncio.create_subprocess_exec(
            'python', bot_file,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=temp_dir
        )
        
        await asyncio.sleep(2)
        
        if process.returncode is not None:
            stderr = await process.stderr.read()
            error = stderr.decode('utf-8', errors='ignore')
            logger.error(f"❌ Бот {bot_id} упал при запуске: {error}")
            return False, f"Бот упал при запуске:\n{error[:500]}"
        
        active_bots[bot_id] = {
            'process': process,
            'token': token,
            'code': code,
            'temp_dir': temp_dir,
            'started_at': datetime.now()
        }
        
        logger.info(f"✅ Бот {bot_id} запущен (PID: {process.pid})")
        return True, f"Бот {bot_id} успешно запущен!"
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота {bot_id}: {e}")
        return False, f"Ошибка: {str(e)}"

async def stop_bot_process(bot_id: str) -> tuple[bool, str]:
    """Останавливает процесс бота"""
    if bot_id not in active_bots:
        return False, f"Бот {bot_id} не найден"
    
    try:
        bot_info = active_bots[bot_id]
        process = bot_info['process']
        
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
        
        # Удаляем временные файлы
        import shutil
        if os.path.exists(bot_info['temp_dir']):
            shutil.rmtree(bot_info['temp_dir'], ignore_errors=True)
        
        del active_bots[bot_id]
        logger.info(f"🛑 Бот {bot_id} остановлен")
        return True, f"Бот {bot_id} остановлен"
        
    except Exception as e:
        logger.error(f"❌ Ошибка остановки бота {bot_id}: {e}")
        return False, f"Ошибка при остановке: {str(e)}"

# === КОМАНДЫ БОТА ===
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я создаю Telegram ботов\n\n"
        "📝 Опиши мне, какого бота ты хочешь, и я создам его код\n\n"
        "Команды:\n"
        "/create - создать бота\n"
        "/list - список активных ботов\n"
        "/help - справка"
    )

@dp.message(F.text == "/create")
async def cmd_create(message: Message):
    user_id = message.from_user.id
    user_states[user_id] = {'state': 'waiting_description'}
    
    await message.answer(
        "📝 Опиши, какого бота хочешь создать\n\n"
        "Например:\n"
        "• Бот для опросов\n"
        "• Бот-напоминалка\n"
        "• Бот с викториной\n\n"
        "Отмена: /cancel"
    )

@dp.message(F.text == "/cancel")
async def cmd_cancel(message: Message):
    user_id = message.from_user.id
    if user_id in user_states:
        del user_states[user_id]
        await message.answer("❌ Создание бота отменено")
    else:
        await message.answer("Нечего отменять")

@dp.message(F.text == "/list")
async def cmd_list(message: Message):
    if not active_bots:
        await message.answer("📭 Нет активных ботов\n\nСоздай первого: /create")
        return
    
    text = "🤖 Активные боты:\n\n"
    for bot_id, bot in active_bots.items():
        uptime = datetime.now() - bot['started_at']
        status = "🟢 работает"
        text += f"• <code>{bot['id']}</code>\n{status}\n\n"
    
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
    """Команда для редактирования кода бота"""
    parts = message.text.split(maxsplit=2)
    
    if len(parts) < 3:
        await message.answer(
            "❌ Укажи ID бота и описание изменений\n\n"
            "Использование:\n"
            "<code>/edit bot_123_0 добавь команду /hello</code>\n\n"
            "Посмотри список: /list",
            parse_mode="HTML"
        )
        return
    
    bot_id = parts[1].strip()
    edit_prompt = parts[2].strip()
    
    if bot_id not in active_bots:
        await message.answer(f"❌ Бот {bot_id} не найден\n\nПосмотри список: /list")
        return
    
    status_msg = await message.answer("🔄 Редактирую код...")
    
    original_code = active_bots[bot_id]['code']
    new_code, error = edit_bot_code(original_code, edit_prompt)
    
    if error:
        await status_msg.edit_text(f"❌ Ошибка редактирования:\n\n{error}")
        return
    
    # Сохраняем новый код
    active_bots[bot_id]['code'] = new_code
    
    await status_msg.edit_text(
        f"✅ Код отредактирован!\n\n"
        f"Чтобы применить изменения:\n"
        f"1. <code>/stop {bot_id}</code>\n"
        f"2. Запусти заново с новым кодом\n\n"
        f"Скачать код: <code>/download {bot_id}</code>",
        parse_mode="HTML"
    )

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
        await message.answer(f"❌ Бот {bot_id} не найден\n\nПосмотри список: /list")
        return
    
    code = active_bots[bot_id]['code']
    
    # Создаем временный файл
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
    temp_file.write(code)
    temp_file.close()
    
    try:
        file = FSInputFile(temp_file.name, filename=f"{bot_id}.py")
        await message.answer_document(file, caption=f"📄 Код бота {bot_id}")
    finally:
        os.unlink(temp_file.name)

@dp.message(F.text.startswith("/requirements"))
async def cmd_requirements(message: Message):
    """Команда для получения requirements.txt"""
    parts = message.text.split(maxsplit=1)
    
    bot_id = None
    if len(parts) >= 2:
        bot_id = parts[1].strip()
        if bot_id not in active_bots:
            await message.answer(f"❌ Бот {bot_id} не найден\n\nПосмотри список: /list")
            return
    
    # Базовые зависимости для всех ботов
    requirements = """aiogram==3.15.0
aiohttp==3.11.11
python-dotenv==1.0.0"""
    
    # Если указан конкретный бот, анализируем его код
    if bot_id:
        code = active_bots[bot_id]['code']
        
        # Проверяем дополнительные импорты
        additional_deps = []
        if 'import requests' in code or 'from requests' in code:
            additional_deps.append('requests==2.31.0')
        if 'import openai' in code or 'from openai' in code:
            additional_deps.append('openai==1.54.0')
        if 'import redis' in code or 'from redis' in code:
            additional_deps.append('redis==5.0.1')
        if 'import psycopg' in code or 'from psycopg' in code:
            additional_deps.append('psycopg2-binary==2.9.9')
        
        if additional_deps:
            requirements += '\n' + '\n'.join(additional_deps)
    
    # Создаем временный файл
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
    temp_file.write(requirements)
    temp_file.close()
    
    try:
        file = FSInputFile(temp_file.name, filename="requirements.txt")
        caption = f"📦 requirements.txt"
        if bot_id:
            caption += f" для {bot_id}"
        await message.answer_document(file, caption=caption)
    finally:
        os.unlink(temp_file.name)

@dp.message(F.text == "/help")
async def cmd_help(message: Message):
    await message.answer(
        "📚 <b>Справка по командам</b>\n\n"
        "<b>Создание бота:</b>\n"
        "/create - запустить процесс создания\n"
        "/cancel - отменить создание\n\n"
        "<b>Управление:</b>\n"
        "/list - список активных ботов\n"
        "/stop bot_id - остановить бота\n\n"
        "<b>Редактирование:</b>\n"
        "/edit bot_id описание - изменить код\n"
        "/download bot_id - скачать .py файл\n"
        "/requirements [bot_id] - скачать зависимости\n\n"
        "<b>Как работает:</b>\n"
        "1. Опиши желаемого бота\n"
        "2. Я сгенерирую код через AI\n"
        "3. Получи токен у @BotFather\n"
        "4. Бот запустится автоматически\n\n"
        "<b>Пример токена:</b>\n"
        "<code>1234567890:ABCdefGHIjklMNOpqrs</code>",
        parse_mode="HTML"
    )

# === ОБРАБОТКА СОСТОЯНИЙ ===
@dp.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id
    
    if user_id not in user_states:
        await message.answer(
            "Не понял 🤔\n\n"
            "Начни с: /create или /help"
        )
        return
    
    state = user_states[user_id]['state']
    
    # Этап 1: Генерируем код
    if state == 'waiting_description':
        description = message.text
        status_msg = await message.answer("🤖 Генерирую код бота...")
        
        code, error = generate_bot_code(description)
        
        if error:
            await status_msg.edit_text(
                f"❌ Не удалось создать бота:\n\n{error}\n\n"
                f"Попробуй еще раз: /create"
            )
            del user_states[user_id]
            return
        
        user_states[user_id] = {
            'state': 'waiting_token',
            'code': code
        }
        
        await status_msg.edit_text(
            "✅ Код готов!\n\n"
            "Теперь создай бота через @BotFather и пришли мне его токен\n\n"
            "Токен выглядит так:\n"
            "<code>1234567890:ABCdefGHIjklMNOpqrs</code>",
            parse_mode="HTML"
        )
    
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
                f"✅ Бот запущен!\n\n"
                f"ID: <code>{bot_id}</code>\n"
                f"📱 Найди его в Telegram и протестируй\n\n"
                f"<b>Команды:</b>\n"
                f"/list - список ботов\n"
                f"<code>/stop {bot_id}</code> - остановить\n"
                f"<code>/edit {bot_id} описание</code> - изменить код\n"
                f"<code>/download {bot_id}</code> - скачать код\n"
                f"<code>/requirements {bot_id}</code> - зависимости",
                parse_mode="HTML"
            )
        else:
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
