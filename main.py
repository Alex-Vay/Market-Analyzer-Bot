from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

# Access environment variables as if they came from the actual environment
TOKEN = os.getenv('TOKEN')

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "Привет! 👋🎉 Я ваш личный бот, готовый помочь Вам с поиском и анализом товаров с маркетплейсов🛒.\n\n"
        " \tПорядок действий:\n"
        "Нажмите Найти Товар\n"
        "Выберите один или несколько маркетплейсов\n"
        "Введите название, модель, цену товара и нажмите Найти\n\n"
        "Как только запрос выполнится, бот отправит Вам уведомление о товаре!🚀"
    )
    keyboard = [
        [InlineKeyboardButton("Найти Товар", callback_data='choose_stores')],
        [InlineKeyboardButton("Помощь", callback_data='help')],
        [InlineKeyboardButton("Информация о боте", callback_data='info')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=welcome_message, reply_markup=reply_markup)


# Функция для создания клавиатуры с магазинами
def create_store_keyboard(selected_stores):
    store_keyboard = []
    for i in range(1, 4):
        store_name = f"Магазин {i}"
        button_text = f"✅ {store_name}" if store_name in selected_stores else store_name
        store_keyboard.append([InlineKeyboardButton(button_text, callback_data=f'store{i}')])

    store_keyboard.append([InlineKeyboardButton("Завершить выбор", callback_data='finish_selection')])
    return InlineKeyboardMarkup(store_keyboard)


# Функция для обработки выбора магазинов
async def choose_stores(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['selected_stores'] = set()
    store_reply_markup = create_store_keyboard(context.user_data['selected_stores'])
    await update.callback_query.edit_message_text(text="Вы на этапе выбора магазинов", reply_markup=store_reply_markup)


# Функция для обработки выбора магазина
async def select_store(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    store_name = f"Магазин {query.data[-1]}"
    selected_stores = context.user_data['selected_stores']

    # Добавляем или удаляем магазин из выбранных
    if store_name in selected_stores:
        selected_stores.remove(store_name)
    else:
        selected_stores.add(store_name)

    # Обновляем клавиатуру с изменёнными кнопками
    store_reply_markup = create_store_keyboard(selected_stores)
    await query.edit_message_text(text="Вы на этапе выбора магазинов", reply_markup=store_reply_markup)


# Функция для завершения выбора
async def finish_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    selected_stores = context.user_data.get('selected_stores', list())

    if selected_stores:
        stores_list = ', '.join(selected_stores)
        await update.callback_query.edit_message_text(
            text=f"Вы выбрали следующие магазины: {stores_list}\n"
                 f"Пожалуйста, укажите товар в формате:\nМарка\nМодель\nЦена.")
        # Устанавливаем состояние ожидания названия товара
        context.user_data['awaiting_product_name'] = True
    else:
        await update.callback_query.edit_message_text(text="Вы не выбрали ни одного магазина.")


async def handle_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('awaiting_product_name'):
        product_info = update.message.text
        product_info_split = product_info.split('\n')
        product_text = f"Марка: {product_info_split[0]}\n" \
                       f"Модель: {product_info_split[1]}\n" \
                       f"Цена: {product_info_split[2]}."

        await update.message.reply_text(f"Вы указали товар:\n{product_text}")
        # Сбрасываем состояние ожидания
        context.user_data['awaiting_product_name'] = False
    else:
        await update.message.reply_text("Пожалуйста, сначала выберите магазины.")


# Основная функция для обработки нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Подтверждение нажатия кнопки

    if query.data == 'choose_stores':
        await choose_stores(update, context)
    elif query.data.startswith('store'):
        await select_store(update, context)
    elif query.data == 'finish_selection':
        await finish_selection(update, context)
    elif query.data == 'help':
        await query.edit_message_text(text="Вы можете использовать команды /start.")
    elif query.data == 'info':
        await query.edit_message_text(text="Я бот, созданный для помощи пользователям!")


def main() -> None:
    # Создаем приложение и регистрируем обработчики
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_product_name))
    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
