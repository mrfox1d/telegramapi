from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from main import admin_id
from handlers.databases import create_order, get_order, orders_list, subscribe_checking, update_subscribe_status
from aiogram.types impo

router = Router()

async def is_subscribed(user_id: int):
    bot = await router.get_chat_member(-1003374254480, user_id)
    database = await subscribe_checking(user_id)
    if bot.status in ['member', 'administrator', 'creator'] and database == 'true':
        return True
    if bot.status in ['member', 'administrator', 'creator'] and database == 'false':
        await update_subscribe_status(user_id, 'true')
        return True
    else:
        if database == 'true':
            await update_subscribe_status(user_id, 'false')
        return False

@router.command("start", "menu")
async def menu(message: Message):
    status = await is_subscribed(message.from_user.id)
    if status == False:
        kb = [[InlineKeyboardButton(text="🔔 Подписаться на канал", url="https://t.me/mfxstudio")],
              [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subscribe")]]
        mk = InlineKeyboardMarkup(inline_keyboard=kb)
        await message.answer("Для использования бота необходимо подписаться на наш канал.", reply_markup=mk)
        return
    elif status == True:
        pass
    else:
        await message.answer("Произошла ошибка при проверке подписки. Пожалуйста, попробуйте снова позже.")
        return
    
    kb = [[InlineKeyboardButton(text="🗃️ Шаблоны", callback_data="templates")],
          [InlineKeyboardButton(text="🚀 Сделать заказ", callback_data="new_order")],
          [InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders")]]
    
    if message.from_user.id == admin_id:
        kb.append([InlineKeyboardButton(text="🛠️ Админ-панель", callback_data="admin_panel")], 
                  [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")])
    
    mk = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer(f"👋 Приветствую тебя в главном меню магазина **mfxstudio**, **{message.from_user.first_name}**!"
                         "Выбери нужный раздел по кнопкам ниже:"
                         , reply_markup=mk, parse_mode="Markdown")