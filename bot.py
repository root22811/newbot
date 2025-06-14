import logging
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = "8133450666:AAHlxeZCDit8GO6t1oeVFA0N4ezeaFaTFGQ"
CHANNEL_ID = "@Power_Flower_Applications"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ----- Тексты на двух языках -----
TEXTS = {
    'ru': {
        'welcome': "👋 Добро пожаловать!\nНажмите кнопку ниже, чтобы заполнить анкету на трудоустройство:",
        'choose_country': "3️⃣ В какую страну вы хотите поехать на работу?",
        'arrival_date': "4️⃣ Когда вы готовы приехать в Польшу на оформление? (не раньше чем через 8 дней от сегодня, формат: ГГГГ-ММ-ДД)",
        'age': "5️⃣ Сколько вам полных лет?",
        'citizenship': "6️⃣ Какое у вас гражданство?",
        'documents': "7️⃣ Какие документы у вас уже готовы или вы только планируете приехать в Европу?",
        'contact': "8️⃣ Оставьте контактные данные (номер телефона, Telegram, WhatsApp и т.д.):",
        'thank_you': "✅ Ваша анкета отправлена менеджерам. Мы с вами скоро свяжемся!",
        'invalid_date': "❗ Дата должна быть не раньше, чем через 8 дней. Введите дату в формате ГГГГ-ММ-ДД.",
        'job_info': "🇳🇱 РАБОТА В НИДЕРЛАНДАХ И БЕЛЬГИИ 🇧🇪\n\nНадёжная работа в Европе с официальным оформлением и полной поддержкой!\n✅ Лицензированное агентство\n✅ Более 10 лет опыта\n✅ Легальная работа по контракту\n...\n📅 Подготовка документов: 5–14 рабочих дней\n❗ Всё официально. Виза обязательна.\n",
    },
    'ua': {
        'welcome': "👋 Ласкаво просимо!\nНатисніть кнопку нижче, щоб заповнити анкету на працевлаштування:",
        'choose_country': "3️⃣ В яку країну ви хочете поїхати на роботу?",
        'arrival_date': "4️⃣ Коли ви готові приїхати до Польщі на оформлення? (не раніше ніж через 8 днів від сьогодні, формат: РРРР-ММ-ДД)",
        'age': "5️⃣ Скільки вам повних років?",
        'citizenship': "6️⃣ Яке у вас громадянство?",
        'documents': "7️⃣ Які документи у вас вже готові або ви тільки плануєте приїхати до Європи?",
        'contact': "8️⃣ Залиште контактні дані (телефон, Telegram, WhatsApp тощо):",
        'thank_you': "✅ Ваша анкета відправлена менеджерам. Ми з вами скоро зв'яжемось!",
        'invalid_date': "❗ Дата має бути не раніше ніж через 8 днів. Введіть дату у форматі РРРР-ММ-ДД.",
        'job_info': "🇳🇱 РОБОТА В НІДЕРЛАНДАХ І БЕЛЬГІЇ 🇧🇪\n\nНадійна робота в Європі з офіційним оформленням!\n✅ Ліцензоване агентство\n✅ 10+ років досвіду\n✅ Легальна робота за контрактом\n...\n📅 Підготовка документів: 5–14 робочих днів\n❗ Все офіційно. Віза обов'язкова.\n",
    }
}

# ----- Состояния анкеты -----
class Form(StatesGroup):
    country = State()
    arrival_date = State()
    age = State()
    citizenship = State()
    documents = State()
    contact = State()

# ----- /start -----
@dp.message_handler(commands='start')
async def start_cmd(message: types.Message, state: FSMContext):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_ua")
    )
    await message.answer("👋 Добро пожаловать!\nВыберите язык / Оберіть мову:", reply_markup=kb)

# ----- Выбор языка -----
@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def set_language(callback_query: types.CallbackQuery, state: FSMContext):
    lang = callback_query.data.split("_")[1]
    await state.update_data(lang=lang)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📝 Заполнить анкету / Заповнити анкету", callback_data="fill_form"))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, TEXTS[lang]['welcome'], reply_markup=kb)

# ----- Показ описания вакансий -----
@dp.callback_query_handler(lambda c: c.data == "fill_form")
async def show_job_info(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🖊 Ввести свои данные / Ввести свої дані", callback_data="start_survey"))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, TEXTS[lang]['job_info'], reply_markup=kb)

# ----- Начало анкеты -----
@dp.callback_query_handler(lambda c: c.data == "start_survey")
async def ask_country(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🇳🇱 Нидерланды – Сельское хоз.", callback_data="Нидерланды - СХ"),
        InlineKeyboardButton("🇧🇪 Бельгия – Строительство", callback_data="Бельгия - Стройка")
    )
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, TEXTS[lang]['choose_country'], reply_markup=kb)
    await Form.country.set()

@dp.callback_query_handler(state=Form.country)
async def ask_arrival(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(country=callback_query.data)
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")

    await bot.send_message(callback_query.from_user.id, TEXTS[lang]['arrival_date'])
    await Form.arrival_date.set()

@dp.message_handler(state=Form.arrival_date)
async def ask_age(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")

    try:
        input_date = datetime.strptime(message.text.strip(), "%Y-%m-%d").date()
        min_date = datetime.now().date() + timedelta(days=8)
        if input_date < min_date:
            raise ValueError
    except ValueError:
        await message.answer(TEXTS[lang]['invalid_date'])
        return

    await state.update_data(arrival_date=str(input_date))
    await message.answer(TEXTS[lang]['age'])
    await Form.age.set()

@dp.message_handler(state=Form.age)
async def ask_citizenship(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")

    await message.answer(TEXTS[lang]['citizenship'])
    await Form.citizenship.set()

@dp.message_handler(state=Form.citizenship)
async def ask_documents(message: types.Message, state: FSMContext):
    await state.update_data(citizenship=message.text)
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")

    await message.answer(TEXTS[lang]['documents'])
    await Form.documents.set()

@dp.message_handler(state=Form.documents)
async def ask_contact(message: types.Message, state: FSMContext):
    await state.update_data(documents=message.text)
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")

    await message.answer(TEXTS[lang]['contact'])
    await Form.contact.set()

@dp.message_handler(state=Form.contact)
async def finish_form(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")

    # Формируем анкету
    summary = (
        f"📥 Новая анкета:\n\n"
        f"🌍 Страна: {data['country']}\n"
        f"📅 Дата прибытия: {data['arrival_date']}\n"
        f"🎂 Возраст: {data['age']}\n"
        f"🛂 Гражданство: {data['citizenship']}\n"
        f"📄 Документы: {data['documents']}\n"
        f"📞 Контакты: {data['contact']}"
    )

    # Отправка в канал
    await bot.send_message(CHANNEL_ID, summary)

    # Ответ пользователю
    await message.answer(TEXTS[lang]['thank_you'])
    await state.finish()

# ----- Запуск -----
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
