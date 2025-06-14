import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from questionnaire import JobForm

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Проверка наличия токена
if not TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env файле")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Логгирование
logging.basicConfig(level=logging.INFO)

# Команда /start
@dp.message(CommandStart())
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Заполнить анкету на трудоустройство", callback_data="start_form")]
    ])
    await message.answer("👋 Добро пожаловать! Нажмите кнопку ниже, чтобы заполнить анкету:", reply_markup=kb)

# Старт формы
@dp.callback_query(F.data == "start_form")
async def show_info(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "<b>🇳🇱 РАБОТА В НИДЕРЛАНДАХ И БЕЛЬГИИ 🇧🇪</b>\n"
        "Надёжная работа в Европе с официальным оформлением и полной поддержкой на каждом этапе!\n"
        "Компания «Срезанные цветы II» — это:\n"
        "✅ Лицензированное агентство\n"
        "✅ Опыт более 10 лет\n"
        "✅ Официальные контракты\n"
        "✅ Полное сопровождение\n"
        "🌷 <b>ВАКАНСИИ:</b>\n"
        "— Нидерланды (цветы, капуста, лук)\n"
        "— Бельгия (строительство)\n"
        "📄 Полный комплект документов\n"
        "💬 Английский не обязателен\n"
        "👫 Приглашаем женщин до 45, мужчин до 50, пары\n"
        "💰 ЗП: от 21,62 zł (Польша) и 14,06 € (Нидерланды)\n"
        "❗ Официально. По визе. Безопасно.\n",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👉 Введите свои данные", callback_data="form_country")]
        ])
    )

# Выбор страны
@dp.callback_query(F.data == "form_country")
async def ask_country(callback: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇳🇱 Нидерланды — Сельское хозяйство", callback_data="nl_agro")],
        [InlineKeyboardButton(text="🇧🇪 Бельгия — Строительство", callback_data="be_construction")]
    ])
    await callback.message.answer("3️⃣ В какую страну вы хотите поехать на работу?", reply_markup=kb)

@dp.callback_query(F.data.in_({"nl_agro", "be_construction"}))
async def country_selected(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(country=callback.data)
    await callback.message.answer("4️⃣ Когда вы готовы приехать в Польшу на оформление?\n(не раньше чем через 8 дней)")
    await state.set_state(JobForm.arrival_date)

@dp.message(JobForm.arrival_date)
async def ask_age(message: types.Message, state: FSMContext):
    await state.update_data(arrival_date=message.text)
    await message.answer("5️⃣ Сколько вам полных лет?")
    await state.set_state(JobForm.age)

@dp.message(JobForm.age)
async def ask_citizenship(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("6️⃣ Какое у вас гражданство?")
    await state.set_state(JobForm.citizenship)

@dp.message(JobForm.citizenship)
async def ask_documents(message: types.Message, state: FSMContext):
    await state.update_data(citizenship=message.text)
    await message.answer("7️⃣ Какие документы у вас уже готовы или вы только планируете приехать в Европу?")
    await state.set_state(JobForm.documents)

@dp.message(JobForm.documents)
async def ask_contact(message: types.Message, state: FSMContext):
    await state.update_data(documents=message.text)
    await message.answer("8️⃣ Оставьте контакт для связи (телефон, Telegram, WhatsApp):")
    await state.set_state(JobForm.contact)

@dp.message(JobForm.contact)
async def form_complete(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    country_map = {
        "nl_agro": "🇳🇱 Нидерланды — Сельское хозяйство",
        "be_construction": "🇧🇪 Бельгия — Строительство"
    }

    result = (
        "<b>📨 Новая анкета от кандидата</b>\n\n"
        f"<b>Страна и направление:</b> {country_map.get(data['country'], '—')}\n"
        f"<b>Дата приезда:</b> {data['arrival_date']}\n"
        f"<b>Возраст:</b> {data['age']}\n"
        f"<b>Гражданство:</b> {data['citizenship']}\n"
        f"<b>Документы:</b> {data['documents']}\n"
        f"<b>Контакт:</b> {data['contact']}"
    )

    await bot.send_message(CHANNEL_ID, result)
    await message.answer("✅ 9️⃣ Ваша анкета отправлена менеджерам. С вами свяжутся в течение 24 часов.")
    await state.clear()

# === Запуск бота ===
if __name__ == "__main__":
    import asyncio

    async def main():
        await dp.start_polling(bot)

    asyncio.run(main())